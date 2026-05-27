#╔══════════════════════════════════════════════════════════════════════════════╗
#║                               CraftForm                                      ║
#╠══════════════════════════════════════════════════════════════════════════════╣
#║  STARTUP LAMBDA  ::  discord_api.py                                          ║
#║  Handles all Discord API interactions during initial deployment.             ║
#║  Registers slash commands and sets the interactions endpoint.                ║
#╚══════════════════════════════════════════════════════════════════════════════╝
import urllib3
import json


#========================================INITIALIZATION========================================
http = urllib3.PoolManager()    # create a new HTTP connection pool manager to make HTTP requests

#========================================DISCORD API URL========================================
def send_discord_api_url(discord_app_id, api_url, discord_bot_token):

    # send a post to the discord API to set the interactions endpoint to the API Gateway URL
    discordResponse = http.request(
        "PATCH",
        f"https://discord.com/api/v10/applications/{discord_app_id}",

        headers={
            "Authorization": f"Bot {discord_bot_token}",  # authenticate the request with the bot token
            "Content-Type": "application/json"  # specify that the request body is in JSON
        },

        body=json.dumps({
            "interactions_endpoint_url": api_url  # the API Gateway URL to set as the interactions endpoint
        })
    )

    # make sure the request was successful
    if discordResponse.status != 200:
        raise Exception(f"Failed to set Discord interactions endpoint: {discordResponse.status} - {discordResponse.data} :(")
    else:
        print("API Gateaway URL set on Discord application :)")
