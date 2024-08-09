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

        next_page_button = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div/div/div[2]/div/div[2]/div/main/div[2]/span/nav/button[2]")
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

    player_blocks = driver.find_elements(By.CSS_SELECTOR, ".sc-dSTIoc.lpdNXV.rt-tr.null")
    for player_stats in player_blocks:
        player_stats_list = player_stats.text.split("\n")
        data_page.append(player_stats_list)
        

    return data_page



def main():
    
    # Parse the arguments to retrieve the year to scrape
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", help="season to scrape (e.g. 2022-23)")
    args = parser.parse_args()
    year_components = args.s.split("-")
    if (len(year_components[1]) == 1):
        year_url_format = year_components[0] + "200" + year_components[1]
        year_filename_format = year_components[0] + "-0" + year_components[1]
    else:
        year_url_format = year_components[0] + "20" + year_components[1]
        year_filename_format = args.s

    # Setup webdriver and access webpage
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
    driver.get(f"https://www.nhl.com/stats/skaters?reportType=season&seasonFrom={year_url_format}&seasonTo={year_url_format}&gameType=2&filter=gamesPlayed,gte,1&page=0&pageSize=50")
    driver.implicitly_wait(5)

    # Retrieve the data
    data = extract_stats_year(driver)

    # Write data to csv
    output_file = f"../data/extracted_data/nhl_regular_season_stats/{year_filename_format}_NHL_Regular_Season_Stats.csv"
    header = ['rank', 'Player', 'Season', 'Team', 'S/C', 'Pos', 'GP', 'G', 'A', 'P', '+/-', 'PIM', 'P/GP', 'EVG', 'EVP',
              'PPG', 'PPP', 'SHG', 'SHP', 'OTG', 'GWG', 'S', 'S%', 'TOI/GP', 'FOW%']
    
    with open(output_file, 'w', newline='', encoding="utf8") as f:

        tsv_writer = csv.writer(f, delimiter='\t')
        tsv_writer.writerow(header)

        for datapoint in data:
            tsv_writer.writerow(datapoint)

    driver.close()


if __name__ == "__main__":
    main()