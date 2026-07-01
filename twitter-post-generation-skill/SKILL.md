---
name: twitter-post-generation-skill
description: Turns a public blog post URL (especially an Anthropic/Claude blog post) into a designer-focused X/Twitter thread, with a relevant image pulled from the source article. Always use this skill whenever the user asks to "create a tweet/post/thread" from a blog link, asks to "turn this article into a Twitter post," mentions posting about a Claude/Anthropic blog update on X/Twitter, or asks for "designer angle" content from a URL — even if they don't say the word "skill" or name this skill directly.
---

# Twitter Post Generation Skill

Turn a blog post URL into an original X/Twitter thread written from a product/UI designer's point of view, for an audience of beginner-to-intermediate designers who are not deeply technical about AI.

## Who this is for

The reader is a product or UI designer, not an engineer. Every tweet should read like a designer explaining something useful to other designers — not a press release, not a news recap, not a technical changelog.

## Workflow

1. **Fetch the article.** Scrape or fetch the URL to get the full text and any images. If the URL redirects (e.g. claude.com/blog often redirects to anthropic.com/engineering or anthropic.com/news), follow the redirect and fetch the final URL.
2. **Find the core idea, not the summary.** Don't try to cover everything in the post. Pick the one idea most relevant to design/UX thinking — a workflow shift, a UX pattern (progressive disclosure, onboarding, feedback loops), a product problem being solved, or a mental model. Everything else in the article is discarded.
3. **Reinterpret, don't translate.** Write in your own words from scratch. Do not lift phrases or follow the article's sentence structure — if you can point to a sentence in the article that maps 1:1 to a tweet, rewrite it. The test: would this thread still make sense and feel original if someone had only heard about the article secondhand, not read it?
4. **Pick an image.** Use an image from the article itself (a diagram, screenshot, or illustration) if one exists and is relevant — never generate a new image. Download it locally (see Saving outputs below) rather than just linking it, so it's ready to attach when the user posts manually.
5. **Write the thread** using the structure and tone below.
6. **Present a preview** of the thread before considering the task done — show the text of each tweet, and mention where the image attaches.

## Thread structure (always exactly 5 tweets)

1. **Hook** — A short, curiosity-driven opening that makes a designer want to keep reading. Max 250 characters. End with 🧵. Pattern: state that most designers will miss why this matters, then contrast the surface feature against the deeper idea. Vary the exact wording each time — don't reuse the same template sentence-for-sentence across different posts.
2. **What happened** — Plain-English explanation of the update/idea, written for someone with zero technical background. No jargon. If a technical term is unavoidable, define it in the same breath. Max 250 characters. Attach the article's image to this tweet if one was found.
3. **Why designers should care** — Translate the update into a UX/product design lesson: what user or workflow problem does it solve, and what's the design thinking behind it? This is the tweet that should make a designer nod and think "oh, that's just [familiar design concept]." Max 250 characters.
4. **Real design application** — A concrete, actionable example of how a product designer would actually use this idea in their own work this week. Not abstract — name a specific behavior change (e.g. "package your design system into a doc your AI tools read on demand"). Max 250 characters.
5. **Design takeaway + source** — One sentence that crystallizes the lesson, formatted as:
   ```
   Design takeaway:
   [one sentence]

   Source:
   [URL]
   ```
   Max 250 characters total including the URL.

## Voice

Friendly, smart, direct, slightly educational, never robotic. Write like a sharp designer thinking out loud to peers, not a news bot summarizing a press release. Short sentences. No corporate language, no "in today's fast-paced world," no excessive exclamation marks.

## Hard rules

- Never copy sentences verbatim from the source article.
- Never paraphrase sentence-by-sentence (i.e. don't mirror the article's paragraph order and just reword each line — extract the idea first, then write fresh).
- Always include the source URL in the final tweet.
- Never use a generated/AI image — only use an image that actually appears in the source article, and only if it's genuinely relevant to the point being made. If no suitable image exists, say so and proceed without one rather than inventing one.
- Respect the 250-character cap per tweet.

## Saving outputs

When the user wants this saved (not just previewed), save into a folder named after the post topic, e.g. `posts/<slug>/`:
- `image.<ext>` — the downloaded source image
- `thread.md` — the 5 tweets in order, plus the source URL

Do not post anything automatically. This skill produces drafts for the user to review and publish themselves, unless a posting integration has been explicitly connected and the user has confirmed publishing for this specific post.

## Output format

Present the thread as 5 labeled tweets (Tweet 1 — Hook, Tweet 2 — What happened, etc.), and note which tweet the image attaches to. A rendered visual preview (e.g. a thread mockup) is a nice-to-have on top of this, not a replacement for showing the actual tweet text.
