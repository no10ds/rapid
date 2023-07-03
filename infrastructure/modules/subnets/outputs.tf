output "private_subnet_ids" {
  value       = aws_subnet.private_subnet[*].id
  description = "A list of private subnet IDs"
}
