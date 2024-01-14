import requests
import csv
import argparse
from pathlib import Path
from bs4 import BeautifulSoup

QMJHL_ROOTPAGE_URL = "https://chl.ca/lhjmq/en/stats/players/"


# Return the HTML content of the QMJHL page that contains the URLs of the other pages of interest
def fetch_qmjhl_html(user_agent):

    fpath = Path("../data/html_pages/qmjhl/rootpage_qmjhl.html")
    headers = {"User-Agent" : user_agent}

    if not fpath.exists():
        html_data = requests.get(QMJHL_ROOTPAGE_URL, headers=headers)

        with open(fpath, "w") as f:
            f.write(html_data.text)

    with open(fpath, "r") as f:
        return f.read()



def main():

    # Get the user agent
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", help="your user-agent")
    args = parser.parse_args()
    user_agent = args.h

    content = fetch_qmjhl_html(user_agent)
    output_file_path = '../data/extracted_data/qmjhl/qmjhl_urls.tsv'
    data = [["season_type", "season_stats_url"]]

    # Fetch data
    soup = BeautifulSoup(content, "html.parser")
    season_options_tags = soup.find_all("select", {"class" : "form-select", "id" : 'seasons'})[1:2] # There are 5 such tags, the 2nd one contains the desired urls
    seasons = season_options_tags[0].find_all("option")
    for s in seasons:
        season_type = s.string.strip()
        season_stats_url = s.get("value")
        data.append([season_type, season_stats_url])


    # Write data to file
    with open(output_file_path, 'w', newline='') as f:

        tsv_writer = csv.writer(f, delimiter='\t')

        for datapoint in data:
            tsv_writer.writerow(datapoint)

    

if __name__ == "__main__":
    main()