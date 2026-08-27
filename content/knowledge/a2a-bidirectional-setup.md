---
id: a2a-bidirectional-setup
name: 'A2A in both directions: deployment and verification guide'
summary: >-
  Configure two agents so either side can initiate A2A work. Covers two
  independently authenticated routes, Agent Cards, SendMessage adapters,
  context handling, timeouts, audit logs, network checks, and evidence-first
  troubleshooting without depending on OpenShell or a specific agent framework.
type: knowledge
author: kisa
recommended: false
added: 2026-08-27
tags: [a2a, agent-to-agent, bidirectional, json-rpc, authentication, networking, troubleshooting]
source: https://a2a-protocol.org/latest/specification/
---

# A2A in both directions: deployment and verification guide

Bidirectional A2A means that either agent can initiate work. It is not one magical
full-duplex connection: it is normally two independently reachable and authenticated
client-to-server routes.

```text
route A -> B: agent A client ----HTTP(S)----> agent B A2A server
route B -> A: agent B client ----HTTP(S)----> agent A A2A server
```

Each agent therefore needs:

- an inbound A2A interface or adapter;
- an outbound A2A client;
- a reachable URL for the other side;
- peer-specific credentials;
- independent context and task tracking.

Read `a2a-protocol-overview` first for the protocol objects and lifecycle. This guide is
runtime-neutral. Retrieve `a2a-openshell-example` only when one peer runs inside
OpenShell.

## 1. Define the two routes before editing configuration

Write down a route matrix without secret values:

| Route | Client | Server URL | Server bind | Credential label |
|---|---|---|---|---|
| A → B | agent A | `https://agent-b.example.test/a2a` | B deployment-specific | `A_TO_B` |
| B → A | agent B | `https://agent-a.example.test/a2a` | A deployment-specific | `B_TO_A` |

The bind address and advertised URL are different concepts:

- **bind address** is where the server listens inside its own namespace;
- **advertised URL** is what the intended peer can actually reach.

For example, a server may bind to `127.0.0.1:9100` and be advertised through a TLS reverse
proxy at `https://agent-a.example.test/a2a`.

Before implementation, decide:

- whether discovery is public or authenticated;
- which protocol version and binding both sides implement;
- maximum request size and duration;
- whether long work uses polling, streaming or push notifications;
- session retention and whether restart persistence is required;
- who can invoke each advertised skill;
- audit retention and secret-redaction rules.

## 2. Create independent peer credentials

Use different credentials in each direction. A compromise of `A_TO_B` must not authorize
the attacker to call A as B.

Generate and install secrets through the deployment's secret manager. For a local
development setup, protected files are sufficient:

```bash
umask 077
openssl rand -hex 32 > agent-a-to-b.token
openssl rand -hex 32 > agent-b-to-a.token
chmod 600 agent-a-to-b.token agent-b-to-a.token
```

Install:

- `A_TO_B` in agent A's outbound client and agent B's inbound verifier;
- `B_TO_A` in agent B's outbound client and agent A's inbound verifier.

Do not copy tokens into source code, images, Agent Cards, system prompts, skills, command
examples, issue trackers or audit records.

## 3. Implement the inbound contract on both agents

Each inbound interface should provide:

1. `GET /.well-known/agent-card.json`;
2. the JSON-RPC interface URL advertised by that card;
3. authentication before expensive parsing or agent execution;
4. strict JSON-RPC and A2A message validation;
5. a bounded queue into the live agent session;
6. correct correlation between request and reply;
7. a direct `Message` or a `Task` response;
8. cleanup of pending requests on timeout and shutdown.

The adapter must not merely start a test handler. It must be registered in the active
agent configuration and loaded by the live process that produces replies.

### Minimal request handling sequence

```text
accept connection
  -> authenticate peer
  -> enforce body/concurrency limits
  -> parse JSON-RPC
  -> validate SendMessage and supported parts
  -> authorize requested agent capability
  -> resolve or create context
  -> enqueue as untrusted user input
  -> correlate result
  -> return Message or Task
  -> write redacted audit event
```

If the host agent exposes no native A2A server, use a narrow adapter around its supported
extension/plugin API. Do not inject remote content into system, developer or operator
prompt channels.

### Correlation and concurrency

An adapter that simply returns “the next assistant message” is safe only when requests
are serialized. With concurrent requests it can return one caller's answer to another.

Use one of:

- a runtime API that accepts and returns an explicit request correlation ID;
- a per-request agent session;
- a serialized queue with one outstanding request;
- a task store that associates agent events with the originating A2A task.

