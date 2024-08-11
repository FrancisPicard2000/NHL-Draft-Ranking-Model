import requests
import csv
import argparse
from pathlib import Path
from bs4 import BeautifulSoup

QMJHL_ROOTPAGE_URL = "https://chl.ca/lhjmq/en/stats/players/"
OHL_ROOTPAGE_URL = "https://chl.ca/ohl/stats/players/"
WHL_ROOTPAGE_URL = "https://chl.ca/whl/stats/players/"

USER_AGENT = None


# Return the HTML content of the junior league page that contains the URLs of the other pages of interest
def fetch_junior_league_html(html_output_file_path, rootpage_url):

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
        html_data = requests.get(rootpage_url, headers=headers)

        with open(fpath, "w") as f:
            f.write(html_data.text)

    with open(fpath, "r", encoding="utf8") as f:
        return f.read()



# Fetch the season stats urls for a given junior league
def fetch_urls(tsv_output_file_path, html_output_file_path, rootpage_url):
    content = fetch_junior_league_html(html_output_file_path, rootpage_url)
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
    with open(tsv_output_file_path, 'w', newline='', encoding="utf8") as f:
        tsv_writer = csv.writer(f, delimiter='\t')

        for datapoint in data:
            tsv_writer.writerow(datapoint)



def main():

    # Get the user agent
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", help="your user-agent")
    args = parser.parse_args()
    USER_AGENT = args.u

    # Fetch the data for the QMJHL, OHL, and WHL
    fetch_urls("../data/extracted_data/qmjhl/qmjhl_urls.tsv", "../data/html_pages/qmjhl/rootpage_qmjhl.html", QMJHL_ROOTPAGE_URL)
    fetch_urls("../data/extracted_data/ohl/ohl_urls.tsv", "../data/html_pages/ohl/rootpage_ohl.html", OHL_ROOTPAGE_URL)
    fetch_urls("../data/extracted_data/whl/whl_urls.tsv", "../data/html_pages/whl/rootpage_whl.html", WHL_ROOTPAGE_URL)

    

if __name__ == "__main__":
    main()