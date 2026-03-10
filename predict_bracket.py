import make_predictions

def predict_game(team1, team2, model):
    if team1 is None:
        return team2
    if team2 is None:
        return team1
    
    result = make_predictions.make_predictions(model, team1, team2)
    return team1 if result["team1_win_prob"] > result["team2_win_prob"] else team2

def advance_round(matchups, model):
    winners = []

    for team1, team2 in matchups:
        winner = predict_game(team1, team2, model)
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

def predict_bracket(bracket, model='logreg'):
    winners = None
    round_num = 1

    # Run the manually defined rounds first
    for round_matchups in bracket:

        print(f"Round {round_num}:\n")

        if winners is not None:
            round_matchups = fill_byes(round_matchups, winners)

        winners = advance_round(round_matchups, model)

        round_num += 1

    # Automatically generate remaining rounds
    while len(winners) > 1:

        print(f"Round {round_num}:\n")

        next_round = build_next_round(winners)

        winners = advance_round(next_round, model)

        round_num += 1

    champion = winners[0]
    return champion

if __name__ == "__main__":
    bracket = [
        # round 1
        [
            ("Prairie View A&M", "Alcorn St."),
            ("Jackson St.", "Grambling St.")
        ],
        # round 2
        [
            ("Bethune Cookman", None),
            ("Texas Southern", "Alabama A&M"),
            ("Southern", "Arkansas Pine Bluff"),
            ("Florida A&M", None)
        ]
    ]
    champ = predict_bracket(bracket)
    print(f"Predicted Champion: {champ}")