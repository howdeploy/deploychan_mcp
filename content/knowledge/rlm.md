---
id: rlm
name: 'RLM — Recursive Language Models against context rot'
summary: >-
  When context bloats, the agent gets dumber (context rot). RLM (MIT CSAIL, 2025) — not a
  bigger window, but a different inference: the long input sits in a Python REPL as a variable,
  and the model writes code to slice/grep it and recursively call sub-LLMs. Up to 100× past the
  window, 10M+ tokens.
type: knowledge
author: kisa
recommended: true
added: 2026-07-04
tags: [rlm, context, long-context, harness, context-rot, agent]
source: https://arxiv.org/abs/2512.24601
---

# RLM — Recursive Language Models

The longer the context, the WORSE the agent. A long Claude Code session gets dumber, ChatGPT
forgets instructions after 50 messages, the agent loses its personality mid-task. This is
**context rot** ("lost in the middle"): the model physically can't hold attention across the whole
window, and its retrieval is U-shaped — it remembers the beginning and end well, and drops the
middle. A bigger window doesn't solve it: at 500k+ tokens the degradation only gets worse.

**RLM flips the approach.** Recursive Language Models — Alex Zhang, Tim Kraska, Omar Khattab, MIT
CSAIL (arXiv 2512.24601, late 2025). Not an architecture and not fine-tuning — it's an
**inference strategy, a thin wrapper over any API**. The idea: don't cram millions of tokens into
the window, but keep them OUTSIDE and let the model dig through them programmatically.

## How it works

The long input is placed into a variable (`context`) in a **Python REPL** sandbox. The root model
(depth 0) keeps only the short task in its window and writes code to:

- **peek / grep / partition / map** — peek in, search with a regex, slice up, iterate;
- **recursively call a sub-LLM** on the relevant chunk — and only on it.

The sub-call's response comes back as a variable in the REPL, and is NOT automatically poured into
the parent's context. The root assembles the final answer from the results. Essentially an
"out-of-core algorithm for text": the way a database works with data larger than RAM, RLM works
with context larger than the window.

The key difference from its neighbors: **no summarization and no compression** (meaning no
information loss, which compaction is guilty of) and **no indexing ahead of time** (unlike RAG).
The model decides for itself what to read and when.

## Why it matters (verified numbers)

- Holds input **up to 2 orders of magnitude (100×) past the model's window** — tens to hundreds of
  millions of tokens; stable at **10M+** with no degradation.
- **RLM(GPT-5-mini) beats GPT-5** on OOLONG (the toughest long-context benchmark) by 2×+ on
  correct answers — and cheaper per request.
- OOLONG-Pairs (density grows quadratically): GPT-5 — F1 <0.1%, RLM — **58%**. CodeQA: 24% →
  **62%**. On BrowseComp-Plus, RLM is up to **3× cheaper** than the summarizing baseline.

The authors' moral: "The model's intelligence is no longer the bottleneck. The bottleneck is the
inference harness." This is exactly about the harness.

## How to apply it

- **Ready-made:** LangChain **Deep Agents** have built-in RLM support; there's an implementation
  for **Google ADK**; Prime Intellect calls RLM "the paradigm of 2026" and trains for it.
- **Vibe-code:** the wrapper is thin — a REPL with a `context` variable plus a function for
  recursively calling a sub-LLM. Works on top of any API (in the paper — GPT-5 / GPT-5-mini /
  Qwen3-Coder).

## Place in the stack

RLM is NOT memory and not storage (don't confuse it with the RAG vector from `agent-memory`). It's
a technique for managing **context**: kin to compaction and hooks, a branch of the `agent-harness`
route. You reach for it when the task hits a wall on LENGTH — giant codebases, deep research across
a thousand documents, multi-hour logs, long-horizon reasoning — and the window and compaction are
already lying to you.
