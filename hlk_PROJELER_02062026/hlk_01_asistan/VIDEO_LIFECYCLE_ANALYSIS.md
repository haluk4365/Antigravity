# SAHNE-2 KRİTİK HATA ANALİZİ

## ÖN BULGU: Prototip Hiç Aktif Olmamış

Log'da `"PROTOTIP"` kelimesi **0 (sıfır)** kez geçiyor.
Prototip bloğu (`start.py:294-326`) hiçbir zaman çalışmamış.

---

## HATA-1: İki HLK Akışı Paralele Çalışıyor

### Gerçek Zaman Çizelgesi (Log'dan: 14:17)

```
t=-3.000sn  dil seçti: tr
t= 0.000sn  sendVideo — ORİJİNAL hedra videosu (prototip DEĞİL!)
t= 1.000sn  sleep(1) başlar
t= 1.020sn  typewriter-1 başlar (22 kelime)
t=13.000sn  ✅ typewriter-1 tamam
t=13.000sn  sleep(1) başlar
t=14.000sn  typewriter-2 başlar (9 kelime)
t=20.000sn  ✅ typewriter-2 tamam
t=20.000sn  deleteMessage(video)
t=20.000sn  deleteMessage(hint)
t=20.000sn  ✅ Dil akışı tamamlandı: tr
```

### 1 Kaç Adet Sahne-2 Task Çalışıyor?

**2 adet** (üst üste çalışmış):

| # | Zaman | Olay |
|---|-------|------|
| 1 | 14:16:54 | sendVideo(Sahne-1) → kullanıcı TR seçti → sendVideo(Sahne-2) |
| 2 | 14:17:33 | sendVideo(Sahne-1) → kullanıcı TR seçti → sendVideo(Sahne-2) |

Her ikisi de **ORİJİNAL akış** (Prototip DEĞİL). Her akışta:
- 2× `sendVideo` (Sahne-1 + Sahne-2)
- 1× `sendMessage` (hint)
- 2× `typewriter_animation` (toplam ~31 editMessageText)
- 3× `deleteMessage` (video + hint + balon-1)
- 1× `_run_balloons()` task

Kullanıcı ekranda **2 ayrı Sahne-2 akışını üst üste görür.**

### 2 Kaç Adet sendVideo() Çağrısı Yapılıyor?

Her akışta **2 adet**: Sahne-1 (tanıtım) + Sahne-2 (hedra).
İki akış toplam = **4 adet sendVideo**.

### 3 Kaç Adet _run_balloons() Çalışıyor?

**2 adet.** Her akışta 1 kez.
Toplam: 2 × (22 + 9) = **62 adet editMessageText** çağrısı.

### 4 Prototip ve Orijinal Aynı Anda mı Aktif?

**HAYIR.** Prototip HİÇ aktif olmamış.

### Kök Neden: Prototip Dosya Yolu

```python
# start.py satır 295
proto_path = Path("PROJELER/SCENE2_BALLOON_PROTOTYPE/output/scene2_tr_prototype.mp4")
```

Bu **göreceli yol** (relative path). Bot başlatılırken:
- `bash` çalışıyor → CWD = `hlk_PROJELER_02062026/` (üst dizin)
- `PowerShell ProcessStart` çalışıyor → CWD = `HLK_01_asistan/`

`proto_path.exists()` **farklı CWD'lerde False dönebilir.**

Prototip bloğu çalışmadığı için kod **satır 327'ye** düşer:
```python
if scene2_path:   # ← bu her zaman True (orijinal hedra videosu)
```
Orijinal akış başlar: sendVideo(hedra) + hint + _run_balloons() + delete.

### Neden İki Akış?

Kullanıcı bir akış tamamlanmadan (`_run_balloons()` henüz bitmemişken) TEKRAR `/start` yapıp TR seçer. `context.user_data.clear()` ile state sıfırlanır. İkinci akış başlar. İlk akış hala arka planda çalışmaya devam eder.

**Sonuç:** Ekranda 2 ayrı SAHNE-2 akışı aynı anda görünür.

---

## HATA-2: HLK Son Cümlesini Tamamlamadan Video Siliniyor

### Gerçek Zaman Çizelgesi (ORİJİNAL akış — TR)

