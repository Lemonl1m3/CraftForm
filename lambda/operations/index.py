import json


def handler(event, context):

    # capture event "body"
    body = json.loads(event["body"])

    # make sure ping requests from Discord to verify API Gateway URL is up and succesful respond
    if body["type"] == 1:
        return {
            "statuscode": 200,
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
                            "content": "It actually works! God bless"  # message sent back to the user
                        }
                    })
                }