# VIDEO DELETE TIMER — Kök Neden Analizi

## 1. Sorun Tanımı

**Son MP3-daktilo senkronizasyon düzeltmesinden sonra:** Daktilo artık AHU MP3 süresine göre dinamik hesaplanıyor ve MP3 ile aynı anda bitiyor. Ancak **video silme zamanlayıcısı hala eski sabit değerleri kullandığı** için video, AHU konuşması tamamlanmadan siliniyor.

---

## 2. Delete Timer Kod Analizi

**Dosya:** `handlers/start.py`

### 2.1 Zamanlayıcı Değişkeni — Satır 288

```python
sahne2_sure = SAHNE2_SURE_LANG.get(language.upper(), SAHNE2_SURE)
```

`sahne2_sure` değişkeni, `SAHNE2_SURE_LANG` sözlüğünden alınır.

### 2.2 SAHNE2_SURE_LANG Tanımı — Satır 48-51

```python
SAHNE2_SURE_LANG = {
    "TR": 13, "EN": 13, "DE": 14, "FR": 18,
    "ES": 18, "RU": 16, "AR": 17, "KR": 10,
}
```

**Bu değerler video dosyalarının ilk oluşturulduğu dönemdeki sürelere göre elle girilmiş sabitlerdir.** O tarihten sonra video/MP3 dosyaları değişmiş ama bu değerler güncellenmemiştir.

### 2.3 Delete Timer Kullanımı — Satır 314-322

```python
# Sahne-2 silme zamanlayıcısı — video ile EŞ ZAMANLI başlar (AR-002_39)
async def _delete_sahne2():
    await asyncio.sleep(sahne2_sure)              # ← sabit SAHNE2_SURE_LANG
    for msg in [sahne2_msg, hint_msg]:
        if msg:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            except Exception as e:
                logger.warning(f"⚠️ Mesaj silinemedi: {e}")

asyncio.create_task(_delete_sahne2())              # t=0'da başlar
```

### 2.4 Daktilo Dinamik Hız Hesabı — Satır 326-358

```python
mp3_dur = _get_mp3_duration(language)             # ← ffprobe ile ölçülen MP3 süresi
available_time = mp3_dur - 2.0
dynamic_delay = available_time / total_words       # ← MP3 süresine göre
```

---

## 3. Sorulara Cevaplar

### S1: Video delete timer hangi değişkene göre hesaplanıyor?

**`sahne2_sure` değişkenine göre.** Bu değişken `handlers/start.py` satır 288'de `SAHNE2_SURE_LANG` sözlüğünden alınır:

```python
sahne2_sure = SAHNE2_SURE_LANG.get(language.upper(), SAHNE2_SURE)
```

### S2: Video delete timer MP3 süresini mi kullanıyor?

**HAYIR.** MP3 süresi (`_get_mp3_duration()`) yalnızca daktilo hızını hesaplamak için kullanılır. Delete timer bu değeri **hiç okumaz, kullanmaz, referans almaz.**

### S3: Video delete timer SAHNE2_SURE_LANG değerini mi kullanıyor?

**EVET.** `sahne2_sure` = `SAHNE2_SURE_LANG[lang]`. Bu sabit değerdir, gerçek video/MP3 süreleriyle ilgisi yoktur.

### S4: Video delete timer sabit süre mi kullanıyor?

**EVET.** `SAHNE2_SURE_LANG` elle girilmiş sabit bir sözlüktür. Hiçbir dinamik hesaplama içermez. ffprobe veya başka bir ölçüm aracı burada kullanılmaz.

### S5: Video neden AHU konuşması tamamlanmadan siliniyor?

**Delete timer süresi (`SAHNE2_SURE`) daktilo/MP3 süresinden daha kısa olduğu için.** Daktilo artık MP3 süresine göre dinamik hesaplanıyor ve MP3 ile aynı anda bitiyor (~t=10-18sn). Ancak delete timer hala eski sabit `SAHNE2_SURE` değerlerini kullanıyor ve **6 dilde bu değer MP3 süresinden kısa.**

### S6: AR-002_39 kuralına göre Scene Complete oluşmadan video siliniyor mu?

**EVET.** AR-002_39 kuralı:
> "HLK aşağıdaki koşullar birlikte gerçekleşmeden sahneyi tamamlanmış kabul edemez:
> • AHU sesi tamamlandı.
> • Daktilo efekti tamamlandı.
> • Konuşma balonu tamamlandı."

Delete timer bu koşulların **hiçbirini kontrol etmez.** Sadece `asyncio.sleep(sabit_süre)` yapar. Bu nedenle AHU sesi ve daktilo tamamlanmadan video silinir.

---

## 4. Dil Bazında Zaman Çizelgesi

### ✅ TR — Tek sorunsuz dil (SAHNE2_SURE=13 >= MP3=12.771)

```
t=0.000  Video+MP3 BAŞLADI | _delete_sahne2(sleep=13) BAŞLADI
t=1.000  Daktilo BAŞLADI
t=12.771 AHU MP3 TAMAM
t=12.772 Daktilo TAMAM
t=12.880 Video bitti
t=13.000 ✅ delete_message — TÜM BİLEŞENLER TAMAM
```

### ❌ EN — Delete timer 0.189sn erken (SAHNE2_SURE=13 < MP3=13.189)

```
t=0.000  Video+MP3 BAŞLADI | _delete_sahne2(sleep=13) BAŞLADI
t=1.000  Daktilo BAŞLADI
t=13.000 ❌ delete_message — AHU HALA KONUŞUYOR! (0.189sn kaldı)
t=13.189 AHU MP3 TAMAM
t=13.189 Daktilo TAMAM
```

