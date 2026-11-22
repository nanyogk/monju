"""Site configuration loader for monju.
Loads the 4-JSON contract (site.json, taxonomy.json, feeds.json, personas.json) from any site directory.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from monju.i18n import get_i18n


@dataclass
class SiteContext:
    site_dir: Path
    config_dir: Path
    data_dir: Path
    public_dir: Path
    state_dir: Path
    site: dict[str, Any]
    taxonomy: dict[str, Any]
    feeds: list[dict[str, Any]]
    personas_data: dict[str, Any]
    i18n: dict[str, str]

    @property
    def site_id(self) -> str:
        return self.site.get("site_id", self.site_dir.name)

    @property
    def locale(self) -> str:
        return self.site.get("locale", "ja")

    @property
    def categories(self) -> list[dict[str, Any]]:
        return self.taxonomy.get("categories", [])

    @property
    def teams(self) -> list[dict[str, Any]]:
        return self.taxonomy.get("teams", [])

    @property
    def personas(self) -> list[dict[str, Any]]:
        return self.personas_data.get("personas", [])

    @property
    def topic_seeds(self) -> dict[str, Any]:
        return self.personas_data.get("topic_seeds", {})

    @property
    def articles_file(self) -> Path:
        return self.data_dir / "articles.json"


def _load_json(path: Path, default: Any) -> Any:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def load_site(site_dir: str | Path) -> SiteContext:
    """Load a monju site directory containing config/{site,taxonomy,feeds,personas}.json."""
    root = Path(site_dir).resolve()
    config_dir = root / "config"
    if not config_dir.exists():
        raise FileNotFoundError(f"Config directory not found at {config_dir}")

    site = _load_json(config_dir / "site.json", {})
    taxonomy = _load_json(config_dir / "taxonomy.json", {"categories": [], "teams": []})
    feeds_doc = _load_json(config_dir / "feeds.json", {"feeds": []})
    personas_data = _load_json(config_dir / "personas.json", {"personas": [], "topic_seeds": {}})

    locale = site.get("locale", "ja")
    i18n = get_i18n(locale, site.get("ui_labels"))

    return SiteContext(
        site_dir=root,
        config_dir=config_dir,
        data_dir=root / "data",
        public_dir=root / "public",
        state_dir=root / "state",
        site=site,
        taxonomy=taxonomy,
        feeds=feeds_doc.get("feeds", []),
        personas_data=personas_data,
        i18n=i18n,
    )
