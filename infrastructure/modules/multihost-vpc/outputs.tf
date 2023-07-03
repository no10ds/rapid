output "vpc_id" {
  value       = aws_vpc.core.id
  description = "The ID of the created VPC"
}

output "vpc_cidr_range" {
  value       = aws_vpc.core.cidr_block
  description = "The ID of the created VPC"
}

output "private_route_table_ids" {
  value       = aws_route_table.core_private_route_table[*].id
  description = "A list of private route table IDs"
}

output "public_subnet_ids" {
  value       = aws_subnet.public_subnet[*].id
  description = "A list of public subnet IDs"
}
