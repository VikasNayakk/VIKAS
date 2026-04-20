import requests
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "photos")
os.makedirs(ASSETS_DIR, exist_ok=True)

PEXELS_KEY = "6tIN39WbMyLT8Tkvey64ri0ii1N2BUdPBC8xU7oGgcOZ1BH4jIlMzLoC"
UNSPLASH_KEY = "kUNy9u0JIKZ7fb9Oebq8yfXgybTyuikDcoY5Ig9QuFk"

session = requests.Session()
session.verify = False

def download_image(url, filename):
    filepath = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(filepath):
        print(f"  Already exists: {filename}")
        return True
    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(r.content)
        print(f"  Downloaded: {filename} ({len(r.content)//1024}KB)")
        return True
    except Exception as e:
        print(f"  FAILED: {filename} - {e}")
        return False

# --- PEXELS ---
print("=== Downloading from Pexels ===")
pexels_queries = [
    ("futuristic technology", "pexels-futuristic-1.jpg"),
    ("neon city night", "pexels-neon-city-2.jpg"),
    ("cyber technology", "pexels-cyber-3.jpg"),
    ("space galaxy", "pexels-space-4.jpg"),
    ("programming code", "pexels-code-5.jpg"),
    ("robot artificial intelligence", "pexels-robot-6.jpg"),
    ("hacker cybersecurity", "pexels-hacker-7.jpg"),
    ("server data center", "pexels-server-8.jpg"),
    ("hologram technology", "pexels-hologram-9.jpg"),
    ("digital abstract", "pexels-abstract-10.jpg"),
]

for query, filename in pexels_queries:
    print(f"  Searching Pexels: '{query}'")
    try:
        r = session.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            timeout=15
        )
        r.raise_for_status()
        data = r.json()
        if data.get("photos"):
            img_url = data["photos"][0]["src"]["large"]
            download_image(img_url, filename)
        else:
            print(f"  No results for '{query}'")
    except Exception as e:
        print(f"  Pexels error: {e}")

# --- UNSPLASH ---
print("\n=== Downloading from Unsplash ===")
unsplash_queries = [
    ("futuristic spaceship", "unsplash-spaceship-1.jpg"),
    ("neon lights abstract", "unsplash-neon-2.jpg"),
    ("alien planet landscape", "unsplash-alien-3.jpg"),
    ("cyberpunk city", "unsplash-cyberpunk-4.jpg"),
    ("technology workspace", "unsplash-workspace-5.jpg"),
    ("circuit board macro", "unsplash-circuit-6.jpg"),
    ("aurora borealis night", "unsplash-aurora-7.jpg"),
    ("dark futuristic corridor", "unsplash-corridor-8.jpg"),
    ("vr virtual reality headset", "unsplash-vr-9.jpg"),
    ("matrix digital rain", "unsplash-matrix-10.jpg"),
]

for query, filename in unsplash_queries:
    print(f"  Searching Unsplash: '{query}'")
    try:
        r = session.get(
            "https://api.unsplash.com/search/photos",
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            timeout=15
        )
        r.raise_for_status()
        data = r.json()
        if data.get("results"):
            img_url = data["results"][0]["urls"]["regular"]
            download_image(img_url, filename)
        else:
            print(f"  No results for '{query}'")
    except Exception as e:
        print(f"  Unsplash error: {e}")

print(f"\n=== Done! Photos saved in: {ASSETS_DIR} ===")
print(f"Total files: {len(os.listdir(ASSETS_DIR))}")
