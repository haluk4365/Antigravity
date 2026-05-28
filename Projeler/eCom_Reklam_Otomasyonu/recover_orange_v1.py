"""
recover_orange_v1.py — Önceki başarısız run'dan kurtarma.

Önceki produce_summer_bikini_orange.py çalıştırmasında:
  - Sahne 1, 2, 3 task'ları başarıyla oluşturuldu (KIE'de render edildi)
  - Sahne 4 'Invalid duration' (3s) ile reddedildi → main() exit
  - Üretilen 3 mp4 indirilemedi, kredi yandı

Bu script:
  1. Önceki 3 task ID'sini KIE'den sorgular, video URL'lerini alır
  2. mp4'leri indirir (kredi harcamaz)
  3. Yalnızca sahne 4'ü yeniden render eder (~100 kredi)
  4. ElevenLabs ile 4 voiceover üretir
  5. moviepy ile birleştirir → FINAL_REKLAM_LARA_ARI_TURUNCU.mp4
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

from produce_summer_bikini_orange import (
    SCENES,
    OUTPUT_FILE,
    upload_reference_images,
    render_scene,
    download,
    generate_voiceovers,
    concat_with_audio,
)

log = get_logger("recover_orange_v1")

# Önceki run'da KIE'de oluşturulan task ID'leri (output log'undan)
PREVIOUS_TASK_IDS = {
    0: "235450941f5f67143d0d86ab7289b3c9",  # scene1_hook
    1: "f9456f0a2a688e856ce34870d3992200",  # scene2_detail
    2: "9f03023fe5d8182eaa466d944dca0fb4",  # scene3_build
}


async def fetch_existing_scene(kie: KieAIService, idx: int, task_id: str) -> str:
    log.info(f"[Eski sahne {idx + 1}] task={task_id} — durum sorgulanıyor")
    result = await kie.async_poll_task(task_id)
    if result.get("status") != "success":
        raise RuntimeError(
            f"Eski sahne {idx + 1} kurtarılamadı: "
            f"{result.get('error', 'unknown')} — "
            f"KIE bakiyesini yükleyip baştan üret."
        )
    urls = result.get("urls") or []
    if not urls:
        raise RuntimeError(f"Sahne {idx + 1} URL boş: {result}")
    video_url = urls[0]
    if isinstance(video_url, dict):
        video_url = video_url.get("url") or ""
    log.info(f"[Eski sahne {idx + 1}] kurtarıldı: {video_url[:90]}…")
    return video_url


async def main() -> None:
    load_dotenv()
    for key in ("IMGBB_API_KEY", "KIE_API_KEY", "ELEVENLABS_API_KEY"):
        if not os.environ.get(key):
            raise SystemExit(f"{key} .env'de eksik")

    imgbb = ImgBBService(os.environ["IMGBB_API_KEY"])
    kie = KieAIService(os.environ["KIE_API_KEY"])
    eleven = ElevenLabsService(os.environ["ELEVENLABS_API_KEY"])

    try:
        bal = kie.get_credit_balance()
        bal_val = bal.get("data", 0) if isinstance(bal, dict) else 0
        log.info(f"Kie AI bakiye: {bal_val} kredi (sadece sahne 4 için ~100 yeter)")
    except Exception as exc:
        log.warning(f"Bakiye okunamadı: {exc}")

    log.info("ADIM 1/4 — Önceki 3 task'ı paralel sorgulayıp video URL'lerini al")
    fetch_tasks = [
        fetch_existing_scene(kie, idx, tid)
        for idx, tid in PREVIOUS_TASK_IDS.items()
    ]
    existing_urls = await asyncio.gather(*fetch_tasks)

    log.info("ADIM 2/4 — Sahne 4'ü yeniden render et")
    ref_urls = upload_reference_images(imgbb)
    scene4_url = await render_scene(kie, 3, SCENES[3], ref_urls)

    all_scene_urls = list(existing_urls) + [scene4_url]
    log.info(f"4 sahne URL hazır: {len(all_scene_urls)} adet")

    with tempfile.TemporaryDirectory(prefix="orange_recover_") as tmp:
        tmp_dir = Path(tmp)

        log.info("ADIM 3/4 — Tüm sahne mp4'lerini indir")
        parts: list[Path] = []
        for i, url in enumerate(all_scene_urls):
            part = tmp_dir / f"scene{i + 1}.mp4"
            download(url, part)
            parts.append(part)

        log.info("ADIM 4/4 — ElevenLabs voiceover + moviepy birleştirme")
        audio_paths = generate_voiceovers(eleven, tmp_dir)
        concat_with_audio(parts, audio_paths, OUTPUT_FILE)

    log.info(f"🎬 Kurtarma tamamlandı: {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
