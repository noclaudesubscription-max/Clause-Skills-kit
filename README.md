# Skills Starter Pack

A portable copy of Claude Code skills, ready to drop into a new machine's
global skills folder.

## Install on another desktop

Copy every subfolder in this pack into your global Claude Code skills
directory, then restart/reopen Claude Code.

**Windows (PowerShell):**
```powershell
Copy-Item -Path "path\to\Skills Starter Pack\*" -Destination "$env:USERPROFILE\.claude\skills\" -Recurse -Force
```

**macOS / Linux (bash):**
```bash
cp -r "path/to/Skills Starter Pack/"* ~/.claude/skills/
```

Claude Code picks up skills from `~/.claude/skills/<skill-name>/SKILL.md`
automatically — no restart of the OS needed, just start a new session.

## What's included

### Design & UI
| Skill | Purpose |
|---|---|
| `frontend-design` | Distinctive, intentional visual design guidance — avoids templated-looking UI |
| `ui-ux-pro-max` | Design intelligence: 50+ styles, 161 palettes, 57 font pairings across 10 stacks |
| `web-design-guidelines` | Reviews UI code against Vercel's Web Interface Guidelines |
| `vercel-react-best-practices` | React/Next.js performance optimization guidelines |
| `vercel-composition-patterns` | React composition patterns — compound components, render props, context |
| `vercel-react-native-skills` | React Native/Expo performance and mobile-specific best practices |
| `bencium-controlled-ux-designer` | Systematic, accessible UX design guidance; always asks before design decisions |
| `motion-framer` | Motion (Framer Motion) animation library guidance |
| `website-cloner-animator` | Turns a URL/screenshot/Figma export into a production-ready animated website |

### Accessibility
| Skill | Purpose |
|---|---|
| `accesslint-audit` | Full WCAG 2.2 audit-and-fix workflow |
| `accesslint-scan` | Locates live-page accessibility violations via CDP |
| `accesslint-diff` | Diffs accessibility violations against a baseline/branch |

> These three expect an `accesslint` MCP server to be connected. Without it,
> the skill files are present but live-DOM auditing won't work.

### Framer
| Skill | Purpose |
|---|---|
| `framer` | Design/edit/publish Framer websites. Requires `npx @framer/agent@latest setup` first. |
| `framer-code-components` | Framer code-component authoring guidance |
| `framer-project-rw2FB3HU0jEe9zIusTs8` | ⚠️ Scoped to one specific Framer project — only useful if the new machine has access to that same project. Safe to delete otherwise. |

### Other
| Skill | Purpose |
|---|---|
| `human-like-browser-operator` | Careful, human-paced browser automation |
| `intraday-trailing-stop` | Intraday trailing stop-loss trading automation |
| `twitter-post-generation-skill` | Turns a blog post URL into a designer-focused X/Twitter thread |
| `twitter-posting-skill` | End-to-end research → draft → post pipeline for Blink Studio's X account |
| `local-website-hosting` | Shares a locally-running site/app via a live public URL using a Cloudflare Quick Tunnel — no upload, no account, data never leaves the machine. Link only works while the machine + tunnel process are running. |
| `html-creative` | Compresses a full web app + its data into one self-contained HTML file (all JS/CSS/data inlined) that opens via `file://` with zero server and zero network requests — a portable snapshot, not a live view. |

### Ponytail ("laziest solution that works")
Source: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)

| Skill | Purpose |
|---|---|
| `ponytail` | Main mode — pushes toward the shortest, simplest solution: stdlib/native features before dependencies, question whether code needs to exist at all |
| `ponytail-review` | Code review focused only on over-engineering — what to delete |
| `ponytail-audit` | Whole-repo audit for over-engineering — ranked list of what to cut |
| `ponytail-debt` | Harvests `ponytail:` comments into a tracked debt ledger |
| `ponytail-gain` | Scoreboard of ponytail's measured impact (less code/cost, more speed) |
| `ponytail-help` | Quick reference for all ponytail commands |

### Token optimization
| Skill | Purpose |
|---|---|
| `token-optimization` | Minimizes token/context usage while preserving correctness — narrow file reads, proportional verification, compact final responses. |

> ⚠️ This one has `disable-model-invocation: true` in its frontmatter, unlike every other skill in this pack. It will **not** auto-trigger based on matching your request — it only runs when explicitly invoked (e.g. `/token-optimization <task>`), regardless of which machine it's installed on.

## Custom slash commands

Unlike the skills above (which live in `skills/` and are picked up
automatically based on context), the files in `commands/` are custom
**slash commands** — install them into `~/.claude/commands/` instead of
`~/.claude/skills/`, and invoke them explicitly (e.g. `/commit`).

Source: [anthropics/claude-code plugins](https://github.com/anthropics/claude-code/tree/main/plugins)

| Command | Purpose |
|---|---|
| `/code-review` | Automated PR code review using multiple specialized agents with confidence-based scoring. Needs `gh` CLI, authenticated. |
| `/commit` | Creates a single git commit from the current staged/unstaged changes. No `gh` needed — purely local. |
| `/commit-push-pr` | Commits, pushes, and opens a PR in one step. Needs `gh` CLI, authenticated, and a folder that's a git repo with a GitHub remote already configured. |
| `/clean_gone` | Cleans up local branches whose remote has been deleted |

`/code-review` and `/commit-push-pr` talk to GitHub directly (reading/posting PRs), so they need the GitHub CLI installed and logged in on the new machine:

```powershell
winget install --id GitHub.cli
gh auth login
```
(`gh auth login` opens a browser for a one-time device code — no manual token handling needed.) `/commit` doesn't need any of this since it only touches the local git repo.

**Windows (PowerShell):**
```powershell
Copy-Item -Path "path\to\Skills Starter Pack\commands\*" -Destination "$env:USERPROFILE\.claude\commands\" -Recurse -Force
```
**macOS / Linux (bash):**
```bash
cp -r "path/to/Skills Starter Pack/commands/"* ~/.claude/commands/
```

> Note: `anthropics/claude-code/plugins` also has a `frontend-design`
> plugin, but its skill content is byte-identical to the `frontend-design`
> skill already in this pack — nothing extra to install there.

## Note

`accesslint-*` needs its MCP server, and `framer*` skills need the Framer
agent/project setup on the new machine — copying the skill files alone
won't wire those up.
