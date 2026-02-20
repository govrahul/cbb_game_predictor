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
    games = pd.read_csv("Data/combined_games_with_neutral.csv")

    games = games[~games['Home_team'].str.contains('TBA')]

    games['Home_team'] = games['Home_team'].apply(name_standardizer.normalize_team_name)
    games['Home_team'] = games['Home_team'].replace(name_standardizer.KENPOM_TO_SPORTSREF)
    games['Home_team'] = games['Home_team'].replace(GAME_TO_COMBINED)

    games['Away_team'] = games['Away_team'].apply(name_standardizer.normalize_team_name)
    games['Away_team'] = games['Away_team'].replace(name_standardizer.KENPOM_TO_SPORTSREF)
    games['Away_team'] = games['Away_team'].replace(GAME_TO_COMBINED)

    combined_teams = set(combined['School'])
    game_teams = set(games['Home_team'])

    missing_combined = combined_teams - game_teams
    missing_game = game_teams - combined_teams

    # Some are missing because of exhibition games or other random matchups that aren't D1
    # All games containing these teams can be dropped
    print("Missing combined teams:")
    print(len(missing_combined))
    for team in sorted(missing_combined):
        print(team)

    print("\nMissing game teams:")
    print(len(missing_game))
    for team in sorted(missing_game):
        print(team)

    games = games[
        ~games['Home_team'].isin(missing_game) &
        ~games['Away_team'].isin(missing_game)
    ]

    stats_cols = [
        "NetRtg",
        "ORtg",
        "DRtg",
        "AdjT",
        "Luck",
        "SOS_NetRtg",
        "Opp_ORtg",
        "Opp_DRtg",
        "NCSOSNetRtg"
    ]

    team_stats = combined[["Year", "School"] + stats_cols]

    home_stats = team_stats.copy()
    home_stats = home_stats.rename(
        columns={col: f"Home_{col}" for col in stats_cols}
    )

    games = games.merge(
        home_stats,
        left_on=["Year", "Home_team"],
        right_on=["Year", "School"],
        how="left"
    ).drop(columns=["School"])

    away_stats = team_stats.copy()
    away_stats = away_stats.rename(
        columns={col: f"Away_{col}" for col in stats_cols}
    )

    games = games.merge(
        away_stats,
        left_on=["Year", "Away_team"],
        right_on=["Year", "School"],
        how="left"
    ).drop(columns=["School"])

    final_cols = (
        ["Year", "Neutral",
        "Home_team", "Home_score"] +
        [f"Home_{col}" for col in stats_cols] +
        ["Away_team", "Away_score"] +
        [f"Away_{col}" for col in stats_cols]
    )

    games_model = games[final_cols]
    pd.set_option('display.max_columns', None)
    games_model.dropna(inplace=True)
    games_model['Result'] = games_model['Home_score'] > games_model['Away_score']
    print(games_model.head())
    
    games_model.to_csv("Data/combined_game_stats_with_neutral.csv")