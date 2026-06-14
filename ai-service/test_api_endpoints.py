import urllib.request
import urllib.error
import json

base = "http://localhost:8000"

endpoints = [
    ("GET /", "/"),
    ("GET /health", "/health"),
    ("GET /api/health", "/api/health"),
    ("GET /api/v1/health", "/api/v1/health"),
    ("GET /api/policies?size=5", "/api/policies?size=5"),
    ("GET /api/v1/policies?size=5", "/api/v1/policies?size=5"),
    ("GET /api/v1/metrics/web-vitals", "/api/v1/metrics/web-vitals"),
    ("GET /api/metrics/web-vitals", "/api/metrics/web-vitals"),
    ("POST /api/user/register", "/api/user/register"),
    ("POST /api/v1/auth/register", "/api/v1/auth/register"),
    ("POST /api/user/login", "/api/user/login"),
    ("POST /api/v1/auth/login", "/api/v1/auth/login"),
    ("GET /api/schools", "/api/schools"),
    ("GET /api/v1/schools", "/api/v1/schools"),
]

for method, path in endpoints:
    url = base + path
    try:
        if method.startswith("POST"):
            data = json.dumps({"username": "testuser", "password": "test123456", "email": "test@test.com"}).encode()
            req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
        else:
            req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode()[:200]
            print(f"{method:<35} -> {resp.status} {body}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print(f"{method:<35} -> HTTP {e.code} {body}")
    except Exception as e:
        print(f"{method:<35} -> ERROR: {e}")

print("\n\n=== Testing Vite proxy (port 3000) ===")
base = "http://localhost:3000"
for method, path in endpoints:
    if path in ["/", "/health"]:
        continue
    url = base + path
    try:
        if method.startswith("POST"):
            data = json.dumps({"username": "testuser", "password": "test123456", "email": "test@test.com"}).encode()
            req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
        else:
            req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode()[:200]
            print(f"{method:<35} -> {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print(f"{method:<35} -> HTTP {e.code}")
    except Exception as e:
        print(f"{method:<35} -> ERROR: {e}")
