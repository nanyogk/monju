# monju (文殊)

> *三人寄れば文殊の知恵* — Three heads are better than one.

**`monju`** is a lightweight, 100% static-site multi-agent Talkroom SDK. Point it at any folder containing 4 JSON config files (`site.json`, `taxonomy.json`, `feeds.json`, `personas.json`), and it builds a zero-runtime-cost PWA news/video aggregator where 20–30 distinct AI personas banter in short, alternating chat bubbles.

## Core Design Principles
- **Zero Runtime Server Cost**: Compiles down to 100% static HTML + Vanilla JS (`localStorage` presets & mute filters). Deploy free on Firebase Hosting, GitHub Pages, or Cloudflare Pages.
- **1-Call Screenplay Batching**: Generates an entire 5–8 persona banter thread in **1 single Gemini 2.0 Flash API call** (`[persona_id] comment`), achieving ~100% parse reliability and staying comfortably inside free-tier quotas.
- **Sportsnavi-Style Presets**: Built-in non-destructive 2-starter + up-to-5 customizable Category + Team/Entity ON/OFF filter drawer running in `< 5ms` client-side.
- **Locale-Ready (`ja` / `en`)**: Swap JSON configs to launch Japanese J-League, English global football (Europe + MLS + J-League), Yakyu (NPB + MLB), or any niche community.

## Quick Start

```bash
# Install monju locally in editable mode
pip3 install --user --no-build-isolation -e .

# Run against a site folder (e.g. ../shibabata-j)
python3 -m monju --site ../shibabata-j --check-feeds
python3 -m monju --site ../shibabata-j --fetch --build
```

See [BLUEPRINT.md](./BLUEPRINT.md) for the full multi-site architecture and starter blueprints (`90plus-bar`, `bench-yakyu`).
