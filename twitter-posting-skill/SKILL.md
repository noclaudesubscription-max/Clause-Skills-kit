---
name: twitter-posting-skill
description: Full end-to-end pipeline for researching, writing, and posting an original X/Twitter thread for Blink Studio — from finding a story, through multi-source research and an originality gate, to drafting, self-editorial review, sourcing a real (non-AI) image, and posting tweet-by-tweet with verification. Always use this skill whenever the user asks to "make a post," "write a thread," "post about [story]," or "find something interesting and post it" — even if they don't name this skill directly. This is the master workflow; it supersedes ad-hoc posting.
---

# Twitter Posting Skill

This is the complete workflow used to go from "make a post" to a verified, live X thread on the user's account (@Blinkxstudio at time of writing). It exists so a fresh session with no prior context can reproduce the exact same process and output quality.

## Non-negotiable rule: confirmation before posting

**Always show the user the final drafted thread and get an explicit go-ahead before clicking Post on anything.** This is not a style preference — it is a hard rule that does not get relaxed by a standing instruction like "just do it yourself from now on." Every individual post needs its own confirmation. The rest of the pipeline (research, drafting, image sourcing) can run without interruption; only the actual publish action requires a fresh "yes" each time.

## Tools used, and where they come from

| Tool | Source | Purpose |
|---|---|---|
| `mcp__playwright__browser_navigate` | Playwright MCP server (registered via `claude mcp add playwright npx @playwright/mcp@latest`) | Navigate to URLs (article pages, x.com compose/profile/status pages) |
| `mcp__playwright__browser_snapshot` | same | Get an accessibility-tree snapshot of the page — this is how you find element refs (textboxes, buttons) and verify text actually entered correctly. Prefer this over screenshots for anything you need to act on. |
| `mcp__playwright__browser_click` | same | Click an element by ref or CSS selector |
| `mcp__playwright__browser_type` | same | Type/fill text into an element |
| `mcp__playwright__browser_file_upload` | same | Upload a file into an active file-chooser modal state (must be triggered by clicking the upload button first) |
| `mcp__playwright__browser_run_code_unsafe` | same | Execute JS in the Playwright server process with access to the real `page` object — this is how real images get downloaded (see Image Sourcing below). No Node `fs`/`require` available in this sandboxed function; only `page`'s own APIs. |
| `mcp__playwright__browser_take_screenshot` | same | Visual screenshot when a snapshot alone doesn't explain what's on screen (e.g. diagnosing a click-intercepted-by-overlay error) |
| `mcp__playwright__browser_wait_for` | same | Wait for text to appear/disappear — more reliable than guessing with snapshots when timing is uncertain |
| `mcp__playwright__browser_press_key` | same | Dismiss stuck overlays (e.g. `Escape`) |
| `mcp__7fa0cd26-10d3-41f2-aa50-a6565ce9c88d__firecrawl_search` | Firecrawl MCP server (user's configured web data provider) | Primary web/news search — supports `sources: [{"type":"news"}]` and `tbs: "qdr:d"` for today-only results |
| `mcp__7fa0cd26-10d3-41f2-aa50-a6565ce9c88d__firecrawl_scrape` | same | Full-page scrape of a chosen article (markdown + links + metadata, including og:image) |
| `WebFetch` | built-in | Fallback for fetching/summarizing a page when Firecrawl isn't the better fit |
| `Write` / `Read` / `Edit` | built-in | Save the research dossier and any local post-asset files |
| `Bash` | built-in | `mkdir` for post-asset folders; also used to call the AgentMail REST API via `curl` (no dedicated AgentMail MCP tool exists) — see Step 7 |

These deferred Playwright tools may not appear in a fresh session's tool list immediately — call `ToolSearch` with query `"playwright browser"` to load them; if the server is still connecting, ToolSearch will wait for it.

Two companion skills this pipeline draws on — invoke them as sub-steps, don't duplicate their content here. A consolidated copy of all three skills together (this one plus its two companions) is also kept in the project folder at `C:\Users\mayan\Downloads\Claude Cowork\Social Media\skills\` as a single bundle for human reference:

```
skills/
├── twitter-posting-skill/          (this skill — the master workflow)
├── twitter-post-generation-skill/
└── human-like-browser-operator/
```

- **human-like-browser-operator** (`C:\Users\mayan\.claude\skills\human-like-browser-operator\SKILL.md`) — observe-before-acting, verify-after-acting browser discipline. Apply its principles throughout Step 8 below.
- **twitter-post-generation-skill** (`C:\Users\mayan\.claude\skills\twitter-post-generation-skill\SKILL.md`) — the original 5-tweet (Hook/What happened/Why care/Application/Takeaway+Source) structured format. Use that exact structure when the user asks for "the designer-angle thread from a blog post" specifically. For the open-ended "find today's most interesting AI story" flow, use the natural-flow voice described in this skill instead (no numbering, no 🧵).

## The full pipeline

### Step 1 — Establish the source
If the user gives a URL, use it. If they say "find something interesting" or "make a daily post," research today's AI news:
- Search `firecrawl_search` with `sources: [{"type":"news"}]` and `tbs: "qdr:d"` for today-only results, plus a broader web search across Hacker News / Reddit for community angle.
- Read at least one primary source, one independent press piece, and one community-discussion thread before picking a story.
- Score candidates on novelty, practical value, virality, discussion potential, future impact. Pick the highest-scoring one and be able to explain why in one sentence.

### Step 2 — Build a research dossier
Don't write from a single article. Gather:
1. **Primary source** — the official announcement/blog/statement. What was claimed, what caveats were given.
2. **Independent analysis** — press coverage (The Verge, TechCrunch, etc.). How journalists are framing it, what they emphasize.
3. **Community perspective** — Reddit, Hacker News, X. What builders are actually saying — confusion, criticism, unexpected angles. This is often where the real insight hides.

Compare all three: what's universally agreed, where do they disagree, what does only one source mention, what is nobody connecting. Save this as `research_dossier.md` in a `posts/<slug>/` folder. Do not show its contents to the user unless asked — it's an internal working document.

Full section-by-section dossier template: see `references/research-dossier-template.md`.

### Step 3 — Originality gate
Before writing a word, complete this sentence: **"The real story isn't ___. The real story is ___."** If the honest answer is just "what launched," you don't have a thread yet — go back to Step 2 and look harder at the community-perspective sources, since press coverage rarely contains the missed angle.

The thread must contain at least one insight that doesn't appear verbatim in any single source — it has to come from combining sources, not from any one of them.

### Step 4 — Write the thread
Voice and formatting rules (apply always, not just when explicitly asked):
- No thread numbering (no "1/5", "2/7"), no "Thread:", no "Part 1", no 🧵 unless the user explicitly asks for it.
- First tweet starts directly with the hook — never "Here's a thread" or similar.
- Vary sentence length. Use whitespace. One new idea per tweet, not a blog post split into paragraphs.
- Include one standalone quotable line — something that reads fine reposted with zero context.
- Include one explicit prediction.
- End on an open question or opinion, not a summary/conclusion.
- Avoid AI-tell vocabulary: "leverage," "synergy," "paradigm," "game-changing," "powerful," "revolutionary," "workflow shift" used as a crutch. Use concrete specifics instead (names, dates, exact quoted phrases from the source).
- If an image will attach to one tweet, that tweet's text should naturally make sense with the image, not just ignore it.

### Step 5 — Self-editorial review
Score the draft 1–10 on: scroll-stopping hook, original insight, human voice, specificity, memorability, storytelling flow, emotional impact, discussion potential, visual synergy (if image attached), AI-detection (no template tells, no uniform paragraph lengths). Anything scoring below 8 gets rewritten before showing the user. Full rubric: see `references/research-dossier-template.md`.

### Step 6 — Source a real image (never AI-generated)
Hard rule: only use a real image that actually appears in a source article (a photo, a diagram, an og:image). Never generate one, even if asked for an "image concept" — if generation is requested, produce a written creative brief but flag clearly that it is not a real downloadable asset and the skill's image rule means it won't be used in the actual post.

**The real-download technique** (this is the part that makes image attachment actually work — figured out after several failed approaches):
1. Plain HTTP fetch of an image URL and saving via Bash/`fs` does NOT work — Bash and Write/Edit operate in a sandboxed filesystem that is separate from the real machine the Playwright browser controls. A file "saved" via Bash is invisible to Playwright's upload tool.
2. The Chrome-extension-based `file_upload` tool also does not work for this — it only accepts files from an explicit pre-shared allowlist (chat attachments or specific session folders), and a freshly downloaded file is never on that list.
3. **What actually works:** use `browser_run_code_unsafe` to run real Playwright code against the live `page` object:
   ```js
   async (page) => {
     const url = 'https://...the-real-image-url...';
     const [download] = await Promise.all([
       page.waitForEvent('download', { timeout: 20000 }),
       page.evaluate(async (u) => {
         const res = await fetch(u);
         const blob = await res.blob();
         const objUrl = URL.createObjectURL(blob);
         const a = document.createElement('a');
         a.href = objUrl;
         a.download = 'whatever.jpg';
         document.body.appendChild(a);
         a.click();
       }, url)
     ]);
     const savedPath = await download.path();
     return { savedPath, suggested: download.suggestedFilename() };
   }
   ```
   Fetching as a blob and using an object URL (rather than the remote URL directly on the `<a download>`) is what actually triggers the browser's native download event — a direct cross-origin `href` often gets ignored by the `download` attribute.
4. The tool's own log line tells you the real, usable path, e.g.: `Downloaded file whatever.jpg to ".playwright-mcp\whatever.jpg"`. That relative path, resolved against the project root, is what `browser_file_upload` can actually read — it's restricted to the project folder and its `.playwright-mcp` subfolder specifically.
5. To upload: click the "Add photos or video" button in the compose dialog (this opens a file-chooser modal state), then call `browser_file_upload` with the absolute path to that `.playwright-mcp\<filename>` file.

### Step 7 — Get confirmation via AgentMail (replaces in-chat confirmation)
Confirmation now happens over email instead of in chat. This does not relax the non-negotiable rule above — it just moves the channel.

**Setup (one-time, already done as of this writing):**
- AgentMail API key is stored in `.env` as `AGENTMAIL_API_KEY` — never print it, only reference it via the env var in shell commands.
- Sending inbox: `blinkstudio@agentmail.to` (created via `POST https://api.agentmail.to/v0/inboxes` with `{"username":"blinkstudio","display_name":"Blink Studio"}`).
- Destination: the user's own email (currently `noclaudesubscription@gmail.com`).
- AgentMail has no dedicated MCP tool — everything goes through its REST API via `curl` in Bash, with `Authorization: Bearer $AGENTMAIL_API_KEY`.

**Flow:**
1. Send the full drafted thread (every tweet, in order, plus which tweet the image attaches to) as the body of an email:
   ```bash
   set -a && source .env && set +a
   curl -s -X POST -H "Authorization: Bearer $AGENTMAIL_API_KEY" -H "Content-Type: application/json" \
     -d '{"to":["noclaudesubscription@gmail.com"],"subject":"Post confirmation needed","text":"<full thread text here>\n\nReply YES to confirm, or reply with changes."}' \
     https://api.agentmail.to/v0/inboxes/blinkstudio@agentmail.to/messages/send
   ```
2. Tell the user in chat that a confirmation email was sent, and wait. Per the user's stated preference, do not poll automatically — wait for the user to come back to the conversation and say they've replied.
3. When the user says they've replied, check the inbox for the actual reply content — do not just trust the user's chat summary of what they wrote, since the parsed reply text is the actual authorization record:
   ```bash
   curl -s -H "Authorization: Bearer $AGENTMAIL_API_KEY" https://api.agentmail.to/v0/inboxes/blinkstudio@agentmail.to/messages
   ```
   Find the message with `"labels":["received",...]` and a `thread_id` matching the confirmation email, and read its `preview`/body text.
4. **Parse for actual affirmative intent.** Only treat clear affirmatives ("yes", "confirmed", "go ahead", "post it") as a green light. Anything ambiguous, off-topic, or a requested change ("looks good but fix tweet 3") is NOT a confirmation to post as-is — go back to the user (in chat or another email) rather than guessing. A test reply like "I got the mail" is explicitly NOT a confirmation — it only confirms deliverability, not approval.
5. Only after a clear affirmative reply is found, proceed to Step 8.

### Step 8 — Post, tweet by tweet, with verification at every step
Apply `human-like-browser-operator` principles throughout. Concretely:
1. Navigate to `https://x.com/compose/post`.
2. Take a snapshot scoped to `[role=dialog][aria-modal=true]` to find the textbox ref (usually `data-testid="tweetTextarea_0"` inside the dialog — when there are two matches on the page, scope the selector to the dialog specifically).
3. Click the textbox, then type the tweet text.
4. If this tweet carries the image: click "Add photos or video" (opens file-chooser modal), then `browser_file_upload` with the real local path from Step 6.
5. Take another snapshot of the dialog and visually confirm the text rendered matches exactly what was approved, and the image attached if expected, and the Post/Reply button is enabled (not `[disabled]`).
6. Click Post.
7. Navigate to the user's profile or directly construct the next status URL from the page's own report, and take a snapshot to confirm the tweet is actually live with the expected text before doing anything else.
8. For each subsequent tweet in the thread: find the just-posted tweet's Reply button (refs go stale fast on this page — if a ref errors as "does not match any elements," re-snapshot rather than guessing), click Reply, type, verify, click Reply/Post again. If ref-finding via the home/profile timeline gets unreliable because of feed reordering, navigate directly to the specific tweet's `/status/<id>` URL and reply from there — more reliable than scrolling a timeline.
9. Watch for X redirecting to `/i/graduated-access` after posting — this is X's bot/automation-detection soft-restriction page. The post still usually goes through underneath it, but repeated triggers are a real signal about posting cadence on a new/unverified account, not noise. Mention it to the user if it appears; don't silently ignore it.

### Step 9 — Wrap-up
Tell the user it's done, list what each tweet said in brief, link to the thread, and mention if the bot-check page appeared at any point during this run.

## Worked example: the actual last post made

See `references/example-post.md` for the complete, verbatim 7-tweet thread that was posted (the Anthropic Mythos 5/Fable 5 export-control story), including the exact research angle, the image source URL and download technique used, and the live status URLs. Use it as the concrete reference for "what does a finished, correct output actually look like."
