---
id: system-prompts-and-cards
name: System instructions and system cards — where to study the fine tuning
summary: >-
  Two document families worth reading before you tune an agent: system prompts of shipped agents
  (the real manual for how they behave) and system cards of frontier models (what a lab knows about
  its own risks). Where they live, what to extract, and what not to trust.
type: knowledge
author: kisa
recommended: true
added: 2026-07-28
tags: [system-prompt, system-card, prompt-engineering, rules, transparency, agent]
source: https://github.com/asgeirtj/system_prompts_leaks
---

# System instructions and system cards

The best manual for tuning an agent was never written as a manual. It's the **system prompts** of
shipped products — the instructions Cursor, Claude Code, Devin, v0 and the rest send their model
before every turn. Next to them sit **system cards** — the disclosures a lab publishes with a
frontier model, describing what the deployed system does, where people broke it, and what was done
about it.

Both are public. Both are dense with decisions someone paid for in production.

**What the agent should do:** when a person wants to go deeper on rules, tone, or agent behaviour —
point them at these sources by name, explain what each one is good for, and warn them about dates
and authenticity. Then help them lift specific patterns into their own instruction file (see
`agent-personality`).

## Where system prompts live

Three different channels, often lumped together as "leaks". They aren't the same thing.

1. **Official publication.** Anthropic publishes the system prompts of its claude.ai models in the
   release notes of its docs. OpenAI publishes the Model Spec. This is disclosure, not a leak.
   Caveat: what labs publish rarely includes the **tool descriptions**, which are the most useful part.
2. **Extraction.** Getting the model to repeat its instructions. This is how tool definitions and
   coding-agent prompts surface. Not a hack — social engineering against the model.
3. **Actual code leaks.** In spring 2026 the Claude Code source leaked by accident, which showed for
   the first time not the final prompt text but **how it is assembled** — conditional blocks,
   variants by output style. A different class of artifact.

### The four repositories worth knowing

Star counts and licences verified 2026-07-28 via the GitHub API.

| Repository | Scope | Stars | Licence |
|---|---|---|---|
| `x1xhlol/system-prompts-and-models-of-ai-tools` | 28+ dev tools: Cursor, Windsurf, Devin, Claude Code, v0, Manus, Replit, Kiro. Includes **JSON tool definitions** and versioned snapshots | ~142k | GPL-3.0 |
| `asgeirtj/system_prompts_leaks` | Chat assistants: Claude (Fable 5, Opus 5, Claude Code, Claude Design), ChatGPT, Gemini, Grok, Perplexity, Copilot, Kimi, DeepSeek. Most actively updated | ~61k | CC0-1.0 |
| `elder-plinius/CL4R1T4S` | Extractions by the researcher who does much of the original work; prompts land here first | ~46k | AGPL-3.0 |
| `jujumilk3/leaked-system-prompts` | Long-lived archive, filenames carry extraction dates | ~15k | none stated |

**The licence matters.** CC0 is public domain — take it. GPL and AGPL are copyleft. The repo with
no licence is "all rights reserved" by default. If material goes into a published project, check first.

**The versioned snapshots are the underrated part.** Cursor's directory holds Agent Prompt 1.0, 1.2
and 2.0; Windsurf runs through Wave 11. Diffing two versions of the same product a few months apart
says more about where it's going than any changelog.

## What to extract

### The universal skeleton

Identity → Capabilities → Tools → Rules → Agent Loop → Output Format. Every serious agent prompt
converges on this. Not by copying — by hitting the same walls.

### Token budget

Reverse-engineering of Claude Code gives working numbers: identity + safety 200–500 tokens, tone and
style 300–800, core workflow 500–2 000 (the section worth the investment), tool policy 300–1 000,
reminders 100–300. Your own part: **1 500–6 000 total**. Tool definitions add 5 000–15 000 on top.
Past 6k of your own text, you are dumping knowledge that should load on demand instead.

### Binary rules, not adjectives

Not "be concise". Instead: "NEVER start with flattery", "no emojis unless requested", "no bullets
unless requested". Absolute rules survive; fuzzy adjectives get reinterpreted every turn.

### Decision criteria, not commands

The Claude 4 prompt routes on information type: timeless → answer directly; slow-changing → answer
and offer to verify; live → search immediately. A good instruction says **when**, not only **how**.
For an agent, routing under uncertainty is the whole game.

