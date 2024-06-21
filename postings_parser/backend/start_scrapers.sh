#!/bin/bash

#echo "$(pip list)"

cd postings_parser/backend/lever_scraper/
python3 main_lever_scraper.py

if [[ "$RUN_SELENIUM" == "true" ]]; then
	echo "Running selenium part"
	if pip show selenium &> /dev/null; then
		cd ../
		python3 runner.py
	else
		echo "Selenium is not installed"
	fi
fi
