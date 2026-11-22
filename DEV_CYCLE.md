# monju Development & Mobile Iteration Cycle (`DEV_CYCLE.md`)

This document captures the practical day-to-day workflow for iterating on **`monju` (SDK)** and any **`monju`-powered site** (like `shibabata-j`, `touchline-pub` / `90plus-bar`, or `bench-yakyu`).

---

## 1. The Fast Mobile-First Iteration Loop

Because `monju` builds 100% static HTML, there are **two complementary loops**:

### Loop A — Instant Local Wi-Fi Check (0s deploy)
Best when tweaking CSS/templates/presets rapidly on your laptop + phone on the same Wi-Fi:
```bash
cd shibabata-j
python3 main.py --build
python3 -m http.server 8000 --directory public
```
Then open `http://<your-mac-lan-ip>:8000/` on your phone (get IP via `ipconfig getifaddr en0`).

### Loop B — Real Mobile & PWA Check via GitHub Pages (~30s, Free HTTPS)
Best for real-world 5G testing, iOS/Android "Add to Home Screen" PWA behavior, YouTube embed smoothness, and sharing test links:
```bash
# 1. If you edited SDK templates/logic in ../monju:
cd ../monju
git add -A && git commit -m "feat: ..." && git push

# 2. Push site config / data update in shibabata-j:
cd ../shibabata-j
git add -A && git commit -m "chore: update feeds/presets" && git push
```
GitHub Actions (`.github/workflows/deploy_pages.yml`) automatically installs `monju`, runs `python3 main.py --build --base-path /shibabata-j`, and publishes to:
> **`https://nanyogk.github.io/shibabata-j/`**

---

## 2. RSS & YouTube Highlight Curation Cycle

Filtering official match highlights out of YouTube native (without Shorts, clickbait, or algorithm noise) is one of the highest-ROI features of a `monju` site.

### Adding or Tuning a Feed
1. Edit `config/feeds.json`:
   ```json
   {
     "id": "unext-football-yt",
     "name": "U-NEXT フットボール公式",
     "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCMjvvElkdLRTgcTKklAUkSw",
     "type": "youtube",
     "default_category_hint": "epl",
     "limit": 8,
     "enabled": true
   }
   ```
2. Verify HTTP 200 & live titles before fetching:
   ```bash
   python3 main.py --check-feeds
   ```
3. Fetch + rebuild:
   ```bash
   python3 main.py --fetch --build
   ```

### Tuning Categories & Team Tags (`taxonomy.json`)
Whenever you add new clubs, players, or league keywords in `config/taxonomy.json`, re-tag ALL previously stored articles in 1 second without re-fetching or spending LLM quota:
```bash
python3 main.py --recategorize --build
```

---

## 3. Enabling Real Live LLM Banter (When Ready)

By default (no `GEMINI_API_KEY` set), `monju` uses each persona's `fallback_line` from `config/personas.json` so you can iterate on UX, feeds, and mobile layout at zero quota cost.

When you are ready to turn on live 1-call Gemini 2.0 Flash banter:
1. Create a free key (no credit card, 1,500 calls/day free) at `https://aistudio.google.com/app/apikey`.
2. **Local test**:
   ```bash
   echo 'GEMINI_API_KEY="AIzaSy..."' > .env
   python3 test_llm.py
   python3 main.py --force-dialogue --build
   ```
3. **Automated GitHub Actions**:
   Add `GEMINI_API_KEY` in GitHub Repo → `Settings` → `Secrets and variables` → `Actions`.

---

## 4. Spinning Up a Brand-New Vertical Site (`touchline-pub` / `90plus-bar` / `bench-yakyu`)

Launching a new sibling site requires **zero engine code**:
1. Create a new folder & repo next to `monju/`:
   ```bash
   mkdir ../touchline-pub && cd ../touchline-pub
   mkdir -p config data
   ```
2. Copy `main.py`, `requirements.txt`, and `.github/workflows/deploy_pages.yml` (adjust `--base-path /<repo-name>`).
3. Author your 4 JSON files in `config/`:
   * `site.json` (`locale: "en"` or `"ja"`, brand, starter presets)
   * `taxonomy.json` (menubar category order + clubs/entities)
   * `feeds.json` (verify with `python3 main.py --check-feeds`)
   * `personas.json` (20–25 personas + `topic_seeds`)
4. Run `python3 main.py --fetch --build` and push to GitHub Pages!
