---
id: x-content-advisor
name: X Content Advisor
summary: >-
  Audit an X account or draft, separate evidence from algorithm folklore, and turn the
  findings into stronger posts, content ideas, and small measurable experiments. Includes
  a dated Phoenix ranking reference and a worked @copenzafan case study.
type: skill
author: kisa
recommended: true
added: 2026-08-14
tags: [x, twitter, content, analytics, growth, phoenix, social-media]
source: https://x.com/XOpenSource/status/2087951962004230428
description: >-
  Use when a user asks how to grow or make better content on X/Twitter, wants an account
  or post audit, asks why a post underperformed, needs a weekly content plan, or wants a
  draft rewritten, a posting-time experiment, or a recommendation-risk review of sensitive
  media using evidence from their own timeline. Works with public profile/post URLs,
  exported analytics, screenshots, images, or text supplied by the user.
triggers:
  - audit my X account
  - analyze my Twitter posts
  - improve this tweet
  - make an X content plan
  - why did this post underperform
  - find the best time to post on X
  - will this image be restricted on X
---

# X Content Advisor

Give practical content advice from the user's own evidence. Treat the published X
algorithm as a set of constraints and clues, not a recipe that predicts reach.

## Choose the smallest useful mode

- **Draft review:** inspect the hook, promise, proof, media, audience fit, and requested
  action. Return a revised draft plus the few changes that matter.
- **Post diagnosis:** compare the post with the account's normal baseline and nearby posts.
  Explain plausible causes; do not claim causality from one observation.
- **Account audit:** sample recent root posts, identify repeatable winners and leaks, then
  recommend three priorities.
- **Content plan:** turn proven themes into a short schedule of root posts, supporting
  self-replies, and one-variable experiments.

Do not force a full audit when the user only asks to fix one draft.

## Audit workflow

### 1. Establish the evidence boundary

Use live sources when available. Record:

- profile and post URLs;
- capture date and timezone;
- number of root posts actually found;
- whether metrics came from native analytics, public counters, screenshots, or the user;
- posts or metrics that could not be accessed.

Public X pages are often incomplete when logged out. Never call a partial public sample
"the whole account." Public counters also change, so date every numerical claim.

For a useful account sample, prefer 10–30 recent **root posts** plus known top performers.
Keep replies, reposts, and roots separate: they occupy different surfaces and are not fair
one-to-one comparisons.

### 2. Build a compact post map

For each root post, capture only fields that help the decision:

| Field | Examples |
|---|---|
| Format | text, image, demo video, comparison, story, launch |
| Topic and audience | AI builders, artists, NFT community, broad tech |
| Hook | result, tension, novelty, opinion, or no clear hook |
| Proof | working demo, output, numbers, code, personal event |
| Action | reply, open resource, share, follow, or none |
| Public outcomes | views, likes, replies, reposts, quotes, bookmarks if visible |

Use medians for the account baseline because one viral post distorts the mean. Show raw
counts for a small sample. Ratios can describe behavior, but low-view ratios are noisy.

### 3. Diagnose three different outcomes

Do not collapse everything into "engagement":

1. **Reach:** views and out-of-network discovery.
2. **Conversation:** replies, quotes, and whether the author can answer usefully.
3. **Depth/conversion:** follows, profile visits, link actions, bookmarks, or downstream
   outcomes when native analytics or user data exposes them.

A community story can create an excellent conversation without broad reach. A visual demo
can earn views without converting. Name which outcome succeeded.

### 4. Find a repeatable mechanism, not a superficial format

Ask why the post made someone stop and act. "Video worked" is too shallow if another video
failed. Look for the combination:

- a result visible immediately;
- novelty or useful tension in the first two lines;
- credible proof;
- a recognizable audience;
- one natural next action with a real payoff.

Phrase conclusions as evidence levels:

- **Observed:** directly supported by the sample.
- **Likely:** a plausible explanation supported by several posts or product mechanics.
- **Test:** an unproven hypothesis for the next posts.

### 5. Recommend changes the user can execute

Return, in this order:

1. one-sentence diagnosis;
2. what already works, with post-level evidence;
3. the three largest leaks;
4. three prioritized changes;
5. requested deliverable: revised draft, post ideas, or a weekly plan;
6. a 2-week test with one changed variable per comparison;
7. evidence limitations.

