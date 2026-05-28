# Project Card

| Alan | Değer |
|------|-------|
| **Platform** | Netlify / Vercel / Cloudflare Pages (statik export) |
| **Start Command** | `npm run dev` (lokal) |
| **Build Command** | `npm run build` |
| **Publish Dir** | `out` |

## Env Variables
Hepsi opsiyonel — `.env.example` dosyasına bakın. Statik/SSG mimari, kritik gizli
anahtar yok.

## Dosya Yapısı (kısa)
- `src/app/` → Sayfa routing (Next.js 15 App Router)
- `src/components/` → React Client Component'ları
- `src/i18n/locales/` → `tr.json`, `en.json`, `es.json`, `zh.json` (4 dil)
- `src/content/blog/` → MDX blog yazıları
- `public/` → Görsel ve medya dosyaları

## Mimari Kurallar
- Tüm görünen metin `i18n/locales/*.json` dosyalarından gelir. Metin değişikliği
  4 dile de yansıtılmalı (önce TR, sonra diğerleri).
- `output: 'export'` aktif — statik HTML üretir, sunucu gerektirmez.
