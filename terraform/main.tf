module "s3" {
  source = "./modules/s3"

  bucket_name = var.bucket_name
  tags        = local.common_tags
}

module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  environment  = var.environment
  bucket_name  = var.bucket_name
  tags         = local.common_tags
}

module "security_group" {
  source = "./modules/security_group"

  project_name   = var.project_name
  environment    = var.environment
  allowed_ssh_ip = var.allowed_ssh_ip

  tags = local.common_tags
}


module "ec2" {
  source = "./modules/ec2"

  project_name  = var.project_name
  environment   = var.environment
  instance_type = var.instance_type
  key_name      = var.key_name

  iam_instance_profile_name = module.iam.instance_profile_name
  iam_role_arn              = module.iam.role_arn

  security_group_id = module.security_group.security_group_id

  tags = local.common_tags
}

