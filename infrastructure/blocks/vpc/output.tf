output "vpc_id" {
  value       = module.vpc.vpc_id
  description = "The id of the vpc for the app"
}

output "private_subnets_ids" {
  value       = module.vpc.private_subnets
  description = "The ids of the private subnets"
}

output "public_subnets_ids" {
  value       = module.vpc.public_subnets
  description = "The ids of the public subnets"
}
