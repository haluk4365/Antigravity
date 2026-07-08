import sys, os, time, shutil
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path('.env'))

API_KEY = os.getenv("HEDRA_API_KEY", "")
print(f"HEDRA_API_KEY var mi: {bool(API_KEY)}")

if not API_KEY:
    print("HATA: HEDRA_API_KEY bulunamadi")
    exit(1)

import requests

BASE_URL = "https://api.hedra.com"
IMAGE_PATH = "hlk_robot_halfbody.png"
AUDIO_PATH = "C:/Users/msist/OneDrive/Desktop/HLK-Claude_EK/SAHNE-3_TR_AHU_V2.mp3"
OUTPUT_PATH = "C:/Users/msist/OneDrive/Desktop/HLK-Claude_EK/SAHNE-3_TR_AHU_V2.mp4"

# Copy image if needed
if not os.path.exists(IMAGE_PATH):
    shutil.copy2("../hlk_robot_halfbody.png", IMAGE_PATH)
    print(f"Gorsel kopyalandi: {IMAGE_PATH}")

print(f"Gorsel: {os.path.getsize(IMAGE_PATH)/1024:.0f} KB")
print(f"Ses: {os.path.getsize(AUDIO_PATH)/1024:.0f} KB")

headers = {"X-API-Key": API_KEY, "Accept": "application/json"}

# 1. Upload image
print("\n1/4 Gorsel yukleniyor...")
with open(IMAGE_PATH, "rb") as f:
    resp = requests.post(f"{BASE_URL}/web-app/v1/images", headers=headers, files={"file": f}, timeout=60)
if resp.status_code != 200:
    print(f"HATA (image): {resp.status_code} - {resp.text[:200]}")
    exit(1)
image_url = resp.json().get("url") or resp.json().get("image_url")
print(f"Gorsel URL: {image_url}")

# 2. Upload audio
print("2/4 Ses yukleniyor...")
with open(AUDIO_PATH, "rb") as f:
    resp = requests.post(f"{BASE_URL}/web-app/v1/audios", headers=headers, files={"file": f}, timeout=60)
if resp.status_code != 200:
    print(f"HATA (audio): {resp.status_code} - {resp.text[:200]}")
    exit(1)
audio_url = resp.json().get("url") or resp.json().get("audio_url")
print(f"Ses URL: {audio_url}")

# 3. Generate video
print("3/4 Video uretiliyor... (bekleme suresi: ~5 dk)")
payload = {
    "image_url": image_url,
    "audio_url": audio_url,
    "model_id": "omnia",
    "aspect_ratio": "9:16",
    "resolution": "720p",
}
headers["Content-Type"] = "application/json"
resp = requests.post(f"{BASE_URL}/web-app/v1/videos/generate", headers=headers, json=payload, timeout=120)
if resp.status_code != 200:
    print(f"HATA (generate): {resp.status_code} - {resp.text[:200]}")
    exit(1)
job_id = resp.json().get("job_id") or resp.json().get("video_id")
print(f"Is baslatildi - Job ID: {job_id}")

# 4. Wait for completion
print("4/4 Tamamlanmasi bekleniyor...")
start = time.time()
max_wait = 600  # 10 dakika maksimum
video_url = None

while time.time() - start < max_wait:
    time.sleep(10)
    try:
        resp = requests.get(f"{BASE_URL}/web-app/v1/jobs/{job_id}", headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status") or data.get("state", "")
            elapsed = time.time() - start
            print(f"  [{elapsed:.0f}s] Durum: {status}")
            if status == "completed":
                video_url = data.get("video_url") or data.get("output_url")
                break
            elif status == "failed":
                print(f"HATA: Is basarisiz - {data.get('error', 'bilinmiyor')}")
                exit(1)
        elif resp.status_code == 404:
            print("HATA: Is bulunamadi")
            exit(1)
    except Exception as e:
        print(f"Kontrol hatasi: {e}")

if not video_url:
    print("HATA: Zaman asimi")
    exit(1)

print(f"Video URL: {video_url}")

# 5. Download
print("Video indiriliyor...")
resp = requests.get(video_url, timeout=120)
if resp.status_code == 200:
    with open(OUTPUT_PATH, "wb") as f:
        f.write(resp.content)
    size_mb = len(resp.content) / (1024 * 1024)
    print(f"BASARILI! Video kaydedildi: {OUTPUT_PATH} ({size_mb:.1f} MB)")
else:
    print(f"Indirme hatasi: {resp.status_code}")
    exit(1)
