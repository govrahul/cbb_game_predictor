import pandas as pd
import torch
import Models.nn
import pickle

def make_predictions(model, team1, team2, data):

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

    # Detect model type automatically
    if hasattr(model, "predict_proba"):  # sklearn logistic regression

        X = pd.DataFrame([diff], columns=model.feature_names_in_)
        proba = model.predict_proba(X)[0]

    else:  # assume PyTorch model

        X = torch.tensor(diff, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            proba = torch.softmax(model(X), dim=1).numpy()[0]

    return {
        "team1": team1,
        "team2": team2,
        "team1_win_prob": proba[1],
        "team2_win_prob": proba[0]
    }
    
if __name__ == "__main__":
    team1 = "Michigan"
    team2 = "Ohio St."
    logreg_model = pickle.load(open('Models/log_reg.pkl', 'rb'))
    nn_model = Models.nn.MarchMadnessNN(input_size=5) 
    nn_model.load_state_dict(torch.load('Models/nn_model.pth'))
    data = pd.read_csv("Data/KenPom Data - 2026.csv") 
    print(make_predictions(logreg_model, team1, team2, data))
    print(make_predictions(nn_model, team1, team2, data))