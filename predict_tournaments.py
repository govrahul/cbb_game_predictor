from predict_bracket import predict_bracket, simulate_bracket

if __name__ == "__main__":
    b10_bracket = [
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
    champ = predict_bracket(b10_bracket)
    print(f"Predicted Big 10 Champion: {champ}")
    probs = simulate_bracket(b10_bracket)

    acc_bracket = [
        [
            ("Stanford", "Pittsburgh"),
            ("SMU", "Syracuse"),
            ("Virginia Tech", "Wake Forest")
        ],
        [
            ("N.C. State", None),
            ("Louisville", None),
            ("Florida St.", "California"),
            ("Clemson", None)
        ],
        [
            ("Virginia", None),
            ("Miami FL", None),
            ("Duke", None),
            ("North Carolina", None)
        ]
    ]
    champ = predict_bracket(acc_bracket)
    print(f"Predicted ACC Champion: {champ}")
    probs = simulate_bracket(acc_bracket)

    b12_bracket = [
        [
            ("Arizona St.", "Baylor"),
            ("Cincinnati", "Utah"),
            ("BYU", "Kansas St."),
            ("Colorado", "Oklahoma St.")
        ],
        [
            ("Iowa St.", None),
            ("UCF", None),
            ("West Virginia", None),
            ("TCU", None)
        ],
        [
            ("Texas Tech", None),
            ("Arizona", None),
            ("Houston", None),
            ("Kansas", None)
        ]
    ]
    champ = predict_bracket(b12_bracket)
    print(f"Predicted Big 12 Champion: {champ}")
    probs = simulate_bracket(b12_bracket)

    sec_bracket = [
        [
            ("LSU", "Kentucky"),
            ("Mississippi St.", "Auburn"),
            ("Mississippi", "Texas"),
            ("South Carolina", "Oklahoma")
        ],
        [
            ("Missouri", None),
            ("Tennessee", None),
            ("Georgia", None),
            ("Texas A&M", None)
        ],
        [
            ("Florida", None),
            ("Vanderbilt", None),
            ("Alabama", None),
            ("Arkansas", None)
        ]
    ]
    champ = predict_bracket(sec_bracket)
    print(f"Predicted SEC Champion: {champ}")
    probs = simulate_bracket(sec_bracket)

