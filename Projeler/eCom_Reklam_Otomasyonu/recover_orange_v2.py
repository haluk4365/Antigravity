"""
recover_orange_v2.py — Yerel 3 sahneden + Sahne 4 yeni render ile final üretim.

Önceki kurtarma adımında 3 sahne (Hook + Detail + Build) yerel diske indirildi:
  hlk-REKLAM\\2026 yaz_HANDMADE_BİKİNİ\\_rescue_turuncu\\
    scene1_hook.mp4
    scene2_detail.mp4
    scene3_build.mp4

Bu script:
  1. Yerel 3 mp4'ü olduğu gibi kullanır (KIE'ye gitmez, kredi harcamaz)
  2. Sahne 4'ü (Payoff 4s) KIE / Seedance ile yeniden render eder
  3. ElevenLabs Nisa ile 4 voiceover üretir
  4. moviepy ile birleştirip ses ekler → FINAL mp4

Çıktı: hlk-REKLAM\\FINAL_REKLAM_LARA_ARI_TURUNCU.mp4
"""

import asyncio
import os
import shutil
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.imgbb_service import ImgBBService
from services.kie_api import KieAIService
from services.elevenlabs_service import ElevenLabsService
from logger import get_logger

from produce_summer_bikini_orange import (
    SCENES,
    OUTPUT_FILE,
    upload_reference_images,
    render_scene,
    download,
    generate_voiceovers,
    concat_with_audio,
)

log = get_logger("recover_orange_v2")

RESCUE_DIR = Path(
    r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM"
    r"\2026 yaz_HANDMADE_BİKİNİ\_rescue_turuncu"
)
LOCAL_SCENES = [
    RESCUE_DIR / "scene1_hook.mp4",
    RESCUE_DIR / "scene2_detail.mp4",
    RESCUE_DIR / "scene3_build.mp4",
]


async def main() -> None:
    load_dotenv()
    for key in ("IMGBB_API_KEY", "KIE_API_KEY", "ELEVENLABS_API_KEY"):
        if not os.environ.get(key):
            raise SystemExit(f"{key} .env'de eksik")

    for p in LOCAL_SCENES:
        if not p.exists():
            raise SystemExit(f"Yerel sahne yok: {p}")

    imgbb = ImgBBService(os.environ["IMGBB_API_KEY"])
    kie = KieAIService(os.environ["KIE_API_KEY"])
    eleven = ElevenLabsService(os.environ["ELEVENLABS_API_KEY"])

    try:
        bal = kie.get_credit_balance()
        bal_val = bal.get("data", 0) if isinstance(bal, dict) else 0
        log.info(f"Kie AI bakiye: {bal_val} kredi (sahne 4 için ~165 yeter)")
    except Exception as exc:
        log.warning(f"Bakiye okunamadı: {exc}")

    log.info("ADIM 1/3 — Sahne 4'ü render et (Payoff 4s)")
    ref_urls = upload_reference_images(imgbb)
    scene4_url = await render_scene(kie, 3, SCENES[3], ref_urls)

    with tempfile.TemporaryDirectory(prefix="orange_v2_") as tmp:
        tmp_dir = Path(tmp)

        log.info("ADIM 2/3 — Sahne 4'ü indir + yerel 3 sahneyi kopyala")
        scene4_path = tmp_dir / "scene4.mp4"
        download(scene4_url, scene4_path)

        parts: list[Path] = []
        for i, src in enumerate(LOCAL_SCENES):
            dst = tmp_dir / f"scene{i + 1}.mp4"
            shutil.copy(src, dst)
            parts.append(dst)
        parts.append(scene4_path)

        log.info("ADIM 3/3 — ElevenLabs voiceover + moviepy birleştirme")
        audio_paths = generate_voiceovers(eleven, tmp_dir)
        concat_with_audio(parts, audio_paths, OUTPUT_FILE)

    log.info(f"🎬 Final reklam hazır: {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