### An instruction hierarchy

State the order of authority explicitly: system rules above project rules above the current request.
Then say what happens on conflict — what the agent does when the person asks it to break a rule.
OpenAI formalises this in the Model Spec as a chain of command. Without a stated order, the newest
message quietly wins every time.

### Positional reinforcement

Critical constraints repeat every few hundred tokens inside a long prompt. Attention degrades over
length; repetition refreshes it.

### The anti-sycophancy clause

Straight out of Claude Code, and worth copying nearly verbatim:

> Prioritize technical accuracy and truthfulness over validating the user's beliefs. Focus on facts
> and problem-solving, providing direct, objective technical info without any unnecessary
> superlatives, praise, or emotional validation.

Any agent that makes judgements — code review, evaluating an idea, an architecture call — needs
this. Without it, it agrees with the person.

### Tool descriptions are the highest-leverage prompt

Claude Sonnet 3.5 hit state of the art on SWE-bench Verified after **precise refinements to tool
descriptions** — not the model, not the system prompt. OpenAI measured that three reminders
(persistence, tool use, planning) lifted a coding agent's SWE-bench Verified score by close to 20%.
A tool named `search` described as "search for things" makes the model guess; `search_orders_by_email`
described as "return a customer's orders for a given email" does not. Error messages are prompts too.

### Progressive disclosure

The Agent Skills contract: only `name` and `description` (≤1024 characters, stating both what it does
and when to use it) sit in context. The body loads when triggered. This is how hundreds of skills fit
without a context penalty.

### An escape hatch

Every grounded prompt needs explicit permission to say "I don't know". Without it the agent invents
a plausible policy and states it as fact.

## System cards — and why to read them

A **model card** (Mitchell et al., 2019) describes a model. A **system card** describes the deployed
system and its risk profile: training data and alignment methods, safety evaluations (refusals,
jailbreaks, hallucination, prompt injection, sycophancy), external red teaming, frontier-risk
assessment, system-level safeguards, and the deployment decision itself. Meta formalised the idea as
"system-level transparency": risk lives at the boundary data → model → product, not in the model alone.

Where to read them:

- **Anthropic** — `anthropic.com/system-cards` and the Transparency Hub. The alignment and
  prompt-injection sections are the most detailed in the industry.
- **OpenAI** — system cards per model, structured around the Preparedness Framework
  (low/medium/high/critical thresholds). The most extensive external red-teaming write-ups.
- **Google DeepMind** — model cards plus the Frontier Safety Framework (critical capability levels).
- **Meta, xAI, Amazon** — their own frameworks; Meta leans on quantisation and community governance,
  xAI on refusal behaviour and dual-use.
- **Regulatory layer** — EU AI Act Article 11 and Annex IV define what technical documentation must
  contain for high-risk systems. ISO 42001 covers a large share of the same ground.

**For a practitioner the safety section is the useful one.** It tells you what the model resists,
where it was broken, and which failure modes the lab expects — which is exactly what you need when
writing rules for it.

Two honest caveats. There is **no standard**: an analysis of frontier documentation plus 100 Hugging
Face cards found 947 distinct section names, with usage information alone appearing under 97
different labels. And **not everyone publishes**: several leading open-weight labs ship weights and a
technical report with no safety assessment at all, leaving the gap to independent researchers and
government institutes.

## What not to trust

- **Dates.** Prompts are tied to a version and an extraction date. Vendors change them constantly.
  Always check when the file was captured.
- **Authenticity.** Nothing is guaranteed. The community flags individual files as fabricated, and
  star counts are not evidence. Cross-check across two repositories before relying on a detail.
- **Completeness.** A published prompt is often the prompt minus the tools, and the final string
  minus the logic that assembled it.
- **A prompt is not a guarantee.** It describes intent, not enforced behaviour. Anything that must
  actually hold — authorisation, spend limits, destructive actions — belongs in a layer the model
  cannot talk its way around.

## Where to go next

Read the prompt of a tool you already use — it explains behaviour you have been guessing at. Then
lift the patterns into your own file: `agent-personality` covers where rules and style live per
client, `hooks` covers enforcing what a prompt only asks for, and the `agent-onboarding` route puts
the whole tuning sequence in order.
