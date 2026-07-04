"""Content dataclasses. See docs/CONTRACT.md §2 (content model) and §3 (DB schema)."""

from __future__ import annotations

from dataclasses import dataclass, field

CONTENT_TYPES = ("skill", "knowledge", "route", "tool")
AUTHORS = ("kisa", "third_party")


@dataclass
class Item:
    """One content item: a skill, knowledge note, route, or tool guide."""

    id: str
    type: str
    author: str
    name: str
    summary: str = ""
    body: str = ""
    recommended: bool = False
    is_base: bool = False
    added: str | None = None
    source: str | None = None
    reminder: str | None = None
    tags: list[str] = field(default_factory=list)
    extra: dict = field(default_factory=dict)  # triggers, allowed_tools, description, …


@dataclass
class RouteStep:
    """One ordered step of a route. ``step_id`` is globally unique: ``<route_id>:<idx>``."""

    step_id: str
    route_id: str
    idx: int
    title: str
    action: str | None = None
    ref: str | None = None  # id of a referenced item (skill/knowledge/tool)
    body: str = ""
