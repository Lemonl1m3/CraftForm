# declares the variables used in the terraform config



# ====================================REGION====================================
variable "region" {
  description = "The AWS region to deploy to. Dynamic and injected from AWS Lambda"
  type        = string
}

# ==================================HOME REGION==================================
variable "home_region" {
  description = "The control-plane (home) region where shared SSM config is read by the Lambda. Injected from the workflow's HOME_REGION."
  type        = string
}

