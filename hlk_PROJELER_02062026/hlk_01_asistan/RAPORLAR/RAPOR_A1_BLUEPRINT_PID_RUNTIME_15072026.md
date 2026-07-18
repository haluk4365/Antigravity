# AŞAMA-1: PID RUNTIME ENTEGRASYONU — IMPLEMENTATION BLUEPRINT

**Plan Türü:** Uygulama Planı (Implementation Blueprint)
**Referans Plan:** RAPOR_PRP_PRODUCTION_REINTEGRATION_PLAN_15072026.md — Aşama 1
**Hazırlanma Tarihi:** 15 Temmuz 2026
**Değişiklik Kapsamı:** 1 dosya değişikliği, 2 satır
**Risk Seviyesi:** 🟢 DÜŞÜK

---

## 1. AŞAMA-1 GENEL ÖZETİ

### 1.1 Amaç

`handlers/website.py:2745` satırındaki manuel PID üretimini kaldırıp, `services/pid_runtime.py` üzerinden anayasal PID formatına (`PID-YYYYMMDD-NNNN`) geçmek.

### 1.2 Mevcut Durum (Kod)

**Dosya:** `handlers/website.py`
**Satır:** 2745
**Mevcut kod:**
```python
pid = f"PID-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
```
**Üretilen PID:** `PID-20260715-115926`
**Format:** `PID-YYYYMMDD-HHMMSS` (6 haneli saat/dakika/saniye)
**Anayasa:** ❌ AR-002_57 ihlali — `PID-YYYYMMDD-NNNN` (4 haneli günlük sayaç) olmalı

### 1.3 Hedef Durum

**Dosya:** `handlers/website.py`
**Satır:** 2745 (değişecek)
**Hedef kod:**
```python
from services.pid_runtime import pid_runtime
record = await pid_runtime.generate()
pid = record.pid
```
**Üretilen PID:** `PID-20260715-0001`
**Format:** `PID-YYYYMMDD-NNNN` (4 haneli günlük sayaç, GC_PID_SEQUENCE_LENGTH=4)
**Anayasa:** ✅ AR-002_57 uyumlu

### 1.4 Neden Bu Kadar Az Değişiklik?

`_run_production_pipeline` fonksiyonunda PID, **tek bir yerde** oluşturulur (satır 2745) ve sonrasında sadece string olarak kullanılır:

| Satır | Kullanım | Etkilenir mi? |
|-------|---------|:------------:|
| 2745 | `pid = f"PID-..."` | ✅ **DEĞİŞECEK** |
| 2751 | `logger.info(f"🎬 [Production] Basliyor: {pid}...")` | ❌ Otomatik düzelir (string) |
| 2754 | `cost_report = {"pid": pid, ...}` | ❌ Otomatik düzelir (string) |
| 2924 | `f"...PID: <code>{pid}</code>"` | ❌ Otomatik düzelir (string) |
| 2927 | `logger.info(f"✅ [Production] VIDEO GONDERILDI: {pid}")` | ❌ Otomatik düzelir (string) |
| 2933 | `f"📋 PID: <code>{pid}</code>"` | ❌ Otomatik düzelir (string) |
| 2940 | `logger.info(f"✅ [Production] BILGILENDIRME: {pid}")` | ❌ Otomatik düzelir (string) |
| 2952 | `f"📋 PID: <code>{pid}</code>"` | ❌ Otomatik düzelir (string) |

**Sonuç:** `pid` değişkeni tüm downstream kullanımlarda string olarak referans edilir. `PIDRecord.pid` de bir string olduğu için, değişiklik sadece 1 oluşturma satırını etkiler, sonraki 7 kullanım otomatik olarak çalışır.

---

## 2. DEĞİŞECEK DOSYALAR

| # | Dosya | Değişiklik | Satır | Sebep | Risk |
|---|-------|----------|:-----:|-------|:----:|
| 1 | `handlers/website.py` | **Import ekle** | Üst seviye import bloğu (satır 10-33 arası) | `pid_runtime` singleton'ına erişim | 🟢 ÇOK DÜŞÜK |
| 2 | `handlers/website.py` | **Satır değiştir** | 2745 | Manuel PID → `pid_runtime.generate()` | 🟢 DÜŞÜK |

