const TEAM_ID = {
  "ARI": 109, "ATL": 144, "BAL": 110, "BOS": 111, "CHC": 112, "CWS": 145,
  "CIN": 113, "CLE": 114, "COL": 115, "DET": 116, "HOU": 117, "KC": 118,
  "LAA": 108, "LAD": 119, "MIA": 146, "MIL": 158, "MIN": 142, "NYM": 121,
  "NYY": 147, "ATH": 133, "PHI": 143, "PIT": 134, "SD": 135, "SF": 137,
  "SEA": 136, "STL": 138, "TB": 139, "TEX": 140, "TOR": 141, "WSH": 120
};

function getFocusColor(value) {
  const num = Number(value);
  if (num < 50) return '#3498db';
  if (num < 120) return '#27ae60';
  if (num < 180) return '#f1c40f';
  if (num < 250) return '#e67e22';
  return '#e74c3c';
}

function fetchGamesAndRender() {
  chrome.storage.sync.get(["favorite", "follows", "timezone"], prefs => {
    fetch("http://localhost:8000/games", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(prefs)
    })
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById("games");
        container.innerHTML = "";

        data.forEach(game => {
          const div = document.createElement("div");
          div.className = "game";

          const awayAbbr = game.away_abbr;
          const homeAbbr = game.home_abbr;

          const awayLogo = `https://www.mlbstatic.com/team-logos/${TEAM_ID[awayAbbr]}.svg`;
          const homeLogo = `https://www.mlbstatic.com/team-logos/${TEAM_ID[homeAbbr]}.svg`;

          const isInProgress = game.status === "In Progress";
          const isFinal = game.status === "Final" || game.status === "Game Over";

          let inningHalfText = "", outsText = "", focusText = "", baseBoxesHTML = "";

          if (isInProgress) {
            const inning = game.inning ?? "?";
            const half = (game.half ?? "").charAt(0).toUpperCase() + (game.half ?? "").slice(1, 3);
            const outs = game.state?.split("_")[0] || "?";
            const baseState = game.state?.split("__")[1] || "000";

            inningHalfText = `${half} ${inning}`;
            outsText = `${outs} out`;

            baseBoxesHTML = `
              <div class="bases">
                <div class="base b1 ${baseState[0] === "1" ? "on" : ""}"></div>
                <div class="base b2 ${baseState[1] === "1" ? "on" : ""}"></div>
                <div class="base b3 ${baseState[2] === "1" ? "on" : ""}"></div>
              </div>
            `;

            focusText = `${game.focus_score_norm ?? ""}`;
          } else if (isFinal) {
            inningHalfText = "Final";
            outsText = "";
          } else {
            inningHalfText = game.game_time || "Scheduled";
            outsText = "";
          }

          let scoreDisplay = "";
          if (isInProgress) {
            scoreDisplay = `<span class="score-num score-inprogress">${game.away_runs ?? ""} - ${game.home_runs ?? ""}</span>`;
          } else if (isFinal) {
            scoreDisplay = `<span class="score-num score-final">${game.away_runs ?? ""} - ${game.home_runs ?? ""}</span>`;
          } else {
            scoreDisplay = `<span class="score-label">${awayAbbr} - ${homeAbbr}</span>`;
          }

          const html = `
            <div class="left">
              <img class="logo away" src="${awayLogo}" alt="${awayAbbr}">
              <div class="score-text">${scoreDisplay}</div>
              <img class="logo home" src="${homeLogo}" alt="${homeAbbr}">
            </div>
            <div class="info-group">
              <div class="middle">
                <div class="line1">${inningHalfText}</div>
                <div class="line2">${outsText}</div>
              </div>
              ${isInProgress ? `<div class="bases-wrapper">${baseBoxesHTML}</div>` : ""}
            </div>
            <div class="focus-column">
              ${isInProgress ? `<div class="focus" style="color: ${getFocusColor(focusText)}" data-id="${game.game_id}">${focusText}</div>` : ""}
            </div>
          `;

          div.innerHTML = html;
          if (game.game_id) {
            div.addEventListener("click", () => {
              const url = `https://www.mlb.com/gameday/${game.game_id}`;
              window.open(url, "_blank");
            });

            const focusElem = div.querySelector(".focus");
            if (focusElem) {
              focusElem.addEventListener("click", e => {
                e.stopPropagation();
                focusElem.classList.add("click-animate");
                setTimeout(() => focusElem.classList.remove("click-animate"), 300);

                const id = focusElem.dataset.id;
                if (id) {
                  const tvUrl = `https://www.mlb.com/tv/g${id}`;
                  window.open(tvUrl, "_blank");
                }
              });
            }
          }

          container.appendChild(div);
        });
      })
      .catch(() => {
        document.getElementById("games").textContent = "Failed to load. Make sure server.py is running.";
      });
  });
}

document.addEventListener("DOMContentLoaded", fetchGamesAndRender);
