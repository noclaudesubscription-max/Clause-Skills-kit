# Worked example — last post made

This is the exact thread posted to @Blinkxstudio, end to end, as a concrete reference.

## Story chosen
"All the news about Anthropic's new AI fight with the White House" — specifically the June 26, 2026 development that Anthropic's Mythos 5 partially returned after a two-week export-control shutdown.

**Why it won the candidate ranking:** novelty 9, virality 9, discussion 10, future impact 9 — first public case of a US government order fully killing a frontier model for its own maker's staff, not just foreign customers.

## Sources actually read
- Primary/press: https://www.theverge.com/ai-artificial-intelligence/950026/anthropic-fable-mythos-ban-ai-shutdown
- Follow-up: https://www.theverge.com/ai-artificial-intelligence/958458/anthropic-mythos-5-is-back-trump-negotiations
- WSJ via Verge: Amazon CEO's conversations with the White House triggered the order
- Community: https://www.reddit.com/r/Anthropic/comments/1u7fu0z/ , https://www.reddit.com/r/claude/comments/1u4epu9/ , https://news.ycombinator.com/item?id=48609194 , https://news.ycombinator.com/item?id=48511072

## The insight (originality gate)
"The real story isn't the export ban. The real story is that Anthropic's own safety hype handed the government the language to justify the ban." This came from combining: (a) Anthropic's own launch-week marketing calling the models more dangerous than anything it had released, with (b) a Hacker News comment arguing Anthropic "painted themselves into that corner." Neither source alone stated this connection.

## Image
Real editorial photo used by The Verge for this story (their og:image), not a generated illustration:
`https://platform.theverge.com/wp-content/uploads/sites/2/2026/04/STK269_ANTHROPIC_2_D.webp?quality=90&strip=all&crop=0%2C10.732984293194%2C100%2C78.534031413613&w=1200`

Downloaded via the `browser_run_code_unsafe` blob-fetch-and-download technique (see SKILL.md Step 6), saved to `.playwright-mcp\anthropic-verge-editorial.webp`, attached to tweet 1.

## The final 7-tweet thread (verbatim, as posted)

**Tweet 1** (with image):
> Anthropic's flagship AI model just got banned by its own government for two weeks. The most interesting part isn't the ban. It's what caused it.

**Tweet 2:**
> A Friday-night export control order cut off Fable 5 and Mythos 5 for every foreign national — including Anthropic's own foreign-born employees, locked out of the thing they built.

**Tweet 3:**
> Here's what nobody's connecting: a week earlier, Anthropic had been calling these models more dangerous than anything they'd ever released. "Safeguards lifted." "Capabilities exceed any model we've made generally available."

**Tweet 4:**
> That language wasn't just marketing. It was the exact case a regulator needed.

**Tweet 5** (quotable line):
> If you spend a week telling the world your product is too dangerous to be safe, don't be shocked when the government takes you at your word.

**Tweet 6** (prediction):
> Watch what happens to AI launch announcements over the next six months. "Most capable model" survives. "Too dangerous to release" quietly disappears — not because labs got safer, but because their lawyers finally read the press release.

**Tweet 7** (open question):
> Curious what other founders think: is hyping danger as a feature finally becoming too risky to be worth it?

## Posting mechanics actually used
- All 7 tweets posted via `mcp__playwright__browser_*` tools (not the Chrome extension, not the standalone `x-post.js` script).
- Tweet 1 posted from `https://x.com/compose/post` with image attached via file-chooser + `browser_file_upload`.
- Each subsequent tweet: located the previous tweet's Reply button via `browser_snapshot`, clicked it, typed, re-snapshotted to verify exact text match before clicking Reply/Post.
- When refs went stale (timeline reordering after a post), navigated directly to the specific `/status/<id>` URL rather than re-scrolling the profile feed.
- X's `/i/graduated-access` bot-check page appeared after some — but not all — of the individual posts in this account's history; each time, the underlying post still went through. Flagged to the user but did not block posting.
