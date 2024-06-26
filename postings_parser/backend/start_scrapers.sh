#!/bin/bash

term_width=$(tput cols 2>/dev/null || echo 80)

printf '%.0s#' $(seq 1 $term_width)
echo
printf '%.0s#' $(seq 1 $term_width)

echo -e "\n\n => Inside bash script"
if [[ "$RUN_SCRAPY" == "true" ]]; then
	cd postings_parser/backend/lever_scraper/
	python3 main_lever_scraper.py
fi

if [[ "$RUN_SELENIUM" == "true" ]]; then
	echo -e "\n => Running scrapers using selenium"
	cd postings_parser/backend/
	python3 runner.py
fi
