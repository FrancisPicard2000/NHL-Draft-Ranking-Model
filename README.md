# NHL-Draft-Ranking-Model

## Overview
This project aims to develop machine learning models to predict how good eligible draft hockey players will be in the future. Currently, the dataset consists of 57 statistics about 917 NHL drafted forwards who have played in the CHL (Canadian Hockey League) between 2000-01 and 2018-19. The models are meant to be used by NHL teams before the NHL Entry draft to make projections on all the relevant CHL players, which might be used later to select the best available player.

  
  

## Question Definition
My initial goal was to answer the fundamental question every team is trying to answer before the draft:

- Which player at our drafting position will be the best for us?

This is often not an obvious question to answer and not quite measurable. First, what is meant by the "best for us"? While some people will prefer players who can play the whole 200 feet, others will love goal scorers. When two very different players have about the same strength overall, the team's need usually settles the debate on who to pick. To make the models as generally applicable as possible, I've decided to rank players based on how many points per regular season game they are projected to get in the future. Note that this statistic is only relevant for forwards, not defensemen nor goalies.

- Which forward at our drafting position will score the most points per regular season game?

Now that we have a metric to rank the players, we need to specify a timestamp for our projection. From the team's point of view, do we want the player that will score the most points in the next season or e.g. in five years? Again, this is different from team to team. For the sake of this project, I've decided to project the number of points per regular season game five years after the draft. Arguably, young players need time to develop before we have a good idea of their peaking value and five years is fair. 

- Which forward at our drafting position will score the most points per regular season game five years after being drafted?

There is one final thing to add to make it a measurable question: in which league(s) do we project the statistic? Only considering the NHL might be a practical concern. Indeed, some players will stay longer in the AHL and dominate there before having a shot in the NHL simply because they need more time to develop. Thus, NHL teams arguably might want to know how good a player will be in the AHL five years after the draft if they do not make it to the NHL just yet.

- Which forward at our drafting position will score the most points per regular season game in either the NHL or the AHL five years after being drafted?

This is a measurable question. To compare projections in the AHL and the NHL, I have decided to turn the problem into a classification one. Briefly, the models will classify players in buckets of points per regular season game in either the AHL or the NHL. The classes/projections will consists of a league (either the AHL or the NHL) and a range of points per game (e.g. \[0.6, 0.8) ). This is because the skill gap between the NHL and the AHL is considerable and the same point rate per game in both leagues reflects very different player skill levels. 

  

  
## Data Collection
The dataset consists of several regular season, playoff, and other statistics about NHL-drafted player from the CHL between 2001 and 2019 (inclusive). Each record corresponds to a drafted player and each feature corresponds to a statistic about it. Among the various hockey databases freely available on the web, HockeyDB is a great place to start collecting this data. Indeed, on HockeyDB, every drafted player is attributed a unique ID that can be used to retrieve yearly statistics about such player in many different leagues, including the CHL, NHL, and AHL. The main concern with collecting data from HockeyDB alone is that there aren't a ton of statistics to work with. For example, the regular season stats only include the GP (number of games played), G (number of goals scored), A (number of assists), Pts (number of points), PIM (number of penalty minutes), and the +/-. However, together with the player's name and the team he played for, we have a great set of features that can almost uniquely define a player. Truly, it would be improbable that two players with the same name played for the same team, during the same year, and had all of those statistics equal. 

For every drafted player from the CHL, we will retrieve their regular season, playoff, and other statistics from the year they have been drafted. For example, if a player is drafted in the 2007 NHL Entry Draft, then we will be gathering data from his 2006-07 regular season and 2007 playoffs in the CHL. Future work could explore whether gathering data from previous junior years help to develop better models. First, basic data will be scraped from the HockeyDB player's data web page. Then, we will seek more features from the CHL website, including e.g. *First (the number of games for which the player has scored the first goal) *DS ("Dangerous Shots", the number of shots close to the net), and *PPG (the number of powerplay goals). After, we will retrieve the player's *Weight and *Height at the draft from the NHL website. Finally, we will retrieve our target feature, regular season *PTS/GP, from HockeyDB five years after the corresponding NHL Entry Draft. To put all of this together, several inner joins will be used between the tables. All in all, the data collection process should be thought of as collecting data from HockeyDB and then adding features to create a more complete dataset.

