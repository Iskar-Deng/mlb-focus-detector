import csv
from collections import defaultdict
import json

raw_data = defaultdict(dict)

with open('data/probs.txt', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        team = row[0].strip('"')  # 'H' or 'V'
        inning = int(row[1])
        if inning > 15:
            continue

        outs = int(row[2])
        base_state = int(row[3])
        score_diff = int(row[4])
        total = int(row[5])
        wins = int(row[6])

        if outs != 0 or base_state != 1:
            continue

        half = 'top' if team == 'V' else 'bot'
        inning_str = f'{inning}_{half}'

        # 跳过不可能的局面
        if inning == 1 and half == 'top' and score_diff < 0:
            continue
        if inning >= 9 and half == 'bot' and score_diff > 0:
            continue
        if inning >= 10 and half == 'top' and score_diff < 0:
            continue

        if -9 <= score_diff <= 9:
            # +0.01 平滑
            win_ratio = (wins + 0.01) / (total + 0.02)
            raw_data[inning_str][score_diff] = win_ratio

# 补全缺失分差（-9 到 +9）: 使用最近的可用值
final_data = {}
all_diffs = list(range(-9, 10))

for inning in raw_data:
    inning_data = {}
    available = raw_data[inning]

    for diff in all_diffs:
        # 检查该分差是否为该 inning 合法
        i_num, half = inning.split('_')
        i_num = int(i_num)
        if i_num == 1 and half == 'top' and diff < 0:
            continue
        if i_num >= 9 and half == 'bot' and diff > 0:
            continue
        if i_num >= 10 and half == 'top' and diff < 0:
            continue

        if diff in available:
            inning_data[diff] = available[diff]
        else:
            # 最近邻补全
            nearest_val = None
            for offset in range(1, 10):
                if diff - offset in available:
                    nearest_val = available[diff - offset]
                    break
                elif diff + offset in available:
                    nearest_val = available[diff + offset]
                    break
            if nearest_val is None:
                nearest_val = 0.5  # fallback
            inning_data[diff] = nearest_val

    final_data[inning] = inning_data

# 保存为 JSON 文件
with open('data/we.json', 'w') as f:
    json.dump(final_data, f, indent=2)

# 示例打印
for inning in sorted(final_data.keys()):
    print(f"{inning}:")
    for diff in sorted(final_data[inning].keys()):
        print(f"  {diff:+}: {final_data[inning][diff]:.3f}")
