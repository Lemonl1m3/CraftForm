# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                               CraftForm                                      ║
# ╠══════════════════════════════════════════════════════════════════════════════╣
# ║  OPERATIONS LAMBDA  ::  commands/server.py                                   ║
# ║  Handles all /server slash command interactions.                             ║
# ║  Create, delete, start, stop, list, status, modify, save, get.              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import json


# ==========================================================================================
#                                   /SERVER COMMAND
# ==========================================================================================
def handle(subcommand, options, body):

    # --------------------------------START--------------------------------
    if subcommand == "start":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "type": 4,  # respond immediately to the user
                "data": {
                    "content": "Your mum a hoe, a pretty one tho <3"  # placeholder :)
                },
            }),
        }

    # --------------------------------STOP--------------------------------
    if subcommand == "stop":
        pass

    # --------------------------------CREATE--------------------------------
    if subcommand == "create":
        pass

    # --------------------------------DELETE--------------------------------
    if subcommand == "delete":
        pass

    # --------------------------------LIST--------------------------------
    if subcommand == "list":
        pass

    # --------------------------------STATUS--------------------------------
    if subcommand == "status":
        pass

    # --------------------------------MODIFY--------------------------------
    if subcommand == "modify":
        pass

    # --------------------------------SAVE--------------------------------
    if subcommand == "save":
        pass

    # --------------------------------GET--------------------------------
    if subcommand == "get":
        pass
