from http.client import ImproperConnectionState
import jwt
import json
import os
import pymongo
import datetime
import bson.json_util as json_util
import hashlib



myclient = pymongo.MongoClient(os.environ.get('db_host'))
mydb = myclient[os.environ.get("db")]
mycol = mydb["user"]

def lambda_handler(event, context):
    if event.get('token', None) == None:
        return {
            'statuscode': 400,
            'body': json.dumps('token is not defined!')
        }

    mydoc = mycol.find()
    json_result = json.loads(json_util.dumps(mydoc))
    hashed_password_from_database = json_result[0]["password_hashed"]
    
    
    token_from_website = event['token']
    token = jwt.encode({
        'id': '1',
        'date': datetime.datetime.now().strftime("%m-%d-%Y"),
        'hashed_password': hashed_password_from_database
    }, 
    os.environ.get("JWT_SECRET"), 
    algorithm='HS256')
    

    if (token == token_from_website):
            return {
        'statuscode': 200,
        'body': True
        }
    
    return {
        'statuscode': 401,
        'body': False
    }

#lambda_handler()