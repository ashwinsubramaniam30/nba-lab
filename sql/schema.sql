-- Raw layer: what the API returns, lightly renamed. One row per team per game.
CREATE TABLE IF NOT EXISTS raw_team_games (
    season       VARCHAR NOT NULL,   -- '2025-26'
    season_type  VARCHAR NOT NULL,   -- 'Regular Season' or 'Playoffs'
    game_id      VARCHAR NOT NULL,   -- text, keeps leading zeros
    game_date    DATE    NOT NULL,
    team_id      VARCHAR NOT NULL,
    team_abbr    VARCHAR,
    team_name    VARCHAR,
    matchup      VARCHAR,
    wl           VARCHAR,
    minutes      INTEGER,
    pts INTEGER, fgm INTEGER, fga INTEGER, fg3m INTEGER, fg3a INTEGER,
    ftm INTEGER, fta INTEGER, oreb INTEGER, dreb INTEGER, ast INTEGER,
    stl INTEGER, blk INTEGER, tov INTEGER, pf INTEGER,
    plus_minus   DOUBLE,
    pulled_at    TIMESTAMP NOT NULL, -- when we downloaded it
    PRIMARY KEY (game_id, team_id)
);

-- Clean layer: built from raw_team_games by SQL (you'll write these next).
CREATE TABLE IF NOT EXISTS teams (
    team_id   VARCHAR PRIMARY KEY,
    team_abbr VARCHAR NOT NULL,
    team_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS games (
    game_id      VARCHAR PRIMARY KEY,
    season       VARCHAR NOT NULL,
    season_type  VARCHAR NOT NULL,
    game_date    DATE    NOT NULL,
    home_team_id VARCHAR NOT NULL,
    away_team_id VARCHAR NOT NULL,
    home_pts     INTEGER NOT NULL,
    away_pts     INTEGER NOT NULL,
    neutral_site BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS team_box (
    game_id     VARCHAR NOT NULL,
    team_id     VARCHAR NOT NULL,
    opponent_id VARCHAR NOT NULL,
    is_home     BOOLEAN NOT NULL,
    pts INTEGER, fgm INTEGER, fga INTEGER, fg3m INTEGER, fg3a INTEGER,
    ftm INTEGER, fta INTEGER, oreb INTEGER, dreb INTEGER, ast INTEGER,
    stl INTEGER, blk INTEGER, tov INTEGER, pf INTEGER,
    possessions DOUBLE,
    PRIMARY KEY (game_id, team_id)
);