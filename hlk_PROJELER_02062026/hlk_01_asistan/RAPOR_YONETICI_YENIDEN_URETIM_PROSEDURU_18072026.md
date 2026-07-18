# RAPOR — Yönetici Yeniden Üretim Prosedürü (AR-002_84)

**Tarih:** 18.07.2026
**Görev:** Üretimi başarısız olan bir PID'nin, HLK Anayasası doğrultusunda tekrar üretilebilmesini sağlayan Yönetici Yeniden Üretim Prosedürünün sisteme eklenmesi.
**Durum:** ✅ TAMAMLANDI — ANA YASA güncellendi + Kod güncellendi + Runtime davranışı test ile doğrulandı (MASTER-003).

---

## 1. Özet

- Yönetici, yalnızca **PID** veya **Ürün Adı** girerek (`/yeniden <PID | Ürün Adı>`) prosedürü başlatır.
- HLK ilgili Production Package'i otomatik bulur; PID, Ürün Adı, Marka, Üretim Tarihi ve Mevcut Üretim Durumunu gösterir; anayasal onay ekranını sunar (**[Evet, Başlat] / [İptal]**).
- Onay sonrası 21 adımlık anayasal prosedür **HLK Runtime kontrolünde** otomatik yürütülür; Yönetici hiçbir teknik karar vermez (MASTER-013).
- Sonuç, Telegram üzerinden hem Yöneticiye hem ilgili Kullanıcıya otomatik bildirilir.
- **Yeni mimari kurulmadı** — mevcut mimariler yeniden kullanıldı: aynı gün eklenen ancak hiçbir yerden çağrılmayan yeniden üretim altyapısı (`find_package`, `prepare_for_reproduction`, `load_full_production_context`, `_decide_reproduction`, Executor `recover`) ilk kez devreye bağlandı.

---

## 2. Anayasal Analiz (MASTER-001 Uygulaması)

Geliştirme öncesi okunan kaynaklar: 00_MASTER_RULE_BOOK, 01_GC, 02_GK, 03_AR (özellikle AR-002_56/57/58/70/76/79/80/81/82/83), 04_OR (OR-004_11/12), 07_STATE_ENGINE, 08_FLOW_DIAGRAM, 09/10/11 kayıt dosyaları, 12/13 Dijital Varlık, 14_OLAY, 15_KARAR, 16_PP_STANDARD, 17_SAHNE.

**Belirleyici dayanak:** OLAY-025 (`EVENT_VIDEO_PRODUCTION_FAILED`) kaydında **"Tekrar Deneme Politikası: Yönetici onayı gerekir"** hükmü zaten mevcuttu. Bu geliştirme, o hükmün AR-002_82 (Mission Persistence) + AR-002_83 (Recovery Policy) çerçevesindeki runtime uygulamasıdır.

**Çelişki kontrolü:** Çelişki tespit edilmedi.
- AR-002_80'in "kapanan Production Runtime yeniden açılamaz" kısıtı yalnızca anayasal kapanışı **tamamlanmış** üretimler içindir; başarısız PID kapanış kriterlerini sağlamadığından aynı PID'ye bağlı **yeni bir yürütme döngüsü** başlatılabilir (AR-002_79 "Kaldığı Noktadan Devam").
- AR-002_57/58 gereği **yeni PID ve yeni Production Package oluşturulmaz**; mevcut PID/paket korunur, sürüm geçmişi (`revision_history`) işlenir.
- FD-008_4 zaten "Session Resume Flow" için rezerve alan tanımlamıştı.

---

## 3. Mimari Akış

