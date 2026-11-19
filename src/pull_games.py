"""Download NBA team game logs into raw_team_games.

Run from the nba-lab folder:
    python src/pull_games.py            # all seasons
    python src/pull_games.py 2026-27    # just one season
"""
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "nba.duckdb"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"

SEASONS = ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26", "2026-27"]
SEASON_TYPES = ["Regular Season", "Playoffs"]

# API column name -> our column name
RENAME = {
    "GAME_ID": "game_id", "GAME_DATE": "game_date", "TEAM_ID": "team_id",
    "TEAM_ABBREVIATION": "team_abbr", "TEAM_NAME": "team_name",
    "MATCHUP": "matchup", "WL": "wl", "MIN": "minutes", "PTS": "pts",
    "FGM": "fgm", "FGA": "fga", "FG3M": "fg3m", "FG3A": "fg3a",
    "FTM": "ftm", "FTA": "fta", "OREB": "oreb", "DREB": "dreb",
    "AST": "ast", "STL": "stl", "BLK": "blk", "TOV": "tov", "PF": "pf",
    "PLUS_MINUS": "plus_minus",
}


def fetch(season, season_type, tries=3):
    """Download one season + season type, retrying if the request fails."""
    for attempt in range(1, tries + 1):
        try:
            finder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season,
                season_type_nullable=season_type,
                league_id_nullable="00",
                timeout=60,
            )
            return finder.get_data_frames()[0]
        except Exception as e:
            print(f"  attempt {attempt} failed: {e}")
            time.sleep(5 * attempt)
    raise RuntimeError(f"Could not download {season} {season_type}")


def clean(df, season, season_type):
    """Rename columns, fix types and add our extra columns."""
    df = df[list(RENAME)].rename(columns=RENAME)
    df["game_id"] = df["game_id"].astype(str).str.zfill(10)
    df["team_id"] = df["team_id"].astype(str)
    df["game_date"] = pd.to_datetime(df["game_date"]).dt.date
    df["season"] = season
    df["season_type"] = season_type
    df["pulled_at"] = datetime.now(timezone.utc).replace(tzinfo=None)
    return df


def main():
    seasons = sys.argv[1:] or SEASONS
    con = duckdb.connect(str(DB_PATH))
    con.execute(SCHEMA_PATH.read_text())

    for season in seasons:
        for season_type in SEASON_TYPES:
            print(f"{season} {season_type}...")
            raw = fetch(season, season_type)
            if raw.empty:
                print("  no games yet, skipping")
                continue
            df = clean(raw, season, season_type)

            con.register("new_rows", df)
            con.execute("BEGIN")
            con.execute(
                "DELETE FROM raw_team_games WHERE season = ? AND season_type = ?",
                [season, season_type],
            )
            con.execute("INSERT INTO raw_team_games BY NAME SELECT * FROM new_rows")
            con.execute("COMMIT")
            con.unregister("new_rows")
            print(f"  loaded {len(df)} rows")
            time.sleep(2)

    print(con.sql("""
        SELECT season, season_type,
               COUNT(*) AS team_rows,
               COUNT(DISTINCT game_id) AS games
        FROM raw_team_games
        GROUP BY ALL
        ORDER BY season, season_type
    """).df())
    con.close()


if __name__ == "__main__":
    main()