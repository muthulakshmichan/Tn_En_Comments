import os
import json
from bson import ObjectId
from datetime import datetime
import pytz
from pymongo import MongoClient
import openai

# Set up the OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']

# MongoDB connection setup
client = MongoClient(os.environ['MONGODB_URI'])
db = client['CoachLife']
player_learning_collection = db['Player Learning']

# Function to detect language using OpenAI API
def detect_language(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a language detection assistant."},
                {"role": "user", "content": f"Detect the language of the following text: {text}"}
            ],
            max_tokens=50,
            temperature=0
        )
        language = response['choices'][0]['message']['content'].strip().lower()
        return language
    except Exception as e:
        print(f"Language detection error: {e}")
        return 'unknown'

# Function to add comment to a document in the database
def add_comment(document_id, comment, commented_by):
    try:
        document_id = ObjectId(document_id)
        comment_language = detect_language(comment)
        now_utc = datetime.now(pytz.UTC)

        ist = pytz.timezone('Asia/Kolkata')
        commented_on = now_utc.astimezone(ist).strftime("%Y-%m-%d %H:%M:%S")

        new_comment = {
            "_id": ObjectId(),
            "CommentedBy": commented_by,
            "CommentedOn": commented_on
        }

        if 'tamil' in comment_language and 'english' in comment_language:
            # Assuming the user input format: "Tamil Comment. English Comment."
            tamil_comment, english_comment = comment.split(". ")
            new_comment["Comment_Tn"] = tamil_comment.strip()
            new_comment["Comment_En"] = english_comment.strip()
        elif 'tamil' in comment_language:  
            new_comment["Comment_Tn"] = comment
        else:  
            new_comment["Comment_En"] = comment

        result = player_learning_collection.update_one(
            {'_id': document_id},
            {'$push': {'Comments': new_comment}}
        )

        if result.matched_count == 0:
            return {"error": "No document found with the provided ID."}

        return {"message": "Comment added successfully."}

    except Exception as e:
        return {"error": str(e)}

# Lambda function handler
def lambda_handler(event, context):
    print("Event received:", event)
    try:
        body = event['body']
        if isinstance(body, dict):
            body = json.dumps(body)  # Ensure body is a JSON string

        body = json.loads(body)  # Parse the JSON string into a dictionary
        document_id = body.get('document_id')
        comment = body.get('comment')
        commented_by = body.get('commented_by')
        
        if not document_id or not comment or not commented_by:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "document_id, comment, and commented_by are required fields."}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            }
        
        response = add_comment(document_id, comment, commented_by)
        return {
            'statusCode': 200,
            'body': json.dumps(response),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Missing key in the event data: {}".format(str(e))}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
