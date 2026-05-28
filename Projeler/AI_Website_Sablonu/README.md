# AI Website Şablonu — Kişisel Marka / Ajans Landing Site

Premium, çok sayfalı bir kişisel marka veya ajans web sitesi şablonu. Next.js 15
App Router üzerine kurulu, statik export ile herhangi bir CDN'e (Netlify, Vercel,
Cloudflare Pages) deploy edilebilir. Hero, ürün/çözüm vitrini, hizmetler, eğitimler,
marka iş birlikleri media kit, hakkımızda ve blog sayfalarını içerir. 4 dil desteği
(TR/EN/ES/ZH) hazır gelir.

Bu bir **şablondur**: tüm metin, görsel ve marka bilgileri placeholder olarak
işaretlenmiştir. Kendi içeriğinizi doldurarak kendi sitenizi üretirsiniz.

## Stack

| Katman | Teknoloji |
|---|---|
| Framework | Next.js 15 (App Router) + TypeScript |
| Styling | Tailwind CSS v4 |
| Animasyon | Framer Motion |
| İkonlar | Lucide React |
| Blog | MDX (`gray-matter` + `next-mdx-remote`) |

## Çalışma Şekli

`src/app/` altında her klasör bir sayfadır (App Router). Tüm görünen metinler
`src/i18n/locales/*.json` dosyalarından okunur — metin değiştirmek için bu JSON
dosyalarını düzenlersiniz. Blog yazıları `src/content/blog/` altındaki `.mdx`
dosyalarıdır. Görseller `public/images/` altına konur.

`next.config.ts` statik export modundadır (`output: 'export'`), yani `npm run build`
çıktısı `out/` klasörüdür ve herhangi bir statik hosting'e atılabilir.

## Kurulum

1. `npm install`
2. `.env.example` dosyasını `.env.local` olarak kopyalayın ve değerleri doldurun
3. `src/i18n/locales/tr.json` içindeki `[KÖŞELİ PARANTEZ]` placeholder'larını kendi
   metinlerinizle değiştirin, sonra en/es/zh dosyalarına da yansıtın
4. `public/images/` altına logo, hero, ürün, ekip ve blog görsellerinizi koyun
5. `src/content/blog/ornek-yazi.mdx` dosyasını kopyalayıp kendi blog yazılarınızı yazın
6. Kod içinde `TODO:` yorumu olan yerleri kendi linkleriniz/içeriğinizle güncelleyin
7. `npm run dev` ile lokal önizleyin, `npm run build` ile statik çıktı alın

## Environment Setup

`.env.local` değişkenleri (hepsi opsiyonel — boş bırakılırsa varsayılan kullanılır):

- `NEXT_PUBLIC_SITE_URL` — sitenizin tam adresi (SEO, sitemap, OG için)
- `NEXT_PUBLIC_CONTACT_EMAIL` — iletişim/CTA e-posta adresi
- `NEXT_PUBLIC_COMMUNITY_URL` — varsa topluluk linki (Skool, Discord vb.)
- `NEXT_PUBLIC_TRAINING_URL` — varsa eğitim/kurs linki

## Deploy

`npm run build` → `out/` klasörü oluşur. Bu klasörü Netlify/Vercel/Cloudflare
Pages'e yükleyin. `netlify.toml` hazır gelir (build command + güvenlik header'ları).
Build command `npm run build`, publish dizini `out`.
