#!/bin/bash

term_width=$(tput cols 2>/dev/null || echo 80)

printf '%.0s#' $(seq 1 $term_width)
echo
printf '%.0s#' $(seq 1 $term_width)

echo -e "\n\n => Starting scrapers"
if [[ "$RUN_SCRAPY" == "true" ]]; then
	echo -e "\n => Running static scrapers using scrapy"
	cd postings_parser/backend/static_scraper/
	python3 main_lever_scraper.py
fi

if [[ "$RUN_SELENIUM" == "true" ]]; then
	echo -e "\n => Running dynamic scrapers using selenium"
	cd postings_parser/backend/dynamic_scraper/
	python3 main_scraper.py --s3_bucket_name="$S3_BUCKET_NAME" --date_parse="$DATE_PARSE" --only_html=False
fi
