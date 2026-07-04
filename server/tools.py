"""The four facets / six tools. See docs/CONTRACT.md §4.

Every tool is a plain synchronous function doing one parameterized, read-only SQLite
query — no shell, no eval, no filesystem access from user input. FastMCP runs sync tools
in a worker thread, so blocking the event loop is never a concern (docs/CONTRACT.md §9-§10).

The docstrings below are what a connected agent actually reads to decide when and how to
call each tool, so they double as the agent-facing spec (docs/CONTRACT.md §11).
"""

from __future__ import annotations

import json
import re
import sqlite3

from mcp.server.fastmcp.exceptions import ToolError

from . import config, db

# Word tokens: latin, digits, and Cyrillic. Everything else (FTS5 operators, quotes,
# punctuation) is dropped, so a user query can never inject FTS5 syntax.
_TOKEN = re.compile(r"[0-9A-Za-zЀ-ӿ_]+")


def _fts_query(text: str) -> str | None:
    tokens = _TOKEN.findall(text or "")
    if not tokens:
        return None
    return " OR ".join(f'"{t}"' for t in tokens)


def _query(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    conn = db.connect_ro(config.DB_PATH)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def _first_line(text: str, limit: int = 160) -> str:
    line = (text or "").strip().splitlines()[0] if (text or "").strip() else ""
    return line[:limit]


# --- 01 · Knowledge --------------------------------------------------------------------

def search_knowledge(query: str, limit: int = 5) -> list[dict]:
    """Search KISA's curated notes and guides by a natural-language query.

    Call this whenever you need context on a vibe-coding topic (an agent setup, a tool, a
    technique, a pattern KISA uses). Returns the most relevant fragments so you can drop
    them straight into your context.

    Args:
        query: A natural-language search query (any language).
        limit: Max number of fragments (default 5).

    Returns a list of {id, title, snippet, source, type, tags}. Empty list if nothing matches.
    The snippet is only a fragment — call get_item(id) to read the full guide.
    """
    match = _fts_query(query)
    if not match:
        return []
    lim = max(1, min(int(limit or config.SEARCH_DEFAULT_LIMIT), config.SEARCH_MAX_LIMIT))
    rows = _query(
        "SELECT i.id AS id, i.name AS name, i.source AS source, i.type AS type, "
        "i.tags AS tags, snippet(items_fts, 3, '[', ']', '…', 12) AS snippet "
        "FROM items_fts JOIN items i ON i.id = items_fts.id "
        "WHERE items_fts MATCH ? AND i.type IN ('knowledge','tool') "
        "ORDER BY rank LIMIT ?",
        (match, lim),
    )
    return [
        {
            "id": r["id"],
            "title": r["name"],
            "snippet": r["snippet"],
            "source": r["source"] or r["id"],
            "type": r["type"],
            "tags": json.loads(r["tags"] or "[]"),
        }
        for r in rows
    ]


def get_item(item_id: str) -> dict:
    """Get the FULL content of any catalog item by id — knowledge, tool, route or skill.

    search_knowledge and list_recommended give only a title and a short snippet. Once you
    know which item you want, call get_item(id) for the complete guide body. Works for every
    type: knowledge and tool guides (otherwise unreachable in full), skills (same body as
    get_skill), and routes (overview + step list — walk them with next_step).

    Args:
        item_id: An item id from search_knowledge, list_recommended, list_skills or the catalog.

    Returns {id, type, name, summary, body, tags, author, recommended, source}. Routes also
    include ``steps``. Raises an error (isError) if the id is unknown.
    """
    rows = _query("SELECT * FROM items WHERE id = ?", (item_id,))
    if not rows:
        raise ToolError(
            f"Item not found: '{item_id}'. Find valid ids via search_knowledge, "
            "list_recommended or list_skills."
        )
    r = rows[0]
    out = {
        "id": r["id"],
        "type": r["type"],
        "name": r["name"],
        "summary": r["summary"],
        "body": r["body"],
        "tags": json.loads(r["tags"] or "[]"),
        "author": r["author"],
        "recommended": bool(r["recommended"]),
        "source": r["source"] or r["id"],
    }
    if r["type"] == "route":
        steps = _query(
            "SELECT step_id, idx, title, action, ref FROM route_steps "
            "WHERE route_id = ? ORDER BY idx",
            (item_id,),
        )
        out["steps"] = [
            {"step_id": s["step_id"], "idx": s["idx"], "title": s["title"],
             "action": s["action"], "ref": s["ref"]}
            for s in steps
        ]
    return out


# --- 02 · Skills -----------------------------------------------------------------------

def list_skills() -> list[dict]:
    """List installable skills — ready-made packs (configs, steps, checklists).

    Use this to see what the agent can install for the user, then call get_skill(id) for
    the full pack. The base skill (tailored-install) comes first: it is step 0 of every
    install — always apply its discipline before installing anything.

    Returns a list of {id, name, summary, tags, author, recommended, base}.
    """
    rows = _query(
        "SELECT id, name, summary, tags, author, recommended, is_base FROM items "
        "WHERE type='skill' ORDER BY is_base DESC, recommended DESC, name COLLATE NOCASE"
    )
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "summary": r["summary"],
            "tags": json.loads(r["tags"] or "[]"),
            "author": r["author"],
            "recommended": bool(r["recommended"]),
            "base": bool(r["is_base"]),
        }
        for r in rows
    ]


