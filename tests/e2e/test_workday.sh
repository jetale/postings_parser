#!/bin/bash


# Get the directory of the current script
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

PROJ_ROOT="$SCRIPT_DIR/../.."

cd "$PROJ_ROOT" || exit 1


# Load environment variables from .env file
if [[ -f .env ]]; then
    source .env
else
    echo "Error: .env file not found."
    exit 1
fi


docker build . --file Dockerfile --tag postings_parser_image

docker run -p 5432:5432 -e PGHOST="$PGHOST" \
        	-e PGDATABASE="$PGDATABASE" \
        	-e PGUSER="$PGUSER" \
        	-e PGPASSWORD="$PGPASSWORD" \
		-e RUN_SELENIUM="true" \
        	postings_parser_image
