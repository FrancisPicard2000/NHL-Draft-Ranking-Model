from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import argparse
import re
from pathlib import Path
import csv



# Retrieve the data of a given player
def retrieve_info(player, driver, init_window, draft_year, year_gap):

    # Retrieve the player's data url
    player_data_url = player.get_attribute('href')
    player_id = player_data_url.split("=")[-1]
    player_name = player.text
    player_name_title = player_name.replace('"', "'")
    
    # Open a new window and access the player's data webpage
    driver.execute_script(f"window.open('{player_data_url}')")
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    windows_after = driver.window_handles
    new_window = [x for x in windows_after if x != init_window][0]
    driver.switch_to.window(new_window)
    WebDriverWait(driver, 20).until(EC.title_contains(f"{player_name_title}")) # edge case: George "Bud" Holloway

    # Format the regular season year
    starting_season_year_str = str(int(draft_year) - 1)
    ending_season_year_str = str(int(draft_year) % 100)
    if (len(ending_season_year_str) == 1):
        ending_season_year_str = "0" + ending_season_year_str
    season_year = starting_season_year_str + "-" + ending_season_year_str

    # Retrieve junior regular season data
    player_junior_data, data_table = retrieve_junior_data(driver, player_id, season_year)
    if (player_junior_data == None):
        # Close the window and go back to the draft window
        driver.close()
        driver.switch_to.window(init_window)
        WebDriverWait(driver, 20).until(EC.title_contains(draft_year))
        return None
    
    # Format the target regular season year
    starting_proj_season_year_str = str(int(starting_season_year_str) + int(year_gap))
    ending_proj_season_year_str = str(int(ending_season_year_str) + int(year_gap))
    if (len(ending_proj_season_year_str) == 1):
        ending_proj_season_year_str = "0" + ending_proj_season_year_str
    proj_season_year = starting_proj_season_year_str + "-" + ending_proj_season_year_str

    # Retrieve target
    category = retrieve_target(data_table, proj_season_year)
    if (category == "Invalid"):
        # Close the window and go back to the draft window
        driver.close()
        driver.switch_to.window(init_window)
        WebDriverWait(driver, 20).until(EC.title_contains(draft_year))
        return "Invalid"
    player_data = [player_name] + player_junior_data + [category]
    
    # Close the window and go back to the draft window
    driver.close()
    driver.switch_to.window(init_window)
    WebDriverWait(driver, 20).until(EC.title_contains(draft_year))

    return player_data



# Retrieve the player's regular season data
def retrieve_junior_data(driver, player_id, season_year):
    # Retrieve the draft data
    try:
        data_table = driver.find_element(By.ID, player_id) # NOT A SKATER
        parent_elements = data_table.find_elements(By.XPATH, f".//td[text()='{season_year}']/..") # NOT FROM CHL (NO KNOWN JUNIOR)
        
    except NoSuchElementException:
        return (None, None)
    
    # Multiple CHL Teams on Draft Year
    player_junior_data = None
    for parent in parent_elements:
        data = parent.text
        data_formatted = re.sub(r'[^a-zA-Z0-9 -]', '', data)
        data_elements = data_formatted.split(" ")
        team = " ".join(data_elements[1:-12]).strip(" ")
        data_vector = [team.strip(" ")] + data_elements[-12:]
        data_vector = data_vector[0:2] + [s.replace("--", "0") for s in data_vector[2:]]
        if (data_vector[1] not in ['QMJHL', 'OHL', 'WHL']): # NOT FROM CHL
            continue

        if (player_junior_data == None): # First CHL team record
            player_junior_data = data_vector
        else:
            # data_vector again for most recent CHL team
            player_junior_data = data_vector[0:2] + [str(int(s1) + int(s2)) for (s1, s2) in zip(player_junior_data[2:], data_vector[2:])]
        
    return player_junior_data, data_table



