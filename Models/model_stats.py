import pandas as pd

pd.set_option('display.max_columns', None)

df = pd.read_csv("Data/combined_game_stats.csv")

home_cols = [col for col in df.columns if col.startswith("Home_")
             and pd.api.types.is_numeric_dtype(df[col])]

for home_col in home_cols:
    away_col = home_col.replace("Home_", "Away_")
    
    # Only compute if matching away column exists
    if away_col in df.columns:
        diff_col = home_col.replace("Home_", "") + "_diff"
        df[diff_col] = df[home_col] - df[away_col]

df['Result'] = df['Result'].astype(int)

model_stats = df[
    [
        "Home_team",
        "Home_score",
        "Away_team",
        "Away_score",
        "NetRtg_diff",
        "ORtg_diff",
        "DRtg_diff",
        "AdjT_diff",
        "Luck_diff",
        "SOS_NetRtg_diff",
        "Result"
    ]
]

print(model_stats.head())
model_stats.to_csv("Data/model_stats.csv")
