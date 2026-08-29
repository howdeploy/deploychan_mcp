---
id: xrayebator
name: 'Xrayebator: your own VPN on a VPS (Xray Reality)'
summary: >-
  KISA's skill for installing and repairing a personal Xray Reality exit on a VPS. The current
  3.0 line provides VLESS + REALITY routes, a managed HAPP subscription, and an August 2026 DNS
  hardening path: encrypted DNS stays inside the full TUN instead of leaking to the access ISP.
type: skill
author: kisa
recommended: false
added: 2026-07-04
tags: [vpn, xray, reality, vless, vps, censorship, dns, doh, happ]
source: https://github.com/howdeploy/Xrayebator
description: >-
  Use when the user needs a personal VPN/proxy on a VPS, or when an existing Xrayebator + HAPP
  connection needs to be repaired after DNS interception or encrypted-resolver blocking. Covers
  safe update, managed routing, DNS bootstrap, leak checks, rollback boundaries, and redaction.
license: MIT
---

# Xrayebator — your own VPN on a VPS (Xray Reality)

Xrayebator installs and manages a personal **VLESS + REALITY** exit on a VPS. REALITY makes the
transport resemble an allowed TLS connection without requiring a public domain for the VPN
transport itself. This raises the cost of basic DPI classification; it is not a promise that the
traffic is literally indistinguishable or immune to active probing.