```
/yeniden <PID | Ürün Adı>                (yalnızca Yönetici — TELEGRAM_ADMIN_USER_ID)
    ↓
find_package()                           (AR-002_72 — PID / ürün adı / marka araması)
    ↓  bulunamadı → OLAY-109 + anayasal gerekçeli Yönetici bildirimi + güvenli sonlandırma
Bilgi Kartı + Anayasal Onay Ekranı       (AR-002_56 deseni — [Evet, Başlat] / [İptal])
    ↓  [İptal] → hiçbir üretim başlatılmaz
[Evet, Başlat] → Constitutional Boot Chain doğrulaması (AR-002_62/70)
    ↓
production_runtime.launch_reproduction() (AR-002_70 — tek giriş noktası)
    ↓
Adım 1-21 (AR-002_84):
  1  PID doğrulama (AR-002_57)
  2-10  Paket + Workflow + State + Olay + Varlık Arşivi/Kataloğu + Sahne + Karar kayıtları yüklenir
  11 SHA-256 bütünlük doğrulaması
  12-13 Son başarılı / başarısız aşama (Task checkpoint kayıtları)
  14-16 HLK Runtime REPRODUCTION kararı → Decision History'ye kayıt
        RETRY | RESUME | REPLAY | START_AS_NEW | REJECT
  17 prepare_for_reproduction + ProductionRequest/PipelineContext yeniden kurulumu
     + Decision Engine servis seçimi (AR-002_75, AR-002_82 Adım 7) + CEE PRE-CHECK
  18 production_executor.recover() — tamamlanmış task'lar checkpoint'ten atlanır
  19 EEC + Olay Kayıt Merkezi + LAC + paket event_logs kayıtları
  20 final_video/service_usage/delivery_info güncellenir; sürüm geçmişi korunur
  21 CEE POST-CHECK + COMPLETION kararı + Telegram bildirimi (Yönetici + Kullanıcı)
```

**Prosedür kararları (HLK Runtime — `_decide_reproduction`):**

| Paket Durumu | Karar | Davranış |
|---|---|---|
| FAILED / başarısız task var | RETRY | Yalnızca başarısız task'lar yeniden koşar; tamamlananlar korunur |
| READY / BUILDING / PRODUCING | RESUME | Kaldığı noktadan devam |
| CREATED | START_AS_NEW | Mevcut PID ile normal akış |
| COMPLETED | REPLAY | Açık Yönetici talebiyle yeni üretim sürümü; mevcut varlıklar korunur |
| ARCHIVED / Runtime pasif / tanımsız | REJECT | Güvenli sonlandırma + gerekçeli bildirim |

---

## 4. Değişen Dosyalar ve Anayasal Gerekçeleri

### 4.1 ANA YASA güncellemeleri (MASTER-003: önce anayasa)

| Dosya | Değişiklik | Anayasal Gerekçe |
|---|---|---|
| `ANA YASA/03_Architecture_Rules.md` | **AR-002_84** maddesi eklendi (Yönetici Yeniden Üretim Prosedürü Mimarisi) | MASTER-005: mevcut katmana madde ekleme (AR-002_82/83 ile aynı yöntem); Proje Yöneticisi talimatı bu görevin kendisidir. Mevcut maddeler değiştirilmedi |
| `ANA YASA/14_OLAY_KAYIT_MERKEZI.md` | **OLAY-107/108/109** eklendi (`EVENT_REPRODUCTION_REQUESTED/STARTED/REJECTED`) | MASTER-001 Single Source of Truth: kodda kullanılan her event yalnızca 14'te tanımlanır. Tamamlanma/başarısızlık için yeni event üretilmedi — OLAY-024/025 yeniden kullanıldı. Numaralandırma: en yüksek kullanılan OLAY-106 → 107'den devam |
| `ANA YASA/01_Global_Configuration.md` | `GC_REPRODUCE_SEARCH_LIMIT` (20), `GC_REPRODUCE_MAX_CANDIDATES` (5) kayıtları eklendi | GC İlkesi + AR-002_81 Sayısal Değer Yasağı: bu parametreler kodda mevcuttu ancak GC dosyasında kayıtlı değildi — uyumsuzluk giderildi |

