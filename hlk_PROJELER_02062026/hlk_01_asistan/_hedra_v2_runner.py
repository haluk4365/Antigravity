import sys, os, time, shutil, uuid
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path('.env'))

API_KEY = os.getenv("HEDRA_API_KEY", "")
print(f"HEDRA_API_KEY var mi: {bool(API_KEY)}")
if not API_KEY:
    print("HATA: API anahtari bulunamadi")
    sys.exit(1)

import requests

BASE_URL = "https://api.hedra.com"
IMAGE_PATH = "hlk_robot_halfbody.png"
AUDIO_PATH = "C:/Users/msist/OneDrive/Desktop/HLK-Claude_EK/SAHNE-3_TR_AHU_V2.mp3"
OUTPUT_PATH = "C:/Users/msist/OneDrive/Desktop/HLK-Claude_EK/SAHNE-3_TR_AHU_V2.mp4"

if not os.path.exists(IMAGE_PATH):
    shutil.copy2("../hlk_robot_halfbody.png", IMAGE_PATH)

print(f"Gorsel: {os.path.getsize(IMAGE_PATH)/1024:.0f} KB")
print(f"Ses: {os.path.getsize(AUDIO_PATH)/1024:.0f} KB")

HEADERS = {"X-API-Key": API_KEY, "Accept": "application/json"}

def api_call(method, path, **kwargs):
    url = f"{BASE_URL}{path}"
    kwargs.setdefault("timeout", 60)
    resp = requests.request(method, url, headers=HEADERS, **kwargs)
    return resp

# 1. Upload Image
print("\n1/5 Gorsel asseti olusturuluyor...")
resp = api_call("POST", "/assets", json={"name": "ahu_sahne3_character", "type": "image"})
if resp.status_code not in (200, 201):
    print(f"HATA (asset): {resp.status_code} - {resp.text[:200]}")
    sys.exit(1)
image_asset_id = resp.json().get("id")
print(f"Image asset ID: {image_asset_id}")

print("Gorsel dosyasi yukleniyor...")
with open(IMAGE_PATH, "rb") as f:
    resp = api_call("POST", f"/assets/{image_asset_id}/upload", files={"file": f})
if resp.status_code not in (200, 201):
    print(f"HATA (upload): {resp.status_code} - {resp.text[:200]}")
    sys.exit(1)
print("Gorsel yuklendi.")

# 2. Upload Audio
print("\n2/5 Ses asseti olusturuluyor...")
resp = api_call("POST", "/assets", json={"name": "ahu_sahne3_audio", "type": "audio"})
if resp.status_code not in (200, 201):
    print(f"HATA (asset): {resp.status_code} - {resp.text[:200]}")
    sys.exit(1)
audio_asset_id = resp.json().get("id")
print(f"Audio asset ID: {audio_asset_id}")

print("Ses dosyasi yukleniyor...")
with open(AUDIO_PATH, "rb") as f:
    resp = api_call("POST", f"/assets/{audio_asset_id}/upload", files={"file": f})
if resp.status_code not in (200, 201):
    print(f"HATA (upload): {resp.status_code} - {resp.text[:200]}")
    sys.exit(1)
print("Ses yuklendi.")

# 3. Generate Video with Audio (lip-sync)
print("\n3/5 Video olusturma istegi gonderiliyor...")
# Try different generation types for lip-sync video
payload = {
    "type": "video_with_audio",
    "image_id": image_asset_id,
    "audio_id": audio_asset_id,
    "ai_model_id": "omnia",
    "aspect_ratio": "9:16"
}

resp = api_call("POST", "/generations", json=payload, timeout=30)
if resp.status_code not in (200, 201):
    print(f"HATA (generation): {resp.status_code}")
    print(f"Yanit: {resp.text[:300]}")
    print("\nAlternatif payload deneniyor...")
    # Try alternative format
    payload2 = {
        "type": "video_with_audio",
        "image_asset_id": image_asset_id,
        "audio_asset_id": audio_asset_id,
        "ai_model_id": "omnia",
        "aspect_ratio": "9:16"
    }
    resp = api_call("POST", "/generations", json=payload2, timeout=30)
    if resp.status_code not in (200, 201):
        print(f"HATA (generation2): {resp.status_code} - {resp.text[:300]}")
        sys.exit(1)

gen_data = resp.json()
gen_id = gen_data.get("id") or gen_data.get("generation_id")
print(f"Generation ID: {gen_id}")

# 4. Wait for completion
print("\n4/5 Video tamamlanmasi bekleniyor...")
start = time.time()
max_wait = 600
video_url = None

while time.time() - start < max_wait:
    time.sleep(10)
    try:
        resp = api_call("GET", f"/generations/{gen_id}")
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status") or data.get("state", "")
            elapsed = time.time() - start
            print(f"  [{elapsed:.0f}s] Durum: {status}")
            if status in ("completed", "succeeded", "done"):
                video_url = data.get("url") or data.get("video_url") or data.get("output_url")
                # Check if result is in assets
                if not video_url:
                    asset_id = data.get("asset_id") or data.get("output_asset_id")
                    if asset_id:
                        print(f"  Output asset ID: {asset_id}, indiriliyor...")
                        resp2 = api_call("GET", f"/assets/{asset_id}")
                        if resp2.status_code == 200:
                            video_url = resp2.json().get("url") or resp2.json().get("download_url")
                break
            elif status in ("failed", "error"):
                print(f"HATA: {data.get('error', 'bilinmiyor')}")
                sys.exit(1)
    except Exception as e:
        print(f"Kontrol hatasi: {e}")

if not video_url:
    print("HATA: Zaman asimi veya video URL bulunamadi")
    sys.exit(1)

print(f"Video URL: {video_url}")

# 5. Download
print("5/5 Video indiriliyor...")
resp = requests.get(video_url, timeout=300)
if resp.status_code == 200:
    with open(OUTPUT_PATH, "wb") as f:
        f.write(resp.content)
    size_mb = len(resp.content) / (1024 * 1024)
    print(f"\nBASARILI! Video kaydedildi: {OUTPUT_PATH} ({size_mb:.1f} MB)")
else:
    print(f"Indirme hatasi: {resp.status_code}")
    sys.exit(1)

# Cleanup
if os.path.exists("_hedra_v2_runner.py"):
    os.remove("_hedra_v2_runner.py")
