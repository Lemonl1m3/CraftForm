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
