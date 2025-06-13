# live/fetch_live.py

from typing import List, Dict
import statsapi
from datetime import datetime

def get_current_game_states() -> Dict[str, List[Dict]]:
    today_str = datetime.today().strftime('%Y-%m-%d')
    games = statsapi.schedule(start_date=today_str, end_date=today_str)

    result = {
        "not_started": [],
        "in_progress": [],
        "final": []
    }

    for g in games:
        status = g['status']
        game_pk = g['game_id']
        home = g.get('home_abbrev') or g['home_name']
        away = g.get('away_abbrev') or g['away_name']

        if status == 'In Progress':
            linescore = statsapi.linescore(game_pk)
            inning = int(linescore['currentInning'])
            half = linescore['inningHalf']
            batting_home = (half == 'bot')

            batting_team = home if batting_home else away
            fielding_team = away if batting_home else home

            outs = linescore['outs']
            base_state = "".join(
                '1' if linescore['onbase'].get(base, False) else '0'
                for base in ['first', 'second', 'third']
            )

            state = f"{outs}_outs__{base_state}"
            home_runs = linescore['r']['home']
            away_runs = linescore['r']['away']

            boxscore = statsapi.boxscore(game_pk)
            pitcher = boxscore.get("teamInfo", {}).get("pitching", {}).get("players", {})
            batter = boxscore.get("teamInfo", {}).get("batting", {}).get("players", {})

            current_pitcher = statsapi.get("game", {"gamePk": game_pk})["liveData"]["boxscore"]["pitchers"]
            current_batter = statsapi.get("game", {"gamePk": game_pk})["liveData"]["boxscore"]["batter"]

            try:
                pitcher_name = statsapi.player_stat_data(current_pitcher)["playerInfo"]["fullName"]
            except:
                pitcher_name = "Pitcher"

            try:
                batter_name = statsapi.player_stat_data(current_batter)["playerInfo"]["fullName"]
            except:
                batter_name = "Batter"

            result['in_progress'].append({
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
                "state": state,
                "pitcher": pitcher_name,
                "batter": batter_name,
            })

        elif status in ['Final', 'Game Over']:
            result['final'].append({
                "game_id": game_pk,
                "status": status,
                "home_team": home,
                "away_team": away,
                "home_runs": g['home_score'],
                "away_runs": g['away_score']
            })

        elif status in ['Scheduled', 'Pre-Game', 'Warmup']:
            result['not_started'].append({
                "game_id": game_pk,
                "status": status,
                "home_team": home,
                "away_team": away,
                "game_time": g.get('game_datetime', g.get('game_time', 'N/A'))
            })

    return result
