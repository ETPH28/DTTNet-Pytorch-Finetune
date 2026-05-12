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

variable "vpc_id" {
  description = "VPC ID for the augmentation instance."
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for the augmentation instance."
  type        = string
}

variable "ami_id" {
  description = "AMI ID for the instance (Ubuntu recommended)."
  type        = string
}

variable "instance_type" {
  description = "Cheaper VM for augmentation workload."
  type        = string
  default     = "c6i.2xlarge"
}

variable "key_name" {
  description = "Optional EC2 key pair."
  type        = string
  default     = ""
}

variable "enable_ssh_ingress" {
  description = "Whether to allow inbound SSH."
  type        = bool
  default     = false
}

variable "ssh_cidr" {
  description = "CIDR range allowed for SSH."
  type        = string
  default     = "0.0.0.0/0"
}

variable "root_volume_size_gb" {
  description = "Root EBS size in GB. Keep >= 1100 GB for full augmentation."
  type        = number
  default     = 1200
}

variable "root_volume_iops" {
  description = "gp3 IOPS."
  type        = number
  default     = 3000
}

variable "root_volume_throughput" {
  description = "gp3 throughput in MiB/s."
  type        = number
  default     = 125
}

variable "source_bucket_name" {
  description = "Source bucket name (no s3://)."
  type        = string
}

variable "destination_bucket_name" {
  description = "Destination bucket name (no s3://)."
  type        = string
}

variable "source_s3_prefix" {
  description = "Source dataset prefix, e.g. s3://bucket/musdb18HQ"
  type        = string
}

variable "destination_s3_prefix" {
  description = "Destination prefix for augmented outputs, e.g. s3://bucket/musdb18HQ-aug"
  type        = string
}

variable "repo_url" {
  description = "Git URL for this repository."
  type        = string
  default     = "https://github.com/your-org/DTTNet-Pytorch-Finetune.git"
}

variable "git_branch" {
  description = "Git branch to checkout."
  type        = string
  default     = "main"
}

variable "local_repo_dir" {
  description = "Repo directory on the instance."
  type        = string
  default     = "/opt/DTTNet-Pytorch-Finetune"
}

variable "local_data_dir" {
  description = "Local dataset directory on instance."
  type        = string
  default     = "/data/musdb18HQ"
}

variable "run_train_split" {
  description = "Augment train split."
  type        = bool
  default     = true
}

variable "run_valid_split" {
  description = "Augment valid split."
  type        = bool
  default     = false
}

variable "run_test_split" {
  description = "Augment test split."
  type        = bool
  default     = false
}

variable "terminate_on_completion" {
  description = "Shutdown on completion; with instance initiated shutdown behavior set to terminate."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags."
  type        = map(string)
  default     = {}
}