This guide was reviewed on **2026-08-29** against Xrayebator `main` at
[`7df2381`](https://github.com/howdeploy/Xrayebator/commit/7df2381ce2427378e80e4e2fbc74f801d83a6795).
The dated DNS section matters: filtering behaviour differs by operator and can change without a
client update.

> **Legality and scope.** Use this for systems and accounts the user is authorised to operate.
> Local rules differ. Do not weaken a corporate DNS or monitoring policy without the system
> owner's approval.

## Privacy boundary for the agent

Treat connection material as secrets. Do not ask the user to paste or publish:

- a subscription URL or QR code;
- tokens, keys, exported client JSON, server addresses, or domains;
- the user's labels for servers, subscriptions, routes, or routing profiles;
- unredacted service logs or packet captures.

Operate over the authorised SSH session, inspect values locally, and report only state such as
“subscription endpoint returned success”, “managed routing is active”, or “one plaintext DNS
packet was observed”. Keep backups on the server. Never put private values in an issue, chat,
shell history, screenshot, or this guide.

## Install or update

For a new disposable VPS, inspect the installer before running it:

```bash
curl -fsSLo ./xrayebator-install.sh \
  https://raw.githubusercontent.com/howdeploy/Xrayebator/main/install.sh
less ./xrayebator-install.sh
sudo bash ./xrayebator-install.sh
```

For an existing installation, take a provider snapshot or another tested recovery point, then
update the project code and enter the menu so one-time migrations run:

```bash
sudo xrayebator-update main
sudo xrayebator
```

The similarly named `sudo xrayebator update` updates Xray-core only. It does not install the
subscription and routing fixes from the project repository.

The current 3.0 flow builds several TCP, XHTTP, and gRPC route variants. HAPP is the primary
subscription client; use version **3.3.6 or newer**. Other clients can consume compatible raw
VLESS routes or the reduced v2ray subscription, but they do not receive the complete managed HAPP
routing behaviour.

## DNS threat model — Russia, August 2026

As of 2026-08-29, assume all three conditions below can occur:

1. **Open DNS can be redirected or forged.** Measurements published on 2026-08-28 showed selected
   UDP/53 queries sent to well-known public resolvers receiving authoritative-looking `NXDOMAIN`
   answers. In the same measurement, TCP/53 reached the intended resolver. This is evidence for
   those networks and timestamps, not proof that every operator implements one identical rule.
2. **A public encrypted resolver can be blocked before DNS is exchanged.** August field reports
   describe DoH and DoT connections stalling or being reset during TLS setup. Results varied by
   operator, region, resolver, address family, and day.
3. **Correct DNS alone does not bypass later filtering.** DoH protects the query on the path to the
   resolver, but a direct connection can still expose destination IP metadata or TLS SNI. A full
   tunnel protects more of the access link than “secure DNS” enabled in a browser alone.

The practical conclusion is deliberately narrower than “switch resolver”: **the DNS transport
must itself be captured by the working VPN tunnel**.

```text
application
    ↓
operating-system DNS + HAPP TUN
    ↓
managed Global Proxy routing
    ↓
VLESS + REALITY tunnel
    ↓
VPS outside the filtered access network
    ↓
authenticated DoH resolver
```

On this path the access ISP sees the tunnel flow, not a separate open DNS exchange or a direct TLS
session to a public resolver. The VPS operator and the chosen resolver remain inside the trust
model: the resolver can see queries, and the VPS can observe destination metadata.

## Required routing invariants

Current Xrayebator `main` generates a complete HAPP routing payload and validates its schema before
publishing it. For the safe default, verify these invariants instead of copying a sample JSON with
someone else's values:

- **Global Proxy is enabled.** Public application traffic and the DoH connection use the tunnel.
- Both **remote DNS** and **domestic DNS** use DoH. Do not leave a provider-DNS or open-UDP fallback
  active merely because it answers faster.
- The DoH hostname has a locally stored **bootstrap address** and a matching host override. This
  avoids the circular first lookup through the access provider. The bootstrap address selects the
  server; TLS certificate validation authenticates it.
- Direct destinations contain only local, private, link-local, multicast, and other host-network
  ranges needed to reach the LAN. There are no public-domain or country-wide direct rules on the
  client.
- Domain strategy is `IPIfNonMatch`; FakeDNS is disabled in this managed DoH profile.
- Geo databases come from the same authenticated HTTPS subscription origin. The client does not
  need a separate direct download from GitHub before routing can initialise.

These are the invariants implemented and regression-tested in the reviewed `main` commit. The
official [HAPP routing documentation](https://www.happ.su/main/dev-docs/routing) confirms the
meaning of Global Proxy, DNS types, host overrides, direct lists, domain strategy, and FakeDNS.

### What the bootstrap entry does not do

A bootstrap entry prevents a plaintext lookup of the DoH hostname; it does not make a direct DoH
connection invisible. Safety comes from **both** the bootstrap entry **and** routing the resulting
HTTPS connection through REALITY. If that HTTPS connection leaves on the physical interface, a
known public endpoint can still be blocked.

The tunnel endpoint has its own bootstrap boundary. When a connection route uses a hostname, that
name may need resolving before the tunnel exists. Keep an out-of-band recovery path and prefer a
locally stored address-based endpoint when DNS failure prevents the tunnel from starting. Do not
publish that address. If using Xrayebator's address-based HTTPS subscription mode, verify its
short-lived certificate renewal rather than assuming it is permanent.

## Repair runbook for an existing HAPP user

Follow the sequence; a green latency result for one route is not enough.

1. **Preserve recovery access.** Confirm SSH access that does not depend on the connection being
   repaired. Take a VPS snapshot. Record no secret values in the work log.
2. **Update the project, then run migrations.** Execute the two update/menu commands above. Do not
   stop after updating Xray-core.
3. **Repair or create the managed HAPP subscription** from the Xrayebator menu. Use the existing
   server-side data where possible; do not invent a public profile label for the user.
4. **Validate locally on the VPS:**

   ```bash
   sudo /usr/local/bin/xray test -config /usr/local/etc/xray/config.json
   sudo systemctl is-active xray
   sudo systemctl is-active xrayebator-sub
   ```

   Inspect detailed logs locally only if a status is not `active`; redact all addresses, domains,
   tokens, labels, and connection strings before reporting.
5. **Update HAPP**, fully quit every old HAPP process, start one current instance, force-refresh the
   existing subscription, and reconnect once. A managed routing entry may be locked in the UI by
   design because the subscription owns it.
6. **Disable competing client routing overrides** during verification. Confirm every invariant in
   the previous section and wait until both geo assets load successfully.
7. **Confirm the main TUN is running.** HAPP route latency is measured by a temporary core and can
   be green while the main application TUN is down.
8. **Run the leak and behaviour checks below.** Only then hand the connection back to the user.

## Verification without disclosing connection data

### Plaintext DNS leak check

On a desktop client, identify the physical network interface locally. In one terminal, observe
only port 53 while HAPP TUN is connected:

```bash
sudo tcpdump -pni <physical-interface> 'udp port 53 or tcp port 53'
```

In another terminal, trigger several uncached lookups through ordinary applications. Stop the
capture and report only whether the packet count was zero. Do not paste the capture: even one line
can expose queried names and network addresses.

Expected result: **no port-53 packets on the physical interface**. Seeing encrypted tunnel traffic
is normal. If port-53 traffic appears, find the process or application bypassing TUN; do not solve
it by selecting another open resolver.

### Direct encrypted-resolver check

Inspect the physical-interface destinations locally while generating a fresh lookup. There must
be no direct connection to the configured DoH bootstrap destination; the only access-network flow
for the lookup should be the VPN transport. Report pass/fail only.

### Behaviour checks

- Resolve and open several ordinary domains through normal applications, not only with a route
  ping tool.
- Confirm subscription refresh and both geo downloads succeed while connected.
- Temporarily test on each access network the user actually relies on; operator behaviour is not
  uniform.
- If the user requires fail-closed behaviour, enable the operating system's “block without VPN” or
  equivalent kill switch after explicit approval and test tunnel failure. Xrayebator configures
  the server; it cannot guarantee the client OS will suppress DNS after HAPP disconnects.

## Fallback order

1. **Full TUN with DNS inside the tunnel** — the managed Xrayebator + HAPP design.
2. **A private or low-profile DoH service on standard HTTPS, still inside the tunnel** — use when
   the managed resolver is unavailable from the VPS. Preserve certificate validation, bootstrap,
   Global Proxy, and the no-public-direct-rules invariant.
3. **Another working public DoH endpoint, still inside the tunnel** — availability is operator- and
   resolver-dependent when used directly, so do not treat today's success as a durable property.
4. **TCP/53 only as a short diagnostic or emergency observation.** It is unencrypted, exposes the
   query, and can be redirected as easily as UDP once policy changes. Never make it the steady-state
   configuration.

DoT and DoQ have distinct, easy-to-filter transports and were not a reliable direct-access escape
in the August reports. They can be valid between the VPS and its resolver, but they do not replace
the client-side full-tunnel requirement.

## What does not solve the problem

- **Changing one open public resolver for another:** the censor can redirect by port or add the
  new endpoint to a block rule.
- **Enabling DNSSEC alone:** a validating resolver can reject forged data or an invalid denial of
  existence for signed zones, but it cannot recover the correct answer from a blocked path. The
  result is commonly a safe failure, not connectivity.
- **Adding site addresses to a hosts file:** CDN addresses change, multiple record types are used,
  and later IP/SNI filtering remains.
- **Browser-only DoH with public traffic outside TUN:** it may protect the DNS exchange while the
  subsequent connection still leaks the destination or is blocked.
- **Country-wide direct routing on the client:** it reintroduces the access ISP into DNS and TLS
  decisions. If the user explicitly needs split DNS for local services, document the privacy
  trade-off and route only the minimum named zones after approval.

## Incident handling

- **Subscription refresh fails before the tunnel starts:** distinguish subscription-hostname
  bootstrap from in-tunnel DNS. Restore through the authorised recovery channel; do not send the
  secret URL to a public checker.
- **Routes are green but applications fail:** update HAPP, terminate stale HAPP cores, refresh the
  subscription, confirm the main TUN, then check routing overrides and geo downloads.
- **DoH appears on the physical interface:** routing is bypassed. Stop and repair Global
  Proxy/direct rules; do not declare success merely because DNS answers are correct.
- **DoH works with TUN off but fails with TUN on:** first test resolver reachability from the VPS.
  Preserve full-tunnel routing while distinguishing a VPS-egress problem from a client leak.
- **The managed DoH endpoint fails from the VPS:** test from the VPS, then select an authorised
  private or alternative DoH endpoint. Keep its identity in local configuration only.
- **A custom routing payload is rejected:** use the managed fallback. Current Xrayebator validates
  the full HAPP schema and deliberately rejects old rules-only JSON that can create a broken locked
  entry.

## Sources and evidence quality

- [Habr, 2026-08-28: open DNS interception measurements](https://habr.com/ru/articles/1075272) —
  direct `dig` observations for UDP/53 versus TCP/53 on the author's network; useful but not a
  nationwide measurement.
- [Teplitsa, 2026-08-07: multi-node DNS censorship study](https://te-st.org/2026/08/07/dnsdnsdns) —
  five observation points, several transports, and an explicit distinction between in-path
  interference and resolver/geolocation behaviour.
- [NTC community thread, August 2026](https://ntc.party/t/%D0%B1%D0%BB%D0%BE%D0%BA%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-doh-google-cloudflare-quad9-opendns/23007?page=7) —
  operator-specific reports showing heterogeneity; treat as field evidence, not controlled proof.
- [Xrayebator reviewed source, 2026-08-29](https://github.com/howdeploy/Xrayebator/blob/7df2381ce2427378e80e4e2fbc74f801d83a6795/xrayebator#L589-L707) —
  managed HAPP schema validation, Global Proxy, DoH bootstrap, local-only direct ranges, geo URLs,
  domain strategy, and FakeDNS state.
- [Xrayebator regression test at the same commit](https://github.com/howdeploy/Xrayebator/blob/7df2381ce2427378e80e4e2fbc74f801d83a6795/validation/test-happ-subscription-static.sh#L65-L100) —
  executable assertions for the managed routing payload and rejection of the legacy incomplete
  shape.
- [RFC 8484 — DNS Queries over HTTPS](https://www.rfc-editor.org/rfc/rfc8484),
  [RFC 7858 — DNS over TLS](https://www.rfc-editor.org/rfc/rfc7858),
  [RFC 9250 — DNS over QUIC](https://www.rfc-editor.org/rfc/rfc9250), and
  [RFC 4033 — DNSSEC capabilities and limits](https://www.rfc-editor.org/rfc/rfc4033) — protocol
  definitions; they do not describe the August 2026 deployment state in Russia.

Re-check current sources before applying this runbook after August 2026. A temporary protocol gap
is an observation, not a stable feature.