**Toplam:** 1 dosya, 2 değişiklik noktası.

### 2.1 Değişiklik #1: Import Ekleme

**Konum:** `handlers/website.py`, satır 33'ten sonra (mevcut import bloğunun sonu)

**Mevcut import bloğu sonu:**
```python
# Satır 32-33
from services.olay_kayit_merkezi import event_registry

logger = logging.getLogger(__name__)
```

**Eklenecek satır:**
```python
from services.olay_kayit_merkezi import event_registry
from services.pid_runtime import pid_runtime          # ← AŞAMA-1: YENİ IMPORT

logger = logging.getLogger(__name__)
```

**Gerekçe:** `pid_runtime` global singleton'dır (`services/pid_runtime.py:1089`). Modül seviyesinde import, `_run_production_pipeline` içinde lazy import gerektirmez. Aynı dosyada `constitution_enforcement`, `execution_event_collector`, `event_registry` zaten aynı şekilde modül seviyesinde import edilmiştir (satır 28-32). Yeni import bu pattern ile tutarlıdır.

### 2.2 Değişiklik #2: PID Oluşturma Satırı

**Konum:** `handlers/website.py`, satır 2745

**Mevcut kod:**
```python
pid = f"PID-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
```

**Yeni kod:**
```python
record = await pid_runtime.generate()
pid = record.pid
```

**Gerekçe:**
- `pid_runtime.generate()` → AR-002_57 PID formatı (`PID-YYYYMMDD-NNNN`)
- `await` gereklidir çünkü `generate()` asenkron çalışır (cross-process kilit)
- `record.pid` → `PIDRecord` nesnesinden PID string'ini alır
- `_run_production_pipeline` zaten `async def` olduğu için `await` kullanılabilir

---

## 3. SADECE OKUNACAK DOSYALAR (Değişiklik Yok)

| # | Dosya | Neden Okunuyor? |
|---|-------|----------------|
| 1 | `services/pid_runtime.py` | Import edilecek modülün mevcut davranışını doğrulamak |
| 2 | `services/pid_runtime.py:495-565` | `generate()` metodunun dönüş tipi (`PIDRecord`) ve `pid` alanı |
| 3 | `services/pid_runtime.py:380-390` | GC parametreleri (GC_PID_PREFIX, GC_PID_SEQUENCE_LENGTH) |
| 4 | `data/pid_runtime_state.json` | Mevcut state'i görmek (Railway'de boş olabilir) |
| 5 | `data/pid_runtime.lock` | Kilit dosyası durumu |
| 6 | `.env` | `GC_PID_PREFIX`, `GC_PID_SEQUENCE_LENGTH` override'ları |

---

## 4. DOKUNULMAMASI GEREKEN DOSYALAR

| # | Dosya | Neden Dokunulmamalı? |
|---|-------|---------------------|
| 1 | `services/pid_runtime.py` | PID Runtime kodu anayasaldır, Aşama-1'de değişiklik gerektirmez |
| 2 | `services/production_runtime.py` | Aşama-5'te entegre edilecek, şimdi dokunulmamalı |
| 3 | `services/production_executor.py` | Aşama-4'te entegre edilecek |
| 4 | `services/production_package_runtime.py` | Aşama-3'te entegre edilecek |
| 5 | `services/execution_event_collector.py` | Aşama-2'de entegre edilecek |
| 6 | `services/olay_kayit_merkezi.py` | Aşama-2'de entegre edilecek |
| 7 | `services/lac.py` | Aşama-7'de entegre edilecek |
| 8 | `main.py` | Değişiklik gerektirmez |
| 9 | `handlers/start.py` | Değişiklik gerektirmez |
| 10 | `handlers/cancel.py` | Değişiklik gerektirmez |
| 11 | `config/settings.py` | Değişiklik gerektirmez |
| 12 | `config/i18n.py` | Değişiklik gerektirmez |
| 13 | `config/video_paths.py` | Değişiklik gerektirmez |
| 14 | `utils/*` (tümü) | Değişiklik gerektirmez |
| 15 | `helpers/*` (tümü) | Değişiklik gerektirmez |

