# rules/cal_focus.py

import json
from scipy.stats import norm

def phi_integral_area(we_from, we_to, sigma=0.15):
    cdf = norm(loc=0.5, scale=sigma).cdf
    return abs(cdf(we_to) - cdf(we_from))

def analyze_state_focus(
    inning: int,
    half: str,  # "top" or "bot"
    score_diff: int,  # batting team score - opponent score
    state: str,  # like "1_outs__010"
    batting_home: bool,
    we_dict: dict,
    rd_dict: dict,
    sigma: float = 0.15,
    baseline_focus_score: float = 0.17143  # default = opening state
) -> dict:
    """
    Returns:
        {
            "base_win_home": float,
            "score_path": List[Dict[run: int, prob: float, we_home: float, area: float]],
            "focus_score": float,
            "focus_score_norm": int
        }
    """

    if state.startswith("3_outs"):
        print("[DEBUG] 3 outs detected, shifting to next half-inning...")
        state = "0_outs__000"
        if half == "top":
            half = "bot"
        else:
            half = "top"
            inning += 1

    key = f"{inning}_{half}"
    if key not in we_dict or state not in rd_dict:
        raise ValueError("Missing WE or RD data for given state.")

    # Current win expectancy (home perspective)
    base_win = we_dict[key].get(str(score_diff))
    if base_win is None:
        for offset in range(1, 10):
            for diff_try in [score_diff - offset, score_diff + offset]:
                if str(diff_try) in we_dict[key]:
                    base_win = we_dict[key][str(diff_try)]
                    break
            if base_win is not None:
                break
    if base_win is None:
        raise ValueError("Could not find or interpolate WE for current state.")

    base_win_home = base_win if batting_home else 1 - base_win

    # Projected half-inning outcomes
    next_half = "bot" if half == "top" else "top"
    next_inning = inning + 1 if next_half == "top" else inning
    next_key = f"{next_inning}_{next_half}"

    # Extended inning WE adjustment
    if next_key not in we_dict and next_inning >= 10:
        if next_half == "top":
            ref_table = we_dict.get("9_top")
            if ref_table:
                next_we_table = {
                    str(int(k) + 1): v for k, v in ref_table.items()
                }
            else:
                next_we_table = {}
        elif next_half == "bot":
            next_we_table = we_dict.get("9_bot", {})
    else:
        next_we_table = we_dict.get(next_key, {})

    focus_score = 0.0
    score_path = []

    for run_str, prob in sorted(rd_dict[state].items(), key=lambda x: int(x[0])):
        runs = int(run_str)
        new_diff = score_diff + runs

        if batting_home and half == "bot" and inning >= 9:
            if new_diff < 0:
                we_home = 0.0
            elif new_diff > 0:
                we_home = 1.0
            else:
                next_diff = -new_diff
                we_after = next_we_table.get(str(next_diff))
                if we_after is None:
                    for offset in range(1, 10):
                        for try_diff in [next_diff - offset, next_diff + offset]:
                            if str(try_diff) in next_we_table:
                                we_after = next_we_table[str(try_diff)]
                                break
                        if we_after is not None:
                            break
                if we_after is None:
                    continue
                we_home = we_after if not batting_home else 1 - we_after
        else:
            next_diff = -new_diff
            we_after = next_we_table.get(str(next_diff))
            if we_after is None:
                for offset in range(1, 10):
                    for try_diff in [next_diff - offset, next_diff + offset]:
                        if str(try_diff) in next_we_table:
                            we_after = next_we_table[str(try_diff)]
                            break
                    if we_after is not None:
                        break
            if we_after is None:
                continue
            we_home = we_after if not batting_home else 1 - we_after

        area = phi_integral_area(base_win_home, we_home, sigma=sigma)
        focus_score += prob * area
        score_path.append({
            "runs": runs,
            "prob": prob,
            "we_home": we_home,
            "area": area
        })

    # Apply leverage multiplier based on inning
    if inning <= 6:
        leverage_multiplier = 1.0
    elif inning == 7:
        leverage_multiplier = 1.2
    elif inning == 8:
        leverage_multiplier = 1.5
    else:  # 9 or later
        leverage_multiplier = 2.0

    half_score = 1
    adjusted_focus = focus_score * leverage_multiplier * half_score

    # Normalize score
    focus_score_norm = int(round(100 * adjusted_focus / baseline_focus_score)) if baseline_focus_score > 0 else 0
    focus_score_norm = max(focus_score_norm, 0)

    return {
        "base_win_home": base_win_home,
        "score_path": score_path,
        "focus_score": adjusted_focus,
        "focus_score_norm": focus_score_norm
    }
