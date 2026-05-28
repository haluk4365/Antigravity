import os
import sys
import json
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.kie_api import KieAIService
from services.elevenlabs_service import ElevenLabsService
from services.replicate_service import ReplicateService
from services.notion_service import NotionService
from services.imgbb_service import ImgBBService
from core.production_pipeline import ProductionPipeline
from logger import get_logger

log = get_logger("local_renderer")

async def progress_callback(step: str, message: str):
    print(f"\n[PROGRESS: {step}] {message}")

async def main():
    log.info("Lokal Video Üretimi Başlatılıyor...")
    load_dotenv()

    # API Anahtarlarını Al
    kie_key = os.environ.get("KIE_API_KEY")
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    replicate_key = os.environ.get("REPLICATE_API_TOKEN")
    notion_token = os.environ.get("NOTION_SOCIAL_TOKEN")
    imgbb_key = os.environ.get("IMGBB_API_KEY")

    if not all([kie_key, elevenlabs_key, replicate_key, notion_token, imgbb_key]):
        log.error("Eksik API Anahtarları!")
        return

    # Servisleri Başlat
    kie_service = KieAIService(kie_key)
    elevenlabs_service = ElevenLabsService(elevenlabs_key)
    replicate_service = ReplicateService(replicate_key)
    notion_service = NotionService(notion_token, os.environ.get("NOTION_DB_ECOM_REKLAM"))
    imgbb_service = ImgBBService(imgbb_key)

    pipeline = ProductionPipeline(
        kie_service,
        elevenlabs_service,
        replicate_service,
        notion_service,
        imgbb_service,
        is_dry_run=False
    )

    # Senaryoyu Yükle
    scenario_path = os.path.join(os.path.dirname(__file__), "scenario_output.json")
    if not os.path.exists(scenario_path):
        log.error("Senaryo dosyası bulunamadı!")
        return

    with open(scenario_path, "r", encoding="utf-8") as f:
        scenario = json.load(f)

    # collected_data'yı yeniden yapılandır
    collected_data = {
        "brand_name": "LARA ARI",
        "product_name": "LARA ARI Furry Leg Warmers (Kürklü Bacak Isıtıcı)",
        "ad_concept": "Sosyal Medya UGC Reklamı (Y2K, Aesthetic Streetwear, Winter Fashion)",
        "best_image_urls": [
            "https://i.ibb.co/h1Jkn9hb/lara-furry-leg-warmers-png.png"
        ]
    }

    preferences = {
        "video_format": "9:16",
        "video_style": "ugc"
    }

    print("\n--- VİDEO ÜRETİMİ BAŞLIYOR ---")
    
    result = await pipeline.produce(
        scenario=scenario,
        collected_data=collected_data,
        progress_callback=progress_callback,
        user_name="LocalUser",
        preferences=preferences
    )

    print("\n--- VİDEO ÜRETİMİ TAMAMLANDI ---")
    if result["status"] == "success":
        print(f"Final Video URL: {result.get('video_url')}")
        print(f"Ses URL: {result.get('audio_url')}")
        print(f"Notion Log URL: {result.get('notion_page_url')}")
        
        # Dosyayı lokal diske kaydetme denemesi
        try:
            import requests
            import shutil
            import glob
            
            video_url = result.get('video_url')
            if video_url:
                print(f"Video indiriliyor... Lütfen bekleyin.")
                video_res = requests.get(video_url)
                video_res.raise_for_status()
                
                # Numaralandirma mantigi
                target_dir = r"c:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM"
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                    
                existing_files = glob.glob(os.path.join(target_dir, "FINAL_REKLAM_LARA_ARI_*.mp4"))
                next_num = 2
                if existing_files:
                    numbers = []
                    for f in existing_files:
                        try:
                            # FINAL_REKLAM_LARA_ARI_02.mp4 formatindan sayiyi al
                            num_str = os.path.basename(f).replace("FINAL_REKLAM_LARA_ARI_", "").replace(".mp4", "")
                            numbers.append(int(num_str))
                        except ValueError:
                            continue
                    if numbers:
                        next_num = max(numbers) + 1
                        
                new_filename = f"FINAL_REKLAM_LARA_ARI_{next_num:02d}.mp4"
                
                # Proje klasorune de kaydet
                local_output_path = os.path.join(os.path.dirname(__file__), new_filename)
                with open(local_output_path, "wb") as f:
                    f.write(video_res.content)
                print(f"Harika! Video proje dizinine kaydedildi: {local_output_path}")
                
                # Hedef klasore kopyala
                target_output_path = os.path.join(target_dir, new_filename)
                shutil.copy2(local_output_path, target_output_path)
                print(f"Harika! Video ayni zamanda hedeflenen REKLAM klasorune siralı olarak eklendi: {target_output_path}")
                
        except Exception as e:
            print(f"Video lokal olarak indirilirken hata oluştu: {e}")
            print("Ancak yukarıdaki linkten indirebilirsiniz.")
    else:
        print(f"HATA OLUŞTU: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
