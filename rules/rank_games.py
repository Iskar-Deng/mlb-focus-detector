import json
import configparser
from datetime import datetime
import pytz

from live.fetch_live import get_current_game_states
from rules.cal_focus import analyze_state_focus
from rules.teams import TEAM_ABBR

def load_config(config_path="config/user.ini"):
    config = configparser.ConfigParser()
    config.read(config_path)
    prefs = config["preferences"]
    favorite_team = prefs.get("favorite_team").strip().lower()
    follow_teams = json.loads(prefs.get("follow_teams", "[]"))
    follow_teams = [t.strip().lower() for t in follow_teams]
    timezone = prefs.get("timezone", "UTC")
    return favorite_team, follow_teams, timezone

def team_priority(team_name, favorite_full, follows_full):
    team_name = team_name.lower()
    if team_name == favorite_full:
        return 0
    elif team_name in follows_full:
        return 1
    else:
        return 2

def rank_games(we_dict, rd_dict, favorite, follows, timezone):
    favorite = favorite.lower()
    follows = [t.lower() for t in follows]
    tz = pytz.timezone(timezone)

    game_states = get_current_game_states()
    ranked = {
        "in_progress": [],
        "delayed": [],
        "not_started": [],
        "final": []
    }

    for group in ranked.keys():
        for game in game_states.get(group, []):
            priority = min(
                team_priority(game["home_team"], favorite, follows),
                team_priority(game["away_team"], favorite, follows)
            )
            game["priority"] = priority
            game["home_abbr"] = TEAM_ABBR.get(game["home_team"], "???")
            game["away_abbr"] = TEAM_ABBR.get(game["away_team"], "???")

            if group == "in_progress":
                score_diff = (
                    game["home_runs"] - game["away_runs"]
                    if game["batting_home"] else
                    game["away_runs"] - game["home_runs"]
                )
                try:
                    raw_half = game["half"].strip().lower()
                    normalized_half = "Top" if raw_half.startswith("top") else "Bot"

                    focus_result = analyze_state_focus(
                        inning=game["inning"],
                        half=normalized_half.lower(),
                        score_diff=score_diff,
                        state=game["state"],
                        batting_home=game["batting_home"],
                        we_dict=we_dict,
                        rd_dict=rd_dict
                    )
                    game["focus_score_norm"] = focus_result["focus_score_norm"]
                    game["half"] = normalized_half
                    print(f"        Focus = {focus_result['focus_score_norm']}")
                except Exception as e:
                    print(f"[ERROR] Failed to compute focus for Game {game['game_id']}: {e}")
                    game["focus_score_norm"] = -1

            try:
                if group in ["not_started", "delayed", "final"]:
                    raw_time = game.get("game_time") or game.get("game_datetime")
                    if raw_time:
                        dt_utc = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                        game["_sort_time"] = dt_utc.astimezone(tz)
                    else:
                        game["_sort_time"] = datetime.max
                else:
                    game["_sort_time"] = datetime.min
            except:
                game["_sort_time"] = datetime.max

            if group in ["not_started", "delayed"]:
                status = game.get("status", "")
                if status == "Delayed":
                    game["game_time"] = "Delayed"
                elif status in ["Pre-Game", "Warmup"]:
                    game["game_time"] = "Pre-Game"
                else:
                    try:
                        dt_local = game["_sort_time"]
                        game["game_time"] = dt_local.strftime("%-I:%M %p") + f" {tz.zone.split('/')[-1]}"
                    except:
                        game["game_time"] = "Scheduled"

            ranked[group].append(game)

    in_progress_sorted = sorted(
        ranked["in_progress"], key=lambda g: (g["priority"], -g.get("focus_score_norm", 0))
    )
    
    combined_upcoming = ranked["delayed"] + ranked["not_started"]
    combined_upcoming_sorted = sorted(
        combined_upcoming, key=lambda g: (g["priority"], g["_sort_time"])
    )

    final_sorted = sorted(
        ranked["final"], key=lambda g: (g["priority"], g["_sort_time"])
    )

    return in_progress_sorted + combined_upcoming_sorted + final_sorted
