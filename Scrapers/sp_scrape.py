import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time

HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

def scrape_sports_reference(url):
    response = requests.get(url, headers=HEADERS)
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
    df = df[df['School'] != 'School']
    df.dropna(subset='School', inplace=True)
    
    # Remove 'NCAA' from end of team names
    df['School'] = (
        df['School']
        .astype(str)
        .str.replace('\xa0', ' ', regex=False)   # fix invisible space
        .str.replace(r'\s*NCAA.*$', '', regex=True)  # remove NCAA suffix
        .str.strip())
    return df

if __name__ == "__main__":
    years = range(2002, 2027)
    combined_df = pd.DataFrame()
    debug=False
    
    # Debugging to fix hidden character issues in names
    if debug:
        sp_url = "https://www.sports-reference.com/cbb/seasons/men/2002-school-stats.html"
        sp_df = scrape_sports_reference(sp_url)
        # top 5 names
        for name in sp_df['School'].head():
            print(repr(name))
        exit(0)

    for year in years:
        sp_url = f"https://www.sports-reference.com/cbb/seasons/men/{year}-school-stats.html"
        sp_df = scrape_sports_reference(sp_url)
        sp_df['Year'] = year
        if sp_df.empty:
            raise RuntimeError(f"Failed to scrape Sports Reference for year {year}")
        combined_df = pd.concat([combined_df, sp_df], ignore_index=True)
        time.sleep(2)

    combined_df.to_csv("Data/sports_reference_stats.csv", index=False)
