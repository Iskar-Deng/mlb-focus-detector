import json
import configparser
from pathlib import Path
from datetime import datetime
import pytz

from live.fetch_live import get_current_game_states
from rules.cal_focus import analyze_state_focus

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

def full_sort_key(game, with_focus=False):
    base = (game["priority"],)
    if with_focus:
        return base + (-game.get("focus_score_norm", 0), game["away_team"], game["home_team"])
    else:
        return base + (game["away_team"], game["home_team"])

def rank_games(we_dict, rd_dict, config_path="config/user.ini"):
    game_states = get_current_game_states()
    favorite, follows, _ = load_config(config_path)

    ranked = {"in_progress": [], "not_started": [], "final": []}

    for group in ["in_progress", "not_started", "final"]:
        for game in game_states[group]:
            priority = min(
                team_priority(game["home_team"], favorite, follows),
                team_priority(game["away_team"], favorite, follows)
            )
            game["priority"] = priority

            if group == "in_progress":
                score_diff = (
                    game["home_runs"] - game["away_runs"]
                    if game["batting_home"] else
                    game["away_runs"] - game["home_runs"]
                )
                try:
                    focus_result = analyze_state_focus(
                        inning=game["inning"],
                        half=game["half"].lower(),
                        score_diff=score_diff,
                        state=game["state"],
                        batting_home=game["batting_home"],
                        we_dict=we_dict,
                        rd_dict=rd_dict
                    )
                    game["focus_score_norm"] = focus_result["focus_score_norm"]
                except Exception:
                    game["focus_score_norm"] = -1  # fallback

            ranked[group].append(game)

    in_progress_sorted = sorted(ranked["in_progress"], key=lambda g: full_sort_key(g, with_focus=True))
    not_started_sorted = sorted(ranked["not_started"], key=full_sort_key)
    final_sorted = sorted(ranked["final"], key=full_sort_key)

    return in_progress_sorted + not_started_sorted + final_sorted

if __name__ == "__main__":
    with open("data/we.json") as f:
        we_dict = json.load(f)
    with open("data/rd_2024.json") as f:
        rd_dict = json.load(f)

    favorite, follows, timezone_str = load_config()
    tz = pytz.timezone(timezone_str)

    ranked_games = rank_games(we_dict, rd_dict)

    for game in ranked_games:
        home = game['home_team']
        away = game['away_team']
        home_name = home.strip().lower()
        away_name = away.strip().lower()

        # 标记 favorite / follow
        if favorite in [home_name, away_name]:
            tag = "★"
        elif any(t in [home_name, away_name] for t in follows):
            tag = "•"
        else:
            tag = " "

        # 状态字符串
        status = game['status']
        if status == "In Progress":
            inning = game.get("inning", "?")
            half = game.get("half", "").capitalize()
            state_str = f"{half} {inning}"
        elif status in ["Final", "Game Over"]:
            state_str = "Final"
        else:
            raw_time = game.get("game_time", "")
            try:
                dt_utc = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                dt_local = dt_utc.astimezone(tz)
                state_str = dt_local.strftime("%-I:%M %p").lstrip("0") + f" {tz.zone.split('/')[-1]}"
            except Exception:
                state_str = "Scheduled"

        # 比分输出
        away_score = game.get('away_runs', '')
        home_score = game.get('home_runs', '')
        print(f"{state_str:<10} {tag} {away} {away_score} - {home} {home_score}", end="")

        if status == "In Progress":
            print(f" | Focus: {game.get('focus_score_norm', 'N/A')}")
        else:
            print("")
