# Error Cases To Test

Running list of failure modes, edge cases, and open decisions for the player projection pipeline. "Expected" results are predictions from reading the code unless marked as observed. Run each case, record what actually happens, then decide on the handling (crash loudly, return `None`, skip, or log).

Status key: `[ ]` not tested or not decided, `[x]` tested or decided. Items starting with "Decide" are design choices, not tests.

## Test players

| Player | ID | Useful for |
|---|---|---|
| Juan Soto | 665742 | Standard hitter, traded mid-2022 (three rows that season) |
| Bobby Witt Jr. | 677951 | Name suffix (`last_name` is "Witt Jr.") |
| Franklin Arias | 808265 | Prospect: no debut date, no MLB stats |
| Gerrit Cole | 543037 | Pitcher with pre-DH hitting rows |
| Paul Skenes | 694973 | Modern pitcher, no hitting rows |
| Clayton Kershaw | 477132 | Retired (`active` false), pitcher from before the universal DH |
| Shohei Ohtani | 660271 | Two-way player (position `TWP`) |
| Mason Miller | 695243 | Closer, traded in 2025 (combined row) |
| Jose Ramirez | 608070 | Switch hitter (`bats` is `S`), Cleveland rename |
| Larry Walker | 123833 | Pre-2000 seasons, Expos rows use team 120 |
| Rafael Devers | 646240 | Exactly 6'0" |
| (fake) | 999999999 | Invalid ID |

## Environment and project setup

- [x] `python -m src.table_creation` reported "No module named src.table_creation". The script now lives in `src/data_pipeline/` and runs as `python -m src.data_pipeline.table_creation`. Check nothing else imports it from the old location.
- [ ] Always run from the project root with `python -m ...`. Running a file directly breaks the `src...` imports.
- [ ] Save files before debugging import errors (an unsaved `fetch.py` caused a confusing `ImportError` earlier).
- [ ] Laptop: `git pull` before working, `pip install -r requirements.txt` after dependency changes, rebuild the `.db` after schema changes (it does not travel through git).
- [ ] Re-run `pip freeze > requirements.txt` after installing anything new.
- [x] `scratch/` is git-ignored, so scratch files do not sync between machines.
- [ ] Add log and cache folders to `.gitignore` when they exist.
- [ ] Add a one-line TODO comment to each empty placeholder file so it reads as deliberate scaffolding.

## Fetch layer

- [x] `fetch_player_info`, `fetch_hitter_stats`, `fetch_pitcher_stats` tested against real IDs; none failed.
- [x] Fake ID on the info endpoint: no exception. The API returns status 404 with a dict containing `messageNumber`, `message`, `timestamp`, `traceId` and no `people` key. `requests` does not raise on a 404, so `.json()` returns the error dict.
- [x] Fake ID on the hitting and pitching stats endpoints: both return status 200 with `{"copyright": "...", "stats": []}`, identical to a real player with no stats (Arias, Skenes hitting). Tested in `test_stats_bad_id_response_looks_like_never_played`.
- [ ] Soto through the pitching endpoint (position player who never pitched): empty `stats`, or a block with empty `splits`?
- [ ] Use `save_json_to_file` to keep reference copies of each response shape.

## Player info (`clean_player_info`)

- [x] Invalid ID response shape observed (see Fetch layer).
- [x] Invalid ID through `clean_player_info` raises `KeyError` at `original_data["people"]`. Tested (`test_player_info_bad_id_raises_key_error`).
- [x] `people` exists but the list is empty: raises `IndexError` at `[0]`. Tested.
- [x] No `mlbDebutDate` (Arias): handled, `debut_date` is `None` and stored as a real NULL.
- [ ] No `birthDate`. Decide whether it is required (stop the pipeline) or optional like debut date.
- [ ] Missing or null nested blocks (`batSide`, `pitchHand`, `primaryPosition`). Decide which fields are required and which optional.
- [x] Silent `None` from a wrong key (the `"abbreviated"` bug): found and fixed, `position` is `LF` for Soto.
- [ ] Add a check that required fields are never `None` after cleaning.
- [x] Retired player: Kershaw `active` is stored as 0.
- [x] Switch hitter: Ramírez's `bats` is stored as `S`. Walker (retired, 1989 debut) loaded with `active` 0, height 75, weight 235.
- [x] All ten test players load with values in the right columns (checked against the database).
- [ ] After wiring in the helpers, confirm Soto, Witt, and Arias still match their saved outputs.
- [ ] Decide where the not-found check lives (see Pipeline).

