import pandas as pd
import make_predictions
from collections import deque

def predict_bracket(first_round_matchups, model='logreg', verbose=True):
    queue = deque()

    for team1, team2 in first_round_matchups:
        queue.append(team1)
        queue.append(team2)

    while len(queue) > 1:
        team1 = queue.popleft()
        team2 = queue.popleft()
        result = make_predictions.make_predictions(model, team1, team2)
        winner = team1 if result['team1_win_prob'] > result['team2_win_prob'] else team2
        if verbose:
            print(f"{team1} vs {team2} -> Winner: {winner}")
        queue.append(winner)

    if verbose:
        print(f"Predicted Champion: {queue[0]}")
    return queue[0]

if __name__ == "__main__":
    first_round = [
        ("Prairie View A&M", "Alcorn St."),
        ("Jackson St.", "Grambling St.")
    ]
    predict_bracket(first_round)