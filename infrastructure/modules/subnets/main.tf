# Subnets
# Private subnets
resource "aws_subnet" "private_subnet" {
  count             = length(data.aws_availability_zones.available.names)
  vpc_id            = var.vpc_id
  cidr_block        = length(var.private_subnet_cidrs) > 0 ? var.private_subnet_cidrs[count.index] : cidrsubnet(var.vpc_cidr_range, var.private_subnet_size, var.private_subnet_offset + count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge({
    Name = "${local.private_subnet_prefix}_${replace(
      data.aws_availability_zones.available.names[count.index],
      "-",
      "_",
    )}"
    Scope = "private" },
  var.tags)
}

resource "aws_route_table_association" "core_private_route_table_association" {
  count          = length(data.aws_availability_zones.available.names)
  subnet_id      = aws_subnet.private_subnet[count.index].id
  route_table_id = var.core_private_route_table_ids[count.index]
}
