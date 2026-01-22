#!/usr/bin/env python3
import http.server
import socketserver
import requests
import hmac
import hashlib
import json

# Configuration
TARGET_HOST = "FORWARDING_URL_ENDPOINT_HERE"
SECRET_KEY = b"SECRET_HERE"
PROXY_PORT = 8090

class HMACProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request("GET")
    
    def do_POST(self):
        self.proxy_request("POST")
    
    def do_PUT(self):
        self.proxy_request("PUT")
    
    def proxy_request(self, method):
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""
        
        # Calculate HMAC signature of the body
        signature = hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()
        
        # Build target URL
        target_url = f"{TARGET_HOST}{self.path}"
        
        # Copy headers
        headers = {
            'Content-Type': 'application/json',
            'hmac-signature': f"sha256={signature}",
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        print(f"\n[+] {method} {target_url}")
        print(f"[+] Body: {body.decode('utf-8', errors='ignore')}")
        print(f"[+] Signature: sha256={signature}")
        
        try:
            # Forward request
            response = requests.request(
                method=method,
                url=target_url,
                headers=headers,
                data=body,
                allow_redirects=False,
                verify=False
            )
            
            # Send response back to sqlmap
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                if key.lower() not in ['content-encoding', 'transfer-encoding', 'connection']:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response.content)
            
            print(f"[+] Response: {response.status_code}")
            print(f"[+] Response body: {response.text[:200]}")
        
        except Exception as e:
            print(f"[-] Error: {e}")
            self.send_error(500, f"Proxy error: {str(e)}")
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

if __name__ == "__main__":
    print(f"[*] HMAC Proxy for endpoints and webhooks")
    print(f"[*] Listening on: http://127.0.0.1:{PROXY_PORT}")
    print(f"[*] Forwarding to: {TARGET_HOST}")
    print(f"[*] Secret key: {SECRET_KEY.decode()}\n")
    
    with socketserver.TCPServer(("127.0.0.1", PROXY_PORT), HMACProxyHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n[*] Shutting down proxy")
