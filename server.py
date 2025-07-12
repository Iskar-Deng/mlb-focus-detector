from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

from rules.rank_games import rank_games
from rules import rank_games as rg_module

app = Flask(__name__)
CORS(app)

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

@app.route("/ping")
def ping():
    return "pong"

@app.route("/status-log", methods=["GET"])
def get_status_log():
    try:
        log_path = "logs/status_seen.log"
        if not os.path.exists(log_path):
            return jsonify({"log": []})
        with open(log_path, "r") as f:
            lines = f.readlines()
        return jsonify({"log": [line.strip() for line in lines]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
