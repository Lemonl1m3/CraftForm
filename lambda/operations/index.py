import json
import boto3
from nacl.signing import VerifyKey  #cryptographic library for verifying signatures
from nacl.exceptions import BadSignatureError   # exception raised when signature verification fails


def verify_signature(event, public_key):

    signature = event["headers"]["x-signature-ed25519"]  # get the signature from the request headers
    timestamp = event["headers"]["x-signature-timestamp"]  # get the timestamp from the request headers

    body = event["body"]  # get the raw body of the request - this is what was signed and needs to be verified

    try:
        verify_key = VerifyKey(bytes.fromhex(public_key))  # convert the public key from a hex string to a PyNaCL VerifyKey object
        verify_key.verify(timestamp.encode() + body.encode(), bytes.fromhex(signature))  # combine the timestamp and body, encode them, and verify the signature using the public key
    except BadSignatureError:
        return False  # signature verification failed
    return True



def handler(event, context):

    # capture event "body"
    body = json.loads(event["body"])

    #====================================VERIFY DISCORD SIGNATURE================================
    
    ssm = boto3.client("ssm")   # create the AWS SSM Parameter store client
    discord_public_key = ssm.get_parameter(Name="/craftform/config/discord/public-key")["Parameter"]["Value"]   # get the Discord public key

    if not verify_signature(event, discord_public_key):  # verify the request signature using the Discord public key
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid request signature"})  # respond with an error if signature verification fails
        }
    
    # make sure ping requests from Discord to verify API Gateway URL is up and succesful respond
    if body["type"] == 1:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "type": 1  # respond with type 1 to acknowledge the ping request
            })
        }
    if body["type"] == 2:

        command = body["data"]["name"]  # capture the slash command
        subcommand = body["data"]["options"][0]["name"]  # capture the slash command's subcommand - words are fun

        if command == "server":
            if subcommand == "start":
                return {
                    "statusCode": 200,  # respond with a 200 status code to tell Discord the command was received and is being processed
                    "body": json.dumps({
                        "type": 4,  # respond immediately to the user
                        "data": {
                            "content": "Your mum a hoe, a pretty one tho <3"  # message sent back to the user
                        }
                    })
                }