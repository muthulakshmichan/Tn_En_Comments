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

def add_comment(document_id, comment, commented_by):
    try:
        document_id = ObjectId(document_id)
        now_utc = datetime.now(pytz.UTC)

        ist = pytz.timezone('Asia/Kolkata')
        commented_on = now_utc.astimezone(ist).strftime("%Y-%m-%d %H:%M:%S")

        new_comment = {
            "_id": ObjectId(),
            "CommentedBy": commented_by,
            "CommentedOn": commented_on,
            "Comment": comment
        }

        result = player_learning_collection.update_one(
            {'_id': document_id},
            {'$push': {'Comments': new_comment}}
        )

        if result.matched_count == 0:
            return {"statusCode": 404, "error": "No document found with the provided ID."}

        return {"statusCode": 200, "message": "Comment added successfully."}

    except Exception as e:
        return {"statusCode": 500, "error": str(e)}

def lambda_handler(event, context):
    print("Event received:", event)
    try:
        body = json.loads(event['body'])

        document_id = body.get('document_id')
        comment = body.get('comment')
        commented_by = body.get('commented_by')

        response = add_comment(document_id, comment, commented_by)

        return {
            'tatusCode': response['statusCode'],
            'body': json.dumps({"message": response['message']} if 'essage' in response else {"error": response['error']}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    except KeyError as e:
        return {
            'tatusCode': 400,
            'body': json.dumps({"error": "Missing key in the event data: {}".format(str(e))}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    except Exception as e:
        return {
            'tatusCode': 500,
            'body': json.dumps({"error": "Internal server error: {}".format(str(e))}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
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
