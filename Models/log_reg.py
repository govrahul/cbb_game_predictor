import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import sklearn.metrics
import pickle
import numpy as np

def make_prediction(model, team1, team2, neutral=False):
    data = pd.read_csv("Data/kenpom_stats.csv")
    data = data[data['Year'] == 2026]

    features = ["NetRtg","ORtg","DRtg","Luck","SOS_NetRtg"]
    team1_stats = data[data['Team'] == team1][features].values.flatten()
    team2_stats = data[data['Team'] == team2][features].values.flatten()
    if len(team1_stats) == 0:
        raise ValueError(f"Team {team1} not found in data")
    if len(team2_stats) == 0:
        raise ValueError(f"Team {team2} not found in data")
    
    team1_stats = team1_stats.astype(float)
    team2_stats = team2_stats.astype(float)
    
    diff = team1_stats - team2_stats
    if not neutral:
        diff = np.append(diff, 1)
    else:
        diff = np.append(diff, 0)
    X = pd.DataFrame([diff], columns=model.feature_names)
    proba = model.predict_proba(X)[0]

    return {
        "team1": team1,
        "team2": team2,
        "team1_win_prob": proba[1],
        "team2_win_prob": proba[0]
    }

df = pd.read_csv("Data/model_stats_with_neutral.csv")
df["Home_Advantage"] = (~df["Neutral"]).astype(int)
df = df[["NetRtg_diff","ORtg_diff","DRtg_diff","Luck_diff","SOS_NetRtg_diff","Home_Advantage","Result"]]

# Adding flipped data so the model does not always predict team 1 wins
# Accuracy increased by 1%, AUC increased by 2%
df_flipped = df.copy()
for col in df.columns[:-1]:
    if col != "Home_Advantage":
        df_flipped[col] = -df_flipped[col]
df_flipped["Result"] = 1 - df_flipped["Result"]
df = pd.concat([df, df_flipped], ignore_index=True)

df.to_csv("Data/training_data_home_court_advantage.csv", index=False)

X = df.drop("Result", axis=1)
y = df["Result"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(sklearn.metrics.classification_report(y_test, y_pred))

accuracy = sklearn.metrics.accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}") # 0.76, about 11% better than guessing team 1 win every time
auc = sklearn.metrics.roc_auc_score(y_test, model.predict_proba(X_test)[:,1])
print(f"AUC: {auc:.2f}") # 0.83, strong performance

model.feature_names = X.columns.tolist()

with open("Models/log_reg_home_court_advantage.pkl", "wb") as f:
    pickle.dump(model, f)

result = make_prediction(model, "Michigan St.", "Michigan")
print(result)