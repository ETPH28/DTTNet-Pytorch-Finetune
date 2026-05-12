terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

locals {
  name_prefix = "${var.project_name}-${var.environment}-augment"
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Workload    = "augmentation"
    },
    var.tags
  )
}

resource "aws_iam_role" "instance_role" {
  name = "${local.name_prefix}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy" "s3_access" {
  name = "${local.name_prefix}-s3"
  role = aws_iam_role.instance_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:ListBucket"]
        Resource = [
          "arn:aws:s3:::${var.source_bucket_name}",
          "arn:aws:s3:::${var.destination_bucket_name}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::${var.source_bucket_name}/*",
          "arn:aws:s3:::${var.destination_bucket_name}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "instance_profile" {
  name = "${local.name_prefix}-profile"
  role = aws_iam_role.instance_role.name
}

resource "aws_security_group" "augment_sg" {
  name        = "${local.name_prefix}-sg"
  description = "Security group for one-off data augmentation node"
  vpc_id      = var.vpc_id
  tags        = local.tags
}

resource "aws_vpc_security_group_egress_rule" "all_egress" {
  security_group_id = aws_security_group.augment_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_vpc_security_group_ingress_rule" "ssh_ingress" {
  count             = var.enable_ssh_ingress ? 1 : 0
  security_group_id = aws_security_group.augment_sg.id
  cidr_ipv4         = var.ssh_cidr
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
}

resource "aws_instance" "augment_worker" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.augment_sg.id]
  key_name               = var.key_name == "" ? null : var.key_name
  iam_instance_profile   = aws_iam_instance_profile.instance_profile.name

  instance_initiated_shutdown_behavior = var.terminate_on_completion ? "terminate" : "stop"

  root_block_device {
    volume_size           = var.root_volume_size_gb
    volume_type           = "gp3"
    iops                  = var.root_volume_iops
    throughput            = var.root_volume_throughput
    delete_on_termination = true
    encrypted             = true
  }

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  user_data = templatefile("${path.module}/user_data.sh.tmpl", {
    repo_url              = var.repo_url
    git_branch            = var.git_branch
    local_repo_dir        = var.local_repo_dir
    local_data_dir        = var.local_data_dir
    source_s3_prefix      = var.source_s3_prefix
    destination_s3_prefix = var.destination_s3_prefix
    run_train_split       = var.run_train_split
    run_valid_split       = var.run_valid_split
    run_test_split        = var.run_test_split
    aws_region            = var.aws_region
    shutdown_on_finish    = var.terminate_on_completion
  })

  tags = merge(local.tags, {
    Name = "${local.name_prefix}"
  })
}
