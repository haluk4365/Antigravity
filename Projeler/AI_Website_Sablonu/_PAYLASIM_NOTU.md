# Paylaşım Notu — AI Website Şablonu

## Mod
C — Şablona çevir

## Ne yapıldı

### Temizlenen sırlar
- Koda gömülü gizli anahtar bulunmadı (statik site, API anahtarı kullanmıyor).
- Affiliate/referral içeren URL'ler kaldırıldı: Udemy `referralCode`, Skool `?ref=...`
  linkleri opsiyonel env değişkenlerine çevrildi.

### Scrub edilen kişisel veriler
- Marka sahibi adı, soyadı ve kişisel domain → `[MARKA ADI]` / `[MARKA SAHİBİ ADI]` / env
- Tüm kişisel domain'li e-posta adresleri → `NEXT_PUBLIC_CONTACT_EMAIL` env
- Kişisel sosyal medya handle'ları (instagram/youtube/tiktok/x)
  → `[KULLANICI_HANDLE]` placeholder
- Ekip üyesi isimleri ve fotoğrafları (gerçek isimler + AI ajanlar)
  → `hakkimizda/page.tsx` jenerik `[EKİP ÜYESİ N]` listesine indirildi
- Gerçek kurumsal referans isimleri ve domainleri → i18n placeholder + `example.com`
- Tüm i18n locale dosyaları (tr/en/es/zh) → bütün metin `[KÖŞELİ PARANTEZ]` placeholder
- İstatistikler (250.000 takipçi, 100M izlenme, demografik veriler) → placeholder
- Kişisel fotoğraflar, marka logoları/SVG'leri, üretilmiş video/blog görselleri,
  og-image, mediakit banner → silindi (`public/` boşaltıldı, `public/images/README.md` eklendi)
- Blog içeriği (9 gerçek MDX yazısı) → silindi, yerine `ornek-yazi.mdx` şablonu kondu
- `STORAGE_KEY` (kişisel marka adı içeren değer) → jenerik `site_lang`

## Öğrenci ne yapmalı

1. `.env.example` → `.env.local` kopyalayın, 4 opsiyonel değişkeni doldurun:
   `NEXT_PUBLIC_SITE_URL`, `NEXT_PUBLIC_CONTACT_EMAIL`, `NEXT_PUBLIC_COMMUNITY_URL`,
   `NEXT_PUBLIC_TRAINING_URL`
2. `src/i18n/locales/tr.json` içindeki tüm `[...]` placeholder'ları kendi metinlerinizle
   doldurun, sonra `en.json` / `es.json` / `zh.json` dosyalarına da yansıtın
3. `public/images/` altına kendi görsellerinizi koyun: `logo.svg`, `portrait.webp`,
   hero görseli, ürün görselleri, ekip fotoğrafları, blog kapakları, `og-image.png`
4. `src/app/hakkimizda/page.tsx` → `teamMembers` dizisini kendi ekibinizle güncelleyin
5. `src/content/blog/ornek-yazi.mdx` → kopyalayıp kendi blog yazılarınızı yazın
6. Kod içinde `TODO:` yorumu olan satırları kontrol edip kendi içeriğinizle doldurun
7. `npm install && npm run dev` ile çalıştırın

## Mod C — Orijinal amaç → yeni jenerik çerçeve

**Orijinal:** Belirli bir kişinin kişisel marka sitesi — biyografi, ekip, gerçek
müşteri referansları, sosyal medya istatistikleri ve kendi blog içerikleriyle dolu
canlı bir production sitesi.

**Yeni çerçeve:** Herhangi bir kişisel marka, danışman veya ajansın kullanabileceği
boş bir Next.js 15 landing site iskeleti. Sayfa yapısı, animasyonlar, çok dilli
altyapı, blog sistemi ve media-kit bölümü korundu; tüm içerik açıkça işaretlenmiş
placeholder'a indirildi. Öğrenci kendi markasını doldurarak dakikalar içinde
yayına hazır bir site çıkarır.
