---
name: local-website-hosting
description: Share a locally-running website/app/dashboard with someone else via a live public URL, without uploading any files or data anywhere. Opens a tunnel (Cloudflare Quick Tunnel) straight to the user's own machine so the site keeps running on their laptop and all data stays there. Use when the user asks to "host this locally and share a link", "give me a shareable link without uploading my data", "expose my local server", "let someone else see my localhost", "tunnel my dev server", "share my dashboard without putting the data online", or similar. Do NOT use this for permanent/production hosting, or when the user explicitly wants the files copied to a static host (that's a different workflow — e.g. uploading a build to a hosting service).
metadata:
  version: 1.0.0
---

# Local Website Hosting (tunnel, not upload)

## What this is for

The user has something running locally (a dev server, a built static site
served by any local HTTP server, an app on localhost) and wants to hand
someone else a URL that shows it live — **without copying any files or
data off their machine**. The site stays served from their laptop; the
tunnel just forwards public traffic to it. When the laptop turns off or
the tunnel process stops, the link stops working. Nothing is stored
remotely — this is the opposite of a "publish/upload" flow.

This is the right tool when the user cares about:
- Not exposing their data to a third-party hosting provider
- A quick, temporary "look at this" link for a demo or review
- Zero setup cost (no account, no signup, no config file)

It is the WRONG tool when the user wants:
- A permanent URL that works even when their machine is off -> that needs
  real hosting (static hosting upload, a VPS, Vercel/Netlify, etc.)
- Guaranteed uptime or a fixed domain -> quick tunnels have neither

## Steps

### 1. Confirm (or start) the local server

Find out what's already running, or start it. Common cases:
- A dev server (Vite, Next.js, CRA, etc.) — usually `npm run dev`.
- A static build — serve it with any simple HTTP server if nothing is
  running yet.

Get the exact **port** it's listening on. Bind to all interfaces if the
tool needs a flag for that (e.g. Vite needs `--host` to accept
non-localhost Host headers over the network; without it the dev server
only listens on 127.0.0.1 and a tunnel can still reach it, so `--host` is
optional for this to work through a tunnel, but harmless to include).

Verify locally first, before touching the tunnel:
```
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:PORT/
```
Expect `200`. Don't proceed to the tunnel step until this passes — a
tunnel in front of a broken/not-yet-ready server just produces a Bad
Gateway later, which is confusing to debug through the extra layer.

### 2. Get `cloudflared`

Prefer Cloudflare's Quick Tunnel over `localtunnel`/`ngrok` free tiers:
- `localtunnel` (`npx localtunnel --port PORT`) shows visitors an
  "enter this IP as a password" interstitial page on first visit, which
  is confusing for a non-technical recipient, and its free relay is
  noticeably flaky (frequent random "Bad Gateway" errors even when the
  local server is healthy).
- `ngrok`'s free tier now requires an account/authtoken even for
  throwaway tunnels — extra friction for a quick share.
- `cloudflared`'s Quick Tunnel needs **no account, no signup, no
  authtoken**, and visitors land directly on the site with no
  interstitial.

Check if it's already installed:
```
command -v cloudflared
```
If missing, download the binary directly (no package manager needed):

**Windows:**
```
mkdir -p "$LOCALAPPDATA/cloudflared"
curl -sSL -o "$LOCALAPPDATA/cloudflared/cloudflared.exe" \
  "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
```
**macOS:**
```
curl -sSL -o /usr/local/bin/cloudflared \
  "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz"
# (Cloudflare ships macOS as a .tgz — extract, or use `brew install cloudflared` if Homebrew is available)
```
**Linux:**
```
curl -sSL -o /usr/local/bin/cloudflared \
  "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
chmod +x /usr/local/bin/cloudflared
```

`scripts/start-tunnel.sh` in this skill automates "check if installed,
download if not, start the tunnel, extract the URL" for the
curl/bash-available case (Windows Git Bash, macOS, Linux).

### 3. Start the tunnel, detached, with output captured to a file

Run it detached from the current shell so it outlives this command and
keeps serving after the conversation moves on:
```
nohup cloudflared tunnel --url http://localhost:PORT > cloudflared.log 2>&1 & disown
```
Wait a few seconds, then read the log file and extract the URL — it
prints a boxed line like:
```
|  https://some-random-words.trycloudflare.com  |
```

### 4. Verify through the tunnel, not just locally

A local 200 does not guarantee the tunnel works — dev servers commonly
reject unrecognized Host headers as a security measure. Test:
```
curl -s -o /dev/null -w "%{http_code}\n" https://THE-TUNNEL-URL/
```
If you get a 403 with a message like "Blocked request... not allowed. To
allow this host, add ... to `server.allowedHosts`" (this is a known Vite
behavior — protection against DNS rebinding attacks), the fix is to add
to the dev server config:
```js
server: { allowedHosts: true }
```
then **restart the dev server** (config changes need a restart) and
re-test the tunnel URL. Also check for any critical sub-routes the app
needs (e.g. an API/data endpoint the frontend fetches) and verify those
return 200 through the tunnel too — not just the root page.

### 5. Report the link, with the caveats stated plainly

Give the user the URL and be explicit about all of these — don't let them
assume it behaves like a normal hosted site:
- It only works while their machine is on, connected, and both the local
  server process and the `cloudflared` process keep running.
- The URL is not fixed — if the tunnel restarts (crash, machine sleep,
  asked to restart it), a brand-new random URL is issued and must be
  re-shared.
- Cloudflare's disclaimer: account-less Quick Tunnels have no uptime
  guarantee — fine for a demo, not for anything that needs to stay up
  unattended.
- No data left their machine — the tunnel only forwards live requests; it
  is not a copy/upload of any files.

## Cleanup

When the user is done sharing:
```
# find and stop the cloudflared process
```
Stopping `cloudflared` immediately kills the public URL. The local dev
server can keep running or be stopped independently — it's a separate
process.
