import json
import boto3
from bson import ObjectId
from datetime import datetime
import pytz
from langdetect import detect
from googletrans import Translator
from pymongo import MongoClient
import os 

translator = Translator()

# MongoDB connection setup
client = MongoClient(os.environ['MONGODB_URI'])
db = client['CoachLife']
player_learning_collection = db['Player Learning']
prompts_collection = db['Prompts']

# Set up the OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']

def detect_language(text):
    try:
        return detect(text)
    except:
        return 'unknown'

def translate_text(text, src='ta', dest='en'):
    try:
        translated = translator.translate(text, src=src, dest=dest)
        return translated.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def add_comment(event, context):
    try:
        # Parse input JSON data
        data = json.loads(event['body'])
        document_id = data['document_id']
        comment = data['comment']
        commented_by = data['commented_by']

        # Ensure the document ID is a valid ObjectId
        document_id = ObjectId(document_id)
        
        # Detect language of the comment
        comment_language = detect_language(comment)

        # Get the current UTC time with timezone aware
        now_utc = datetime.now(pytz.UTC)

        # Convert UTC time to your desired timezone
        ist = pytz.timezone('Asia/Kolkata')
        commented_on = now_utc.astimezone(ist).strftime("%Y-%m-%d %H:%M:%S")

        new_comment = {
            "_id": ObjectId(),
            "CommentedBy": commented_by,
            "CommentedOn": commented_on
        }

        if comment_language == 'ta':  # Tamil language
            translated_comment = translate_text(comment, src='ta', dest='en')
            new_comment["Comment_Tn"] = comment
            new_comment["Comment_En"] = translated_comment
        else:  # For non-Tamil comments
            new_comment["Comment_En"] = comment
          
        result = player_learning_collection.update_one(
            {'_id': document_id},
            {'$push': {'Comments': new_comment}}
        )

        if result.matched_count == 0:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "No document found with the provided ID."})
            }

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Comment added successfully."}),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        }
      
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        }
