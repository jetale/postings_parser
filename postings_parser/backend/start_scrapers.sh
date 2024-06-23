#!/bin/bash

#echo "$(pip list)"
echo "Inside bash script"
if [[ "$RUN_SCRAPY" == "true"]]; then
	cd postings_parser/backend/lever_scraper/
	python3 main_lever_scraper.py
fi

if [[ "$RUN_SELENIUM" == "true" ]]; then
	echo "Running scrapers using selenium"
	cd postings_parser/backend/
	python3 runner.py
fi
