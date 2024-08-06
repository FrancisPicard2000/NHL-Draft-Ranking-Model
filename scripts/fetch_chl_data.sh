#!/bin/bash

# Store the years
first_season_year=$1 # e.g. 2007-08
last_season_year=$2 # e.g. 2017-18
user_agent=$3 # if the page sources are stored locally, no need to provide a user_agent

first_year=${first_season_year:0:4}
next_year_octal=${first_season_year:5:2}
next_year=$((10#$next_year_octal))
last_year=${last_season_year:0:4}

current_year=$first_year
chl_leagues=("qmjhl" "ohl" "whl")

# Retrieve the relevant urls
python fetch_chl_urls.py -u "$user_agent"

# Retrieve the CHL data
while [ $current_year -le $last_year ] 
do
    playoff_year=$((current_year + 1))
    for league in "${chl_leagues[@]}"
    do
        python chl_scraper.py -l "$league" -s "$current_year-$next_year | Regular Season" -u "$user_agent"
        python chl_scraper.py -l "$league" -s "$playoff_year | Playoffs" -u "$user_agent"
    done

    current_year=$((current_year + 1))
    next_year=$((next_year + 1))
done


