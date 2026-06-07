


plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "aws" {
  enabled = true
  version = "0.x.x"   # ← put the current version from the tflint-ruleset-aws releases page
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}