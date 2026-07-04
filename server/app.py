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
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

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


class _RelaxMcpAccept:
    """Normalize a missing or ``*/*`` Accept header on the MCP endpoint only.

    MCP Streamable HTTP requires clients to send ``Accept: application/json,
    text/event-stream``; the SDK returns 406 otherwise. Proper MCP clients comply, but
    curl (``*/*``) and minimal JSON-RPC clients often don't. Accept is content negotiation,
    not a security control, so normalizing it for the ``/mcp`` path removes needless
    friction without weakening anything. Non-HTTP scopes (lifespan) pass through untouched.
    """

    def __init__(self, app, mcp_path: str):
        self.app = app
        self.mcp_path = mcp_path

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http" and scope.get("path", "").startswith(self.mcp_path):
            accept = b""
            rest = []
            for key, value in scope["headers"]:
                if key == b"accept":
                    accept = value
                else:
                    rest.append((key, value))
            a = accept.decode("latin-1").lower()
            if (not a) or ("*/*" in a) or ("application/json" not in a):
                accept = b"application/json, text/event-stream"
            rest.append((b"accept", accept))
            scope = {**scope, "headers": rest}
        await self.app(scope, receive, send)


def create_app():
    asgi = mcp.streamable_http_app()
    # Serve the static site (landing, docs, catalog.json) at / — the /mcp route is
    # already registered, so it matches first; everything else falls through to static.
    if config.WEB_DIR.is_dir():
        asgi.router.routes.append(
            Mount("/", app=StaticFiles(directory=str(config.WEB_DIR), html=True))
        )
    asgi.add_middleware(TrustedHostMiddleware, allowed_hosts=config.allowed_hosts())
    return _RelaxMcpAccept(asgi, config.MCP_PATH)


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host=config.HOST, port=config.PORT)


if __name__ == "__main__":
    main()
