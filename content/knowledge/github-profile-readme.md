---
id: github-profile-readme
name: Custom GitHub profile page — the special repository
summary: >-
  A GitHub profile is a page you author yourself. It lives in a repository named exactly like the
  account, renders from README.md on the default branch, and takes art, GIFs, custom SVG buttons and
  dynamic widgets. What the renderer allows, what it silently strips, how assets resolve, and why a
  profile stops showing up.
type: knowledge
author: kisa
recommended: true
added: 2026-07-29
tags: [github, profile, readme, markdown, svg, badges, actions, branding]
source: https://github.com/howdeploy/howdeploy
---

# Custom GitHub profile page

Every GitHub account has a page nobody edits: avatar, bio, pinned repos, contribution graph. Above
all of that sits a slot most people never fill — a **profile README**, authored by the account owner
and rendered at the top of `github.com/<username>`.

It is not a settings screen. It is a **repository**. One specific repository, with one specific name,
and GitHub wires it to the profile automatically.

**What the agent should do:** when a person wants a custom profile page, create the special
repository, put the README at its root, keep every asset inside that same repository, and verify the
page renders. Then use the layout tricks below — the renderer is a narrow subset of HTML, and most
"why doesn't this work" time is spent rediscovering what it strips.

## The mechanism

A repository whose name **matches the account name exactly** is special. GitHub says so at creation
time: *"You found a secret! `user/user` is a ✨ special ✨ repository that you can use to add a
README.md to your GitHub profile."*

GitHub shows the README on the profile when **all four** conditions hold:

1. A repository exists whose name matches the username.
2. The repository is **public**.
3. It contains `README.md` **in its root**.
4. That file has content.

Two facts the docs state less loudly:

- The README is read from the **default branch**. A README pushed to `master` while the default
  branch is `main` renders nowhere. Check `Settings → General → Default branch`.
- **A repository created before July 2020** with a matching name is not wired up automatically.
  For those, open the repository and click **Share to profile**. This is the "button" people
  remember — it is a migration path for old repositories, not a normal activation step. New
  repositories need no button at all.

Removing the page is the same list inverted: delete or empty the README, make the repository private,
or rename either the repository or the account.

### Creating it

Clicking through: **New repository** → name = username → **Public** → *Add README* on → **Create** →
**Edit README**. GitHub pre-fills a template.

From a terminal, which is what an agent should prefer:

```bash
gh repo create "$USER_NAME" --public --add-readme --description "Profile README for @$USER_NAME"
git clone "https://github.com/$USER_NAME/$USER_NAME" && cd "$USER_NAME"
# edit README.md, add assets/, commit, push
```

Verify with `gh api "users/$USER_NAME"` and by opening `github.com/<username>` in a private window —
not in the tab that has been cached all session.

## What the renderer allows

The profile README goes through the same GitHub Flavored Markdown pipeline as any repository README,
which means inline HTML is allowed **and then aggressively sanitized**. GitHub's own wording: the
HTML is sanitized, "removing things that could harm you and your kin — such as `script` tags,
inline-styles, and `class` or `id` attributes."

Dead on arrival:

| Removed | Consequence |
|---|---|
| `<script>` | No JavaScript. None. Nothing on the page is interactive except links and `<details>`. |
| `<style>`, `style="…"` | No CSS at all — not even `text-align`. |
| `class`, `id` | No hooks, no anchoring to your own styles. |
| `<iframe>`, `<object>`, `<embed>`, `<form>` | No embeds, no video players, no inputs. |
| Inline `<svg>` | SVG must be a **file** referenced by `<img>`, not markup pasted into the README. |

Survives, and is the entire toolbox:

- `<img>` with `src`, `alt`, `width`, `height`, `align` — the deprecated `align` attribute is the
  only way to float or centre anything.
- `<div align="center">`, `<p align="center">`, `<br clear="right">`.
- `<pre>`, `<code>`, `<details>`/`<summary>`, `<table>`, `<sub>`, `<sup>`, `<kbd>`, `<blockquote>`.
- Fenced ` ```mermaid ` blocks — rendered natively since 2022, alongside geoJSON, topoJSON and ASCII
  STL. Note that Mermaid does **not** render on GitHub Pages, only on GitHub itself.
- Emoji shortcodes, task lists, tables, footnotes, alerts.

Three behaviours GitHub adds on its own, verified on a live profile page:

- Every `<img>` is wrapped in a link to the file's blob page and gets `style="max-width: 100%"`
  injected — images are clickable whether you want it or not.
- Animated GIFs are wrapped in an `<animated-image>` element with a play/pause control.
- External links get `rel="nofollow"`.

There is also a size ceiling: the rendered view truncates at roughly **512 KB** of README. Nobody
reaches that with prose; a generated README that inlines data can.

## Assets: keep them in the repository

The strongest pattern is boring — commit the art next to the README and reference it with a relative
path:

```html
<img src="./assets/profile-art.png" width="26%" align="right" alt="Description of the art">
```

On the profile page GitHub rewrites that to
`/<username>/<username>/raw/<default-branch>/assets/profile-art.png`. Verified directly against a
rendered profile: relative paths work, and they resolve **against the default branch**, which is one
more reason the default branch must be the one you are pushing to.

Why this beats the alternatives:

- **Versus `raw.githubusercontent.com` absolute URLs** — relative paths keep working after a rename
  and survive a clone.
- **Versus drag-and-drop upload** (`github.com/user-attachments/assets/…`, produced by dropping a
  file into an issue comment) — those URLs are opaque, not part of the repository, and there is no
  public API to create them. Fine for a one-off screenshot in an issue, wrong for a profile you
  intend to maintain.
- **Versus hotlinking someone else's host** — everything external goes through GitHub's camo proxy
  and gets cached (see below).

Practical limits: browser upload caps at 25 MiB per file, Git warns above 50 MiB, GitHub blocks above
100 MiB. A profile that ships a 2.6 MB PNG is already generous; keep GIFs small — they autoplay in
everyone's feed of tabs.

## Layout tricks that actually work

Without CSS, layout comes from four moves.

**Art beside text.** Float the image right, write the paragraphs, then clear:

```html
<img src="./assets/profile-art.png" width="26%" align="right" alt="…">