Do not promise a view or follower range. X's score is personalized, experiments can override
defaults, and public engagement counts do not expose the model probabilities.

## Content rules that survive algorithm changes

### Make the root post complete

Use this shape when it suits the material:

1. **Hook:** state the surprising result, conflict, or payoff in the first 1–2 lines.
2. **Proof:** show the output, demo, comparison, screenshot, or concrete event.
3. **Context:** explain what changed and why it matters to this audience.
4. **Action:** ask for one useful next step only when the user receives something specific.
5. **Self-reply:** place code, workflow, sources, limitations, or a deeper breakdown there
   when the root would otherwise become crowded.

A self-reply improves context and conversion on the conversation page. Do not describe it
as a second independent out-of-network root-post opportunity.

### Prefer a value contract to generic engagement bait

Good actions are specific and fulfillable:

- "Reply `workflow` and I'll post the node graph" — only if the author will actually do it.
- "Which failure should I test next: hands or temporal consistency?"
- "Repo and setup notes are in the first reply."

Avoid interchangeable "like/follow/share" requests. A CTA cannot rescue a weak premise.

### Rotate mechanisms, not just media types

Useful recurring pillars for a technical creator:

- **Build proof:** a working tool or workflow with the result first.
- **Comparison:** side-by-side outputs plus a decisive takeaway and test conditions.
- **Failure analysis:** one artifact, why it happened, and the attempted fix.
- **Personal stakes:** a real event, decision, loss, surprise, or disagreement tied to the
  audience's world.
- **Deep resource:** code, nodes, prompt, checklist, or postmortem delivered in a thread.

Pure text can work, but it needs unusually strong tension or insight. Adding arbitrary media
does not fix an undifferentiated thought.

### Space competing roots deliberately

There is no published "maximum two posts per day" rule. However, same-author candidates in
one feed slate are diversity-decayed, so several similar roots can compete with one another.
Prefer one strong root and its useful thread over several near-duplicate roots. Treat timing
as an experiment, not a universal law.

### Test posting time instead of declaring a universal best hour

The published recommender does not prescribe a best clock time. Use native follower-activity
analytics when available. Otherwise, select two plausible windows for the audience, rotate
comparable root posts between them, and compare medians after at least four posts per window.
Keep topic, format, and day mix as similar as practical.

For a mixed Europe + US East audience, use this only as a starting test grid:

| Goal | Moscow time hypothesis | Days to start with | Approximate overlap |
|---|---|---|---|
| Europe morning | 10:00–12:00 | Tue–Thu | Europe morning; little US overlap |
| Broad overlap | 15:00–18:00 | Tue–Thu | Europe afternoon + US East morning |
| Narrow compromise | 16:00–17:30 | Tue–Thu | A practical subset of the broad-overlap window |
| Later mixed window | 19:00–21:00 | Tue–Fri | Europe evening + US East midday |

Moscow stays on UTC+3 while Europe and the US change daylight-saving offsets. Recalculate
the audience's local time when the clocks change. Never present this grid as an X algorithm
rule or call a slot "best" before the account's own test supports it.

### Treat sensitive media as a distribution constraint

Sensitive visuals may hold attention among people who can see them, but adult/NSFW, gore,
spam, malicious-link, and do-not-amplify labels can interstitial or hard-drop content from
Home Recommendations. Account-level adult labels can also remove out-of-network candidates.

Do not advise classifier evasion or imply that wording such as "AI-generated tech demo"
neutralizes media labels. Follow platform rules and keep the main growth loop suitable for
broad recommendation surfaces.

### Separate content boundaries from classifier claims

The open repository publishes what visibility rules do **after** a safety label or account
flag exists. It does not publish the media classifier's complete feature set, thresholds,
or the frequency with which a visual cue produces `NSFW_HIGH_PRECISION` versus
`NSFW_HIGH_RECALL`. Never convert an aesthetic cue into a guaranteed label.

Use this qualitative review instead:

