---
id: jev-integration
name: Add Jev to an agent or pipeline
summary: >-
  A seven-step route from understanding System One decisions to one measured Jev
  integration: define the contract, connect the API, observe independently, add
  bounded feedback or routing, handle browser execution separately and verify
  outage behavior before rollout.
type: route
author: kisa
recommended: false
added: 2026-09-18
tags: [jev, typesafe, system-one, leveling-up, agents, pipelines, pi, hermes, research, browser-use]
steps:
  - title: Understand decisions, generation and confidence
    action: read
    ref: jev-in-agent-pipelines
    body: >-
      Read the primitives and KISA's case table. Explain which part of your task
      requires generated text, which is a bounded semantic decision, and which
      belongs in deterministic code. Exit criterion: distinguish a valid output
      type, a confident judgment and a verified task outcome.
  - title: Choose one decision and define its evidence
    action: configure
    ref: jev-in-agent-pipelines
    body: >-
      Pick one existing branch: answer grading, research checks, document triage
      or tool routing. Define the host-owned state, atomic questions, allowed
      outputs, missing-evidence behavior and failure policy. Exit criterion: a
      few labeled success, failure and ambiguous examples, with no dependency on
      a new framework. Follow tailored-install for the actual runtime.
  - title: Connect and validate the TypeSafe API
    action: configure
    ref: jev
    body: >-
      Keep credentials on the host; pin a model and validate response shapes
      offline first. If useful, give the integration builder the official skill.
      With API access and a run budget, make one live request and record elapsed
      time, model identity and usage. Exit criterion: a real parsed decision plus
      an explicit unavailable result for a failed evaluation.
  - title: Attach an independent observer
    action: configure
    ref: jev-in-agent-pipelines
    body: >-
      Review the completed request, answer and actual tool evidence through the
      runtime's lifecycle hook or a manual command. Store scores outside the
      worker's conversation. Exit criterion: the worker continues its original
      task and does not start configuring Jev. For the recorded Pi research
      extension, select observe explicitly; its installed default is correct.
  - title: Add one bounded feedback or routing path
    action: configure
    ref: jev-in-agent-pipelines
    body: >-
      Choose the useful branch for your project. For research, evaluate tool
      selection, opened sources, coverage, citations and usage; map failed checks
      to host-written feedback with at most two final-answer corrections. For a
      pipeline, route only to existing handlers. Exit criterion: one known bad
      case is caught, a good case passes, and an unchanged answer is not billed
      repeatedly. Missing evaluation never becomes a passing result.
  - title: Add browser execution only if the task needs it
    action: configure
    ref: jev-in-agent-pipelines
    body: >-
      Otherwise skip this step. Choose an isolated browser executor or a guard
      around an existing browser bridge. Map Jev's choices to freshly observed
      elements; leave field text to the local model and permissions to the host.
      Set step/time limits and verify the observed outcome after DONE. Record
      browser authentication separately from Jev availability; perform any live
      UI check only with the user's required authorization.
  - title: Qualify failures, tune thresholds and retain rollback
    action: verify
    ref: jev-in-agent-pipelines
    body: >-
      Check timeouts, invalid responses, missing evidence, stale reviews and the
      correction ceiling. Preserve ordinary text with a not-checked marker when
      optional review is unavailable; retain required gates for side effects.
      Compare held-out cases and baseline task latency/cost, then enable only the
      useful path. Exit criterion: documented thresholds, honest verification
      limits and a tested way to disable the optional evaluator.
---

# Add Jev to an agent or pipeline

The destination is **one useful, measured decision point** inside an existing
system. KISA's Pi, Hermes and local-model work supplies both the examples and
the failure cases. You do not need to reproduce all of those environments.

Start with `onboard("integrate Jev into my agent pipeline")` or call
`next_step("jev-integration:1")`, then follow `next_step_id`. The client keeps
progress. The full material is in `jev-in-agent-pipelines`; API setup is in
`jev`.

## Choose the branch that matches the job

- **Independent evaluator:** complete steps 1–4 and 7; leave the worker's
  conversation untouched.
- **Research or application pipeline:** also complete step 5 with one explicit
  rubric and correction/routing policy.
- **Browser work:** add step 6 after the observer works. Distinguish the browser
  driver, Jev decision service and local text model before testing a full task.

On a new runtime, reuse the design rather than copying hook names blindly.
Moving MCP tools or skill files does not move the evaluator's lifecycle hooks.
Use `tailored-install` to identify the actual extension mechanism.

## What counts as done

The agent still solves the user's original task; valid and invalid decisions
are handled explicitly; the evaluation catches a demonstrated class of error;
request cost and added latency are recorded. An evaluator outage preserves
ordinary text with an honest marker while required action checks remain in
force. No success claim depends only on a score or a browser's DONE label.

Roll out after the comparison, not just after the API returns HTTP 200. If the
observer adds no useful signal, leave it off and keep the baseline.
