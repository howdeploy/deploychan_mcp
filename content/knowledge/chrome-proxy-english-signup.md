---
id: chrome-proxy-english-signup
name: Passing a strict signup gate — English Chrome through a proxy
summary: >-
  A field-tested trick for anti-bot signup walls that flag your browser language and IP: launch a
  clean Chrome profile pre-seeded to en-US through a residential/mobile SOCKS5 proxy. Two proxy
  variants (no-auth like Happ, and login/password via a local forwarder). Used to register on
  Stack Overflow for Agents from a blocked region.
type: knowledge
author: kisa
recommended: false
added: 2026-07-06
tags: [chrome, proxy, socks5, signup, anti-bot, stack-overflow-for-agents, workaround]
source: https://mcp.deploychan.webcam/docs
---

# Passing a strict signup gate: English Chrome through a proxy

Some signup pages are the most paranoid part of a whole service. They fingerprint your browser and
your exit IP, and refuse to **create a new account** if either looks wrong. The concrete case this
guide came from is **Stack Overflow for Agents**: several operators independently hit the same wall —
registering a *new* account fails with an error complaining about the **IP**, and a Russian browser
locale doesn't help. Logging in and using an existing account works fine; the block is specifically at
account creation. (This is an empirical field finding, not an official Stack Overflow policy.)

A personal VPN didn't clear it, and neither did four paid ones — datacenter IPs get flagged. What
worked was a **residential/mobile proxy** plus a **clean Chrome profile forced to English**. (On one
setup an Xrayebator instance in Happ/INCY proxy mode on someone else's server also passed — a clean
residential exit is the point, not the specific product.) Once the account exists, the proxy is no
longer needed.

The technique below is generic — it applies to any strict signup gate, not just SOFA. Commands are for
Linux with `google-chrome-stable`.

## 1. Force the browser to English

Chrome reads its language from the profile. Create a fresh profile and pre-seed `en-US` before first
launch:

```bash
rm -rf ~/.config/chrome-proxy-profile
mkdir -p ~/.config/chrome-proxy-profile/Default

# Main settings file
echo '{"intl":{"selected_languages":"en-US,en"},"spellcheck":{"dictionaries":["en-US"],"dictionary":""}}' \
  > ~/.config/chrome-proxy-profile/Default/Preferences

# Interface locale
echo '{"intl":{"app_locale":"en_US","selected_languages":"en-US,en","accept_languages":"en-US,en"}}' \
  > ~/.config/chrome-proxy-profile/Local\ State
```

## 2. Proxy without auth (e.g. Happ, local)

If your proxy accepts connections with no username/password, point Chrome straight at it:

```bash
LANGUAGE=en_US LANG=en_US.UTF-8 google-chrome-stable \
  --user-data-dir="$HOME/.config/chrome-proxy-profile" \
  --proxy-server="socks5://127.0.0.1:10808" \
  "https://api.ipify.org"
```

Opening `https://api.ipify.org` first is a sanity check — it prints the exit IP the site will see.

## 3. Proxy with login/password (e.g. GeekProxy)

Chrome can't pass credentials in `--proxy-server`. You need a local forwarder: it accepts connections
with no password and authenticates to the upstream proxy itself.

```bash
# Start the forwarder (once, runs in the background)
python3 /tmp/socks5-forwarder.py &

# Chrome connects to the forwarder
LANGUAGE=en_US LANG=en_US.UTF-8 google-chrome-stable \
  --user-data-dir="$HOME/.config/chrome-proxy-profile" \
  --proxy-server="socks5://127.0.0.1:10888" \
  "https://stackoverflow.com/users/signup"
```

The forwarder lives at `/tmp/socks5-forwarder.py`. To switch proxies, edit `REMOTE_HOST`,
`REMOTE_PORT`, `USERNAME`, `PASSWORD` inside it.

## The full chain

```text
┌────────┐    SOCKS5      ┌───────────┐    SOCKS5+auth    ┌────────────┐
│ Chrome │ ───────────────→│ forwarder │ ─────────────────→│ GeekProxy  │ → internet
│ (en-US)│   :10888        │ (Python)  │   :824            │ residential│
└────────┘  no password    └───────────┘                   └────────────┘
```

Chrome speaks plain SOCKS5 to the local forwarder with no password; the forwarder adds the
username/password and talks to the upstream residential proxy. The site sees an English browser on a
clean residential IP — and lets you create the account.

## After signup

The proxy is only needed to get past registration. Once the account exists you can log in and use the
service normally on your usual connection. For Stack Overflow for Agents specifically: create the
account this way, then hand the agent the onboarding line and let it walk `/skill.md` — see the
`stack-overflow-for-agents` guide and the `join-sofa` route.
