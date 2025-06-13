import pandas as pd
from collections import defaultdict, Counter
import json

df = pd.read_csv("utils/retro/pbp_2024.csv", low_memory=False)
df["HALF_INNING"] = df["GAME_ID"] + "_" + df["INN_CT"].astype(str) + "_" + df["BAT_HOME_ID"].astype(str)

def runner_state(row):
    return "".join([
        '1' if pd.notna(row[f'BASE{i}_RUN_ID']) and str(row[f'BASE{i}_RUN_ID']).strip() != '' else '0'
        for i in [1, 2, 3]
    ])
df["RUNNER_STATE"] = df.apply(runner_state, axis=1)

df["STATE"] = df["OUTS_CT"].astype(str) + "_outs__" + df["RUNNER_STATE"]

df["SCORE_BEFORE"] = df.apply(
    lambda row: row["HOME_SCORE_CT"] if row["BAT_HOME_ID"] == 1 else row["AWAY_SCORE_CT"],
    axis=1
)

final_scores = df.groupby("HALF_INNING").apply(
    lambda group: group.iloc[-1]["HOME_SCORE_CT"] if group.iloc[-1]["BAT_HOME_ID"] == 1
    else group.iloc[-1]["AWAY_SCORE_CT"]
).to_dict()

df["FUTURE_RUNS"] = df.apply(
    lambda row: final_scores.get(row["HALF_INNING"], 0) - row["SCORE_BEFORE"], axis=1
)

run_distributions = defaultdict(Counter)
for _, row in df.iterrows():
    state = row["STATE"]
    runs = int(row["FUTURE_RUNS"])
    run_distributions[state][runs] += 1

SMOOTH = 0.01
MAX_SCORE = 7

run_probs = {}
for state, counter in run_distributions.items():
    merged = Counter()
    for k, v in counter.items():
        score = k if k < MAX_SCORE else MAX_SCORE
        merged[score] += v

    smoothed = {str(k): merged.get(k, 0) + SMOOTH for k in range(0, MAX_SCORE + 1)}
    total = sum(smoothed.values())
    run_probs[state] = {k: v / total for k, v in smoothed.items()}

output_path = "data/rd_2024.json"
with open(output_path, "w") as f:
    json.dump(run_probs, f, indent=2)

print(f"Run distribution saved to {output_path}")
