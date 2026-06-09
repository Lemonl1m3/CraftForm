


plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "aws" {
  enabled = true
  version = "0.x.x"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}
