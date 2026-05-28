import os, sys, json, asyncio, requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

from services.kie_api import KieAIService
from logger import get_logger
log = get_logger("render_scene2")

BACK_IMAGE_URL = "https://i.ibb.co/Rpvb09xX/hlk-LARA025-02-JPG.jpg"
OUTPUT_PATH = r"c:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\scene2_sirt.mp4"

async def main():
    kie = KieAIService(os.environ.get("KIE_API_KEY"))

    # Bakiye kontrol
    bal = kie.get_credit_balance()
    bal_val = bal.get("data", 0) if isinstance(bal, dict) else 0
    print(f"Kie AI Bakiye: {bal_val} kredi")

    # Senaryo'dan Scene 2 prompt'unu al
    with open("scenario_output.json", "r", encoding="utf-8") as f:
        scenario = json.load(f)

    scene2 = scenario["scenes"][1]  # Build sahnesi
    prompt = scene2["video_prompt"]
    duration = scene2["duration_seconds"]  # 6s

    print(f"\nSahne: {scene2['scene_name']} ({duration}s)")
    print(f"Prompt: {prompt[:100]}...")
    print(f"\nSirt gorseli referans: {BACK_IMAGE_URL}")
    print("\nKie AI'ya sahne gonderiliyor...")

    # Kie AI'ya gonder - sirt gorseli referans olarak
    print("\nKie AI video gorev olusturuluyor...")
    task_id = await kie.create_video(
        prompt=prompt,
        duration=duration,
        aspect_ratio="9:16",
        reference_images=[BACK_IMAGE_URL]
    )

    print(f"Gorev ID: {task_id} — tamamlanmasi bekleniyor (3-5 dk)...")

    # Polling
    import asyncio as _asyncio
    from services.kie_api import KieAIService as _K
    video_url = None
    for attempt in range(90):
        await _asyncio.sleep(5)
        status = await kie.get_task_result(task_id)
        state = status.get("state") or status.get("status", "")
        print(f"  Deneme {attempt+1}: {state}")
        if state in ("succeed", "completed", "success"):
            outputs = status.get("outputs") or status.get("videos") or []
            if outputs:
                video_url = outputs[0].get("url") or outputs[0]
            break
        elif state in ("failed", "error"):
            print(f"❌ Uretim basarisiz: {status}")
            return

    if video_url:
        print(f"\n✅ Sahne uretildi: {video_url}")
        print("Video indiriliyor...")
        resp = requests.get(video_url)
        resp.raise_for_status()
        with open(OUTPUT_PATH, "wb") as f:
            f.write(resp.content)
        print(f"✅ Kaydedildi: {OUTPUT_PATH}")
    else:
        print("❌ Video URL alinamadi.")

if __name__ == "__main__":
    asyncio.run(main())
