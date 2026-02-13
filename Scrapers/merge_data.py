import pandas as pd
import name_standardizer

if __name__ == "__main__":
    kenpom_df = pd.read_csv("Data/kenpom_stats.csv")
    sp_df = pd.read_csv("Data/sports_reference_stats.csv")

    kenpom_df = kenpom_df[kenpom_df['Team'] != 'Team']
    sp_df = sp_df[sp_df['Year'] >= 2024]
    kenpom_df['Team'] = kenpom_df['Team'].apply(name_standardizer.normalize_team_name)
    kenpom_df['Team'] = kenpom_df['Team'].replace(name_standardizer.KENPOM_TO_SPORTSREF)

    kenpom_teams = kenpom_df['Team'].unique()
    sports_reference_teams = sp_df['School'].unique()

    kp_set = set(kenpom_teams)
    sp_set = set(sports_reference_teams)
    print(f"KenPom teams: {len(kp_set)}, Sports Reference teams: {len(sp_set)}")

    missing_kenpom = kp_set - sp_set
    missing_sportsref = sp_set - kp_set

    if missing_kenpom or missing_sportsref:
        print("Unmatched kenpom teams:\n")
        for team in sorted(missing_kenpom):
            print(team)

        print("\nUnmatched sports reference teams:\n")
        for team in sorted(missing_sportsref):
            print(team)
    else:
        print("All teams matched, merging datasets")
        combined = pd.merge(sp_df, kenpom_df, how='left', left_on=['School', 'Year'], right_on=['Team', 'Year'])
        combined.to_csv('Data/combined_data.csv')