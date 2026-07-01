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

## Note

`accesslint-*` needs its MCP server, and `framer*` skills need the Framer
agent/project setup on the new machine — copying the skill files alone
won't wire those up.
