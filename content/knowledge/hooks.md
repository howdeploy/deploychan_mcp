---
id: hooks
name: 'Hooks, cache, and the harness: control over the agent'
summary: >-
  How to get inside the black box of an autonomous agent: hooks (loop interceptors —
  per client, Claude Code / Codex / Hermes), prefix-based context caching (cache_control,
  TTL, env vars), RTK for compressing command output, and the harness as the frame that
  ties it all together.
type: knowledge
author: kisa
recommended: true
added: 2026-07-04
tags: [hooks, harness, caching, rtk, agent, optimization]
source: https://mcp.deploychan.webcam/docs
---

# Hooks, cache, and the harness: control over the agent

A modern agent (Claude Code, Codex, Hermes) stopped being a chatbot long ago. It works on
its own: it decides to run a command in the terminal, runs it, reads the result, and based
on the result decides the next step — and round and round it goes.

That autonomy is where all the power and all the trouble live. Every step the agent takes at
its own discretion. It picks the command itself. It pulls the full output back into context
itself — the whole thing, with all the garbage: progress bars, logs, two-hundred-line stack
traces. And it decides what comes next itself. Meanwhile companies love to trim the thinking
and swap out system instructions — at any moment that autonomy can start shooting you in the
knees.

The people who actually know agents usually skip exactly this part: they polish the system
prompt, lay out rules across `CLAUDE.md`, wire up MCP, pick the model — and leave the moment
itself, "agent decided → command ran → output came back", a black box. The point where you
can get into that box is between "decided" and "ran", and on the way back. That's what hooks
are.

## What hooks are

A hook is your script that the agent fires itself at a strictly defined moment in its loop.
Not you by hand, not on request — the agent automatically, every time it reaches the right
point. Decided to run a command → the hook fires before launch. Command finished → another
one fires. Session start, context compaction, end of response — you can hang code on any of
these events.

That's how control comes back: the agent is still autonomous, but your interceptors sit at
the key forks. One won't let `rm -rf` through, another runs the file through prettier after
an edit, a third slips a reminder into context, a fourth logs everything. Turned on via config
— each client has its own, but the logic is the same: "on event X run command Y".

### Claude Code

Hooks live in `settings.json` — globally `~/.claude/settings.json` or per project
`.claude/settings.json`. Events: `PreToolUse` (before a tool), `PostToolUse` (after),
`UserPromptSubmit`, `SessionStart`, `PreCompact` (before context compaction), `Stop`. The
script receives JSON via stdin (`tool_name`, `tool_input`, `cwd`…), and returns text in stdout
(injected into context), JSON, or an exit code — `exit 2` blocks execution.

