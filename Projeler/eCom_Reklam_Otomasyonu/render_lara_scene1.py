"""
render_lara_scene1.py — LARA ARI Sunset Koleksiyonu — Sahne 1 (BRASIL Üzerinde - Konuşan Influencer)
Pipeline (KABUL EDILEN v1 YAKLASIMI):
  1. ElevenLabs Jessica sesi
  2. Anchor Frame (anchor_lara_brasil.jpg) → Seedance 2.0 first_frame_url (tutarli gorunum)
  3. LatentSync guidance_scale=1.0 (dogal lip-sync)

NOT: guidance_scale=2.5 ve Wav2Lip denendi — ikisi de kotu sonuc verdi.
Bu pipeline final/kabul edilen standarttir. Degistirme.
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
from services.elevenlabs_service import ElevenLabsService
from services.replicate_service import ReplicateService
from logger import get_logger

log = get_logger("render_lara_scene1")

# ============================================================================
# AYARLAR VE YOLLAR
# ============================================================================
HLK = Path(r"C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM")
SUNSET_DIR = HLK / "LARA_Sunset_230526"

# Orijinal referans görseller (anchor üretimi için)
CHARACTER_REFS = [
    SUNSET_DIR / "lara.jpeg",
    SUNSET_DIR / "lara_02.jpeg",
    SUNSET_DIR / "lara_03.jpeg"
]
PRODUCT_REF = SUNSET_DIR / "BRASIL-CROPTOP-SUNSETMARKET.jpg"

# ── Anchor Görseli (bir kere üret, sonra yeniden kullan) ──
# Bu dosya varsa tekrar üretme → zaman + kredi tasarrufu
# Yeni render her seferinde bir sonraki numara ile kaydedilir
# Mevcut final: SCENE1_BRASIL_WEARING_01.mp4
OUTPUT_FILE = SUNSET_DIR / "TEST_SCENE1_BRASIL_HOOK.mp4"
ANCHOR_FILE = SUNSET_DIR / "anchor_lara_brasil.jpg"

VOICEOVER_TEXT = "Kızlar selam! Lara Arı'nın yeni Sunset büstiyerine bayıldım, üzerimdeki duruşu şaka mı?!"

# ── Anchor-frame pipeline prompt'u ──
# NOT: Artık @Image1..@Image4 referansı YOK — first_frame_url ilk kareyi sabitliyor
SCENE_PROMPT = (
    "Continue naturally from the first frame. "
    "The young woman is on a sandy beach at golden-hour sunset, "
    "holding her smartphone in selfie mode, arm extended. "
    "She walks slowly along the beach shoreline at a steady pace. "
    "The selfie camera moves in sync with her, maintaining a constant distance so her upper body and the crop-top remain in steady, clear focus without scaling distortion, while the sunset beach background moves smoothly behind her. "
    "She looks directly into the lens with a highly energetic, warm, and playful expression, smiling naturally with her mouth closed (no speaking or lip movements). "
    "She gently touches the colorful beaded details on her white crocheted crop-top with her free hand, highlighting them. "
    "Warm golden sunset light, soft sea breeze, natural curly hair movement. "
    "Raw 9:16 vertical UGC vlog style, silent, 4 seconds."
)

# Anchor üretimi için karakter tanımı (yalnızca anchor_lara_brasil.jpg yoksa kullanılır)
ANCHOR_CHARACTER_PROMPT = (
    "Young Turkish woman, early 20s, long wavy dark curly hair, "
    "natural makeup, warm tanned skin, confident energetic expression. "
    "She is wearing the exact white ribbed crop-top with colorful beaded 'BRASIL' lettering "
    "as shown in the reference image. "
    "Standing on a sandy beach at golden sunset, holding smartphone in selfie mode, "
    "arm extended toward camera. "
    "Medium shot, upper body visible, 9:16 vertical portrait, photorealistic, golden hour light."
)


async def main():
    load_dotenv()

    log.info("=" * 70)
    log.info("LARA ARI — Sahne 1 v2 (Anchor Frame Pipeline - Tutarli Gorunum)")
    log.info("=" * 70)

    # API Anahtarlarını Al
    kie_key = os.environ.get("KIE_API_KEY")
    imgbb_key = os.environ.get("IMGBB_API_KEY")
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    replicate_key = os.environ.get("REPLICATE_API_TOKEN")

    if not all([kie_key, imgbb_key, elevenlabs_key, replicate_key]):
        log.error("Eksik API Anahtarlari! .env dosyasini kontrol edin.")
        return

    # Servisleri Başlat
    kie = KieAIService(kie_key)
    imgbb = ImgBBService(imgbb_key)
    elevenlabs = ElevenLabsService(elevenlabs_key)
    replicate = ReplicateService(replicate_key)

    # ── 1. ElevenLabs Dis Ses Uretimi ──
    log.info("\n[1/5] ElevenLabs ile Turkce dis ses uretiliyor...")
    try:
        audio_bytes = await asyncio.to_thread(
            elevenlabs.generate_speech,
            text=VOICEOVER_TEXT,
            voice_name="Jessica",  # Genc, neseli ve samimi (UGC/influencer)
            stability=0.30,
            similarity_boost=0.80,
            style=0.65,
        )
        audio_duration = ElevenLabsService.measure_audio_duration(audio_bytes)
        log.info(f"  Dis ses hazir. Sure: {audio_duration:.2f} saniye")

        # Replicate'e yukle (LatentSync adimi icin)
        log.info("  Replicate storage'a ses dosyasi yukleniyor...")
        audio_url = await replicate.async_upload_audio(audio_bytes)
        log.info(f"  Replicate Ses URL: {audio_url[:80]}...")
    except Exception as e:
        log.error(f"Dis ses uretim/yukleme hatasi: {e}")
        return

    # ── 2. Urun Gorseli ImgBB'ye Yukle ──
    log.info("\n[2/5] Urun gorseli ImgBB'ye yukleniyor...")
    if not PRODUCT_REF.exists():
        log.error(f"Urun gorseli bulunamadi: {PRODUCT_REF}")
        return
    product_res = imgbb.upload_image_bytes(PRODUCT_REF.read_bytes(), name=PRODUCT_REF.stem)
    product_imgbb_url = product_res["url"]
    log.info(f"  Urun BRASIL yuklendi: {product_imgbb_url[:80]}...")

    # ── 3. ANCHOR FRAME: Sabit ilk kare görseli ──
    log.info("\n[3/5] ANCHOR FRAME kontrol ediliyor...")

    anchor_imgbb_url = None

    if ANCHOR_FILE.exists():
        # ✅ Anchor hazır — direkt kullan (Nano Banana 2'ye kredi harcama)
        log.info(f"  Anchor gorseli hazir: {ANCHOR_FILE.name} ({ANCHOR_FILE.stat().st_size // 1024} KB)")
        log.info("  ImgBB'ye yukleniyor...")
        anchor_res = imgbb.upload_image_bytes(ANCHOR_FILE.read_bytes(), name=ANCHOR_FILE.stem)
        anchor_imgbb_url = anchor_res["url"]
        log.info(f"  Anchor URL: {anchor_imgbb_url[:80]}...")
    else:
        # Anchor yoksa Nano Banana 2 ile uret ve kaydet
        log.info("  Anchor gorseli bulunamadi — Nano Banana 2 ile uretiliyor...")
        log.info("  (BRASIL tishortunu giyinis manken + urun kompoziti)")
        try:
            anchor_kie_url = await kie.async_create_character_with_product(
                character_prompt=ANCHOR_CHARACTER_PROMPT,
                product_image_url=product_imgbb_url,
                aspect_ratio="9:16"
            )
            log.info(f"  Kie AI anchor uretildi: {anchor_kie_url[:80]}...")

            # Lokal kaydet — bir dahaki sahne/video icin yeniden kullanilir
            anchor_response = requests.get(anchor_kie_url, timeout=60)
            anchor_response.raise_for_status()
            ANCHOR_FILE.write_bytes(anchor_response.content)
            log.info(f"  Anchor kaydedildi: {ANCHOR_FILE}")

            # ImgBB'ye yukle
            anchor_res = imgbb.upload_image_bytes(ANCHOR_FILE.read_bytes(), name=ANCHOR_FILE.stem)
            anchor_imgbb_url = anchor_res["url"]
            log.info(f"  Anchor ImgBB'de: {anchor_imgbb_url[:80]}...")

        except Exception as e:
            log.error(f"Anchor frame uretim hatasi: {e}", exc_info=True)
            return

    # ── 4. Video Render (Kie AI — first_frame_url modu) ──
    log.info("\n[4/5] Seedance 2.0 ile video render ediliyor (first_frame_url modu)...")
    try:
        task_id = await asyncio.to_thread(
            kie.create_video,
            prompt=SCENE_PROMPT,
            first_frame_url=anchor_imgbb_url,   # ANCHOR → tutarli gorunum garantisi
            duration=4,
            aspect_ratio="9:16",
            resolution="720p",
            generate_audio=False,
            # NOT: first_frame_url kullanildiginda reference_images KULLANILMAZ
        )
        log.info(f"  Task ID: {task_id}")
        log.info("  Bekleniyor... (5-10 dakika)")

        result = await kie.async_poll_task(task_id)

        if result.get("status") != "success":
            log.error(f"  Render basarisiz: {result.get('error', 'unknown')}")
            return

        urls = result.get("urls") or []
        if not urls:
            log.error("  Video URL alinamadi")
            return

        raw_video_url = urls[0]
        if isinstance(raw_video_url, dict):
            raw_video_url = raw_video_url.get("url") or ""

        log.info(f"  Video hazir: {raw_video_url[:90]}...")

        # ── 5. Video ve Ses Birleştirme (off-camera voiceover, NO lip sync) ──
        log.info("\n[5/5] Replicate ile video ve ses birleştiriliyor (replace_audio=True)...")
        final_video_url = await replicate.async_merge_video_audio(
            video_url=raw_video_url,
            audio_url=audio_url,
            replace_audio=True,
            duration_mode="audio",
            audio_volume=2.5
        )
        log.info(f"  Birleştirildi: {final_video_url[:90]}...")

        # ── 6. Indir ve Kaydet ──
        log.info(f"\nFinal video indiriliyor -> {OUTPUT_FILE.name}")
        response = requests.get(final_video_url, timeout=180)
        response.raise_for_status()
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_bytes(response.content)
        size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
        log.info(f"  Kaydedildi: {OUTPUT_FILE}")
        log.info(f"  Boyut: {size_mb:.1f} MB")

        log.info("\n" + "=" * 70)
        log.info("SAHNE 1 v2 (ANCHOR FRAME PIPELINE) TAMAMLANDI!")
        log.info(f"  Anchor: {ANCHOR_FILE}")
        log.info(f"  Video:  {OUTPUT_FILE}")
        log.info("=" * 70)

    except Exception as e:
        log.error(f"  Birleştirme/Indirme hatasi: {e}", exc_info=True)
        return


if __name__ == "__main__":
    asyncio.run(main())
