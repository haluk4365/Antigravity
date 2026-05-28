"""
produce_lara_sunset_v2.py — LARA ARI Sunset Koleksiyonu — 3 Sahne (Hibrit Çözünürlük)
Süre: 4s + 4s + 4s = 12 saniye
Sahne 1 (720p): BRASIL Crop-Top (Hook)
Sahne 2 (720p): TURKISH DELIGHT Crop-Top (Detail)
Sahne 3 (480p): BRASIL Tank-Top (Lifestyle/Closing)
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

log = get_logger("produce_lara_sunset_v2")

# ============================================================================
# DOSYA YOLLARI
# ============================================================================
HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

CHARACTER_REFS = [
    SUNSET_DIR / "lara.jpeg",
    SUNSET_DIR / "lara_02.jpeg",
    SUNSET_DIR / "lara_03.jpeg"
]

PRODUCT_BRASIL = SUNSET_DIR / "BRASIL-CROPTOP-SUNSETMARKET.jpg"
PRODUCT_TURKISH = SUNSET_DIR / "TURKISHDELIGHT-CROPTOP-SUNSETMARKET.jpg"
PRODUCT_TANKTOP = SUNSET_DIR / "BRASIL-TANKTOP-SUNSETMARKET.jpg"

SCENE1_FILE = SUNSET_DIR / "SCENE1_BRASIL.mp4"
SCENE2_FILE = SUNSET_DIR / "SCENE2_TURKISH.mp4"
SCENE3_FILE = SUNSET_DIR / "SCENE3_TANKTOP.mp4"
FINAL_FILE = SUNSET_DIR / "FINAL_REKLAM_LARA_SUNSET_V2.mp4"

# ============================================================================
# PROMPTLAR (Manken ve Ürün Ayrıştırılmış)
# ============================================================================
SCENE1_PROMPT = (
    "@Image1 and @Image2 and @Image3 as character references for the woman. @Image4 as the product reference. "
    "A confident young Turkish woman Lara holds the product @Image4 in front of her chest with both hands, "
    "showing it directly to the camera. The camera is steady and locked on the product. Warm golden sunset beach light "
    "shines on the product, highlighting the vibrant green, yellow, blue, and white beads spelling \"BRASIL\". "
    "The hand-crocheted white fabric texture, individual crochet stitches, and pearl-like quality of the beads "
    "must be preserved exactly as in @Image4, with no morphing or distortion of the text or shape. She smiles warmly. "
    "Smooth, stable 9:16 vertical fashion editorial video, silent, 4 seconds, no camera shake, maintain face consistency."
)

SCENE2_PROMPT = (
    "@Image1 and @Image2 and @Image3 as character references for the woman. @Image4 as the product reference. "
    "The young Turkish woman Lara is wearing the product @Image4. She stands on a sandy beach during sunset, "
    "looking into the camera with a warm smile. The warm amber sunlight highlights the white crocheted texture of "
    "the top she is wearing. The red embroidered \"Turkish Delight\" text and the lustrous white pearl details "
    "scattered on the top must be preserved exactly as shown in @Image4, capturing the fine textile texture. "
    "Camera does a very slow and smooth dolly-in. Cinematic fashion commercial, 9:16 dikey, silent, 4 seconds, "
    "no logo or fabric distortion, maintain face consistency."
)

SCENE3_PROMPT = (
    "@Image1 and @Image2 and @Image3 as character references for the woman. @Image4 as the product reference. "
    "The young Turkish woman Lara wears the product @Image4, walking confidently along the shoreline at sunset. "
    "She turns her head towards the camera, smiling warmly. The soft breeze moves her curly dark hair. "
    "The texture and exact cut of the white crocheted tank-top @Image4 is preserved perfectly. "
    "The camera is smooth and stable, gradually zooming in on her. Beautiful warm sunset color grading, "
    "9:16 vertical, silent, 4 seconds, no distortion, maintain face consistency."
)

# ============================================================================
# RENDER FONKSİYONU
# ============================================================================
async def render_scene(kie: KieAIService, idx: int, name: str, prompt: str,
                       duration: int, resolution: str, ref_urls: list[str], output_path: Path) -> bool:
    """Tek bir sahneyi render et."""
    log.info(f"\n[Sahne {idx}] {name} ({resolution}) — Başlıyor...")
    try:
        task_id = await asyncio.to_thread(
            kie.create_video,
            prompt=prompt,
            duration=duration,
            aspect_ratio="9:16",
            resolution=resolution,
            generate_audio=False,
            reference_images=ref_urls,
        )
        log.info(f"  [Sahne {idx}] Task ID: {task_id}")
        log.info(f"  [Sahne {idx}] Bekleniyor... (3-5 dakika)")

        result = await kie.async_poll_task(task_id)

        if result.get("status") != "success":
            log.error(f"  [Sahne {idx}] HATA: {result.get('error', 'unknown')}")
            return False

        urls = result.get("urls") or []
        if not urls:
            log.error(f"  [Sahne {idx}] Video URL alınamadı")
            return False

        video_url = urls[0]
        if isinstance(video_url, dict):
            video_url = video_url.get("url") or ""

        log.info(f"  [Sahne {idx}] Video hazır")

        # İndir
        log.info(f"  [Sahne {idx}] İndiriliyor...")
        response = requests.get(video_url, timeout=180)
        response.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        size_mb = output_path.stat().st_size / (1024*1024)
        log.info(f"  [Sahne {idx}] Kaydedildi: {output_path.name} ({size_mb:.1f} MB)")

        return True

    except Exception as e:
        log.error(f"  [Sahne {idx}] Render hatası: {e}", exc_info=True)
        return False

# ============================================================================
# MAIN
# ============================================================================
async def main():
    load_dotenv()

    log.info("=" * 70)
    log.info("LARA ARI Sunset Reklamı — V2 Hibrit Üretim")
    log.info("=" * 70)

    kie_key = os.environ.get("KIE_API_KEY")
    if not kie_key:
        log.error("KIE_API_KEY bulunamadı!")
        return

    kie = KieAIService(kie_key)
    imgbb_key = os.environ.get("IMGBB_API_KEY")
    imgbb = ImgBBService(imgbb_key) if imgbb_key else None

    # ── 1. Görselleri ImgBB'ye Yükle ──
    log.info("\nGörselleri ImgBB'ye yüklüyorum...")
    manken_urls = []
    
    # Manken resimleri (aynı sıra)
    for path in CHARACTER_REFS:
        if not path.exists():
            log.error(f"Manken görseli bulunamadı: {path}")
            return
        if imgbb:
            res = imgbb.upload_image_bytes(path.read_bytes(), name=path.stem)
            manken_urls.append(res["url"])
            log.info(f"  Manken {path.name} yüklendi")

    # Ürün resimleri
    product_urls = {}
    for label, path in [("BRASIL", PRODUCT_BRASIL), 
                         ("TURKISH", PRODUCT_TURKISH), 
                         ("TANKTOP", PRODUCT_TANKTOP)]:
        if not path.exists():
            log.error(f"Ürün görseli bulunamadı: {path}")
            return
        if imgbb:
            res = imgbb.upload_image_bytes(path.read_bytes(), name=path.stem)
            product_urls[label] = res["url"]
            log.info(f"  Ürün {label} yüklendi")

    # ── 2. Kredi Bakiye Kontrolü ──
    log.info("\nBakiye kontrol ediliyor...")
    try:
        balance_data = await asyncio.to_thread(kie.get_credit_balance)
        balance = 396.0
        if balance_data and isinstance(balance_data, dict):
            data_block = balance_data.get("data", balance_data)
            if isinstance(data_block, dict):
                balance = float(data_block.get("balance", data_block.get("credit", 0)))
            else:
                balance = float(data_block)
        
        required = (4 * 25) + (4 * 25) + (4 * 11.5)  # Sahne 1, 2 (720p) + Sahne 3 (480p) = 246 kredi
        log.info(f"  Bakiye: {balance:.1f} kredi")
        log.info(f"  Gerekli (Hibrit): {required:.1f} kredi")
        if balance < required:
            log.error(f"  ❌ Yetersiz bakiye! ({balance:.1f} < {required:.1f})")
            return
        log.info(f"  ✅ Yeterli")
    except Exception as e:
        log.warning(f"  Bakiye kontrol edilemedi, devam ediliyor: {e}")

    # ── 3. Sahneleri Paralel Olarak Render Et ──
    log.info("\nSahneler paralel olarak render ediliyor...\n")

    # Sahnelerin özel referans listeleri (Manken 1,2,3 + Ürün)
    ref_scene1 = manken_urls + [product_urls["BRASIL"]]
    ref_scene2 = manken_urls + [product_urls["TURKISH"]]
    ref_scene3 = manken_urls + [product_urls["TANKTOP"]]

    task1 = asyncio.create_task(
        render_scene(kie, 1, "BRASIL Crop-top", SCENE1_PROMPT, 4, "720p", ref_scene1, SCENE1_FILE)
    )
    task2 = asyncio.create_task(
        render_scene(kie, 2, "TURKISH DELIGHT", SCENE2_PROMPT, 4, "720p", ref_scene2, SCENE2_FILE)
    )
    task3 = asyncio.create_task(
        render_scene(kie, 3, "BRASIL Tank-top", SCENE3_PROMPT, 4, "480p", ref_scene3, SCENE3_FILE)
    )

    results = await asyncio.gather(task1, task2, task3)

    if not all(results):
        log.error("\n❌ Bir veya daha fazla sahnenin üretimi başarısız oldu!")
        return

    # ── 4. Sahneleri Birleştir ──
    log.info("\n" + "=" * 70)
    log.info("Sahneler moviepy ile birleştiriliyor...")
    log.info("=" * 70)

    try:
        from moviepy import VideoFileClip, concatenate_videoclips

        scene1 = VideoFileClip(str(SCENE1_FILE))
        scene2 = VideoFileClip(str(SCENE2_FILE))
        scene3 = VideoFileClip(str(SCENE3_FILE))

        # Sahne 3'ü (480p) Sahne 1 ve 2 (720p) boyutuna getirmek için yeniden boyutlandır
        # Genellikle 720p vertical Seedance çıkışı 496x864 pikseldir
        w, h = scene1.size
        log.info(f"Sahne 1 Boyut: {w}x{h}, Sahne 3 bu boyuta göre ölçeklendiriliyor.")
        scene3_resized = scene3.resize(newsize=(w, h))

        clips = [scene1, scene2, scene3_resized]
        final = concatenate_videoclips(clips, method="compose")
        FINAL_FILE.parent.mkdir(parents=True, exist_ok=True)
        final.write_videofile(
            str(FINAL_FILE),
            fps=24,
            codec="libx264",
            audio=False,
            verbose=False,
            logger=None
        )

        size_mb = FINAL_FILE.stat().st_size / (1024*1024)
        log.info(f"\n✅ Final video birleştirildi: {FINAL_FILE.name} ({size_mb:.1f} MB)")
        log.info(f"   Konum: {FINAL_FILE}")
        log.info(f"\n" + "=" * 70)
        log.info("✅ LARA ARI REKLAM FİLMİ BAŞARIYLA TAMAMLANDI!")
        log.info("=" * 70)

    except Exception as e:
        log.error(f"Birleştirme hatası: {e}", exc_info=True)
        return

if __name__ == "__main__":
    asyncio.run(main())
