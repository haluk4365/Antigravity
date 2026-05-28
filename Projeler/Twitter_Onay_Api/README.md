# Twitter_Onay_Api

Twitter_Text_Paylasim'in ürettiği draft'lar için onay endpoint'i. Sabah gelen özet mailindeki "Onayla ve yayına al" butonuna tıklanınca bu servis tetiklenir: imzalı token doğrulanır → Typefully draft'ı bir sonraki boş slot'a (11/13/15:30 İstanbul) zamanlanır → Notion'da Status `Approved` olarak işaretlenir.

## Stack
Python 3 + FastAPI + Uvicorn. Tek dosya: `main.py`.

## Çalışma Şekli
HTTP servisi olarak Railway'de 7/24 ayakta. `GET /onay?token=...` çağrısı:
1. HMAC-SHA256 ile token imzasını doğrular (APP_SECRET).
2. Token payload'ından `draft_id` ve `notion_page_id` okur.
3. Typefully API'ye PATCH atar (`publish_at: next-free-slot`).
4. Notion sayfasının Status'ünü `Approved` yapar.
5. Kullanıcıya HTML cevap döner ("Yayına alındı" veya hata mesajı).

Kaynak: Twitter_Text_Paylasim cron'u sabah maili gönderirken her draft için imzalı token üretir; bu API o token'ı tüketir.

## Environment Setup
Ortam değişkenleri için `.env.example`'a bak. Doldurman gerekenler:
- `APPROVAL_SECRET` — Mail butonundaki token'ı imzalamak/doğrulamak için kullanılan ortak gizli anahtar (Twitter_Text_Paylasim ile aynı olmak zorunda)
- `TYPEFULLY_API_KEY` — Typefully Pro hesabının API key'i
- `TYPEFULLY_SOCIAL_SET_ID` — X hesabının Typefully social set ID'si
- `NOTION_SOCIAL_TOKEN` — Notion Internal Integration token'ı (sosyal DB'lere erişimli)

## Deploy
Railway'de `RAILPACK` builder, web servis (`uvicorn main:app --host 0.0.0.0 --port $PORT`). Healthcheck `/` endpoint'i. Auto-deploy: push deploy eder. Son güncelleme: 2026-05-07.
