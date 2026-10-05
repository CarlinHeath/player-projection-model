# quick test, can run this directly or in a scratch file
import src.data_pipeline.fetch
import src.data_pipeline.clean

devers_info = src.data_pipeline.fetch.fetch_player_info(646240)
prospect_info = src.data_pipeline.fetch.fetch_player_info(808265)
soto_stats = src.data_pipeline.fetch.fetch_hitter_stats(665742)
cole_stats = src.data_pipeline.fetch.fetch_pitcher_stats(543037)

print(src.data_pipeline.clean.clean_player_info(prospect_info))