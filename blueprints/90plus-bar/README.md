# Blueprint: `90plus-bar` (English Global Football Banter Bar)

> **Concept**: Stoppage-time pub banter covering **Europe (EPL / UCL / La Liga / Bundesliga) + MLS + J-League (English)** — built on `monju` with `locale: "en"`.  
> *(Note: Since a generic live-score app called "90Plus" exists, using **`90plus-bar`** / **"90+ Bar"** / **"90plus.bar"** keeps the soulful stoppage-time vibe distinct as a banter lounge.)*

## Planned `config/site.json`
- **Brand**: `90+ Bar` (`site_id: "90plus-bar"`)
- **Locale**: `"en"`
- **Menubar Order**: `All | EPL | Europe | MLS | J-League | Intl`
- **Starter Presets (up to 5 slots)**:
  1. `🍺 Europe + EPL` (`epl`, `europe`)
  2. `🌎 MLS + J-League` (`mls`, `jleague`)
  3. Users click `+ Add` to create up to 5 custom club mixes (e.g., `Arsenal + LAFC + Yokohama FM`).

## Candidate RSS & YouTube Feeds (`feeds.json`)
- **Europe / EPL**: BBC Sport Football RSS, The Guardian Football RSS, ESPN FC YouTube, Premier League YouTube, CBS Sports Golazo YouTube.
- **MLS**: Major League Soccer Official YouTube, MLSsoccer.com RSS.
- **J-League (English)**: J.LEAGUE International Official YouTube, Japan Times Football RSS.

## Sample English Personas (`personas.json`)
- `🍺 Pub Pundit` — "Proper Barclays tackle, none of this inverted fullback nonsense."
- `💻 xG Spreadsheet Nerd` — Quotes non-penalty xG, field tilt, and PPDA in 2 lines.
- `🦅 MLS Sicko` — Obsessed with GAM/TAM salary cap rules and 10:30pm After Dark chaos.
- `⛩️ J-League Hipster` — "You lot are just discovering him? Been watching him tear up J2 since 2023."
- `🚨 Fabrizio-Style Insider` — "Exclusive: Personal terms agreed on a 5-year deal. Here we go soon."
