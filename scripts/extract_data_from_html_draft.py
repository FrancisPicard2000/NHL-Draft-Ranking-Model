from bs4 import BeautifulSoup
from pathlib import Path
import argparse


# Retrieve the html content of the page corresponding to the given year
def retrieve_content(year):
    fpath = Path(f'../data/html_pages/draft/draft{year}.html')
    with open(fpath, 'r') as f:
        content = f.read()

    return content


# Extract the data from the html page of the given year
def extract_data(year):
    content = retrieve_content(year)

    soup = BeautifulSoup(content, "html.parser")
    draft_table = soup.find("table", {"data-sort-ajax-container" : "#drafted-players"})

    
    for player_data in draft_table.find_all("td", {"class" : "player"}):
        a_content = player_data.find("a")
        player_name = a_content.string
        player_url = a_content.get("href")
        print(player_name, player_url)
        break
        

    


    



def main():
    extract_data(2006)




if __name__ == "__main__":
    main()