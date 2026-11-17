from nba_api.stats.endpoints import leaguegamefinder

finder = leaguegamefinder.LeagueGameFinder(
    season_nullable="2025-26",
    league_id_nullable="00",
    season_type_nullable="Regular Season",
    timeout=60,
)
games = finder.get_data_frames()[0]
print(games.shape)
print(games.head())
games.to_csv("data/games_2025_26.csv", index=False)