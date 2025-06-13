from flask import Flask, request, jsonify
from flask_cors import CORS
import json

from rules.rank_games import rank_games
from rules import rank_games as rg_module

app = Flask(__name__)
CORS(app)

# Load WE and RD data once at startup
with open("data/we.json") as f:
    we_dict = json.load(f)
with open("data/rd_2024.json") as f:
    rd_dict = json.load(f)

@app.route("/games", methods=["POST"])
def get_games():
    try:
        data = request.get_json()
        print("Received POST /games with data:", data)

        favorite = data.get("favorite", "").strip()
        follows = data.get("follows", [])
        timezone = data.get("timezone", "UTC")

        games = rank_games(we_dict, rd_dict, favorite, follows, timezone)
        return jsonify(games)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=8000, debug=True)
