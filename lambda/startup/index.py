#╔══════════════════════════════════════════════════════════════════════════════╗
#║                              CraftForm                                       ║
#╠══════════════════════════════════════════════════════════════════════════════╣
#║  STARTUP LAMBDA  ::  index.py                                                ║
#║  Entry point for the CloudFormation Custom Resource startup function.        ║
#║  Orchestrates GitHub and Discord setup on first deployment.                  ║
#╚══════════════════════════════════════════════════════════════════════════════╝

import urllib3
import json
import boto3
import os  # for accessing environment variables injected into the Lambda
import discord_api
import github_api


# main handler function for the Lambda function - entry point for the Lambda
def handler(event, context):

    # ===============================INJECTED VARIABLES===============================

    awsApi_url      = os.environ["ApiGatewayUrl"]
    gitRole_arn     = os.environ["GithubActionsRoleArn"]
    github_username = os.environ["GitHubUsername"]
    discord_app_id  = os.environ["DiscordAppId"]
    
    #==================================INITIALIZATION=================================

    http = urllib3.PoolManager()    # create a new HTTP connection pool manager to make HTTP requests
    ssm  = boto3.client("ssm")   # create a AWS System Manager client to interact with SSM Parameter Store
    secretsManager = boto3.client("secretsmanager")   # create a AWS Secrets Manager client to interact with Secrets Manager
    secrets = secretsManager.get_secret_value(SecretId="craftForm-secrets")   # get the secret value for the secret named "craftForm-secrets" from Secrets Manager
    secrets_dict = json.loads(secrets["SecretString"])   # the secret value is a JSON string

    #==================================API EXECUTION==================================
    
    try:
        #-----------------------GITHUB INTEGRATION------------------------
        github_pat = secrets_dict["GitHub-PAT"]   # get the GitHub Personal Access Token from the secrets dictionary

        github_api.fork_repo(github_pat, github_username)   # fork the CraftForm repo into the user's GitHub account and wait for the fork to be ready

        github_api.enable_github_actions(github_pat, github_username)  # enable GitHub Actions in the forked repo

        github_api.push_secretsTo_github(github_pat, github_username, gitRole_arn)   # push the AWS API Gateway URL and GitHub Actions Role ARN as encrypted secrets to the forked GitHub repo

        # store the GitHub forked repo URL into SSM parameter store 
        ssm.put_parameter(
            Name      =  "/craftform/config/github_repo", 
            Value     =  f"{github_username}/CraftForm", 
            Type      =  "String", 
            Overwrite =  True
        )

        #-----------------------DISCORD INTEGRATION-----------------------
        
        discord_bot_token = secrets_dict["Discord-Bot-Token"]   # get the bot token from Secret Manager

        discord_api.send_discord_api_url(discord_app_id, awsApi_url, discord_bot_token)   # set the API Gateway URL as the interactions endpoint in the Discord







        #------------------------SUCCESS RESPONSE-------------------------
        response = {
            "Status": "SUCCESS",
            "PhysicalResourceId": "craftform-startup",
            "StackId": event["StackId"],
            "RequestId": event["RequestId"],
            "LogicalResourceId": event["LogicalResourceId"]
        }



    # if any errors or failures happen - report to cloudformation with failure status and error message    
    except Exception as e:
        response = {
            "Status": "FAILED",
            "Reason": str(e),
            "PhysicalResourceId": "craftform-startup",
            "StackId": event["StackId"],
            "RequestId": event["RequestId"],
            "LogicalResourceId": event["LogicalResourceId"]
        }
    
    

    #==================================CLOUDFORMATION RESPONSE=========================
    http.request(
        "PUT",
        event["ResponseURL"],
        body=json.dumps(response),
        headers={"Content-Type": "application/json"}
    )