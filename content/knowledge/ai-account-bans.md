---
id: ai-account-bans
name: 'Why AI accounts get banned — and how to keep yours alive'
summary: >-
  A field-grounded map of account bans on Claude and ChatGPT/Codex for users in restricted
  regions: why datacenter IPs and crypto/prepaid cards raise risk, what actually triggers
  KYC and suspensions, the one behavior that reliably kills accounts (rotating proxies), and
  what to do when you are flagged. Facts are labelled Documented / Community / Field.
type: knowledge
author: kisa
recommended: true
added: 2026-07-10
tags: [bans, accounts, vps, payments, kyc, stripe, stability, restricted-region]
source: https://support.claude.com/en/articles/8241253-safeguards-warnings-and-appeals
---

# Why AI accounts get banned — and how to keep yours alive

The typical story: you rent a VPS somewhere, get a crypto-backed card, pay for Claude Code or
Codex through Stripe — and a ban lands, asking for KYC or a phone number, and you have no idea
what you did wrong. This guide maps why that happens and how to keep a *legitimately paid*
account stable. It is written for real paying users in regions where these services aren't
officially available — not for fraud, multi-accounting, or forged identity.

Every claim is labelled so you know how much to trust it:
- **[Documented]** — from official Anthropic / OpenAI / Stripe pages.
- **[Community]** — repeatedly reported by users; strong pattern, not vendor-confirmed.
- **[Field]** — first-hand from KISA's own experience.

## The mental model: the enemy is change, not existence

The single most useful frame. Steady, old accounts with a consistent history tend to live for
years. **[Field]** Bans cluster in two places: **signup**, and a **sudden break in your usual
pattern** — a new country, a burst of automation, or rotating your exit IP. A stable account
doing the same thing from the same place is rarely the target. Something that suddenly *changes*
is. Optimize for consistency, not for a perfect one-time setup.

## Layer 1 — IP and VPS

- **Datacenter IPs start with a penalty. [Documented mechanics]** Exits from VPS providers
  (Hetzner, DigitalOcean, OVH, Vultr) are tagged `hosting_provider` by IP-reputation vendors
  (MaxMind, IP2Proxy, IPQualityScore, Team Cymru, Spamhaus). Not an instant ban — but a higher
  base risk score, and if the country is unsupported, geo-enforcement stacks on top. OpenAI
  states access from an unsupported location "may result in account block or suspension";
  Anthropic reserves the right to refuse unsupported regions.
- **Cleanliness hierarchy. [Community + mechanics]** Best: residential / mobile IP in a
  supported country. Middle: a clean dedicated IP on a decent host in a supported country (not
  recycled, not in an abused `/24`). Worst: shared datacenter IPs from a dirty subnet, and
  public VPN endpoints (detected by active probing and known-server lists).
- **A field-tested stack. [Field]** Fornex (VPS in an EU location — Germany / Netherlands /
  Sweden are on the supported lists; RU-language panel; pays with crypto) plus your own Xray
  Reality (`xrayebator`) for transport masking and DPI bypass. Honest limit: a Fornex exit is
  still a **datacenter** IP. Great for an agent's day-to-day research over Xray; for the
  cleanest *signup and billing* a residential/mobile exit is better (see
  `chrome-proxy-english-signup`). Transport masking is not IP reputation.
- **The crown rule — do NOT rotate IPs. [Field]** This is the most reliable way to lose an
  account. In the field, changing five proxies in a row got the account killed within 8–12
  hours. One stable exit lives; hopping dies. Rapid IP change is the top community-reported
  trigger for "Suspicious Activity" — and it's first-hand confirmed here.
- **Match geo. [Documented]** `card_country` vs `ip_country` is a signal Stripe exposes; keep
  the exit country consistent with the card and billing where you can (nuanced below).

## Layer 2 — Payments

The processor is Stripe. **[Documented]** Its Radar engine scores each charge 0–99: ≥65 is
elevated (manual review / challenge), ≥75 is highest (blocked before it reaches the network).

- **Funding type is a trade-off. [Documented]** Prepaid / virtual / crypto-funded cards
  (Bybit, and crypto cards generally) score worse — issuer model, weak BIN reputation, low
  disputability. Convenient, but with a risk premium.
