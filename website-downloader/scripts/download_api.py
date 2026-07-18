import os
import json
import urllib.request
import urllib.parse
import sys

# Parameterized values with defaults
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://wondermake.xyz"
TARGET_DIR = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
TIMEOUT = 15

# Parse domain from BASE_URL for generic checking
PARSED_BASE = urllib.parse.urlparse(BASE_URL)
DOMAIN = PARSED_BASE.netloc

PAGES = [
    "",
    "work",
    "about",
    "services",
    "contact",
    "journal",
    "privacy",
    "hosting",
    "terms",
    "services/branding",
    "services/website-design",
    "services/product-design",
    "services/design-support"
]

def log(msg):
    print(msg, flush=True)

def download_file(url, local_path):
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return True
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    log(f"Downloading: {url} -> {local_path}")
    for attempt in range(2):
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                content = response.read()
                with open(local_path, 'wb') as f:
                    f.write(content)
                log(f"Success ({len(content)} bytes)")
                return True
        except Exception as e:
            log(f"Attempt {attempt+1} failed for {url}: {e}")
    return False

# List to keep track of assets found in the JSON payload
discovered_assets = set()

def scan_dict_for_urls(d):
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, str):
                if v.startswith("/uploads/") or v.startswith("/thumbs/") or v.startswith("/assets/"):
                    discovered_assets.add(v)
                elif DOMAIN in v:
                    parsed = urllib.parse.urlparse(v)
                    if parsed.netloc == DOMAIN:
                        discovered_assets.add(parsed.path)
            else:
                scan_dict_for_urls(v)
    elif isinstance(d, list):
        for item in d:
            scan_dict_for_urls(item)

def generate_webp_thumbnails(upload_path):
    filename = os.path.basename(upload_path)
    if not filename or "." not in filename:
        return []
        
    name, ext = os.path.splitext(filename)
    ext_clean = ext.lstrip(".")
    
    presets = [
        "project-logo",
        "showcase-media",
        "project-landscape-lg"
    ]
    
    generated = []
    for preset in presets:
        generated.append(f"/thumbs/{name}_{preset}_{ext_clean}.webp")
        
    generated.append(f"/thumbs/{name}_opengraph.png")
    generated.append(f"/thumbs/{name}_opengraph-square.png")
    generated.append(f"/thumbs/{name}_favicon-32.png")
    generated.append(f"/thumbs/{name}_favicon-192.png")
    generated.append(f"/thumbs/{name}_favicon-180.png")
    
    return generated

def download_api_json(page_path):
    api_name = "_" + page_path.replace("/", "_")
    api_url = f"{BASE_URL}/api/posts/{api_name}"
    local_path = os.path.join(TARGET_DIR, "api", "posts", api_name)
    
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    log(f"Downloading API data: {api_url} -> {local_path}")
    try:
        req = urllib.request.Request(
            api_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            data = response.read()
            with open(local_path, 'wb') as f:
                f.write(data)
            
            try:
                json_data = json.loads(data.decode('utf-8'))
                scan_dict_for_urls(json_data)
            except Exception as je:
                log(f"Error parsing JSON for assets: {je}")
                
        return True
    except Exception as e:
        log(f"Failed to download API endpoint {api_url}: {e}")
        return False

def main():
    log(f"API Downloader Starting. URL: {BASE_URL}, Target Dir: {TARGET_DIR}")
    
    # 1. Download all JSON payloads
    for page in PAGES:
        download_api_json(page)
        
    # 2. Expand discovered assets to include webp thumbnails for all uploads
    final_queue = set()
    for asset in discovered_assets:
        final_queue.add(asset)
        if asset.startswith("/uploads/"):
            webps = generate_webp_thumbnails(asset)
            final_queue.update(webps)
            
    log(f"\nDiscovered {len(discovered_assets)} base assets, expanded to {len(final_queue)} files including thumbnails. Starting download...")
    
    # 3. Download everything in final_queue
    downloaded_count = 0
    for asset in sorted(list(final_queue)):
        clean_asset = asset.lstrip("/")
        download_url = f"{BASE_URL}/{clean_asset}"
        local_path = os.path.join(TARGET_DIR, clean_asset)
        
        if clean_asset in PAGES or (clean_asset + "/") in PAGES or clean_asset in [p.replace('/', os.sep) for p in PAGES]:
            continue
            
        if download_file(download_url, local_path):
            downloaded_count += 1
            
    log(f"\n--- API Downloader Finished! ---")
    log(f"Downloaded files in this run: {downloaded_count}")

if __name__ == "__main__":
    main()
