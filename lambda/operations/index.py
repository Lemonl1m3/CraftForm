# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                               CraftForm                                      ║
# ╠══════════════════════════════════════════════════════════════════════════════╣
# ║  OPERATIONS LAMBDA  ::  index.py                                             ║
# ║  Handles all incoming Discord interactions for CraftForm.                    ║
# ║  Verifies signatures, answers pings, and routes slash commands.              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ==========================================================================================
#                            IMPORTS AND DEPENDENCIES
# ==========================================================================================
import json
import base64
import boto3
from nacl.signing import VerifyKey  # cryptographic library for verifying signatures

# ==========================================================================================
#                           SETUP CLIENTS AND GLOBAL VARIABLES
# ==========================================================================================
ssm = boto3.client("ssm")  # create the AWS SSM Parameter store client
discord_public_key = ssm.get_parameter(Name="/craftform/config/discord/public-key")["Parameter"]["Value"]  # get the Discord public key


# ==========================================================================================
#                    VERIFY DISCORD SIGNATURE AND HANDLE INTERACTIONS
# ==========================================================================================
def verify_signature(event, rawBody, public_key):

    signature = event["headers"]["x-signature-ed25519"]  # get the signature from the request headers
    timestamp = event["headers"]["x-signature-timestamp"]  # get the timestamp from the request headers

    try:
        verify_key = VerifyKey(bytes.fromhex(public_key))  # convert the public key from a hex string to a PyNaCL VerifyKey object
        verify_key.verify(
            timestamp.encode() + rawBody.encode(), bytes.fromhex(signature)
        )  # combine the timestamp and body, encode them, and verify the signature using the public key

    except Exception as e:  # catch any exceptions because discord sends a bad ping request to the interactions endpoint when first setting up
        print("Error occurred while verifying signature:", str(e))
        return False  # signature verification failed
    return True


# ==========================================================================================
#                                 DISCORD API INTERACTIONS
# ==========================================================================================
def handler(event, context):

    print("Received event:", json.dumps(event))  # log the incoming event for debugging

    # ====================================VERIFY DISCORD SIGNATURE================================

    rawBody = event["body"]  # capture the raw body of the request FIRST because sometime the api gateway changes it

    # API Gateway may base64 encode the body when it forwards the request to Lambda
    if event.get("isBase64Encoded", False):
        rawBody = base64.b64decode(rawBody).decode()  # decode the body if it is base64 encoded

    print("Verifying signature....")
    if not verify_signature(event, rawBody, discord_public_key):  # verify the request signature using the Discord public key
        print("Signature verification FAILED :(")
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid request signature"}),  # respond with an error if signature verification fails
        }
    print("Signature verification SUCCESS :)")

    # capture event decoded "body"
    body = json.loads(rawBody)

    print("Interaction type:", body["type"])  # log the interaction type for debugging

    # make sure ping requests from Discord to verify API Gateway URL is up and succesful respond
    if body["type"] == 1:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "type": 1  # respond with type 1 to acknowledge the ping request
                }
            ),
        }

    # ====================================HANDLE SLASH COMMANDS===================================
    if body["type"] == 2:
        command = body["data"]["name"]  # capture the slash command
        options = body["data"].get("options", [])  # top-level commands like /update have no subcommands, so this can be empty
        subcommand = options[0]["name"] if options else None  # only grab a subcommand if there actually is one

        # --------------------------------SERVER COMMANDS--------------------------------
        if command == "server":
            if subcommand == "start":
                return {
                    "statusCode": 200,  # respond with a 200 status code to tell Discord the command was received and is being processed
                    "headers": {"Content-Type": "application/json"},  # set the content type to JSON - needed for Discord to understand the response
                    "body": json.dumps(
                        {
                            "type": 4,  # respond immediately to the user
                            "data": {
                                "content": "Your mum a hoe, a pretty one tho <3"  # message sent back to the user
                            },
                        }
                    ),
                }

        # --------------------------------UPDATE COMMAND--------------------------------
        # the actual update (sync the fork, pull the latest release, redeploy the lambdas, re-register
        # commands) takes WAY longer than discord's 3 second deadline - so we can't do it here. instead we
        # punt the heavy lifting to the staging function async and just tell discord we're "thinking" :)
        if command == "update":
            lambdaClient = boto3.client("lambda")  # need the lambda client to kick off the staging function

            lambdaClient.invoke(
                FunctionName="craftform-staging-function",  # the inline staging function does the actual work
                InvocationType="Event",  # fire-and-forget - this returns straight away, we don't wait on it
                Payload=json.dumps(
                    {
                        "action": "update",  # tells staging to take the direct-invoke path, not the cloudformation one
                        "application_id": body["application_id"],  # staging needs this to hit the followup webhook later
                        "interaction_token": body["token"],  # the token discord gave us for THIS interaction
                        "version": "latest",  # which release to pull - latest for now
                    }
                ).encode(),
            )

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "type": 5,  # deferred response - shows the user "thinking..." while staging does its thing and edits the message when it's done
                    }
                ),
            }
