

terraform apply -auto-approve
ansible-playbook -i inventory.ini ../../job_parser/ansible/playbook.yml
terraform destroy