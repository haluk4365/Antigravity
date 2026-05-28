"""
rerender_white_134.py — Beyaz reklamı sahne 1, 3, 4'ü yeniden render et.

Düzeltmeler:
  Sahne 1: ürün havada uçmuyor, BOTH HANDS ile gerçekten tutuyor, ÜST PARÇA gösteriyor (alt değil)
  Sahne 3: sokak kıyafeti yok, SADECE bikini seti giyiyor
  Sahne 4: bikini doğru giyilmiş, ARKA İPLER ARKADA (önde değil)

Sahne 2 mevcut dosyadan kullanılır (sorun yoktu).
Render bitince mevcut _rescue_beyaz scene{1,3,4}.mp4 üzerine yazılır + remix.

Çıktı: FINAL_REKLAM_LARA_ARI_BEYAZ.mp4 (üzerine yazar)
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.imgbb_service import ImgBBService
from services.kie_api import KieAIService
from services.elevenlabs_service import ElevenLabsService
from logger import get_logger

from produce_summer_bikini_white import (
    CHARACTER_REF,
    PRODUCT_TOP,
    PRODUCT_BOTTOM,
    RESCUE_DIR,
    AMBIENT_PATH,
    OUTPUT_FILE,
    PRODUCT_DESC,
    FORMAT_SPEC,
    SCENES as ORIG_SCENES,
    upload_reference_images,
    download,
    generate_voiceovers,
    concat,
)

log = get_logger("rerender_white_134")

# Karakter temel (outfit yok — sahneye göre değişecek)
CHARACTER_BASE = (
    "The EXACT same young Turkish Gen-Z woman from the reference image — "
    "approximately 20 years old, SAME FACE as reference, BUT with hair "
    "worn DOWN in loose soft balayage beach waves cascading over her "
    "shoulders (NOT in a top bun). Dewy fresh natural makeup, sun-kissed "
    "skin, warm playful smile. DO NOT generate a different person — only "
    "the hairstyle differs."
)

OUTFIT_STREET = (
    "She wears a MODERN trendy Gen-Z summer outfit — a fitted CROPPED "
    "short-sleeve white tank/crop top exposing a small midriff section. "
    "ABSOLUTELY NO necklace, NO chain, NO jewelry around the neck or "
    "chest, NO earrings visible. Contemporary fashion-forward summer "
    "style. NO winter coat, NO fur, NO long sleeves."
)

OUTFIT_BIKINI_ONLY = (
    "She is wearing ONLY the matching ivory seashell crochet bikini set "
    "(top AND bottom from the product description) — NO cropped top, NO "
    "tank top, NO t-shirt, NO street clothes layered over the bikini, NO "
    "shirt covering her body. ABSOLUTELY NO necklace, NO chain, NO "
    "jewelry around the neck or chest. She has changed into the "
    "swimwear; only the bikini (and pareo if mentioned in the scene) is "
    "on her body."
)

# Sahne tanımları — sadece 1, 3, 4 (sahne 2 mevcut)
NEW_SCENES = [
    {
        "idx": 0,  # scene1
        "name": "scene1_hook",
        "duration": 4,
        "character": f"{CHARACTER_BASE} {OUTFIT_STREET}",
        "setting": (
            "Setting: LUXURY WHITE YACHT DECK at midday, polished teak "
            "wood floor, glossy white yacht railings visible behind, deep "
            "open ocean turquoise water all around, soft warm daylight, "
            "vibrant luxe summer mood."
        ),
        "action": (
            "There is NO pareo, NO scarf, NO shawl anywhere in this "
            "shot — only the bikini top in her hands. "
            "She is FIRMLY HOLDING the IVORY SEASHELL-SHAPED BIKINI TOP "
            "(the UPPER piece with the two scallop-shell-shaped cups, NOT "
            "the bottom brief) with BOTH HANDS at chest height. Her hands "
            "are CLEARLY VISIBLE physically gripping the bikini top — the "
            "bikini is NOT floating, NOT levitating, NOT suspended in air "
            "by itself. Both shell-shaped cups, both shoulder straps and "
            "the pearl bead accents are FULLY CENTERED and ENTIRELY "
            "VISIBLE in the camera frame, not cropped, not cut off. She "
            "smiles excitedly with a 'look at this!' expression. Handheld "
            "iPhone front-camera selfie, slight wobble, real skin, phone "
            "sensor grain, warm daylight."
        ),
    },
    {
        "idx": 2,  # scene3
        "name": "scene3_build",
        "duration": 4,
        "character": f"{CHARACTER_BASE} {OUTFIT_BIKINI_ONLY}",
        "setting": (
            "Setting: same luxury yacht, she stands on the open white "
            "deck with the deep turquoise ocean and white yacht railing "
            "behind her, soft warm afternoon light, sea breeze moving "
            "her loose balayage waves naturally."
        ),
        "action": (
            "She is wearing the FULL ivory seashell bikini set on her "
            "body — top covering her chest, bottom on her hips, WITH the "
            "sheer light-grey/off-white crochet net pareo wrapped around "
            "her hips and tied at the side. NO t-shirt, NO tank top, NO "
            "street clothes — only the bikini and the matching pareo. "
            "She turns slowly in place to "
            "reveal the back of the bikini set — the back-tie strings "
            "tied behind her back CLEARLY VISIBLE, then looks back over "
            "her shoulder smiling. Handheld iPhone back-camera vertical "
            "9:16, gentle motion."
        ),
    },
    {
        "idx": 3,  # scene4
        "name": "scene4_payoff",
        "duration": 4,
        "character": f"{CHARACTER_BASE} {OUTFIT_BIKINI_ONLY}",
        "setting": (
            "Setting: same luxury yacht deck, warm afternoon light, "
            "soft sun flare and ocean horizon behind her."
        ),
        "action": (
            "Tight selfie close-up, she faces the camera directly with "
            "the FRONT of the bikini top visible — the two shell-shaped "
            "cups in front, the HALTER NECK STRAP rising from the inner "
            "corners of the cups up to behind her neck. The BACK-TIE "
            "STRAP is BEHIND her back (out of view), NOT crossing in "
            "front of her chest, NOT visible on the front of her body. "
            "She is wearing the pareo wrapped around her HIPS ONLY "
            "(below the waist) — but in this TIGHT SELFIE CLOSE-UP the "
            "pareo is BELOW THE FRAME and NOT VISIBLE; only her upper "
            "body is in the shot (bikini top, bare shoulders, neck, "
            "face, hair). ABSOLUTELY NO fabric, NO pareo, NO scarf, NO "
            "shawl, NO cloth of any kind on her shoulders, neck, chest, "
            "or upper body. Bare shoulders and bare collarbones visible "
            "with only the bikini halter strap. "
            "She throws a peace sign with one hand "
            "and laughs brightly. Front camera, candid joyful, warm "
            "daylight on her skin."
        ),
    },
]


def build_prompt(scene_def: dict) -> str:
    return (
        f"Character: {scene_def['character']} "
        f"{PRODUCT_DESC} "
        f"{scene_def['setting']} "
        f"Action: {scene_def['action']} "
        f"{FORMAT_SPEC}"
    )


async def render_one(kie, scene_def, ref_urls) -> str:
    log.info(f"Render: {scene_def['name']}")
    task_id = await asyncio.to_thread(
        kie.create_video,
        prompt=build_prompt(scene_def),
        duration=scene_def["duration"],
        aspect_ratio="9:16",
        generate_audio=False,
        reference_images=ref_urls,
    )
    result = await kie.async_poll_task(task_id)
    if result.get("status") != "success":
        raise RuntimeError(f"{scene_def['name']} fail: {result.get('error', '?')}")
    urls = result.get("urls") or []
    if not urls:
        raise RuntimeError(f"{scene_def['name']} URL boş")
    return urls[0] if not isinstance(urls[0], dict) else urls[0].get("url")


async def main():
    load_dotenv()
    imgbb = ImgBBService(os.environ["IMGBB_API_KEY"])
    kie = KieAIService(os.environ["KIE_API_KEY"])
    eleven = ElevenLabsService(
        os.environ["ELEVENLABS_API_KEY"], model_id="eleven_multilingual_v2"
    )
    log.info(f"KIE bakiye: {kie.get_credit_balance().get('data')}")

    ref_urls = upload_reference_images(imgbb)

    # Sadece sahne 4 render — sahne 1 ve 3 geçen turda OK
    todo = [s for s in NEW_SCENES if s["idx"] == 3]
    tasks = [render_one(kie, s, ref_urls) for s in todo]
    urls = await asyncio.gather(*tasks)

    for scene_def, url in zip(todo, urls):
        target = RESCUE_DIR / f"scene{scene_def['idx'] + 1}.mp4"
        log.info(f"Overwrite {target.name}")
        download(url, target)

    # Tüm 4 sahneyi remix et
    scene_paths = [RESCUE_DIR / f"scene{i + 1}.mp4" for i in range(4)]
    with tempfile.TemporaryDirectory(prefix="white_remix_") as tmp:
        tmp_dir = Path(tmp)
        audios = generate_voiceovers(eleven, tmp_dir)
        concat(scene_paths, audios, AMBIENT_PATH, OUTPUT_FILE)
    log.info(f"✅ {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
