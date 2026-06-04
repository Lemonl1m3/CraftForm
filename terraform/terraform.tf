# version requirements for Terraform and providers

terraform{
    required_version = ">= 1.11.0"  # has to be greater than or equal to 1.11.0 to do state locking on S3


    #========================PROVIDER CONFIGURATION========================
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 6.0"
        }
    }
    #========================BACKEND CONFIGURATION========================
    backend "s3"{
        use_lockfile = true    # enables state locking directly in the S3 bucket

        # bucket, key, and region are dynamic and are injected from the workflow
    }
}