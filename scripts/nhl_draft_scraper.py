import requests
import argparse
import json
import csv
from pathlib import Path
from bs4 import BeautifulSoup


# Collect the html content of Elite Prospect NHL Entry Draft for a given year
def get_draft_page_html_content(year):
    
    fpath = Path(f'../data/html_pages/draft/draft{year}.html')
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
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
    
    # Caching: Only request if we haven't done so before
    if not fpath.exists():
        html_data = requests.get(f"https://www.hockeydb.com/ihdb/draft/nhl{year}e.html", headers=HEADERS)

        with open(fpath, "w") as f:
            f.write(html_data.text)

    with open(fpath, "r") as f:
        return f.read()



# Retrieve the draft data from the html content
def retrieve_draft_data(html_content):

    soup = BeautifulSoup(html_content, "html.parser")
    data_body = soup.find("tbody")
    players_tr_list = data_body.find_all("tr", class_=lambda x: x != "hideme")

    team_label_map_file = open("../data/other/team_label_map.json", "r")
    team_label_map = json.load(team_label_map_file)

    chl_data = []

    for player_tr in players_tr_list:

        # Extract the name
        player_name = player_tr.find("a", {"target" : "players"}).text

        # Extract the position
        player_position_unformatted = player_tr.find("td", {"class" : "hidemob"}).text
        if (player_position_unformatted in ["L", "R"]):
            player_position = player_position_unformatted + "W"
        else:
            player_position = player_position_unformatted
        
        # Extract the team label
        player_junior_team_unformatted = player_tr.find("td", {"class" : "l hidemob"}).text
        player_junior_team_components = player_junior_team_unformatted.split(" ")
        player_junior_team = " ".join(player_junior_team_components[0:-1])
        player_junior_team_league = player_junior_team_components[-1].strip("[]")

        if player_junior_team_league in ["QMJHL", "OHL", "WHL"]:      # If the player is from the CHL, keep his info
            player_junior_team_label = team_label_map[player_junior_team]
            chl_data.append([player_name, player_position, player_junior_team_league, player_junior_team_label])

    team_label_map_file.close()
    return chl_data
            


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", help="year to scrape")

    args = parser.parse_args()
    year = int(args.y)

    html_content = get_draft_page_html_content(year)
    draft_data = retrieve_draft_data(html_content)

    # Store the draft data
    draft_data_file_path = f"../data/extracted_data/draft/draft{year}_stats.csv"
    header = ["Name", "Position", "League", "Team"]

    with open(draft_data_file_path, 'w', newline='') as f:

        tsv_writer = csv.writer(f, delimiter='\t')
        tsv_writer.writerow(header)

        for datapoint in draft_data:
            tsv_writer.writerow(datapoint)

    
if __name__ == "__main__":
    main()