## Cleaning helpers

`_convert_height`
- [x] Sample strings `6'1"`, `6'10"`, `5'5"`, `6' 0"` convert correctly; real heights for the test players loaded as 71 to 78 inches.
- [ ] No player under 5'8" tested yet.
- [x] `_convert_height` now returns `None` for `None`, `""`, `"183 cm"`, and `"6'"` (named exceptions in both blocks). Tested in `tests/test_helpers.py`, along with `6'1"`, `6'10"`, `5'5"`, and `6' 0"`.
- [ ] Docstring records the format, the integer-inches output, and the failure behavior.

`_create_date`
- [x] Tested `{}`, a `None` value, a valid string, `""`, and `"2018-13-45"`. All bad inputs return `None`.
- [x] Decided: a garbled date string returns `None`, same as a missing value (`TypeError` and `ValueError` both caught). Logging it is still open (see Logging).

`_get_nested_data`
- [x] Tested `{}`, `{"batSide": None}`, `{"batSide": {}}`, `{"batSide": {"code": "L"}}`, `{"batSide": "L"}`. Only the full block returns a value; the rest return `None`.
- [ ] `None` passed as the dictionary returns `None` silently. Decide whether that is acceptable.

`_convert_float`
- [x] Tested `".263"`, `"2.60"`, `".---"`, `None`, `""`, `"abc"`, and `263` (an int). `".---"` raises `ValueError` and `None` raises `TypeError`; both are caught by name.
- [x] A misspelled `float` now raises `NameError`, which is not in the `except` list, so it surfaces.
- [x] Decided: `_convert_float` returns `None` for anything unconvertible (`TypeError` and `ValueError`), including `".---"`.
- [ ] Decide which fields go through it (hitters: `avg`, `obp`, `slg`, `ops`, `babip`); counts stay integers.
- [x] Soto's file never puts `".---"` in a stored column (it appears only in `stolenBasePercentage` and `caughtStealingPercentage`, which the table does not store). Placeholder path tested with a direct call (`test_float_returns_none_for_placeholder`). A real player with no at-bats is still untested.

All helpers
- [x] Bare `except:` clauses replaced with named exception types in all four helpers. A typo that raises `AttributeError` (`.gett`, `.replce`) is still swallowed inside `_get_nested_data` and `_convert_height`.
- [ ] No test code (prints, sample strings) at module level in `clean.py`.

## Position handling

- [ ] Starting vs relief pitchers: compare the raw `primaryPosition` blocks (code, name, type, abbreviation) for Miller (closer) and Skenes (starter) and record what differs, if anything.
- [ ] If the API does not separate them, decide where the distinction comes from (games started vs games pitched, saves) and whether it belongs in `clean`, a new column, or a query.
- [ ] Role signal in the stat rows: Miller's 2023 row has 6 games started, then 0 starts and 20 to 38 saves a season from 2024 on. Decide whether role is derived from `games_started`, `games_played`, and `saves`.
- [x] Ohtani's position is `TWP` in the database.
- [ ] Decide whether to store `TWP` as-is or map it.
- [ ] Do not rely on `position == 'P'` alone to decide which stat tables to fill (Ohtani, pitchers who hit).
- [x] The stats response has no position field, so the `position` column was removed from both stat tables. Only `players` has `position`.

## Names and search

