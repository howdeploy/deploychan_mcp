---
id: agent-memory
name: The agent's memory system and evolution
summary: >-
  The memory ladder: LLM Wiki → FTS5 → RAG → Holographic → Curator → GEPA. What to
  pick for the person, who installs it how (Hermes out of the box vs Claude Code / Codex
  build it themselves), where it eats resources. Plus hooks against hallucinations.
type: knowledge
author: kisa
recommended: true
added: 2026-07-04
tags: [memory, rag, vector, wiki, hermes, evolution, agent]
source: https://mcp.deploychan.webcam/docs
---

# The memory system and evolution

The agent reads its notes fresh every time — the question is **what form the knowledge is
served in**. That determines whether it remembers everything in seconds or drowns in RAM.
Below is a ladder from simple to complex. The right answer isn't "the coolest one" but "the
one that fits the person".

**Research first, then choose.** Memory is the last step of the route for a reason: memory
tools (providers, frameworks, benchmarks) change fast. Before choosing, turn on internet
access (step 1, "Internet and research") and check the current state of the options with a
live search — don't rely on the model's memory, it goes stale. The stack is chosen on real data.

**What the agent should do:** question the person (privacy? a cheap VPS? huge docs? need
evolution?), pick a stack from this ladder to fit its own runtime, and set it up. Don't drag a
vector store into a place where a wiki is enough.

## The memory ladder

**1. LLM Wiki — notes in .md.** The agent writes notes in markdown, reads them through Obsidian,
and knows from its system instructions where to go. The rules for keeping the wiki live in the
wiki itself and in skills (example — ObsidianDataWeave; graphify builds the links). Note-taking
is Karpathy-style. Simple, transparent, no resource cost. Works with any client. Downside: no
good for fast search over a huge corpus or precise citation.

**2. FTS5 — SQL by keywords.** The same notes, but in a database with a full-text index (FTS5).
It doesn't search semantics, but in seconds it pulls whole months-old chats by keyword. That's
exactly why Hermes "always remembers everything". Covers 90% of cases, cheap, no resource cost.
By the way, this very MCP server runs on exactly SQLite+FTS5.

**3. RAG — vectors and semantics.** Notes, books, and docs are cut into chunks, each chunk turns
into an embedding (a vector of meaning) and lands in a vector DB. The agent searches not by words
but by meaning — "similar in sense". Load in whole books/docs/policy — the agent cites them deeply
and coherently. This is a separate tier with its own forks:

- **Static RAG** (the classic, Lewis et al., 2020). You index the corpus once — after that you
  only read. The data changed → the index is stale. Naively reindexing everything from scratch is
  expensive; the right way is **incrementally**: `upsert` only the changed chunks (insert the new
  one / update the existing one), a delta index on top of the stable one. That's what "keeping
  memory current" means at the vector level.
- **Dynamic / agentic RAG.** The agent decides for itself what more to fetch, reformulates the
  query, and appends to and updates its own database on the fly — the knowledge doesn't freeze.
  More expensive in latency, but it doesn't lie with stale data.
- **The cost isn't the vectors, it's the model in RAM.** The embeddings themselves are cheap: a
  vector = `dims × 4` bytes (1536-dim → ~6 KB). A couple of fat books is a few thousand chunks,
  ~10–150 MB, NOT gigabytes. GB scale starts at hundreds of thousands of vectors (~6 GB per 1M
  @1536d) — that's a library of hundreds of books. On a cheap VPS the RAM is eaten not by the
  vectors of a couple of books but by the **resident embedder model** (hundreds of MB to GB), an
  optional local LLM, and **in-memory engines** (Redis/FAISS in RAM). Cured with disk: `pgvector`
  (on top of Postgres), `Chroma`, `Qdrant`, `sqlite-vec` keep the vectors on disk. Retrieval
  orchestration — `LangChain` / `LlamaIndex`.

> Not to be confused with **RLM (Recursive Language Models**, MIT CSAIL, Zhang 2025). This is NOT
> storage and not a kind of RAG but an inference technique against *context rot*: a long context
> (10M+ tokens) is put into a Python-REPL variable, and the model writes code to slice/grep it and
> recursively call a sub-LLM. RLM belongs next to the harness and compaction, not in the memory
> ladder (breakdown — the `rlm` knowledge item).

