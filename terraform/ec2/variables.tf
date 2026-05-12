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
  description = "VPC ID where instances run."
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for ASG placement."
  type        = list(string)
}

variable "ami_id" {
  description = "AMI ID for GPU instances (recommended: AWS DLAMI GPU image)."
  type        = string
}

variable "instance_types" {
  description = "Ordered candidate instance types for ASG mixed policy."
  type        = list(string)
  default     = ["g6e.xlarge"]
}

variable "key_name" {
  description = "Optional EC2 key pair name for SSH."
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

variable "root_device_name" {
  description = "Root block device name."
  type        = string
  default     = "/dev/sda1"
}

variable "root_volume_size_gb" {
  description = "Root EBS volume size in GB."
  type        = number
  default     = 1024
}

variable "root_volume_iops" {
  description = "gp3 IOPS."
  type        = number
  default     = 3000
}

variable "root_volume_throughput" {
  description = "gp3 throughput (MiB/s)."
  type        = number
  default     = 125
}

variable "min_size" {
  description = "ASG min size."
  type        = number
  default     = 1
}

variable "max_size" {
  description = "ASG max size."
  type        = number
  default     = 4
}

variable "desired_capacity" {
  description = "ASG desired instance count."
  type        = number
  default     = 1
}

variable "on_demand_base_capacity" {
  description = "On-demand base capacity in mixed instances policy."
  type        = number
  default     = 0
}

variable "on_demand_percentage_above_base_capacity" {
  description = "100 means all On-Demand. 0 means all Spot above base capacity."
  type        = number
  default     = 100
}

variable "spot_allocation_strategy" {
  description = "Spot allocation strategy for ASG mixed policy."
  type        = string
  default     = "capacity-optimized"
}

variable "artifacts_bucket" {
  description = "S3 bucket for checkpoints/logs/data."
  type        = string
}

variable "data_bucket_names" {
  description = "Additional S3 bucket names to allow dataset sync (without s3:// prefix)."
  type        = list(string)
  default     = []
}

variable "artifacts_prefix" {
  description = "Prefix used for checkpoints and logs inside artifacts bucket."
  type        = string
  default     = "dtt-runs"
}

variable "dataset_s3_prefix" {
  description = "Optional dataset prefix (e.g. s3://bucket/musdb18HQ). Leave empty to skip sync."
  type        = string
  default     = ""
}

variable "dataset_upload_s3_prefix" {
  description = "Optional destination prefix to upload local dataset (e.g. s3://bucket/musdb18HQ)."
  type        = string
  default     = ""
}

variable "augmentation_upload_s3_prefix" {
  description = "Optional destination prefix to upload augmented dataset."
  type        = string
  default     = ""
}

variable "sync_dataset_on_boot" {
  description = "If true, sync dataset from dataset_s3_prefix to local_data_dir at boot."
  type        = bool
  default     = true
}

variable "sync_dataset_to_s3_on_boot" {
  description = "If true, sync local_data_dir to dataset_upload_s3_prefix at boot."
  type        = bool
  default     = false
}

variable "enable_data_augmentation" {
  description = "If true, run src/utils/data_augmentation.py against local_data_dir after download."
  type        = bool
  default     = false
}

variable "run_training_on_boot" {
  description = "If true, launch training command in background at boot."
  type        = bool
  default     = true
}

variable "repo_url" {
  description = "Git URL for the training repo."
  type        = string
  default     = "https://github.com/your-org/DTTNet-Pytorch-Finetune.git"
}

variable "git_branch" {
  description = "Git branch to checkout."
  type        = string
  default     = "main"
}

variable "local_repo_dir" {
  description = "Path on instance where repo is cloned."
  type        = string
  default     = "/opt/DTTNet-Pytorch-Finetune"
}

variable "local_data_dir" {
  description = "Path on instance where dataset is stored."
  type        = string
  default     = "/data/musdb18HQ"
}

variable "training_command" {
  description = "Training command executed at boot."
  type        = string
  default     = "python train.py experiment=vocals_dis datamodule=musdb_dev14 trainer=default trainer.devices=1 model.bn_norm=BN ~trainer.sync_batchnorm datamodule.batch_size=4"
}

variable "tags" {
  description = "Additional tags."
  type        = map(string)
  default     = {}
}
