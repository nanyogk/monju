"""Generic X (Twitter) Outgoing Promotion Bot for monju sites."""
from __future__ import annotations

import json
import os
from typing import Any

from monju.site_loader import SiteContext


def publish_article_to_x(ctx: SiteContext, article: dict[str, Any]) -> bool:
    """Post an article to X (dry-run safe when credentials are absent)."""
    state_file = ctx.state_dir / "tweeted.json"
    tweeted_slugs: set[str] = set()
    if state_file.exists():
        try:
            tweeted_slugs = set(json.loads(state_file.read_text(encoding="utf-8")))
        except Exception:
            tweeted_slugs = set()

    slug = article.get("slug", "")
    if slug in tweeted_slugs:
        print(f"[monju.bot] Article {slug} already tweeted. Skipping.")
        return False

    base_url = os.getenv("SITE_BASE_URL") or ctx.site.get("base_url", "https://example.com")
    title = article.get("title", "")
    quote = article.get("punchy_quote", "")
    article_url = f"{base_url.rstrip('/')}/articles/{slug}/"

    if len(title) > 50:
        title = title[:47] + "…"
    if len(quote) > 70:
        quote = quote[:67] + "…"

    hashtags = " ".join(ctx.site.get("hashtags", [f"#{ctx.site.get('brand_name', 'monju')}"]))
    if ctx.locale == "en":
        tweet_text = f"{title}\n\n💬 Banter highlight:\n\"{quote}\"\n\n👇 Join the thread\n{article_url}\n\n{hashtags}"
    else:
        tweet_text = f"【話題の速報】{title}\n\n💬 AI論客の一言:\n「{quote}」\n\n👇 議論の続きを読む\n{article_url}\n\n{hashtags}"

    api_key = os.getenv("X_API_KEY", "")
    api_secret = os.getenv("X_API_SECRET", "")
    access_token = os.getenv("X_ACCESS_TOKEN", "")
    access_secret = os.getenv("X_ACCESS_TOKEN_SECRET", "")

    def _save() -> None:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(list(tweeted_slugs), ensure_ascii=False, indent=2), encoding="utf-8")

    if not (api_key and api_secret and access_token and access_secret):
        print("[monju.bot] (Dry Run - No X API keys found) Would post tweet:")
        print("-" * 50)
        print(tweet_text)
        print("-" * 50)
        tweeted_slugs.add(slug)
        _save()
        return True

    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )
        resp = client.create_tweet(text=tweet_text)
        print(f"[monju.bot] Successfully tweeted {slug} (Tweet ID: {resp.data.get('id')})")
        tweeted_slugs.add(slug)
        _save()
        return True
    except Exception as e:
        print(f"[monju.bot] Error posting to X: {e}")
        return False
