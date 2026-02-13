import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("Data/model_stats.csv")

stats = [
    "NetRtg_diff",
    "ORtg_diff",
    "DRtg_diff",
    "AdjT_diff",
    "Luck_diff",
    "SOS_NetRtg_diff"
]

for stat in stats:
    win = df[df["Result"] == True][stat].dropna()
    loss = df[df["Result"] == False][stat].dropna()

    plt.figure()
    plt.boxplot([loss, win], labels=["Loss", "Win"])
    plt.title(f"{stat} vs Result")
    plt.xlabel("Game Result (Home Team)")
    plt.ylabel(stat)
    plt.show()

# NetRtg and ORtg as expected have a positive correlation with wins
# Luck also has a slight positive correlation
# DRtg surprisingly has a negative correlation
# AdjT and SOS_NetRtg have about no correlation (roughly the same distribution in wins and losses)

subset = df[stats + ["Result"]]
corr = subset.corr()[['Result']]
sns.heatmap(
    corr.sort_values(by='Result'),
    annot=True,
    cmap='coolwarm',
    center=0
)
plt.title("Correlation of Stats with Wins")
plt.show()

# From the correlation heatmap, tempo seems to be the least necessary predictor and will be excluded