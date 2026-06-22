# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                               CraftForm                                      ║
# ╠══════════════════════════════════════════════════════════════════════════════╣
# ║  OPERATIONS LAMBDA  ::  commands/region.py                                   ║
# ║  Handles all /region slash command interactions.                             ║
# ║  Create, delete, and list regions.                                           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import urllib3
import json
from ssm_helpers import list_names_under  # shared ssm helpers (add get_json when you read configs)

# the prefix every deployed region's config lives under
REGIONS_PREFIX = "/craftform/regions/"

# ==========================================================================================
#                                   /REGION COMMAND
# ==========================================================================================
def handle(subcommand, options, body):

    # capture the regions that are already created
    active_regions = list_names_under(REGIONS_PREFIX)
    
    # ================================<CREATE>================================
    if subcommand == "create":
        pass

    # ================================<DELETE>================================
    if subcommand == "delete":
        pass

    # =================================<LIST>=================================
    if subcommand == "list":
        # the whole list_regions loop is now just this :)
        active_regions = list_names_under(REGIONS_PREFIX)
        pass
