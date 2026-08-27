---
id: a2a-openshell-example
name: 'A2A with Pi inside OpenShell: an isolated two-way example'
summary: >-
  Apply bidirectional A2A to a host agent and a Pi agent isolated by OpenShell
  and rootless Podman. Covers sandbox-to-host egress, a Pi inbound adapter,
  service forwarding, extension registration, nested network namespaces,
  nsenter diagnostics, and a concrete two-turn exchange.
type: knowledge
author: kisa
recommended: false
added: 2026-08-27
tags: [a2a, agent-to-agent, openshell, pi, sandbox, podman, networking, example]
source: https://docs.nvidia.com/openshell/latest/
---

# A2A with Pi inside OpenShell: an isolated two-way example

This is a concrete deployment example, not the general A2A explanation.

Retrieve:

- `a2a-protocol-overview` for Agent Cards, Messages, Tasks and `contextId`;
- `a2a-bidirectional-setup` for the runtime-neutral two-route deployment method;
- `openshell-pi-agent` for building and operating the Pi sandbox itself.

The example connects:

- a host-level agent with an A2A server and client; and
- a Pi coding agent inside an OpenShell sandbox backed by rootless Podman.

Every name, path, port and token below is generic. No model vendor, API provider,
personal skill, private prompt, account identifier or public IP is required.

## Topology

```text
host / VM network namespace
├─ host agent A2A server :9900
├─ OpenShell gateway (loopback + mTLS)
└─ rootless Podman container
   ├─ OpenShell supervisor namespace
   └─ nested agent network namespace
      ├─ Pi process
      └─ Pi A2A adapter :9910

Pi -> host: host.containers.internal:9900
host -> Pi: OpenShell loopback forward -> Pi:9910
            diagnostic fallback: nsenter into Pi's network namespace
```

Do not hard-code the numeric address behind `host.containers.internal`. Resolve it inside
the sandbox because the compute driver owns that mapping.

This example uses:

- `PI_TO_HOST_TOKEN` for Pi → host;
- `HOST_TO_PI_TOKEN` for host → Pi.

They are unrelated secrets even when both routes run on one machine.

## Security invariants

Before adding adapters:

1. keep OpenShell policy validation `fail_closed`;
2. run Pi as the unprivileged sandbox user;
3. allow writes only in the sandbox workspace and temporary directory;
4. permit only required A2A destinations, ports and executable paths;
5. store tokens in sandbox-user-owned mode-`0600` files;
6. keep external forwards on loopback unless a protected remote exposure is deliberate;
7. authenticate inside each A2A application even when the transport is local;
8. treat inbound A2A text as untrusted user input;
9. cap request size, duration, concurrency and recursive delegation;
10. redact authorization headers from logs.

An OpenShell L4/TCP rule controls the connection but cannot authorize an HTTP method,
path or A2A skill. The A2A adapter still has to enforce application-level policy.

## Direction 1: Pi calls the host agent

### 1. Enable the host listener

The switch is host-agent-specific. An illustrative environment configuration is:

```dotenv
A2A_HOST=<PRIVATE_BIND_ADDRESS>
A2A_PORT=9900
A2A_AGENT_NAME=host-agent
A2A_PEER_TOKENS=pi-agent:<PI_TO_HOST_TOKEN>
A2A_PUBLIC_URL=http://<SANDBOX_REACHABLE_HOST>:9900/
```

These keys are not universal A2A settings. Adapt them to the chosen host runtime.

Use `127.0.0.1` when a local forward is enough. Use `0.0.0.0` only when another namespace
must connect directly and a token plus network controls are already active. Some secure
servers intentionally refuse a non-loopback bind until authentication is configured.

Prove the listener before involving Pi:

```bash
ss -ltnp | rg ':9900\b'
curl -fsS http://127.0.0.1:9900/.well-known/agent-card.json | jq .
```

### 2. Resolve the sandbox path to the host

From Pi's sandbox:

```bash
openshell sandbox exec -n pi-agent -- getent hosts host.containers.internal
openshell sandbox exec -n pi-agent -- command -v node
openshell sandbox exec -n pi-agent -- command -v pi
```

Record the real executable paths for the policy. Do not guess them.

### 3. Allow only A2A egress

A minimal policy fragment is:

```yaml
version: 1

filesystem_policy:
  include_workdir: true
  read_only: [/usr, /lib, /etc, /proc, /var/log]
  read_write: [/sandbox, /tmp, /dev/null]

landlock:
  compatibility: hard_requirement

process:
  run_as_user: sandbox
  run_as_group: sandbox

network_policies:
  host_a2a:
    name: host-a2a
    endpoints:
      - host: host.containers.internal
        port: 9900
        protocol: tcp
    binaries:
      - path: /actual/path/from-command-v-node
      - path: /actual/path/from-command-v-pi
```

