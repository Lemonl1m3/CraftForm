#╔══════════════════════════════════════════════════════════════════════════════╗
#║                               CraftForm                                      ║
#╠══════════════════════════════════════════════════════════════════════════════╣
#║  STARTUP LAMBDA  ::  github_api.py                                           ║
#║  Handles all GitHub API interactions during initial deployment.              ║
#║  Forks repo, enables Actions, and pushes AWS secrets.                        ║
#╚══════════════════════════════════════════════════════════════════════════════╝
import time
import json
import urllib3
from nacl import encoding, public
from base64 import b64encode

#========================================INITIALIZATION========================================
http = urllib3.PoolManager()    # create a new HTTP connection pool manager to make HTTP requests

#===========================================ENCYPTION===========================================
def encrypt_secret(public_key, secret):
    # decode the Bse64-encoded key GitHub returns
    key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())

    # create a sealed box with that public key
    sealed_box = public.SealedBox(key)

    # encrypt the secret with the sealed box and key, then Base64-encode the result so it can be sent as a string in the GitHub API request
    encrypted = sealed_box.encrypt(secret.encode("utf-8"))

    # encode the result as base64 so it can be sent as a string
    return b64encode(encrypted).decode("utf-8")

#========================================GITHUB FORKING========================================
def fork_repo(github_pat, github_username):
    # make a http GET request to ask Github if the repo already exists in the user's account
    gitResponse = http.request(
         "GET",
         f"https://api.github.com/repos/{github_username}/CraftForm",

         headers = {
             "Authorization": f"token {github_pat}",
             "Accept": "application/vnd.github.v3+json"
        }
    )
    # if the repo already exists, skip the forking process
    if gitResponse.status == 200:
        print("Repo already forked :)")
        return
    
    # fork the CrafForm repo into the user's GitHub account using the Github API and provided PAT
    gitResponse = http.request(

        "POST",
        "https://api.github.com/repos/Liamade/CraftForm/forks",    # the repo to fork - Liamade/CraftForm

        # authenticate the request with the Github PAT and specify that we want to use the GitHub API v3
        headers={
            "Authorization": f"token {github_pat}",   # this request is coming from particular user - use PAT for authentication
            "Accept": "application/vnd.github.v3+json"  # we want the response in the format of GitHub API v3
        }
    )

    # make sure the request was successful
    if gitResponse.status != 202:
        raise Exception(f"Failed to fork repo: {gitResponse.status} - {gitResponse.data} :(")
    else:
        print("Repo forked successfully :)")


    # check and make sure that GitHub fork has finished
    for i in range(10):
        # ask GitHub if the forked repo exists in the user's account
        gitResponse = http.request(
            "GET",
            f"https://api.github.com/repos/{github_username}/CraftForm",  # check the forked repo in the user's account

            headers = {
                "Authorization": f"token {github_pat}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        if gitResponse.status == 200:
            print("Fork is ready :)")
            break
               
        print("Fork still combombulating, waiting...")
        print(f"Attempt: {i+1}")
        time.sleep(3) # wait for a few seconds before checking again
    else:
        raise Exception("Forking took too long :(")


#========================================GITHUB ACTIONS========================================
def enable_github_actions(github_pat, github_username):

    # enable GitHub Actions in the forked repo
    gitResponse = http.request(
        "PUT",
        f"https://api.github.com/repos/{github_username}/CraftForm/actions/permissions",
        
        headers= {
            "Authorization": f"token {github_pat}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"   # says "I'm sending JSON data in the body of this request"
        },

        body=json.dumps({
            "enabled": True,  # enable GitHub Actions in the forked repo
            "allowed_actions": "all"  # allow all actions in GitHub Actions
        })
    )

    # make sure the request was succesful
    if gitResponse.status != 204:  # GitHub API returns a 204 No Content status code for a successful request to enable Actions
        raise Exception(f"Failed to enable GitHub Actions: {gitResponse.status} - {gitResponse.data} :(")
    else:
        print("GitHub Actions enabled :)")


#========================================GITHUB IAM ROLE========================================
def push_secretsTo_github(github_pat, github_username, role_arn):

    # get the public key from GitHub to encrypt the secret before pushing it to GitHub
    # this is required by GitHub - all secrets have to be encrypted with GitHub's public key
    keyResponse = http.request(
        "GET",
        f"https://api.github.com/repos/{github_username}/CraftForm/actions/secrets/public-key",  # get the public key for encrypting secrets in GitHub

        headers = {
            "Authorization": f"token {github_pat}",
            "Accept": "application/vnd.github.v3+json",
        }
    )

    # make sure the public key request was successful
    if keyResponse.status != 200:
        raise Exception(f"Failed to get public key: {keyResponse.status} - {keyResponse.data} :(")
    else:
        print("Public key came back :)")

    # extract the public key from the response
    # we capture both the public key and the key ID
    # Public Key - used to encrypt the secret before sending it to GitHub
    # Key ID     - included in the request to GitHub when pushing the secret
    keyData    = json.loads(keyResponse.data.decode("utf-8"))
    public_key = keyData["key"]  # the public key to encrypt secrets with
    key_id     = keyData["key_id"]  # the key ID to include in the request to GitHub when pushing secrets

    # encrypt the GitHub secret  with the public key
    # GitHub requires that all secrets pushed to GitHub are encrypted with the Public Key captured
    encrypted_secret = encrypt_secret(public_key, role_arn)

    # push the encrypted secret to GitHub using the API - this will make the secret available in the forked repo
    # GitHub Actions will be able to access this secret and use it within it's workflows and pipelines
    gitResponse = http.request(
        "PUT",
        f"https://api.github.com/repos/{github_username}/CraftForm/actions/secrets/AWS_ROLE_ARN",  # name of the secret in GitHub - AWS_ROLE_ARN

        headers = {
            "Authorization": f"token {github_pat}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"  
        },
        body=json.dumps({
            "encrypted_value": encrypted_secret,
            "key_id": key_id
        })
    )

    # make sure the request to push the secret was successful
    if gitResponse.status not in [201, 204]:  # GitHub API returns a 201 Created status code for a new secret and a 204 No Content status code for an updated secret
        raise Exception(f"Failed to push secret: {gitResponse.status} - {gitResponse.data} :(")
    else:
        print("Secret placed :)")