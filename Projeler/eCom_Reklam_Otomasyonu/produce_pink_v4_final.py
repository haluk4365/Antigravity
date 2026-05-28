"""
v4 final — tasarruflu: sahne 2 (kızıl havuz) için mevcut v4_test_redhead.mp4
kullanılır; sahne 1 (sarışın balkon) ve sahne 3 (kumral plaj) yeniden üretilir.
3'ü birleştirilip FINAL_REKLAM_LARA_ARI_PINK_v4.mp4 olarak kaydedilir.

Stratejik nokta (v3 → v4 değişikliği): reference image olarak yalnızca
PINK-b2 (üst) kullanılır; alt parça prompt'tan tarif edilir (Seedance'in
alt'ın çiçeklerini üstün bağcığına kopyalama hatası düzeltildi).
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from produce_pink_ad import (
    SCENES,
    build_prompt,
    render_scene,
    download,
    concat,
    upload_product_images,
)
from services.imgbb_service import ImgBBService
from services.kie_api import KieAIService
from logger import get_logger

log = get_logger("produce_pink_v4_final")

SCENE2_EXISTING = Path(
    r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\v4_test_redhead.mp4"
)
OUTPUT_FILE = Path(
    r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\FINAL_REKLAM_LARA_ARI_PINK_v4.mp4"
)


async def main() -> None:
    load_dotenv()
    if not SCENE2_EXISTING.exists():
        raise SystemExit(f"Sahne 2 dosyası bulunamadı: {SCENE2_EXISTING}")

    imgbb = ImgBBService(os.environ["IMGBB_API_KEY"])
    kie = KieAIService(os.environ["KIE_API_KEY"])

    bal = kie.get_credit_balance().get("data", 0)
    log.info(f"Başlangıç bakiye: {bal} kredi (ihtiyaç ≈ 410)")

    ref_urls = upload_product_images(imgbb)  # sadece PINK-b2 (üst)

    log.info("Sahne 1 (sarışın) ve Sahne 3 (kumral) paralel render…")
    # SCENES içinde index 0=sarışın, 1=kızıl, 2=kumral
    tasks = [
        render_scene(kie, 0, SCENES[0], ref_urls),
        render_scene(kie, 2, SCENES[2], ref_urls),
    ]
    s1_url, s3_url = await asyncio.gather(*tasks)

    with tempfile.TemporaryDirectory(prefix="pink_v4_") as tmp:
        tmp_dir = Path(tmp)
        s1 = tmp_dir / "scene1.mp4"
        s3 = tmp_dir / "scene3.mp4"
        download(s1_url, s1)
        download(s3_url, s3)
        # Sahne 2 olarak mevcut v4 test dosyasını kullan
        log.info(f"Sahne 2 olarak mevcut dosya kullanılıyor: {SCENE2_EXISTING.name}")
        concat([s1, SCENE2_EXISTING, s3], OUTPUT_FILE)

    bal_after = kie.get_credit_balance().get("data", 0)
    log.info(f"🎬 Reklam hazır: {OUTPUT_FILE}")
    log.info(f"Bitiş bakiye: {bal_after} kredi (yakım: {bal - bal_after})")


if __name__ == "__main__":
    asyncio.run(main())
