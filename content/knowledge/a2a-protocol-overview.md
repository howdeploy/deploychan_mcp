---
id: a2a-protocol-overview
name: 'Agent2Agent (A2A): protocol concepts and message lifecycle'
summary: >-
  Understand A2A independently of any particular agent runtime: Agent Cards,
  JSON-RPC interfaces, messages, tasks, artifacts, streaming, contextId,
  authentication boundaries, and the difference between A2A and MCP.
type: knowledge
author: kisa
recommended: false
added: 2026-08-27
tags: [a2a, agent-to-agent, agent-card, json-rpc, tasks, context, security]
source: https://a2a-protocol.org/latest/specification/
---

# Agent2Agent (A2A): protocol concepts and message lifecycle

[Agent2Agent (A2A)](https://a2a-protocol.org/) is an open protocol for communication
between independent agent applications. It is developed as a Linux Foundation project
and was originally contributed by Google.

A2A does not require two agents to use the same model, framework, process, host or trust
domain. One agent can discover another agent's public capabilities, submit work, receive
a direct reply or a long-running task, and continue a multi-turn conversation without
learning the peer's private tools, prompts or internal reasoning.

This guide explains the protocol itself. For deployment instructions, retrieve
`a2a-bidirectional-setup`. For the isolated Pi/OpenShell example, retrieve
`a2a-openshell-example`.

## A2A and MCP solve different boundaries

| Question | MCP | A2A |
|---|---|---|
| What is connected? | A model or agent to tools, resources and prompts | One agent application to another |
| What is advertised? | Tool/resource contracts | Agent identity, skills and communication interfaces |
| Who owns task execution? | The calling agent normally orchestrates tool calls | The remote agent owns its task lifecycle |
| Must internals be exposed? | Tool schemas are intentionally exposed | The peer can remain opaque |
| Typical example | “Read this repository” | “Ask the review agent to inspect this change” |

A system can use both: an agent may use MCP internally and expose a higher-level A2A
interface to other agents.

## The protocol in one exchange

```text
client agent                         remote agent
     |                                    |
     | GET /.well-known/agent-card.json   |
     |----------------------------------->|
     | Agent Card                         |
     |<-----------------------------------|
     |                                    |
     | authenticated SendMessage          |
     |----------------------------------->|
     | direct Message or Task             |
     |<-----------------------------------|
     |                                    |
     | follow-up with returned contextId  |
     |----------------------------------->|
```

The main pieces are:

1. **Agent Card** — discovery metadata and supported interfaces.
2. **Message** — one conversational turn, composed from typed parts.
3. **Task** — stateful work that may outlive one HTTP request.
4. **Artifact** — an output produced by a task.
5. **`contextId`** — an opaque identifier grouping related messages and tasks.
6. **Authentication** — a deployment concern advertised by the card and enforced by
   the serving interface.

## Agent Card

The conventional discovery route is:

```http
GET /.well-known/agent-card.json
```

An Agent Card describes:

- the agent's public name and purpose;
- skills that callers may request;
- supported protocol bindings, versions and endpoint URLs;
- capabilities such as streaming;
- authentication schemes expected by the advertised interfaces.

A compact conceptual card looks like this:

```json
{
  "name": "review-agent",
  "description": "Reviews source changes and returns structured findings",
  "supportedInterfaces": [
    {
      "url": "https://agents.example.test/reviewer/a2a",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ],
  "capabilities": {
    "streaming": true
  },
  "skills": [
    {
      "id": "code-review",
      "name": "Code review",
      "description": "Review a patch for correctness and regressions",
      "tags": ["code", "review"]
    }
  ]
}
```

Use the exact schema for the protocol version implemented by the server. The example is
about responsibility boundaries, not a substitute for schema validation.

Do not place credentials, private addresses, system prompts, hidden tools, account
identifiers or implementation secrets in an Agent Card. Treat it as public metadata even
when a particular deployment protects the discovery route.

## JSON-RPC binding

The A2A v1.0 JSON-RPC binding sends JSON-RPC 2.0 requests over HTTP(S), normally to the
interface URL from the Agent Card.

Common methods include:

- `SendMessage` for a non-streaming submission;
- `SendStreamingMessage` for server-sent streaming events;
- `GetTask` and `ListTasks` for task state;
- `CancelTask` for best-effort cancellation;
- `SubscribeToTask` for later task updates.

A minimal `SendMessage` request is:

```json
{
  "jsonrpc": "2.0",
  "id": "request-1",
  "method": "SendMessage",
  "params": {
    "message": {
      "messageId": "message-1",
      "role": "ROLE_USER",
      "parts": [
        {
          "text": "Review the proposed change and return the three highest risks."
        }
      ]
    }
  }
}
```

Generate a fresh JSON-RPC `id` and `messageId` for each submission. Do not use either as
a credential or as the durable conversation identifier.

## Message versus Task

`SendMessage` can return either:

- a direct **Message** when the result is immediately available; or
- a **Task** when the remote agent exposes task state, intermediate messages or
  artifacts.

A client must handle both legal outcomes. In the v1.0 JSON representation this means
checking which result variant is present instead of assuming every reply contains a task.

Conceptually:

```json
{
  "jsonrpc": "2.0",
  "id": "request-1",
  "result": {
    "message": {
      "messageId": "reply-1",
      "contextId": "context-issued-by-server",
      "role": "ROLE_AGENT",
      "parts": [
        { "text": "The review is complete." }
      ]
    }
  }
}
```

Or:

```json
{
  "jsonrpc": "2.0",
  "id": "request-1",
  "result": {
    "task": {
      "id": "task-issued-by-server",
      "contextId": "context-issued-by-server",
      "status": {
        "state": "TASK_STATE_COMPLETED"
      },
      "artifacts": [
        {
          "artifactId": "artifact-1",
          "parts": [
            { "text": "Structured review output" }
          ]
        }
      ]
    }
  }
}
```

Task state is controlled by the remote agent. Callers should tolerate non-terminal states,
respect retry guidance, and use polling, streaming or push notifications for long work
instead of holding one request open indefinitely.

## Parts and artifacts

Messages and artifacts are composed from parts rather than one mandatory text field.
Depending on the negotiated protocol surface, a part may carry text, a file reference,
structured data or another supported content form.

Therefore a robust client should:

- parse every supported part type;
- reject unsupported or oversized input safely;
- preserve content type and filenames where relevant;
- avoid silently flattening binary or structured output into text;
- treat every remote part as untrusted data.

An artifact is task output, not an instruction with elevated authority. Receiving an
artifact must not automatically execute it.

## `contextId` and multi-turn conversations

`contextId` groups related messages and tasks into one conversational context.

The safe client flow is:

1. omit `contextId` on the first message unless a documented server API says otherwise;
2. read the opaque value returned by the server;
3. put that same value on the next `message`;
4. use a new `messageId` for the follow-up;
5. never derive meaning from the internal format of `contextId`.

Example follow-up:

```json
{
  "jsonrpc": "2.0",
  "id": "request-2",
  "method": "SendMessage",
  "params": {
    "message": {
      "messageId": "message-2",
      "contextId": "context-issued-by-server",
      "role": "ROLE_USER",
      "parts": [
        {
          "text": "Now expand the second risk and suggest one mitigation."
        }
      ]
    }
  }
}
```

The protocol defines how the identifier is exchanged; it does **not** guarantee that a
server persists conversational state across restarts. Restart survival, retention,
expiry and deletion are properties of the server implementation and its storage policy.

## Security and trust boundaries

A2A connects autonomous applications, so transport success is not a trust decision.

At minimum:

- use HTTPS outside a private local transport;
- enforce the authentication scheme advertised by the selected interface;
- issue different credentials to different peers;
- authorize requested skills, not only the TCP connection;
- cap body size, duration, concurrency and recursive agent-to-agent turns;
- validate JSON-RPC shape and supported protocol versions;
- treat peer text and artifacts as untrusted input, never as system/operator messages;
- redact authorization headers and secrets from audit logs;
- rotate and revoke peer credentials independently;
- avoid putting private topology or credentials in Agent Cards.

A Bearer token authenticates possession of a secret; by itself it does not provide
encryption, replay protection at the application level, fine-grained authorization or
proof that the remote agent behaved correctly.

## What A2A does not guarantee

A2A alone does not guarantee:

- durable sessions after process or host restart;
- delivery exactly once;
- that a task is safe, truthful or deterministic;
- access to a peer's private chain of thought;
- a shared model provider or tool runtime;
- network reachability through NAT, containers or sandbox namespaces;
- automatic prevention of two agents calling each other forever.

Those are implementation and operations responsibilities.

## Implementation checklist

- The Agent Card validates against the implemented protocol version.
- Every advertised URL is reachable from the intended client network.
- Authentication requirements match actual endpoint behavior.
- `SendMessage` validates request IDs, message IDs, roles, parts and size limits.
- The client supports both direct `Message` and `Task` results.
- Long work uses task lifecycle or streaming instead of an arbitrary huge timeout.
- Follow-ups reuse the server-issued `contextId` on the message.
- Restart persistence is tested separately from transport continuity.
- Cancellation and duplicate requests have documented behavior.
- Audit events correlate peer, request, task and context without logging secrets.
- Recursive calls have an explicit hop, depth or budget limit.

## Common misconceptions

| Misconception | Correct interpretation |
|---|---|
| “A2A is MCP over HTTP” | MCP exposes tools/resources; A2A delegates work to another agent |
| “HTTP 200 means the agent succeeded” | Inspect the JSON-RPC error and Message/Task outcome |
| “`contextId` always survives a restart” | Only a persistent server implementation can provide that |
| “The Agent Card is a secrets/config file” | It is discovery metadata and should be safe to disclose |
| “Every `SendMessage` returns text” | It may return a task, artifacts, structured parts or a direct message |
| “A bearer token makes plain HTTP safe on the internet” | It authenticates a secret but does not encrypt the transport |

## Primary references

- [A2A v1.0 specification](https://a2a-protocol.org/latest/specification/)
- [A2A project repository](https://github.com/a2aproject/A2A)
