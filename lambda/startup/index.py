#╔══════════════════════════════════════════════════════════════════════════════╗
#║                              CraftForm                                       ║
#╠══════════════════════════════════════════════════════════════════════════════╣
#║  STARTUP LAMBDA  ::  index.py                                                ║
#║  Entry point for the CloudFormation Custom Resource startup function.        ║
#║  Orchestrates GitHub and Discord setup on first deployment.                  ║
#╚══════════════════════════════════════════════════════════════════════════════╝

import urllib3
import json
import os  # for accessing environment variables injected into the Lambda
import discord_api
import github_api


# main handler function for the Lambda function - entry point for the Lambda
def handler(event, context):
    # ===============================INJECTED VARIABLES===============================
    awsApi_url = os.environ["ApiGatewayUrl"]
    gitRole_arn = os.environ["GithubActionsRoleArn"]
    github_username = os.environ["GitHubUsername"]
    discord_app_id = os.environ["DiscordAppId"]
    github_pat = os.environ["GithubPAT"]

    #==================================API EXECUTION==================================
    http = urllib3.PoolManager()    # create a new HTTP connection pool manager to make HTTP requests
    try:
        #-----------------------GITHUB INTEGRATION------------------------
        github_api.fork_repo(github_pat, github_username)   # fork the CraftForm repo into the user's GitHub account and wait for the fork to be ready

        github_api.enable_github_actions(github_pat, github_username)  # enable GitHub Actions in the forked repo

        github_api.push_secretsTo_github(github_pat, github_username, awsApi_url, gitRole_arn)   # push the AWS API Gateway URL and GitHub Actions Role ARN as encrypted secrets to the forked GitHub repo

        #-----------------------DISCORD INTEGRATION-----------------------




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