Validate this against the installed OpenShell policy schema. On releases that require
TCP-capture infrastructure at sandbox creation, the first native TCP endpoint cannot be
hot-added. Preserve the persistent workspace and recreate the runtime only when the
installed version requires it.

When TCP support already exists, preview an additive update:

```bash
openshell policy update pi-agent \
  --add-endpoint host.containers.internal:9900:full:tcp \
  --binary /actual/path/from-command-v-node \
  --binary /actual/path/from-command-v-pi \
  --dry-run
```

Then apply the same update with `--wait`. Prefer additive updates or the maintained base
policy; do not replace the complete effective policy from a generated dump.

### 4. Add a Pi outbound extension

Pi does not need native A2A support. A reviewed TypeScript extension can expose an
`ask_peer_agent` tool and call the host with `fetch()`.

The extension should:

- read its endpoint from configuration;
- read the bearer token from a protected file at runtime;
- generate new JSON-RPC and message IDs;
- handle both direct `Message` and `Task` results;
- retain the server-returned `contextId` for follow-ups;
- apply an abort timeout;
- return remote content as untrusted tool output.

The reusable client implementation is in `a2a-bidirectional-setup`.

Register the extension in Pi's active agent directory. Pi normally uses
`~/.pi/agent`; `PI_CODING_AGENT_DIR` can override it:

```json
{
  "extensions": [
    "/sandbox/agent_home/.pi/agent/extensions/a2a-bridge.ts"
  ]
}
```

Write settings as the sandbox user so ownership remains correct. Restart the Pi session
after initial registration. A file existing on disk does not prove that the live Pi
process loaded it.

### 5. Test Pi → host

First test discovery from the sandbox:

```bash
openshell sandbox exec -n pi-agent -- \
  curl -fsS http://host.containers.internal:9900/.well-known/agent-card.json
```

Then send a raw authenticated `SendMessage` with a unique marker:

```json
{
  "jsonrpc": "2.0",
  "id": "pi-to-host-1",
  "method": "SendMessage",
  "params": {
    "message": {
      "messageId": "pi-message-1",
      "role": "ROLE_USER",
      "parts": [
        {
          "text": "Reply with PI_TO_HOST_OK and your advertised agent name."
        }
      ]
    }
  }
}
```

Finally invoke the same route through the loaded Pi extension. Success requires the marker
from the live host agent, not merely HTTP 200.

## Direction 2: the host calls Pi

### 1. Add a Pi inbound A2A adapter

The Pi extension can start a small JSON-RPC server in Pi's process namespace. It should:

1. listen on a configured local port, for example `127.0.0.1:9910`;
2. validate `HOST_TO_PI_TOKEN` before agent execution;
3. serve an Agent Card;
4. accept only supported JSON-RPC methods and A2A parts;
5. enforce body, time and concurrency limits;
6. enqueue text through Pi's extension API as a real user/follow-up message;
7. correlate the resulting assistant event to the request;
8. return a `Message` or `Task` carrying `contextId`;
9. reject or serialize concurrent requests unless correlation is robust;
10. close the listener and pending requests on session shutdown.

Do not transform inbound peer text into Pi's system prompt or extension configuration.

Register the inbound extension in `settings.json`, restart Pi, and look for an explicit
startup log from the current session. Then prove the socket inside Pi's namespace.

### 2. Cross the sandbox boundary with service forwarding

Prefer the OpenShell control plane over direct Podman port manipulation:

```bash
openshell forward service pi-agent \
  --target-port 9910 \
  --local 127.0.0.1:19910
```

The host client now uses:

```text
http://127.0.0.1:19910/
```

Keep this bind on loopback. If a different machine must call Pi, place an intentional
TLS/authenticated proxy in front instead of casually widening the forward.

The Agent Card's interface URL must describe the address the host peer can reach, not
Pi's internal `127.0.0.1:9910`.

### 3. Test host → Pi

Check the forwarded card:

```bash
curl -fsS http://127.0.0.1:19910/.well-known/agent-card.json | jq .
```

Then send:

```json
{
  "jsonrpc": "2.0",
  "id": "host-to-pi-1",
  "method": "SendMessage",
  "params": {
    "message": {
      "messageId": "host-message-1",
      "role": "ROLE_USER",
      "parts": [
        {
          "text": "Reply with HOST_TO_PI_OK and your advertised agent name."
        }
      ]
    }
  }
}
```

Call the forwarded endpoint with the protected token:

```bash
curl -fsS http://127.0.0.1:19910/ \
  -H "Authorization: Bearer ${HOST_TO_PI_TOKEN}" \
  -H 'Content-Type: application/json' \
  --data @host-to-pi-1.json \
  | tee host-to-pi-1.response.json
```

