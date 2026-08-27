---
id: openshell-pi-agent
name: 'OpenShell + Pi: build an isolated coding-agent sandbox'
summary: >-
  Install and operate Pi inside an OpenShell sandbox with rootless Podman,
  fail-closed filesystem/network policy, brokered credentials, persistent workspace,
  pinned inference, reviewed extensions, and evidence-based verification. Includes an
  optional bidirectional A2A bridge without exposing personal providers or prompts.
type: skill
author: kisa
recommended: false
added: 2026-08-27
tags: [openshell, pi, sandbox, podman, isolation, security, a2a, agent]
source: https://docs.nvidia.com/openshell/
description: >-
  Use when the user wants to install, configure, migrate, harden, inspect, or troubleshoot
  a Pi coding agent running in NVIDIA OpenShell, especially with rootless Podman,
  deny-by-default networking, hidden credentials, persistent state, or A2A communication.
  Do not use for ordinary containerization that does not involve an agent sandbox.
triggers:
  - set up OpenShell and Pi
  - isolate a Pi coding agent
  - troubleshoot an OpenShell sandbox
  - connect an OpenShell agent over A2A
reminder: Verify the live process, namespace, socket and authenticated request; an agent's self-report is not deployment evidence.
---

# OpenShell + Pi

Build a useful Pi coding agent without giving the model ambient access to the host,
arbitrary internet egress or real API credentials. Prefer the official Pi community
sandbox first; create a custom image only when reproducibility or preinstalled tooling
requires it.

This workflow intentionally contains no personal system prompt, private skill, named model
vendor or account-specific provider. Select those from the user's own requirements.

## Non-negotiable invariants

- Inspect the current machine and installed CLI before changing anything. OpenShell is
  fast-moving; use `openshell <command> --help` as the local command contract.
- Keep the gateway on loopback with mTLS unless the user explicitly designs a remote
  gateway topology.
- Use a rootless compute driver when the host supports it. For Podman, require Podman 5.x,
  cgroups v2, rootless networking and an active user socket.
- Keep `enable_bind_mounts = false`. A host bind mount can negate the filesystem boundary.
- Keep `policy_validation_failure_mode = "fail_closed"`.
- Put real credentials in OpenShell provider records, never in `--env`, images,
  `settings.json`, `models.json`, skills, prompts or project files.
- Give the sandbox only explicit read-only/read-write paths and explicit egress.
- Run the agent as a non-root identity and prefer Landlock `hard_requirement` on a known
  compatible Linux host.
- Treat `/sandbox` as persistent agent state and `/tmp` as ephemeral. Do not confuse
  `sandbox delete` with stop; deletion may remove the managed workspace.
- Review every Pi extension before loading it. Extensions execute code with the agent
  user's sandbox permissions.
- Prove behavior with OS/network evidence. Do not accept “I tested it” from the sandboxed
  agent without checking the live runtime.

## Authorization boundaries

Read-only discovery is safe to perform immediately. Before creating containers, enabling
services, replacing policy, attaching credentials, restarting an active agent or changing
firewall/network exposure, make sure that action is inside the user's request. Before any
delete or workspace replacement, require explicit confirmation and a verified backup.

## 1. Discover the actual host

Collect facts without printing secret values:

```bash
uname -a
openshell --version
podman --version
podman info --format json
systemctl --user is-active podman.socket
openshell status
openshell whoami
openshell doctor
openshell sandbox list
```

Check cgroups and Landlock support using the host's native tools. Do not assume a distro,
package manager, socket path or UID. Never dump the entire process environment or provider
records into logs.

If OpenShell already exists, preserve its generated gateway metadata, TLS state, workspaces
and unrelated sandboxes. Inspect before editing:

```bash
openshell gateway list
openshell sandbox list
openshell provider list
openshell inference get
```

## 2. Install OpenShell and prepare rootless Podman

Use one official installation route after the user approves the download:

```bash
curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh
```

or:

```bash
uv tool install -U openshell
```