### ❌ DE — Delete timer 0.071sn erken (SAHNE2_SURE=14 < MP3=14.071)

```
t=0.000  Video+MP3 BAŞLADI | _delete_sahne2(sleep=14) BAŞLADI
t=14.000 ❌ delete_message — AHU HALA KONUŞUYOR! (0.071sn kaldı)
t=14.071 AHU MP3 TAMAM
t=14.072 Daktilo TAMAM
```

### ❌ FR — Delete timer 0.251sn erken (SAHNE2_SURE=18 < MP3=18.251)

```
t=0.000  Video+MP3 BAŞLADI | _delete_sahne2(sleep=18) BAŞLADI
t=18.000 ❌ delete_message — AHU HALA KONUŞUYOR! (0.251sn kaldı)
t=18.208 Video bitti
t=18.249 Daktilo TAMAM
t=18.251 AHU MP3 TAMAM
```

### ✅ ES — Sorunsuz (SAHNE2_SURE=18 >= MP3=17.786)

```
t=0.000  Video+MP3 BAŞLADI | _delete_sahne2(sleep=18) BAŞLADI
t=17.785 Daktilo TAMAM
t=17.786 AHU MP3 TAMAM
t=17.875 Video bitti
t=18.000 ✅ delete_message — TÜM BİLEŞENLER TAMAM
```

### ❌ AR — Delete timer 0.229sn erken (SAHNE2_SURE=17 < MP3=17.229)

```
t=0.000  Video+MP3 BAŞLADI | _delete_sahne2(sleep=17) BAŞLADI
t=17.000 ❌ delete_message — AHU HALA KONUŞUYOR! (0.229sn kaldı)
t=17.208 Video bitti
t=17.229 AHU MP3 TAMAM
t=17.230 Daktilo TAMAM
```

### ❌ RU — Delete timer 0.347sn erken (SAHNE2_SURE=16 < MP3=16.347)

```
t=0.000  Video+MP3 BAŞLADI | _delete_sahne2(sleep=16) BAŞLADI
t=16.000 ❌ delete_message — AHU HALA KONUŞUYOR! (0.347sn kaldı)
t=16.347 AHU MP3 TAMAM
t=16.348 Daktilo TAMAM
t=16.375 Video bitti
```

### ❌ KR — Delete timer 0.170sn erken (SAHNE2_SURE=10 < MP3=10.170)

```
t=0.000  Video+MP3 BAŞLADI | _delete_sahne2(sleep=10) BAŞLADI
t=10.000 ❌ delete_message — AHU HALA KONUŞUYOR! (0.170sn kaldı)
t=10.170 AHU MP3 TAMAM
t=10.171 Daktilo TAMAM
t=10.176 Video bitti
```

---

## 5. ÖZET TABLO — Delete Timer vs Tüm Bileşenler

| Dil | DeleteTimer | Video | MP3 | Daktilo | Timer-Video | Timer-MP3 | Timer-Daktilo | Durum |
|-----|------------|-------|-----|---------|------------|----------|--------------|-------|
| TR | **13** | 12.880 | 12.771 | 12.772 | **+0.120** | **+0.229** | **+0.228** | ✅ |
| EN | **13** | 13.208 | 13.189 | 13.189 | **-0.208** | **-0.189** | **-0.189** | ❌ |
| DE | **14** | 14.041 | 14.071 | 14.072 | **-0.041** | **-0.071** | **-0.072** | ❌ |
| FR | **18** | 18.208 | 18.251 | 18.249 | **-0.208** | **-0.251** | **-0.249** | ❌ |
| ES | **18** | 17.875 | 17.786 | 17.785 | **+0.125** | **+0.214** | **+0.215** | ✅ |
| AR | **17** | 17.208 | 17.229 | 17.230 | **-0.208** | **-0.229** | **-0.230** | ❌ |
| RU | **16** | 16.375 | 16.347 | 16.348 | **-0.375** | **-0.347** | **-0.348** | ❌ |
| KR | **10** | 10.176 | 10.170 | 10.171 | **-0.176** | **-0.170** | **-0.171** | ❌ |

**6/8 dilde delete timer tüm bileşenlerden önce tetikleniyor.** En büyük fark RU'da (-0.348sn).

---

## 6. Kök Neden

```
_GET_MP3_DURATION()                   SAHNE2_SURE_LANG
      │                                      │
      ▼                                      ▼
  MP3=16.347sn                          KOD=16sn (sabit)
      │                                      │
      │                                      ▼
      │                              _DELETE_SAHNE2()
      │                              asyncio.sleep(16)
      │                                      │
      ▼                                      ▼
  DAKTİLO=16.348sn                     t=16sn delete tetiklenir
  (MP3 ile eş)                              │
      │                                      ▼
      ▼                                 ❌ AHU KONUŞMASI
  t=16.347 AHU TAMAM                    YARIDA KALIR
```

**İki farklı zaman kaynağı kullanılıyor:**
1. **Daktilo** → `_get_mp3_duration()` = ffprobe ile ölçülen **gerçek MP3 süresi** (dinamik, doğru)
2. **Delete timer** → `SAHNE2_SURE_LANG[lang]` = elle girilmiş **sabit değer** (statik, güncel değil)

**Düzeltme:** `asyncio.sleep(sahne2_sure)` yerine `asyncio.sleep(mp3_dur)` kullanılmalı. Veya daha doğrusu, delete timer `SAHNE2_SURE` yerine `_get_mp3_duration()` ile ölçülen gerçek MP3 süresini kullanmalı. Böylece delete timer, daktilo ve AHU MP3 ile aynı anda (t=MP3_süresi) tetiklenir.
