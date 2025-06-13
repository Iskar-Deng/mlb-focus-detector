# mlb-focus-detector

This is a Chrome extension that displays live MLB games with a focus score representing game intensity.

## Features

- Shows teams, scores, inning, and outs
- Color-coded focus score (higher = redder, lower = bluer)
- Visual base runner display
- Click a game to open its MLB Gameday page
- Click the focus score to open the MLB.TV stream

## Focus Logic

The focus score measures how critical the current game situation is. It's calculated using:
- Inning and half-inning
- Score difference from the batting team's perspective
- Base/out state
- Win expectancy shift if runs are scored

The more a scoring event would swing the win probability, the higher the focus score.

## How to Use

1. Load this extension via `chrome://extensions/`
2. Run `server.py` in this directory
3. Click the extension icon to view games
4. Click any game to open its Gameday page
5. Click the focus score to open the MLB.TV stream
