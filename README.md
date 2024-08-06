# NHL-Draft-Ranking-Model

## Overview
This project aims to develop machine learning models to predict how good eligible draft hockey players will be in the future. Currently, the dataset consists of X statistics about all the players (X) who have played in the CHL (Canadian Hockey League) from 1999-00 to 2018-19. The models are meant to be used by NHL teams before the yearly draft to get insights about the best player to select.



## Question Definition
My initial goal was to answer the fundamental question every team is trying to answer before the draft:

- Which player at our drafting position will be the best?

This is often not an obvious question to answer and not quite measurable. First, what is meant by "best" player? While some people will prefer players who can play the whole 200 feet, others will love goal scorers. When two very different players have about the same strength overall, the team's need usually settles the debate. To make the models as generally applicable as possible, I've decided to rank players based on how many points per game they are projected to get in the future.

- Which player at our drafting position will score the most points per game?

Now that we have a metric to rank the players, we need to specify a timestamp for our projection. From the team's point of view, do we want the player that will score the most points in the next season or e.g. in five years? Again, this is team dependent. For the sake of this project, I've decided to project the number of points per game in five years. Arguably, young players need time to develop before we know their peaking value and five years is fair. 

- Which player at our drafting position will score the most points per game five years after the draft?

There is one final thing to add to make it a measurable question: in which league(s) do we project the points? Only considering the NHL might be a practical concern. Indeed, some players will stay longer in the AHL and dominate there before having a shot in the NHL. Thus, NHL teams arguably might want to know how good a player will be in the AHL five years after the draft if they do not make it to the NHL just yet.

- Which player at our drafting position will score the most points per game in either the NHL or the AHL five years after the draft?

This is a measurable question. Yet, there are some things left to be specified. First, to compare point projections in the AHL and the NHL, this will be a classification problem. Briefly, models will classify players in buckets of points in either the AHL or the NHL in one of the X classes. Future work could explore on whether modeling the problem into a multioutput problem or a regression problem by only considering e.g. NHL would yield more desirable results. Second, for players who have played in the NHL and the AHL during their fifth year, the models will be trained to classify in the league the players have played the most. For players who have played the same amount of games in the NHL and the AHL during their fifth year, the NHL point projection will be looked at. Finally, from a practical standpoint, the models should be applied to all the eligible players before the draft. Then to select the best player at your drafting position, start from the top of the output list and select the highest not-yet-selected player.



## Data Collection
[Explain the data collection process, the scripts involved]

All the data used in this project will be stored in the data directory, which contains several sub-directories. First, the html_pages directory contains all the webpages' page source used for local scraping. Next, the extracted_data directory contains all the data of interest that have been extracted from the webpages' page source like e.g. player statistics. The model_dataset directory contains data combined from the extracted_data directory which will be given as input to various machine learning models. Finally, the other directory contains data maps used for convenience.


CHL stats scraping:
To begin with, the CHL data has been scraped from the CHL website directly. The webpages of interest are statically loaded, so I have used the BeautifulSoup and Requests packages to scrape them. One of the concerns is that the URLs of the desired pages contain a number (e.g. https://chl.ca/lhjmq/en/stats/players/178/) which depends, to the best of my knowledge, on the number of webpages already created on the website. Yet, when the number is omitted, the web browser is directed to the most recent webpage (i.e. the webpage of the most recent data). It is worth noting here that the page source of the most recent webpage contains the URLs of the other pages of interest. 

The fetch_chl_urls.py script retrieves the URLs of the desired pages from the most recent webpage's page source and saves them into one .tsv file for each of the three junior leagues. Then, the chl_scraper.py script will scrape the CHL website and retrieve the data for a given season using the appropriate URL from the tsv files. Both scripts have been written so that all webpages' page source content are stored locally if they are not already there and the scripts are working on the locally stored content. This is to avoid requesting the CHL's website unnecessarily. Finally, the fetch_chl_data.sh script retrieves the CHL data using the two python scripts mentioned above. From the user's standpoint, running the bash script is sufficient to collect the data from the CHL website. For now, the script should be called with two arguments: the starting and ending season years. For example, to retrieve the CHL data from 1999-00 to 2018-19, one would call

    ./fetch_chl_data.sh 1999-00 2018-19

Gotcha: The CHL website has been able to detect that scrapers were used, even with custom headers, after as little as two requests. So the scripts might only work when the page sources are already stored locally. However, as there would only be a handful of new pages to add every year, I didn't bother too much on this issue. Still, all the scripts can take as input the User Agent as well, but this argument can be omitted when calling them. In the future, it would be interesting to see if using other scraping techniques and packages (e.g. Selenium) would solve the issue. The main branch does not contain the data but has all the necessary results and conclusion. To have access to the locally stored data, please consult X branch.







## Data Annotation: Classifying dataset instances
[Explain the classes/buckets]



## Results
This section will explore the different models' performance. To consult the in-depth data analysis and model construction, please consult X.
