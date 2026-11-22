"""Democratic Persona Selector for monju.
Randomly selects 5 to 8 personas per article in randomized speaking order,
seeded gently by topic_seeds defined in config/personas.json.
"""
from __future__ import annotations

import random
from typing import Any

from monju.site_loader import SiteContext


def select_personas_for_article(
    ctx: SiteContext,
    title: str,
    summary: str,
    min_count: int = 5,
    max_count: int = 8,
) -> list[dict[str, Any]]:
    """Select 5 to 8 personas in randomized order for a democratic banter thread."""
    personas_map = {p["id"]: p for p in ctx.personas}
    if not personas_map:
        return []

    text = f"{title} {summary}".lower()
    target_count = min(len(personas_map), random.randint(min_count, max_count))

    # 1. Contextual topic seeds from personas.json
    seeded_ids: list[str] = []
    for _topic, seed_data in ctx.topic_seeds.items():
        keywords = seed_data.get("keywords", [])
        candidates = seed_data.get("candidates", [])
        if any(kw.lower() in text for kw in keywords):
            available = [cid for cid in candidates if cid in personas_map and cid not in seeded_ids]
            if available:
                seeded_ids.extend(random.sample(available, min(len(available), 2)))
        if len(seeded_ids) >= 3:
            break

    # 2. Fill remaining slots democratically from the entire persona pool
    remaining_ids = [pid for pid in personas_map if pid not in seeded_ids]
    random.shuffle(remaining_ids)

    chosen_ids = list(seeded_ids)
    needed = target_count - len(chosen_ids)
    if needed > 0:
        chosen_ids.extend(remaining_ids[:needed])

    # 3. Randomize final speaking order
    random.shuffle(chosen_ids)
    return [personas_map[pid] for pid in chosen_ids]
