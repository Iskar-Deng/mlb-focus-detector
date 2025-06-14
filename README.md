# mlb-focus-detector

This is a Chrome extension that displays live MLB games with a focus score representing game intensity.

![Popup UI Demo](assets/popup-demo.png)

## Features

- Shows teams, scores, inning, and outs
- Color-coded focus score (higher = redder, lower = bluer)
- Visual base runner display
- Click a game to open its MLB Gameday page
- Click the focus score to open the MLB.TV stream

## Focus Logic

The focus score measures how critical the current game situation is. It's calculated using:
- Inning and half-inning (with bonus weight after the 7th)
- Score difference
- Base/out state
- Win expectancy shift if runs are scored
- Final score is normalized to an integer, where 100 represents the game started.

The more a scoring event would swing the win probability, the higher the focus score.

## How to Use

1. Load this extension via `chrome://extensions/`
2. Install the required dependencies via `pip install -r requirements.txt`
3. Run `server.py` in this directory
4. Click the extension icon to view games
5. Click any game to open its Gameday page
6. Click the focus score to open the MLB.TV stream
