from pathlib import Path
import requests
import argparse


# Collect the html content of Elite Prospect NHL Entry Draft for a given year
def get_draft_page_html_data(year):
    
    fpath = Path(f'../data/html_pages/draft/draft{year}.html')
    
    # Caching: Only request if we haven't done so before
    if not fpath.exists():
        html_data = requests.get(f"https://www.eliteprospects.com/draft/nhl-entry-draft/{year}")

        with open(fpath, "w") as f:
            f.write(html_data.text)

    with open(fpath, "r") as f:
        return f.read()
    


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="first year to scrape")
    parser.add_argument("-l", help="last year to scrape")

    args = parser.parse_args()

    fyear = int(args.f)
    lyear = int(args.l)

    for year in range(fyear, lyear):
        get_draft_page_html_data(year)



if __name__ == "__main__":
    main()