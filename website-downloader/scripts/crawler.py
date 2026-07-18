import os
import re
import urllib.request
import urllib.parse
import sys

# BASE_URL and TARGET_DIR configured via arguments or defaults
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://wondermake.xyz"
TARGET_DIR = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
TIMEOUT = 15

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
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    # Skip if exists and non-empty
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        log(f"Skipping (already exists): {local_path}")
        return True
        
    log(f"Downloading {url} -> {local_path}")
    
    for attempt in range(2):
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                content = response.read()
                if len(content) > 0:
                    with open(local_path, 'wb') as f:
                        f.write(content)
                    log(f"Success ({len(content)} bytes)")
                    return True
                else:
                    log(f"Warning: downloaded 0 bytes from {url}")
        except Exception as e:
            log(f"Attempt {attempt+1} failed for {url}: {e}")
            
    # Clean up empty file if failed
    if os.path.exists(local_path) and os.path.getsize(local_path) == 0:
        try:
            os.remove(local_path)
        except:
            pass
    return False

def extract_assets(html_content):
    html_clean = html_content.replace('\\\\/', '/').replace('\\/', '/')
    assets = set()
    
    # 1. Scripts
    for m in re.finditer(r'<script[^>]+src=["\']([^"\']+)["\']', html_clean):
        assets.add(m.group(1))
        
    # 2. Stylesheets/Links
    for m in re.finditer(r'<link[^>]+href=["\']([^"\']+)["\']', html_clean):
        assets.add(m.group(1))
        
    # 3. Images
    for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', html_clean):
        assets.add(m.group(1))
        
    # 4. JSON/SSR static assets (e.g. /uploads/..., /thumbs/...)
    for m in re.finditer(r'(?:/uploads/|/thumbs/|/assets/)[a-zA-Z0-9_\-\./]+', html_clean):
        assets.add(m.group(0))
        
    return assets

def scan_js_css_for_vite_chunks(file_path):
    chunks = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Match standard Vite chunk pattern
        matches = re.findall(r'[a-zA-Z0-9_-]+-[a-fA-F0-9]{8}\.[a-zA-Z0-9]+', content)
        for m in matches:
            chunks.add(f"assets/{m}")
            
        # Also look for CSS url() imports
        css_assets = re.findall(r'url\([\'"]?([^\'")]+)[\'"]?\)', content)
        for css_asset in css_assets:
            if css_asset.startswith("data:"):
                continue
            clean_url = css_asset.split("?")[0].split("#")[0]
            if not clean_url.startswith("http"):
                chunks.add(f"assets/{clean_url.lstrip('/')}")
                
    except Exception as e:
        log(f"Error scanning file {file_path}: {e}")
    return chunks

def main():
    log(f"Crawl Starting. URL: {BASE_URL}, Target Dir: {TARGET_DIR}")
    downloaded_assets = set()
    all_extracted_assets = set()
    
    # Step 1: Download pages
    for page in PAGES:
        url = f"{BASE_URL}/{page}" if page else BASE_URL
        if page:
            local_path = os.path.join(TARGET_DIR, page, "index.html")
        else:
            local_path = os.path.join(TARGET_DIR, "index.html")
            
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        log(f"\n--- Fetching Page: {url} ---")
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                html = response.read().decode('utf-8', errors='ignore')
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(html)
            page_assets = extract_assets(html)
            all_extracted_assets.update(page_assets)
            log(f"Page downloaded and parsed. Found {len(page_assets)} potential assets.")
        except Exception as e:
            log(f"Failed to fetch page {url}: {e}")
            
    # Step 2: Download extracted assets recursively using a queue
    log(f"\nFound {len(all_extracted_assets)} initial assets. Starting recursive download...")
    
    queue = list(all_extracted_assets)
    visited = set(queue)
    
    while queue:
        asset = queue.pop(0)
        
        if asset.startswith("http") and not asset.startswith(BASE_URL):
            continue
        if asset.startswith("//"):
            continue
            
        clean_asset = asset
        if clean_asset.startswith(BASE_URL):
            clean_asset = clean_asset[len(BASE_URL):]
            
        if clean_asset.startswith("/"):
            clean_asset = clean_asset[1:]
            
        if not clean_asset or clean_asset.startswith("#") or clean_asset.startswith("?"):
            continue
            
        download_url = f"{BASE_URL}/{clean_asset}"
        local_filename = clean_asset.split("?")[0]
        local_path = os.path.join(TARGET_DIR, local_filename)
        
        if local_filename in PAGES or (local_filename + "/") in PAGES or local_filename in [p.replace('/', os.sep) for p in PAGES]:
            continue
            
        success = download_file(download_url, local_path)
        if success:
            downloaded_assets.add(local_path)
            
            if local_filename.endswith(".js") or local_filename.endswith(".css"):
                new_chunks = scan_js_css_for_vite_chunks(local_path)
                for chunk in new_chunks:
                    if chunk not in visited:
                        visited.add(chunk)
                        queue.append(chunk)
                        log(f"Discovered dynamic chunk: {chunk}")

    log("\n--- Download complete! ---")
    log(f"Downloaded pages: {len(PAGES)}")
    log(f"Downloaded unique assets: {len(downloaded_assets)}")

if __name__ == "__main__":
    main()
