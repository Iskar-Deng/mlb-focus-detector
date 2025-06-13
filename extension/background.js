const TEAMS = {
  "ARI": "Arizona Diamondbacks",
  "ATL": "Atlanta Braves",
  "ATH": "Athletics",
  "BAL": "Baltimore Orioles",
  "BOS": "Boston Red Sox",
  "CHC": "Chicago Cubs",
  "CWS": "Chicago White Sox",
  "CIN": "Cincinnati Reds",
  "CLE": "Cleveland Guardians",
  "COL": "Colorado Rockies",
  "DET": "Detroit Tigers",
  "HOU": "Houston Astros",
  "KC": "Kansas City Royals",
  "LAA": "Los Angeles Angels",
  "LAD": "Los Angeles Dodgers",
  "MIA": "Miami Marlins",
  "MIL": "Milwaukee Brewers",
  "MIN": "Minnesota Twins",
  "NYM": "New York Mets",
  "NYY": "New York Yankees",
  "PHI": "Philadelphia Phillies",
  "PIT": "Pittsburgh Pirates",
  "SD": "San Diego Padres",
  "SF": "San Francisco Giants",
  "SEA": "Seattle Mariners",
  "STL": "St. Louis Cardinals",
  "TB": "Tampa Bay Rays",
  "TEX": "Texas Rangers",
  "TOR": "Toronto Blue Jays",
  "WSH": "Washington Nationals"
};

const TIMEZONES = [
  "US/Pacific", "US/Mountain", "US/Central", "US/Eastern"
];

// Setup context menu when extension installed or updated
chrome.runtime.onInstalled.addListener(() => {
  // Favorite
  chrome.contextMenus.create({
    id: "fav_team",
    title: "Select Favorite Team",
    contexts: ["action"]
  });

  for (const [abbr, name] of Object.entries(TEAMS)) {
    chrome.contextMenus.create({
      id: `fav_${abbr}`,
      parentId: "fav_team",
      title: name,
      type: "radio",
      contexts: ["action"]
    });
  }

  // Follow (checkbox)
  chrome.contextMenus.create({
    id: "follow_team",
    title: "Follow Teams",
    contexts: ["action"]
  });

  for (const [abbr, name] of Object.entries(TEAMS)) {
    chrome.contextMenus.create({
      id: `follow_${abbr}`,
      parentId: "follow_team",
      title: name,
      type: "checkbox",
      contexts: ["action"]
    });
  }

  // Timezone
  chrome.contextMenus.create({
    id: "tz_group",
    title: "Select Time Zone",
    contexts: ["action"]
  });

  TIMEZONES.forEach(tz => {
    chrome.contextMenus.create({
      id: `tz_${tz}`,
      parentId: "tz_group",
      title: tz,
      type: "radio",
      contexts: ["action"]
    });
  });
});

// Handle clicks
chrome.contextMenus.onClicked.addListener((info) => {
  // Favorite
  if (info.menuItemId.startsWith("fav_")) {
    const abbr = info.menuItemId.replace("fav_", "");
    chrome.storage.sync.set({ favorite: TEAMS[abbr] });
  }

  // Follow (checkbox toggle)
  if (info.menuItemId.startsWith("follow_")) {
    const abbr = info.menuItemId.replace("follow_", "");
    chrome.storage.sync.get("follows", (data) => {
      const follows = new Set(data.follows || []);
      if (info.checked) {
        follows.add(TEAMS[abbr]);
      } else {
        follows.delete(TEAMS[abbr]);
      }
      chrome.storage.sync.set({ follows: [...follows] });
    });
  }

  // Timezone
  if (info.menuItemId.startsWith("tz_")) {
    const tz = info.menuItemId.replace("tz_", "");
    chrome.storage.sync.set({ timezone: tz });
  }
});
