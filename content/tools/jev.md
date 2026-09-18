---
id: jev
name: Jev — connect the TypeSafe decision API
summary: >-
  Connect Jev as a typed decision service beside an existing model: HTTP contract,
  Choice/Score/Noul, credentials, official agent skill, model pinning, usage and
  failure handling. Based on KISA's Pi, Hermes and local-model integrations.
type: tool
author: third_party
recommended: false
added: 2026-09-18
tags: [jev, typesafe, system-one, api, local-llm, agents, evaluation, browser-use]
source: https://docs.typesafe.ai/api
---

# Jev — connect the TypeSafe decision API

**Checked September 18, 2026.** TypeSafe AI develops Jev. KISA's integration
experience is in `jev-in-agent-pipelines`; the practical route is
`jev-integration`. This item explains connection, not an installation of our
private Pi or Hermes setup.

## Choose the interface

Jev accepts application state and typed questions. It returns decisions your
application consumes. Keep the existing LLM for prose, code and field values;
call Jev through a separate adapter. It is a hosted service, not downloadable
local weights or a drop-in chat-completions model. See the
[introduction](https://docs.typesafe.ai/introduction).

Apply `tailored-install` before changing a user's environment. Identify the
actual host, selected model, tool loop, secret store and existing HTTP client.
One HTTP request is enough to begin; no new agent framework is required.

## One request, three kinds of decision

The endpoint is `POST https://api.typesafe.ai/v1/systemone`, with a bearer key.
The request carries `model`, `state` and `questions`; the response contains
`answers`, `model` and `usage`. Answers retain your question IDs. IDs are lookup
keys, not instructions visible to the model: put the full question in
`instructions`. [HTTP contract](https://docs.typesafe.ai/api)

Provision `TYPESAFE_API_KEY` in the host's private environment or secret store.
Do not paste it into agent context, tracked configuration or a browser client.
The following command makes a billable request **only when you run it**:

```bash
curl --fail-with-body --silent --show-error --max-time 20 \
  https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H 'Content-Type: application/json' --data-binary @- <<'JSON'
{
  "model": "jev-1.13.0",
  "state": {
    "request": "Compare the current stable releases of two libraries.",
    "draft": "Both releases were checked and have identical features.",
    "opened_sources": [],
    "tool_results": []
  },
  "questions": {
    "next_step": {
      "type": "choice",
      "instructions": "Which next step fits the request and available evidence?",
      "criteria": {
        "research": "Current external facts are needed and evidence is missing.",
        "answer": "The supplied evidence supports the requested comparison.",
        "clarify": "The libraries or requested comparison are not identified."
      }
    },
    "supported": {
      "type": "noul",
      "instructions": "Do the supplied tool results substantiate the draft's claim that both releases were checked?"
    },
    "coverage": {
      "type": "score",
      "instructions": "How much of the requested comparison does the draft cover?",
      "criteria": [
        "No concrete comparison is supplied.",
        "Some requested differences are explained; material gaps remain.",
        "All requested differences and relevant limitations are explained."
      ]
    }
  }
}
JSON
```

Inspect `answers.next_step.choice`, `answers.supported.noul` and
`answers.coverage.score`. This is a deliberately incomplete task: identifying
the missing library names and detecting the unsupported verification claim
are separate judgments. Do not hard-code one expected route as a universal
model guarantee.

Choice includes option probabilities and confidence. Score also includes
`legend`; this three-level rubric yields a score between 0 and 2. Noul is a
probability between 0 and 1 and has no separate confidence field.
[Choice](https://docs.typesafe.ai/primitives/choice),
[Score](https://docs.typesafe.ai/primitives/score),
[Noul](https://docs.typesafe.ai/primitives/noul)

## Validate before consuming

At the adapter boundary, require every requested answer and its matching type.
Reject missing fields, booleans masquerading as numbers, NaN/infinity,
out-of-range values and unknown choices. For Choice/Score, validate the complete
distribution and its near-unit sum; for Score, check the rubric's range and
legend. Preserve the provider's actual model and usage alongside the result.

Use a finite timeout and a small total attempt budget. Fix `401` credentials and
`422` request errors instead of repeating them. Back off for `429` and `529`;
account for SDK retries so an outer retry loop does not multiply calls.
[Error contract](https://docs.typesafe.ai/api)

Return an explicit `unavailable` or `invalid_response` result when evaluation
fails. Do not substitute a passing probability. The host then applies the
text-versus-action failure policy in `jev-in-agent-pipelines`.

## Version, limits and cost

At the checked date, the model page lists `jev-1.13.0`; `jev-latest` and
`jev-preview` resolve to it. Pin a version when comparing rubrics or thresholds.
The documented price is **$0.042 per million input tokens**, with free output
tokens. Limits are **64K tokens per entire request** and **32K for state plus
the longest question**. Inputs are text/JSON, without native image, audio or
video support. Posted limits of 1,200 requests/minute and 250,000 tokens/second
are explicitly changeable. Verify current account limits before sizing a job.
[Models](https://docs.typesafe.ai/models)

For example, 2,000 input tokens cost about $0.000084 at that rate. Retries and
extra evaluations add calls; search, browser hosting and the text model have
their own costs. Record actual `usage`, not an assumed constant request size.

The launch article reports 70–500 ms and large speedups on selected workloads.
Those are vendor measurements with geographic and benchmark qualifications,
not a guarantee for our complete agent loop.
[Launch article, September 15](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

## Give the builder the official skill

The official skill documents API shapes and integration patterns. For a
supported agent, the documented installer is:

```bash
npx skills add typesafe-ai/skills --skill typesafe-ai
```

Inspect the source and select the intended agent/project; keep one installed
copy. A manual installation includes the skill's reference directory, not just
`SKILL.md`. Claude Code also has a documented plugin installation path.
[Official skill instructions](https://docs.typesafe.ai/agent-skill)

This gives the **builder** knowledge of Jev. It does not automatically attach
an evaluator to Pi, Hermes, Codex or another runtime. Connect the runtime's
actual hooks or tools explicitly. When the task is to grade a local model,
keep evaluator setup instructions out of that model's task prompt; this
separation was a concrete repair in KISA's sessions.

## Connection acceptance check

1. Validate saved valid and malformed responses offline; no API key is needed.
2. Confirm host access and the selected local model's health independently.
3. Run one authorized Jev request; capture answer types, elapsed time and usage.
4. Simulate an unavailable evaluator and check the configured fallback.
5. Verify the chosen runtime consumes the result without changing the user's
   task. A registered skill or MCP tool alone does not prove this.

Then continue with `next_step("jev-integration:4")` for observation mode.
