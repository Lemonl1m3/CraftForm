# calls modules, locals and data sources to create the infrastructure







provider "aws" {    # where Terraform should deploy to

  region = var.region   # what region Terraform knows to deploy to


  default_tags {    # tagging for all the created resources -- really useful for the IAM policy
    tags = {
      "Project" = "craftForm"
    }
  }


}



module "region" {
  source = "./modules/region"   # call the region module

  region = var.region   # mainly for naming conventions

  aws_id = var.aws_id
  
}