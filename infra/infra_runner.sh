#!/bin/bash

eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa

# Function to check the exit status of a command and exit if error
exit_if_error() {
  if [ $? -ne 0 ]; then
    echo "Error: $1 failed. Exiting."
    exit 1
  fi
}


# Function to just check the exit status. This does not exit the  script if there is error just displays
check_exit_status() {
   if [ $? -ne 0 ]; then
	echo "Error: $1 failed check log"
   fi
}


cd terraform || { echo "Failed to change directory to terraform. Exiting."; exit 1; }

# Apply Terraform configuration
echo "Applying Terraform configuration..."
terraform apply -auto-approve
exit_if_error "Terraform apply"
echo "Terraform apply completed successfully."

# Make sure ec2 boots up
echo "Sleeping for 60 seconds"
sleep 60


# Run Ansible playbook
cd ../

echo "Running Ansible playbook..."
ansible-playbook -vvvv -i terraform/inventory.ini ansible/playbook.yml
check_exit_status "Ansible playbook"
echo "Ansible playbook completed"

# Destroy Terraform configuration
cd terraform || { echo "Failed to change directory to terraform. Exiting."; exit 1; }

echo "Destroying Terraform configuration..."
terraform destroy -auto-approve
check_exit_status "Terraform destroy"
echo "Terraform destroy completed"