### 👋 Hi, I'm …

Two or three lines about the work.<br>Manual <br> is how you control line breaks.

<br clear="right">
```

**A terminal-looking block.** `<pre>` renders monospace and preserves spacing — a stack list inside
`<pre>` reads like a terminal without a single style attribute:

```html
<pre>
🤖 Vibe coding • AI agents • automation
⌨️ Codex • Kimi CLI • custom skills
🐧 Linux • Flipper Zero • moddable gadgets
</pre>
```

**Centred rows.** `<div align="center">` with a row of linked images is how every button strip and
icon grid on GitHub is built. Tables work too when you need a real grid with captions.

**Collapsible sections.** `<details><summary>More</summary>…</details>` is the only interactive
element that survives sanitization — good for long lists that would otherwise bury the page.

## Buttons, badges, plates

Three routes, in increasing order of control.

### 1. shields.io

The default. A static badge is a URL:

```
https://img.shields.io/badge/<label>-<message>-<color>?style=for-the-badge&logo=telegram&logoColor=white
```

Parameters worth knowing: `style` (`flat`, `flat-square`, `plastic`, `for-the-badge`, `social`),
`logo` (any slug from simple-icons), `logoColor`, `label`, `labelColor`, `color`, `cacheSeconds`.
Underscore renders as a space, `__` as a literal underscore, `--` as a literal dash. Collections of
pre-made ones live in `Ileriayo/markdown-badges` (~17k stars, MIT).

Cost: every badge is a request to a third-party service, proxied and cached by GitHub. When shields
is slow, your profile shows broken images.

### 2. Your own SVG buttons — the durable option

Nothing stops you committing hand-made SVG buttons and referencing them relatively. No external
service, no cache weirdness, exact colours, and the file is 1 KB:

```html
<div align="center">
  <a href="https://t.me/…"><img src="./assets/buttons/telegram.svg" height="28" alt="Telegram"></a>
  <a href="https://youtube.com/…"><img src="./assets/buttons/youtube.svg" height="28" alt="YouTube"></a>
</div>
```

Generating them beats drawing them. A small Node script that takes an icon from simple-icons or
lucide, recolours it, and emits a rounded rect + label produces a consistent set in one run — and
regenerates the whole set when the palette changes:

```js
// scripts/generate-assets.mjs — sketch of the pattern
const width = Math.max(70, Math.ceil(label.length * 6.4 + 40))
const svg = [
  `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="28" viewBox="0 0 ${width} 28" role="img" aria-label="${label}">`,
  `<rect x=".5" y=".5" width="${width - 1}" height="27" rx="7" fill="${background}"/>`,
  icon,  // source icon, currentColor replaced with an explicit colour
  `<text x="29" y="18.2" fill="#ffffff" font-size="11" font-weight="700">${label}</text>`,
  '</svg>',
].join('')
```

Two rules for these files. **Bake the colours in** — an SVG loaded through `<img>` cannot inherit the
page's theme, so `currentColor` renders as black. And **keep the `aria-label`/`alt`** — a screen
reader announces the alt text and nothing else; text inside an `<img>`-embedded SVG is unreachable.

### 3. Dynamic widgets

Live cards rendered by third-party services. Verified active as of 2026-07:

| Project | What | Stars | Licence |
|---|---|---|---|
| `anuraghazra/github-readme-stats` | stats, top languages, repo cards | ~80k | MIT |
| `DenverCoder1/github-readme-streak-stats` | contribution streak | ~7k | MIT |
| `DenverCoder1/readme-typing-svg` | animated typing headline | ~9.1k | MIT |
| `Platane/snk` | contribution graph eaten by a snake (Action, commits an SVG) | ~6k | none stated |
| `kittinan/spotify-github-profile` | now playing | ~2.2k | MIT |

The catch with all of them: **the public instance is shared and rate-limited.** GitHub's API allows
5k requests/hour per token, and a popular public instance burns that — the card degrades to
"Maximum retries exceeded" or "Downtime due to GitHub API rate limiting" at the worst moment. The fix
is to fork and self-host (Vercel, Docker, anything) with your own PAT in `PAT_1`. An expired PAT
produces the same error message, so check the token first when a working card suddenly breaks.

`Platane/snk` sidesteps the problem entirely by running as an Action and committing a generated SVG
into the repository — a static file, no live service. That pattern is worth copying for anything you
care about.

## The camo cache — why a dynamic image freezes

Every image from an external host is fetched through `camo.githubusercontent.com`, GitHub's image
proxy. It exists for privacy (no tracking pixels), HTTPS, and DDoS protection — and it **caches
aggressively**, honouring the origin's `Cache-Control` and, in redirect chains, sometimes the wrong
one. A badge can sit stale for days.

Two remedies:

- Serve the image with `Cache-Control: no-cache, no-store, must-revalidate` from your own endpoint —
  camo then re-fetches on each view.
- Purge explicitly: `curl -s -X PURGE "https://camo.githubusercontent.com/<hash>"`. Automatable in an
  Action that greps the rendered README for camo URLs and purges each.

Images served from your own repository do not go through camo — they come from `/raw/` and update
with the commit.

## Automating the page with Actions

The profile repository runs Actions like any other. The standard shape — a schedule, a generator, a
guarded commit:

```yaml
name: Update README
on:
  schedule:
    - cron: "0 6 * * *"   # UTC
  workflow_dispatch:       # manual trigger, essential while iterating