All data used in this project will be stored in the *data directory. Within it will four sub-directories. First, the *html_pages directory will store the HTML code (page source) of the web pages we will be scraping using BeautifulSoup. Next, the *extracted_data directory will store all the raw data the scrapers have extracted from the web pages. Third, the *model_dataset directory will store the datasets that will be used to develop the machine learning models. Finally, the *other directory contains tools that will be useful when merging the tables together. Especially, those tools are used to uniformize the information across two sources (e.g. the Rimouski Oceanic in the QMJHL might be referred to as Rim on one website and Rimouski Oceanic on another, yet this is the same information).

Over the data collection process, I will be using draft years and regular season years. To be clear, draft years are referring to the year the NHL Entry Drafts occur in, e.g. 2007, whereas regular season years are referring to the years the regular seasons span across, e.g. 2006-07.

TLDR: To check how to collect the whole data, it is sufficient to check the Automating the Data Collection Process section.

  

### HockeyDB stats scraping:
As mentioned above, the first step will be to collect basic statistics from HockeyDB. To start, there is a web page for every NHL Entry Draft on HockeyDB. From there, we can access every drafted player's data web page and retrieve the data corresponding to the appropriate years. For this scraping task, I have decided to use Selenium with a Firefox webdriver. The hockeydb_scraper.py script takes as input a draft year and the gap in years between the NHL Entry Draft and the time to record the *PTS/GP target (which should be thought of as in how many years after the draft we want to retrieve the regular season *PTS/GP statistic). It retrieves all the necessary data from HockeyDB for the input draft year. To automate the process of scraping for multiple years, the fetch_hockeydb_data.sh script should be called. From the user's standpoint, running the bash script is sufficient to collect the data from HockeyDB. For example, to retrieve the data on HockeyDB from the 2001 draft until the 2019 draft with a gap of five years between the NHL Entry Draft and the target recording, one would call

    ./fetch_hockeydb_data.sh 2001 2019 5

It took one hour and twenty minutes to run the script on my machine with those inputs. Note that there are about 230 web pages to scrape per draft year, for a total of roughly 4,370 web pages to scrape between 2001 and 2019.

  