def get_skill(skill_id: str) -> dict:
    """Get the full pack for one skill: install steps, config and checklist.

    Args:
        skill_id: A skill id from list_skills().

    Returns {id, name, summary, reminder, tags, allowed_tools, triggers, author,
    recommended, base, body}. The ``body`` is the full markdown pack. Raises an error
    (isError) if the id is unknown or is not a skill (tools/knowledge live in search_knowledge).
    """
    rows = _query("SELECT * FROM items WHERE id = ?", (skill_id,))
    if not rows:
        raise ToolError(f"Skill not found: '{skill_id}'. Use list_skills() to see valid ids.")
    r = rows[0]
    if r["type"] != "skill":
        raise ToolError(
            f"'{skill_id}' is a {r['type']}, not a skill — find tools and knowledge "
            "via search_knowledge or the catalog."
        )
    extra = json.loads(r["extra"] or "{}")
    return {
        "id": r["id"],
        "name": r["name"],
        "summary": r["summary"],
        "reminder": r["reminder"],
        "tags": json.loads(r["tags"] or "[]"),
        "allowed_tools": extra.get("allowed_tools", []),
        "triggers": extra.get("triggers", []),
        "author": r["author"],
        "recommended": bool(r["recommended"]),
        "base": bool(r["is_base"]),
        "body": r["body"],
    }


# --- 03 · Leveling up ------------------------------------------------------------------

def _route_payload(route_id: str, matched: bool) -> dict:
    info = _query("SELECT id, name, summary FROM items WHERE id = ?", (route_id,))
    if not info:
        return {"route_id": None, "matched": False, "steps": []}
    steps_rows = _query(
        "SELECT step_id, idx, title, action, ref, body FROM route_steps "
        "WHERE route_id = ? ORDER BY idx",
        (route_id,),
    )
    steps = []
    for s in steps_rows:
        ref_type = None
        if s["ref"]:
            tr = _query("SELECT type FROM items WHERE id = ?", (s["ref"],))
            ref_type = tr[0]["type"] if tr else None
        steps.append({
            "step_id": s["step_id"],
            "idx": s["idx"],
            "title": s["title"],
            "action": s["action"],
            "ref": s["ref"],
            "ref_type": ref_type,
            "summary": _first_line(s["body"]),
        })
    return {
        "route_id": info[0]["id"],
        "name": info[0]["name"],
        "summary": info[0]["summary"],
        "matched": matched,
        "steps": steps,
    }


