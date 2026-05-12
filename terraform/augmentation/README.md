# One-Off Augmentation Stack

This stack launches a single EC2 worker for dataset augmentation:

1. Syncs dataset from `source_s3_prefix` to local disk.
2. Runs `src/utils/data_augmentation.py`.
3. Syncs results to `destination_s3_prefix`.
4. Optionally shuts down and terminates itself (`terminate_on_completion=true`).

## Usage

```bash
cp terraform.tfvars.example terraform.tfvars
# edit values
terraform init
terraform plan
terraform apply
```

## Cost Guardrails

- Use a cheap CPU instance first (`c6i.2xlarge` default).
- Keep `terminate_on_completion=true`.
- Use only train split unless you need valid/test augmentation.
