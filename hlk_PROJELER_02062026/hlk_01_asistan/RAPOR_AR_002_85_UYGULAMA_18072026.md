# RAPOR — AR-002_85 Video Üretim Başarı İlkesi: Anayasa Ekleme ve Kod Uyumlulaştırma

**Tarih:** 18.07.2026
**Kapsam:** AR-002_85 anayasa maddesinin eklenmesi ve kod tabanının bu maddeye uygun hale getirilmesi.

---

## 1. Yeni Anayasa Maddesi

| Alan | Değer |
|---|---|
| **Dosya** | `ANA YASA/03_Architecture_Rules.md` |
| **Yeni AR numarası** | **AR-002_85** |
| **Madde Adı** | VİDEO ÜRETİM BAŞARI İLKESİ |
| **Eklenme yeri** | AR-002_84'ün hemen altı (satır 7488) |
| **Önceki son kural** | AR-002_84 (satır 7276) |

---

## 2. Değiştirilen Dosyalar

| # | Dosya | Değişiklik |
|---|---|---|
| 1 | `ANA YASA/03_Architecture_Rules.md` | AR-002_85 eklendi (+113 satır) |
| 2 | `services/production_runtime.py` | 5 `success=True` sabit değeri kaldırıldı, hesaplanan değerlerle değiştirildi |
| 3 | `services/hlk_runtime.py` | `_decide_completion` artık `delivered AND video AND failed==0` kontrolü yapıyor |

---

## 3. Yapılan Değişikliklerin Özeti

### 3.1 Tespit Edilen İhlaller ve Düzeltmeleri

| # | Dosya:Satır | İhlal | Düzeltme |
|---|---|---|---|
| **İ1** | `production_runtime.py:1198` | `success=True` hardcoded → `_notify_reproduction_result` | `reproduction_success = ctx.delivered and bool(ctx.video_path)` ile hesaplanan değer |
| **İ2** | `hlk_runtime.py:869` | `_decide_completion` her durumda `{"success": True}` | `if failed_tasks == 0 and delivered and video: completion_success = True else: completion_success = False` |
| **İ3** | `production_runtime.py:1966` | Exception'da fallback `completion_success = True` | `completion_success = False` (AR-002_85: doğrulanmamış başarı üretilemez) |
| **İ4** | `production_runtime.py:265` | `_result.success = True` (koşulsuz) | `_result.success = executor_report.get("failed_tasks", 0) == 0` |
| **İ5** | `production_runtime.py:679` | `_result.success = True` (koşulsuz) | `_result.success = executor_report.get("failed_tasks", 0) == 0` |
| **İ6** | `production_runtime.py:1975` | `params.get("success", True)` varsayılan `True` | `params.get("success", False)` |
| **İ7** | `production_runtime.py:1204` | `params.get("success", True)` varsayılan `True` | `params.get("success", False)` |

### 3.2 Nihai Durum

```bash
# Kod tabanında hardcoded success=True arandı:
grep -rn '\.success\s*=\s*True\b' services/  → SONUÇ: BOŞ (0 eşleşme)
grep -rn '"success", True' services/          → SONUÇ: BOŞ (0 eşleşme)
grep -rn 'success=True' services/             → SONUÇ: 0 sabit değer
```

Kalan `completion_success = True` (hlk_runtime.py:863) **koşulludur** — yalnızca `failed_tasks == 0 and delivered and video` sağlandığında atanır. AR-002_85 ile uyumludur.

---

## 4. Doğrulanan Video Üretim Akışları

| Akış | Başarı Koşulu | Doğrulama Zinciri | AR-002_85 Uyumu |
|---|---|---|---|
| **İlk Video Üretimi** (`_run_managed`) | `_result.success = failed_tasks == 0` + COMPLETION kararı `delivered AND video AND failed==0` | executor report → failed_tasks → COMPLETION → HLK Runtime → CEE | ✅ |
| **Yeniden Üretim** (`_run_reproduction`) | `ctx.delivered AND bool(ctx.video_path)` → `reproduction_success` → `_notify_reproduction_result(success=hesaplanan)` | pipeline context → ctx.delivered + ctx.video_path → notification | ✅ |
| **Devam Ettirme** (`recover`) | `_result.success = failed_tasks == 0` | executor report → failed_tasks | ✅ |
| **Tekrar Deneme** (RETRY) | `_run_reproduction` akışıyla aynı | ctx.delivered + ctx.video_path | ✅ |
| **Toplu Üretim** | `_run_managed` akışıyla aynı | executor report + COMPLETION | ✅ |

Her akışta:
- Başarı kararı **gerçek veriye** dayanır (video dosyası varlığı, teslimat durumu, executor raporu)
- **Sabit `success=True` değeri** hiçbir kod yolunda kalmamıştır
- COMPLETION kararı `delivered AND video AND failed==0` şartına bağlıdır
- `params.get("success", False)` → varsayılan başarısızlıktır

---

## 5. Sonuç

**"HLK artık doğrulanmamış hiçbir video üretimini başarı olarak değerlendiremez, tamamlandı olarak işaretleyemez ve kullanıcıya veya yöneticiye bildiremez."**
