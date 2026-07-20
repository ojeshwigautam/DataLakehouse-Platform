variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "allowed_ssh_ip" {
  type        = string
  description = "CIDR allowed for SSH"
}





variable "tags" {
  type = map(string)
}


