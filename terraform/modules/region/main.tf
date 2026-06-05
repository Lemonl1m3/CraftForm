


#==============================================================================
#                               S3 BUCKET
#==============================================================================
#       The S3 bucket is what holds all the world data within this region.
#    This lets file transfers between the S3 and Ec2 instances be very fast and
#    super cheap.
#-----------------------------------------------------------------------------
#===============================BUCKET CREATION===============================
resource "aws_s3_bucket" "bucket" {

  bucket = var.bucket_name  # bucket names from variables.tf

}
#==============================BUCKET VERSIONING==============================
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.bucket.id  # specificying the bucket created above

  versioning_configuration {
    status = "Disabled" # versioning is disabled for world-data bucket
  }

}
#==============================PUBLIC ACCESS BLOCK=============================
resource "aws_s3_bucket_public_access_block" "public_access_block" {  
  bucket = aws_s3_bucket.bucket.id

  #-------------------BLOCK PUBLIC ACCESS CONFIGURATION-------------------
  block_public_acls       = true  # stops ACLs from being applied
  block_public_policy     = true  # stops policies from being applied
  ignore_public_acls      = true  # ignores any ACLs that may be applied
  restrict_public_buckets = true  # restricts the bucket from being public public 

}