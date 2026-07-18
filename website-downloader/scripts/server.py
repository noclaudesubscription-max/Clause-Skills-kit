import http.server
import socketserver
import os
import urllib.request
import urllib.error
import hashlib
import sys

# Parameterized configuration with defaults
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
DIRECTORY = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
TARGET_HOST = sys.argv[3] if len(sys.argv) > 3 else "https://wondermake.xyz"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        
    def end_headers(self):
        # Enable CORS and disable caching for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
        
    def do_PROXY(self, method):
        target_url = f"{TARGET_HOST}{self.path}"
        print(f"Proxying request: {method} {self.path}", flush=True)
        
        # Read request body for POST/PUT requests
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        # Support offline caching for POST request payloads (like database queries)
        is_post = (method == 'POST')
        body_hash = ""
        if is_post and body:
            body_hash = hashlib.md5(body).hexdigest()
            cache_file = os.path.join(DIRECTORY, "api", "post_cache", f"{body_hash}.json")
            if os.path.exists(cache_file):
                print(f"Serving POST /api from local cache: {body_hash}", flush=True)
                with open(cache_file, 'rb') as f:
                    cached_data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(cached_data)))
                self.end_headers()
                self.wfile.write(cached_data)
                return

        # Clean headers (exclude Host so urllib can set it correctly)
        headers = {k: v for k, v in self.headers.items() if k.lower() != 'host'}
        headers['Host'] = urllib.parse.urlparse(TARGET_HOST).netloc
        
        try:
            req = urllib.request.Request(
                target_url,
                data=body,
                headers=headers,
                method=method
            )
            with urllib.request.urlopen(req, timeout=15) as res:
                status = res.status
                res_data = res.read()
                
                print(f"Proxy Response: {status}, Size: {len(res_data)} bytes", flush=True)
                
                # Cache successful POST response body
                if status == 200 and is_post and body_hash:
                    cache_file = os.path.join(DIRECTORY, "api", "post_cache", f"{body_hash}.json")
                    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                    with open(cache_file, 'wb') as f:
                        f.write(res_data)
                    print(f"Successfully cached POST response: {body_hash}", flush=True)
                
                # Send response to client
                self.send_response(status)
                for k, v in res.getheaders():
                    if k.lower() not in ('transfer-encoding', 'connection', 'content-length'):
                        self.send_header(k, v)
                self.send_header('Content-Length', str(len(res_data)))
                self.end_headers()
                self.wfile.write(res_data)
                
                # Cache static assets locally on Drive D if successful
                if status == 200 and method == 'GET':
                    path_lower = self.path.lower()
                    if path_lower.startswith('/thumbs/') or path_lower.startswith('/uploads/') or path_lower.startswith('/assets/'):
                        local_path = self.translate_path(self.path)
                        local_path_clean = local_path.split('?')[0].split('#')[0]
                        os.makedirs(os.path.dirname(local_path_clean), exist_ok=True)
                        with open(local_path_clean, 'wb') as f:
                            f.write(res_data)
                        print(f"Successfully cached asset locally: {self.path}", flush=True)
        except urllib.error.HTTPError as e:
            try:
                err_data = e.read()
                self.send_response(e.code)
                for k, v in e.headers.items():
                    if k.lower() not in ('transfer-encoding', 'connection', 'content-length'):
                        self.send_header(k, v)
                self.send_header('Content-Length', str(len(err_data)))
                self.end_headers()
                self.wfile.write(err_data)
            except:
                self.send_error(e.code)
        except Exception as e:
            print(f"Proxy connection failed: {e}", flush=True)
            self.send_error(502, f"Proxy error: {e}")

    def handle_range(self, file_path, file_size, range_header):
        # Range header format: bytes=start-end
        try:
            range_val = range_header.strip().split('=')[1]
            start_str, end_str = range_val.split('-')
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
        except Exception as e:
            self.send_error(400, f"Bad Range Header: {e}")
            return
            
        if start >= file_size or end >= file_size or start > end:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{file_size}')
            self.end_headers()
            return
            
        length = end - start + 1
        self.send_response(206)
        
        # Guess MIME type
        ext = os.path.splitext(file_path)[1].lower()
        mime_type = self.extensions_map.get(ext, 'application/octet-stream')
        
        self.send_header('Content-Type', mime_type)
        self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
        self.send_header('Content-Length', str(length))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        
        try:
            with open(file_path, 'rb') as f:
                f.seek(start)
                self.wfile.write(f.read(length))
        except Exception as e:
            print(f"Error serving range: {e}", flush=True)

    def serve_local_file(self, file_path):
        range_header = self.headers.get('Range')
        if range_header and os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            self.handle_range(file_path, file_size, range_header)
        else:
            rel_path = os.path.relpath(file_path, DIRECTORY).replace('\\', '/')
            self.path = '/' + rel_path
            super().do_GET()

    def do_GET(self):
        # 1. Video streaming API redirect to local uploads
        if self.path.startswith('/api/media-stream/'):
            parts = self.path.strip('/').split('/')
            if len(parts) >= 3:
                filename = parts[2]
                local_video_path = os.path.join(DIRECTORY, "uploads", filename)
                if os.path.exists(local_video_path):
                    self.serve_local_file(local_video_path)
                    return

        # 2. API routes must always go to the real live backend
        if self.path.startswith('/api') or self.path.startswith('/api/'):
            self.do_PROXY('GET')
            return
            
        # 3. Check if file exists locally
        local_path = self.translate_path(self.path)
        local_path_clean = local_path.split('?')[0].split('#')[0]
        
        exists = os.path.exists(local_path_clean)
        if exists and os.path.isdir(local_path_clean):
            exists = os.path.exists(os.path.join(local_path_clean, 'index.html'))
            local_path_clean = os.path.join(local_path_clean, 'index.html')
            
        if exists:
            self.serve_local_file(local_path_clean)
        else:
            self.do_PROXY('GET')
            
    def do_POST(self):
        self.do_PROXY('POST')
        
    def do_OPTIONS(self):
        self.do_PROXY('OPTIONS')

# Strict MIME mapping override to prevent Windows Registry pollution
CustomHandler.extensions_map = {
    '': 'application/octet-stream',
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.mjs': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.mp4': 'video/mp4',
    '.riv': 'application/octet-stream',
    '.webmanifest': 'application/manifest+json'
}

def main():
    socketserver.TCPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving HTTP on port {PORT} with live proxy fallback (multi-threaded, self-caching)...", flush=True)
        httpd.serve_forever()

if __name__ == "__main__":
    main()
