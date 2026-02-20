import pandas as pd

combined = pd.DataFrame()
years = [2023, 2024, 2025]
for year in years:
    df = pd.read_parquet(f"Data/{year}-{year+1}Season.parquet", columns=["Home_team", "Home_score", "Away_team", "Away_score", "Neutral"])
    df["Year"] = year
    combined = pd.concat([combined, df], ignore_index=True)

combined.to_csv("Data/combined_games_with_neutral.csv", index=False)