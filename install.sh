#!/bin/bash

echo "This script sets the environment variables and paths for running the application inside docker container"

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
VAR_NAME="PROJ_POSTINGS_PARSER_PATH"

install_additional_software() {
  echo "Installing additional software..."
  sudo apt-get update
  sudo apt-get install -y <software-package-name>
  echo "Additional software installed."
}

set_env_var() {
  local var_name=$1
  local var_value

  read -p "Enter $var_name (leave blank to skip): " var_value
  if [ -n "$var_value" ]; then
    if grep -q "$var_name=" "$env_file"; then
      sed -i.bak "s/^$var_name=.*/$var_name=\"$var_value\"/" "$env_file"
    else
      echo "$var_name=\"$var_value\"" >> "$env_file"
    fi
  fi
}

full_install=false
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --full)
      full_install=true
      ;;
  esac
  shift
done

env_file=".env"
# put environment variables in .env file
set_env_var "PGHOST"
set_env_var "PGUSER"
set_env_var "PGDATABASE"
set_env_var "PGPASSWORD"
set_env_var "AWS_ACCESS_KEY_ID"
set_env_var "AWS_SECRET_ACCESS_KEY"

if [ "$full_install" = true ]; then
  install_additional_software
fi

if [ -f "$env_file" ]; then
  echo "Current environment variables set in $env_file:"
  cat "$env_file"
else
  echo "No environment variables were set."
fi


export VAR_NAME="$SCRIPT_DIR"
echo "=> $VAR_NAME is set to $SCRIPT_DIR"
echo "export PROJ_POSTINGS_PARSER_PATH=\"$SCRIPT_DIR\"" >> ~/.bashrc
source ~/.bashrc

echo "=> Permanent export added to ~/.bashrc"
