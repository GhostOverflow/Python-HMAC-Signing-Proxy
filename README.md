# HMAC Proxy Server

A lightweight HTTP proxy server that automatically signs outgoing requests with HMAC-SHA256 signatures. Originally designed for forwarding requests to webhook endpoints that require HMAC authentication (like GoPhish), but can be adapted for any HMAC-authenticated API.

## Features

- ✅ Supports GET, POST, and PUT requests
- ✅ Automatic HMAC-SHA256 signature generation
- ✅ Request/response logging
- ✅ Preserves original request headers and body
- ✅ Simple configuration via constants

## Use Case

This proxy is useful when you need to interact with HMAC-authenticated APIs using tools that don't natively support HMAC signing (e.g., SQLMap, curl, browser extensions).

**Example scenario:**

SQLMap → localhost:8090 → HMAC Proxy (signs request) → Target API (validates signature)

text


## Requirements

```
pip install requests
```
## Configuration

Edit the following constants in the script:

```
TARGET_HOST = "https://your-target-endpoint.com"  # Target API endpoint
SECRET_KEY = b"your-secret-key-here"              # HMAC secret key
PROXY_PORT = 8090                                  # Local proxy port
```
## Usage

1. Start the proxy
```
python3 hmac_proxy.py
```
Output:
```
[*] HMAC Proxy for GoPhish Webhook
[*] Listening on: http://127.0.0.1:8090
[*] Forwarding to: https://your-target-endpoint.com
[*] Secret key: your-secret-key-here
```
2. Send requests through the proxy

Using curl:
```
curl -X POST http://127.0.0.1:8090/api/endpoint \
  -H "Content-Type: application/json" \
  -d '{"data": "test"}'
```
Using SQLMap:
```
sqlmap -u "http://127.0.0.1:8090/api/endpoint?id=1" --batch
```
Using any HTTP client:
```
Point your tool to: http://127.0.0.1:8090/your/path
```
The proxy will:
    Intercept your request
    Calculate HMAC signature of the request body
    Add hmac-signature: sha256=<signature> header
    Forward to TARGET_HOST/your/path
    Return the response to your client

## How It Works

HMAC Signature Generation
```
signature = hmac.new(SECRET_KEY, request_body, hashlib.sha256).hexdigest()
```
The signature is added to the request header:
```
hmac-signature: sha256=<calculated_signature>
```
Request Flow
```
Client Request
    ↓
Proxy receives request
    ↓
Read request body
    ↓
Calculate HMAC-SHA256(body, secret_key)
    ↓
Add hmac-signature header
    ↓
Forward to TARGET_HOST
    ↓
Receive response
    ↓
Forward response to client
```
Example Output
```
[+] POST https://target.com/api/webhook
[+] Body: {"email":"test@example.com","action":"clicked"}
[+] Signature: sha256=a3f5e8c9d2b4f1a7e6c3d8b5f2a9e1c4d7b3f6a2e5c8d1b4f7a3e6c9d2b5f8a1
[+] Response: 200
[+] Response body: {"success":true,"message":"Webhook processed"}
```

Pull requests welcome! For major changes, please open an issue first.
Disclaimer

This tool is for authorized security testing and legitimate API integration only. Users are responsible for compliance with applicable laws and terms of service.
