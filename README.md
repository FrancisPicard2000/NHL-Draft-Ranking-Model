# NHL-Draft-Ranking-Model

## Overview
This project aims to develop machine learning models to predict how good eligible draft hockey players will be in the future. Currently, the dataset consists of X statistics about all the players (X) who have played in the CHL (Canadian Hockey League) from X to X. The models are meant to be used by NHL teams before the yearly draft to get insights about the best player to select.



## Question Reformulation
My initial goal was to answer the fundamental question every team is trying to answer before the draft:

    - Which player at our drafting position will be the best?

This is often not an obvious question to answer and not quite measurable. First, what is meant by "best" player? While some people will prefer players who can play the whole 200 feet, others will love goal scorers. When two very different players have about the same strength overall, the team's need usually settles the debate. To make the models as generally applicable as possible, I've decided to rank players based on how many points per game they are projected to get in the future.

    - Which player at our drafting position will score the most points per game?

Now that we have a metric to rank the players, we need to specify a timestamp for our projection. From the team's point of view, do we want the player that will score the most points in the next season or e.g. in five years? Again, this is team dependent. For the sake of this project, I've decided to project the number of points per game in five years. Arguably, young players need time to develop before we know their peaking value and five years is fair. 

    - Which player at our drafting position will score the most points per game five years after the draft?

There is one final thing to add to make it a measurable question: in which league(s) do we project the points? Only considering the NHL might be a practical concern. Indeed, some players will stay longer in the AHL and dominate there before having a shot in the NHL. Thus, NHL teams arguably might want to know how good a player will be in the AHL five years after the draft if they do not make it to the NHL just yet.

    - Which player at our drafting position will score the most points per game in either the NHL or the AHL five years after the draft?

This is a measurable question. Yet, there are some things left to be specified. First, to compare point projections in the AHL and the NHL, this will be a classification problem. Briefly, models will classify players in buckets of points in either the AHL or the NHL in one of the X classes. Future work could explore on whether modeling the problem into a multioutput problem or a regression problem by only considering e.g. NHL would yield more desirable results. Second, for players who have played in the NHL and the AHL during their fifth year, the models will be trained to classify in the league the players have played the most. For players who have played the same amount of games in the NHL and the AHL during their fifth year, the NHL point projection will be looked at. Finally, from a practical standpoint, the models should be applied to all the eligible players before the draft. Then to select the best player at your drafting position, start from the top of the output list and select the highest not-yet-selected player.

