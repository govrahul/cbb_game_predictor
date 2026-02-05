# Figure out what team names don't align across websites

import scrape
import pandas as pd
import re

def normalize_team_name(name: str) -> str:
    if pd.isna(name):
        print(name)
        return name
    
    name = name.strip()

    # Standard punctuation cleanup
    name = re.sub(r"\.", "", name)
    name = re.sub(r"\s+", " ", name)

    # Convert trailing / mid " St" to " State"
    # Examples:
    #   Michigan St. -> Michigan State
    #   N C State -> NC State (handled below)
    # Avoid:
    #   St John's
    #   Mount St Mary's
    name = re.sub(
        r"(?<!^) St(?!\s*[A-Za-z]*')\b",
        " State",
        name
    )

    # Saint normalization ONLY at start
    name = re.sub(r"^St ", "Saint ", name)

    # Directional/state abbreviations
    replacements = {
        r"\bFL\b": "Florida",
        r"\bOH\b": "Ohio",
        r"\bPA\b": "Pennsylvania",
        r"\bIL\b": "Illinois",
        r"\bMD\b": "Maryland",
        r"\bNC\b": "North Carolina",
        r"\bCA\b": "California",
        r"\bNY\b": "New York",
    }

    for pat, repl in replacements.items():
        name = re.sub(pat, repl, name)

    # Remove trailing seed numbers
    name = re.sub(r"\s\d+$", "", name)

    return name

KENPOM_TO_SPORTSREF = {
    "Albany": "Albany (NY)",
    "Arkansas Pine Bluff": "Arkansas-Pine Bluff",
    "BYU": "Brigham Young",
    "Bethune Cookman": "Bethune-Cookman",
    "CSUN": "Cal State Northridge",
    "Cal Baptist": "California Baptist",
    "Central Connecticut": "Central Connecticut State",
    "Charleston": "College of Charleston",
    "FIU": "Florida International",
    "Fairleigh Dickinson": "FDU",
    "Gardner Webb": "Gardner-Webb",
    "Grambling State": "Grambling",
    "Illinois Chicago": "Illinois-Chicago",
    "LIU": "Long Island University",
    "LSU": "Louisiana State",
    "Louisiana Monroe": "Louisiana-Monroe",
    "Loyola Chicago": "Loyola (IL)",
    "Loyola Maryland": "Loyola (MD)",
    "Maryland Eastern Shore": "Maryland-Eastern Shore",
    "McNeese": "McNeese State",
    "Miami Florida": "Miami (FL)",
    "Miami Ohio": "Miami (OH)",
    "Mount St Mary's": "Mount St. Mary's",
    "Nebraska Omaha": "Omaha",
    "Nicholls": "Nicholls State",
    "North Carolina State": "NC State",
    "Penn": "Pennsylvania",
    "Prairie View A&M": "Prairie View",
    "Queens": "Queens (NC)",
    "SIUE": "SIU Edwardsville",
    "SMU": "Southern Methodist",
    "Saint Bonaventure": "St. Bonaventure",
    "Saint Francis": "Saint Francis (PA)",
    "Saint John's": "St. John's (NY)",
    "Saint Mary's": "Saint Mary's (CA)",
    "Saint Thomas": "St. Thomas",
    "Sam Houston State": "Sam Houston",
    "Southeast Missouri": "Southeast Missouri State",
    "Southern Miss": "Southern Mississippi",
    "Stephen F Austin": "Stephen F. Austin",
    "Tennessee Martin": "Tennessee-Martin",
    "Texas A&M Corpus Chris": "Texas A&M-Corpus Christi",
    "UMBC": "Maryland-Baltimore County",
    "UMass Lowell": "Massachusetts-Lowell",
    "UNLV": "Nevada-Las Vegas",
    "USC": "Southern California",
    "USC Upstate": "South Carolina Upstate",
    "UT Rio Grande Valley": "Texas-Rio Grande Valley",
    "VCU": "Virginia Commonwealth",
}

def get_team_names():
    kenpom = scrape.scrape_kenpom_year(2026)
    sports_reference = scrape.scrape_sports_reference('https://www.sports-reference.com/cbb/seasons/men/2026-school-stats.html')

    kenpom_teams = kenpom['Team']
    sports_reference_teams = sports_reference['School']
    kenpom_teams = kenpom_teams.apply(normalize_team_name)
    kenpom_teams = kenpom_teams.replace(KENPOM_TO_SPORTSREF)
    kenpom_only = set(kenpom_teams) - set(sports_reference_teams)
    sports_reference_only = set(sports_reference_teams) - set(kenpom_teams)

    kenpom_only = sorted(list(kenpom_only))
    sports_reference_only = sorted(list(sports_reference_only))

    return kenpom_only, sports_reference_only

if __name__ == "__main__":
    kenpom_only, sp_only = get_team_names()
    print("Teams only in KenPom:")
    for team in kenpom_only:
        print(team)
    print("\nTeams only in Sports Reference:")
    for team in sp_only:
        print(team)