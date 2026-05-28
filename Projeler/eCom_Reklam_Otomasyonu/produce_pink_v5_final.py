"""
v5 final — tasarruflu sahne 3 düzeltmesi.

Sahne 1 (sarışın balkon): v4 final'in ilk 5 saniyesinden crop edilir (re-render YOK)
Sahne 2 (kızıl havuz): mevcut v4_test_redhead.mp4 kullanılır
Sahne 3 (kumral plaj): yeni prompt ile yeniden üretilir — halter bağcıkları ve
                       uç boncuklarının CLEARLY VISIBLE olması vurgusu eklendi
                       (önceki sürümde strapless gibi çıkmıştı).

Çıktı: FINAL_REKLAM_LARA_ARI_PINK_v5.mp4
Maliyet: ~205 kredi (sadece sahne 3)
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from produce_pink_ad import (
    SCENES,
    render_scene,
    download,
    concat,
    upload_product_images,
)
from services.imgbb_service import ImgBBService
from services.kie_api import KieAIService
from logger import get_logger

log = get_logger("produce_pink_v5_final")

HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
V4_FINAL = HLK / "FINAL_REKLAM_LARA_ARI_PINK_v4.mp4"
SCENE2_EXISTING = HLK / "v4_test_redhead.mp4"
OUTPUT_FILE = HLK / "FINAL_REKLAM_LARA_ARI_PINK_v5.mp4"


def crop_scene1_from_v4(dst: Path) -> None:
    """v4 final'in ilk ~5 saniyesini sahne 1 olarak çıkarır."""
    from moviepy import VideoFileClip

    log.info(f"v4 finalden sahne 1 crop ediliyor (0-5s) → {dst.name}")
    src = VideoFileClip(str(V4_FINAL)).subclipped(0, 5)
    src.write_videofile(
        str(dst),
        codec="libx264",
        audio=False,
        fps=src.fps or 24,
        preset="medium",
        threads=4,
    )
    src.close()


async def main() -> None:
    load_dotenv()
    if not V4_FINAL.exists():
        raise SystemExit(f"v4 final yok: {V4_FINAL}")
    if not SCENE2_EXISTING.exists():
        raise SystemExit(f"Sahne 2 yok: {SCENE2_EXISTING}")

    imgbb = ImgBBService(os.environ["IMGBB_API_KEY"])
    kie = KieAIService(os.environ["KIE_API_KEY"])
    bal = kie.get_credit_balance().get("data", 0)
    log.info(f"Başlangıç bakiye: {bal} kredi (ihtiyaç ≈ 205)")

    ref_urls = upload_product_images(imgbb)  # PINK-b2 (üst)

    with tempfile.TemporaryDirectory(prefix="pink_v5_") as tmp:
        tmp_dir = Path(tmp)

        scene1 = tmp_dir / "scene1.mp4"
        crop_scene1_from_v4(scene1)

        log.info("Sahne 3 (kumral) yeniden render — halter bağcıkları net…")
        s3_url = await render_scene(kie, 2, SCENES[2], ref_urls)
        scene3 = tmp_dir / "scene3.mp4"
        download(s3_url, scene3)

        log.info(f"Concat: sahne1 (crop) + sahne2 ({SCENE2_EXISTING.name}) + sahne3 (yeni)")
        concat([scene1, SCENE2_EXISTING, scene3], OUTPUT_FILE)

    bal_after = kie.get_credit_balance().get("data", 0)
    log.info(f"🎬 v5 hazır: {OUTPUT_FILE}")
    log.info(f"Bitiş bakiye: {bal_after} (yakım: {bal - bal_after})")


if __name__ == "__main__":
    asyncio.run(main())