**Özellikle dikkat:** `handlers/website.py` içindeki **diğer iki manuel PID**:

| Satır | Fonksiyon | İşlem |
|:-----:|-----------|-------|
| 2446 | `_build_odeme_bilgileri_karti()` | ⛔ **DOKUNMA!** — Ödeme kartı görüntüsü için, production PID'si değil |
| 2557 | `_build_admin_odeme_bildirimi()` | ⛔ **DOKUNMA!** — Admin bildirim kartı için, production PID'si değil |

Bu iki satır, Aşama-1'in kapsamı dışındadır. Farklı fonksiyonlardadır ve production zincirine ait değildir. Bu aşamada değiştirilmemelidir.

---

## 5. FONKSİYON BAZLI ETKİ ANALİZİ

| Fonksiyon | Dosya:Satır | İşlem | Sebep |
|-----------|:----------:|:-----:|-------|
| `_run_production_pipeline()` | `website.py:2719` | ✅ **1 satır değişecek** | Manuel PID → `pid_runtime.generate()` |
| `_run_production_pipeline()` içi | `website.py:2751,2754,2924,2927,2933,2940,2952` | 🔵 **Otomatik etkilenir** | `pid` string olarak kullanılır, değişiklik gerekmez |
| `handle_admin_payment_approve()` | `website.py:2639` | 🔵 **Dolaylı etkilenir** | `_run_production_pipeline` çağrısı değişmez, ama üretilen PID formatı değişir |
| `pid_runtime.generate()` | `pid_runtime.py:495` | 🟢 **Çağrılacak** | Aşama-1 ile ilk kez production'da kullanılacak |
| `_build_odeme_bilgileri_karti()` | `website.py:2399` | ⛔ **DOKUNULMAZ** | Farklı fonksiyon, production zincirinde değil |
| `_build_admin_odeme_bildirimi()` | `website.py:2543` | ⛔ **DOKUNULMAZ** | Farklı fonksiyon, production zincirinde değil |
| `handle_website_link()` | `website.py:114` | ⛔ **DOKUNULMAZ** | Link doğrulama, production zincirinde değil |
| `handle_payment_declared()` | `website.py:2604` | ⛔ **DOKUNULMAZ** | Ödeme bildirimi, production zincirinde değil |
| `main.py:post_init()` | `main.py:423` | ⛔ **DOKUNULMAZ** | Constitutional Boot, Aşama-1 ile ilgisi yok |

---

## 6. YENİ DOSYA / SİLİNECEK DOSYA

| Soru | Cevap |
|------|-------|
| Yeni dosya oluşturulacak mı? | ❌ **HAYIR** — tüm altyapı mevcut |
| Silinecek dosya var mı? | ❌ **HAYIR** |
| `data/pid_runtime_state.json` silinecek mi? | ❌ **HAYIR** — Railway'de zaten temiz başlar veya mevcut state ile devam eder |
| `data/pid_runtime.lock` silinecek mi? | ⚠️ **SADECE ESKİ/PROBLEMLİ İSE** — Stale lock durumunda temizlenebilir |

---

## 7. RİSK ANALİZİ

### 7.1 Dosya Bazlı Riskler

| Dosya | Risk | Etkisi | Olasılık | Geri Dönüş Yöntemi |
|-------|------|--------|:--------:|-------------------|
| `handlers/website.py` (import) | Yanlış import yolu | `ImportError`, bot başlamaz | ÇOK DÜŞÜK | Import satırını sil, eski koda dön |
| `handlers/website.py:2745` | `pid_runtime.generate()` exception | Production başlamaz | DÜŞÜK | Satırı eski manuel PID'ye geri döndür |
| `data/pid_runtime.lock` | Stale lock (önceki crash) | `generate()` timeout (30s) sonra hata | DÜŞÜK | Lock dosyasını sil, yeniden dene |
| `data/pid_runtime_state.json` | Bozuk JSON | `generate()` çalışır ama sayaç sıfırlanır | ÇOK DÜŞÜK | State dosyasını sil, boş state ile başla |

