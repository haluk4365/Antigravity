# 🚀 Antigravity — AI Agent Talimatları

Bu dosya, Antigravity projesiyle çalışan AI agent'ın her konuşmada bilmesi gereken temel kuralları içerir.

---

## 🔐 Google OAuth — Merkezi Token Sistemi

**Google API erişimi (Gmail, Drive, Sheets) için asla yeni token oluşturma, terminal URL yapıştırma veya tarayıcı açma!**

Tokenlar zaten merkezi depoda mevcut ve otomatik yenileniyor:

```
_knowledge/credentials/oauth/
├── google_auth.py              ← Bu modülü import et
└── gmail-token.json            ← [GMAIL_ADRESINIZ]
```

### Kullanım
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.expanduser("~/Desktop/Antigravity"), "_knowledge/credentials/oauth"))
from google_auth import get_gmail_service, get_sheets_service, get_drive_service

# Ana hesap
gmail = get_gmail_service("outreach")
sheets = get_sheets_service("outreach")
drive = get_drive_service("outreach")
```

### Kurallar
1. **Yeni token oluşturma** — mevcut tokenlar `refresh_token` ile sonsuza kadar yenilenir
2. **Token dosyasını kopyalama veya taşıma** — merkezi depodaki dosyalar kullanılır
3. **Kullanıcıdan terminal etkileşimi isteme** — token yenileme otomatik
4. Sadece token tamamen bozulduysa: `cd _knowledge/credentials/oauth && python3 auth_helper.py status`

---

## 🔑 API Anahtarları — Merkezi .env Deposu

Tüm API anahtarları tek dosyada: `_knowledge/credentials/master.env`

Projelere bağlamak için `_skills/sifre-yonetici/` skill'ini kullan (detaylar `SKILL.md`'de).

---

## 🚀 Otonom Çalışma ve Terminal Kullanımı (ÇOK ÖNEMLİ)

**Sen (Antigravity), tam otonom bir AI asistansın. Kullanıcıdan manuel işlem yapmasını İSTEMEMELİSİN.**

1. **Terminal Komutları:** Bir terminal komutu çalıştırılması gerekiyorsa (bağımlılık yükleme, git komutları, dosya taşıma, script çalıştırma), kullanıcıya "Lütfen terminale gidip şu komutu yapıştırın" DEME. Bunun yerine `run_command` tool'unu kullanarak komutu bizzat ÇALIŞTIR. Kullanıcı çıkan pencereden sadece onaylayacaktır. Seçebiliyorsan 'SafeToAutoRun' argümanını gerektiği yerde kullanarak işlemleri hızlandır.
2. **GitHub İşlemleri:** GitHub commit, push, PR açma, branch oluşturma gibi işlemler için KESİNLİKLE GitHub MCP server tool'larını (`mcp_github-mcp-server_*`) veya terminal üzerinden `git` komutlarını (`run_command` ile) kullan. Kullanıcıdan GitHub'ta manuel işlem yapmasını ASLA isteme.
3. **Railway Deployments:** Railway ile ilgili bir işlem (deploy, ortam değişkeni ekleme/güncelleme) yapman gerekiyorsa, `master.env` dosyasındaki `RAILWAY_TOKEN` bilgisini `RAILWAY_TOKEN=... railway ...` şeklinde kullanarak `run_command` üzerinden bizzat çalıştır.
4. **Dosya Değişiklikleri:** Olası tüm dosya okuma/yazma/düzenleme işlemlerini doğrudan tool'ları kullanarak (örn: `replace_file_content`, `write_to_file`) gerçekleştir.

Kısacası: **Elindeki yetkileri (Tool'ları, MCP'yi ve Terminali) kullan, kullanıcıdan senin yerine klavye/fare kullanmasını isteme.**

---

## 📁 Proje Yapısı

```
Antigravity/
├── _agents/          ← Orkestrasyon agent'ları + workflow'lar
├── _skills/          ← Atomik beceriler (lead bulma, mail atma, video üretimi vb.)
├── _knowledge/       ← Merkezi bilgi bankası + credentials deposu
└── Projeler/         ← Aktif projeler
```

---

## 📋 Sık Kullanılan Workflow'lar

| Komut | İşlev |
|-------|-------|
| `/mail-gonder` | Lead listesine mail gönder |
| `/lead-toplama` | Hedef profil ve e-posta listesi oluştur |
| `/marka-outreach` | Marka iş birliği outreach pipeline'ı |
| `/fatura-kes` | Invoice üret |
| `/durum-kontrol` | Railway servislerinin sağlık durumu |
| `/yedekle` | Manuel yedekleme |
| `/sifre-bagla` | Projeye token/API anahtarı bağla |

---

## 🎬 Video Üretim Kuralları (eCom Reklam / Kie AI)

### 🔑 KURAL: Her Yeni Video Projesine Başlamadan Önce Anchor Frame Oluştur

**Her yeni video projesinde, üretim başlamadan önce MUTLAKA şu adımları uygula:**

#### Adım 1 — Manken + Ürün Anchor Görseli Üret
```python
# Kie AI Nano Banana 2 ile karakter + ürün kompozit görseli üret
anchor_url = await kie.async_create_character_with_product(
    character_prompt="Young Turkish woman, early 20s, ...",
    product_image_url=product_imgbb_url,
    aspect_ratio="9:16"
)
```

#### Adım 2 — Bu Anchor'u first_frame_url Olarak Kullan
```python
task_id = await asyncio.to_thread(
    kie.create_video,
    prompt=SCENE_PROMPT,
    first_frame_url=anchor_url,   # ← ZORUNLU
    duration=6,
    aspect_ratio="9:16",
    # reference_images ve first_frame_url aynı anda KULLANILMAZ
)
```

#### Adım 3 — Ses Ekle (Replicate LatentSync)
```python
final_url = await replicate.async_latentsync(
    video_url=raw_video_url,
    audio_url=audio_url
)
```

### ⚠️ Neden?
- `reference_images` yöntemi her seferinde farklı yüz/görünüm üretir
- `first_frame_url` yöntemi ilk kareyi sabitler → tüm video boyunca tutarlı görünüm
- Anchor görseli bir kere üretilip sonraki sahnelerde de kullanılabilir (zaman + kredi tasarrufu)

### 💡 Kullanıcıya Her Proje Başında Şunu Sor:
> "Bu proje için daha önce üretilmiş bir anchor (manken + ürün) görseli var mı?
> Varsa yolunu ver, yoksa şimdi üretelim."

### 🗂️ Anchor Görseli Kaydetme Konumu
```
hlk-REKLAM/<PROJE_ADI>/
├── anchor_<MANKEN>_<URUN>.jpg   ← Üretilen anchor görseli burada saklanır
├── lara.jpeg                     ← Orijinal manken referansları
└── BRASIL-CROPTOP-*.jpg          ← Ürün referansı
```

---

## 💰 Bütçe ve Ekonomik Çalışma Kuralları (ZORUNLU KURAL)

Kullanıcıdan gelen her yeni komut/revizyon isteğinde en ekonomik yöntemi belirle ve **işe başlamadan önce seçenekleri bütçeleri (kredi/maliyet) ile birlikte kullanıcıya sunup onay al.**

### 1. Dış Ses / Dudak Senkronizasyonu Revizyonları (Sıfır Kredi Kuralı)
- Eğer sadece seslendirme metni, tonlama, ses hızı veya sesin başındaki duraklama (break time) değişiyorsa, **asla Kie AI ile videoyu baştan render etme (0 kredi harca).**
- Bunun yerine, zaten üretilmiş olan sessiz ham videoyu (`raw_video_url` veya lokal yedek) kullanarak yalnızca ElevenLabs ile yeni sesi üret ve Replicate (LatentSync) ile sesi videoya yeniden giydir.

### 2. Yeni Video Çözünürlüğü ve Süre Seçenekleri
- Yeni bir video render edilmeden önce kullanıcıya bütçe seçeneklerini sun:
  - **Seçenek A (Premium):** 720p Çözünürlük (Saniye başına 25 Kredi)
  - **Seçenek B (Ekonomik):** 480p Çözünürlük (Saniye başına 11.5 Kredi)
  - **Süre Optimizasyonu:** Dış ses süresine göre video uzunluğunu (örneğin 6sn yerine 4sn) optimize etmeyi teklif et.