| Review class | Content description | Recommendation-risk interpretation |
|---|---|---|
| **Explicit** | Visible genitals, explicit sex acts, or full/near-full sexual nudity | Treat as high distribution risk. If an NSFW label/flag is applied, Home can interstitial it and Home Recommendations can drop it OON. Do not claim which classifier label is guaranteed. |
| **Sexually suggestive** | No explicit nudity, but sexualized expression, pose, fluids/wet styling, framing, or fetish-coded context | Treat as uncertain but material label risk. Review the actual media and account context; do not assign a probability without measured examples. |
| **Neutral or ambiguous cosplay** | Portrait/costume presentation without explicit nudity or intentionally sexualized expression/context | Lower apparent risk, not a guarantee of `ALLOW`; other media, text, account, and safety signals still apply. |

When reviewing a sensitive candidate, report four separate facts:

1. **Visible explicitness:** what intimate anatomy or sex act is actually visible.
2. **Presentation:** expression, pose, fluids, crop, clothing, and surrounding context.
3. **Rule evidence:** which published visibility action would follow **if** a known label
   were present.
4. **Uncertainty:** whether the label itself is observed in Under the Hood/native UI or only
   hypothesized from the image.

Example from the @copenzafan case: a face-and-shoulders crop with an ahegao-coded expression,
visible tongue/tears/saliva, wet styling, and a helmet contains no described explicit nudity
beyond bare shoulders, but its presentation is deliberately sexually suggestive. Classify the
content review as **suggestive, non-explicit**. The crop and absence of links do not prove it
will avoid a media label: links/card images are evaluated by separate rules, while the actual
classifier thresholds are not published. Do not recommend tighter cropping as label evasion.

Published consequences that can be stated precisely:

- `NSFW_HIGH_PRECISION` can produce an interstitial in the base Home policy for viewers who
  have not enabled sensitive media.
- `NSFW_HIGH_PRECISION` and `NSFW_HIGH_RECALL` are OON drop rules in Home Recommendations.
- logged-out and underage viewers can be dropped from sensitive media; viewers without a
  stated age can also be dropped in listed age-gating jurisdictions.
- tweet-level flags, author adult flags, NSFW avatar/banner labels, and account-level safety
  labels can independently reduce recommendation eligibility.

## Published X ranking reference — snapshot 2026-08-13

Use this section only as a dated reference. If the user asks about the **current** algorithm
after this snapshot, verify the official repository before quoting exact values.

The published `RankingScorer` combines each viewer's model-predicted probability of an
action with configurable weights. The numbers below are not points awarded for public
action counts and cannot be used to calculate a post's score.

Selected published defaults at commit `a389166`:

| Predicted action | Default weight |
|---|---:|
| Favorite | 0.5 |
| Reply | 5 |
| Retweet | 1 |
| Share | 2 |
| Share via DM | 5 |
| Share via **copying the X post link** | 20 |
| Follow author | 4 |
| Open external link | 0.2 |
| Video open / quality video view | 0.05 / 0.05 |
| Continuous dwell time | 0.004 |
| Not interested | -43.2 |
| Block author | -31.2 |
| Mute author | -58.8 |
| Report | -234 |

Critical interpretations:

- A GitHub click is `open_link`, not `share_via_copy_link`. Do not tell users that adding a
  repository URL earns the copy-link weight.
- The published scorer shows no hard external-link penalty. It gives `open_link` a small
  positive weight, but an outbound click can still reduce opportunities for later on-platform
  actions. Present that as an indirect behavioral hypothesis, not a coded penalty.
- The published bidirectional-follow reply boost applies to eligible original posts from
  mutually followed authors. It does not mean that a back-and-forth reply chain receives a
  special "bidirectional conversation" multiplier.
- Default out-of-network factors are `0.75` generally and `0.5` for topic OON candidates;
  these are configurable and not a ban on OON content.
- Author diversity is applied within the candidate slate. With the published defaults,
  successive same-author candidates are approximately multiplied by `1`, `0.625`, `0.4375`,
  `0.34375`, approaching a `0.25` floor. It is not a strike after the third daily post.
- The Home filter removes replies and reposts from accounts the viewer does not follow.
  Threads still help existing readers, notifications, profile conversion, and conversation.
- Bookmarks appear in engagement history and retrieval features, but this published weighted
  scorer has no separate bookmark head. Do not invent a direct bookmark coefficient.
- Likes have a smaller coefficient than replies, but are more common. Calling them worthless
  ignores both propensity and the rest of the model.
- Ranking experiments can override production defaults for traffic. Quote the commit and date.

## Worked case: @copenzafan

