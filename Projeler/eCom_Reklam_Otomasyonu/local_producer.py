import os
import sys
import json
from dotenv import load_dotenv

# Path ayarı
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.imgbb_service import ImgBBService
from services.openai_service import OpenAIService
from services.perplexity_service import PerplexityService
from core.scenario_engine import ScenarioEngine
from logger import get_logger

log = get_logger("local_producer")

def main():
    log.info("Lokal Prodüktör başlatılıyor...")
    load_dotenv()

    # Ortam değişkenlerini al
    imgbb_key = os.environ.get("IMGBB_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    perplexity_key = os.environ.get("PERPLEXITY_API_KEY", "bypass")

    if not imgbb_key or not openai_key:
        log.error("Eksik API anahtarları! .env dosyasını kontrol edin.")
        return

    imgbb_service = ImgBBService(imgbb_key)
    openai_service = OpenAIService(openai_key)
    perplexity_service = PerplexityService(perplexity_key)
    scenario_engine = ScenarioEngine(openai_service, perplexity_service)

    # 1. Görselleri Bul
    base_dir = r"c:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk-REKLAM\lara_hlk_rklm.01"
    image_paths = [
        os.path.join(base_dir, "hlk_LARA025.01.JPG"),
        os.path.join(base_dir, "hlk_LARA025.02.JPG")
    ]

    image_urls = []
    # 2. Görselleri Yükle
    log.info("Fotoğraflar ImgBB'ye yükleniyor...")
    for path in image_paths:
        if os.path.exists(path):
            with open(path, "rb") as f:
                res = imgbb_service.upload_image_bytes(f.read(), os.path.basename(path))
                image_urls.append(res["url"])
                log.info(f"Yüklendi: {res['url']}")
        else:
            log.warning(f"Dosya bulunamadı: {path}")

    if not image_urls:
        log.error("Hiç görsel yüklenemedi, işlem durduruluyor.")
        return

    # 3. Collected Data'yı Hazırla (OpenAI Vision kullanarak ürün detayı çıkarabiliriz ama şimdilik manuel besleyelim)
    log.info("Ürün analizi ve senaryo üretimi yapılıyor...")
    
    collected_data = {
        "brand_name": "LARA ARI",
        "product_name": "LARA ARI Kadın Giyim Ürünü (LARA025)",
        "ad_concept": "Sosyal Medya Reklamı (UGC Tarzı, Doğal ve Samimi)",
        "product_description": "Fotoğraflardaki zarif ürün. Hedef kitle: Şıklığına önem veren, modern kadınlar.",
        "target_audience": "Şık, modern kadınlar",
        "best_image_urls": image_urls
    }

    # 4. Araştırma (Bypass edildi)
    research_data = scenario_engine.research(collected_data)

    # 5. Senaryo Üret
    preferences = {
        "video_style": "ugc",
        "video_format": "9:16",
        "custom_note": "Ürün bir kadın giyim/moda ürünü. Görselleri analiz ederek giysiyi detaylı tarif et ve senaryoyu moda/şık konsept üzerine kur."
    }
    
    scenario = scenario_engine.generate_scenario(collected_data, research_data, preferences)

    # Çıktıyı kaydet
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenario_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scenario, f, ensure_ascii=False, indent=2)

    log.info(f"Senaryo başarıyla oluşturuldu ve {output_path} konumuna kaydedildi.")
    
    print("\n--- SENARYO HAZIR ---")
    print(f"Başlık: {scenario.get('title')}")
    print(f"Dış Ses: {scenario.get('voiceover_text')}")
    print(f"Süre: {scenario.get('total_duration_seconds')} saniye")

if __name__ == "__main__":
    main()
