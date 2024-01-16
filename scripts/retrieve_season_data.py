import argparse
import pandas as pd
import requests
from pathlib import Path


USER_AGENT = None

# Retrieve the url corresponding to the webpage containing the stats of the given season
def retrieve_season_url(season):

    # Load the dataframe that contains the seasons and their data urls
    qmjhl_df = pd.read_csv("../data/extracted_data/qmjhl/qmjhl_urls.tsv", sep='\t')

    season_row = qmjhl_df[qmjhl_df['season_type'].str.contains(season)]
    url_unformatted_string = season_row['season_stats_url'].to_string()
    url = url_unformatted_string.split(' ')[-1]

    return url



# Retrieve the html content of the webpage
def retrieve_hmtl_content(url, season):

    filename_format = '_'.join(season.split(' ')) 
    html_output_file_path = f'../data/html_pages/qmjhl/{filename_format}.html'

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

    with open(fpath, "r") as f:
        return f.read()




def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", help="season to scrape (e.g. 2023-24 \| Regular Season)")
    parser.add_argument("-u", help="your user-agent", default=None) # No need to provide the user-agent again if the html content is saved locally

    args = parser.parse_args()
    season = args.s
    USER_AGENT = args.u

    url = retrieve_season_url(season)

    html_content = retrieve_hmtl_content(url, season)
    



if __name__ == "__main__":
    main()