Take vectors when you need to lock knowledge in at 99.9% and reference large docs/books/policy,
you have the resources for RAM/disk, and you're ready to vibe-code a solution out of ready-made
frameworks. Don't drag it into a place where keyword FTS5 is enough.

**4. Holographic — HRR, local, no dependencies.** A Hermes memory provider based on Holographic
Reduced Representations: algebraic memory on top of local SQLite, trust-scoring, instant recall,
and **zero external calls** (no LLM, no embeddings, no network). Ideal for privacy, air-gapped
setups, and weak hardware. Downside: search quality is below embeddings, no memory synthesis. On
Hermes it's set up with `hermes memory setup` → holographic; on other clients the equivalent gets
vibe-coded.

**5. Curator — curating built-in memory.** Not a dump but curated memory: the agent makes digests
of what's useful (facts about the person, the projects), runs session-search, and self-improves by
deciding what's worth keeping. Without curation, semantic memory turns into a landfill. On Hermes
this is a built-in layer (MEMORY.md / USER.md); the analog is Hindsight's `reflect` (periodic
synthesis over all memories, best on the LongMemEval benchmark).

**6. GEPA — prompt evolution (optional).** GEPA (Genetic-Pareto, Berkeley, arXiv 2507.19457) — the
agent reads its own traces (reasoning, tool calls, errors), reflects in natural language, diagnoses
failures, and **evolves its own instructions**, holding a Pareto front of the best variants. It
beats RL with many times fewer runs. This is what "evolution" means: over time the agent rewrites
itself to fit its tasks. Not a Hermes provider but a public package — installs anywhere (see below).

## Who installs it how (by client)

Half the ladder is the conveniences of a specific client, not universal packages. The fork depends
on who you are (step 0: identify the runtime).

**Hermes — out of the box.** The memory manager is built in: `hermes memory setup` switches between
8 providers (Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory).
Curator, session-search, Holographic's HRR memory — all ready, in one command. A person on Hermes
has the shortest path.

**Claude Code / Codex — build the base themselves.** There's no built-in memory manager, the stack
is assembled by hand — but it's not hard:

1. **LLM Wiki** — works immediately, nothing to install. Markdown + a "where to go" rule in the
   instructions. The base for everyone.
2. **FTS5** — gets vibe-coded: SQLite + a full-text index over notes/logs + a search command.
   Exactly what this MCP runs on. A day's work, covers 90%.
3. **Hooks** — Claude Code has a hook system out of the box (an anchor at session start, a
   fact-check after a response). Codex has no persistent hooks — the same effect comes from a
   wrapper script around the call.
4. **The heavy stuff (RAG vectors, HRR at the Holographic level)** — gets vibe-coded as needed out
   of ready-made frameworks. Not "out of the box", but doable.

**And GEPA, if the client isn't Hermes?** GEPA is not a Hermes provider but a public Python package:
`pip install gepa`, or `dspy.GEPA`, or `mlflow.genai.optimize_prompts()`. Any agent can install it.
The catch isn't installation but that this isn't "memory out of the box": GEPA evolves your
prompts/instructions against an eval signal (a task + a metric) that you have to define. For Claude
Code / Codex it's a vibe-code project: build a metric, feed it your traces, get improved
instructions. A light version of the same principle, without the package — by hand: periodically
read your traces, reflect, and rewrite your own `CLAUDE.md` / `AGENTS.md` / slash-commands, keeping
the best versions. That's what "evolution" is for a non-Hermes client.

## Hooks against hallucinations

A separately underrated story is the **hook system**: scripted agent events. With a hook you can
pull an anchor from the LLM Wiki at session start, and check facts after a response. It's a cheap,
powerful crutch against hallucinations and a playground for experiments. Claude Code has hooks out
of the box; where there are none, wrap the session in a script.

## How to choose for the person

- Transparent and cheap, everything under control → **LLM Wiki**.
- The default, 90% of tasks, memory "out of the box" → **FTS5** (Hermes / this MCP).
- Precise citation of huge docs, resources available → **RAG** (vectors).
- Privacy, weak hardware, zero dependencies → **Holographic** (Hermes) or a vibe-coded analog.
- Memory should clean and improve itself → **Curator / Hindsight reflect**.
- The agent should evolve on its own → **GEPA** (`pip install gepa` / `dspy.GEPA`).

The point is the same for every client: build a personal system for the person, one where the agent
doesn't forget and grows over time. Hermes gives it in a command, Claude Code and Codex — by hand.
The tier is chosen for the person and for real data, not by hype.