### CHL stats scraping:
Next, we will scrape the CHL website for additional CHL statistics. The webpages of interest are statically loaded, so I have used the BeautifulSoup and Requests packages to scrape them. One of the concerns is that the URLs of the desired pages contain a number (e.g. https://chl.ca/lhjmq/en/stats/players/178/) which depends, to the best of my knowledge, on the number of webpages already created on the website. Yet, when the number is omitted, the web browser is directed to the most recent webpage (i.e. the webpage of the most recent data). Thankfully, the page source of the most recent web page contains the URLs of the other pages of interest. 

The retrieve_chl_urls.py script retrieves the URLs of the desired pages from the most recent web page's page source. Then, the chl_scraper.py script will scrape the CHL website and retrieve the data for a specific season. Both scripts have been written so that all web pages' page source contents are stored locally if they are not already there, and then the scripts work with the locally stored content. This is to avoid requesting the CHL's website unnecessarily. Finally, the fetch_chl_data.sh script automates the process of retrieving data using the two scripts above for multiple years. Note that the chl_scraper.py script is called twice by fetch_chl_data.sh: once for the regular season and another time for the playoffs. From the user's standpoint, running the bash script is sufficient to collect the data from the CHL website. For now, the script should be called with two arguments: the starting and ending season years. For example, to retrieve the CHL data from 2000-01 until 2018-19, one would call

    ./fetch_chl_data.sh 2000-01 2018-19

It took two minutes to run the script on my machine with those inputs.

Gotcha: The CHL website has been able to detect that scrapers were used, even with custom headers, after as little as two requests. So the scripts might only work when the page sources are already stored locally. However, as there would only be six of new pages to add every year (regular season and playoffs for each of the three junior leagues), I didn't bother too much on this issue. Still, all the scripts can take as input the User Agent as well, but this argument can be omitted when calling them. In the future, it would be interesting to see if using other scraping techniques and packages (e.g. Selenium) would solve the issue. The main branch contains the page sources needed.

  

### NHL draft scraping:
The *Weight and *Height at the draft have been scraped from the NHL website. As those webpages are dynamically loaded, the scraper is built using Selenium and a Firefox webdriver. The nhl_draft_scraper.py retrieves those features for every NHL-drafted player from the CHL for a specific year, as well as other features used to merge the tables (i.e. the player's name, junior team, etc.). To automate the process of collecting the features for multiple consecutive years, the fetch_nhl_draft_data.sh bash script should be used. For example, to retrieve the NHL draft data from the 2001 draft until the 2019 draft, one would call

    ./fetch_nhl_draft_data.sh 2001 2019

It took four minutes and 30 seconds to run the script on my machine with those inputs.

  

### Merging the Data
The final step of the data collection process is to merge the data we have gathered. First, we will do an inner join between the HockeyDB data and the CHL stats data on the players' names, junior teams, GP, G, A, and PTS. As already mentioned, it would be surprising that those features do not uniquely define a player for a given year, so I have assumed that they do. Next, we will perform an inner join between the obtained table and the NHL draft data on the players' names and junior teams. Since drafted players in a specific year are referred to by their names and junior teams, I will assume that they uniquely define a player. The create_dataset.py script does all this work. To create the dataset from the 2001 draft to the 2019 draft, one would call

    ./create_dataset.py -f 2001 -l 2019

It is worth addressing the potential disparities among the HockeyDB, the CHL, and the NHL websites. First, there are very few differences in the GP, G, A, and PTS statistics for the same player between the HockeyDB and the CHL website (less than a handful per year). As these errors occur randomly, I have decided to exclude the players with at least one disparity in those features because doing this would not introduce bias. Next, I have observed that most of the disparities among the three websites occur in the players' name. From my observations, about 4% of the drafted CHL players have their names spelled differently in at least two of the three websites. I noticed that those players usually have a cognate first name, e.g. Mike and Michael, or their last name is capitalized differently. e.g. McLachlan and Mclachlan. So I wouldn't say that these errors are happening randomly among the players. However, I think it is fair to assume in general that a player's name is independent of his success. Especially, that those errors do not target any type of player from the point of view of hockey statistics. Hence, I have decided to exclude the players whose names are spelled differently across at least two websites as doing so would again not introduce any bias. 

  

### Automating the Data Collection Process
The collect_data.sh script can be called to do the whole data collection process. To create the dataset from the 2001 draft to the 2019 draft and to record the regular season PTS/GP statistics (target) five years after the players' NHL Entry Draft, one would call

    ./collect_data.sh 2001 2019 5

It took one hour and thirty minutes to run the script on my machine with those inputs. The dataset obtained from the data collection has 917 player records over 57 different statistics.

  


## Data Annotation: Classifying Records
There are 13 possible classes. First, the PTS/GP statistic can fit in either of the following six ranges of values:

    [0.0, 0.2), [0.2, 0.4), [0.4, 0.6), [0.6, 0.8), [0.8, 1.0), [1.0, ...)

Note that the square bracket means that the value is included where as the parenthesis means that the value is excluded. For example, a value of 0.2 falls within \[0.2, 0.4) and not [0.0, 0.2). Also, the statistic can be retrieved in either the AHL or the NHL. Mapping all possible leagues and ranges gives a total of 12 classes. The last class is reserved for the players who haven't played in either the NHL or the AHL a few years after the draft (third input to the collect_data.sh script). For this project, I've decided to record the statistic five years after a player has been drafted.

The classification process is fairly straightforward and is already implemented during the data collection; the user has nothing to do to classify the records. First, the PTS/GP statistic is retrieved from the HockeyDB scraping. Then, the class is obtained by mapping the value to the league it was measured in and the range of values that include it. For example, if a player was drafted in the 2009 NHL Entry Draft and only played in the NHL during the 2013-14 regular season (2009 + 5 = 2014) with a PTS/GP statistic of 0.47, then this record is classified as: NHL \[0.4, 0.6).

For players who have played in both the NHL and the AHL five years after being drafted, the PTS/GP statistic is taken from the league they have played the most games into. For example, if a player was drafted in the 2004 NHL Entry Draft and played 47 games in the AHL with a PTS/GP of 0.87 and 23 games in the NHL with a PTS/GP of 0.20 during the 2008-09 regular season, then the record is classified as: AHL \[0.8, 1.0). 

For players who have played the same amount of games in the NHL and the AHL, the statistic is taken from the NHL. For example, if a player was drafted in the 2015 NHL Entry Draft and played 34 games in the AHL with a PTS/GP of 0.57 and 34 games in the NHL with a PTS/GP of 0.34 during the 2019-20 regular season, then the record is classified as: NHL \[0.2, 0.4)

Finally, players who haven't played in either the NHL or the AHL five years after being drafted are classified as: "0". 

  

  
## Results
This section will explore the different models' performance. To consult the in-depth data analysis and model construction, please consult X.
