import sys, os, time, shutil
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path('.env'))

API_KEY = os.getenv("HEDRA_API_KEY", "")
if not API_KEY:
    print("HATA: HEDRA_API_KEY bulunamadi")
    sys.exit(1)

import requests
BASE_URL = "https://api.hedra.com/web-app/public"
HEADERS = {"X-API-Key": API_KEY, "Accept": "application/json"}

IMAGE_PATH = "hlk_robot_halfbody.png"
AUDIO_PATH = "C:/Users/msist/OneDrive/Desktop/HLK-Claude_EK/SAHNE-3_TR_AHU_V2.mp3"
OUTPUT_PATH = "C:/Users/msist/OneDrive/Desktop/HLK-Claude_EK/SAHNE-3_TR_AHU_V2.mp4"

if not os.path.exists(IMAGE_PATH):
    shutil.copy2("../hlk_robot_halfbody.png", IMAGE_PATH)

print(f"Gorsel: {os.path.getsize(IMAGE_PATH)/1024:.0f} KB")
print(f"Ses: {os.path.getsize(AUDIO_PATH)/1024:.0f} KB")
print(f"API: {BASE_URL}")
print()

def call(method, path, **kw):
    kw.setdefault("timeout", 60)
    return requests.request(method, f"{BASE_URL}{path}", headers=HEADERS, **kw)

# 1. Upload Image
print("1/5 Gorsel asseti olusturuluyor...")
resp = call("POST", "/assets", json={"name": "ahu_sahne3_char", "type": "image"})
if resp.status_code not in (200, 201):
    print(f"HATA: {resp.status_code} - {resp.text[:200]}")
    sys.exit(1)
img_id = resp.json()["id"]
print(f"  Image asset: {img_id}")

print("  Dosya yukleniyor...")
with open(IMAGE_PATH, "rb") as f:
    resp = call("POST", f"/assets/{img_id}/upload", files={"file": f})
if resp.status_code not in (200, 201, 204):
    print(f"HATA: {resp.status_code} - {resp.text[:200]}")
    sys.exit(1)
print("  Gorsel yuklendi.")

# 2. Upload Audio
print("2/5 Ses asseti olusturuluyor...")
resp = call("POST", "/assets", json={"name": "ahu_sahne3_aud", "type": "audio"})
if resp.status_code not in (200, 201):
    print(f"HATA: {resp.status_code} - {resp.text[:200]}")
    sys.exit(1)
aud_id = resp.json()["id"]
print(f"  Audio asset: {aud_id}")

print("  Dosya yukleniyor...")
with open(AUDIO_PATH, "rb") as f:
    resp = call("POST", f"/assets/{aud_id}/upload", files={"file": f})
if resp.status_code not in (200, 201, 204):
    print(f"HATA: {resp.status_code} - {resp.text[:200]}")
    sys.exit(1)
print("  Ses yuklendi.")

# 3. Generate video_with_audio
print("3/5 Lip-sync videosu olusturuluyor...")
payload = {
    "type": "video_with_audio",
    "image_id": img_id,
    "audio_id": aud_id,
    "ai_model_id": "hedra"
}
resp = call("POST", "/generations", json=payload, timeout=30)
if resp.status_code not in (200, 201):
    print(f"HATA: {resp.status_code} - {resp.text[:300]}")
    sys.exit(1)
gen_id = resp.json()["id"]
print(f"  Generation ID: {gen_id}")

# 4. Wait
print("4/5 Tamamlanmasi bekleniyor...")
start = time.time()
max_wait = 600
video_url = None

while time.time() - start < max_wait:
    time.sleep(10)
    resp = call("GET", f"/generations/{gen_id}/status")
    if resp.status_code == 200:
        d = resp.json()
        status = d.get("status") or d.get("state", "")
        elapsed = time.time() - start
        print(f"  [{elapsed:.0f}s] {status}")
        if status in ("completed", "succeeded", "done"):
            video_url = d.get("url") or d.get("video_url") or d.get("output_url")
            asset_id = d.get("asset_id") or d.get("output_asset_id")
            if not video_url and asset_id:
                r2 = call("GET", f"/assets/{asset_id}")
                if r2.status_code == 200:
                    video_url = r2.json().get("url")
            break
        elif status in ("failed", "error"):
            print(f"HATA: {d.get('error', 'bilinmiyor')}")
            sys.exit(1)

if not video_url:
    print("HATA: Zaman asimi")
    sys.exit(1)

print(f"  Video URL: {video_url}")

# 5. Download
print("5/5 Indiriliyor...")
resp = requests.get(video_url, timeout=300)
if resp.status_code == 200:
    with open(OUTPUT_PATH, "wb") as f:
        f.write(resp.content)
    mb = len(resp.content) / (1024*1024)
    print(f"\nBASARILI! {OUTPUT_PATH} ({mb:.1f} MB)")
else:
    print(f"HATA: {resp.status_code}")
