# 🤖 E-posta Asistanı

Her gün saat **12:00**'da otomatik olarak Gmail'i kontrol eden, gereksiz mailleri temizleyen ve önemli maillere taslak yanıt hazırlayan Python tabanlı e-posta asistanı.

---

## 📁 Proje Yapısı

```
e-posta-asistani/
├── main.py              ← Ana script (asistanın kendisi)
├── run.bat              ← İlk kurulum ve test için çalıştır
├── setup_task.bat       ← Windows Görev Zamanlayıcısı kurulumu
├── requirements.txt     ← Python bağımlılıkları
├── .env                 ← API anahtarları
├── credentials.json     ← [SİZİN İNDİRMENİZ GEREKECEK]
├── token.json           ← [Otomatik oluşur - ilk oturum sonrası]
└── logs/                ← Günlük çalışma logları
```

---

## 🚀 Kurulum Adımları

### Adım 1 — Google Cloud Credentials Oluşturma

1. [Google Cloud Console](https://console.cloud.google.com/) adresine gidin
2. Yeni bir proje oluşturun (veya mevcut birini seçin)
3. Sol menüden **"APIs & Services" → "Enable APIs and Services"** seçin
4. **"Gmail API"** arayın ve etkinleştirin
5. Sol menüden **"Credentials"** → **"Create Credentials"** → **"OAuth 2.0 Client IDs"** seçin
6. Uygulama türü: **"Desktop app"** seçin
7. **"Download JSON"** butonuna tıklayın
8. İndirilen dosyayı bu klasöre kopyalayın ve adını **`credentials.json`** yapın

> ⚠️ **ÖNEMLI:** Bu dosyayı GitHub'a veya başka bir yere yüklemeyin!

---

### Adım 2 — İlk Kurulum ve Test

1. `run.bat` dosyasına **çift tıklayın**
2. Tarayıcınızda Google oturum açma sayfası açılacak
3. Gmail hesabınızla giriş yapın ve izin verin
4. Asistan çalışmaya başlayacak ve `logs/` klasörüne log yazacak

---

### Adım 3 — Otomatik Zamanlama Kurulumu

1. `setup_task.bat` dosyasına **sağ tıklayın → "Yönetici olarak çalıştır"**
2. Görev Zamanlayıcısı'na otomatik olarak eklenecek
3. Her gün saat **12:00**'da arka planda sessizce çalışacak

---

## ⚙️ Nasıl Çalışır?

```
12:00 → Gmail'e bağlan
      ↓
   Son 24 saatin okunmamış maillerini getir
      ↓
   Her mail için GPT-4o-mini ile analiz yap
      ↓
   ┌─────────────────┬─────────────────────────────┐
   │ Kategori A      │ Kategori B                  │
   │ (Gereksiz)      │ (Önemli / Yanıt Gerektiren) │
   ├─────────────────┼─────────────────────────────┤
   │ • Okundu işaret │ • GPT ile taslak yanıt yaz  │
   │ • Gereksizler_AI│ • Gmail'de Taslak olarak    │
   │   etiketine taşı│   kaydet (göndermez!)       │
   └─────────────────┴─────────────────────────────┘
```

---

## 📬 Sonuçları Nerede Görürüm?

| Kontrol Yeri | Açıklama |
|---|---|
| Gmail → **Gereksizler_AI** etiketi | Otomatik arşivlenen gereksiz mailler |
| Gmail → **Taslaklar (Drafts)** | Hazır ama gönderilmemiş yanıtlar |
| `logs/` klasörü | Her çalışmanın detaylı logu |

---

## 🛠 Sorun Giderme

| Sorun | Çözüm |
|---|---|
| `credentials.json bulunamadı` | Adım 1'i takip edin |
| `token.json geçersiz` | `token.json` dosyasını silin, `run.bat` ile yeniden çalıştırın |
| `OpenAI hatası` | `.env` dosyasındaki `OPENAI_API_KEY` değerini kontrol edin |
| Görev zamanlayıcı çalışmıyor | `setup_task.bat`'ı "Yönetici olarak çalıştır" ile açın |
