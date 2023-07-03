output "vpc_id" {
  value       = aws_vpc.core.id
  description = "The ID of the created VPC"
}

output "public_subnet_ids" {
  value       = aws_subnet.public_subnet[*].id
  description = "A list of public subnet IDs"
}

output "private_subnet_ids" {
  value       = aws_subnet.private_subnet[*].id
  description = "A list of private subnet IDs"
}