For a rootless Podman driver, enable the user's Podman socket through the host's service
manager and verify that it responds. The common socket is
`/run/user/<NUMERIC_UID>/podman/podman.sock`, but use the discovered path rather than
copying a UID from an example.

Record at least:

- `openshell --version`;
- Podman version, runtime and network helper;
- gateway config path;
- community/custom image digest;
- Pi version;
- policy revision/hash.

## 3. Harden the gateway

Patch the generated config minimally. A Podman-oriented baseline is:

```toml
[openshell]
version = 1

[openshell.gateway]
bind_address = "127.0.0.1:17670"
log_level = "info"
compute_drivers = ["podman"]
policy_validation_failure_mode = "fail_closed"

[openshell.drivers.podman]
socket_path = "/run/user/<NUMERIC_UID>/podman/podman.sock"
image_pull_policy = "missing"
enable_bind_mounts = false
```

The exact accepted values can differ across releases. Preserve fields generated by the
installed version and confirm them with the current gateway-config reference. Restart the
user gateway only after validating the file and confirming that no active task will be
interrupted.

After restart:

```bash
openshell status
openshell whoami
openshell doctor
```

`whoami` should show authenticated mTLS transport. A listening loopback port alone is not
enough.

## 4. Start from a minimal policy

Build the policy from required capabilities, not from a copied provider catalog. A secure
Pi baseline is:

```yaml
version: 1

filesystem_policy:
  include_workdir: true
  read_only:
    - /usr
    - /lib
    - /etc
    - /proc
    - /var/log
    - /dev/urandom
  read_write:
    - /sandbox
    - /tmp
    - /dev/null

landlock:
  compatibility: hard_requirement

process:
  run_as_user: sandbox
  run_as_group: sandbox

network_policies: {}
```

Every path listed under `hard_requirement` must exist in the chosen image or startup can
fail. Start with no runtime network access, observe denials, then add narrow rules for the
actual destination and calling binary.

Prefer build-time installation of reviewed CLI dependencies. Runtime package-manager
access widens the exfiltration and supply-chain surface. If runtime access is necessary,
restrict it to the exact registry, read methods and package-manager executable.

### Optional internal A2A endpoint

If the Pi agent must call a host A2A service, include the TCP substrate in the initial
policy on OpenShell versions that require it:

```yaml
network_policies:
  host_a2a:
    name: host-a2a
    endpoints:
      - host: host.containers.internal
        port: 9900
        protocol: tcp
    binaries:
      - path: /actual/path/to/node
      - path: /actual/path/to/pi
```

Discover executable paths inside the final image. Do not add `curl`, shells or wildcard
binaries unless the use case truly needs them.

## 5. Choose the inference boundary

Ask the user which model endpoint and model ID they own. Do not substitute a personal or
recommended provider silently.

For brokered inference:

1. Create an OpenShell provider record from a secret read without echo.
2. Configure the workspace inference route.
3. Point Pi at `https://inference.local/v1` with a non-secret placeholder key.
4. Deny direct sandbox access to the upstream inference host.

Use the installed CLI help because provider types require different credential names:

```bash
openshell provider create --help
openshell inference set --help
```

A safe input pattern is:

```bash
read -rsp 'Provider credential: ' PI_PROVIDER_SECRET
export PI_PROVIDER_SECRET
# Pass the environment variable NAME to --credential; do not place its value in argv.
openshell provider create \
  --name model-provider \
  --type <PROVIDER_TYPE> \
  --credential PI_PROVIDER_SECRET
unset PI_PROVIDER_SECRET

openshell inference set \
  --provider model-provider \
  --model <USER_SELECTED_MODEL_ID> \
  --timeout 120
```

Do not use `--no-verify` as a default. It records an unverified route and can turn a setup
mistake into a later runtime failure.

## 6. Create the persistent Pi sandbox

The official community image is the shortest reproducible starting point:

```bash
openshell sandbox create \
  --name pi-agent \
  --from pi \
  --cpu 2 \
  --memory 4Gi \
  --policy ./pi-policy.yaml \
  --approval-mode manual \
  --no-auto-providers \
  -- pi
```