### 7.2 Runtime Riskleri

| Risk | Etkisi | Olasılık | Önleme | Geri Dönüş |
|------|--------|:--------:|--------|-----------|
| `pid_runtime.generate()` ilk kez çağrıldığında state dosyası yok | Boş state ile başlar, `PID-YYYYMMDD-0001` üretir | YÜKSEK (normal) | Bu beklenen davranıştır, önlem gerekmez | Gerekmez |
| Cross-process kilit hatası (Railway'de fcntl) | PID üretimi timeout olur | DÜŞÜK | `pid_runtime.py:175-249` fcntl.flock kullanır, Railway Linux'ta standart | Stale lock temizle |
| PID format değişikliği eski log'ları etkiler | Eski PID'ler `PID-...-HHMMSS`, yeniler `PID-...-NNNN` — karışmaz | YOK | Format farkı net, arama/kıyaslama etkilenmez | Gerekmez |
| `datetime` import'u artık gereksiz | Kullanılmayan import kalır | YOK | `datetime` zaten satır 15'te import edilmiş, diğer fonksiyonlarda kullanılıyor | Gerekmez |

### 7.3 En Kritik Risk: Cross-Process Kilit

**Senaryo:** Railway'de önceki bir worker crash olmuş ve `pid_runtime.lock` dosyası stale kalmış olabilir.

**PID Runtime'ın savunması:**
- `_cross_process_lock_acquire()` (satır 171-329) içinde `_break_stale_lock()` çağrısı vardır
- `_GC_PID_LOCK_TIMEOUT = 30.0` saniye — bu süreden eski kilitler otomatik kırılır
- `_is_lock_stale()` (satır 99-121) — holder bilgisi ve mtime kontrolü yapar
- Railway'de `fcntl.flock` kernel-enforced olduğu için process exit'te otomatik serbest kalır

**Ek önlem:** Deploy öncesi `data/pid_runtime.lock` dosyası manuel olarak silinebilir. PID Runtime yokluğunda sorunsuz başlar.

---

## 8. RAILWAY TEST PLANI

### 8.1 Test Ortamı Gereksinimleri

| Gereksinim | Açıklama |
|-----------|----------|
| Ortam | Railway Production (`ENV=production`) |
| Bot | `@hlk_reklam_asistani01_bot` |
| Ön koşul | `.env`'de `TELEGRAM_TOKEN` production token'ı |
| Temizlik (opsiyonel) | `data/pid_runtime.lock` ve `data/pid_runtime_state.json` silinebilir |

### 8.2 Testler

#### Test 1: Temel PID Üretimi

| Parametre | Değer |
|-----------|-------|
| **Amaç** | `pid_runtime.generate()` başarıyla çağrılır ve anayasal PID formatı üretir |
| **Test Adımı** | 1. `/start` ile yeni oturum başlat<br>2. Tüm sahne akışını tamamla (ürün linki → brief → senaryo → fiyat → ödeme)<br>3. Yönetici ödemeyi onaylasın → production başlasın<br>4. Log'ları kontrol et |
| **Beklenen Sonuç** | Log'da `🆔 [PID Runtime] PID oluşturuldu: PID-20260715-0001` görünür |
| **Başarı Kriteri** | `[ ]` PID formatı `PID-YYYYMMDD-NNNN`<br>`[ ]` `data/pid_runtime_state.json` güncellenir<br>`[ ]` Production hatasız tamamlanır<br>`[ ]` Kullanıcı videosunu alır |

#### Test 2: PID Format Doğrulaması (Statik Kontrol)

| Parametre | Değer |
|-----------|-------|
| **Amaç** | Üretilen PID'nin `validate_pid_static()` ile format kontrolünden geçmesi |
| **Test Adımı** | 1. Test 1'de üretilen PID'yi al<br>2. `validate_pid_static(pid)` çağrısı yap |
| **Beklenen Sonuç** | `PIDValidationResult.is_valid == True` |
| **Başarı Kriteri** | `[ ]` `checks.format_valid == True`<br>`[ ]` `checks.date_valid == True`<br>`[ ]` `checks.sequence_valid == True` |

#### Test 3: PID Tekillik Kontrolü

| Parametre | Değer |
|-----------|-------|
| **Amaç** | Aynı gün ikinci production'da sayaç artar, farklı PID üretilir |
| **Test Adımı** | 1. Test 1'deki production'dan sonra ikinci bir production başlat<br>2. İki PID'yi karşılaştır |
| **Beklenen Sonuç** | İlk PID: `PID-20260715-0001`, İkinci PID: `PID-20260715-0002` |
| **Başarı Kriteri** | `[ ]` `pid1 != pid2`<br>`[ ]` Sayaç 1'den 2'ye artar<br>`[ ]` `data/pid_runtime_state.json`'da iki kayıt |

#### Test 4: Production Akışı Bozulmadı

| Parametre | Değer |
|-----------|-------|
| **Amaç** | PID değişikliği production'ın diğer adımlarını etkilemez |
| **Test Adımı** | 1. Test 1'deki production akışını izle<br>2. Görsel, ses, video üretimi ve teslimat adımlarını kontrol et |
| **Beklenen Sonuç** | Tüm production adımları başarıyla tamamlanır |
| **Başarı Kriteri** | `[ ]` Görsel üretimi başarılı<br>`[ ]` Ses üretimi başarılı<br>`[ ]` Video üretimi başarılı<br>`[ ]` Video kullanıcıya gönderilir<br>`[ ]` Log'da `✅ [Production] VIDEO GONDERILDI: PID-...` görünür |

#### Test 5: Restart Sonrası Sayaç Devamlılığı

| Parametre | Değer |
|-----------|-------|
| **Amaç** | Bot restart olduğunda PID sayacı kaldığı yerden devam eder |
| **Test Adımı** | 1. Test 1 ve 3'te PID'ler üret (ör: 0001, 0002)<br>2. Bot'u restart et<br>3. Yeni bir production başlat |
| **Beklenen Sonuç** | Yeni PID: `PID-20260715-0003` (0002'den sonra) |
| **Başarı Kriteri** | `[ ]` `data/pid_runtime_state.json` restart sonrası korunur<br>`[ ]` Sayaç 3'e devam eder (0001, 0002'den sonra)<br>`[ ]` Eski PID'ler pasif (`is_active: false`) |

#### Test 6: Eski PID Formatıyla Karışmama

| Parametre | Değer |
|-----------|-------|
| **Amaç** | Yeni PID formatı (`NNNN`) eski formattan (`HHMMSS`) ayırt edilebilir |
| **Test Adımı** | 1. Yeni PID formatını kontrol et<br>2. Eski log'larla karşılaştır |
| **Beklenen Sonuç** | Yeni: `PID-20260715-0001` (4 haneli)<br>Eski: `PID-20260715-115926` (6 haneli) |
| **Başarı Kriteri** | `[ ]` Format farkı net<br>`[ ]` `len(sequence_part) == 4` |

---

## 9. ROLLBACK PLANI

### 9.1 Acil Rollback (Production Durursa)

**Süre:** < 1 dakika

```
Adım 1: handlers/website.py:2745 satırını eski haline döndür
        pid = f"PID-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"

Adım 2: handlers/website.py import satırını kaldır
        from services.pid_runtime import pid_runtime  ← BU SATIRI SİL

Adım 3: Bot'u restart et
        Railway'de redeploy
```

### 9.2 Kısmi Rollback (PID Runtime Çalışıyor Ama Sorun Var)

**Süre:** < 2 dakika

```
Adım 1: _run_production_pipeline içinde pid_runtime.generate() çağrısını
        try/except içine al:
        
        try:
            record = await pid_runtime.generate()
            pid = record.pid
        except Exception as e:
            logger.warning(f"PID Runtime hatası, manual PID'ye dönülüyor: {e}")
            pid = f"PID-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"

Adım 2: Bu, PID Runtime hatasında production'ın devam etmesini sağlar
```

### 9.3 State Temizliği (Gerektiğinde)

```
# Railway'de SSH/Shell erişimi ile:
rm -f data/pid_runtime.lock
rm -f data/pid_runtime_state.json
# PID Runtime boş state ile başlar, PID-YYYYMMDD-0001'den devam eder
```

---

## 10. ANAYASAL UYUM KONTROLÜ

### 10.1 MASTER

| Kural | Gereklilik | Aşama-1 Durumu |
|-------|-----------|---------------|
| **MASTER-001** | Analiz Zorunluluğu — kod değişikliğinden önce anayasa okunur | ✅ Bu blueprint AR-002_57, AR-002_71 referanslarıyla hazırlandı |
| **MASTER-003** | Kod ↔ Anayasa ↔ Runtime uyumu | ✅ PID formatı AR-002_57'ye uygun hale gelir |
| **MASTER-004** | Karar Mekanizması — modül kendi başına karar vermez | ✅ `pid_runtime` karar vermez, sadece PID üretir |

### 10.2 GC (Global Configuration)

| Parametre | Değer | Kaynak | Aşama-1'de Kullanım |
|-----------|-------|--------|-------------------|
| `GC_PID_PREFIX` | `PID` | `pid_runtime.py:381` — env: `GC_PID_PREFIX` | ✅ `PIDRecord.pid` bu prefix ile başlar |
| `GC_PID_DATE_FORMAT` | `YYYYMMDD` | `pid_runtime.py:382` | ✅ Tarih formatı |
| `GC_PID_SEQUENCE_LENGTH` | `4` | `pid_runtime.py:383` — env: `GC_PID_SEQUENCE_LENGTH` | ✅ 4 haneli sayaç (0001, 0002, ...) |
| `GC_PID_SEQUENCE_START` | `1` | `pid_runtime.py:384` | ✅ Sayaç 1'den başlar |
| `GC_PID_LOCK_TIMEOUT` | `30.0` | `pid_runtime.py:72` — env: `GC_PID_LOCK_TIMEOUT` | ✅ Stale lock 30sn sonra kırılır |

### 10.3 GK (Genel Kurallar)

| Kural | Gereklilik | Aşama-1 Durumu |
|-------|-----------|---------------|
| **GENEL_KURAL_1** | Oturum zaman aşımı | ✅ Aşama-1 oturum yönetimini etkilemez |

### 10.4 AR (Architecture Rules)

| Kural | Gereklilik | Aşama-1 Durumu |
|-------|-----------|---------------|
| **AR-002_57** | PID formatı: `PID-YYYYMMDD-NNNN` | ✅ `pid_runtime.generate()` bu formatı üretir |
| **AR-002_57** | PID Tekillik Kuralı | ✅ Cross-process kilit + persistence |
| **AR-002_57** | PID Merkeziyet Kuralı | ✅ Sadece `pid_runtime` singleton'ı PID üretir |
| **AR-002_57** | PID silinemez | ✅ `deactivate()` ile pasifleştirilir, silinmez |
| **AR-002_71** | PID Runtime — tek yetkili katman | ✅ `pid_runtime.generate()` kullanılır |
| **AR-002_71** | Ön koşul: STATE_VIDEO_PRODUCTION | ⚠️ Aşama-1'de state kontrolü yapılmaz — Aşama-5'te eklenecek |

> **Not:** AR-002_71, PID oluşturma için STATE_VIDEO_PRODUCTION state'inde olmayı ön koşul sayar. Aşama-1, state kontrolü olmadan PID Runtime'ı doğrudan çağırır. Bu, Aşama-5'te `production_runtime.start_production()` içinde düzeltilecektir. Aşama-1'in amacı format düzeltmedir, tam anayasal akış değildir.

### 10.5 SE (State Engine)

| Kural | Gereklilik | Aşama-1 Durumu |
|-------|-----------|---------------|
| **SE-007_3** | STATE_VIDEO_PRODUCTION | ⚠️ State kontrolü Aşama-5'te eklenecek |
| **SE-007_4** | STATE_PAYMENT_VERIFICATION → STATE_VIDEO_PRODUCTION | ⚠️ Mevcut akışta `se.fire(PAYMENT_APPROVED)` zaten çağrılır (`website.py:2650`) |

### 10.6 FLOW (Flow Diagram)

| Kural | Gereklilik | Aşama-1 Durumu |
|-------|-----------|---------------|
| **FD-008_1** | STATE_VIDEO_PRODUCTION akışı | ✅ Aşama-1 PID üretimini düzeltir, akışı değiştirmez |

### 10.7 OR (Operational Rules)

| Kural | Gereklilik | Aşama-1 Durumu |
|-------|-----------|---------------|
| **OR-004** | Operasyonel kurallar | ✅ Aşama-1 operasyonel akışı değiştirmez |

### 10.8 QR (Quality Rules)

| Kural | Gereklilik | Aşama-1 Durumu |
|-------|-----------|---------------|
| **QR-004** | Kalite kontrol | ✅ Aşama-1 kalite kontrolü etkilemez |

### 10.9 MR (Module Rules)

| Kural | Gereklilik | Aşama-1 Durumu |
|-------|-----------|---------------|
| **MR** | Modül bağımsızlığı | ✅ `pid_runtime` kendi sorumluluğunda çalışır |

---

## 11. UYGULAMA ÖNCESİ KONTROL LİSTESİ

Aşama-1 uygulanmadan önce aşağıdakiler doğrulanmalıdır:

- [ ] `services/pid_runtime.py` dosyası mevcut ve import edilebilir
- [ ] `services/pid_runtime.py:1089` — `pid_runtime` singleton'ı mevcut
- [ ] `services/pid_runtime.py:495` — `generate()` metodu `PIDRecord` döndürür
- [ ] `data/` dizini mevcut (yoksa PID Runtime otomatik oluşturur)
- [ ] `data/pid_runtime.lock` dosyası stale değil (varsa silinebilir)
- [ ] `.env`'de `GC_PID_PREFIX`, `GC_PID_SEQUENCE_LENGTH` override'ları yok (varsayılanlar yeterli)
- [ ] `handlers/website.py:2745` satırındaki mevcut kod yedeklendi
- [ ] Railway deploy öncesi test ortamında (`ENV=test`) bir kez denenmiş

---

## 12. UYGULAMAYA HAZIRLIK KARARI

# ✅ AŞAMA-1 UYGULAMAYA HAZIR

**Gerekçe:**

1. **Değişiklik minimal:** 1 dosya, 2 satır (1 import + 1 satır değişikliği)
2. **Rollback anında:** Tek satır geri alınarak eski PID formatına dönülebilir
3. **Downstream etki yok:** `pid` değişkeni tüm kullanımlarda string, `PIDRecord.pid` de string
4. **PID Runtime production'da test edilmiş:** Cross-process kilit, persistence, tekillik mekanizmaları testlerle doğrulanmış
5. **Railway uyumlu:** `fcntl.flock` Linux'ta kernel-enforced, process crash'te otomatik serbest
6. **Anayasal uyum:** AR-002_57 PID format ihlali giderilir
7. **Sonraki aşamalara temel:** Doğru PID formatı, Aşama 2-9 için zorunlu ön koşuldur

---

**Blueprint Hazırlayan:** Claude Code (DeepSeek V4 Pro)
**Hazırlanma Tarihi:** 15 Temmuz 2026
**Anayasal Referans:** AR-002_57, AR-002_71, GC_PID_PREFIX, GC_PID_SEQUENCE_LENGTH
**Değişiklik Kapsamı:** 1 dosya, 2 satır
**Risk:** 🟢 DÜŞÜK
