# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                               CraftForm                                      ║
# ╠══════════════════════════════════════════════════════════════════════════════╣
# ║  STARTUP LAMBDA  ::  discord_api.py                                          ║
# ║  Handles all Discord API interactions during initial deployment.             ║
# ║  Registers slash commands and sets the interactions endpoint.                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝


# ==========================================================================================
#                            IMPORTS AND DEPENDENCIES
# ==========================================================================================
import urllib3
import json
from pathlib import Path

# ==========================================================================================
#                          SETUP CLIENTS AND GLOBAL VARIABLES
# ==========================================================================================
http = urllib3.PoolManager()  # create a new HTTP connection pool manager to make HTTP requests

slash_commands = json.loads((Path(__file__).parent / "slash_commands.json").read_text())


# ==========================================================================================
#                        DISCORD API SETUP AND INTERACTIONS
# ==========================================================================================
def send_discord_api_url(discord_app_id, api_url, discord_bot_token):

    # send a post to the discord API to set the interactions endpoint to the API Gateway URL
    discordResponse = http.request(
        "PATCH",
        f"https://discord.com/api/v10/applications/{discord_app_id}",
        headers={
            "Authorization": f"Bot {discord_bot_token}",  # authenticate the request with the bot token
            "Content-Type": "application/json",  # specify that the request body is in JSON
        },
        body=json.dumps(
            {
                "interactions_endpoint_url": api_url  # the API Gateway URL to set as the interactions endpoint
            }
        ),
    )

    # make sure the request was successful
    if discordResponse.status != 200:
        raise Exception(f"Failed to set Discord interactions endpoint: {discordResponse.status} - {discordResponse.data} :(")
    else:
        print("API Gateaway URL set on Discord application :)")


def register_slash_commands(discord_app_id, discord_bot_token):

    # register the slash commands with the Discord API
    discordResponse = http.request(
        "PUT",
        f"https://discord.com/api/v10/applications/{discord_app_id}/commands",
        headers={
            "Authorization": f"Bot {discord_bot_token}",  # authenticate the request with the bot token
            "Content-Type": "application/json",  # specify that the request body is in JSON
        },
        body=json.dumps(slash_commands),  # the list of slash commands to register
    )

    # make sure the request was successful
    if discordResponse.status != 200:
        raise Exception(f"Failed to register slash commands: {discordResponse.status} - {discordResponse.data} :(")
    else:
        print("Slash commands registered with Discord :)")