# Retrieve the player's target (PTS/GP in X years)
def retrieve_target(data_table, proj_season_year):
    proj_parent_elements = data_table.find_elements(By.XPATH, f".//td[text()='{proj_season_year}']/..")
    gp_dict = {'AHL': 0, 'NHL': 0}
    pts_dict = {'AHL': 0, 'NHL': 0}

    # Multiple NHL/AHL teams
    for parent in proj_parent_elements:
        proj_data = parent.text
        proj_data_elements = proj_data.split(" ")
        proj_data_elements = [s.replace("--", "0") for s in proj_data_elements] # Only play in the playoffs

        if (len(proj_data_elements) < 12): # Not from the AHL/NHL
            gp, league= retrieve_data_diff_league(proj_data_elements)
            if (league not in gp_dict):
                gp_dict[league] = int(gp)
            else:
                gp_dict[league] += int(gp)
            continue
        
        else:
            gp = proj_data_elements[-11]
            pts = proj_data_elements[-8]
            league = proj_data_elements[-12]
        
            if (league not in ['NHL', 'AHL']):
                gp, league = retrieve_data_diff_league(proj_data_elements)
                if league not in gp_dict:
                    gp_dict[league] = int(gp)
                else:
                    gp_dict[league] += int(gp)
                continue

        gp_dict[league] += int(gp)
        pts_dict[league] += int(pts)


    # Find target league and pts/gp
    if (max(gp_dict['AHL'], gp_dict["NHL"]) < 20):

        # If Regular, -> 0
        if any(value >= 20 for value in gp_dict.values()):
            target = "Not_In_NHL_AHL"
            proj_league = "Not_In_NHL_AHL"

        # Else -> Hard to say
        else:
            target = "Other"
            proj_league = "Other"


    elif (gp_dict['AHL'] > gp_dict["NHL"]):
        target = round(pts_dict['AHL']/gp_dict['AHL'], 2)
        proj_league = 'AHL'

    else:
        target = round(pts_dict['NHL']/gp_dict['NHL'], 2)
        proj_league = 'NHL'

    
    # Categorize for a given league and pts/gp
    category = categorize(proj_league, target)
    return category



def retrieve_data_diff_league(proj_data_elements):
    potential_gp = None
    potential_league = None

    # Retrieve the gp from many different formats
    # Assume: Teams can have a number in their name (e.g. HV71), but not two separated by a space
    # Assume: Hockey Leagues do not have numbers in their name
    # Format to look for: League_name (string), GP (int), G (int), first occurrence of this pattern within elements
    for elem in proj_data_elements:
        try:
            int(elem)
            if (potential_gp == None):
                potential_gp = elem
            else:
                 break
        except ValueError:
            potential_gp = None
            potential_league = elem
            continue
    
    return potential_gp, potential_league



# Takes the league and the PTS/GP statistic and categorize the datapoint
def categorize(league, value):

    intervals = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]


    if (league == "Not_In_NHL_AHL") and (value == "Not_In_NHL_AHL"):
        return "Not_In_NHL_AHL"
    
    if (league == "Other") and (value == "Other"):
        return "Other"

    if (value >= 1.0):
        return league + " [1.0, ...]"

    for interval in intervals:
        if interval[0] <= value < interval[1]:
            return league + f" [{interval[0]}, {interval[1]})"


def main():

    # Script arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", help="Draft Year to Scrape (e.g. 2005)")
    parser.add_argument("-g", help="Gap")
    args = parser.parse_args()
    draft_year = args.y
    gap = args.g
    
    # Create the webdriver
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)

    # Access HockeyDB NHL Entry Draft webpage
    driver.get(f"https://www.hockeydb.com/ihdb/draft/nhl{draft_year}e.html")
    driver.implicitly_wait(2)
    windows_before  = driver.current_window_handle

    # Click on every player, retrieve the data, and write to file
    drafted_players = driver.find_elements(By.XPATH, '//*[@target="players"]')

    Path("../data/extracted_data/base").mkdir(parents=True, exist_ok=True)
    output_file = f"../data/extracted_data/base/base_table_draft{draft_year}.tsv"
    fpath = Path(output_file) 
    header = ["Rank", "Name", "Team", "League", "GP", "G", "A", "PTS", "PIM", "+/-", "PGP", "PG", "PA", "PPTS", "PPIM", "Proj_PTS/GP"]
    rank = 0
    with open(fpath, "w", newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(header)
        for player in drafted_players:
            rank += 1
            player_data = retrieve_info(player, driver, windows_before, draft_year, gap)
            if (player_data != None):
                writer.writerow([rank] + player_data)


    driver.close()



if __name__ == "__main__":
    main()