"""Unified CLI Pipeline Runner for monju Talkroom SDK."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from monju.bot.x_publisher import publish_article_to_x
from monju.generator.build_html import build_site
from monju.ingest.categorizer import enrich_article_with_tags
from monju.ingest.rss_fetcher import check_all_feeds, fetch_all_feeds
from monju.salon.dialogue import generate_talkroom_dialogue
from monju.site_loader import SiteContext, load_site


def load_articles(ctx: SiteContext) -> list[dict[str, Any]]:
    if ctx.articles_file.exists():
        try:
            return json.loads(ctx.articles_file.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_articles(ctx: SiteContext, articles: list[dict[str, Any]]) -> None:
    ctx.data_dir.mkdir(parents=True, exist_ok=True)
    ctx.articles_file.write_text(json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8")


def run_pipeline(
    site_dir: str | Path,
    fetch: bool = False,
    recategorize: bool = False,
    build: bool = True,
    tweet: bool = False,
    force_dialogue: bool = False,
    check_feeds: bool = False,
) -> None:
    ctx = load_site(site_dir)

    if check_feeds:
        check_all_feeds(ctx)
        if not (fetch or recategorize or build or tweet or force_dialogue):
            return

    existing_articles = load_articles(ctx)
    articles_map = {a["slug"]: a for a in existing_articles}

    if fetch:
        print(f"[monju] Fetching enabled feeds for '{ctx.site_id}'...")
        raw_items = fetch_all_feeds(ctx)
        added = 0
        for item in raw_items:
            slug = item["slug"]
            if slug not in articles_map:
                enriched = enrich_article_with_tags(ctx, item)
                articles_map[slug] = enriched
                added += 1
        print(f"[monju] Fetched {len(raw_items)} items ({added} new).")

    if recategorize:
        print(f"[monju] Re-categorizing {len(articles_map)} tracked articles using taxonomy.json...")
        feed_hint_by_name = {f.get("name"): f.get("default_category_hint", "auto") for f in ctx.feeds}
        for art in articles_map.values():
            if not art.get("feed_category_hint"):
                art["feed_category_hint"] = feed_hint_by_name.get(art.get("source", ""), "auto")
            enrich_article_with_tags(ctx, art)

    new_dialogue_count = 0
    for article in articles_map.values():
        if force_dialogue or not article.get("dialogue"):
            print(f"[monju.salon] Generating banter: {article['title'][:36]}...")
            dialogue, punchy_quote = generate_talkroom_dialogue(ctx, article)
            article["dialogue"] = dialogue
            article["punchy_quote"] = punchy_quote
            new_dialogue_count += 1

    all_articles = sorted(articles_map.values(), key=lambda x: x.get("published_at", ""), reverse=True)
    save_articles(ctx, all_articles)
    print(f"[monju] Tracked articles: {len(all_articles)} (new dialogues: {new_dialogue_count})")

    if build:
        print(f"[monju] Building static site into {ctx.public_dir}...")
        build_site(ctx, all_articles)

    if tweet and all_articles:
        latest = all_articles[0]
        print(f"[monju] Publishing latest article to X: {latest['title'][:36]}...")
        publish_article_to_x(ctx, latest)


def main(default_site: str = ".") -> None:
    parser = argparse.ArgumentParser(description="monju — Multi-Agent Talkroom Static Site Builder")
    parser.add_argument("--site", default=default_site, help="Path to site directory containing config/")
    parser.add_argument("--check-feeds", action="store_true", help="Verify HTTP status and entries for all feeds.json URLs")
    parser.add_argument("--fetch", action="store_true", help="Fetch fresh news/videos from feeds.json")
    parser.add_argument("--recategorize", action="store_true", help="Re-apply taxonomy.json categories & team tags to all stored articles")
    parser.add_argument("--build", action="store_true", help="Build static site into <site>/public/")
    parser.add_argument("--tweet", action="store_true", help="Publish latest article to X")
    parser.add_argument("--force-dialogue", action="store_true", help="Force regenerate banter threads with LLM")
    parser.add_argument("--all", action="store_true", help="Run full pipeline (Fetch -> Dialogue -> Build -> Tweet)")
    args = parser.parse_args()

    if args.all:
        run_pipeline(
            site_dir=args.site,
            fetch=True,
            recategorize=args.recategorize,
            build=True,
            tweet=True,
            force_dialogue=args.force_dialogue,
            check_feeds=args.check_feeds,
        )
    else:
        run_pipeline(
            site_dir=args.site,
            fetch=args.fetch,
            recategorize=args.recategorize,
            build=args.build,
            tweet=args.tweet,
            force_dialogue=args.force_dialogue,
            check_feeds=args.check_feeds,
        )