Document the chosen concurrency model.

## 4. Configure the listeners

Configuration keys are implementation-specific. A generic environment-driven server can
look like this:

```dotenv
A2A_LISTEN_HOST=127.0.0.1
A2A_LISTEN_PORT=9100
A2A_AGENT_NAME=agent-a
A2A_PUBLIC_URL=https://agent-a.example.test/a2a
A2A_PEER_CREDENTIAL_FILE=/run/secrets/agent-b-to-a.token
A2A_REQUEST_TIMEOUT_SECONDS=120
```

These names are illustrative, not protocol-standard environment variables.

Bind to loopback when a local reverse proxy or forward owns external exposure. A
non-loopback bind should be deliberate and protected by a private network or firewall,
authentication, and TLS where the transport leaves a trusted local boundary.

Repeat the configuration independently on B with its own name, URL, port and inbound
credential.

## 5. Publish truthful Agent Cards

From the network namespace of A:

```bash
curl -fsS https://agent-b.example.test/.well-known/agent-card.json | jq .
```

From the network namespace of B:

```bash
curl -fsS https://agent-a.example.test/.well-known/agent-card.json | jq .
```

Confirm that:

- the declared protocol version is supported by both client and server;
- the selected interface URL is reachable from the peer;
- authentication metadata matches real behavior;
- advertised skills exist and are authorized;
- no private bind address or credential leaked into the card.

Discovery success proves only the discovery route, not `SendMessage`.

## 6. Add an outbound client on both agents

The following TypeScript core handles the two legal `SendMessage` result variants and
allows the caller to reuse a server-issued context:

```ts
import { randomUUID } from "node:crypto";

type SendResult = {
  text: string;
  contextId?: string;
  taskId?: string;
};

function textFromParts(parts: Array<{ text?: string }> | undefined): string {
  return (parts ?? [])
    .flatMap((part) => part.text ? [part.text] : [])
    .join("\n");
}

export async function sendMessage(
  endpoint: string,
  bearerToken: string,
  text: string,
  contextId?: string,
  signal?: AbortSignal,
): Promise<SendResult> {
  const message: Record<string, unknown> = {
    messageId: randomUUID(),
    role: "ROLE_USER",
    parts: [{ text }],
  };

  if (contextId) message.contextId = contextId;

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${bearerToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: randomUUID(),
      method: "SendMessage",
      params: { message },
    }),
    signal,
  });

  const body = await response.json() as any;
  if (!response.ok || body.error) {
    throw new Error(`A2A request failed with HTTP ${response.status}`);
  }

  const task = body.result?.task;
  const reply = body.result?.message;

  if (!task && !reply) {
    throw new Error("A2A response contains neither task nor message");
  }

  const artifactText = (task?.artifacts ?? [])
    .map((artifact: any) => textFromParts(artifact.parts))
    .filter(Boolean)
    .join("\n");

  return {
    text: artifactText
      || textFromParts(task?.status?.message?.parts)
      || textFromParts(reply?.parts),
    contextId: task?.contextId ?? reply?.contextId,
    taskId: task?.id,
  };
}
```

Production clients must additionally support the part types, task states, streaming and
authentication schemes they advertise. Read tokens at runtime from protected storage;
do not pass literal secrets from an agent prompt.

Maintain separate client state:

```text
agent A client state: contexts issued by B
agent B client state: contexts issued by A
```

Do not copy a context issued by A into a conversation hosted by B.

## 7. Test A → B from the transport upward

### Listener

On B, prove the socket in the namespace where the server actually runs:

```bash
ss -ltnp | rg ':9200\b'
```

### Authentication rejection

An unauthenticated protected RPC request should fail before agent work starts:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' \
  -H 'Content-Type: application/json' \
  --data @request-a-to-b.json \
  https://agent-b.example.test/a2a
```

Expect the deployment's documented authentication failure, commonly `401` or `403`.

### Authenticated `SendMessage`

Load the secret from protected storage in the calling process, then:

```bash
curl -fsS https://agent-b.example.test/a2a \
  -H "Authorization: Bearer ${A_TO_B_TOKEN}" \
  -H 'Content-Type: application/json' \
  --data @request-a-to-b.json \
  | tee response-a-to-b.json