Adjust CPU and memory to the host. `-- pi` makes Pi the canonical main process. If the
command is omitted, the image starts a retained shell and Pi must be launched manually
after every runtime start. Choose deliberately; do not report Pi as running merely because
the container is healthy.

Do not use `--no-keep` for a persistent agent. Use:

```bash
openshell sandbox stop pi-agent
openshell sandbox start pi-agent
```

for routine lifecycle management.

### When a custom image is justified

Create a custom image only for reviewed, pinned build-time dependencies or a reproducible
runtime layout. Keep it generic:

```dockerfile
ARG BASE_IMAGE=ghcr.io/nvidia/openshell-community/sandboxes/base:latest
ARG PI_VERSION
FROM ${BASE_IMAGE}

USER root
RUN npm install -g --ignore-scripts --no-audit --no-fund \
    "@earendil-works/pi-coding-agent@${PI_VERSION}" \
 && npm cache clean --force

COPY policy.yaml /etc/openshell/policy.yaml

WORKDIR /sandbox
USER sandbox
ENTRYPOINT ["/bin/bash"]
```

For a real build, pin the base image by digest and pass an explicit Pi version. Do not copy
personal skills, prompts, credentials or host configuration into a public image.

## 7. Configure Pi without leaking credentials

Pi's global configuration directory defaults to `~/.pi/agent`; it can be overridden with
`PI_CODING_AGENT_DIR`. Keep it under the persistent workspace.

Minimal `models.json` for OpenShell-managed, OpenAI-compatible inference:

```json
{
  "providers": {
    "openshell": {
      "baseUrl": "https://inference.local/v1",
      "api": "openai-completions",
      "apiKey": "unused",
      "models": [
        { "id": "USER_SELECTED_MODEL_ID" }
      ]
    }
  }
}
```

Minimal `settings.json`:

```json
{
  "defaultProvider": "openshell",
  "defaultModel": "USER_SELECTED_MODEL_ID",
  "defaultProjectTrust": "never",
  "enableInstallTelemetry": false,
  "packages": [],
  "extensions": [],
  "skills": [],
  "prompts": [],
  "themes": []
}
```

Add model capability fields only when the model's real API contract is known. Invented
context windows, tool support or reasoning flags create subtle failures.

For offline/reproducible startup, consider non-secret environment flags such as
`PI_OFFLINE=1`, `PI_SKIP_VERSION_CHECK=1` and `PI_TELEMETRY=0`, but only after all required
resources are present in the image or persistent workspace.

### Extensions and skills

- Install only reviewed resources needed for the user's task.
- Prefer absolute paths inside the persistent workspace.
- Register extensions in the active `settings.json`; copying a `.ts` file alone does not
  load it.
- Write configuration as the sandbox user, not as root.
- Restart the Pi session after first registration and verify its startup log.
- Use `/reload` for iterative development, then repeat a clean-start test.
- Do not copy a system prompt or persona from another deployment.

## 8. Transfer and persist data explicitly

Do not mount the host home directory. Use OpenShell's explicit transfer commands:

```bash
openshell sandbox upload pi-agent ./project /sandbox/projects/project
openshell sandbox download pi-agent /sandbox/projects/project ./project-backup
```

Back up only intended data. A whole-workspace download may include session history or
token files and needs the same protection as the agent's private state.

Test persistence with a harmless marker across `stop`/`start`. Separately test recovery
from a backup; a named volume is persistence, not a backup.

## 9. Verify the isolation

Run checks in layers:

```bash
openshell sandbox get pi-agent
openshell policy get pi-agent --full
openshell logs -n 100 pi-agent
openshell sandbox exec -n pi-agent -- id
openshell sandbox exec -n pi-agent -- pwd
openshell sandbox exec -n pi-agent -- pi --version
```

Then prove these invariants:

