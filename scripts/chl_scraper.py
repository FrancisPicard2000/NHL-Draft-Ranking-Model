import argparse
import pandas as pd
import requests
import re
import ast
import csv
from pathlib import Path
from bs4 import BeautifulSoup
from unidecode import unidecode


USER_AGENT = None
SEASON_YEARS = None
SEASON_TYPE = None

# Retrieve the url corresponding to the webpage containing the stats of the given season
def retrieve_season_url(league, season):

    # Load the dataframe that contains the seasons and their data urls
    league_df = pd.read_csv(f"../data/extracted_data/{league}/{league}_urls.tsv", sep='\t')

    season_row = league_df[league_df['season_type'].str.contains(season)]
    url_unformatted_string = season_row['season_stats_url'].to_string()
    url = url_unformatted_string.split(' ')[-1]

    return url



# Retrieve the html content of the webpage
def retrieve_hmtl_content(url, league, season):
    
    html_output_file_path = f"../data/html_pages/{league}/{league}_{SEASON_YEARS}_{SEASON_TYPE}.html"

    fpath = Path(html_output_file_path)
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    if not fpath.exists():
        html_data = requests.get(url, headers=headers)

        with open(fpath, "w") as f:
            f.write(html_data.text)

    with open(fpath, "r", encoding="utf8") as f:
        return f.read()



# Retrieve the data from the html file and preprocess it
def retrieve_data_unformatted(html_content, league):

    # Specific script tag to retrieve the data from
    if (SEASON_TYPE == "playoffs"):
        if (league == "qmjhl"):
            script_tag_no = 19
        else:
            script_tag_no = 16
    else:
        if (league == "qmjhl"):
            script_tag_no = 23
        else:
            script_tag_no = 16

    soup = BeautifulSoup(html_content, "html.parser")
    script_text = soup.find_all("script")[script_tag_no:script_tag_no+1][0].text

    data = re.search('data:(.*)', script_text)
    
    return data.group(0).strip('data: });')
    


# Process the unformatted data retrieved from the html file
def process_unformatted_data(data, league):

    output_csv_file_path = f"../data/extracted_data/{league}/{league}_{SEASON_YEARS}_{SEASON_TYPE}_stats.csv"
    fpath = Path(output_csv_file_path) 
    
    header = [
        "Name",
        "Position",
        "GP",
        "G",
        "A",
        "PTS",
        "+/-",
        "PIM",
        "PPG",
        "PPA",
        "SHG",
        "SHA",
        "SOG",
        "DS",
        "GWG",
        "OTG",
        "First",
        "Insurance",
        "SOGP",
        "SO/G"
        "ATT",
        "SOWG",
        "SO%",
        "FOA",
        "FOW",
        "FO%",
        "PTS/G",
        "PIM/G"
    ]

    if (SEASON_TYPE == "playoffs"):
        header = ["P" + stat for stat in header] # Playoff stats will be thought as: Playoff Game Played, Playoff Goals, etc.

    player_data_list = ast.literal_eval(data) # list containing one element per player
    
    with open(fpath, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for player_data in player_data_list:
            player_name = [unidecode(' '.join(reversed(player_data[5][1].split(', '))))]
            player_position = [player_data[1]]
            player_team = [player_data[6][0][1]]
            player_other_stats = [int(i) for i in player_data[7:-6]] + [float(i) for i in player_data[-6:-5]] + [int(i) for i in player_data[-5:-3]] + [float(i) for i in player_data[-3:]]
        
            player_row = player_name + player_position + player_team + player_other_stats
            writer.writerow(player_row)
        
    
    
def main():
    global SEASON_YEARS, SEASON_TYPE, USER_AGENT
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", help="the league (one of qmjhl, ohl, or whl)")
    parser.add_argument("-s", help="season to scrape (e.g. 2023-24 \| Regular Season) (e.g. 2023 \| Playoffs)")
    parser.add_argument("-u", help="your user-agent", default=None) # No need to provide the user-agent again if the html content is stored locally

    args = parser.parse_args()
    league = args.l
    season = args.s
    season_components = season.split(" ")

    SEASON_YEARS = season_components[0]
    if (len(SEASON_YEARS) == 6):
        SEASON_YEARS = SEASON_YEARS[:5] + "0" + SEASON_YEARS[5]

    if (season_components[-1].lower() == "playoffs"):
        SEASON_TYPE = "playoffs"
    else:
        SEASON_TYPE = f"{season_components[-2].lower()}_{season_components[-1].lower()}"

    USER_AGENT = args.u

    url = retrieve_season_url(league, season)

    html_content = retrieve_hmtl_content(url, league, season)

    unf_data = retrieve_data_unformatted(html_content, league)

    process_unformatted_data(unf_data, league)
    



if __name__ == "__main__":
    main()