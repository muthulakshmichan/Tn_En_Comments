import os
import json
from bson import ObjectId
from datetime import datetime
import pytz
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient(os.environ['MONGODB_URI'])
db = client['CoachLife']
player_learning_collection = db['Player Learning']

# Function to add comment to a document in the database
def add_comment(document_id, comment_en, comment_tn, commented_by):
    try:
        document_id = ObjectId(document_id)
        now_utc = datetime.now(pytz.UTC)

        ist = pytz.timezone('Asia/Kolkata')
        commented_on = now_utc.astimezone(ist).strftime("%Y-%m-%d %H:%M:%S")

        new_comment = {
            "_id": ObjectId(),
            "CommentedBy": commented_by,
            "CommentedOn": commented_on
        }

        if comment_tn:  # If Tamil comment is provided
            new_comment["Comment_Tn"] = comment_tn
        if comment_en:  # If English comment is provided
            new_comment["Comment_En"] = comment_en

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
        comment_en = body.get('comment_en', "")  # Default to empty string if not provided
        comment_tn = body.get('comment_tn', "")  # Default to empty string if not provided
        commented_by = body.get('commented_by')
        
        if not document_id or not commented_by:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "document_id and commented_by are required fields."}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            }

        if not comment_en and not comment_tn:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "At least one of comment_en or comment_tn must be provided."}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            }
        
        response = add_comment(document_id, comment_en, comment_tn, commented_by)
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
