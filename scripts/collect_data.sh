#!/bin/bash

# Compute the inputs
first_draft_year=$1 # e.g. 2007
last_draft_year=$2 # e.g. 2017
year_gap=$3
overwrite=$4

first_season_first_year=$((first_draft_year - 1))
first_season_second_year=${first_draft_year:2}
last_season_first_year=$((last_draft_year - 1))
last_season_second_year=${last_draft_year:2}


# Call the scripts
if [ "$overwrite" == "True" ]; then
    ./fetch_hockeydb_data.sh "$first_draft_year" "$last_draft_year" "$year_gap"
    ./fetch_chl_data.sh "$first_season_first_year-$first_season_second_year" "$last_season_first_year-$last_season_second_year"
    ./fetch_nhl_draft_data.sh "$first_draft_year" "$last_draft_year"
fi
python create_dataset.py -f "$first_draft_year" -l "$last_draft_year"