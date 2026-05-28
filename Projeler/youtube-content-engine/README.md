# youtube-content-engine

YouTube içerik radarı: takip edilen kanallardan ve belirlenen konulardan (topic search) yeni videoları çeker, "fresh / matured / discovery" bucket'lara ayırır, Claude ile fikir üretir ve günlük HTML özet mailini gönderir. Amaç: yeni video üretmeden önce hangi konuların yükselişte olduğunu görmek + ham fikirler için ilk taslak.

## Stack
Node.js 20 + TypeScript. Anthropic SDK (Claude), Notion SDK (radar + idea store), Resend (mail). YouTube Data API.

## Çalışma Şekli
Railway cron (`cronSchedule: 30 7 * * *` = 07:30 UTC). Akış (`src/index.ts`):
1. Paralel olarak kanal videoları (`radar/channels.ts`), topic videoları (`radar/topics.ts`), Notion'dan önceki gönderilmiş ID'ler ve son 30 fikrin hash'leri çekilir.
2. Discovery videoları (takip edilmeyen kanallardan trending) eklenir.
3. `bucketize()` fresh / matured / discovery'e ayırır; Notion'a göre dedup.
4. `runIdeaEngine()` Claude ile yeni fikir taslakları üretir (hash'lenip Notion'a kaydedilir).
5. `buildHtml() + sendMail()` Resend üzerinden günlük özet maili atar (`RESEND_TO`).

Hata olursa `sendFailureMail` ile kullanıcıya tek satırlık fail bildirimi düşer.

## Environment Setup
Ortam değişkenleri için `.env.example`'a bak. Doldurman gerekenler:
- `YOUTUBE_API_KEY` — YouTube Data API v3 key (kanal + arama için)
- `ANTHROPIC_API_KEY` — Claude (idea engine)
- `NOTION_API_KEY` — Notion Internal Integration token
- `NOTION_RADAR_DB_ID` — Daha önce gönderilen videoların loglandığı DB
- `NOTION_IDEA_DB_ID` — Üretilen fikirlerin (hash dedup) DB'si
- `RESEND_API_KEY` — Mail gönderim
- `RESEND_FROM` — Gönderen e-posta adresi
- `RESEND_TO` — Özet mailinin gideceği alıcı adresi
- `TZ` — `Europe/Istanbul`

## Deploy
Railway, `RAILPACK` builder, `npm run daily` start command. Cron `30 7 * * *`. `restartPolicyType: NEVER` (cron job — tekrar çalıştırma yok). Son güncelleme: 2026-05-07.
