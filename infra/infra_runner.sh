#!/bin/bash -l


NUM_PROCESSES=20
TIMEOUT_SEC=3600

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

echo
printf '%.0s#' $(seq 1 $term_width)
echo

start=$(date +%s)

#Generate input files
echo "=> Activating environment"
source $PROJ_POSTINGS_PARSER_PATH/env/bin/activate
echo "=> Generating input files"
python $PROJ_POSTINGS_PARSER_PATH/postings_parser/utils/create_input_files.py --num_file $NUM_PROCESSES
echo "=> Done generating input files"


cd $PROJ_POSTINGS_PARSER_PATH/infra/
cd terraform || { echo "Failed to change directory to terraform. Exiting."; exit 1; }

# Apply Terraform configuration
echo "=> Applying Terraform configuration..."
terraform apply -auto-approve
exit_if_error "Terraform apply"
echo "=> Terraform apply completed successfully."

# Make sure ec2 boots up
echo "=> Pausing for 60 seconds for ec2s to boot up"
sleep 60

printf '%.0s#' $(seq 1 $term_width)
echo
# Run Ansible playbook
cd ../

echo "=> Running Ansible playbook..."
timeout $TIMEOUT_SEC ansible-playbook -i $PROJ_POSTINGS_PARSER_PATH/infra/terraform/inventory.ini --forks=$NUM_PROCESSES $PROJ_POSTINGS_PARSER_PATH/infra/ansible/playbook.yml &
pid=$!
if wait $pid; then
    echo "Ansible playbook completed successfully."
    check_exit_status "Ansible playbook"
    echo "=> Ansible playbook completed"
else
    # Timeout occurred, kill the ansible-playbook process
    echo "Timeout occurred. Killing ansible-playbook process with PID: $pid"
    kill -9 $pid  # Forcefully terminate 
fi


# Destroy Terraform configuration
cd terraform || { echo "Failed to change directory to terraform. Exiting."; exit 1; }

echo "=> Destroying Terraform configuration..."
terraform destroy -auto-approve
check_exit_status "Terraform destroy"
echo "=> Terraform destroy completed"

hours=$((runtime / 3600))
minutes=$(( (runtime % 3600) / 60 ))
seconds=$((runtime % 60))
printf "Elapsed time: %02d:%02d:%02d\n" $hours $minutes $seconds

