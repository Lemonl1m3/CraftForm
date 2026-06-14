


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
# ==============================ROUTE ASSOCIATIONS==============================
# link every public subnet to the main route table
resource "aws_route_table_association" "public" {

  for_each = aws_subnet.public    # for each public subnet created
  subnet_id = each.value.id       # subnet's id
  route_table_id = aws_route_table.main_routeTable.id   # point to this route table

}
# ================================S3 VPC ENDPOINT================================
resource "aws_vpc_endpoint" "s3" {

  vpc_id = aws_vpc.main_vpc.id
  service_name = "com.amazonaws.${var.region}.s3" # the resource for the specific region this endpoint reaches
  vpc_endpoint_type = "Gateway"
  route_table_ids = [aws_route_table.main_routeTable.id]  # the route table the endpoint gets linked to
}

#==============================================================================
#                                 SECURITY
#==============================================================================
#       The resources that help control the security going inside and outside
#  of the home region. Helps dictate traffice and who allows to access resources
#-----------------------------------------------------------------------------
# ================================SECURITY GROUP================================
# the security group to dictate what kind of traffic can reach the ec2 instances
resource "aws_security_group" "allow_MC" {

  name = "allow_MC"
  description = "Allow TCP inbound traffic through minecraft port"
  vpc_id = aws_vpc.main_vpc.id

}
# INBOUND RULES
resource "aws_vpc_security_group_ingress_rule" "allow_TCP" {

  security_group_id = aws_security_group.allow_MC.id
  cidr_ipv4 = "0.0.0.0/0"
  from_port = 25565
  ip_protocol = "tcp"
  to_port = 25565
}
# OUTBOUND RULES
resource "aws_vpc_security_group_egress_rule" "allow_all_out" {
  security_group_id = aws_security_group.allow_MC.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"   # -1 = all protocols
}

# ===================================IAM ROLE===================================
resource "aws_iam_role" "server_role" {
  name = "minecraft_server_role"

  # only ec2 instances are allowed to assume this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement =[
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}
# ===============================S3 ACCESS POLICY===============================
resource "aws_iam_role_policy" "s3_access" {
  name = "allow_s3_acecss"
  role = aws_iam_role.server_role.name

  policy = jsonencode ({
    Version = "2012-10-17"
    Statement = [
      # policy to the actual bucket
      {
        Sid = "BucketLevel"
        Effect = "Allow"
        Action = ["s3:ListBucket"]
        Resource = aws_s3_bucket.world_data_bucket.arn
      },
      # policy to act on objects
      {
        Sid = "ObjectLevel"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = "${aws_s3_bucket.workd_data_bucket.arn}/*"
      }
    ]
  })
}

# ===============================INSTANCE PROFILE===============================
# allows ec2 instances to actually assume the iam role
resource "aws_iam_instance_profile" "server_profile" {

  name = "minecraft_server_profile"
  role = aws_iam_role.server_role.name

}

# ==============================SSM MANAGED POLICY==============================
# allow servers to talk outbound to the ssm service so people can "ssh"
resource "aws_iam_role_policy_attachement" "ssm_core" {

  role = aws_iam_role.server_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"

}