Assert the JSON-RPC result and marker, then verify that Pi's current session log and the
redacted A2A audit refer to the same request.

## Nested network namespace diagnostics

OpenShell may place Pi in a network namespace nested inside the rootless Podman
container. In that topology:

- Pi's `localhost` belongs to the nested agent namespace;
- `podman exec ... curl localhost:9910` starts in the container's main namespace;
- therefore the latter can fail even when Pi really listens.

Use `openshell forward service` for normal transport. For a Podman-backed host-only
diagnostic:

```bash
CID=<CONTAINER_ID>
PI_PID=$(podman exec "$CID" pgrep -x pi | head -n 1)

podman exec "$CID" readlink /proc/1/ns/net
podman exec "$CID" readlink "/proc/$PI_PID/ns/net"
podman exec "$CID" nsenter -t "$PI_PID" -n -- ss -ltn
podman exec "$CID" nsenter -t "$PI_PID" -n -- \
  curl -fsS http://127.0.0.1:9910/.well-known/agent-card.json
```

Different namespace links explain the reachability difference. Add the bearer header
when discovery is protected.

`nsenter` assumes authorized host access to the container and exposes runtime internals.
It is a diagnostic fallback, not the application transport.

## Two-turn communication example

Extract the context returned by Pi:

```bash
jq -r \
  '.result.task.contextId // .result.message.contextId // empty' \
  host-to-pi-1.response.json
```

Create a follow-up with a new request ID and message ID:

```json
{
  "jsonrpc": "2.0",
  "id": "host-to-pi-2",
  "method": "SendMessage",
  "params": {
    "message": {
      "messageId": "host-message-2",
      "contextId": "<SERVER_RETURNED_CONTEXT_ID>",
      "role": "ROLE_USER",
      "parts": [
        {
          "text": "What exact marker did I ask you to return in the previous turn?"
        }
      ]
    }
  }
}
```

The correct answer proves continuity in the running Pi session. Repeat after a clean Pi
session/container restart only if durable contexts are a requirement. OpenShell workspace
persistence and A2A context persistence are separate properties.

## Evidence order

For Pi → host:

1. host process and socket;
2. host Agent Card from Pi's namespace;
3. authenticated raw `SendMessage`;
4. the registered Pi outbound extension;
5. a second turn with host-issued `contextId`.

For host → Pi:

1. extension listed in active Pi settings;
2. current Pi session startup log;
3. socket inside Pi's namespace;
4. OpenShell service forward;
5. authenticated raw `SendMessage`;
6. marker from the live Pi session;
7. a second turn with Pi-issued `contextId`.

An adapter unit test is not deployment proof. Neither is an agent's statement that its
server is listening.

## OpenShell-specific troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| Pi gets an OpenShell network denial | Host, port or executable is absent from policy | Inspect denial logs and effective policy |
| Policy update cannot add first TCP endpoint | Sandbox lacks TCP-capture setup | Check installed-version docs; preserve workspace before recreation |
| Extension file exists but port is closed | Extension is unregistered or session was not restarted | Inspect active `settings.json` and current startup log |
| `podman exec` cannot reach Pi's listener | Pi listens in a nested netns | Use service forwarding; compare namespace links |
| Forward works but card URL is unusable | Card advertises the internal bind | Advertise the forwarded/routable interface URL |
| Pi replies after caller timed out | Forward, adapter and agent budgets differ | Align budgets or return a Task |
| Settings become root-owned | Host wrote into the agent workspace as root | Write through the sandbox user and repair ownership deliberately |
| State disappears after deleting sandbox | Runtime deletion was treated as stop | Use stop/start and explicit backup for persistent state |

## Completion checklist

- OpenShell remains fail-closed and Pi remains unprivileged.
- The sandbox policy allows only the host A2A endpoint and required binaries.
- Pi → host and host → Pi use independent credentials.
- Both Pi extensions are registered in the active configuration.
- A clean Pi start logs the inbound listener.
- Service forwarding reaches Pi without exposing a public Podman port.
- Both directions pass raw and live-agent `SendMessage` tests.
- Both clients reuse the context issued by the receiving server.
- Nested-netns checks are used only for diagnostics.
- Workspace persistence and A2A context persistence are tested separately.
- No token, personal prompt or private implementation data appears in cards or logs.

## Primary references

- [A2A v1.0 specification](https://a2a-protocol.org/latest/specification/)
- [A2A project](https://github.com/a2aproject/A2A)
- [OpenShell documentation](https://docs.nvidia.com/openshell/latest/)
- [OpenShell policies](https://docs.nvidia.com/openshell/latest/sandboxes/policies)
- [Pi settings](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/settings.md)
- [Pi extensions](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)