- agent UID/GID is non-root;
- `/sandbox` and `/tmp` are writable;
- an unlisted path is inaccessible or read-only as designed;
- the host home directory and host private keys are absent;
- a non-allowlisted network destination is denied;
- the configured internal inference route works;
- the direct upstream inference endpoint is denied;
- real credential values do not appear in readable files, process arguments or logs;
- `stop`/`start` preserves a marker and Pi configuration;
- the Pi process, not only the container, is actually running.

Do not print secret-bearing environment values while checking them. Compare hashes,
presence/absence or redacted names instead.

For a no-tool model smoke test:

```bash
openshell sandbox exec -n pi-agent -- \
  pi --no-tools --no-session --print 'Reply with PI_SANDBOX_OK only.'
```

For a read-only code review, use Pi's strict tool allowlist instead of its normal coding
tools.

## 10. Add bidirectional A2A only when needed

Retrieve the knowledge items from this MCP server according to the task:

- `a2a-protocol-overview` for Agent Cards, Messages, Tasks, `contextId` and protocol
  security boundaries;
- `a2a-bidirectional-setup` for the runtime-neutral two-route deployment and verification
  workflow;
- `a2a-openshell-example` for Pi adapters, OpenShell policy, service forwarding and
  nested-netns diagnostics.

The short operational shape is:

```text
Pi -> host agent:
  host.containers.internal:<host-a2a-port>
  + exact OpenShell endpoint/binary allowlist
  + Pi outbound extension

host agent -> Pi:
  Pi inbound extension on loopback:<pi-a2a-port>
  + openshell forward service
  + peer-specific bearer token
```

Prefer:

```bash
openshell forward service pi-agent \
  --target-port 9910 \
  --local 127.0.0.1:19910
```

over direct Podman port exposure. If the listener exists only in Pi's nested network
namespace, use `nsenter` to diagnose it, not as the normal public transport.

## 11. Troubleshoot from facts

### Sandbox is healthy but Pi is absent

Check whether `pi` was the canonical main command. A shell-based sandbox can remain
healthy while no Pi session exists. Inspect processes and current session logs.

### Policy update appears accepted but traffic is denied

Inspect the loaded revision and denial log. A candidate can fail validation and leave the
sandbox quarantined in `fail_closed` mode. Also check whether the first TCP endpoint had to
exist at sandbox creation.

### Extension says it is installed but no tool/listener exists

Confirm all four facts:

1. file exists with sandbox-user ownership;
2. active `settings.json` includes its path;
3. the live Pi session started after registration;
4. logs and socket state show the extension initialized.

### Host cannot reach a Pi listener

Compare `/proc/1/ns/net` with the Pi process namespace. Use `openshell forward service` to
cross the boundary. A normal `podman exec` command may be looking at the supervisor/main
namespace rather than the agent namespace.

### A previous log is mistaken for current work

Check timestamps, process start time, current session files and CPU activity before saying
the agent is busy. Old crash logs are not current state.

## Definition of done

- OpenShell gateway is authenticated over loopback mTLS.
- Rootless Podman and its user socket are healthy.
- Gateway rejects invalid policy fail-closed and host bind mounts are disabled.
- Pi runs as a non-root sandbox user.
- Only `/sandbox`, `/tmp` and explicitly chosen paths are writable.
- Network starts deny-by-default and every exception has an endpoint and binary owner.
- Credentials live only in provider records or protected token files.
- Pi uses the intended inference route and cannot call the upstream endpoint directly.
- Workspace data survives `stop`/`start` and has a tested backup plan.
- Extensions are registered, reviewed and proven loaded in the live session.
- A2A, if enabled, passes Agent Card, authenticated `SendMessage`, follow-up `contextId`
  and correct-namespace socket tests in both directions.
- No personal provider, model, skill, prompt, account or host identifier entered the
  reusable configuration.

## Primary references

- [OpenShell documentation](https://docs.nvidia.com/openshell/)
- [OpenShell repository](https://github.com/NVIDIA/OpenShell)
- [OpenShell Pi community sandbox](https://github.com/NVIDIA/OpenShell-Community/tree/main/sandboxes/pi)
- [Pi settings](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/settings.md)
- [Pi custom models](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md)
- [Pi extensions](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)
