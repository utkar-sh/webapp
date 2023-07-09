import boto3
import time
import json
from uuid import uuid4


def send_validation(email_address):
    sns_client = boto3.client('sns', region_name='us-west-2')
    dynamodb_table = boto3.resource('dynamodb', region_name='us-west-2').Table('UserAccountVerificationTokenTable')

    token = str(uuid4())
    item = {"UserId": email_address, "token": token, "ExpireTime": int(time.time() + 300), "sendStatus": "Not sent"}
    message = "{\"email\": \"%s\", \"token\": \"%s\", \"message_type\": \"validation\"}" % (email_address, str(token))

    try:
        dynamodb_table.put_item(Item=item)
        sns_client.publish(TopicArn='arn:aws:sns:us-west-2:531886003212:UserAccountVerificationSNSTopic',
                           Message=message)
        return True
    except Exception:
        return False


def verify_token(email_address, token):
    dynamodb_table = boto3.resource('dynamodb', region_name='us-west-2').Table('UserAccountVerificationTokenTable')
    try:
        response = dynamodb_table.get_item(Key={"UserId": email_address})
        if "Item" in response.keys():
            item = response['Item']
            true_token = item['token']
            expire_time = item["ExpireTime"]
            if expire_time < int(time.time()):
                return False
            if true_token == token:
                return True
    except Exception:
        return False