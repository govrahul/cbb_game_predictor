from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
from collections import defaultdict
from time import sleep

def scrape_sports_reference(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    stats = soup.find("table", id="basic_school_stats")
    if not stats:
        raise RuntimeError("Could not find Sports Reference stats table")
    
    df = pd.read_html(StringIO(str(stats)))[0]
    df.columns = [
        f"{lvl0}_{lvl1}" if lvl1 else lvl0
        for lvl0, lvl1 in df.columns
    ]   
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel()

    df.reset_index(drop=True, inplace=True)
    df.drop(columns=['Unnamed: 0_level_0_Rk', 'Unnamed: 8_level_0_Unnamed: 8_level_1', 'Unnamed: 11_level_0_Unnamed: 11_level_1', 'Unnamed: 14_level_0_Unnamed: 14_level_1', 
                     'Unnamed: 17_level_0_Unnamed: 17_level_1', 'Unnamed: 20_level_0_Unnamed: 20_level_1'], inplace=True)
    df.rename(columns={'Unnamed: 1_level_0_School': 'School'}, inplace=True)
    df.columns = df.columns.str.replace('Conf.', 'Conf')

    # pd.set_option('display.max_columns', None)
    # print(df.head())
    return df

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

def scrape_kenpom_year(year):
    url = f"https://kenpom.com/index.php?y={year}"
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="ratings-table")
    if table is None:
        raise RuntimeError(f"KenPom table not found for year {year}")

    df = pd.read_html(StringIO(str(table)), header=18)[0]
    df.columns = df.iloc[0]
    df.drop(index=0, inplace=True)
    df.columns = dedupe_columns(df.columns)

    # Rename core columns
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

    # Remove repeated header rows inside table
    df = df[df['Team'] != 'Team']

    # Clean team names (remove seed/rank numbers)
    df['Team'] = (
        df['Team']
        .str.replace(r'\d+$', '', regex=True)
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
    combined_sports_reference_data = pd.DataFrame()
    combined_kenpom_data = pd.DataFrame()
    for year in years:
        sp_url = f"https://www.sports-reference.com/cbb/seasons/men/{year}-school-stats.html"
        df_sp = scrape_sports_reference(sp_url)
        df_sp['Year'] = year
        combined_sports_reference_data = pd.concat([combined_sports_reference_data, df_sp], ignore_index=True)
        df_kp = scrape_kenpom_year(year)
        combined_kenpom_data = pd.concat([combined_kenpom_data, df_kp], ignore_index=True)
        sleep(1)

    combined_sports_reference_data.to_csv("Data/sports_reference_data.csv", index=False)
    combined_kenpom_data.to_csv("Data/kenpom_data.csv", index=False)
    print("Data scraping complete")

    print("Joining datasets")
    merged = pd.merge(
        combined_sports_reference_data,
        combined_kenpom_data,
        left_on=['School', 'Year'],
        right_on=['Team', 'Year'],
        how='left'
    )
    merged.to_csv("Data/merged_data.csv", index=False)
    print("Merged data saved")