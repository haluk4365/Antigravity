"""
rerender_red_scene1.py — Kırmızı sahne 1'i Gen-Z yaz kıyafetli olarak yeniden
render et + scene1.mp4'ün üzerine yaz + final remix tetikle.

Sebep: önceki sahne 1'de karakter kürk yakalı mont giymişti (referans imajdan).
Düzeltme: prompt'a açık Z-kuşağı yaz kıyafeti + kürk/mont YASAK eklendi.
"""

import asyncio
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.imgbb_service import ImgBBService
from services.kie_api import KieAIService
from logger import get_logger

from produce_summer_bikini_red import (
    COLLECTION,
    CHARACTER_REF,
    PRODUCT_TOP,
    PRODUCT_BOTTOM,
    RESCUE_DIR,
    CHARACTER_DESC,
    PRODUCT_DESC,
    FORMAT_SPEC,
)

log = get_logger("rerender_red_scene1")

# Yeni sahne 1 — kıyafet vurgusu eklenmiş
SCENE1 = {
    "name": "scene1_hook",
    "duration": 4,
    "setting": (
        "Setting: warm golden-hour seaside terrace, deep amber sunset "
        "light, calm ocean visible behind, vibrant summer evening mood."
    ),
    "outfit": (
        "She is wearing a MODERN trendy Gen-Z summer streetwear outfit — "
        "a fitted CROPPED short-sleeve white or soft pastel TANK / CROP "
        "TOP that exposes a small section of midriff, paired with a "
        "delicate thin gold chain necklace and tiny minimal hoop "
        "earrings. Contemporary, fashion-forward, the kind of outfit a "
        "trendy young Instagram/TikTok creator who follows crochet/"
        "handmade brands like Lara Arı would wear in summer. "
        "ABSOLUTELY NO winter coat, NO fur, NO faux fur, NO fall jacket, "
        "NO long sleeves, NO leather, NO heavy clothing, NO oversized "
        "baggy basic tee. The outfit must look stylish, modern, summer-"
        "appropriate, slightly cropped and form-fitting."
    ),
    "action": (
        "She holds up the red 3D-flower crochet bikini top in front of "
        "her chest with BOTH HANDS, the bikini top FULLY CENTERED and "
        "ENTIRELY VISIBLE in the frame — both triangle cups, both shoulder "
        "straps, and the back-tie strings ALL clearly shown, NOT cut off "
        "by the frame edge, NOT cropped, NOT partially hidden. Camera "
        "framed at chest-up so the full bikini top is the focal point. "
        "She smiles excitedly with a 'look at this!' expression. Handheld "
        "iPhone front-camera selfie angle, slight wobble, real skin, "
        "phone sensor grain, warm sunset light."
    ),
}


def build_prompt() -> str:
    return (
        f"Character: {CHARACTER_DESC} {SCENE1['outfit']} "
        f"{PRODUCT_DESC} "
        f"{SCENE1['setting']} "
        f"Action: {SCENE1['action']} "
        f"{FORMAT_SPEC}"
    )


def upload_refs(imgbb: ImgBBService) -> list[str]:
    urls = []
    for ref in [CHARACTER_REF, PRODUCT_TOP, PRODUCT_BOTTOM]:
        if not ref.exists():
            raise SystemExit(f"Referans yok: {ref}")
        with open(ref, "rb") as fh:
            data = fh.read()
        safe = "".join(c if c.isascii() else "_" for c in ref.stem).replace(" ", "_")
        urls.append(imgbb.upload_image_bytes(data, name=safe)["url"])
        log.info(f"Upload: {ref.name}")
    return urls


async def main() -> None:
    load_dotenv()
    imgbb = ImgBBService(os.environ["IMGBB_API_KEY"])
    kie = KieAIService(os.environ["KIE_API_KEY"])

    bal = kie.get_credit_balance()
    log.info(f"KIE bakiye: {bal.get('data')}")

    ref_urls = upload_refs(imgbb)

    log.info("Sahne 1 yeniden render — Gen-Z yaz kıyafetli")
    prompt = build_prompt()
    task_id = await asyncio.to_thread(
        kie.create_video,
        prompt=prompt,
        duration=SCENE1["duration"],
        aspect_ratio="9:16",
        generate_audio=False,
        reference_images=ref_urls,
    )
    result = await kie.async_poll_task(task_id)
    if result.get("status") != "success":
        raise RuntimeError(f"Render fail: {result.get('error', '?')}")
    urls = result.get("urls") or []
    video_url = urls[0] if not isinstance(urls[0], dict) else urls[0].get("url")

    target = RESCUE_DIR / "scene1.mp4"
    log.info(f"İndiriliyor → {target}")
    r = requests.get(video_url, timeout=180)
    r.raise_for_status()
    target.write_bytes(r.content)
    log.info(f"✅ Sahne 1 güncellendi ({target.stat().st_size:,} byte)")
    log.info("Şimdi remix_red_energetic.py çalıştır → FINAL_REKLAM_LARA_ARI_KIRMIZI_v2.mp4 güncellenir")


if __name__ == "__main__":
    asyncio.run(main())
