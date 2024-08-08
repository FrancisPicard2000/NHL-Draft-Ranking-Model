#!/bin/bash

# Store the years
first_draft_year=$1 # e.g. 2007
last_draft_year=$2 # e.g. 2017

current_year=$first_draft_year
# Retrieve the NHL draft data
while [ $current_year -le $last_draft_year ] 
do
    python nhl_draft_scraper.py -y "$current_year"
    current_year=$((current_year + 1))
done