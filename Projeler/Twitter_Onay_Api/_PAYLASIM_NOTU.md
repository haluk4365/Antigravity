# Paylaşım Notu — Twitter_Onay_Api

**Mod:** A (doğrudan ver)

## Ne yapıldı
- **Temizlenen sırlar:** Yok — `main.py` tüm anahtarları `os.environ` üzerinden okuyor, koda gömülü değer bulunmadı.
- **Scrub edilen kişisel veriler:** Yok — kişisel e-posta, isim, ID veya domain bulunmadı.
- Mevcut `.env.example` zaten placeholder'lı; olduğu gibi korundu.

## Öğrenci ne yapmalı
1. `.env.example` → `.env` kopyala ve doldur:
   - `APPROVAL_SECRET` — mail butonundaki imzalı token'ı doğrulayan ortak gizli anahtar (Twitter_Text_Paylasim ve Instagram_Carousel_Cron ile AYNI değer olmalı)
   - `TYPEFULLY_API_KEY`, `TYPEFULLY_SOCIAL_SET_ID`
   - `NOTION_SOCIAL_TOKEN`
2. `pip install -r requirements.txt` → Railway'de 7/24 web servisi olarak deploy et (`Procfile` mevcut).
3. Servis URL'sini Twitter_Text_Paylasim ve Instagram_Carousel_Cron'un `APPROVAL_BASE_URL` env değişkenine yaz.
