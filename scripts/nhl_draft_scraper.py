from selenium import webdriver
from selenium.webdriver.common.by import By
import argparse
import json
import csv



# Extract draft's data
def extract_draft_data(driver):

    draft_data = []

    # Collect data on all web pages
    while True:
        page_data_unformatted = retrieve_player_info_page(driver)
        page_data_formatted = format_raw_data(page_data_unformatted)
        draft_data += page_data_formatted

        next_page_button = driver.find_element(By.CLASS_NAME, "next-button")

        if (not (next_page_button.is_enabled())):
            break
        
        next_page_button.click()
        

    return draft_data



# Retrieve the players' info in the given page
def retrieve_player_info_page(driver):
    
    data = []

    player_blocks = driver.find_elements(By.CLASS_NAME, "rt-tr-group")
    for player in player_blocks:
        player_info_components = player.text.split("\n")
        data.append(player_info_components)

    return data



# Format heights from imperial to metric (to get continuous-ish data)
def format_height(height_string):

    height_components = height_string.strip("\"").split("\' ")
    foot = int(height_components[0])
    inches = int(height_components[1])

    return (30*foot + 2.5*inches)



# Format the raw data extracted from a webpage
def format_raw_data(raw_data):

    formatted_data = []
    team_label_map_file = open("../data/other/team_label_map.json", "r")
    team_label_map = json.load(team_label_map_file)

    for raw_player_data in raw_data:
        if (len(raw_player_data) == 12):
            add_ind = 0
        else:
            add_ind = 1

        if (len(raw_player_data) not in [11, 12]):
            continue # Missing data (e.g. 2009 draft pick 118 by the Maple Leafs)

        player_name = raw_player_data[1]
        player_position = raw_player_data[6-add_ind]
        player_junior_team_league = raw_player_data[10-add_ind]
        player_height = format_height(raw_player_data[8-add_ind])
        player_weight = int(raw_player_data[9-add_ind])

        # If the player is from the CHL, keep his info
        if (player_junior_team_league in ['QMJHL', 'OHL', 'WHL']):
            player_junior_team_label = team_label_map[raw_player_data[-1]]
            player_data = [player_name, player_position, player_junior_team_league, player_junior_team_label, player_height, player_weight]
            formatted_data.append(player_data)

    return formatted_data



def main():

    # Parse the arguments to retrieve the desired draft year
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", help="year to scrape")
    args = parser.parse_args()
    year = int(args.y)
    
    # Setup webdriver and access webpage
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
    driver.get(f"https://records.nhl.com/draft/draft-picks?year={year}")
    driver.implicitly_wait(5)

    # Retrieve the data
    data = extract_draft_data(driver)

    # Store the draft data
    draft_data_file_path = f"../data/extracted_data/draft/draft{year}_stats.csv"
    header = ["Name", "Position", "League", "Team", "Height", "Weight"]

    with open(draft_data_file_path, 'w', newline='') as f:

        tsv_writer = csv.writer(f, delimiter='\t')
        tsv_writer.writerow(header)

        for datapoint in data:
            tsv_writer.writerow(datapoint)

    

if __name__ == "__main__":
    main()