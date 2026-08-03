"""deploychan MCP — public remote-MCP server serving KISA's curated vibe-coding experience.

Content lives in ``content/`` (markdown + YAML frontmatter). ``ingest`` loads it into a
SQLite + FTS5 database and generates ``web/catalog.json``. ``app`` exposes four facets
(seven tools) over Streamable HTTP. See ``docs/CONTRACT.md`` for the full contract.
"""

__version__ = "0.1.0"
