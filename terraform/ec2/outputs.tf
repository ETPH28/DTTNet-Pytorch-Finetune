output "asg_name" {
  description = "Auto Scaling Group name."
  value       = aws_autoscaling_group.training_asg.name
}

output "launch_template_id" {
  description = "Launch Template ID."
  value       = aws_launch_template.training.id
}

output "security_group_id" {
  description = "Training security group ID."
  value       = aws_security_group.training_sg.id
}
