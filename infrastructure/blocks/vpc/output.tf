output "vpc_id" {
  value       = module.core_vpc.vpc_id
  description = "The id of the vpc for the app"
}

output "private_subnets_ids" {
  value       = module.core_vpc.private_subnet_ids
  description = "The ids of the private subnets"
}

output "public_subnets_ids" {
  value       = module.core_vpc.public_subnet_ids
  description = "The ids of the public subnets"
}
