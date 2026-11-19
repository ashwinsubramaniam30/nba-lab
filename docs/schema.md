# Database schema

The database is a single DuckDB file (`data/nba.duckdb`). Raw data from the
NBA stats API is stored as-is in `raw_` tables, and clean tables are rebuilt
from it with SQL. That way a newly discovered data problem can be fixed by
changing the SQL, without downloading anything again.

## Tables

### raw_team_games
- **Grain:** one row per team per game, exactly as the NBA stats API returns it.
- **Primary key:** `game_id` + `team_id`
- **Why it exists:** keeps the original source data so the clean tables can
  always be rebuilt, and so we can check what the source actually said.
- **Notes:** IDs are stored as text to keep leading zeros (`0022500147`).
  `pulled_at` records when each row was downloaded.

### teams
- **Grain:** one row per team
- **Primary key:** team_id
- **Why it exists:** lookup table that maps each team_id to its abbreviation and name, so other tables only need to store the ID.

### games
- **Grain:** one row per each game 
- **Primary key:** game_id
- **Why it exists:** creates one row for each game with the important information i.e. season, date, home team, away team, and points scored by each
- **Notes:** a neutral site game means that the game was not played at either of the team's home court, so it was originally listed as "@" rather than "vs" for both teams

### team_box
- **Grain:** one row per team per game
- **Primary key:** game_id and team_id
- **Why it exists:** possessions let you measure efficiency fairly by using per 100 possessions and shooting stats (3-pointers, free throws) are what the luck adjustment uses.
- **Notes:** possessions is estimated as FGA − OREB + TOV + 0.44 × FTA

## Known data issues

### 1. PLUS_MINUS is unreliable
- **What:** in 7 games, one row's PLUS_MINUS was wrong
- **How I found it:** calculating the opponent's score by using the PLUS_MINUS stat gave two different scores for the same game
- **How it's handled:** scores come from each team’s own PTS, and PLUS_MINUS isn’t used

### 2. Neutral-site games
- **What:** the games are not played on either team's home floor
- **Which games:** the NBA cup semifinal and international games are all neutral-site games
- **How it's handled:** kept the team the NBA listed as home (the team after @) and added the neutral_site flag, so the model can skip home-court advantage for those games