Dokunulmayan anayasa dosyaları ve gerekçesi: **07_STATE_ENGINE** (yeni kullanıcı state'i yok — prosedür kullanıcı konuşma akışı dışında, Production Runtime seviyesinde çalışır), **08_FLOW_DIAGRAM** (kullanıcı sahne akışı değişmedi), **09/10/11** (yeni Workflow/Feature kaydı gerekmedi — WF-008 + WF-017 + FEAT-014 kapsamı yeterli; AR-002_84 bunlara atıf yapar), **17_SAHNE** (yeni sahne yok).

### 4.2 Kod değişiklikleri

| Dosya | Değişiklik | Anayasal Gerekçe |
|---|---|---|
| `handlers/yeniden_uretim.py` **(YENİ)** | `/yeniden` komutu, bilgi kartı + onay ekranı, onay/iptal callback'leri, `TELEGRAM_ADMIN_USER_ID` yetki katmanı | AR-002_84 Yönetici İş Akışı; MASTER-013 (handler karar vermez, yalnızca devreder); OLAY-025 "Yönetici onayı gerekir"; onay ekranı deseni AR-002_56 |
| `services/production_runtime.py` | `launch_reproduction()` + `run_reproduction()` + `_run_reproduction()` (Adım 1-21), istisna/başarısızlık yolları, olay-kayıt yardımcıları; ayrıca `_run_managed` brief bölümüne `user_id`/`chat_id` eklendi | AR-002_70 (Production Runtime tek giriş noktası ve tek orkestratör); AR-002_79/82/83 (mevcut süreklilik/recovery mimarilerinin kullanımı); brief'e kullanıcı kimliği: Adım 21 Kullanıcı bildirimi için kalıcı adres — 12/13_DIGITAL_ASSET kayıt standardındaki "Kullanıcı Kimliği/Telegram Kimliği" alanlarıyla uyumlu |
| `services/hlk_runtime.py` | `_decide_user_notification`'a 5 yeni bildirim türü: `reproduction_not_found / rejected / started / completed / failed` | MASTER-013 + OR-004_12 + GK-001_5: süreç kararı içeren tüm mesaj içerikleri yalnızca HLK Runtime kararı ile üretilir |
| `services/production_executor.py` | (a) `recover()` farklı PID'den kalan eski raporu sıfırlar; (b) `_update_package_status` event_logs'a artık **ekleme** yapar (önceden bölümü siliyordu) | (a) AR-002_79: recovery raporu ilgili PID'nin gerçek tamamlanma durumunu göstermeli; (b) **mevcut kusur düzeltmesi** — AR-002_73 + 15_KARAR §10 "kayıtlar silinemez": eski kod her üretim sonunda önceki tüm event loglarını yok ediyordu (kodun kendi yorumu "mevcut loglara eklenir" ile de çelişiyordu) |
| `services/production_package_runtime.py` | `archive()` içindeki **mevcut kusur** düzeltildi: `json.dumps` çıktısına (string) sözlük ataması yapılıyordu → arşivleme her zaman `'str' object does not support item assignment` ile çöküyordu | 16_PP_STANDARD Temel İlke #4 "Production Package arşivlenebilir" fiilen çalışmıyordu; AR-002_84 arşiv araması (`find_package`) ve REJECT-ARCHIVED yolu doğru arşiv formatına muhtaçtır. Düzeltme `_save_to_disk` ile aynı formatı kullanır |
| `main.py` | `/yeniden` CommandHandler + `reprod_onay:`/`reprod_iptal:` CallbackQueryHandler kayıtları | Mevcut handler kayıt deseni (main.py Command/Callback bölümü) |
| `test_yeniden_uretim.py` **(YENİ)** | 7 testlik doğrulama paketi (aşağıda) | MASTER-003 Runtime doğrulaması; test artıkları kendini temizler |

**Bilinçli olarak dokunulmayanlar:** `production_runtime.recover()` (eski imza korunarak geriye dönük uyumlu bırakıldı — AR-002_84 akışı onun yerine yönetilen `run_reproduction`'ı kullanır), `handlers/website.py`, `config/i18n.py`, `utils/state_engine.py`, `services/scene_registry.py`.

---

## 5. Yetki Matrisi (MASTER-013)

| İşlem | Yönetici | HLK Runtime |
|---|:---:|:---:|
| Prosedürü başlatma (PID/Ürün Adı + onay) | ✅ | — |
| Üretimin devamı / yeniden üretim kararı | ❌ | ✅ (`_decide_reproduction`) |
| Kurtarma kararları | ❌ | ✅ (AR-002_79/83) |
| Sağlayıcı / model seçimleri | ❌ | ✅ (Decision Engine — AR-002_75) |
| Üretim stratejileri | ❌ | ✅ |
| Bildirim içerikleri | ❌ | ✅ (USER_NOTIFICATION kararları) |
| Tamamlanma kararı | ❌ | ✅ (COMPLETION — AR-002_80/82) |

Kullanıcı prosedürü **başlatamaz**: `/yeniden` komutu ve her iki callback `TELEGRAM_ADMIN_USER_ID` doğrulamasıyla korunur; değişken tanımsızsa **hiç kimse** Yönetici kabul edilmez (güvenli varsayılan).

---

## 6. İstisna Durumları

| Durum | Davranış |
|---|---|
| PID doğrulanamadı / paket bulunamadı | Prosedür başlatılmaz → OLAY-109 → anayasal gerekçeli Yönetici bildirimi → güvenli sonlandırma |
| Paket ARCHIVED | HLK Runtime REJECT → gerekçeli bildirim → güvenli sonlandırma |
| Boot Chain pasif | `authorization_denied` bildirimi → üretim başlatılmaz |
| Üretim yeniden başarısız | OLAY-025 + eskalasyon kaydı + paket FAILED + **durum ve anayasal karar gerekçesi** Yöneticiye ve Kullanıcıya bildirilir |
| Yönetici [İptal] | Hiçbir üretim işlemi başlatılmaz |

---

## 7. Test Sonuçları (Runtime Doğrulaması)

| Test Paketi | Sonuç |
|---|---|
| `test_yeniden_uretim.py` (YENİ — 7 test: arama, kayıt yükleme, 7 karar senaryosu, RETRY hazırlığı, checkpoint recovery, tam zincir Adım 1-21, istisna akışı) | **7/7 PASS** |
| `test_production_executor.py` (regresyon) | **11/11 PASS** |
| `test_production_package_runtime.py` (regresyon — arşiv düzeltmesi sonrası) | **12/12 PASS** (önceki durumda TEST 12 her koşuda düşüyordu) |
| `test_production_runtime.py` (regresyon) | **13/13 PASS** |
| Sözdizimi (`py_compile`) — değişen 5 py dosyası | OK |
| `main.py` import (handler zinciri) | OK |

Tam zincir testinde doğrulanan davranışlar: OLAY-107 + OLAY-108 paket `event_logs`'unda kalıcı; REPRODUCTION kararı `decision_history`'de; sürüm geçmişi `revision_history`'de; Yönetici 2 bildirim (başlangıç + tamamlanma), Kullanıcı 2 bildirim (teslim + tamamlanma) aldı; tamamlanan task'lar checkpoint'ten atlandı.

Test artıkları temizlendi (`data/production_packages` boş — proje kuralı).

---

## 8. Kurulum Notu (Canlıya Geçiş)

Railway (ve lokal `.env`) ortamına aşağıdaki değişken eklenmelidir:

```
TELEGRAM_ADMIN_USER_ID=<Yöneticinin Telegram kullanıcı ID'si>
```

Bu değişken tanımlanmadan `/yeniden` komutu hiç kimse için çalışmaz (güvenli varsayılan). Kod değişikliği commit edilip Railway'e deploy edildikten sonra prosedür canlıda aktif olur.

---

## 9. Bilinen Sınırlar

1. **Eski paketlerde kullanıcı adresi:** Bu geliştirmeden önce üretilmiş başarısız paketlerde `brief.chat_id` bulunmaz; bu durumda teslim/bildirim Yönetici sohbetine yapılır. Yeni üretimlerde kullanıcı kimliği pakete kalıcı yazılır.
2. **Ortama bağlı PID kayıtları:** `data/pid_runtime_state.json` ortama özgüdür — Railway'de üretilen bir PID lokalde doğrulanamaz; istisna akışı devreye girer (güvenli sonlandırma). Canlı yeniden üretim canlı ortamda çalıştırılmalıdır.
3. **Test ortamında CEE POST-CHECK uyarısı:** Gerçek provider anahtarları olmadan DecisionPacket doğrulaması FAIL raporlar (kayıt amaçlıdır, akışı engellemez — normal üretim akışıyla aynı davranış). Canlıda gerçek provider'larla geçerlidir.
4. **OLAY-104..106:** 21_CEE dosyasında referanslı ancak 14_OLAY'da tanımsız (mevcut tutarsızlık, bu görevin kapsamı dışında) — çakışmayı önlemek için yeni olaylar OLAY-107'den başlatıldı.

---

## 10. MASTER-003 Uyum Beyanı

| Koşul | Durum |
|---|---|
| ANA YASA güncellendi | ✅ AR-002_84 + OLAY-107/108/109 + GC kayıtları |
| Kod güncellendi | ✅ 5 dosya güncellendi, 2 dosya eklendi |
| Runtime davranışı doğrulandı | ✅ 43/43 test PASS (7 yeni + 36 regresyon) |

**= TAMAMLANDI**
