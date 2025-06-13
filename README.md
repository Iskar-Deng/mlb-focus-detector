# mlb-focus-detector

This is a Chrome extension that displays live MLB games with focus intensity.

## Features

- Shows teams, scores, inning, and outs
- Color-coded focus score (higher = redder, lower = bluer)
- Visual representation of base runners
- Click a game to open its MLB Gameday page
- Click the focus score to open MLB.TV

## Focus Logic

Focus score is calculated on the backend using inning, score difference, base state, etc., and shown in color gradient:
- Higher score → redder (more intense)
- Lower score → bluer (less interesting)

## How to Use

1. Load this extension via `chrome://extensions/`
2. Run the backend that provides a `/games` endpoint
3. run `server.py` in this directory
4. Click the extension icon to view games
5. Click any game to open its Gameday page

