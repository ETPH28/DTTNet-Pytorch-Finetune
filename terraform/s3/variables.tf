variable "aws_region" {
  description = "AWS region."
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile name."
  type        = string
  default     = "default"
}

variable "project_name" {
  description = "Project tag/name prefix."
  type        = string
  default     = "dttnet"
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "bucket_name" {
  description = "Optional explicit bucket name. Leave empty to auto-generate."
  type        = string
  default     = ""
}

variable "force_destroy" {
  description = "Allow deleting non-empty bucket."
  type        = bool
  default     = false
}

variable "enable_lifecycle" {
  description = "Enable object expiration lifecycle."
  type        = bool
  default     = true
}

variable "lifecycle_prefix" {
  description = "Prefix to apply lifecycle policy to."
  type        = string
  default     = "checkpoints/"
}

variable "lifecycle_expiration_days" {
  description = "Delete current objects after N days."
  type        = number
  default     = 30
}

variable "lifecycle_noncurrent_days" {
  description = "Delete non-current object versions after N days."
  type        = number
  default     = 14
}

variable "tags" {
  description = "Additional tags."
  type        = map(string)
  default     = {}
}
