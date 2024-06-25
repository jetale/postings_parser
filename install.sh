#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
VAR_NAME="PROJ_POSTINGS_PARSER_PATH"

export VAR_NAME="$SCRIPT_DIR"

echo "$VAR_NAME is set to $SCRIPT_DIR"

echo "export PROJ_POSTINGS_PARSER=\"$SCRIPT_DIR\"" >> ~/.profile

source ~/.bashrc

echo "Permanent export added to ~/.bashrc"
