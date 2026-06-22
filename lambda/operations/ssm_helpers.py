# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                               CraftForm                                      ║
# ╠══════════════════════════════════════════════════════════════════════════════╣
# ║  OPERATIONS LAMBDA  ::  ssm_helpers.py                                       ║
# ║  Little shared helpers for poking around the SSM parameter store.            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ==========================================================================================
#                               SSM PARAMETER HELPERS
# ==========================================================================================
# almost all of the command code uses the ssm parameter store the same way and the tree
# is built in a way that listing it is relatively easy. this acts as a shared helper to help
# minimize the code in other files
# ------------------------------------------------------------------------------------------
import json
from aws_clients import ssm  # shared client -- made once per cold start


# ===============================LIST NAMES UNDER A PREFIX===============================
# pull the resource names sitting directly under a prefix.
def list_names_under(prefix):

    # make sure we've got the trailing slash so the strip + split below lines up
    if not prefix.endswith("/"):
        prefix += "/"

    names = []

    # paginate -- get_parameters_by_path caps at 10 results a page, so we have to loop
    paginator = ssm.get_paginator("get_parameters_by_path")
    for page in paginator.paginate(Path=prefix, Recursive=True):
        for param in page["Parameters"]:
            # chop the prefix off, then take the FIRST segment after it = the resource name
            name = param["Name"][len(prefix):].split("/")[0]
            if name and name not in names:  # dedupe -- multiple params per resource is fine
                names.append(name)

    return names


# ===================================GET A JSON PARAM===================================
# a bunch of our params are json blobs
def get_json(name):
    return json.loads(ssm.get_parameter(Name=name)["Parameter"]["Value"])
