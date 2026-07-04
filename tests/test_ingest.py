"""Tests for content ingestion and catalog generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from server import ingest


def test_ingest_counts(seeded):
    s = seeded["summary"]
    assert s["items"] == 4
    assert s["by_type"] == {"skill": 1, "knowledge": 1, "route": 1, "tool": 1}
    assert s["route_steps"] == 2
    # Catalog excludes the base skill -> 3 showcase items.
    assert s["catalog_items"] == 3


def test_catalog_json(seeded):
    catalog = json.loads((seeded["web_dir"] / "catalog.json").read_text(encoding="utf-8"))
    ids = {i["id"] for i in catalog["items"]}
    assert "tailored-install" not in ids  # base skill hidden from the catalog
    assert ids == {"prompt", "route-zero", "tavily-setup"}
    assert catalog["connect"]["clients"]["claude-code"].startswith("claude mcp add")
    assert catalog["profile"]["name"] == "KISA"
    assert "generated" in catalog


def test_step_ids_are_namespaced(seeded):
    from server import config, db

    conn = db.connect_ro(config.DB_PATH)
    try:
        rows = conn.execute("SELECT step_id, ref FROM route_steps ORDER BY idx").fetchall()
    finally:
        conn.close()
    assert [r["step_id"] for r in rows] == ["route-zero:1", "route-zero:2"]
    assert [r["ref"] for r in rows] == ["prompt", "tavily-setup"]


def test_bad_ref_aborts(tmp_path: Path):
    content = tmp_path / "content"
    (content / "routes").mkdir(parents=True)
    (content / "routes" / "broken.md").write_text(
        "---\nid: broken\nname: Broken\nsummary: x\ntype: route\nadded: 2026-01-01\n"
        "steps:\n  - title: Go\n    ref: does-not-exist\n---\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        ingest.run_ingest(content_dir=content, db_path=tmp_path / "d.db", web_dir=tmp_path / "w")


def test_missing_required_field_aborts(tmp_path: Path):
    content = tmp_path / "content"
    (content / "knowledge").mkdir(parents=True)
    (content / "knowledge" / "nosummary.md").write_text(
        "---\nid: nosummary\nname: No Summary\ntype: knowledge\nadded: 2026-01-01\n---\nbody\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        ingest.run_ingest(content_dir=content, db_path=tmp_path / "d.db", web_dir=tmp_path / "w")
