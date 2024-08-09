#!/bin/bash

# Store the years
first_season_year=$1 # e.g. 2007-08
last_season_year=$2 # e.g. 2017-18

first_year=${first_season_year:0:4}
next_year_octal=${first_season_year:5:2}
next_year=$((10#$next_year_octal))
last_year=${last_season_year:0:4}

current_year=$first_year
# Retrieve the CHL data
while [ $current_year -le $last_year ] 
do
    python ahl_stats_scraper.py -s "$current_year-$next_year"
    
    current_year=$((current_year + 1))
    next_year=$((next_year + 1))
done