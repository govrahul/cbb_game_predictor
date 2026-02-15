import pandas as pd
import torch
import Models.nn
import pickle

def make_predictions(model, team1, team2, input_size=5):
    m = None
    if model == 'logreg':
        m = pickle.load(open('Models/log_reg.pkl', 'rb'))
    elif model == 'nn':
        m = Models.nn.MarchMadnessNN(input_size=input_size)
        m.load_state_dict(torch.load('Models/nn_model.pth'))
    else:
        raise ValueError("Model must be either 'logreg' or 'nn'")
    
    # Get data for input teams
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
    if model == 'logreg':
        X = pd.DataFrame([diff], columns=m.feature_names)
        proba = m.predict_proba(X)[0]
        return {
            "team1": team1,
            "team2": team2,
            "team1_win_prob": proba[1],
            "team2_win_prob": proba[0]
        }
    elif model == 'nn':
        X = torch.tensor(diff, dtype=torch.float32).unsqueeze(0)
        proba = torch.softmax(m(X), dim=1).detach().numpy()[0]
        return {
            "team1": team1,
            "team2": team2,
            "team1_win_prob": proba[1],
            "team2_win_prob": proba[0]
        }
    
if __name__ == "__main__":
    team1 = "Michigan"
    team2 = "Ohio St."
    print(make_predictions('logreg', team1, team2))
    print(make_predictions('nn', team1, team2))