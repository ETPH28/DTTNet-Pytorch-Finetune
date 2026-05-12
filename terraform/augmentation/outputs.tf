output "augmentation_instance_id" {
  description = "Instance ID running augmentation."
  value       = aws_instance.augment_worker.id
}

output "augmentation_instance_private_ip" {
  description = "Private IP of augmentation instance."
  value       = aws_instance.augment_worker.private_ip
}

output "augmentation_instance_state" {
  description = "Current instance state."
  value       = aws_instance.augment_worker.instance_state
}