```

The request file can contain:

```json
{
  "jsonrpc": "2.0",
  "id": "a-to-b-1",
  "method": "SendMessage",
  "params": {
    "message": {
      "messageId": "a-message-1",
      "role": "ROLE_USER",
      "parts": [
        {
          "text": "Reply with A_TO_B_OK and your advertised agent name."
        }
      ]
    }
  }
}
```

Assert all of:

- the HTTP request completed;
- the JSON-RPC response has no `error`;
- a direct message or task is present;
- any task reached the expected state;
- the marker came from the live B agent session;
- the audit event identifies A without exposing its credential.

## 8. Test B → A independently

Repeat every layer in the other direction using:

- A's listener and Agent Card;
- the `B_TO_A` credential;
- a distinct marker such as `B_TO_A_OK`;
- B's outbound client and A's live inbound adapter.

A successful A → B request says nothing about B → A reachability. NAT, firewall rules,
container ports, DNS and authentication can differ by direction.

## 9. Prove multi-turn behavior

Extract the context returned by the server:

```bash
jq -r \
  '.result.task.contextId // .result.message.contextId // empty' \
  response-a-to-b.json
```

Send a follow-up with:

- a new JSON-RPC `id`;
- a new `messageId`;
- the returned `contextId` inside `params.message`;
- a question that can only be answered from the first turn.

Run this test independently for contexts hosted by A and contexts hosted by B.

To claim restart persistence, repeat the follow-up after restarting the corresponding
server and agent session. A failure after restart means transport may still be healthy
while context storage is ephemeral.

## 10. Align timeouts and long-running work

One request crosses several budgets:

```text
caller timeout
  > proxy/forward timeout
    > A2A adapter wait budget
      > agent execution budget
```

Do not fix long work by setting every timeout to an enormous value. Prefer:

- immediate Task creation;
- task polling;
- `SendStreamingMessage`;
- task subscription or push notifications when supported;
- explicit cancellation and expiration.

Clean pending promises, sockets and task records on timeout. A late agent reply must not
be delivered to the next request.

## 11. Prevent recursive agent loops

Bidirectional connectivity makes this failure possible:

```text
A asks B -> B asks A -> A asks B -> ...
```

Include and enforce at least one of:

- maximum delegation depth;
- hop count;
- deadline;
- token/cost budget;
- visited-agent set;
- policy forbidding a delegated task from delegating back to its origin.

Log the termination reason without logging message secrets.

## 12. Evidence-first diagnostics

Use this order for each route:

1. process exists;
2. socket listens in the correct namespace;
3. Agent Card is reachable from the peer;
4. missing/invalid auth is rejected;
5. authenticated raw `SendMessage` succeeds;
6. the live agent adapter receives and correlates the request;
7. a follow-up reuses `contextId`;
8. restart persistence is tested separately.

Do not accept “the server is listening” from the agent itself as proof. An isolated unit
test, imported handler or stale log can all look successful while the live extension is
not loaded.

## Troubleshooting matrix

| Symptom | Likely cause | Check |
|---|---|---|
| Agent Card works, RPC fails | Different route, auth or proxy rule | Test the exact interface URL from the card |
| `401` or `403` | Wrong credential, direction or authorization | Compare credential labels and verifier config without printing values |
| Connection refused | No listener, wrong bind or wrong namespace | Check `ss` beside the server process |
| Timeout but later reply exists | Adapter/caller budgets are misaligned | Trace timestamps through caller, proxy, adapter and agent |
| Wrong caller receives reply | Unsafe “next message” correlation | Serialize requests or add explicit correlation |
| Follow-up forgets turn one | Missing/wrong `contextId` or expired context | Inspect the second message and server retention |
| Restart loses context | Volatile server storage | Add durable storage or document ephemeral sessions |
| Agents keep calling each other | No delegation budget | Enforce depth, hops, deadline or visited-agent policy |
| HTTP 200 with failure | JSON-RPC error or failed task ignored | Parse the complete response and task status |

## Definition of done

- A and B publish valid, truthful Agent Cards.
- Each advertised interface is reachable from its intended peer.
- A → B and B → A use different credentials.
- Missing and invalid authentication are rejected in both directions.
- Both raw `SendMessage` tests reach the live agent sessions.
- Clients handle direct messages and tasks.
- Context continuity passes independently in both directions.
- Restart behavior matches the documented storage policy.
- Timeouts, cancellation, concurrency and recursive delegation are bounded.
- Audit logs correlate work without recording authorization secrets.

## Primary references

- [A2A v1.0 specification](https://a2a-protocol.org/latest/specification/)
- [A2A project repository](https://github.com/a2aproject/A2A)