- **A KYC'd, real card beats a country match. [Field — refines the theory]** The Stripe docs
  say `card_country` should match `ip_country`. In practice a genuinely **KYC'd** card wins.
  KISA's Solayer Emerald card is **issued out of Kenya** and is paid from an **EU** exit — a
  textbook country mismatch — and it "lives perfectly." The lesson: don't obsess over matching
  the country if the instrument is truly legitimate. A real, KYC'd Visa with a consistent
  identity is more stable than a matching-country prepaid with no KYC. Card legitimacy
  dominates.
- **The card must supply a full billing address. [Documented]** Checkout asks for country,
  state, city, ZIP, billing address, and name. A card that only gives a bare number is a
  stop-factor; a proper virtual card (Solayer, Zarub) provides the full set.
- **3D Secure is gold. [Documented]** Prefer cards that support 3DS (Zarub does). Completing
  3DS on the first charge enrolls the card on-file with strong authentication and cuts later
  off-session blocks.
- **Complete card-side KYC where offered. [Documented]** Solayer requires it — that's what
  makes the instrument "white." No-KYC cards (Zarub) are faster but score as less legitimate.
- **Vet the issuer. [Documented]** Solayer is a public project with KYC. Zarub is a Telegram-bot
  issuer with mixed reviews and even fraud-suspicion threads — usable as a fallback, but check
  its current reputation before you route money and an account through it.

**Recommended card: Solayer Emerald** — a real KYC'd Visa that, in the field, simply lives.
Zarub is a convenient fallback (fast, no-KYC, 3DS), not the pick for a long-lived main account.

## Layer 3 — Signup and warm-up (research-backed, not KISA-tested)

Honest caveat: KISA's own accounts are **old** and predate the strict era — so there is no
personally-tested signup ritual here. Treat this layer as **[Community / Documented]**
recommendations for anyone creating a *new* account:

- Sign up from a clean English browser profile with a timezone matching your exit (see
  `chrome-proxy-english-signup`). **[Community]**
- Sign up on the **same environment you'll keep using** — don't sign up on residential then
  switch to datacenter forever. **[Community]**
- Use a real phone number and don't churn it (Anthropic asks for one as a baseline).
  **[Documented]**
- Don't rotate the IP during signup or the first payment. **[Community + Field]**
- Warm up: no bursty automation or heavy API right after creation — ramp like a human.
  **[Community]**
- One account, one identity, one exit. No multi-accounting on the same card/device/IP.
  **[Community]**
- Close any verification prompt (KYC / Persona) promptly instead of ignoring it. **[Documented]**

## Layer 4 — When you get flagged

- **Appeal odds are low, officially. [Documented]** Anthropic's own transparency data:
  ~1,700 overturns out of ~52,000 appeals (Jul–Dec 2025) ≈ 3.3%. OpenAI publishes no rate; a
  common community estimate is ~20–30%. Expect "no."
- **You're not wiped. [Documented]** A banned Claude account can still log in to export data or
  delete the account; the appeal form requires being logged in.
- **KYC doesn't fix everything. [Documented]** Identity verification (gov ID + selfie via
  Persona) can restore a hold that was purely about identity or payment — but not a suspension
  for confirmed abuse or a sanctioned region.
- **How to appeal. [Documented / Community]** Submit receipts, payment timestamps, a screenshot
  of the error, and a short factual explanation. No essays.
- **The sober call. [Field + research]** At ~3% overturn, prevention beats cure. If an account
  died for behavior (the proxy-rotation case), it is often faster to set up a fresh account
  *correctly* than to fight a low-odds appeal — but multi-accounting has its own risks (a
  linked card/device/IP fingerprint), so never farm accounts on one stack.

## Honest gaps — what nobody publishes

- Neither Anthropic nor OpenAI disclose which IP-reputation vendors they use.
- There is no public case tying a ban to a specific named VPS provider.
- No published numbers for how long an IP must stay "clean," or how many KYC attempts you get.
- OpenAI has no public payment-KYC page — that side is community-only.

This isn't a weakness of the research; it's how the market works. Anti-fraud is deliberately
opaque. So this guide gives you probabilities and field-tested habits, not secret thresholds —
because those thresholds aren't published by anyone, and pretending otherwise would be a lie.
