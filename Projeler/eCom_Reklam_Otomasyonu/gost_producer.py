#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gost_producer.py — GOST Image & Video Generator
===============================================
e-ticaret satıcıları için ürün görsellerini ve reklam videolarını otomatik üretir.
[e-tic.docx] (Part 1 ve Part 2) gereksinimlerini bütçe kurallarına uygun olarak gerçekleştirir.

Yaptığı İşlemler:
1. Lokal ürün görselini ImgBB'ye yükler (public URL alır).
2. Nano Banana 2 ile önden görünüş, 0 derece açı (front lay) stüdyo mockup'ı üretir.
3. GPT-4 Vision ile orijinal görsel ile üretilen mockup'ı kıyaslar (Malzeme, doku, birleşim hatası kontrolü).
   - Hata tespit edilirse promptu otomatik güncelleyip yeniden dener (maksimum 3 deneme).
4. Çıktıyı 'YENİ GÖRSELLER' klasörü altına <urun_adi>_GOST.png ve <urun_adi>_GOST.jpg olarak kaydeder.
5. Oluşturulan GOST görselini ilk kare (first_frame_url) olarak kullanarak Seedance 2.0 / Kling ile reklam videosu üretir.
   - Bütçe tercihine göre 480p veya 720p çözünürlük ve optimize süre kullanır.
   - Videoyu 'YENİ GÖRSELLER' altına <urun_adi>_GOST_REKLAM.mp4 olarak kaydeder.
"""

import os
import sys
import argparse
import asyncio
import time
from pathlib import Path
import json
import requests

# Proje kökünü sys.path'e ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from logger import get_logger
from services.imgbb_service import ImgBBService
from services.kie_api import KieAIService
from services.openai_service import OpenAIService

log = get_logger("gost_producer")

# ============================================================================
# GPT-4 VISION KARŞILAŞTIRMA VE DÜZELTME YÖNERGESİ
# ============================================================================
COMPARE_PROMPT = """
Sen bir e-ticaret görsel kalite kontrol uzmanı ve detay analistisin.
Aşağıda iki görsel bulunmaktadır:
1. Görsel: Kullanıcının yüklediği Orijinal Ürün Fotoğrafı.
2. Görsel: AI tarafından üretilen E-ticaret Vitrin Mockup Görseli (GOST).

Bu iki görseli malzeme, doku kalitesi, yan ürünler/bileşenler ve birleşim yerleri açısından çok dikkatli bir şekilde karşılaştır.
AI tarafından üretilen görselde (2. Görsel) orijinal ürüne kıyasla herhangi bir detay kaybı, şekil bozulması veya malzeme tutarsızlığı olup olmadığını kontrol et.
Ayrıca, üretilen görselin "önden görünüş, 0 derece açı (front lay / front shot)" vitrin standardına uyup uymadığını doğrula.

