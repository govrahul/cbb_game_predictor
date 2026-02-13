import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
from collections import defaultdict
import name_standardizer

HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

def dedupe_columns(cols):
    counts = defaultdict(int)
    new_cols = []

    for col in cols:
        if counts[col]:
            new_cols.append(f"{col}_{counts[col]}")
        else:
            new_cols.append(col)
        counts[col] += 1

    return new_cols

def scrape_kenpom(year):
    name_dict = name_standardizer.KENPOM_TO_SPORTSREF

    url = f"https://kenpom.com/index.php?y={year}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find("table", id="ratings-table")
    if table is None:
        raise RuntimeError(f"KenPom table not found for year {year}")
    
    df = pd.read_html(StringIO(str(table)), header=16)[0]
    print(df.head(10))
    exit(0)
    header_row = None
    for i, row in df.iterrows():
        row_values = row.astype(str).str.lower()
        if 'rk' in row_values.values and 'team' in row_values.values:
            header_row = i
            break

    if header_row is None:
        raise RuntimeError("Could not detect KenPom header row")
    
    df.columns = df.iloc[header_row]
    df.columns = dedupe_columns(df.columns)
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    df = df.rename(columns={
        'Rk': 'Kenpom_Rank',
        'NetRtg': 'Kenpom_Eff',
        'ORtg': 'Kenpom_Off_Eff',
        'ORtg_1': 'Kenpom_Off_Eff_Rank',
        'DRtg': 'Kenpom_Def_Eff',
        'Drtg_1': 'Kenpom_Def_Eff_Rank',
        'AdjT': 'Kenpom_AdjTempo',
        'AdjT_1': 'Kenpom_AdjTempo_Rank',
        'Luck': 'Kenpom_Luck_Rtg',
        'Luck_1': 'Kenpom_Luck_Rtg_Rank',
        'NetRtg_1': 'Kenpom_SoS',
        'NetRtg_2': 'Kenpom_SoS_Rank',
        'ORtg_2': 'Kenpom_Opp_Off_Eff',
        'ORtg_3': 'Kenpom_Opp_Off_Eff_Rank',
        'DRtg_2': 'Kenpom_Opp_Def_Eff',
        'Drtg_3': 'Kenpom_Opp_Def_Eff_Rank',
        'NetRtg_3': 'Kenpom_NcSoS_Eff',
        'NetRtg_4': 'Kenpom_NcSoS_Eff_Rank',
    })

    df = df[df['Team'] != 'Team']

    # Clean team names (remove seed/rank numbers)
    df['Team'] = (
        df['Team']
        .str.replace(r'\s\d+\*+$', '', regex=True)
        .str.strip()
    )

    # Add year + team_id
    df['Year'] = int(year)
    df['team_id'] = df['Team'] + "_" + df['Year'].astype(str)

    # Convert numeric columns
    numeric_cols = [
        'Kenpom_Rank',
        'Kenpom_Eff',
        'Kenpom_Off_Eff',
        'Kenpom_Def_Eff',
        'Kenpom_AdjTempo',
        'Kenpom_SoS',
        'Kenpom_Opp_Off_Eff',
        'Kenpom_Opp_Def_Eff'
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(subset=['Team'], inplace=True)
    df['Team'] = df['Team'].apply(name_standardizer.normalize_team_name)
    df['Team'] = df['Team'].replace(name_dict)

    return df[
        [
            'team_id',
            'Team',
            'Conf',
            'Year',
            'Kenpom_Rank',
            'Kenpom_Eff',
            'Kenpom_Off_Eff',
            'Kenpom_Def_Eff',
            'Kenpom_AdjTempo',
            'Kenpom_SoS',
            'Kenpom_Opp_Off_Eff',
            'Kenpom_Opp_Def_Eff'
        ]
    ]

if __name__ == "__main__":
    years = range(2002, 2027)
    combined_df = pd.DataFrame()
    
    debug = True
    
    if debug:
        y = 2024
        df = scrape_kenpom(y)
        print(df.shape)
        print([team for team in df['Team'].unique() if 'Duke' in team])
        exit(0)

    for year in years:
        print(f"Scraping Kenpom for year {year}")
        df = scrape_kenpom(year)
        if df.empty:
            raise RuntimeError(f"Failed to scrape KenPom for year {year}")
        combined_df = pd.concat([combined_df, df], ignore_index=True)
        time.sleep(2)

    combined_df.to_csv("Data/kenpom_stats.csv", index=False)