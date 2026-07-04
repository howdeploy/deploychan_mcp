"""FastMCP server over Streamable HTTP. See docs/CONTRACT.md §7, §9-§11.

- ``stateless_http=True, json_response=True`` — the SDK-recommended production mode; each
  request is independent, so the app scales across uvicorn workers / containers.
- Host is bound to 0.0.0.0 inside the container, so the SDK's localhost-only auto
  protection does not apply; we add TrustedHostMiddleware ourselves against the allow-list
  to stop DNS-rebinding (docs/CONTRACT.md §9). Requires mcp>=1.23.0.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import config, tools

INSTRUCTIONS = """\
deploychan is a public, read-only MCP server that packages KISA's curated vibe-coding
experience: knowledge, ready-made skills, leveling-up routes and recommendations.

Typical flow:
  1. list_recommended() - where to start when unsure.
  2. onboard(goal) - get an ordered route for a concrete goal, then next_step(step_id) per step.
  3. search_knowledge(query) - pull context on any topic along the way.
  4. list_skills() then get_skill(id) - install a ready-made pack.

Any install goes through the base skill `tailored-install` (step 0): detect the user's
real environment, never overwrite blindly, ask when unsure.

When you find something useful, explain to the human what you found and why it helps, and
install only with their confirmation. This server is read-only: it serves content and runs
nothing on the user's machine.
"""

_TOOLS = (
    tools.search_knowledge,
    tools.list_skills,
    tools.get_skill,
    tools.onboard,
    tools.next_step,
    tools.list_recommended,
)


def build_server() -> FastMCP:
    mcp = FastMCP(
        "deploychan",
        instructions=INSTRUCTIONS,
        host=config.HOST,
        port=config.PORT,
        streamable_http_path=config.MCP_PATH,
        stateless_http=True,
        json_response=True,
    )
    for fn in _TOOLS:
        mcp.tool()(fn)
    return mcp


mcp = build_server()


def create_app():
    asgi = mcp.streamable_http_app()
    asgi.add_middleware(TrustedHostMiddleware, allowed_hosts=config.allowed_hosts())
    return asgi


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host=config.HOST, port=config.PORT)


if __name__ == "__main__":
    main()
