"""Tests for the six MCP tools."""

from __future__ import annotations

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from server import tools


def test_search_knowledge_finds_note(seeded):
    hits = tools.search_knowledge("how are prompts structured")
    ids = [h["id"] for h in hits]
    assert "prompt" in ids
    hit = next(h for h in hits if h["id"] == "prompt")
    assert hit["title"] == "Anatomy of a prompt"
    assert hit["source"] == "YouTube: KISA"


def test_search_covers_tools_not_skills(seeded):
    assert any(h["id"] == "tavily-setup" for h in tools.search_knowledge("tavily search"))
    # Skills are not searchable via search_knowledge.
    assert all(h["type"] in ("knowledge", "tool") for h in tools.search_knowledge("install"))


def test_search_injection_is_safe(seeded):
    # FTS5 operators / SQL punctuation must never raise, just yield a (possibly empty) list.
    for q in ['"; DROP TABLE items; --', "prompt AND (NEAR", "*", "", "   "]:
        assert isinstance(tools.search_knowledge(q), list)


def test_list_and_get_skill(seeded):
    skills = tools.list_skills()
    assert [s["id"] for s in skills] == ["tailored-install"]
    assert skills[0]["base"] is True

    pack = tools.get_skill("tailored-install")
    assert pack["reminder"].startswith("Detect the environment")
    assert pack["allowed_tools"] == ["Read", "Bash", "Write"]
    assert "Tailored Install" in pack["body"]


def test_get_skill_errors(seeded):
    with pytest.raises(ToolError):
        tools.get_skill("nope")
    with pytest.raises(ToolError):
        tools.get_skill("prompt")  # knowledge, not a skill


def test_get_item_returns_full_body(seeded):
    # tool: full body retrievable (search_knowledge only returns a snippet)
    tool = tools.get_item("tavily-setup")
    assert tool["type"] == "tool"
    assert "Install steps for Tavily" in tool["body"]

    # knowledge
    kn = tools.get_item("prompt")
    assert kn["type"] == "knowledge"
    assert "Roles, context, constraints" in kn["body"]

    # route: overview + ordered steps
    rt = tools.get_item("route-zero")
    assert rt["type"] == "route"
    assert [s["step_id"] for s in rt["steps"]] == ["route-zero:1", "route-zero:2"]

    with pytest.raises(ToolError):
        tools.get_item("nope")


def test_onboard_matches_and_falls_back(seeded):
    matched = tools.onboard("from zero to vibe coding")
    assert matched["route_id"] == "route-zero"
    assert matched["matched"] is True
    assert len(matched["steps"]) == 2
    assert matched["steps"][0]["ref_type"] == "knowledge"

    fallback = tools.onboard("xyzzy totally unrelated plugh")
    assert fallback["matched"] is False
    assert fallback["route_id"] == "route-zero"  # recommended route as a starting point


def test_next_step_walks_route(seeded):
    first = tools.next_step("route-zero:1")
    assert first["idx"] == 1
    assert first["total"] == 2
    assert first["materials"]["id"] == "prompt"
    assert first["next_step_id"] == "route-zero:2"

    last = tools.next_step("route-zero:2")
    assert last["materials"]["id"] == "tavily-setup"
    assert last["next_step_id"] is None

    with pytest.raises(ToolError):
        tools.next_step("route-zero:99")


def test_list_recommended_excludes_base(seeded):
    rec = tools.list_recommended()
    ids = {r["id"] for r in rec}
    assert ids == {"prompt", "route-zero"}  # recommended, base excluded, tavily not recommended