```
t= 0.000sn  sendVideo — orijinal hedra videosu BAŞLADI (12.880sn)
            AHU MP3 BAŞLADI (12.771sn)
t= 1.000sn  typewriter-1 BAŞLADI (sleep(1) bitti)
t= 1.020sn  boş balon ▌ göründü
t= 1.347sn  ilk kelime yazıldı
t= 8.655sn  Mesaj-1 son kelime (22 kelime × 0.3475sn)
t= 9.000sn  sleep(1) başladı
t=10.000sn  typewriter-2 BAŞLADI (9 kelime)
t=10.350sn  Mesaj-2 ilk kelime
^^^^^ BU ANDA VİDEO HALA OYNUYOR (12.880sn sürüyor)

t=12.771sn  AHU MP3 TAMAM — HLK konuşması bitti
t=12.880sn  VİDEO BİTTİ — son karede dondu
t=12.880sn  VİDEO BİTTİ AMA TYPWRITER-2 HALA ÇALIŞIYOR
t=13.000sn  Mesaj-2 son kelime yazıldı
t=13.000sn  HTML format (son düzenleme)
t=13.000sn  deleteMessage(video)
t=13.000sn  deleteMessage(hint)
```

### Kök Neden Analizi

**`_run_balloons()` → `deleteMessage` arasındaki zamanlama:**

1. Video 12.880sn'de biter
2. AHU MP3 12.771sn'de biter (0.109sn önce)
3. **Typewriter-2 (9 kelime) ~10sn'de başlar, ~13sn'de biter**
4. Video 12.880sn'de bittiğinde typewriter-2 hala 3.12sn daha devam ediyor!
5. Kullanıcı: video bitti → son kare → HLK metni hala yazılıyor → **HLK konuşması yarım kaldı hissi**
6. Typewriter-2 bitince deleteMessage anında çalışır

**Yanlış olan şey: `deleteMessage` typewriter-2 bitince çalışıyor, video bitince DEĞİL.**

```
VİDEO:   ████████████████████████░░░░░░░░░░░░░░░░   12.88sn'DE BİTTİ
MP3:     ██████████████████████░░░░░░░░░░░░░░░░░░░   12.77sn'DE BİTTİ
TYPEW-1:       ████████████████████░░░░░░░░░░░░░░░   8.66sn'DE BİTTİ
TYPEW-2:                              ████████████   10sn-13sn ÇALIŞIYOR
                                                    ❌ VİDEO 12.88sn'DE BİTTİ
                                                      TYPEWRITER 13sn'DE BİTTİ
                                                      0.12sn BOYUNCA STATİK KARE
```

**Normal akış:**
```
1. video biter → statik son kare (0.12sn)
2. typewriter-2 biter → deleteMessage
3. video kaybolur → link isteme state
```

**Kullanıcı deneyimi:**
```
HLK konuşuyor → video devam ediyor → AHU sesi bitti → 
video son karede HLK dudakları oynamıyor → 
yazı yazılmaya devam ediyor →
video siliniyor → "HLK yarım kaldı!"
```

### İkincil Neden: `deleteMessage` Zamanlaması

Şu anki kod:

```python
await _run_balloons()          # typewriter bitene kadar bekle (~13sn)
for msg in [sahne2_msg, ...]:  # sonra sil
    await delete_message(...)
```

Olması gereken:

```python
# Video bitince typewriter bitmese de sil
# Veya: typewriter'ı video süresine senkronize et
```

### Video Süresi vs Typewriter Süre Uyumsuzluğu

| Bileşen | TR | EN | DE | FR | ES | AR | RU | KR |
|---------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Video (sn)** | 12.880 | 13.208 | 14.041 | 18.208 | 17.875 | 17.208 | 16.375 | 10.176 |
| **Typewriter bitiş (sn)** | ~13.0 | ~13.2 | ~14.1 | ~18.3 | ~17.8 | ~17.2 | ~16.4 | ~10.2 |
| **Video bitiş vs Typewriter** | ≈eşit | ≈eşit | ≈eşit | ≈eşit | ≈eşit | ≈eşit | ≈eşit | ≈eşit |

*Typewriter süresi, MP3 süresine göre dinamik hesaplanır. Video süresi MP3'ten ~0.1sn uzundur.*

---

## KESİN KÖK NEDENLER

### HATA-1: İki HLK Akışı
```
Kök neden: `proto_path.exists()` farklı CWD'lerde False döner
              ↓
          Prototip bloğu çalışmaz
              ↓
          ORİJİNAL akış çalışır (typewriter + hint + delete)
              ↓
          Kullanıcı `/start` yapınca yeni akış başlar, eskisi ölmez
              ↓
          EKRANDA 2 AKIŞ AYNI ANDA GÖRÜNÜR
```

### HATA-2: Video Erken Siliniyor
```
Kök neden: `deleteMessage` typewriter-2 bittiğinde çalışır
           (video bittiğinde DEĞİL)
              ↓
          Video 12.88sn'de biter
          Typewriter-2 ~13sn'de biter
              ↓
          0.12sn boyunca video statik kare, typewriter hala yazıyor
              ↓
          "HLK konuşması yarım kaldı" hissi
```
