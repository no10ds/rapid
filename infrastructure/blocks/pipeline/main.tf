resource "aws_instance" "pipeline" {
  #checkov:skip=CKV_AWS_135:EBS Optimised not available for instance type
  ami                         = data.aws_ami.this.id
  instance_type               = "t3.medium"
  associate_public_ip_address = false
  iam_instance_profile        = aws_iam_instance_profile.pipeline_instance_profile.name
  subnet_id                   = data.terraform_remote_state.vpc-state.outputs.private_subnets_ids[0]
  user_data = templatefile("${path.module}/initialisation-script.sh.tpl", {
    runner-registration-token = var.runner-registration-token
  })
  monitoring             = true
  vpc_security_group_ids = [aws_security_group.this.id]

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    encrypted   = true
    volume_size = 64
  }

  tags = merge(
    var.tags,
    {
      Name = "github-action-runner"
    },
  )
}

resource "aws_iam_instance_profile" "pipeline_instance_profile" {
  name = "pipeline_instance_profile"
  role = aws_iam_role.pipeline_ecr_role.name
}

resource "aws_security_group" "this" {
  vpc_id      = data.terraform_remote_state.vpc-state.outputs.vpc_id
  name        = "${var.resource-name-prefix}-pipeline-sg"
  description = "Pipeline security group"
}

resource "aws_security_group_rule" "this" {
  type              = "egress"
  description       = "Allow all outbound traffic"
  from_port         = 0
  to_port           = 65535
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.this.id
}
