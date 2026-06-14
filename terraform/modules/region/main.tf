


#==============================================================================
#                               S3 BUCKET
#==============================================================================
#       The S3 bucket is what holds all the world data within this region.
#    This lets file transfers between the S3 and Ec2 instances be very fast and
#    super cheap.
#-----------------------------------------------------------------------------
# ===============================BUCKET CREATION===============================
resource "aws_s3_bucket" "world_data_bucket" {

  bucket = "craftform-${var.region}-${var.aws_id}"  # bucket names from variables.tf

}
# ==============================BUCKET VERSIONING==============================
# this is kind of unneeded since versioning is disabled by default but i like to be explicit
resource "aws_s3_bucket_versioning" "versioning" {

  bucket = aws_s3_bucket.world_data_bucket.id  # specificying the bucket created above

  versioning_configuration {
    status = "Disabled" # versioning is disabled for world-data bucket
  }

}
# ==============================PUBLIC ACCESS BLOCK=============================
# prevent public access to the bucket via ACLs at the account/bucket level
resource "aws_s3_bucket_public_access_block" "public_access_block" {  

  bucket = aws_s3_bucket.world_data_bucket.id

  # -------------------BLOCK PUBLIC ACCESS CONFIGURATION-------------------
  block_public_acls       = true  # stops ACLs from being applied
  block_public_policy     = true  # stops policies from being applied
  ignore_public_acls      = true  # ignores any ACLs that may be applied
  restrict_public_buckets = true  # restricts the bucket from being public public 

}

# make sure that the only person in control of the bucket objects is the aws account owner
resource "aws_s3_bucket_ownership_controls" "ownership" {

  bucket = aws_s3_bucket.world_data_bucket.id

  # control who owns all objects inside the bucket. 
  rule{
    object_ownership = "BucketOwnerEnforced"
  }
}
# ===============================BUCKET ENCRYPTION==============================
resource "aws_s3_bucket_server_side_encryption_configuration" "encryption"{

  bucket = aws_s3_bucket.world_data_bucket.id

  # make sure everything uploaded into the bucket is encrypted
  rule {  
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }

}

#==============================================================================
#                                   VPC
#==============================================================================
#       The VPC is the virtual network that everything that needs to be 
#  reachable via the internet is in (ec2, s3 gateawy, subnets, etc.)
#-----------------------------------------------------------------------------
# =================================VPC CREATION================================
resource "aws_vpc" "main_vpc"{
  # kind of a huge cidr block, but doesn't really matter and it's something that
  # will never run out and people can just go crazy with
  cidr_block = "10.0.0.0/16"

  enable_dns_hostnames = true   # needed for ssm session manager
}
# ==================================AWS ZONES==================================
data "aws_availability_zones" "available" {

  state = "available" # get the aws zones that are available to the region
}

# build out a little map for the aws zones
locals {

  # pair each aws zone with it's own cidr
  public_subnets = {
    for index, az in data.aws_availability_zones.available.names :
      az => cidrsubnet(aws_vpc.main_vpc.cidr_block, 10, index) # each az name (key) gets a cidr block (value)
  }

}
# ================================PUBLIC SUBNETS================================
# one public subnet per AZ
resource "aws_subnet" "public" {

  for_each                 = local.public_subnets # computed for each entry in public_subnets
  vpc_id                   = aws_vpc.main_vpc.id  # the vpc that the subnets are deployed into
  availability_zone        = each.key   # the name of the 'n' availability zone
  cidr_block               = each.value # the cidr block of the 'n' availability zone
  map_public_ip_on_launch  = true     # gives resources deployed into subnet a public IP by default
}
# =====================================IGW=====================================
resource "aws_internet_gateway" "main_gw" {
  vpc_id = aws_vpc.main_vpc.id
}
# =================================ROUTE TABLE=================================
resource "aws_route_table" "main_routeTable" {
  
  vpc_id = aws_vpc.main_vpc.id

  # any traffic heading outside of the vpc, direct through the igw
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_gw.id
  }

}