def onboard(goal: str) -> dict:
    """Get a step-by-step leveling-up route for a goal: what to read and install, in order.

    Call this when the user has a concrete goal ("connect Tavily", "harden my VPS",
    "go from zero to shipping"). Returns the whole route with an ordered list of step ids;
    then call next_step(step_id) for each step's materials. Onboarding is stateless — you
    hold the progress, the server does not.

    Args:
        goal: The user's goal, in natural language.

    Returns {route_id, name, summary, matched, steps:[{step_id, idx, title, action, ref,
    ref_type, summary}]}. If nothing matches, ``matched`` is false and a recommended route
    is returned as a starting point.
    """
    match = _fts_query(goal)
    if match:
        rows = _query(
            "SELECT i.id AS id FROM items_fts JOIN items i ON i.id = items_fts.id "
            "WHERE items_fts MATCH ? AND i.type = 'route' ORDER BY rank LIMIT 1",
            (match,),
        )
        if rows:
            return _route_payload(rows[0]["id"], True)
    rows = _query("SELECT id FROM items WHERE type='route' AND recommended=1 ORDER BY added DESC LIMIT 1")
    if not rows:
        rows = _query("SELECT id FROM items WHERE type='route' ORDER BY added DESC LIMIT 1")
    if rows:
        return _route_payload(rows[0]["id"], False)
    return {"route_id": None, "matched": False, "steps": [],
            "message": "No leveling-up routes are available yet."}


def next_step(step_id: str) -> dict:
    """Get one route step's materials and action. See onboard() for the step ids.

    Args:
        step_id: A step id from onboard() (format ``<route_id>:<n>``).

    Returns {step_id, route_id, idx, total, title, action, ref, materials, body,
    next_step_id}. ``materials`` is the referenced item (id/type/name/summary/body) when the
    step points at one. ``next_step_id`` is null on the last step. Raises an error (isError)
    if the step id is unknown.
    """
    rows = _query(
        "SELECT step_id, route_id, idx, title, action, ref, body FROM route_steps WHERE step_id = ?",
        (step_id,),
    )
    if not rows:
        raise ToolError(f"Step not found: '{step_id}'. Get valid step ids from onboard().")
    s = rows[0]
    total = _query("SELECT COUNT(*) AS n FROM route_steps WHERE route_id = ?", (s["route_id"],))[0]["n"]
    materials = None
    if s["ref"]:
        m = _query("SELECT id, type, name, summary, body FROM items WHERE id = ?", (s["ref"],))
        if m:
            materials = {
                "id": m[0]["id"], "type": m[0]["type"], "name": m[0]["name"],
                "summary": m[0]["summary"], "body": m[0]["body"],
            }
    nxt = _query("SELECT step_id FROM route_steps WHERE route_id = ? AND idx = ?", (s["route_id"], s["idx"] + 1))
    return {
        "step_id": s["step_id"],
        "route_id": s["route_id"],
        "idx": s["idx"],
        "total": total,
        "title": s["title"],
        "action": s["action"],
        "ref": s["ref"],
        "materials": materials,
        "body": s["body"],
        "next_step_id": nxt[0]["step_id"] if nxt else None,
    }


# --- 04 · Recommended ------------------------------------------------------------------

def list_recommended() -> list[dict]:
    """KISA's curated picks across all types — what to install and read first.

    Call this when the user doesn't know where to start. Returns a cross-type shortlist.

    Returns a list of {id, name, type, summary, author, tags, added}.
    """
    rows = _query(
        "SELECT id, name, type, summary, author, tags, added FROM items "
        "WHERE recommended = 1 AND is_base = 0 ORDER BY added DESC, name COLLATE NOCASE"
    )
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "type": r["type"],
            "summary": r["summary"],
            "author": r["author"],
            "tags": json.loads(r["tags"] or "[]"),
            "added": r["added"],
        }
        for r in rows
    ]
