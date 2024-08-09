from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse
import time
import csv


class LoadingError(Exception):
    pass

POSITIONS = ["LW", "C", "RW", "F", "D", "G"]

# Access the webpage of the regular season we want
# No direct pattern using the season's name
def access_desired_season_webpage(driver, season):
    label = season + " Regular Season"
    e = driver.find_element(By.XPATH, f"//option[@label='{label}']")
    value = e.get_attribute("value")
    
    driver.get(f"https://theahl.com/stats/player-stats/all-teams/{value}?playertype=skater&rookie=no&sort=points&statstype=expanded&page=1&league=4&position=skaters")


# Extract the data from the webpage and format it
def extract_stats_season(driver):

    season_stats = []
    last_page = False

    while True:

        # Attempt to load the webpage
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "ht-table")))
        except:
            raise LoadingError("AHL website loads foreover")
        
        # Retrieve the data and format it
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "ht-table")))
        page_data_unformatted = driver.find_element(By.CLASS_NAME, "ht-table").text # All the data is comprised in one huge string
        page_data_unf_string_list = page_data_unformatted.split("\n") # Split the string to have a list of strings, each corresponding to the data of one player
        page_data_unf_list = [player_string_stats.split(" ") for player_string_stats in page_data_unf_string_list][1:] # Now have a list for each player, don't include the header (element at index 0)

        for player_data_unf in page_data_unf_list:
            player_data_formatted_but_name = [elem for elem in player_data_unf if elem not in ['+', 'x', '*']]

            position_index = [i for i, elem in enumerate(player_data_formatted_but_name) if elem in POSITIONS][0]
            player_name = " ".join(player_data_formatted_but_name[1:position_index])

            # Formatted data: rank + name + stats
            player_data_formatted = [player_data_formatted_but_name[0]] + [player_name] + player_data_formatted_but_name[position_index:] # Allow names with multiple spaces
            season_stats.append(player_data_formatted)


        # Check if there is another data page to scrape
        page_buttons = driver.find_elements(By.CLASS_NAME, "ht-paging-button")
        for button in page_buttons:
            if (button.text == ""): # Last "Next" button has ng-hide
                last_page = True
        
        if last_page:
            break
        
        # If there is another page to scrape, access it
        next_page_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/div/main/article/div[2]/ng-view/div[2]/div[5]/div[2]/a")
        driver.execute_script("arguments[0].scrollIntoView()", next_page_button)
        driver.implicitly_wait(2)
        next_page_button.click()
        time.sleep(1)

    return season_stats



def main():

    # Parse the arguments to retrieve the year to scrape
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", help="season to scrape (e.g. 2022-23 Regular Season)")
    args = parser.parse_args()
    season = args.s
    year = season.split(" ")[0]
    year_components = year.split("-")
    if (len(year_components[1]) == 1):
        year_filename_format = year_components[0] + "-0" + year_components[1]
    else:
        year_filename_format = year

    # Setup webdriver and access webpage
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
    driver.get("https://theahl.com/stats/player-stats/all-teams/?playertype=skater&rookie=no&sort=points&statstype=expanded&page=1&league=4&position=skaters")
    driver.implicitly_wait(5)

    # Access desired season
    access_desired_season_webpage(driver, year_filename_format)

    # Retrieve the data
    data = extract_stats_season(driver)
    
    # Write data to csv
    output_file = f"../data/extracted_data/ahl_regular_season_stats/{year_filename_format}_AHL_Regular_Season_Stats.csv"
    header = ['rank', 'Player', 'Pos', 'Team', 'GP', 'G', 'A', 'PTS', '+/-', 'PIM', 'PPG', 'SHG', 'SH', 'PPA', 'SHA', 'GWG', 
              'FG', 'IG', 'OTG', 'UA', 'EN', 'SH%', 'SOG', 'SOA', 'SOWG', 'SO%']
    
    with open(output_file, 'w', newline='', encoding="utf8") as f:

        tsv_writer = csv.writer(f, delimiter='\t')
        tsv_writer.writerow(header)

        for datapoint in data:
            tsv_writer.writerow(datapoint)

    driver.close()




if __name__ == "__main__":
    main()