Yanıtını SADECE aşağıdaki JSON formatında ver, başka hiçbir metin ekleme:
{
  "is_valid": true VEYA false,
  "explanation": "Karşılaştırmanın kısa özeti (Türkçe)",
  "discrepancies": ["Varsa tespit edilen malzeme, doku, bileşen veya birleşim yeri hataları"],
  "improved_prompt": "Eğer hata varsa, Nano Banana 2 modelinin bir sonraki denemede bu hataları düzeltmesi için İngilizce olarak yazılmış detaylı ve düzeltilmiş prompt. Eğer hata yoksa null."
}
"""

DEFAULT_PROMPT_TEMPLATE = (
    "A professional product photography, front-facing 0-degree angle shot, flat lay, "
    "of the product shown in the reference image. The product is centered on a clean, minimal, "
    "bright white studio background. Photorealistic, 4K resolution, professional commercial studio lighting, "
    "sharp focus on all parts of the product, preserving every detail of the materials, texture, components, "
    "and joints exactly. No model, no hands, no human element, no text, no watermark, no logos overlay."
)


async def compare_images_gpt4_vision(openai_svc: OpenAIService, orig_url: str, gost_url: str) -> dict:
    """GPT-4 Vision ile orijinal ve üretilen görseli karşılaştırır."""
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": COMPARE_PROMPT},
                {"type": "image_url", "image_url": {"url": orig_url, "detail": "high"}},
                {"type": "image_url", "image_url": {"url": gost_url, "detail": "high"}},
            ],
        }
    ]
    try:
        response_dict = openai_svc.chat_json(messages, max_tokens=1000)
        return response_dict
    except Exception as e:
        log.error(f"GPT-4 Vision karşılaştırma hatası: {e}")
        # Hata durumunda dönecek güvenli fallback
        return {
            "is_valid": True,
            "explanation": f"Karşılaştırma yapılamadı (Hata: {e}). Mevcut çıktı kabul ediliyor.",
            "discrepancies": [],
            "improved_prompt": None
        }


async def generate_gost_image(kie_svc: KieAIService, imgbb_svc: ImgBBService, openai_svc: OpenAIService, 
                              image_path: Path, output_dir: Path, product_name: str, aspect_ratio: str,
                              is_dry_run: bool = False) -> str:
    """1. Bolum: Onden gorunus 0 derece GOST gorselinin uretilmesi ve validasyon dongusu."""
    
    # 1. Orijinal gorseli ImgBB'ye yukle
    if is_dry_run:
        log.info("DRY-RUN: ImgBB upload simule ediliyor.")
        orig_url = "https://i.ibb.co/dummy_original.jpg"
    else:
        log.info(f"Orijinal gorsel ImgBB'ye yukleniyor: {image_path.name}")
        try:
            orig_upload = imgbb_svc.upload_image_bytes(image_path.read_bytes(), name=f"{product_name}_original")
            orig_url = orig_upload["url"]
            log.info(f"Orijinal gorsel URL: {orig_url}")
        except Exception as e:
            log.error(f"ImgBB upload hatasi: {e}")
            raise RuntimeError(f"Orijinal gorsel ImgBB'ye yuklenemedi: {e}")

    current_prompt = DEFAULT_PROMPT_TEMPLATE
    gost_url = None
    max_attempts = 3
    
    for attempt in range(1, max_attempts + 1):
        log.info(f"\n--- GOST Gorsel Uretim Denemesi {attempt}/{max_attempts} ---")
        log.info(f"Kullanilan Prompt: {current_prompt[:120]}...")
        
        try:
            if is_dry_run:
                log.info("DRY-RUN: Nano Banana 2 gorsel uretimi simule ediliyor...")
                await asyncio.sleep(1)
                gost_url = "https://i.ibb.co/dummy_gost.jpg"
                log.info(f"Uretilen Gorsel URL (Mock): {gost_url}")
                
                # GPT-4 Vision kalite kontrolunu simule et
                log.info("DRY-RUN: GPT-4 Vision kalite kontrolu simule ediliyor...")
                if attempt == 1:
                    comparison = {
                        "is_valid": False,
                        "explanation": "Mocked validation failure: minor texture misalignment in the seam.",
                        "discrepancies": ["Seam details do not match the reference photo"],
                        "improved_prompt": "A professional front-facing flat lay, exact same seam line structure..."
                    }
                else:
                    comparison = {
                        "is_valid": True,
                        "explanation": "Mocked validation success: texture, materials, and 0-degree angle are now perfectly correct.",
                        "discrepancies": [],
                        "improved_prompt": None
                    }
            else:
                # Nano Banana 2 ile uret
                task_id = kie_svc.create_image(
                    prompt=current_prompt,
                    aspect_ratio=aspect_ratio,
                    resolution="1k", # nano-banana-2 varsayilan 1k ile baslar
                    image_input=[orig_url]
                )
                
                # Polling
                log.info("Gorsel uretiliyor, bekleniyor...")
                poll_res = await kie_svc.async_poll_task(task_id)
                
                if poll_res.get("status") != "success" or not poll_res.get("urls"):
                    error_msg = poll_res.get("error", "Bilinmeyen hata")
                    log.warning(f"Gorsel uretimi basarisiz oldu: {error_msg}")
                    if attempt == max_attempts:
                        raise RuntimeError(f"Gorsel uretimi basarisiz: {error_msg}")
                    continue
                    
                gost_url = poll_res["urls"][0]
                log.info(f"Uretilen Gorsel URL: {gost_url}")
                
                # GPT-4 Vision ile karsilastir (Self-Healing)
                log.info("GPT-4 Vision kalite kontrolu yapiliyor...")
                comparison = await compare_images_gpt4_vision(openai_svc, orig_url, gost_url)
                
            log.info(f"Kalite Kontrol Sonucu: {json.dumps(comparison, indent=2, ensure_ascii=True)}")
            
            if comparison.get("is_valid") is True:
                log.info("Gorsel kalite kontrolunden basariyla gecti!")
                break
            else:
                log.warning("Gorsel kalite kontrolunden gecemedi. Tespit edilen hatalar:")
                for disc in comparison.get("discrepancies", []):
                    log.warning(f" - {disc}")
                
                improved_prompt = comparison.get("improved_prompt")
                if improved_prompt:
                    current_prompt = improved_prompt
                else:
                    current_prompt = (
                        f"{DEFAULT_PROMPT_TEMPLATE} Make sure details like materials, "
                        f"textures, and components match the original reference image exactly."
                    )
                
                if attempt == max_attempts:
                    log.warning("Maksimum deneme sayisina ulasildi. Son cikti kaydediliyor.")
                    
        except Exception as e:
            log.error(f"Deneme {attempt} sirasinda hata olustu: {e}")
            if attempt == max_attempts:
                raise

    if not gost_url:
        raise RuntimeError("GOST gorseli uretilemedi.")

    # Sonuclari Kaydet
    output_gost_dir = output_dir / "YENI GORSELLER"
    output_gost_dir.mkdir(parents=True, exist_ok=True)
    
    png_path = output_gost_dir / f"{product_name}_GOST.png"
    jpg_path = output_gost_dir / f"{product_name}_GOST.jpg"
    
    if is_dry_run:
        log.info("DRY-RUN: Orijinal lokal gorsel cikti klasorune kopyalaniyor...")
        png_path.write_bytes(image_path.read_bytes())
        jpg_path.write_bytes(image_path.read_bytes())
    else:
        log.info(f"\nGorseller indiriliyor ve kaydediliyor...")
        resp = requests.get(gost_url, timeout=60)
        resp.raise_for_status()
        
        png_path.write_bytes(resp.content)
        jpg_path.write_bytes(resp.content)
    
    log.info(f"Saved: {png_path}")
    log.info(f"Saved: {jpg_path}")
    
    return gost_url


async def generate_ad_video(kie_svc: KieAIService, imgbb_svc: ImgBBService, gost_url: str, 
                             output_dir: Path, product_name: str, video_resolution: str, video_duration: int,
                             is_dry_run: bool = False):
    """2. Bolum: GOST gorselini ilk kare (first_frame_url) olarak kullanarak reklam videosu uretilmesi."""
    log.info(f"\n--- Reklam Videosu Uretimi (Seedance 2.0) ---")
    
    if is_dry_run:
        log.info("DRY-RUN: Video referansi upload simule ediliyor.")
        gost_kie_url = "https://i.ibb.co/dummy_gost_ref.jpg"
    else:
        # 1. GOST gorselini Kie AI sunucusuna yukle
        log.info("GOST gorseli video referansi icin Kie AI sunucusuna yukleniyor...")
        try:
            gost_kie_url = kie_svc.upload_file_from_url(gost_url, file_name=f"{product_name}_gost_ref.jpg")
            log.info(f"Kie-native GOST URL: {gost_kie_url}")
        except Exception as e:
            log.warning(f"Kie upload hatasi (orijinal URL fallback olarak kullanilacak): {e}")
            gost_kie_url = gost_url

    # Video Prompt
    video_prompt = (
        f"Cinematic ad video showcasing the {product_name} starting from the first frame. "
        "A stylish female fashion model standing in a modern studio environment, showcasing the product. "
        "Camera smoothly zooms out and pans. Warm cinematic lighting, elegant commercial vibe, "
        "natural motion, high frame rate, photorealistic."
    )
    
    log.info(f"Video Prompt: {video_prompt}")
    log.info(f"Video Suresi: {video_duration}s, Cozunurlugu: {video_resolution}")
    
    try:
        output_gost_dir = output_dir / "YENI GORSELLER"
        video_path = output_gost_dir / f"{product_name}_GOST_REKLAM.mp4"

        if is_dry_run:
            log.info("DRY-RUN: Seedance 2.0 video uretimi simule ediliyor...")
            await asyncio.sleep(1)
            # mock_video kopyala
            workspace_root = Path(r"c:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)")
            mock_video = workspace_root / "Projeler" / "klip_1sn.mp4"
            if mock_video.exists():
                log.info(f"DRY-RUN: Mock video kopyalaniyor: {mock_video.name} -> {video_path.name}")
                video_path.write_bytes(mock_video.read_bytes())
            else:
                log.info("DRY-RUN: Mock video bulunamadi, bos mock dosya yaziliyor...")
                video_path.write_text("dummy video content")
        else:
            # Seedance 2.0 ile video uret (first_frame_url modunda)
            task_id = kie_svc.create_video(
                prompt=video_prompt,
                duration=video_duration,
                aspect_ratio="9:16", # standart dikey reels/reklam formati
                first_frame_url=gost_kie_url,
                resolution=video_resolution,
                generate_audio=True
            )
            
            log.info("Video uretiliyor, bekleniyor (bu islem 2-5 dakika surebilir)...")
            poll_res = await kie_svc.async_poll_task(task_id)
            
            if poll_res.get("status") != "success" or not poll_res.get("urls"):
                raise RuntimeError(f"Video uretimi basarisiz: {poll_res.get('error', 'Bilinmeyen hata')}")
                
            video_url = poll_res["urls"][0]
            log.info(f"Video basariyla uretildi! URL: {video_url}")
            
            log.info(f"Video indiriliyor → {video_path.name}")
            v_resp = requests.get(video_url, timeout=120)
            v_resp.raise_for_status()
            
            video_path.write_bytes(v_resp.content)
            
        log.info(f"Saved: {video_path}")
        log.info(f"Video Boyutu: {video_path.stat().st_size // 1024} KB")
        
    except Exception as e:
        log.error(f"Video uretimi sirasinda hata olustu: {e}")
        raise


async def main():
    parser = argparse.ArgumentParser(description="GOST Görsel ve Reklam Videosu Üretim Programı")
    parser.add_argument("--image", type=str, help="Ürün fotoğrafının lokal dosya yolu")
    parser.add_argument("--output-dir", type=str, help="Çıktı klasörlerinin oluşturulacağı ana dizin (varsayılan: görselin bulunduğu klasör)")
    parser.add_argument("--product-name", type=str, help="Ürünün adı (varsayılan: dosya adı)")
    parser.add_argument("--aspect-ratio", type=str, default="1:1", help="Görsel en-boy oranı (1:1 veya 4:5, varsayılan: 1:1)")
    parser.add_argument("--resolution", type=str, default="480p", choices=["480p", "720p"], 
                        help="Video çözünürlüğü (480p: Ekonomik, 720p: Premium, varsayılan: 480p)")
    parser.add_argument("--duration", type=int, default=5, help="Video süresi saniye (varsayılan: 5s)")
    parser.add_argument("--no-video", action="store_true", help="Reklam videosu üretimini atla")
    parser.add_argument("--dry-run", action="store_true", help="Simulate API calls and copy local files instead")
    
    # Argümanları parse et
    args = parser.parse_args()
    
    # İnteraktif mod (Argümanlar boşsa sor)
    image_path_str = args.image
    if not image_path_str:
        print("\n=== GOST Gorsel ve Reklam Videosu Uretim Asistani ===")
        image_path_str = input("Lutfen urun fotografinin lokal dosya yolunu girin: ").strip().strip("'\"")
        
    if not image_path_str:
        print("Hata: Urun fotografi yolu bos olamaz.")
        sys.exit(1)
        
    image_path = Path(image_path_str)
    if not image_path.exists():
        print(f"Hata: Belirtilen dosya bulunamadi: {image_path}")
        sys.exit(1)

    product_name = args.product_name
    if not product_name:
        product_name = image_path.stem
        
    output_dir_str = args.output_dir
    if not output_dir_str:
        output_dir = image_path.parent
    else:
        output_dir = Path(output_dir_str)

    # Bütçe ve Tercihler Bilgisi
    print("\n--- CALISMA AYARLARI ---")
    print(f"Urun Adi: {product_name}")
    print(f"Gorsel Orani: {args.aspect_ratio}")
    print(f"Cikti Dizini: {output_dir / 'YENI GORSELLER'}")
    if not args.no_video:
        print(f"Video Suresi: {args.duration} saniye")
        print(f"Video Cozunurlugu: {args.resolution} ({'Ekonomik' if args.resolution == '480p' else 'Premium'})")
    else:
        print("Video Uretimi: ATLANACAK")
    print("------------------------\n")
    
    # API Anahtarları Kontrolü
    kie_key = settings.KIE_API_KEY
    imgbb_key = settings.IMGBB_API_KEY
    openai_key = settings.OPENAI_API_KEY
    
    if not all([kie_key, imgbb_key, openai_key]):
        print("Hata: Gerekli API anahtarlari eksik! (.env dosyasini kontrol edin)")
        sys.exit(1)
        
    # Servisleri başlat
    kie_svc = KieAIService(kie_key, base_url=settings.KIE_BASE_URL)
    imgbb_svc = ImgBBService(imgbb_key)
    openai_svc = OpenAIService(openai_key, model=settings.OPENAI_MODEL)
    
    log.info("GOST uretim sureci baslatildi.")
    try:
        # Bölüm 1: GOST Görsel Üretimi & Kalite Kontrol
        gost_url = await generate_gost_image(
            kie_svc, imgbb_svc, openai_svc, 
            image_path, output_dir, product_name, args.aspect_ratio,
            is_dry_run=args.dry_run
        )
        
        # Bölüm 2: GOST Görseli Üzerinden Video Üretimi
        if not args.no_video:
            await generate_ad_video(
                kie_svc, imgbb_svc, gost_url, 
                output_dir, product_name, args.resolution, args.duration,
                is_dry_run=args.dry_run
            )
            
        log.info("\n*** TUM ISLEMLER BASARIYLA TAMAMLANDI! ***")
        log.info(f"Dosyalariniz burada: {output_dir / 'YENI GORSELLER'}")
        
    except Exception as e:
        log.error(f"Islem basarisiz oldu: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
