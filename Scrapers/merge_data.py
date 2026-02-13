import pandas as pd

if __name__ == "__main__":
    kenpom_df = pd.read_csv("Data/kenpom_stats.csv")
    sp_df = pd.read_csv("Data/sports_reference_stats.csv")

    kenpom_teams = kenpom_df['Team'].unique()
    sports_reference_teams = sp_df['School'].unique()

    kp_set = set(kenpom_teams)
    sp_set = set(sports_reference_teams)
    print(f"KenPom teams: {len(kp_set)}, Sports Reference teams: {len(sp_set)}")

    missing_kenpom = kp_set - sp_set
    missing_sportsref = sp_set - kp_set

    print("Unmatched kenpom teams:\n")
    for team in sorted(missing_kenpom):
        print(team)

    print("\nUnmatched sports reference teams:\n")
    for team in sorted(missing_sportsref):
        print(team)