permissions:
  contents: write          # without this the bot cannot push
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/build_readme.py
      - name: Commit if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add README.md
          git diff --staged --quiet || git commit -m "chore: refresh profile README"
          git push
```

Three details that cause most failures: `permissions: contents: write` (or the repository-level
"Read and write permissions" setting) or the push is denied; the `git diff --staged --quiet ||` guard
or every run fails on an empty commit; and `workflow_dispatch` so the workflow can be tested without
waiting for cron — which GitHub delays under load and never runs to the minute.

A common generator pattern is marker-based: keep `<!--START_SECTION:posts-->` / `<!--END_SECTION-->`
in the README and have the script replace only what sits between them, leaving hand-written content
untouched.

## Organizations

Same idea, different path:

- **Public** org profile → repository named `.github`, **public**, file at `profile/README.md`.
- **Member-only** view → repository named `.github-private`, file at the same `profile/README.md`.

Casing matters in the path (`README.md`), and the repository name must be exact. A `profile/`
directory in `.github-private` never shows publicly — that is the single most common mix-up.

## The rest of the profile page

The README is the headline, not the whole page:

- **Pinned items** — up to **six** repositories and gists combined, reorderable by drag. `Customize
  your pins` at the top of the "Popular repositories"/"Pinned" section.
- **Bio, company, location, website, social links** — `Edit profile` in the sidebar. The bio renders
  above the README and is the only text shown on hover cards elsewhere on GitHub.
- **Achievements** — awarded automatically (Pull Shark, Starstruck, …), displayed in the sidebar, can
  be hidden in profile settings.
- **Profile picture and social preview** — the avatar is the one element seen in every comment thread
  on the site; treat it as brand, not decoration.
- Organization profiles also support pinned repositories, chosen by an owner.

## When the page does not show up

Work the list in order:

1. Repository name equals the username — watch `-` versus `_`.
2. Repository is **public**.
3. `README.md` is at the **root**, not in a folder.
4. The file is not empty.
5. It is on the **default branch**.
6. Repository created before July 2020 → click **Share to profile**.
7. Broken images only → check whether they are external (camo cache, dead service, rate-limited
   widget) or internal (wrong relative path, wrong branch, case mismatch in the filename).
8. Still nothing → open the profile in a private window; caching and propagation are real.

Renaming an existing repository into place is reported to fail often enough that deleting and
recreating with the correct name is a legitimate second move.

## Taste

The mechanics take twenty minutes; the page is looked at for eight seconds. What separates a profile
from a badge dump:

- **One idea per screen.** Who you are, what you build, where to find you. A wall of forty
  technology badges says nothing — it is the same wall on ten thousand profiles.
- **Own your assets.** Art, buttons and icons committed into the repository never break, never rate
  limit, and never depend on somebody's free Vercel tier.
- **Write `alt` text.** It is the only thing a screen reader gets, and the only thing visible when an
  image fails.
- **Say what is true.** "Currently learning X" and "shipped X" are different claims; the profile is
  read by people who can check.

## Where to go next

The reference profile behind this guide is `github.com/howdeploy/howdeploy` — art floated right, a
`<pre>` stack block, generated SVG buttons and skill plates, a GIF, all assets relative. Clone it and
strip it down rather than starting from a template gallery. For a broader survey of what people
build, `abhisheknaiidu/awesome-github-profile-readme` (~31k stars, CC0) and
`rzashakeri/beautify-github-profile` (~12k stars, CC0) collect the patterns.
