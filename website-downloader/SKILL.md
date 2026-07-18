---
name: website-downloader
description: Recursively mirror websites (including dynamic Vite code-split chunks, dynamic WebP thumbnails, and API payloads), set up a multi-threaded streaming server, and cache database POST routes locally.
---

# Website Downloader Skill

Use this skill when you need to completely download, patch, and run an existing web application or website on local hosting in a self-contained, offline-compatible manner.

## Key Phases

### Phase 1: Recursively Download Static Chunks & HTML
1. Locate index pages and crawl links.
2. Search JavaScript/CSS files for Vite bundle chunks matching `[name]-[hash].[ext]` and download them recursively.
3. Keep all files in a relative folder matching the site's path structure (e.g. `/work/index.html` for path `/work`).

### Phase 2: Crawl API Payloads & Predict WebP Permutations
1. Standard template engines request JSON payloads (e.g. `/api/posts/_services_branding`). Replace path slashes with underscores and fetch them.
2. Scan JSON data for files under `/uploads/`.
3. Predict and download dynamically sized WebP thumbnail/favicon permutations that the client-side code creates at runtime:
   - `/thumbs/{name}_project-logo_{ext}.webp`
   - `/thumbs/{name}_showcase-media_{ext}.webp`
   - `/thumbs/{name}_project-landscape-lg_{ext}.webp`
   - `/thumbs/{name}_opengraph.png`
   - `/thumbs/{name}_favicon-32.png`

### Phase 3: Set Up a Multi-Threaded Range-Capable Local Server
1. Standard servers are single-threaded; streaming video blocks them. Use `http.server.ThreadingHTTPServer`.
2. Implement **HTTP 206 Range (Partial Content)** header parsing to allow Safari and modern browsers to stream media.
3. Reroute `/api/media-stream/{filename}.mp4/` locally to `/uploads/{filename}.mp4`.
4. Overwrite standard MIME maps to prevent Windows registry pollution from serving `.js` chunks as `text/plain`.

### Phase 4: Cache POST Requests Offline
1. The app might call `POST /api` to sync layout/post options.
2. Generate an MD5 hash of the POST request body.
3. Save the response payload to `api/post_cache/{hash}.json`.
4. Serve subsequent POST requests with matching bodies directly from this local cache.

---

## Critical Windows Caveats

> [!WARNING]
> Under Windows, python's console `sys.stdout` will crash with `UnicodeEncodeError` (e.g. `'charmap' codec can't encode character...`) if you print raw response bodies containing non-ASCII Unicode characters (like `\u06f8`). 
> NEVER print raw request/response payloads directly to stdout. Keep logging safe and simple.

---

## Support Scripts

Copy the scripts located in the `scripts/` folder of this skill to automate the process:
*   [crawler.py](file:///d:/Blink%20Studio/Portfolio/.agents/skills/website-downloader/scripts/crawler.py)
*   [download_api.py](file:///d:/Blink%20Studio/Portfolio/.agents/skills/website-downloader/scripts/download_api.py)
*   [server.py](file:///d:/Blink%20Studio/Portfolio/.agents/skills/website-downloader/scripts/server.py)
