from selenium import webdriver
from selenium.webdriver.common.by import By
import argparse
import time
import csv


# Extract the regular season stats of the given year
def extract_stats_year(driver):

    stats_year = []
    cookie_flag = True

    # Collect data on all web pages
    while True:

        page_data = extract_stats_page(driver)
        stats_year += page_data

        next_page_button = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div/div/div[2]/div/div/main/div[5]/div[2]/div[3]/button")
        driver.execute_script("arguments[0].scrollIntoView()", next_page_button)
        driver.implicitly_wait(2)
        
        if (cookie_flag):
            cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            cookie_button.click()
            driver.implicitly_wait(2)
            cookie_flag = False
        
        
        if (not (next_page_button.is_enabled())):
            break
        
        time.sleep(2)
        next_page_button.click()
        

    return stats_year



# Extract the regular season stats of the current page
def extract_stats_page(driver):

    data_page = []

    player_blocks = driver.find_elements(By.CLASS_NAME, "rt-tr-group")
    for player_stats in player_blocks:
        player_stats_list = player_stats.text.split("\n")
        data_page.append(player_stats_list)
        

    return data_page



def main():
    
    # Parse the arguments to retrieve the year to scrape
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", help="year to scrape (e.g. 2022-23)")
    args = parser.parse_args()
    year_components = args.y.split("-")
    year = year_components[0] + "20" + year_components[1]

    # Setup webdriver and access webpage
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
    driver.get(f"https://www.nhl.com/stats/skaters?reportType=season&seasonFrom={year}&seasonTo={year}&gameType=2&filter=gamesPlayed,gte,1&page=0&pageSize=50")
    driver.implicitly_wait(5)

    # Retrieve the data
    data = extract_stats_year(driver)

    # Write data to csv
    output_file = f"../data/extracted_data/nhl_regular_season/{args.y}_Regular_Season_Stats.csv"
    header = ['rank', 'Player', 'Season', 'Team', 'S/C', 'Pos', 'GP', 'G', 'A', 'P', '+/-', 'PIM', 'P/GP', 'EVG', 'EVP',
              'PPG', 'PPP', 'SHG', 'SHP', 'OTG', 'GWG', 'S', 'S%', 'TOI/GP', 'FOW%']
    
    with open(output_file, 'w', newline='') as f:

        tsv_writer = csv.writer(f, delimiter='\t')
        tsv_writer.writerow(header)

        for datapoint in data:
            tsv_writer.writerow(datapoint)



if __name__ == "__main__":
    main()