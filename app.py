import os
import json
from bson import ObjectId
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient(os.environ['MONGODB_URI'])
db = client['CoachLife']
player_learning_collection = db['Player Learning']
learning_pathway_collection = db['Learning Pathway']

# Lambda function handler
def lambda_handler(event, context):
    print("Event received:", event)
    try:
        # Parse request body
        body = json.loads(event['body'])
        player_id = body.get('playerId')
        pathway_id = body.get('pathwayId')
        status = body.get('status')

        if not player_id or not pathway_id or not status:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing playerId, pathwayId, or status in request body'})
            }

        try:
            # Check if player_id and pathway_id exist in Player Learning collection
            existing_doc = player_learning_collection.find_one({'playerId': ObjectId(player_id), 'pathwayId': ObjectId(pathway_id)})

            if existing_doc:
                # Update status if document exists
                result = player_learning_collection.update_one(
                    {'_id': existing_doc['_id']},
                    {'$set': {'status': status}}
                )
                response = {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'message': f"Updated status for player {player_id} in pathway {pathway_id}."})
                }
            else:
                # Check if pathway_id exists in Learning Pathway collection
                pathway_doc = learning_pathway_collection.find_one({'_id': ObjectId(pathway_id)})

                if pathway_doc:
                    # Create new document in Player Learning collection
                    new_doc = {
                        'playerId': ObjectId(player_id),
                        'pathwayId': ObjectId(pathway_id),
                        'status': status
                    }
                    result = player_learning_collection.insert_one(new_doc)
                    response = {
                        'statusCode': 201,
                        'headers': {
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'message': f"Created new document for player {player_id} in pathway {pathway_id}."})
                    }
                else:
                    response = {
                        'statusCode': 404,
                        'headers': {
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': f"Pathway with id {pathway_id} does not exist in Learning Pathway collection."})
                    }
        except Exception as e:
            response = {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f"Internal Server Error: {str(e)}"})
            }

        return response

    except KeyError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"error": "Missing key in the event data: {}".format(str(e))})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"error": "Internal server error: {}".format(str(e))})
        }














# import os
# import json
# import openai
# from bson import ObjectId
# from datetime import datetime
# import pytz
# from langdetect import detect
# from googletrans import Translator
# from pymongo import MongoClient

# translator = Translator()

# # MongoDB connection setup
# client = MongoClient(os.environ['MONGODB_URI'])
# db = client['CoachLife']
# player_learning_collection = db['Player Learning']
# prompts_collection = db['Prompts']

# # Set up the OpenAI API key
# openai.api_key = os.environ['OPENAI_API_KEY']

# # Function to detect language of the text
# def detect_language(text):
#     try:
#         return detect(text)
#     except:
#         return 'unknown'

# # Function to translate text using OpenAI API
# def translate_text(text, src='ta', dest='en'):
#     try:
#         if src != 'en' and dest == 'en':
#             response = openai.ChatCompletion.create(
#                 model="gpt-4-turbo",
#                 messages=[
#                     {"role": "system", "content": "You are a translation assistant that translates Tamil text to English exactly as it is without adding any additional context or interpretation."},
#                     {"role": "user", "content": f"Tamil: {text}\nTranslate to English:"}
#                 ],
#                 max_tokens=150,
#                 temperature=0
#             )
#             translated_text = response['choices'][0]['message']['content'].strip()
#             return translated_text
#         else:
#             return text
#     except Exception as e:
#         print(f"Translation error: {e}")
#         return text

# # Function to add comment to a document in the database
# def add_comment(document_id, comment, commented_by):
#     try:
#         document_id = ObjectId(document_id)
#         comment_language = detect_language(comment)
#         now_utc = datetime.now(pytz.UTC)

#         ist = pytz.timezone('Asia/Kolkata')
#         commented_on = now_utc.astimezone(ist).strftime("%Y-%m-%d %H:%M:%S")

#         new_comment = {
#             "_id": ObjectId(),
#             "CommentedBy": commented_by,
#             "CommentedOn": commented_on
#         }

#         if comment_language == 'ta':  
#             translated_comment = translate_text(comment, src='ta', dest='en')
#             new_comment["Comment_Tn"] = comment
#             new_comment["Comment_En"] = translated_comment
#         else:  
#             new_comment["Comment_En"] = comment

#         result = player_learning_collection.update_one(
#             {'_id': document_id},
#             {'$push': {'Comments': new_comment}}
#         )

#         if result.matched_count == 0:
#             return {"error": "No document found with the provided ID."}

#         return {"message": "Comment added successfully."}

#     except Exception as e:
#         return {"error": str(e)}

# # Lambda function handler
# def lambda_handler(event, context):
#     print("Event received:", event)
#     try:
#         body = event['body']
#         if isinstance(body, str):
#             body = json.loads(body)

#         document_id = body.get('document_id')
#         comment = body.get('comment')
#         commented_by = body.get('commented_by')
#         response = add_comment(document_id, comment, commented_by)
#         return {
#             'statusCode': 200,
#             'body': json.dumps(response),
#             'headers': {
#                 'Access-Control-Allow-Origin': '*',
#                 'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
#                 'Access-Control-Allow-Headers': 'Content-Type'
#             }
#         }
#     except KeyError as e:
#         return {
#             'statusCode': 400,
#             'body': json.dumps({"error": "Missing key in the event data: {}".format(str(e))}),
#             'headers': {
#                 'Access-Control-Allow-Origin': '*',
#                 'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
#                 'Access-Control-Allow-Headers': 'Content-Type'
#             }
#         }
