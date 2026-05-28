# 📊 Maliyet Raporu Standardı

## Kural
Kullanıcı maliyet raporu istediğinde:
1. **Word belgesi (.docx)** formatında üret
2. **O anki projenin klasörüne** kaydet (örn. hlk-REKLAM, Projeler/XYZ vb.)
3. Dosya adı: `PROJE_ADI_Maliyet_Raporu.docx`

## Format
- Ana başlık: Proje adı + "Video Üretim Maliyet Raporu"
- Alt başlık: Tarih + proje adı
- **Tablo:** Video/açıklama | Üretilen içerik | Kullanılan kredi | Maliyet (USD)
- **Diğer servisler:** Bullet list (ElevenLabs, Replicate, vb.)
- **Genel Toplam:** Kırmızı, büyük, ortalı
- **Not:** Abonelik ücretleri dahil değil

## Skill Konumu
`_skills/maliyet-raporu/maliyet_raporu.py`

İçe aktarma:
```python
from _skills.maliyet-raporu.maliyet_raporu import maliyet_raporu_olustur
```

## Kayıt Klasörü Kuralı
| Proje | Kayıt Klasörü |
|-------|--------------|
| LARA ARI reklamları | `hlk-REKLAM\` |
| eCom Reklam Otomasyonu | `Projeler\eCom_Reklam_Otomasyonu\` |
| Diğer projeler | Projenin kendi klasörü |
