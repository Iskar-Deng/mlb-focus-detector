from typing import List, Dict
import statsapi
import pytz
import os
from datetime import datetime

STATUS_LOG_FILE = "logs/status_seen.log"

def log_status_to_file(status: str):
    status = status.strip()
    if not status:
        return

    today_str = datetime.today().strftime("%Y-%m-%d")
    log_line = f"{today_str} | {status}"

    if not os.path.exists(STATUS_LOG_FILE):
        with open(STATUS_LOG_FILE, "w") as f:
            f.write("")

    with open(STATUS_LOG_FILE, "r") as f:
        seen_lines = set(line.strip() for line in f.readlines())

    if log_line not in seen_lines:
        with open(STATUS_LOG_FILE, "a") as f:
            f.write(log_line + "\n")
        print(f"[LOG] New game status logged: {log_line}")
        
def get_current_game_states() -> Dict[str, List[Dict]]:
    pacific = pytz.timezone("US/Pacific")
    today_pt = datetime.now(pacific).strftime('%Y-%m-%d')
    print(f"[INFO] Fetching MLB games for {today_pt}")
    games = statsapi.schedule(start_date=today_pt, end_date=today_pt)

    result = {
        "not_started": [],
        "in_progress": [],
        "final": []
    }

    for g in games:
        status = g['status']
        log_status_to_file(status)
        game_pk = g['game_id']
        home = g.get('home_abbrev') or g['home_name']
        away = g.get('away_abbrev') or g['away_name']

        print(f"[INFO] Processing game: {away} @ {home} — status: {status}")

        if status == 'In Progress':
            try:
                game_data = statsapi.get("game", {"gamePk": game_pk})
                linescore = game_data["liveData"]["linescore"]

                inning = int(linescore["currentInning"])
                half = linescore["inningHalf"][:3]
                batting_home = (half.lower() == "bot")

                batting_team = home if batting_home else away
                fielding_team = away if batting_home else home

                outs = linescore.get("outs", 0)
                offense = linescore.get("offense", {})
                base_state = "".join([
                    "1" if base in offense else "0"
                    for base in ["first", "second", "third"]
                ])

                state = f"{outs}_outs__{base_state}"
                home_runs = linescore["teams"]["home"]["runs"]
                away_runs = linescore["teams"]["away"]["runs"]

                print(f"[DEBUG] Game {game_pk}: inning={inning}, half={half}, outs={outs}, bases={base_state}, state={state}, score={away_runs}-{home_runs}")

                result["in_progress"].append({
                    "game_id": game_pk,
                    "status": status,
                    "inning": inning,
                    "half": half,
                    "batting_home": batting_home,
                    "batting_team": batting_team,
                    "fielding_team": fielding_team,
                    "home_team": home,
                    "away_team": away,
                    "home_runs": home_runs,
                    "away_runs": away_runs,
                    "state": state
                })
            except Exception as e:
                print(f"[ERROR] Failed to parse in-progress game {game_pk}: {e}")

        elif status in ['Final', 'Game Over']:
            result['final'].append({
                "game_id": game_pk,
                "status": status,
                "home_team": home,
                "away_team": away,
                "home_runs": g['home_score'],
                "away_runs": g['away_score']
            })

        # elif status in ['Scheduled', 'Pre-Game', 'Warmup']:
        else:
            raw_time = g.get('game_datetime') or g.get('game_time', 'N/A')
            result['not_started'].append({
                "game_id": game_pk,
                "status": status,
                "home_team": home,
                "away_team": away,
                "game_time": raw_time
            })

    print(f"[INFO] Done. {len(result['in_progress'])} in-progress, {len(result['final'])} final, {len(result['not_started'])} not started.")
    return result
