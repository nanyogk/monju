"""Generic Multi-Category & Entity/Team Tagging Engine for monju.
Driven 100% by config/taxonomy.json — zero domain-hardcoded keywords.
"""
from __future__ import annotations

from typing import Any

from monju.site_loader import SiteContext


def categorize_article(
    ctx: SiteContext,
    title: str,
    summary: str,
    feed_category_hint: str = "auto",
) -> tuple[str, list[str], list[dict[str, str]]]:
    """Inspect title, summary, and optional feed hint to assign:
    - primary category slug
    - full list of matched category slugs (supports multi-category overlap)
    - list of matching team/entity tags
    """
    haystack = f"{title} {summary}".lower()
    valid_cat_slugs = [c["slug"] for c in ctx.categories]
    priority_order = ctx.taxonomy.get("category_priority", valid_cat_slugs)
    fallback_cat = ctx.taxonomy.get("fallback_category") or (valid_cat_slugs[0] if valid_cat_slugs else "general")

    matched_teams: list[dict[str, str]] = []
    matched_categories: list[str] = []

    # 1. Match specific teams/entities from taxonomy.json
    for team in ctx.teams:
        for kw in team.get("keywords", []):
            if kw.lower() in haystack:
                matched_teams.append({
                    "slug": team["slug"],
                    "name": team["name"],
                    "short_name": team["short_name"],
                    "category": team["category"],
                    "color": team.get("color", "#3b82f6"),
                })
                if team["category"] not in matched_categories:
                    matched_categories.append(team["category"])
                break

    # 2. Match explicit category-level keywords defined in taxonomy.json
    for cat in ctx.categories:
        cat_slug = cat["slug"]
        for kw in cat.get("keywords", []):
            if kw.lower() in haystack:
                if cat_slug not in matched_categories:
                    matched_categories.append(cat_slug)
                break

    # 3. Apply feed_category_hint when nothing matched (or when hint is specific and not auto)
    if not matched_categories:
        if feed_category_hint and feed_category_hint != "auto" and feed_category_hint in valid_cat_slugs:
            matched_categories.append(feed_category_hint)
        else:
            matched_categories.append(fallback_cat)

    # 4. Pick primary category using priority_order
    primary = matched_categories[0]
    for p_cat in priority_order:
        if p_cat in matched_categories:
            primary = p_cat
            break

    # Order categories cleanly (primary first, then taxonomy order)
    ordered_cats = [primary] + [c for c in valid_cat_slugs if c in matched_categories and c != primary]
    return primary, ordered_cats, matched_teams


def enrich_article_with_tags(ctx: SiteContext, article: dict[str, Any]) -> dict[str, Any]:
    """Enrich an article dictionary with primary category, categories list, and team_tags."""
    hint = article.get("feed_category_hint", "auto")
    primary, categories, matched_teams = categorize_article(
        ctx,
        article.get("title", ""),
        article.get("summary", ""),
        feed_category_hint=hint,
    )
    article["category"] = primary
    article["categories"] = categories
    article["team_tags"] = matched_teams
    return article