- [ ] Suffix players: an exact match on `"Witt"` misses `"Witt Jr."`. Test `LIKE` matching.
- [ ] Case sensitivity in search.
- [ ] Nicknames and legal first names (Witt's raw `firstName` is "Robert", stored `first_name` is "Bobby").
- [ ] Decide how a one-box search like "Bobby Witt" queries the stored columns (`full_name` is kept).

## Stats cleaning (`clean_hitter_stats`, `clean_pitcher_stats`)

- [x] Return a list of dictionaries, one per season and team, with keys matching the table columns (no `stat_id`, which SQLite generates).
- [x] `team_id` comes from the `team` block of each split.
- [x] Combined multi-team rows (`numTeams`, no `team` key) are skipped. Soto 2022 has three raw rows and two cleaned rows.
- [x] `".---"` placeholder in percentage fields: `_convert_float` returns `None` for it (see Cleaning helpers). The direct-call test is still open below.
- [x] Miller's 2025 Padres row has `".---"` in `winPercentage`, which the table does not store, so it does not exercise the conversion. Covered by the same direct-call test.
- [ ] Decide how to get season-level rates for traded pitchers, since the combined row is skipped and rates like ERA cannot be summed. Counts sum exactly (verified for Miller 2025), so ERA can be recomputed from `earned_runs` and `outs`.
- [ ] String-formatted numbers (`".263"`, `"2.60"`) need conversion to float; decide which shared helper does it.
- [x] Innings pitched: decided to store `outs` (an integer) instead of `inningsPitched`, because `"208.1"` means 208 and 1/3 innings and floats add wrongly (`208.1 + 100.2` gives `308.3`). Divide by `3.0` when innings are needed. Checks and the schema change are under Database and schema.
- [x] Prospect with no MLB games: both stats responses come back as `{"stats": []}`.
- [x] Skenes through the hitting endpoint: `{"stats": []}`.
- [ ] Check for a `stats` block with an empty `splits` list from the real API (not yet observed). A hand-built one raises `IndexError` (tested).
- [x] Can the pipeline tell "never played" from "bad ID" using the stats endpoints? No: a fake ID returns the same `{"stats": []}` as a player with no stats. Only the info endpoint (404, no `people` key) can catch a bad ID, so any bad-ID check belongs there (see Pipeline).
- [x] Early return: observed `TypeError: 'NoneType' object is not iterable` in the insert. The pipeline now skips empty results with a plain `if`, which handles both `None` and `[]`. The cleaners still return `None`.
- [x] Two-way and pre-2022 pitchers: Ohtani has rows in both tables (9 hitting, 7 pitching), Kershaw has 13 hitting and 18 pitching, Cole has 7 hitting (2013 to 2019) and 13 pitching. Position players have no pitching rows, and Skenes and Miller have no hitting rows.
- [ ] Rows for the current, in-progress season vs completed seasons.
- [x] Indexing fixed: `original_data["stats"][0]["splits"]`. `stats` is a list holding one block, so `["stats"]["splits"]` fails and a hardcoded index like `[3]` raises an error.
- [x] Row count: Soto's saved file has 11 splits and gives 10 cleaned rows once the combined 2022 row is skipped. Miller's pitching file has 6 splits and gives 5 rows, skipping the combined 2025 row.
- [x] Skip check for the combined row (`numTeams`) works for Soto 2022 and Miller 2025, and both team rows are kept.
- [ ] `player_id` via `_get_nested_data(dirty_data[0], "player", "id")` should give 665742. Decide whether it is required (a missing ID should stop the run) and whether to read it from the first split or from each split.
- [x] `dirty_data[0]` raises `IndexError` if `stats` exists but `splits` is empty. Tested with a hand-built response (`test_stats_block_with_empty_splits_raises_index_error`).
- [ ] While testing extraction, use square brackets so a wrong key raises `KeyError` instead of quietly returning `None`.
- [x] Compared the raw `stat` keys with the table columns. Hitters: 34 raw keys, 27 used, 7 deliberate omissions. Pitchers: all 44 table columns match the cleaned dictionary. `position` is no longer a column.
- [ ] Decide: a mapping of column name to API key vs 27 separate `.get(...)` lines. API names differ from column names (for example `homeRuns` vs `home_runs`).
- [x] Check known values: Soto 2025 is 160 games, 43 home runs, 38 stolen bases, 577 at-bats; the 2022 Padres row is 52 games. All match. Skenes 2024 (23 games, 170 strikeouts, 11-3, 399 outs, 514 batters faced) also matches.
- [x] Every cleaned dictionary has the same keys, and no stat value is `None`. True for Soto (10 rows), Skenes (3 rows), and Miller (5 rows) after the key fix below.
- [x] Pitching raw key is `strikeoutsPer9Inn` (lowercase o). The wrong capital gave `None` in every row with no error, because `_get_nested_data` and `_convert_float` both return `None` on a bad key. Fixed.
- [x] Test cleaning in `tests/` by loading a saved response from `tests/fixtures/` with `json.load`, not from the database creation script. Done in `tests/test_clean_stats.py` for Soto, Skenes, Miller, and teams; every known value in CLAUDE.md passes.
- [ ] Passing a player ID into a cleaning function fails; the cleaner expects the response from `fetch_hitter_stats`, so fetch first and then clean.

## Insert (`insert.py`)

- [x] `conn.commit` without parentheses never ran. The insert functions no longer commit; the pipeline script does (see the commit decision below).
- [x] Verify rows persist when read through a fresh connection. Tested with a temp file; a second test confirms the insert functions alone do not commit.
- [x] `insert_player_data` is still positional (no column list), so the dictionary's key order must match the table. Tested: `clean_player_info`'s key order equals the `players` columns, and values land in the right columns.
- [ ] Decide whether to switch `insert_player_data` to the column-list form that `insert_data` uses.
- [x] Stat tables: `stat_id` is the first column and the dictionary lacks it. `insert_data` builds a column list from the dictionary's keys, so the counts match.
- [ ] Validate `table_name` against an allowed set (identifiers cannot be parameters).
- [ ] Duplicate `players` row. Decide fail, skip, or replace (`INSERT OR REPLACE` vs `ON CONFLICT`).
- [ ] Empty list: the current `insert_data` loops over the list, so an empty list does nothing and raises nothing (tested). Confirm that is what you want.
- [ ] Decide input shape (single dictionary vs list) and name (generic vs `insert_player_info`).
- [x] Decided: the pipeline script owns the connection and the commits, and the insert functions do not commit. It commits after the schema, after the teams load, and once per player after the info row and both stat inserts.
- [ ] Closing: the script closes the connection only at the end. A `with` block on a connection commits or rolls back but does not close it.
- [x] Decided the boundary: one commit per player. Simulated a failure on player 2 (stat row pointing at a missing team): player 1 was complete, and player 2 and its rows were absent.
- [ ] `PRAGMA foreign_keys = ON` is per connection; set it on every connection that inserts.
- [x] Player with no stat rows (Arias): the `players` row loads and both stat tables have nothing for him, with no error. Still use `LEFT JOIN` when listing every player.
- [x] Insert order: `teams`, then `players`, then stat rows. The 10-player run has no stat row without a parent player or team.
- [x] Dates stored as ISO text; Arias `debut_date` is a real NULL.
- [ ] Check for the `sqlite3` date adapter deprecation warning on this Python version, and decide whether `clean` or `insert` converts dates.

- [x] First generic `insert_data` ran `executemany` inside a loop over the same list. On `teams` it failed on the repeat and left 0 rows after reopening the file; on a stat-shaped table it turned 10 rows into 100 with no error. Fixed.
- [x] After a stat insert, the table's row count equals `len(data_list)` (tested with Soto's 10 rows). Adding the same check inside the pipeline is still open.
- [x] The parameter is now named `data_list`.
- [ ] Zero vs missing: Walker's pre-2000 rows have `catcher_interference` of 0 in all 11 rows. A NULL check cannot tell zero events from a stat the API does not track for that era. Check whether any hitter row anywhere is nonzero.
- [ ] Tiny samples: Ohtani's 2020 pitching row is an ERA of 37.8 over 5 outs. Projection weighting has to account for small samples.

