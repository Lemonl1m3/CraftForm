# declares the variables used in the terraform config


variable "region" {
  description = "The AWS region to deploy to. Dynamic and injected from AWS Lambda"
  type        = string
}

variable "aws_id"{
  description = "The AWS ID for the user"
  type        = string
}