# Terraform (AWS Infrastructure)

This directory provisions AWS infrastructure for **DataLakehouse-Platform**:

- S3 Data Lake bucket (versioning, encryption, lifecycle rules, public access block)
- IAM Role + Policy + Instance Profile for EC2
- Security Group (SSH ingress)
- EC2 Ubuntu instance (Docker-ready; runs setup via user_data)

## Commands

```bash
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy
```

## Notes

1. Create `terraform.tfvars` from `terraform.tfvars.example`.
2. Ensure the `key_name` exists in your AWS account/region.
3. Ensure `allowed_ssh_ip` is your public IP/CIDR.
4. Ensure `vpc_id` is a valid VPC where you want to deploy the security group + instance.

