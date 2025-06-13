from fetch_live import get_current_game_states
import json

snaps = get_current_game_states()
print(json.dumps(snaps, indent=2))
