resource "null_resource" "packer_build" {
  triggers = {
    sha256_ami_config  = filesha256("${path.module}/template.json")
    sha256_ami_install = filesha256("${path.module}/install.sh")
    version            = var.pipeline_ami_version
  }

  provisioner "local-exec" {
    command = <<EOF
    set -ex;
    PACKER_LOG=1 packer validate \
      -var "version=${var.pipeline_ami_version}" \
      -var "subnet_id=${data.terraform_remote_state.vpc-state.outputs.public_subnets_ids[0]}" \
      -var "vpc_id=${data.terraform_remote_state.vpc-state.outputs.vpc_id}" \
      -var "region=${var.aws_region}" \
      template.json
    PACKER_LOG=1 packer build \
      -var "version=${var.pipeline_ami_version}" \
      -var "subnet_id=${data.terraform_remote_state.vpc-state.outputs.public_subnets_ids[0]}" \
      -var "vpc_id=${data.terraform_remote_state.vpc-state.outputs.vpc_id}" \
      -var "region=${var.aws_region}" \
      template.json
EOF
  }
}
