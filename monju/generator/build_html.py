"""Static Site HTML & PWA Builder for monju.
Renders Top Page (with Sportsnavi-style presets), Category Pages, Team Pages, and Article Pages.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from monju.site_loader import SiteContext

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def build_site(ctx: SiteContext, articles: list[dict[str, Any]]) -> None:
    """Build all static HTML pages and PWA files into ctx.public_dir."""
    public_dir = ctx.public_dir
    public_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
    categories = ctx.categories
    all_teams = ctx.teams
    category_map = {c["slug"]: c for c in categories}

    # Group teams by category slug in taxonomy order
    teams_by_category: list[dict[str, Any]] = []
    for cat in categories:
        cat_teams = [t for t in all_teams if t.get("category") == cat["slug"]]
        teams_by_category.append({
            "slug": cat["slug"],
            "name": cat["name"],
            "short_name": cat.get("short_name", cat["name"]),
            "emoji": cat.get("emoji", ""),
            "teams": cat_teams,
        })

    # Normalize categories list on every article for safe template rendering
    sorted_articles = sorted(articles, key=lambda x: x.get("published_at", ""), reverse=True)
    for art in sorted_articles:
        if not art.get("categories"):
            art["categories"] = [art.get("category", categories[0]["slug"] if categories else "general")]

    shared_ctx = {
        "site": ctx.site,
        "i18n": ctx.i18n,
        "categories": categories,
        "category_map": category_map,
        "all_teams": all_teams,
        "teams_by_category": teams_by_category,
        "persona_count": len(ctx.personas),
        "default_presets": ctx.site.get("default_presets", []),
        "max_presets": int(ctx.site.get("max_presets", 5)),
    }

    # 1. Render Top Page (public/index.html)
    top_template = env.get_template("index.html")
    top_html = top_template.render(
        **shared_ctx,
        articles=sorted_articles,
        current_category=None,
        current_category_obj=None,
        current_team=None,
        current_team_obj=None,
        is_top_page=True,
    )
    (public_dir / "index.html").write_text(top_html, encoding="utf-8")
    print(f"[monju.build] Rendered Top page ({len(sorted_articles)} articles)")

    # 2. Render Category Pages (public/c/<category>/index.html)
    for cat in categories:
        cat_slug = cat["slug"]
        cat_dir = public_dir / "c" / cat_slug
        cat_dir.mkdir(parents=True, exist_ok=True)

        filtered = [
            a for a in sorted_articles
            if cat_slug in a.get("categories", [a.get("category")])
        ]
        cat_html = top_template.render(
            **shared_ctx,
            articles=filtered,
            current_category=cat_slug,
            current_category_obj=cat,
            current_team=None,
            current_team_obj=None,
            is_top_page=False,
        )
        (cat_dir / "index.html").write_text(cat_html, encoding="utf-8")
        print(f"[monju.build] Rendered Category: /c/{cat_slug}/ ({len(filtered)} articles)")

    # 3. Render Team / Entity Pages (public/t/<team>/index.html)
    for team in all_teams:
        team_slug = team["slug"]
        team_dir = public_dir / "t" / team_slug
        team_dir.mkdir(parents=True, exist_ok=True)

        filtered = [
            a for a in sorted_articles
            if any(t.get("slug") == team_slug for t in a.get("team_tags", []))
        ]
        team_html = top_template.render(
            **shared_ctx,
            articles=filtered,
            current_category=None,
            current_category_obj=None,
            current_team=team_slug,
            current_team_obj=team,
            is_top_page=False,
        )
        (team_dir / "index.html").write_text(team_html, encoding="utf-8")

    print(f"[monju.build] Rendered {len(all_teams)} team/entity tag pages")

    # 4. Render Article Detail Pages (public/articles/<slug>/index.html)
    article_template = env.get_template("article.html")
    for i, article in enumerate(sorted_articles):
        slug = article["slug"]
        art_dir = public_dir / "articles" / slug
        art_dir.mkdir(parents=True, exist_ok=True)

        prev_article = sorted_articles[i - 1] if i > 0 else None
        next_article = sorted_articles[i + 1] if i < len(sorted_articles) - 1 else None

        art_html = article_template.render(
            **shared_ctx,
            article=article,
            dialogue=article.get("dialogue", []),
            punchy_quote=article.get("punchy_quote", ""),
            prev_article=prev_article,
            next_article=next_article,
            current_category=article.get("category"),
            is_top_page=False,
        )
        (art_dir / "index.html").write_text(art_html, encoding="utf-8")

    print(f"[monju.build] Rendered {len(sorted_articles)} individual article pages")

    # 5. Generate PWA manifest.json
    brand = ctx.site.get("brand_name", "monju")
    emoji = ctx.site.get("logo_emoji", "⚽")
    theme_color = ctx.site.get("theme_color", "#10b981")
    manifest = {
        "name": f"{brand} - {ctx.site.get('tagline', '')}".strip(" -"),
        "short_name": brand,
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": theme_color,
        "description": ctx.site.get("description", ""),
        "icons": [
            {
                "src": f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>{emoji}</text></svg>",
                "sizes": "192x192 512x512",
                "type": "image/svg+xml",
                "purpose": "any maskable",
            }
        ],
    }
    (public_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # 6. Generate lightweight Service Worker (public/sw.js)
    sw_code = f"""// {brand} Service Worker (monju)
const CACHE_NAME = '{ctx.site_id}-v2';
self.addEventListener('install', (e) => {{
  self.skipWaiting();
}});
self.addEventListener('activate', (e) => {{
  e.waitUntil(clients.claim());
}});
self.addEventListener('fetch', (e) => {{
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
}});
"""
    (public_dir / "sw.js").write_text(sw_code, encoding="utf-8")
    print("[monju.build] Generated PWA manifest.json and sw.js")
