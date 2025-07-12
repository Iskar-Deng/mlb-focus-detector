# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-07-11
### Changed
- Backend now **always fetches games based on US/Eastern date**, ensuring consistent game listings regardless of server time zone.
- Frontend no longer requires manual time zone selection.
- Automatically uses user's **local browser time zone** for game time formatting.

### Added
- Periodic fetch: **auto-refresh every 60 seconds** while popup is open, to keep data current and prevent Render backend from sleeping.

### Removed
- Time zone selection menu from extension context menu.
  
### Fixed
- Incorrect or missing game states (e.g. status stuck at “Scheduled”) caused by UTC-based date fetching in cloud deployment.

---

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
