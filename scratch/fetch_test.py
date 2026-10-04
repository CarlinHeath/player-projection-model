# quick test, can run this directly or in a scratch file
import src.data_pipeline.fetch

print(src.data_pipeline.fetch.fetch_player_info(665742))     # real ID (Soto)
print(src.data_pipeline.fetch.fetch_hitter_stats(665742))
print(src.data_pipeline.fetch.fetch_pitcher_stats(543037))