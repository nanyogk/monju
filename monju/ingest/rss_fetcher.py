"""Config-driven RSS and YouTube Video Highlight Ingestion Engine for monju."""
from __future__ import annotations

import datetime
import hashlib
import re
import time
from typing import Any

import feedparser
import requests
from bs4 import BeautifulSoup

from monju.site_loader import SiteContext

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def clean_text(html_content: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()


def generate_slug(date_str: str, title: str) -> str:
    """Generate YYYYMMDD-hash slug from title."""
    h = hashlib.sha256(title.encode("utf-8")).hexdigest()[:8]
    sanitized_date = date_str.replace("-", "")[:8]
    return f"{sanitized_date}-{h}"


def parse_entry_date(entry: Any) -> tuple[str, str]:
    """Return ISO format string and date prefix YYYYMMDD."""
    now = datetime.datetime.now(datetime.timezone.utc)
    dt = now

    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
        except Exception:
            dt = now
    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            dt = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
        except Exception:
            dt = now

    return dt.isoformat(), dt.strftime("%Y%m%d")


def extract_fan_buzz(ctx: SiteContext, title: str, summary: str) -> list[str]:
    """Extract fan commentary talking points using site-configured buzz rules or locale defaults."""
    buzz: list[str] = []
    text = f"{title} {summary}".lower()

    for rule in ctx.site.get("fan_buzz_rules", []):
        keywords = rule.get("keywords", [])
        comment = rule.get("comment", "")
        if comment and any(kw.lower() in text for kw in keywords):
            buzz.append(comment)

    if not buzz:
        t_short = title[:24] + ("…" if len(title) > 24 else "")
        buzz = [
            ctx.i18n["default_buzz_1"].format(title=t_short),
            ctx.i18n["default_buzz_2"],
        ]

    return buzz[:3]


def check_all_feeds(ctx: SiteContext) -> list[dict[str, Any]]:
    """Probe every configured feed in feeds.json and print a health report."""
    report: list[dict[str, Any]] = []
    print(f"[monju] Checking {len(ctx.feeds)} configured feeds for site '{ctx.site_id}'...\n")

    for feed_info in ctx.feeds:
        enabled = feed_info.get("enabled", True)
        status_flag = "ON " if enabled else "OFF"
        name = feed_info.get("name", feed_info.get("id", "unknown"))
        url = feed_info.get("url", "")
        t0 = time.time()
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            elapsed = time.time() - t0
            parsed = feedparser.parse(resp.content) if resp.status_code == 200 else None
            count = len(parsed.entries) if parsed else 0
            latest = clean_text(getattr(parsed.entries[0], "title", ""))[:44] if count else "-"
            ok = resp.status_code == 200 and count > 0
            mark = "✅" if ok else "⚠️"
            print(f"  {mark} [{status_flag}] HTTP {resp.status_code} | {count:2d} items | {elapsed:4.2f}s | {name:<24} | {latest}")
            report.append({"id": feed_info.get("id"), "name": name, "ok": ok, "status": resp.status_code, "count": count})
        except Exception as e:
            elapsed = time.time() - t0
            print(f"  ❌ [{status_flag}] ERROR    |  0 items | {elapsed:4.2f}s | {name:<24} | {e}")
            report.append({"id": feed_info.get("id"), "name": name, "ok": False, "status": 0, "count": 0})

    ok_count = sum(1 for r in report if r["ok"])
    print(f"\n[monju] Feed health summary: {ok_count}/{len(report)} healthy.")
    return report


def normalize_title_for_dedupe(title: str) -> str:
    """Normalize headline by removing trailing source suffixes like '(サッカーキング)' for deduplication."""
    cleaned = re.sub(r"[\(（][^\(（\)）]{2,20}[\)）]\s*$", "", title).strip()
    return re.sub(r"\s+", "", cleaned).lower()


def fetch_all_feeds(ctx: SiteContext, default_limit: int = 8) -> list[dict[str, Any]]:
    """Fetch and parse all enabled RSS and YouTube feeds configured for the site."""
    articles: list[dict[str, Any]] = []
    seen_titles: set[str] = set()

    for feed_info in ctx.feeds:
        if not feed_info.get("enabled", True):
            continue

        name = feed_info.get("name", "Feed")
        url = feed_info.get("url", "")
        feed_type = feed_info.get("type", "rss")
        limit = int(feed_info.get("limit", default_limit))
        category_hint = feed_info.get("default_category_hint", "auto")

        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"[monju.ingest] Warning: {name} returned HTTP {resp.status_code}")
                continue

            parsed = feedparser.parse(resp.content)
            entries = parsed.entries[:limit]

            for entry in entries:
                title = clean_text(getattr(entry, "title", ""))
                norm_title = normalize_title_for_dedupe(title)
                if not title or norm_title in seen_titles:
                    continue
                seen_titles.add(norm_title)

                link = getattr(entry, "link", "")
                raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
                summary = clean_text(raw_summary)
                if len(summary) > 280:
                    summary = summary[:277] + "..."

                iso_date, date_prefix = parse_entry_date(entry)
                slug = generate_slug(date_prefix, title)

                video_id = None
                if feed_type == "youtube":
                    video_id = getattr(entry, "yt_videoid", None)
                    if not video_id and "v=" in link:
                        video_id = link.split("v=")[-1].split("&")[0]
                    elif not video_id and "/shorts/" in link:
                        video_id = link.split("/shorts/")[-1].split("?")[0]

                thumbnail = None
                if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                    thumbnail = entry.media_thumbnail[0].get("url")
                elif video_id:
                    thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

                fan_comments = extract_fan_buzz(ctx, title, summary)

                articles.append({
                    "id": slug,
                    "slug": slug,
                    "title": title,
                    "link": link,
                    "summary": summary if summary else f"{title}{ctx.i18n['default_summary_suffix']}",
                    "source": name,
                    "feed_id": feed_info.get("id", ""),
                    "feed_type": feed_type,
                    "feed_category_hint": category_hint,
                    "video_id": video_id,
                    "thumbnail": thumbnail,
                    "fan_comments": fan_comments,
                    "published_at": iso_date,
                    "date_prefix": date_prefix,
                })
        except Exception as e:
            print(f"[monju.ingest] Warning: Failed to fetch {name}: {e}")

    articles.sort(key=lambda x: x["published_at"], reverse=True)
    return articles
