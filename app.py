import os
import json
from bson import ObjectId
from datetime import datetime
import pytz
from pymongo import MongoClient
from translate import detect_language

# MongoDB connection setup
client = MongoClient(os.environ['MONGODB_URI'])
db = client['CoachLife']
player_learning_collection = db['Player Learning']

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
            "CommentedOn": commented_on,
            "Comment": comment  # Store the original comment
        }

        if comment_language == 'ta':  
            new_comment["Comment_Tn"] = comment  # Store Tamil comment in Comment_TN
        else:  
            new_comment["Comment_En"] = comment  # Store English comment in Comment_EN

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
