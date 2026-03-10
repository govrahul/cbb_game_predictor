import pandas as pd
import pickle
import streamlit as st
from make_predictions import make_predictions
from predict_bracket import simulate_bracket
from brackets import BIG10_BRACKET, ACC_BRACKET, BIG12_BRACKET, SEC_BRACKET
import altair as alt

st.set_page_config(
    page_title="College Basketball Game Predictor",
    page_icon="🏀",
    layout="wide"
)

# cache model and data
@st.cache_resource
def load_model():
    model = pickle.load(open('Models/log_reg.pkl', 'rb'))
    return model

@st.cache_data
def load_data():
    data = pd.read_csv("Data/KenPom Data - 2026.csv")
    return data

model = load_model()
data = load_data()
teams = sorted(data['Team'].unique())

tab1, tab2 = st.tabs(["Game Predictor", "Tournament Simulator"])

with tab1:
    st.title("NCAA Men's Basketball Win Probability Predictor")

    # Initialize session state if not already set
    if "team1" not in st.session_state:
        st.session_state.team1 = teams[0]
    if "team2" not in st.session_state:
        st.session_state.team2 = teams[1]

    col1, col2 = st.columns(2)

    with col1:
        team1 = st.selectbox(
            "Select Team 1",
            teams,
            key="team1"
        )

    with col2:
        team2 = st.selectbox(
            "Select Team 2",
            teams,
            key="team2"
        )


    # Get prediction
    result = make_predictions(model=model, team1=team1, team2=team2, data=data)
    p1 = result["team1_win_prob"]
    p2 = result["team2_win_prob"]

    st.markdown("---")
    st.subheader(f"{team1} vs {team2}")

    # Visual matchup card
    winner = team1 if p1 > p2 else team2
    confidence = max(p1, p2)

    st.markdown(
        f"""
        <div style="text-align:center; padding:20px;">
            <h2 style="margin-bottom:10px;">🏀 Matchup Prediction</h2>
            <h1 style="color:#1f77b4;">{winner} favored</h1>
            <h3>Confidence: {confidence:.1%}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Confidence tier
    if confidence > 0.75:
        st.success("🔥 Strong Favorite")
    elif confidence > 0.6:
        st.info("Moderate Edge")
    else:
        st.warning("Toss-Up Game")

    # Dual-sided probability bar
    fav1 = p1 > p2
    fav2 = p2 > p1

    color1 = "#4CAF50" if fav1 else "#E74C3C"
    color2 = "#4CAF50" if fav2 else "#E74C3C"

    st.markdown(
        f"""
        <div style="display:flex; width:100%; height:35px; border-radius:10px; overflow:hidden; margin-top:20px;">
            <div style="width:{p1*100}%; background-color:{color1};"></div>
            <div style="width:{p2*100}%; background-color:{color2};"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-weight:bold; margin-top:5px;">
            <span>{team1} {p1:.1%}</span>
            <span>{p2:.1%} {team2}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Strength breakdown
    st.markdown("### Key Matchup Differences")

    # Pull stats again to compute diffs
    features = ["NetRtg", "ORtg", "DRtg", "Luck", "SOS_NetRtg"]
    friendly_names = [
        "Overall Efficiency",     # NetRtg
        "Offensive Strength",     # ORtg
        "Defensive Strength",     # DRtg
        "Close Game Performance", # Luck
        "Strength of Schedule"    # SOS_NetRtg
    ]

    team1_stats = data[data['Team'] == team1][features].iloc[0]
    team2_stats = data[data['Team'] == team2][features].iloc[0]
    team1_stats = team1_stats.astype(float)
    team2_stats = team2_stats.astype(float)

    if team1_stats.empty or team2_stats.empty:
        st.error("One of the selected teams could not be found in the dataset.")
        st.stop()

    rows = []

    for feat, label in zip(features, friendly_names):
        v1 = team1_stats[feat]
        v2 = team2_stats[feat]

        # Determine which team is better in that metric
        if feat == "DRtg": # For devensive efficiency, lower is better
            team1_better = v1 < v2
            team2_better = v2 < v1
        else: # For all other metrics, higher is better
            team1_better = v1 > v2
            team2_better = v2 > v1

        v1_display = f"{v1:.2f} ✓" if team1_better else f"{v1:.2f}"
        v2_display = f"{v2:.2f} ✓" if team2_better else f"{v2:.2f}"

        rows.append([label, v1_display, v2_display])

    breakdown = pd.DataFrame(
        rows,
        columns=["Metric", f"Team 1: {team1}", f"Team 2: {team2}"]
    )

    st.dataframe(breakdown, use_container_width=True)

with tab2:
    st.title("Tournament Simulator")
    tournament = st.selectbox(
        "Select Tournament",
        ["Big 10", "ACC", "Big 12", "SEC"]
    )
    tournament = tournament.replace(" ", "").upper()
    bracket = globals().get(f"{tournament}_BRACKET")

    if st.button("Simulate Tournament"):
        progress_bar = st.progress(0)
        sorted_probs, round_probs = simulate_bracket(bracket, model, data, progress_bar=progress_bar)

        st.subheader("Champion Probabilities")
        df = pd.DataFrame(
            sorted_probs.items(), 
            columns=["Team", "Championship Probability"]
        )
        chart = alt.Chart(df).mark_bar().encode(
            x="Championship Probability:Q",
            y=alt.Y("Team:N", sort="-x")
        )
        st.altair_chart(chart, width='stretch')
        favorite = df.iloc[0]

        st.subheader("Tournament Favorite")
        st.markdown(
            f"""
            <div style="text-align:center; padding:20px;">
                <h2 style="margin-bottom:10px;">🏆 {favorite['Team']} favored to win</h2>
                <h3>Championship Probability: {favorite['Championship Probability']:.1%}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")
st.caption("Developed by: Rahul Govil")
st.caption("Data Source: https://kenpom.com/")