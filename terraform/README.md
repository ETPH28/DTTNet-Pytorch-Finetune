# Terraform Setup (S3 + EC2/ASG)

This directory provides two Terraform stacks:

- `s3/`: creates an artifacts bucket for checkpoints/logs.
- `ec2/`: creates an Auto Scaling Group for GPU training instances with optional Spot usage and boot-time training startup.
- `augmentation/`: launches a cheaper one-off EC2 worker that syncs dataset from S3, runs augmentation, uploads outputs, then shuts down.

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

## 3) Run One-Off Augmentation Worker

```bash
cd ../augmentation
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
terraform init
terraform plan
terraform apply
```

This stack is intended as a batch job. With `terminate_on_completion=true`, the instance powers off and terminates itself after upload finishes.

## Notes

- The EC2 stack uses cloud-init `user_data` to install dependencies and run your training command at boot.
- Instances write logs to `/var/log/dtt-bootstrap.log` and `/var/log/dtt-train.log`.
- If using Spot, ASG will replace interrupted instances automatically.
- Checkpoint frequently to S3 in your training command so restarts can resume.
- Data pipeline toggles (in `ec2/terraform.tfvars`):
  - `sync_dataset_on_boot`: pull dataset from S3 to local disk.
  - `proposed_augmentation_s3_prefix`: optional pull of proposed augmentation variants (e.g. `s3://.../custom_aug`) into `${local_data_dir}/custom_aug`.
  - `enable_data_augmentation`: run `src/utils/data_augmentation.py` on instance.
  - `augmentation_upload_s3_prefix`: push augmented dataset back to S3.
  - `initial_weights_s3_uri`: optional base checkpoint used to initialize fine-tuning weights (without optimizer state resume).
  - `checkpoint_sync_interval_seconds`: periodic upload interval for `.ckpt` files while training runs.
  - `run_training_on_boot`: disable to evaluate instance setup without launching training.
