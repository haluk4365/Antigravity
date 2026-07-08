import sys, os, time
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path('.env'))

API_KEY = os.getenv("HEDRA_API_KEY", "")
if not API_KEY:
    print("HATA: API anahtari yok"); sys.exit(1)

import requests
BASE = "https://api.hedra.com/web-app/public"
H = {"X-API-Key": API_KEY, "Accept": "application/json"}

OUTPUT_PATH = "C:/Users/msist/OneDrive/Desktop/HLK-Claude_EK/SAHNE-3_TR_AHU_V2.mp4"
IMG_ID = "fbc260de-8eee-4ffc-a5a8-d333239527f1"
AUD_ID = "2714a4a9-a3c6-47a5-b3c3-d33a50d627df"
AVATAR_MODEL = "26f0fc66-152b-40ab-abed-76c43df99bc8"

def c(method, path, **kw):
    kw.setdefault("timeout", 60)
    return requests.request(method, f"{BASE}{path}", headers=H, **kw)

# Generate
print("1/4 Karakter videosu olusturuluyor... (Hedra Avatar)")
payload = {
    "type": "video",
    "ai_model_id": AVATAR_MODEL,
    "start_keyframe_id": IMG_ID,
    "audio_id": AUD_ID,
    "generated_video_inputs": {
        "text_prompt": "A professional Turkish female AI assistant, warm confident expression, half-body shot, cinematic lighting, dark background, natural speaking",
        "aspect_ratio": "9:16"
    }
}
resp = c("POST", "/generations", json=payload, timeout=30)
if resp.status_code not in (200, 201):
    print(f"HATA: {resp.status_code}")
    print(resp.text[:400])
    sys.exit(1)
gen_id = resp.json()["id"]
print(f"  Gen ID: {gen_id}")

# Wait
print("2/4 Bekleniyor...")
start = time.time()
max_wait = 600
video_url = None
while time.time() - start < max_wait:
    time.sleep(10)
    resp = c("GET", f"/generations/{gen_id}/status")
    if resp.status_code == 200:
        d = resp.json()
        status = d.get("status") or d.get("state", "")
        el = time.time() - start
        print(f"  [{el:.0f}s] {status}")
        if status in ("completed", "succeeded", "done"):
            video_url = d.get("url") or d.get("video_url") or d.get("output_url")
            aid = d.get("asset_id") or d.get("output_asset_id")
            if not video_url and aid:
                r2 = c("GET", f"/assets/{aid}")
                video_url = r2.json().get("url") if r2.status_code == 200 else None
            break
        elif status in ("failed", "error"):
            print(f"HATA: {d.get('error', d)}"); sys.exit(1)

if not video_url:
    print("Zaman asimi"); sys.exit(1)

print(f"  URL: {video_url[:80]}...")

# Download
print("3/4 Indiriliyor...")
resp = requests.get(video_url, timeout=300)
if resp.status_code == 200:
    with open(OUTPUT_PATH, "wb") as f:
        f.write(resp.content)
    mb = len(resp.content) / (1024*1024)
    print(f"BASARILI! {OUTPUT_PATH} ({mb:.1f} MB)")
else:
    print(f"Indirme hatasi: {resp.status_code}")

print("4/4 Tamam.")
