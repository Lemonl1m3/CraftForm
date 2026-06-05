

output "bucket_name" {
  description = "The name (id) of the S3 bucket created by this module"
  value       = aws_s3_bucket.bucket.id
}