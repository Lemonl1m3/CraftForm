# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                               CraftForm                                      ║
# ╠══════════════════════════════════════════════════════════════════════════════╣
# ║  OPERATIONS LAMBDA  ::  aws_clients.py                                       ║
# ║  One shared home for the boto3 clients used across the command handlers.     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ==========================================================================================
#                               SHARED AWS CLIENTS
# ==========================================================================================
# these live at module level on purpose -- lambda builds them ONCE per cold start and reuses
# this way we don't have to rebuild the clients everytime to call them
# ------------------------------------------------------------------------------------------
import boto3

ssm           = boto3.client("ssm")             # parameter store -- config + per-region discovery
secrets       = boto3.client("secretsmanager")  # the github PAT (for dispatching workflows)
lambda_client = boto3.client("lambda")          # invoking other craftform functions (e.g. /update -> staging)
