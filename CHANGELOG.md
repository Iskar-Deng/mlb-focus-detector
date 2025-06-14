# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-06-13
### Added
- Chrome extension UI for live MLB game display
- Color-coded focus score (blue → red based on intensity)
- Base runner visualization with diamond icons
- Click game to open MLB Gameday
- Click focus score to open MLB.TV
- Backend calculates focus using inning, score, base state, etc.

### Notes
- Focus score normalized using win expectancy projections and potential run distributions
- Data source: `statsapi` for live game state
- Display updates every time popup is opened