Blocking dangerous commands:
```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [ { "type": "command", "command": "~/.claude/hooks/guard.sh" } ] }
    ]
  }
}
```
`guard.sh` reads the command from stdin, sees `rm -rf` or `git push --force` → `exit 2`, and
the agent won't run it. Other classics: auto-format after an edit (`PostToolUse` + `matcher:
"Write|Edit"` → `prettier`) and rule injection at startup (`SessionStart` → the script prints
guidelines straight into the agent's context).

### Codex

Almost identical to Claude Code — it copied the model down to matching event names. Hooks in
`~/.codex/config.toml` (the `[hooks]` section) or a separate `~/.codex/hooks.json`; per project —
`<repo>/.codex/...`.
```toml
[[hooks.PreToolUse]]
matcher = "^Bash$"
type = "command"
command = "python3 ~/.codex/hooks/check.py"
timeout = 30
statusMessage = "Checking the command"
```
A caveat: hooks reliably catch shell commands, but not always file edits (`apply_patch`) and
MCP calls — a known limitation. Plus there's a simpler mechanism — `notify`: a command on the
`agent-turn-complete` event (for example, a desktop notification that the agent has finished).

### Hermes

Hermes (Hermes Agent by Nous Research) can do hooks too, but they're built "programmer-style"
— through Python rather than raw shell. Three options:

- **Shell hooks** — closest to Claude Code: in `config.yaml` under the `hooks:` key you hang a
  shell command on an event (notifications, audit logs, alerts).
- **Gateway hooks** — `HOOK.yaml` + `handler.py` in `~/.hermes/hooks/<name>/`, catching
  `gateway:startup`, `session:start`, `agent:end`, `command:`.
- **Plugin hooks** — plugins (`~/.hermes/plugins/`, `plugin.yaml` + Python) on `pre_llm_call`,
  `post_llm_call`, `on_session_start/end`, `transform_llm_output`, `pre/post-tool-call`. Here a
  hook is a Python middleware function: you can rewrite the model's output before it lands in the dialogue.

## How caching works

Every request to the model is the entire context in full: the system prompt, the tool list,
the skills, the whole conversation history. Pushing all of that through again on every step is
expensive — so there's a cache. It runs on a single rule: **the prefix gets cached** — the part
that comes from the start and doesn't change.

The context assembly order is rigid: first the tools (`tools`), then the system prompt
(`system`), then the messages (`messages`). You place a cache point (`cache_control`) — and
everything before it goes into the cache. The next request with the same beginning reads it for
~10% of the price.

The key nuance: **the cache is a prefix match, byte for byte**. One byte changes at the start —
the entire cache after that spot burns down. Stick a `datetime.now()` into the system prompt —
every request is unique, there's no cache at all. Change the tool list (and it's at position 0) —
the whole cache is wiped. That's why the stable stuff is kept up front and left untouched, while
the changeable stuff (the current question, fresh command output) goes at the very end, after
the last cache point.

The TTL is short: 5 minutes by default (writes at 1.25x of normal) or an hour (writes at 2x).
Reading from cache — ~0.1x. On large repeating prefixes this saves up to 90%.

**What Claude caches.** That same prefix, in the familiar order: tool definitions, system prompt,
the start of the history. In Claude Code that's: the system prompt, all the tool descriptions,
your `CLAUDE.md`, and the accumulated history — the stable foundation of the session. You can
place up to four cache points. There's a threshold: a chunk smaller than ~1024 tokens (on Opus
4.x — ~4096) silently isn't cached, no error. The cache becomes readable only after the first
response has started streaming — so ten parallel requests with the same beginning will still pay
full price. To check: the `cache_read_input_tokens` field (read, cheap) vs
`cache_creation_input_tokens` (written, with a surcharge). A steady zero on reads means something
at the start is changing and breaking the cache.

**How to turn it on.** In a ready-made agent (Claude Code / Codex) — nothing to do, caching works
out of the box, controlled by env:
- `DISABLE_PROMPT_CACHING=1` — turn it off (there are per-model variants: `..._HAIKU/_SONNET/_OPUS`).
- `ENABLE_PROMPT_CACHING_1H=1` — hourly TTL (on a subscription the hour is given anyway; on API/Bedrock/Vertex — via this variable).
- `FORCE_PROMPT_CACHING_5M=1` — force 5 minutes back.

Your own code through the Anthropic API — you place the point by hand, the `cache_control` field in the Messages API request:
```python
client.messages.create(
    model="claude-opus-4-8",
    system=[{
        "type": "text",
        "text": "<large stable prompt>",
        "cache_control": {"type": "ephemeral"}
    }],
    messages=[{"role": "user", "content": "question"}],
)
```
A single `cache_control` at the top level — the system moves the point itself as the dialogue
grows. Manually — the same `cache_control` on a specific block (up to 4 points); hourly TTL —
`{"type": "ephemeral", "ttl": "1h"}`.

**Where the cache lives.** Not on your machine and not "inside the model itself". You can't build
your own in hardware, it doesn't touch the model weights — the model remembers nothing between
requests. Physically it's on the provider's servers (Anthropic, Bedrock, Vertex), and what's
stored there isn't texts/answers but intermediate computations over the prefix (internal token
representations). On a repeat the model takes the ready-made result, hence the savings. The cache
is ephemeral, tied to the model, and you have no direct access to it. A separate trick, "your own
cache on your side", is already a cache of finished ANSWERS on your end (Redis/a database): the
same request a second time → you hand back the saved one, without hitting the API at all. Two
different levers, don't confuse them.

## RTK — compressing command output

RTK (`rtk-ai/rtk`) — the "Rust Token Killer", a CLI proxy written in Rust. It hits the other side
of context: not the prefix, but command output. The agent is about to run `git status` or `ls -la`
— RTK intercepts it, runs it, and returns not raw output at ~2000 tokens but something squeezed
down to ~150–200: it filters garbage, collapses file trees, cuts repeats. 60–90% savings on output,
<10ms overhead, 100+ commands. It's installed as a hook (there's the tie-in with the first topic) —
that same `PreToolUse` interception that rewrites the command into its `rtk` equivalent.

## Compress prompts/skills or output?

You can do both, but the levers are different in nature. Command output (what RTK strangles) is
the changeable tail: new on every step, it never enters the cache and just piles up. Compress it —
you save directly and on every step. Prompts and skills are the opposite, a stable prefix: after
the first request they're already in the cache at ~10%. Compressing them makes sense, but the
effect is on the first (cold) request; on a warm cache — not much.

A gotcha from the prefix rule: compressing the tools and system prompt *on the fly*, mid-session,
is harmful. Touch `tools` (position 0) — you've blown the whole cache and paid to write it again.
With skills it's trickier: the savings are built in (progressive disclosure) — a skill sits as a
short description line, and the full body loads only when a task calls for it. The right move is
not to cram everything into `CLAUDE.md` but to keep instructions as skills on lazy loading.

In short, by descending impact: cut what isn't cached and piles up — command output (RTK) and the
swelling history. Keep the prefix (tools, system prompt) stable for the cache's sake and compress
it once at the start, not along the way. Skills — on lazy loading.

## What a harness is

The separate mechanisms above assemble into a single frame — the **harness**.

There's the model — that's weights. It can do exactly one thing: text in → text out. It doesn't
run commands, doesn't open files, doesn't remember the previous request. And there's the harness —
the program around the model that turns "text to text" into a working agent. You launch Claude Code
or Codex in the terminal — you're launching the harness; the model itself it calls over the network.

What the harness does:
- **The loop.** Assembles context, sends it to the model, gets a response. It decided to call a
  tool — the harness runs it and returns the result into context, sends again. Round and round,
  until the task is done. At each step the model only makes a decision; the harness runs the loop itself.
- **Context assembly.** What goes into the request and in what order (system, tools, CLAUDE.md,
  history) — the cache depends on the order.
- **Tools.** Declares the set to the model (Bash, Read, Edit, MCP) and executes the calls itself.
- **Interceptions.** The places where the harness wedges into the loop and runs your code — hooks.
- **Context and memory.** Compaction, truncation, cache, and whatever has to survive the session.

When people say "agent" they almost always mean the harness, not the model. The model can be
swapped (Opus today, Sonnet tomorrow) — the harness stays the same.

Memory is what people underrate most. The model holds no state between requests — every request is
independent. Memory exists only because the harness puts the history back into context each time.
But context is limited, it shrinks on compaction, and it resets between sessions. That's why
long-term memory is moved outside the model, into the harness: rules in `CLAUDE.md`, instructions
in skills, files, logs, external databases. An agent's memory is not a property of the model but
something built around it.

It all comes together:
- **Hooks** give control over the loop (protection via `PreToolUse`, a safety net via `SessionStart`/`PreCompact`).
- **Cache** lowers the cost (a stable prefix is read cheaply).
- **RTK** cleans the input (compresses command output, the history grows more slowly).
- **Memory** holds state between steps and sessions.

The takeaway is simple. Tuning the system prompt improves a single input to the model. Building a
harness sets up everything around it: protection so the agent doesn't run something dangerous; a
safety net so it doesn't lose context and rules; savings so it runs cheaper and longer before
compaction. The model is handed to you ready-made, and at any moment its thinking can be cut down
or its system instructions swapped. The harness you configure yourself, and it stays under your control.
