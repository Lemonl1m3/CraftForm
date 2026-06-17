# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                               CraftForm                                      ║
# ╠══════════════════════════════════════════════════════════════════════════════╣
# ║  OPERATIONS LAMBDA  ::  commands/update.py                                   ║
# ║  Handles the /update slash command.                                          ║
# ║  Kicks off the staging function to sync, redeploy, and refresh commands.    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import json
import boto3


# ==========================================================================================
#                                   /UPDATE COMMAND
# ==========================================================================================
def handle(subcommand, options, body):

    # the actual update takes WAY longer than discord's 3 second deadline - so we can't do
    # it here. instead we kick off the staging function async and tell discord we're "thinking" :)
    lambdaClient = boto3.client("lambda")

    lambdaClient.invoke(
        FunctionName="craftform-staging-function",  # staging function does all the actual heavy lifting
        InvocationType="Event",  # fire-and-forget - returns immediately, we don't wait on it
        Payload=json.dumps({
            "action": "update",  # tells staging to take the /update path, not the cloudformation one
            "application_id": body["application_id"],  # staging needs this to edit the "thinking..." message later
            "interaction_token": body["token"],  # the token for THIS interaction - staging uses it for the followup webhook
        }).encode(),
    )

    # tell discord we're thinking - staging will edit this message when it's done :)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"type": 5}),  # type 5 = deferred response = "thinking..." spinner
    }
