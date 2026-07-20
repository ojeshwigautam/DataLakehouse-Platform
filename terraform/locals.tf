locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Repository  = "DataLakehouse-Platform"
    Owner       = "unknown"
  }
}