- [ ] Run a forced-failure test on the real pipeline (for example a wrong table name for one player's stats), reopen the file, and confirm that player's `players` row is absent. Blocked: `table_creation.py` runs everything at import and calls the live API, so a test cannot import it. It needs its loop moved into a function that takes a connection and the fetched data. (`test_insert_functions_do_not_commit` already proves the insert functions do not commit.)
- [ ] If the loop ever catches errors and continues, call `connection.rollback()` first. Simulated without it: the next player's commit saved the failed player's `players` row with no stat rows. With it, the failed player was left out cleanly.
- [x] The `Loading player` print now runs at the start of each loop iteration, so a crash names the player.
- [ ] Decide stop vs skip-and-log for a failing player.
- [ ] Wrap the load loop in `try`/`finally` so `connection.close()` runs after a crash.
- [ ] If the load ever stops deleting the `.db` first (incremental loads), players already loaded will hit the primary key on a rerun. Decide skip or replace.

## Database and schema

- [x] Schema builds all four tables (verified).
- [x] Re-running the creation script raised `table players already exists` (observed). Decided: delete the `.db` at the start of each run.
- [ ] Decide whether table creation is a function with an `if __name__ == "__main__":` guard that takes a connection, and whether the pipeline should ever create tables.
- [x] `position` column on `hitting_season_stats` and `pitching_season_stats` had no source. Decided: removed.
- [x] Stat tables had no uniqueness rule, so duplicate rows inserted silently. Decided: `UNIQUE (player_id, season, team_id)` on both tables, with all three columns `NOT NULL` so NULLs cannot slip past it. A repeated insert now raises `IntegrityError`; a traded season with two teams is still allowed. Tested in `test_insert.py`.
- [ ] Decide what the pipeline does when a rerun hits the uniqueness rule: stop, skip, or upsert.
- [x] `teams` is filled from a saved `data/teams.json` (30 teams) before any player loads.
- [x] Stat rows referencing teams missing from `teams`: checked for 10 players (Walker 1989 to 2005, Ramírez, Kershaw, Cole, Ohtani, Miller). None missing. Re-check as more players load.
- [x] One `team_id` carries one franchise through renames and moves: Ramírez's 14 rows all use 114, and Walker's 1989 to 1994 Expos rows use 120. `teams` stores the current name only (114 is Cleveland Guardians, 120 is Washington Nationals, 133 is Athletics).
- [ ] Decide whether as-of-season team names are ever needed. The stat tables store only `team_id`, so they would have to come from somewhere else.
- [ ] `sqlite3.connect` when the `data/` folder does not exist (it is not in git, so check on the laptop).
- [ ] Database path: a relative path depends on the folder you run from, and the laptop's folder name differs. Consider `pathlib` from `__file__` and define it once.
- [ ] Schema changes need a rebuild on both devices.
- [x] Spelling: `plate_apperances` fixed to `plate_appearances` in `schema.sql`.
- [x] Pitching table: `innings_pitched float` replaced with `outs int`.
- [ ] Decide whether to keep the name `outs` or rename it to something more specific (for example `outs_recorded`). Rebuild on both devices after any schema change.
- [x] `outs` is present in every pitching split checked and matches the `inningsPitched` notation, including `.1` and `.2` splits. Verified for Skenes (3 splits) and Miller (6 splits, including the combined row).
- [x] Summing a traded pitcher's team rows matches the combined row. Miller 2025: outs, games, batters faced, strikeouts, saves, and holds all match.
- [ ] Decide whether to keep the stored per-nine and per-inning rate columns or compute them from `outs`.
- [ ] SQLite integer division: compare `SELECT 625 / 3` with `SELECT 625 / 3.0` and always divide by `3.0` in queries. Decide `/` vs `//` in Python.
- [ ] Optional: a SQLite view that shows `outs / 3.0` as innings for baseball readers.
- [ ] The creation script is being used as a testing ground. Keep it to creating the database and put tests in `tests/`.
- [x] Replacing the `.db`: the script checks for the file and deletes it before `sqlite3.connect`, so the first run (no file) works.
- [ ] On Windows, deleting a `.db` that is open in DB Browser raises `PermissionError`; close it first.
- [ ] Deleting erases the loaded players. Consider renaming the old file to a backup and keeping only the latest.
- [ ] Guard against accidental runs with `if __name__ == "__main__":`, a confirmation, or a flag.
- [ ] Test the replace step on a copy of the `.db`: file exists, file missing, file open in DB Browser.

## Pipeline (`table_creation.py`)

There is no separate `pipeline.py`; `table_creation.py` builds the database and runs the load loop.

- [x] The script runs `executescript(schema)` every time. A second run no longer fails because the `.db` is deleted first. If the pipeline is ever split from table creation, decide that it assumes tables exist.
- [x] Loop body now stores each stage in a variable.
- [ ] Connection is closed only after the loop; guarantee the close with `try`/`finally`.
- [ ] Second run: the first existing player hits the duplicate behavior.
- [ ] Decide failure behavior mid-loop: stop, skip and log, or retry.
- [ ] Bad-ID check before `clean`: validate the info response (`people` missing or empty). Decide raise a custom exception vs return a boolean, and which file owns it.
- [ ] Decide skip, log, or stop on a bad ID.
- [x] Each player's pass fetches info and both stat groups, skips empty results, and commits once at the end.
- [x] The test player list comment matches the IDs (10 names, 10 IDs, same order).

## Teams refresh (`team_refresh.py`)

- [ ] It deletes `data/teams.json` before making the request, so a failed request leaves no file. Make the request first, then replace the file.
- [ ] No validity check before writing: an error response would overwrite the good file. Decide what a valid response must contain (a `teams` list with 30 entries).
- [ ] No `if __name__ == "__main__":` guard, so importing it makes a live call and overwrites `data/teams.json`. Tests must never import it.
- [ ] Relative path: run it from the project root as `python -m src.data_pipeline.team_refresh`.
- [ ] Decide whether a refresh should keep a dated backup of the previous file.

## Git and tooling

- [x] Teams load failures tested: a missing file raises `FileNotFoundError`, an error response raises `KeyError: 'teams'`, and a second teams insert raises `IntegrityError`.
- [x] Foreign keys tested: a stat row pointing at team 9999 raises `IntegrityError` with the pragma on and is accepted with it off.
- [x] Root `.gitignore` tested in a throwaway repo. Tracked: `data/teams.json`, `tests/fixtures/`, `src/`, `database/`, `docs/`. Ignored: `data/player_projection.db`, other JSON in `data/`, `scratch/`, `venv/`, `.env`, `*.log`.
- [ ] `git check-ignore -v` also prints `!` exception rules (it printed the `teams.json` exception), so it cannot tell tracked from ignored. Use `git ls-files <path>` or `git status` instead.
- [x] Add `/CLAUDE.md` to the root `.gitignore` (the `.gitignore` inside `venv/` is a different, auto-generated file). It will not sync to the laptop, so copy it by hand.
- [x] After the first Claude Code session, run `git status` for a new `.claude/` folder or `CLAUDE.local.md`. Checked: neither appeared. `.pytest_cache/` ignores itself.
- [x] Copied the saved Soto hitting, Skenes pitching, Miller pitching, and teams responses into `tests/fixtures/` as `soto_hitting.json`, `skenes_pitching.json`, `miller_pitching.json`, `teams.json`. Not committed yet.
- [x] Installed `pytest` 9.1.1, added it to `requirements.txt` (now UTF-8 instead of UTF-16), and run tests with `python -m pytest` from the project root. 56 tests pass.
- [ ] Tests must not call the live API or use the real `.db`. Review every test before committing it.

## Logging (deferred)

Goal: when `_create_date` or `_convert_height` turn bad data into `None`, leave a record so the affected rows can be found and corrected later. Reading: https://docs.python.org/3/howto/logging.html (Basic Tutorial, Logging to a file).

- [ ] Decide where the player ID comes from. The helpers do not know it, so pass it in or log from `clean_player_info`.
- [ ] Decide what each entry contains: player ID, field name, raw value from the API, and what went wrong.
- [ ] Decide severity. A missing debut date (expected for prospects) vs a garbled date string (bad data).
- [x] Bare `except:` clauses replaced with specific exception types.
- [ ] Decide where logging is configured once (the entry point, currently `table_creation.py`).
- [ ] Decide where the log file lives and whether it goes in `.gitignore`.
- [ ] Log skipped players and bad IDs with their ID.
- [ ] Test: each case (missing key, `None` value, garbled string, bad height) produces the entry you decided on.
- [ ] Apply the same logging to stats cleaning helpers.

## Network, cache, and scale

- [ ] No internet: `requests` raises `ConnectionError` or `Timeout`. Fallback to cache is postponed.
- [x] Non-200 HTTP responses: first one observed is a 404 from the info endpoint for a fake ID. The body is still JSON, so `.json()` works and returns the error dict.
- [ ] Decide whether to call `raise_for_status()` in fetch. It would turn a fake ID on the info endpoint into `HTTPError: 404` at fetch time (and change `test_player_info_bad_id_raises_key_error`), but would not catch a fake ID on the stats endpoints (they return 200). It would also catch server errors (500) and rate limiting (429), which may return HTML instead of JSON.
- [ ] `requests.get` has no timeout by default, so a hung API call waits forever. Consider `timeout=10`.
- [ ] Cache the raw response before cleaning, so the offline path runs `clean` and `insert` on the same shape.
- [ ] Decide where cache-writing lives (the pipeline script), one file per player and data type vs one big file, and whether the cache is git-ignored or synced between devices.
- [ ] Should a "not found" response ever be saved to the cache?
- [ ] League-wide load: roughly 1,200 players, several calls each. My estimate is 10 to 30 minutes sequential; measure one call and one insert with `time.perf_counter()`.
- [ ] Check for bulk endpoints, rate limits, and the API's terms of use before a full run.
- [ ] Make runs resumable (record which players are already saved).
- [ ] Batch inserts only if commits ever become the bottleneck; the network dominates run time.

## Deferred decisions

- [ ] `games_missed` and an `injuries` table (needs a separate injury source; add with `ALTER TABLE` when a feature needs it).
- [ ] Rosters (40-man, top-30 prospects): decide which feature needs them; consider `current_team` on `players` instead.
- [ ] Search function: build after the pipeline works.
- [ ] Minor league stats are not supported (prospects have no rows).
