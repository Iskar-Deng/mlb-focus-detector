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


def full_sort_key(game, with_focus=False):
    base = (game["priority"],)
    if with_focus:
        return base + (-game.get("focus_score_norm", 0), game["away_team"], game["home_team"])
    else:
        return base + (game["away_team"], game["home_team"])


def rank_games(we_dict, rd_dict, favorite, follows, timezone):
    """
    Return sorted list of games by:
    - Group order: In Progress > Not Started > Final
    - Team priority: favorite > follow > others
    - Focus score descending (for in-progress only)
    """
    favorite = favorite.lower()
    follows = [t.lower() for t in follows]
    tz = pytz.timezone(timezone)

    game_states = get_current_game_states()
    ranked = {"in_progress": [], "not_started": [], "final": []}

    for group in ["in_progress", "not_started", "final"]:
        for game in game_states[group]:
            # Tag priority
            priority = min(
                team_priority(game["home_team"], favorite, follows),
                team_priority(game["away_team"], favorite, follows)
            )
            game["priority"] = priority

            # Add team abbreviations
            game["home_abbr"] = TEAM_ABBR.get(game["home_team"], "???")
            game["away_abbr"] = TEAM_ABBR.get(game["away_team"], "???")

            # Tag: favorite = ★, follow = •
            home_name = game["home_team"].strip().lower()
            away_name = game["away_team"].strip().lower()
            if favorite in [home_name, away_name]:
                game["tag"] = "★"
            elif any(t in [home_name, away_name] for t in follows):
                game["tag"] = "•"
            else:
                game["tag"] = ""

            # Calculate focus score
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
                    game["focus_score_norm"] = -1

            # Format game_time for not_started
            if group == "not_started":
                raw_time = game.get("game_time", "")
                try:
                    dt_utc = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                    dt_local = dt_utc.astimezone(tz)
                    game["game_time"] = dt_local.strftime("%-I:%M %p") + f" {tz.zone.split('/')[-1]}"
                except Exception:
                    game["game_time"] = "Scheduled"

            ranked[group].append(game)

    # Apply sorting
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

    games = rank_games(we_dict, rd_dict, favorite, follows, timezone_str)

    for game in games:
        tag = game.get("tag", "")
        away = game["away_team"]
        home = game["home_team"]
        away_score = game.get("away_runs", "")
        home_score = game.get("home_runs", "")
        status = game["status"]

        if status == "In Progress":
            inning = game.get("inning", "?")
            half = game.get("half", "").capitalize()
            state_str = f"{half} {inning}"
        elif status in ["Final", "Game Over"]:
            state_str = "Final"
        else:
            state_str = game.get("game_time", "Scheduled")

        print(f"{state_str:<10} {tag} {away} {away_score} - {home} {home_score}", end="")
        if status == "In Progress":
            print(f" | Focus: {game.get('focus_score_norm', 'N/A')}")
        else:
            print("")
