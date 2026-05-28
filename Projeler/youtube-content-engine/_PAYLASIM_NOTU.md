# Paylasim Notu — youtube-content-engine

## Mod
A — Dogrudan ver.

## Ne yapildi
- Standalone repo `.git/` klasoru ve `node_modules/` KOPYALANMADI.
- Gercek `.env` dosyasi kopyalanmadi (sadece `.env.example`).
- Kisisel veri scrub'lari:
  - `.env.example` — `RESEND_FROM` / `RESEND_TO` kisisel e-postalari → `<EMAIL>`; tum anahtarlar `<...>` placeholder formatina cevrildi
  - `src/mail/send.ts` — kisisel kurumsal ve gmail e-posta default'lari → `radar@example.com` / `admin@example.com`
  - `src/ideas/ideas.ts` — LLM prompt'undaki "Dolunay Özeren" + "AI Factory" referanslari jeneriklestirildi
  - `src/radar/discovery.ts` — relevance filtre prompt'undaki kisisel isim jeneriklestirildi
  - `README.md` — kisisel e-posta default'lari aciklamadan temizlendi
- `src/radar/channels.ts` (`TRACKED_HANDLES`) ve `src/radar/topics.ts` (`TRACKED_TOPICS`) — public YouTube kanal handle'lari ve jenerik konu kelimeleri; ornek varsayilan olarak birakildi (kisisel veri degil).

## Ogrenci ne yapmali
1. `npm install` ile bagimliliklari kurun.
2. `.env.example` → `.env` kopyalayip doldurun:
   - `YOUTUBE_API_KEY` — YouTube Data API v3 anahtari
   - `ANTHROPIC_API_KEY` — Claude API anahtari
   - `NOTION_API_KEY`, `NOTION_RADAR_DB_ID`, `NOTION_IDEA_DB_ID` — Notion entegrasyonu
   - `RESEND_API_KEY`, `RESEND_FROM`, `RESEND_TO` — mail gonderimi
3. Isterseniz `src/radar/channels.ts` ve `topics.ts` icindeki takip listesini kendi nisinize gore degistirin.
