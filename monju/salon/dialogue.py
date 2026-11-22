"""Democratic Dialogue Coordinator using 1-Call Screenplay Batching."""
from __future__ import annotations

import random
from typing import Any

from monju.salon.router import select_personas_for_article
from monju.salon.screenplay import generate_thread_screenplay
from monju.site_loader import SiteContext


def generate_talkroom_dialogue(ctx: SiteContext, article: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    """Run a 5 to 8 persona banter thread in ONE single API call."""
    title = article.get("title", "")
    summary = article.get("summary", "")
    fan_comments = article.get("fan_comments", [])

    selected_personas = select_personas_for_article(ctx, title, summary, min_count=5, max_count=8)
    dialogue_history = generate_thread_screenplay(
        ctx=ctx,
        personas=selected_personas,
        article_title=title,
        article_summary=summary,
        fan_comments=fan_comments,
    )

    candidates = dialogue_history[-3:] if len(dialogue_history) >= 3 else dialogue_history
    chosen_teaser = random.choice(candidates)["content"] if candidates else ""
    return dialogue_history, chosen_teaser
