import pandas as pd
import name_standardizer

GAME_TO_COMBINED = {
    "A&M-Corpus Christi": "Texas A&M-Corpus Christi",
    "Alcorn": "Alcorn State",
    "App State": "Appalachian State",
    "Ark-Pine Bluff": "Arkansas-Pine Bluff",
    "Army West Point": "Army",
    "Boston U": "Boston University",
    "CSU Bakersfield": "Cal State Bakersfield",
    "Central Ark": "Central Arkansas",
    "Central Conn State": "Central Connecticut State",
    "Central Mich": "Central Michigan",
    "Charleston So": "Charleston Southern",
    "Col of Charleston": "College of Charleston",
    "ETSU": "East Tennessee State",
    "Eastern Ill": "Eastern Illinois",
    "Eastern Ky": "Eastern Kentucky",
    "Eastern Mich": "Eastern Michigan",
    "Eastern Wash": "Eastern Washington",
    "FGCU": "Florida Gulf Coast",
    "Fla Atlantic": "Florida Atlantic",
    "Ga Southern": "Georgia Southern",
    "LMU (California)": "Loyola Marymount",
    "Lamar University": "Lamar",
    "Miami (Florida)": "Miami (FL)",
    "Miami (Ohio)": "Miami (OH)",
    "Middle Tenn": "Middle Tennessee",
    "Mississippi Val": "Mississippi Valley State",
    "NIU": "Northern Illinois",
    "North Ala": "North Alabama",
    "Northern Ariz": "Northern Arizona",
    "Northern Colo": "Northern Colorado",
    "Northern Ky": "Northern Kentucky",
    "Ole Miss": "Mississippi",
    "Queens (North Carolina)": "Queens (NC)",
    "SFA": "Stephen F. Austin",
    "Saint John's (New York)": "St. John's (NY)",
    "Saint Mary's (California)": "Saint Mary's (CA)",
    "Saint Thomas (MN)": "St. Thomas",
    "Seattle U": "Seattle",
    "South Fla": "South Florida",
    "Southeast Mo State": "Southeast Missouri State",
    "Southeastern La": "Southeastern Louisiana",
    "Southern Ill": "Southern Illinois",
    "Southern Ind": "Southern Indiana",
    "Southern U": "Southern",
    "UAlbany": "Albany (NY)",
    "UConn": "Connecticut",
    "UIC": "Illinois-Chicago",
    "UIW": "Incarnate Word",
    "ULM": "Louisiana-Monroe",
    "UMES": "Maryland-Eastern Shore",
    "UNCW": "UNC Wilmington",
    "UNI": "Northern Iowa",
    "UT Martin": "Tennessee-Martin",
    "UTRGV": "Texas-Rio Grande Valley",
    "Western Caro": "Western Carolina",
    "Western Ill": "Western Illinois",
    "Western Ky": "Western Kentucky",
    "Western Mich": "Western Michigan",
}

if __name__ == "__main__":
    combined = pd.read_csv("Data/combined_data.csv")
    games = pd.read_parquet("Data/2023-2024Season.parquet", 
                            columns=['Home_team', 'Home_score', 'Away_team', 'Away_score'])

    games['Home_team'] = games['Home_team'].apply(name_standardizer.normalize_team_name)
    games['Home_team'] = games['Home_team'].replace(name_standardizer.KENPOM_TO_SPORTSREF)
    games['Home_team'] = games['Home_team'].replace(GAME_TO_COMBINED)

    combined_teams = set(combined['School'])
    game_teams = set(games['Home_team'])

    missing_combined = combined_teams - game_teams
    missing_game = game_teams - combined_teams

    print("Missing combined teams:")
    print(len(missing_combined))
    for team in sorted(missing_combined):
        print(team)

    print("\nMissing game teams:")
    print(len(missing_game))
    for team in sorted(missing_game):
        print(team)