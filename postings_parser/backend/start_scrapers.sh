#!/bin/bash

echo "$(pip list)"

cd postings_parser/backend/lever_scraper/
python3 main_lever_scraper.py


cd ../
python3 runner.py
