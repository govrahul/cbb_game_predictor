import make_predictions
import random
from collections import Counter, defaultdict
from tqdm import tqdm
import pickle
import pandas as pd

def predict_game(team1, team2, model, data, simulate=False):
    if team1 is None:
        return team2
    if team2 is None:
        return team1
    
    result = make_predictions.make_predictions(model, team1, team2, data)
    p = result["team1_win_prob"]
    if simulate:
        return team1 if random.random() < p else team2
    else:
        return team1 if result["team1_win_prob"] > result["team2_win_prob"] else team2

def advance_round(matchups, model, data, simulate=False, verbose=True):
    winners = []

    for team1, team2 in matchups:
        winner = predict_game(team1, team2, model, data, simulate)
        if verbose:
            print(f"{team1} vs {team2} -> Predicted winner: {winner}\n")
        winners.append(winner)

    return winners

def fill_byes(matchups, winners):
    winners_iter = iter(winners)
    filled = []

    for team1, team2 in matchups:
        if team1 is None:
            team1 = next(winners_iter)

        if team2 is None:
            team2 = next(winners_iter)

        filled.append((team1, team2))

    return filled

def build_next_round(winners):
    next_round = []

    for i in range(0, len(winners), 2):
        team1 = winners[i]
        team2 = winners[i+1] if i + 1 < len(winners) else None
        next_round.append((team1, team2))

    return next_round

def predict_bracket(bracket, model, data, simulate=False, verbose=True):
    winners = None
    round_num = 1
    round_winners = []

    # Run the manually defined rounds first
    for round_matchups in bracket:

        if verbose:
            print(f"Round {round_num}:\n")

        if winners is not None:
            round_matchups = fill_byes(round_matchups, winners)

        winners = advance_round(round_matchups, model, data, simulate, verbose)

        round_winners.append(winners)

        round_num += 1

    # Automatically generate remaining rounds
    while len(winners) > 1:

        if verbose:
            print(f"Round {round_num}:\n")

        next_round = build_next_round(winners)

        winners = advance_round(next_round, model, data, simulate, verbose)

        round_winners.append(winners)

        round_num += 1

    champion = winners[0]

    return champion, round_winners

def simulate_bracket(bracket, model, data, nsim=500, verbose=True, progress_bar=None):
    round_counts = defaultdict(lambda: defaultdict(int))
    results = Counter()

    for i in range(nsim):
        champ, rounds = predict_bracket(bracket, model, data, simulate=True, verbose=False)
        results[champ] += 1

        for r, winners in enumerate(rounds):
            for winner in winners:
                round_counts[r][winner] += 1    

        if progress_bar and i % 50 == 0:
            progress_bar.progress(i / nsim)

    if progress_bar:
        progress_bar.progress(1.0)

    probs = {team: count/nsim for team, count in results.items()}
    sorted_probs = dict(sorted(probs.items(), key=lambda x: -x[1]))

    round_probs = {
        team: {r: count/nsim for r, count in rounds.items()}
        for team, rounds, in round_counts.items()
    }

    if verbose:
        for team, prob in sorted_probs.items():
            print(f"{team}: {prob:.2%}")

    return sorted_probs, round_probs

# for streamlit app
def predict_single_bracket(bracket, model, data):

    winners = None
    rounds = []

    for round_matchups in bracket:

        if winners is not None:
            round_matchups = fill_byes(round_matchups, winners)

        round_result = []
        round_winners = []

        for team1, team2 in round_matchups:

            winner = predict_game(team1, team2, model, data)

            round_result.append((team1, team2, winner))
            round_winners.append(winner)

        rounds.append(round_result)
        winners = round_winners

    # build remaining rounds automatically
    while len(winners) > 1:

        next_round = build_next_round(winners)

        round_result = []
        round_winners = []

        for team1, team2 in next_round:

            winner = predict_game(team1, team2, model, data)

            round_result.append((team1, team2, winner))
            round_winners.append(winner)

        rounds.append(round_result)
        winners = round_winners

    champion = winners[0]

    return champion, rounds

if __name__ == "__main__":
    bracket = [
        # round 1
        [
            ("Maryland", "Oregon"),
            ("Penn St.", "Northwestern")
        ],
        # round 2
        [
            ("Iowa", None),
            ("Washington", "USC"),
            ("Indiana", None),
            ("Minnesota", "Rutgers")
        ],
        # round 3
        [
            ("Ohio St.", None),
            ("Wisconsin", None),
            ("Purdue", None),
            ("UCLA", None)
        ],
        # round 4
        [
            ("Michigan", None),
            ("Illinois", None),
            ("Nebraska", None),
            ("Michigan St.", None)
        ]
    ]
    model = pickle.load(open('Models/log_reg.pkl', 'rb'))
    data = pd.read_csv("Data/KenPom Data - 2026.csv")
    champ = predict_bracket(bracket, model, data)
    print(f"Predicted Champion: {champ}")

    probs, _ = simulate_bracket(bracket, model, data)