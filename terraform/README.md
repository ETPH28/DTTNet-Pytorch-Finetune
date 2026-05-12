# Terraform Setup (S3 + EC2/ASG)

This directory provides two Terraform stacks:

- `s3/`: creates an artifacts bucket for checkpoints/logs.
- `ec2/`: creates an Auto Scaling Group for GPU training instances with optional Spot usage and boot-time training startup.

## Prereqs

1. Terraform `>= 1.5`
2. AWS CLI configured (`aws configure` or SSO)
3. A valid AWS profile and region

## 1) Create S3 Bucket

```bash
cd terraform/s3
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
terraform init
terraform plan
terraform apply
```

Record the output bucket name, then use it in the EC2 stack as `artifacts_bucket`.

## 2) Create EC2/ASG Training Infra

```bash
cd ../ec2
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
terraform init
terraform plan
terraform apply
```

## Notes

- The EC2 stack uses cloud-init `user_data` to install dependencies and run your training command at boot.
- Instances write logs to `/var/log/dtt-bootstrap.log` and `/var/log/dtt-train.log`.
- If using Spot, ASG will replace interrupted instances automatically.
- Checkpoint frequently to S3 in your training command so restarts can resume.