This is a teaching snapshot captured on **2026-08-14**, not live account analytics. The
logged-out timeline was incomplete; 16 identifiable recent root posts were used.

Baseline for the found sample:

- median: 4 likes and about 254 views;
- excluding the two clearest standouts: about 4 likes and 240 views on average;
- the observed ordinary range broadly matched 1–9 likes and 50–300 views.

Selected posts:

| Post | Public snapshot | What it actually shows |
|---|---|---|
| [CanvasTTY demo](https://x.com/copenzafan/status/2084896539512635750) | 43 likes, 8 replies, 7 reposts, 8 bookmarks, 2.2k views | An original product concept, visible proof, and a useful audience problem worked together. The GitHub URL was in a self-reply, so the win cannot be credited to an external link in the root. |
| [Second CanvasTTY video](https://x.com/copenzafan/status/2085066251043258590) | 5 likes, 0 replies, 274 views | A long product video by itself was not sufficient; novelty and framing mattered. Posting another root on the same product the same day likely made it compete for attention. |
| [Cool Cat story](https://x.com/copenzafan/status/2085349228755210519) | 22 likes, 10 replies, 4 reposts, 453 views | Strong community conversation and personal stakes, but not broad reach. Call it a conversation winner, not a reach winner. |
| [Choirboy prompt post](https://x.com/copenzafan/status/2087224574568280296) | 9 likes, 0 replies, 2 bookmarks, 256 views | A niche "secret/deep-tech" angle reached the normal range but did not create discussion. It needs a sharper demonstrated outcome or a question experts can answer. |
| [Short AI lesson](https://x.com/copenzafan/status/2087567420709871758) | 1 like, 51 views | The thought had no visible proof, specificity, or tension. This supports improving the premise, not a blanket ban on text posts. |
| Sensitive Minimax H3/Krea cosplay experiment (URL not supplied) | User-provided snapshot: 6,374 views and 35 bookmarks | A major reach/depth outlier relative to the account baseline. It supports testing strong visual technical demos; it does not prove that NSFW receives a ranking boost. Bookmark count is observed, while dwell and the exact distribution path were not measured. |

Preserve the sensitive post as a **user-provided** result until its URL or native analytics
screenshot is available. Do not silently promote it to independently verified public data.

The account had about 1,294 followers at capture time. The published new-author cold-start
boost used a default follower cap of 1,000, so the account did not qualify under that snapshot.
The post may have been published at a different follower count, but do not attribute its reach
to cold-start without follower count and eligibility evidence from the publication date.

### Advice derived from the case

1. Lead with original visual build proof; do not reduce the lesson to "post more video."
2. Give each root a distinct promise. Put repository, nodes, caveats, and deeper proof in a
   self-reply when that keeps the root focused.
3. Use personal stories when there is a real stake and recognizable community, while judging
   them by conversation rather than raw reach.
4. Turn technical comparisons into a decision: show test conditions, winner, failure, and
   what the reader should do differently.
5. Replace generic engagement CTAs with a concrete value exchange.
6. Do not make sensitive content the account's main discovery engine: labels can erase its
   out-of-network advantage even when visible viewers watch for longer.

## Official sources for the snapshot

- [X Open Source announcement](https://x.com/XOpenSource/status/2087951962004230428)
- [xai-org/x-algorithm repository](https://github.com/xai-org/x-algorithm)
- [Referenced source commit](https://github.com/xai-org/x-algorithm/commit/a389166f6cf5da70a286b568c87695d4dcdce3a1)
- [Published parameters](https://github.com/xai-org/x-algorithm/blob/a389166f6cf5da70a286b568c87695d4dcdce3a1/home-mixer/params/param.rs)
- [Ranking scorer](https://github.com/xai-org/x-algorithm/blob/a389166f6cf5da70a286b568c87695d4dcdce3a1/home-mixer/scorers/ranking_scorer.rs)
- [Visibility rules](https://github.com/xai-org/x-algorithm/blob/a389166f6cf5da70a286b568c87695d4dcdce3a1/visibility-filtering/rules/registry.rs)
- [OON reply/repost filter](https://github.com/xai-org/x-algorithm/blob/a389166f6cf5da70a286b568c87695d4dcdce3a1/home-mixer/filters/oon_reply_retweet_filter.rs)
