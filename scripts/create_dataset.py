import argparse
import json
import pandas as pd
from pathlib import Path

JUNIOR_LEAGUES = ['QMJHL', 'OHL', 'WHL']
FORWARDS_POSITIONS = ['C', 'LW', 'RW']

# Format the HockeyDB Team feature to match the CHL Team feature
def format_team_hockeydb(base_table):
    hdb_chl_team_label_map_file = open("../data/other/hdb_chl_team_label_map.json", "r")
    hdb_team_label_map = json.load(hdb_chl_team_label_map_file)
    base_table['Team'] = base_table['Team'].map(hdb_team_label_map)
    base_table = base_table.explode('Team')
    hdb_chl_team_label_map_file.close()
    return base_table


# Format the NHL Draft Team feature to match the CHL Team feature
def format_team_nhldraft(nhldraft_table):
    nhldraft_chl_team_label_map_file = open("../data/other/draft_chl_team_label_map.json", "r")
    nhldraft_chl_team_label_map = json.load(nhldraft_chl_team_label_map_file)
    nhldraft_table['Team'] = nhldraft_table['Team'].map(nhldraft_chl_team_label_map)
    nhldraft_table = nhldraft_table.explode('Team')
    nhldraft_chl_team_label_map_file.close()
    return nhldraft_table


# Load and Combine the CHL data
def load_chl_data(current_year):
    first_year_reg_season = str(int(current_year) - 1)
    last_year_reg_season = str(int(current_year) % 100)
    if (len(last_year_reg_season) == 1):
        last_year_reg_season = "0" + last_year_reg_season
    season_year = first_year_reg_season + "-" + last_year_reg_season

    chl_reg_season_table = None
    chl_playoffs_table = None
    for junior_league in JUNIOR_LEAGUES:
        jl_lower = junior_league.lower()
        junior_league_reg_season_table = pd.read_csv(f"../data/extracted_data/{jl_lower}/regular_season/{jl_lower}_{season_year}_regular_season_stats.tsv", sep='\t', encoding='utf8')
        junior_league_reg_season_table['Year'] = season_year
        if (junior_league == JUNIOR_LEAGUES[0]):
            chl_reg_season_table = junior_league_reg_season_table
        else:
            chl_reg_season_table = pd.concat([chl_reg_season_table, junior_league_reg_season_table])
            
        junior_league_playoff_table = pd.read_csv(f"../data/extracted_data/{jl_lower}/playoffs/{jl_lower}_{current_year}_playoffs_stats.tsv", sep='\t', encoding='utf8')
        if (junior_league == JUNIOR_LEAGUES[0]):
            chl_playoffs_table = junior_league_playoff_table
        else:
            chl_playoffs_table = pd.concat([chl_playoffs_table, junior_league_playoff_table])
    
    chl_playoffs_table = chl_playoffs_table.rename(columns={"PName" : "Name", "PTeam" : "Team"})
    chl_playoffs_table = chl_playoffs_table.loc[chl_playoffs_table['PPosition'].isin(FORWARDS_POSITIONS)]
    chl_playoffs_table = chl_playoffs_table.drop(columns=['PPosition'])
    chl_reg_season_table = chl_reg_season_table.loc[chl_reg_season_table['Position'].isin(FORWARDS_POSITIONS)]
    chl_reg_season_table = chl_reg_season_table.drop(columns=['Position'])
    return chl_reg_season_table, chl_playoffs_table 


def main():
    global JUNIOR_LEAGUES
    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help="First Draft Year to Scrape")
    parser.add_argument("-l", help="Last Draft Year to Scrape")
    args = parser.parse_args()
    first_draft_year = args.f
    last_draft_year = args.l
    current_year = first_draft_year

    # Add data for every year of interest
    dataset = None
    while (int(current_year) <= int(last_draft_year)):

        # Load HockeyDB data and format Team feature
        base_table = pd.read_csv(f"../data/extracted_data/base/base_table_draft{current_year}.tsv", sep='\t', encoding='utf8')
        base_table_team_formatted = format_team_hockeydb(base_table)
        base_table_formatted = base_table_team_formatted.drop(columns=['Rank', 'PIM', '+/-', 'PPIM'])

        # Load CHL data
        chl_reg_season_table, chl_playoffs_table = load_chl_data(current_year)

        # Load NHL Draft data
        nhldraft_table = pd.read_csv(f"../data/extracted_data/draft/draft{current_year}_stats.tsv", sep='\t', encoding='utf8')
        nhldraft_table_team_formatted = format_team_nhldraft(nhldraft_table)
        nhldraft_table_formatted = nhldraft_table_team_formatted.drop(columns=['Position', 'League'])


        # Merge HockeyDB and CHL
        base_table_chl_reg_season_augmented = pd.merge(base_table_formatted, chl_reg_season_table, how='inner', 
                                                       on=['Name', 'Team', 'GP', 'G', 'A', 'PTS'])
        
        
        # Those who didn't play in the playoffs have no record in the CHL website
        # But their statistics should be set to 0 (e.g. 0 goal scored)
        base_table_chl_augmented = pd.merge(base_table_chl_reg_season_augmented, chl_playoffs_table, how='inner',
                                            on=['Name', 'Team', 'PGP', 'PG', 'PA', 'PPTS'])

        no_playoff_stats = base_table_chl_reg_season_augmented.loc[base_table_chl_reg_season_augmented['PGP'] == 0]
        extra_columns = set(base_table_chl_augmented) - set(no_playoff_stats)
        for col in extra_columns:
            no_playoff_stats = no_playoff_stats.assign(**{col: 0})
        
        base_table_chl_augmented = pd.concat([base_table_chl_augmented, no_playoff_stats], ignore_index=True)
        
        # Merge above and NHL Draft
        base_table_augmented = pd.merge(base_table_chl_augmented, nhldraft_table_formatted, how='inner',
                                        on=['Name', 'Team'])

        # Append to overall dataset
        if (current_year == first_draft_year):
            dataset = base_table_augmented
        else:
            dataset = pd.concat([dataset, base_table_augmented])
        
        # Go to next year
        current_year = str(int(current_year) + 1)
        
    # Write dataset to file
    dataset_formatted = dataset.drop(columns=['Name', 'Team'])
    Path("../data/model_dataset").mkdir(parents=True, exist_ok=True)
    dataset_formatted.to_csv(f'../data/model_dataset/whole_dataset{first_draft_year}-{last_draft_year}.tsv', sep='\t', index=False, encoding='utf8')





if __name__ == "__main__":
    main()