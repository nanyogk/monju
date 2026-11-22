# monju Multi-Site Blueprint

> **Engine Repo**: `github.com/nanyogk/monju` (0% domain-hardcoded reusable SDK)  
> **First Site Repo**: `github.com/nanyogk/shibabata-j` (芝ばたJ — Japanese Football Talkroom)  
> **Future Site Repos**: `90plus-bar` (English Europe + MLS + J-League), `bench-yakyu` (NPB + MLB)

---

## 1. Two-Tier Repository Topology

```text
workspace/
├── monju/                        # Standalone SDK repo (this repo)
│   ├── pyproject.toml
│   ├── BLUEPRINT.md
│   ├── monju/                    # Pure Python + Jinja2 + Vanilla JS engine
│   │   ├── cli.py                # Unified CLI (--site, --fetch, --recategorize, --check-feeds, --build)
│   │   ├── site_loader.py        # Reads 4 JSON configs from any site folder
│   │   ├── i18n.py               # Built-in `ja` & `en` UI chrome + LLM prompt templates
│   │   ├── ingest/               # Config-driven RSS & YouTube fetcher + multi-category tagger
│   │   ├── salon/                # Democratic 5–8 persona router + 1-call screenplay engine
│   │   ├── generator/            # Static HTML + PWA + Sportsnavi-style preset drawer builder
│   │   └── bot/                  # X (Twitter) optional publisher
│   └── blueprints/
│       ├── 90plus-bar/           # English Global Football Bar (Europe + MLS + J-League)
│       └── bench-yakyu/          # Yakyu Talkroom (NPB + MLB)
│
├── shibabata-j/                  # Active Site Repo #1 (Japanese Football)
│   ├── config/
│   │   ├── site.json
│   │   ├── taxonomy.json
│   │   ├── feeds.json
│   │   └── personas.json
│   ├── data/articles.json
│   ├── main.py
│   └── public/
│
├── 90plus-bar/                   # Future Site Repo #2 (English Europe + MLS + J-League)
└── bench-yakyu/                  # Future Site Repo #3 (Japanese NPB + MLB)
```

---

## 2. The 4-JSON Site Contract

Creating a new vertical talkroom requires **zero Python or HTML edits** — only 4 files inside `config/`:

| File | Responsibility |
| :--- | :--- |
| `config/site.json` | Brand name, `locale` (`"ja"` or `"en"`), tagline, theme color, GitHub/site URLs, X hashtags, `default_presets` (2 starter presets), `max_presets` (5), and optional UI text overrides. |
| `config/taxonomy.json` | Ordered list of `categories` (defines Menubar order!), `fallback_category`, category keyword cues, and `teams` (entities/clubs with slug, short name, category, brand hex color, and keyword list). |
| `config/feeds.json` | Array of RSS & YouTube feeds (`id`, `name`, `url`, `type`, `default_category_hint`, `limit`, `enabled`). Validated via `--check-feeds`. |
| `config/personas.json` | Roster of 20–30 personas (`id`, `name`, `short_name`, `avatar_emoji`, `color`, `system_prompt`, optional `fallback_line`) + `topic_seeds` for contextual routing. |

---

## 3. Navigation & Sportsnavi-Style Preset UX

1. **Soul-First Single-Row Menubar**:
   * Displays static SEO category tabs in exact `taxonomy.json` order (for `shibabata-j`: `総合 | J1 | J2・J3 | 日本代表 | EPL | 欧州`).
   * Zero duplicate category bars, zero cluttered tag walls above the fold.
2. **Non-Destructive Presets (2 Starters + Up to 5 Slots)**:
   * Top page displays a single compact Preset Strip: `[🔥 All] [Starter 1] [Starter 2] [Custom 3..5] [＋ Add]`.
   * Users never have to overwrite starter presets to make their own; they can freely add up to 5 slots, rename, delete, or reset to defaults.
3. **Sportsnavi OR-Filter Rule (`< 5ms` Vanilla JS)**:
   * `Category = ON` → includes all articles in that category.
   * `Category = OFF` + `Team = ON` → includes only articles matching that specific team alongside other ON categories.
   * Persisted entirely in `localStorage` (`<site_id>_presets_v1`).

---

## 4. Multi-Category Tagging & Feed Curation

* Articles receive **both** a primary `category` (for breadcrumbs/badges) and a `categories` list (e.g., `["national", "epl"]` when a Brighton/Samurai Blue story drops).
* Each feed in `feeds.json` supplies a `default_category_hint` (`"j1"`, `"epl"`, `"europe"`, `"national"`, or `"auto"`), preventing overseas highlights from falsely falling back into domestic categories.
* Use `python3 main.py --check-feeds` to audit HTTP status, entry count, and latest titles whenever curating new RSS/YouTube channels.

---

## 5. Planned Sibling Verticals

* **[`blueprints/90plus-bar/`](./blueprints/90plus-bar/README.md)**: English-only stoppage-time banter bar covering **Europe (EPL/UCL/La Liga) + MLS + J-League**.
* **[`blueprints/bench-yakyu/`](./blueprints/bench-yakyu/README.md)**: Japanese baseball dugout talkroom covering **NPB (Central/Pacific) + MLB Japanese Stars + Samurai Japan**.
