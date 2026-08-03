"""content/ -> SQLite + FTS5 and web/catalog.json. See docs/CONTRACT.md §5-§6.

Run: ``python -m server.ingest`` (or the ``deploychan-ingest`` script). Validation is
strict: bad content aborts with a non-zero exit so a broken corpus never ships.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
import sys
from pathlib import Path

import yaml

from . import config, db
from .models import AUTHORS

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)

# Which folder feeds which type, and how the id is derived from the path.
_SOURCES = {
    "skill": ("skills", "SKILL.md"),   # content/skills/<id>/SKILL.md
    "knowledge": ("knowledge", None),  # content/knowledge/<id>.md
    "route": ("routes", None),         # content/routes/<id>.md
    "tool": ("tools", None),           # content/tools/<id>.md
}


class ContentError(Exception):
    """Raised (collected) when a content file is invalid."""


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(meta, dict):
        raise ContentError("frontmatter is not a mapping")
    return meta, m.group(2).strip()


def _iso(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, (_dt.date, _dt.datetime)):
        return value.isoformat()[:10]
    return str(value)


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value]


def _discover(content_dir: Path) -> list[tuple[str, str, Path]]:
    """Yield (type, id, file_path) for every content file found."""
    found: list[tuple[str, str, Path]] = []
    for ctype, (folder, filename) in _SOURCES.items():
        base = content_dir / folder
        if not base.exists():
            continue
        if filename:  # skills: one dir per id
            for d in sorted(base.iterdir()):
                f = d / filename
                if d.is_dir() and f.exists():
                    found.append((ctype, d.name, f))
        else:  # single markdown file per id
            for f in sorted(base.glob("*.md")):
                found.append((ctype, f.stem, f))
    return found


def _build_item(ctype: str, item_id: str, path: Path, errors: list[str]) -> dict | None:
    try:
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    except ContentError as e:
        errors.append(f"{path}: {e}")
        return None

    def err(msg: str) -> None:
        errors.append(f"{path}: {msg}")

    if str(meta.get("id", item_id)) != item_id:
        err(f"frontmatter id '{meta.get('id')}' != path id '{item_id}'")
    if meta.get("type") and meta["type"] != ctype:
        err(f"frontmatter type '{meta['type']}' != folder type '{ctype}'")
    author = meta.get("author", "kisa")
    if author not in AUTHORS:
        err(f"author '{author}' not in {AUTHORS}")
    if not meta.get("name"):
        err("missing required field 'name'")
    if not meta.get("summary"):
        err("missing required field 'summary'")

    extra: dict = {}
    if meta.get("triggers"):
        extra["triggers"] = _as_list(meta["triggers"])
    if meta.get("allowed-tools") or meta.get("allowed_tools"):
        extra["allowed_tools"] = _as_list(meta.get("allowed-tools") or meta.get("allowed_tools"))
    if meta.get("description"):
        extra["description"] = str(meta["description"])

    steps = meta.get("steps") if ctype == "route" else None

    return {
        "row": {
            "id": item_id,
            "type": ctype,
            "author": author,
            "name": str(meta.get("name", item_id)),
            "summary": str(meta.get("summary", "")),
            "body": body,
            "recommended": 1 if meta.get("recommended") else 0,
            "is_base": 1 if meta.get("base") else 0,
            "added": _iso(meta.get("added")),
            "source": meta.get("source"),
            "reminder": meta.get("reminder"),
            "tags": json.dumps(_as_list(meta.get("tags")), ensure_ascii=False),
            "extra": json.dumps(extra, ensure_ascii=False),
        },
        "steps": steps,
    }


def _build_steps(route_id: str, steps, known_ids: set[str], errors: list[str]) -> list[dict]:
    out: list[dict] = []
    if not steps:
        errors.append(f"route '{route_id}': has no steps")
        return out
    if not isinstance(steps, list):
        errors.append(f"route '{route_id}': 'steps' must be a list")
        return out
    for i, step in enumerate(steps, start=1):
        if not isinstance(step, dict) or not step.get("title"):
            errors.append(f"route '{route_id}' step {i}: missing 'title'")
            continue
        ref = step.get("ref")
        if ref and ref not in known_ids:
            errors.append(f"route '{route_id}' step {i}: ref '{ref}' is not a known item id")
        out.append({
            "step_id": f"{route_id}:{i}",
            "route_id": route_id,
            "idx": i,
            "title": str(step["title"]),
            "action": step.get("action"),
            "ref": ref,
            "body": str(step.get("body", "")).strip(),
        })
    return out


def run_ingest(
    content_dir: Path | str | None = None,
    db_path: Path | str | None = None,
    web_dir: Path | str | None = None,
) -> dict:
    """Load content into the DB and write catalog.json. Returns a summary dict."""
    content_dir = Path(content_dir or config.CONTENT_DIR)
    db_path = Path(db_path or config.DB_PATH)
    web_dir = Path(web_dir or config.WEB_DIR)

    discovered = _discover(content_dir)
    errors: list[str] = []
    built = [b for b in (_build_item(t, i, p, errors) for t, i, p in discovered) if b]

    ids = [b["row"]["id"] for b in built]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        errors.append(f"duplicate item ids across types: {sorted(dupes)}")
    known_ids = set(ids)

    all_steps: list[dict] = []
    for b in built:
        if b["row"]["type"] == "route":
            all_steps += _build_steps(b["row"]["id"], b["steps"], known_ids, errors)

    if errors:
        raise SystemExit("ingest failed — invalid content:\n  " + "\n  ".join(errors))

    conn = db.connect_rw(db_path)
    try:
        db.init_schema(conn)
        conn.execute("DELETE FROM route_steps")
        conn.execute("DELETE FROM items")
        conn.execute("DELETE FROM items_fts")
        cols = ("id", "type", "author", "name", "summary", "body", "recommended",
                "is_base", "added", "source", "reminder", "tags", "extra")
        conn.executemany(
            f"INSERT INTO items ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
            [tuple(b["row"][c] for c in cols) for b in built],
        )
        conn.executemany(
            "INSERT INTO route_steps (step_id,route_id,idx,title,action,ref,body) "
            "VALUES (?,?,?,?,?,?,?)",
            [(s["step_id"], s["route_id"], s["idx"], s["title"], s["action"], s["ref"], s["body"])
             for s in all_steps],
        )
        # Russian display strings and translated bodies are indexed alongside the English
        # ones: without them every Russian-language query matches nothing at all.
        i18n_ru = _load_i18n_ru(content_dir)
        ru_bodies = _load_ru_bodies(content_dir)
        conn.executemany(
            "INSERT INTO items_fts (name,summary,tags,body,name_ru,summary_ru,body_ru,id) "
            "VALUES (?,?,?,?,?,?,?,?)",
            [(b["row"]["name"], b["row"]["summary"], b["row"]["tags"], b["row"]["body"],
              (i18n_ru.get(b["row"]["id"]) or {}).get("name", ""),
              (i18n_ru.get(b["row"]["id"]) or {}).get("summary", ""),
              ru_bodies.get(b["row"]["id"], ""),
              b["row"]["id"])
             for b in built],
        )
        conn.commit()
    finally:
        conn.close()

    catalog = _build_catalog(built, content_dir, web_dir)
    by_type: dict[str, int] = {}
    for b in built:
        by_type[b["row"]["type"]] = by_type.get(b["row"]["type"], 0) + 1
    return {
        "items": len(built),
        "by_type": by_type,
        "route_steps": len(all_steps),
        "catalog_items": len(catalog["items"]),
        "db_path": str(db_path),
    }


def _load_meta(content_dir: Path) -> dict:
    meta_file = content_dir / "meta.yml"
    if not meta_file.exists():
        return {}
    return yaml.safe_load(meta_file.read_text(encoding="utf-8")) or {}


def _load_i18n_ru(content_dir: Path) -> dict:
    """Russian display strings for the site catalog (name/summary), keyed by item id.

    Agent-facing bodies stay English; this only localizes the catalog cards when RU is picked.
    """
    f = content_dir / "i18n.ru.yml"
    if not f.exists():
        return {}
    return yaml.safe_load(f.read_text(encoding="utf-8")) or {}


def _load_ru_bodies(content_dir: Path) -> dict:
    """Russian translations of item bodies, keyed by item id.

    Lives in ``content/i18n/ru/<type>/<id>.md`` — a separate tree, deliberately outside the
    type folders that ``_discover`` walks, so a translation is never mistaken for its own
    catalog item. Frontmatter, if present, is stripped; only the prose is indexed.
    """
    base = content_dir / "i18n" / "ru"
    if not base.exists():
        return {}
    out: dict = {}
    for f in sorted(base.rglob("*.md")):
        _, body = parse_frontmatter(f.read_text(encoding="utf-8"))
        if body.strip():
            out[f.stem] = body.strip()
    return out


def _build_catalog(built: list[dict], content_dir: Path, web_dir: Path) -> dict:
    meta = _load_meta(content_dir)
    i18n_ru = _load_i18n_ru(content_dir)
    # Showcase catalog: exclude base skills (step-0 infrastructure, not browsable content).
    items = []
    for b in built:
        r = b["row"]
        if r["is_base"]:
            continue
        item = {
            "id": r["id"], "name": r["name"], "summary": r["summary"],
            "type": r["type"], "author": r["author"],
            "recommended": bool(r["recommended"]), "base": False,
            "added": r["added"], "tags": json.loads(r["tags"]),
        }
        ru = i18n_ru.get(r["id"]) or {}
        if ru.get("name"):
            item["name_ru"] = ru["name"]
        if ru.get("summary"):
            item["summary_ru"] = ru["summary"]
        items.append(item)
    items.sort(key=lambda x: (x["added"] or "", x["name"]), reverse=True)

    connect = dict(meta.get("connect", {}))
    connect["clients"] = meta.get("clients", {})
    catalog = {
        "generated": _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat(),
        "items": items,
        "connect": connect,
        "profile": meta.get("profile", {}),
    }
    web_dir.mkdir(parents=True, exist_ok=True)
    (web_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return catalog


def main() -> None:
    try:
        summary = run_ingest()
    except SystemExit as e:
        print(e, file=sys.stderr)
        raise
    print(
        f"ingest ok: {summary['items']} items {summary['by_type']}, "
        f"{summary['route_steps']} route steps, "
        f"catalog={summary['catalog_items']} -> {summary['db_path']}"
    )


if __name__ == "__main__":
    main()
