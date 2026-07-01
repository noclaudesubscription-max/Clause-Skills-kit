---
name: html-creative
description: Compresses a full web app (React/Vite or similar) plus its data into one fully self-contained HTML file that runs with zero server, zero build tooling, and zero network requests for the app itself — just open the file in a browser. Use when the user asks to "make this a single HTML file", "bundle this into one file", "let me share this dashboard/app without hosting it", "make this work offline", "compress this into an HTML file I can email/send", or wants to hand someone a working copy of an app without exposing any server, port, or data upload. Not for apps that require a real backend (auth, databases, server-side APIs) — only for apps whose only "backend" is static data that can be baked in at build time.
metadata:
  version: 1.0.0
---

# HTML Creative (single-file app bundling)

## What this is for

Turning an existing built web app into one standalone `.html` file that:
- Has all JS and CSS inlined — no separate `<script src>`/`<link href>` files.
- Has its data baked directly into the HTML as an embedded JS value — no
  `fetch()` of a JSON file needed at runtime.
- Opens correctly via `file://` (double-click, drag into a browser), not
  just from a web server.
- Makes zero network requests for the app's own functioning. (An external
  font/CDN import is the one common exception — see Caveats.)

This is for sharing something with someone else *without* uploading data
anywhere, running a server, or opening a port. You just send the file
(email, USB, chat attachment) and it runs entirely in their own browser on
their own machine. It's the opposite of the `local-website-hosting` skill
(which tunnels a live server) — this one produces a portable artifact with
no live component at all once built.

## When NOT to use this

- The app needs a real backend at runtime (authentication, a database,
  server-side API calls, anything that must happen on a server) — a
  single static file can't do that. This only works when the app's only
  external dependency is data that's knowable at build time.
- The user wants the data to stay live/current without rebuilding — a
  single-file export is a **snapshot**, not a live view. Every time the
  underlying data changes, the file must be rebuilt and re-shared.

## Prerequisites

Works cleanly on a Vite-based app (React, Vue, Svelte, vanilla). The
technique generalizes to any bundler that has an equivalent "inline
everything" plugin (e.g. Parcel supports this natively; webpack via
`html-webpack-inline-source-plugin`), but the steps below assume Vite.

## Steps

### 1. Install the inlining plugin

```bash
npm install -D vite-plugin-singlefile
```

### 2. Create a SEPARATE build config — do not modify the main one

Add `vite.singlefile.config.js` (or `.ts`) alongside the existing
`vite.config.js`. Keep the normal dev/build config completely untouched —
the app needs to keep working normally in dev mode and in any existing
deployment; this is an additional build target, not a replacement.

```js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react'; // swap for the actual framework plugin in use
import { viteSingleFile } from 'vite-plugin-singlefile';
import fs from 'node:fs';
import path from 'node:path';

// Adjust to wherever the app's runtime data actually lives.
const dataPath = path.resolve(__dirname, 'path/to/data.json');

function embedAppData() {
  return {
    name: 'embed-app-data',
    transformIndexHtml(html) {
      const json = fs.readFileSync(dataPath, 'utf8');
      const script = `<script>window.__APP_DATA__ = ${json};</script>`;
      return html.replace('</head>', `${script}</head>`);
    },
  };
}

export default defineConfig({
  plugins: [react(), embedAppData(), viteSingleFile()],
  build: {
    outDir: 'dist-singlefile',
    assetsInlineLimit: Infinity, // inline images/fonts as data URIs too, not just JS/CSS
    cssCodeSplit: false,          // one CSS bundle, so it can be fully inlined
  },
});
```

Add an npm script so it's a one-command rebuild later:
```json
"build:standalone": "vite build --config vite.singlefile.config.js"
```

### 3. Make the app read embedded data first, falling back to its normal data source

Find wherever the app currently fetches its runtime data (an API call, a
`fetch('/data.json')`, etc.) and make it check for the embedded global
first:

```js
function getEmbeddedData() {
  return typeof window !== 'undefined' ? window.__APP_DATA__ : undefined;
}

// In the data-loading hook/function: if getEmbeddedData() returns
// something, use it synchronously and skip the network fetch entirely.
// Otherwise, fall through to the existing fetch/API call unchanged.
```

This keeps ONE codebase serving both the normal live app and the
standalone snapshot — no forked/duplicated app logic.

### 4. Fix routing for `file://` compatibility

If the app uses client-side routing with a history-API-based router
(e.g. React Router's `BrowserRouter`), switch it to a hash-based router
(`HashRouter`). Browsers restrict `history.pushState` under the `file://`
protocol in ways that break `BrowserRouter` navigation (silent failures or
security errors) — `HashRouter` uses URL fragments (`#/page`) instead,
which work identically under `file://`, `http://`, and `https://`. This
is a one-line import swap and works fine in every delivery mode, so it's
safe to make this change globally rather than conditionally.

### 5. Build and verify

```bash
npm run build:standalone
```

Check the output is genuinely self-contained before treating it as done:
```bash
grep -c 'src="/' dist-singlefile/index.html   # expect 0 — no local script/asset refs left
```
A remaining external `<link>`/`<script>` pointing at a CDN (e.g. Google
Fonts) is expected and fine — that's a progressive enhancement, not a
functional dependency (see Caveats).

Then actually load the built file and confirm:
- The page renders real content, not a blank screen (check
  `document.body.innerText`, not just that it "loaded" — a blank
  React root with no errors can look deceptively fine from a screenshot
  alone if the screenshot tool hangs on some unrelated animation/chart
  render; reading the DOM text content is more reliable).
- `window.__APP_DATA__` (or whatever it was named) is actually populated.
- Client-side navigation between at least 2-3 different routes/pages
  works and shows the right content for each.
- No console errors.

If you need to preview it through a local static file server for
verification (some verification tools require an http:// origin), serve
it from an **isolated temp directory containing only the one file** —
serving it from a directory that also contains a same-named source folder
(e.g. a file `foo.html` next to a real folder `foo/`) can cause
clean-URL-rewriting static servers to resolve the wrong thing and show a
blank/wrong page. That's a serving artifact, not a bug in the file itself
— double-check by reading `document.body.innerText` before assuming the
build is broken.

### 6. Copy the result to its final shareable filename

```bash
cp dist-singlefile/index.html ./the-name-the-user-wants.html
```

## Caveats to tell the user

- **This is a snapshot, not live.** If the underlying data changes, the
  file must be rebuilt and re-shared — it will not reflect any future
  changes on its own.
- **Any genuinely external resource still needs network.** A Google
  Fonts `@import`/`<link>`, a CDN-hosted script, an external image URL —
  none of those get inlined by this technique unless explicitly converted
  to a data URI first. The app should still work fully offline; it just
  won't get the exact intended fonts/assets without connectivity. Say
  this plainly rather than implying full offline fidelity if such
  references remain.
- **File size grows.** Inlining bundles everything (including base64
  assets) into one file, so it will be noticeably larger than the
  original multi-file build. This is an expected, acceptable tradeoff for
  portability, not a bug.
- **No live component at all.** Unlike a tunnel-based sharing approach,
  there is nothing running once the file is built — no server to stop,
  no process to manage, no way to push a live update. That's the whole
  point (true zero-exposure sharing), but make sure the user understands
  they're getting a point-in-time export, not a live view.
