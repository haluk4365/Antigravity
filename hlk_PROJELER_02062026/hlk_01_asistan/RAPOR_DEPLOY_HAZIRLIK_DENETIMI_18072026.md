# RAPOR — Deploy Hazırlık Denetimi (Yönetici Yeniden Üretim Prosedürü / AR-002_84)

**Tarih:** 18.07.2026
**Kapsam:** AR-002_84 Yönetici Yeniden Üretim Prosedürü geliştirmesinin canlı ortama (Railway — @HLK_01_asistan_bot) alınmadan önce eksiksiz dağıtım öncesi doğrulaması.
**Yöntem:** MASTER-001 anayasal analiz + git denetimi + statik/import doğrulama + Railway ortam denetimi (salt okunur). Hiçbir commit, push, merge veya deploy işlemi YAPILMADI. Hiçbir üretim BAŞLATILMADI.

✅ Tüm KAYNAKLAR okundu ve öğrenildi.
(00_MASTER_RULE_BOOK, 01_GC, 02_GK, 03_AR — AR-002_84 diff, 07_STATE_ENGINE, 08_FLOW_DIAGRAM — FD-008_4, 14_OLAY diff — OLAY-107/108/109, ilgili servis kaynakları)

---

## 1. Kod Değişiklik Denetimi

**Değiştirilen dosyalar (9):**

| Dosya | Değişiklik | Denetim Sonucu |
|---|---|---|
| `ANA YASA/03_Architecture_Rules.md` | +212 satır — dosya sonuna **AR-002_84** eklendi | ✅ Salt ekleme; mevcut maddeler değiştirilmedi (RS-006 uyumlu) |
| `ANA YASA/14_OLAY_KAYIT_MERKEZI.md` | +92 satır — **OLAY-107/108/109** eklendi | ✅ Salt ekleme; Bölüm 21 öncesine yerleştirilmiş |
| `ANA YASA/01_Global_Configuration.md` | +2 satır — `GC_REPRODUCE_SEARCH_LIMIT` (20), `GC_REPRODUCE_MAX_CANDIDATES` (5) | ✅ Salt ekleme |
| `config/settings.py` | +7 — `TELEGRAM_ADMIN_USER_ID` + `is_admin()` (güvenli varsayılan) | ✅ |
| `main.py` | +15 — `/yeniden` CommandHandler + `reprod_onay:`/`reprod_iptal:` callback kayıtları | ✅ Mevcut kayıt deseniyle birebir |
| `services/hlk_runtime.py` | +218 — REPRODUCTION karar kategorisi + `_decide_reproduction` + 5 bildirim türü | ✅ |
| `services/production_runtime.py` | +678 — `launch_reproduction` / `run_reproduction` / `_run_reproduction` (Adım 1–21) + `_run_managed` brief'e `user_id`/`chat_id` | ✅ Salt ekleme; mevcut `recover()` dokunulmamış |
| `services/production_package_runtime.py` | +265 — `find_package` / `prepare_for_reproduction` / `load_full_production_context` + `archive()` kusur düzeltmesi | ✅ |
| `services/production_executor.py` | +18/−4 — event_logs artık EKLENİYOR (silinmiyor); `recover()` farklı PID rapor sıfırlama | ✅ Kayıt koruma yönünde düzeltme (15_KARAR §10) |

**Yeni dosyalar (bu geliştirmeye ait):** `handlers/yeniden_uretim.py`, `test_yeniden_uretim.py` (repo'da 16 tracked test_*.py emsali var), `RAPOR_YONETICI_YENIDEN_URETIM_PROSEDURU_18072026.md`, 24 adet `data/enforcement/CEE-20260718-*.json` (bugünkü test koşularının CEE kanıt kayıtları; repo'da 70 tracked CEE emsali var — mevcut pratikle uyumlu).

**Silinen dosya:** Yok.

**Geçici/test artığı denetimi:** `data/production_packages/` **boş** ✅ (proje kuralı), `data/pid_runtime_state.json` yok ✅, test dosyası kendi artıklarını temizliyor (satır 347–350) ✅.

**Bu geliştirmeye AİT OLMAYAN untracked dosyalar (commit DIŞI bırakılmalı):**
`vosk-model-small-*` (6 klasör), `hlk_ANTIGRAVITY/`, `hlk_PROJELER_02062026/Arşivdir-Kullanilmaz/`, `.railway-config-pull-7276/`, kök `requirements.txt`, `temp_docx_lines.txt`, `word_subs_krt.ass`, `create_krt_subtitle.py`, `generate_image.py`, `fix_i18n*.py` (3 adet), `faz5_robot_video.py`, `test_cikti.txt`, `test_telegram_formlar.py`, `hlk_PROJELER_02062026/README.md`, `hlk_PROJELER_02062026/requirements.txt`.

---

## 2. Python Doğrulaması

| Kontrol | Sonuç |
|---|---|
| `py_compile` (8 dosya: 6 değişen + handler + test) | ✅ OK |
| `main.py` import zinciri (handler kayıtları dahil, bot başlatılmadan) | ✅ OK — dil senkronu 8/8 |
| Çağrılan sembollerin varlığı (kaynak doğrulaması) | ✅ Tamamı mevcut |

Doğrulanan semboller: `ProductionState.RECOVERING/EXECUTING/TIMED_OUT/IDLE`, `_GC_PRODUCTION_TIMEOUT`, `_start_heartbeat`, `_on_task_done`; `hlk_runtime.boot/get_session/is_active/authorize_production/on_production_start/on_production_terminal/request_decision` + rationale `"Justifications"` anahtarı; `EventRecord` (12 alan birebir), `EECEventType.TASK_STARTED/CODE_COMPLETED`, `ExecutionPhase.EXECUTE/POST_CHECK`, `emit_event/listen/register_from_eec`; `EscalationReason.ALL_PROVIDERS_FAILED` + `escalate`; `production_executor.recover(pid)` + `ExecutorReport.to_dict/failed_tasks/errors`; `package_runtime.load/update_section/update_status/verify_integrity` + `service_usage` bölümü izinli listede; `pid_runtime.validate` (4 denetim: format+tarih+sıra+kayıt); `ProductionRequest/PipelineContext/set_context/clear_context/register_handlers`; `decision_engine.decide` + `DecisionPacket.to_dict/decision_id`; CEE `pre_check/enforce_post_check` imzaları.

**Kullanılmayan kod bulgusu:** `_GC_REPRODUCE_MAX_CANDIDATES` tanımlı ancak hiçbir yerde kullanılmıyor (aşağıda ⚠️-2).

---

## 3. Mimari Doğrulama

| Kural | Durum | Kanıt |
|---|---|---|
| Handler yalnızca yönlendirme yapıyor (MASTER-013) | ✅ | `handlers/yeniden_uretim.py`: yetki kontrolü + `find_package` çağrısı + anayasal onay ekranı + `launch_reproduction` devri. Hiçbir üretim/strateji/durum kararı yok; "bulunamadı" bildirimi dahi HLK Runtime `USER_NOTIFICATION` kararıyla üretiliyor |
| Runtime tüm teknik kararları alıyor | ✅ | `_decide_reproduction` (REPRODUCTION kategorisi) AR-002_84 karar tablosunun birebir uygulaması: ARCHIVED→REJECT, COMPLETED→REPLAY, FAILED/başarısız task→RETRY, READY/BUILDING/PRODUCING→RESUME, CREATED→START_AS_NEW, tanımsız/Runtime pasif→REJECT. Karar Decision History'ye ekleniyor |
| Production Package mimarisi korunuyor | ✅ | Yeni metotlar salt ekleme; kayıtlar append-only (`_append_package_list_section`, revision_history); PID/paket 1:1 korunuyor (yeni PID/paket üretilmiyor) |
| Workflow korunuyor | ✅ | 09/10/11 dosyaları ve workflow kodları değişmedi; WF-008/WF-017 + FEAT-014 atıfla kullanılıyor |
| State Engine korunuyor | ✅ | `utils/state_engine.py` değişmedi; yeni kullanıcı state'i yok (SE-007_3 dokunulmamış); olaylar STATE_VIDEO_PRODUCTION içinde |
| Event Collector korunuyor | ✅ | `execution_event_collector.py` değişmedi; mevcut `emit_event/listen` API'si kullanılıyor |
| Constitution Enforcement Engine etkilenmiyor | ✅ | `constitution_enforcement.py` değişmedi; akış mevcut PRE-CHECK/POST-CHECK'i çağırıyor |
| Mevcut üretim akışı bozulmuyor | ✅ | Normal akışta tek davranış değişikliği: (a) brief'e `user_id`/`chat_id` eklenmesi (salt ek alan), (b) executor `event_logs`'un silinmek yerine EKLENMESİ (kusur düzeltmesi — kayıt koruma yönünde), (c) `archive()` çalışır hale geldi (önceden her zaman çöküyordu). Regresyon testleri: 36/36 PASS (rapor) |
| AR-002_80 çelişkisi | ✅ Yok | Kapanışı tamamlanmış Runtime yeniden açılmıyor; aynı PID'ye yeni yürütme döngüsü başlatılıyor (AR-002_84 "Sınırlar ve Kapsam" bölümü bunu açıkça tanımlıyor) |

---

## 4. Railway Deploy Denetimi (canlı ortamdan salt okunur doğrulandı)

Servis: `HLK_01_asistan` — ● Online, repo `haluk4365/Antigravity`, environment `production`.

| Değişken | Canlı Değer | Durum |
|---|---|---|
| `TELEGRAM_ADMIN_USER_ID` | **TANIMSIZ** | 🚨 Deploy öncesi eklenmeli — tanımsızken `/yeniden` hiç kimse için çalışmaz (güvenli varsayılan; sistem bozulmaz ama canlı test imkânsız) |
| `GC_PACKAGE_STORAGE_DIR` | `/data/production_packages` | ✅ Volume üzerinde |
| `PID_STATE_DIR` | `/data` | ✅ Volume üzerinde |
| `GC_ESCALATION_DIR` | **TANIMSIZ** | ⚠️ Kod varsayılanı `data/escalations` → geçici container FS → redeploy'da kaybolur. Öneri: `/data/escalations` |
| `GC_EXECUTOR_STATE_DIR` | `/data` | ✅ Checkpoint kayıtları kalıcı |
| `GC_CEE_REPORT_DIR` | `/data/enforcement` | ✅ CEE kayıtları kalıcı |
| `GC_REPRODUCE_SEARCH_LIMIT` / `MAX_CANDIDATES` | Tanımsız | ✅ Sorun değil — kod varsayılanları (20/5) GC dosyasıyla aynı |
| `TELEGRAM_TOKEN`, `TELEGRAM_ALLOWED_USERS`, `ENV=production`, sağlayıcı anahtarları (Higgsfield/Kie/Fal/ElevenLabs/Hedra/Descript/OpenAI) | Tanımlı | ✅ |

Not: Lokal `.env` dosyasında da `TELEGRAM_ADMIN_USER_ID` yok — lokal test botu için de eklenmeli.

---

## 5. Kalıcı Veri Doğrulaması

Volume: `hlk_01_asistan-volume` → `/data` (kullanım 0.1 / 4.9 GB). Railway volume'ları deploy'dan etkilenmez.

| Veri | Konum (canlı) | Deploy sonrası korunur mu? |
|---|---|---|
| Production Package | `/data/production_packages/*.json` | ✅ |
| PID Runtime State | `/data/pid_runtime_state.json` | ✅ |
| Digital Asset kayıtları | Package içi bölümler (`digital_assets`) — `/data/production_packages` | ✅ |
| Event kayıtları | Package `event_logs` + `/data/enforcement` (CEE) | ✅ |
| Karar kayıtları | Package `decision_history` (+ CEE justification) | ✅ |
| Executor checkpoint | `/data` (`GC_EXECUTOR_STATE_DIR`) | ✅ |
| Eskalasyon kayıtları | `data/escalations` (container FS) | ❌ → ⚠️-1 (env eklenerek çözülür) |

**Deploy sonrası veri kaybı riski:** Eskalasyon kayıtları dışında YOK. Bu risk bu geliştirmeyle gelmedi (mevcut canlı davranış), ancak yeniden üretim başarısızlık yolu eskalasyon yazdığı için canlı test öncesi kapatılması önerilir.

---

## 6. Geriye Dönük Uyumluluk

- **Migration GEREKMİYOR.** `ProductionPackage.from_dict` tüm alanları varsayılanlarla tolere eder; eski paketler yeni kodla olduğu gibi yüklenir. Yeni kod eski pakete yalnızca EKLEME yapar (revision_history, event_logs, decision_history, `production_type="reproduction"`).
- **PID-20260718-0001:** Railway'de üretilmiş bir PID'dir; paket ve PID kaydı `/data` volume üzerindedir ve volume deploy'dan etkilenmediği için **yeniden üretilebilir durumda kalır**. Lokal ortamda bu PID mevcut değildir (ortama özgü kayıt — bilinen sınır #2); lokalden birebir doğrulanamaz, kesin doğrulama canlıda yapılır (Bölüm 8).
- **Eski paketlerde `brief.chat_id` yok** → teslim/bildirim Yönetici sohbetine düşer (kodda güvenli fallback mevcut: `brief.chat_id → delivery_info.chat_id → admin_chat_id`). Bilinen sınır #1; PID-20260718-0001 için geçerli olacaktır.
- **Rollback uyumluluğu:** Yeni kodun yazdığı paket alanları eski kod tarafından da okunabilir (ek alanlar eski `from_dict`'te yok sayılır ya da varsayılanla okunur) → geri dönüşte veri bozulmaz.

---

## 7. Rollback Hazırlığı

- **Yöntem 1 (önerilen):** Railway Dashboard → Deployments → önceki çalışan deployment → **Redeploy** (kod anında eski sürüme döner; volume verisine dokunulmaz).
- **Yöntem 2:** `git revert <deploy_commit>` + push → otomatik yeni deploy.
- Son çalışan sürüm bellidir: `7d738d7` ("deploy: 2026-07-18 — AR-002_82 + AR-002_83 eklendi") — şu an canlıda koşan kod.
- **Veri kaybı riski:** Yok — tüm kalıcı veri volume üzerinde; her iki yöntem de volume'a dokunmaz.
- Geliştirme salt-ekleme olduğundan rollback'te şema/uyumsuzluk sorunu oluşmaz (Bölüm 6).

---

## 8. Canlı Test Hazırlığı (PID-20260718-0001) — üretim BAŞLATILMADI

| Kontrol | Durum |
|---|---|
| Package bulunabiliyor mu? | ⚠️ Lokalden kesin doğrulanamadı (`railway ssh` SSH anahtarı gerektiriyor; loglarda PID görünmedi). Volume + env doğru olduğundan paket canlıda üretildiyse yerindedir. Kesin doğrulama deploy sonrası sıfır riskli smoke test ile yapılır (aşağıda) |
| Runtime yükleyebiliyor mu? | ✅ Mekanizma doğrulandı: `find_package` → PID doğrulama (4 denetim) → `load` → bilgi kartı. Tam zincir testi 7/7 PASS |
| Yeniden üretim prosedürü başlayabiliyor mu? | ✅ Kod hazır; ANCAK `TELEGRAM_ADMIN_USER_ID` canlıda tanımlanmadan `/yeniden` çalışmaz (🚨-1) |
| Telegram bildirimi çalışacak durumda mı? | ✅ `TELEGRAM_TOKEN` canlıda tanımlı; bildirimler HLK Runtime USER_NOTIFICATION kararıyla üretiliyor. Eski pakette kullanıcı adresi olmadığından kullanıcı bildirimi Yönetici sohbetine düşecek (bilinen sınır #1) |

**Önerilen sıfır riskli canlı smoke test (üretim başlatmadan):**
1. Railway'e `TELEGRAM_ADMIN_USER_ID` eklendikten ve deploy tamamlandıktan sonra: `/yeniden PID-20260718-0001`
2. Bilgi kartı gelirse → paket bulundu + Runtime yükledi (Adım "bulma/yükleme" canlıda doğrulanmış olur)
3. **[İptal]** butonuna basılır → hiçbir üretim başlatılmaz (AR-002_84 İptal yolu)
4. Gerçek yeniden üretim, Proje Yöneticisi kararıyla ayrıca [Evet, Başlat] ile yapılır.

---

## 9. Git Hazırlığı (HENÜZ ÇALIŞTIRILMADI)

### 🚨 Kritik yol disiplini — büyük/küçük harf tuzağı

Diskteki klasör adı `HLK_01_asistan`, git index'teki yol `hlk_01_asistan` (core.ignorecase=true). `git add --dry-run` ile kanıtlandı: **git, yazılan yolu birebir kaydeder.** Büyük harfli yol veya `git add .` / `git add -A` kullanılırsa repo'da ikinci bir `HLK_01_asistan/` ağacı oluşur; Railway (Linux, büyük/küçük harf duyarlı) checkout'unda `handlers/yeniden_uretim.py` servis kökünün DIŞINA düşer → `main.py` import hatasıyla **bot açılışta çöker**. Tüm add komutları aşağıdaki gibi KÜÇÜK harfli tam yolla verilmelidir.

Kalıcı çözüm (önerilir, deploy öncesi): diskteki klasörü index ile aynı case'e çevir:
```powershell
Rename-Item "C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk_PROJELER_02062026\HLK_01_asistan" "hlk_01_asistan"
```

### Önerilen sıra (repo kökünden)

```powershell
# 1) Değişen dosyalar (ANA YASA + kod)
git add "hlk_PROJELER_02062026/hlk_01_asistan/ANA YASA/01_Global_Configuration.md" `
        "hlk_PROJELER_02062026/hlk_01_asistan/ANA YASA/03_Architecture_Rules.md" `
        "hlk_PROJELER_02062026/hlk_01_asistan/ANA YASA/14_OLAY_KAYIT_MERKEZI.md" `
        "hlk_PROJELER_02062026/hlk_01_asistan/config/settings.py" `
        "hlk_PROJELER_02062026/hlk_01_asistan/main.py" `
        "hlk_PROJELER_02062026/hlk_01_asistan/services/hlk_runtime.py" `
        "hlk_PROJELER_02062026/hlk_01_asistan/services/production_executor.py" `
        "hlk_PROJELER_02062026/hlk_01_asistan/services/production_package_runtime.py" `
        "hlk_PROJELER_02062026/hlk_01_asistan/services/production_runtime.py"

# 2) Yeni dosyalar (KÜÇÜK harf yol — zorunlu)
git add "hlk_PROJELER_02062026/hlk_01_asistan/handlers/yeniden_uretim.py" `
        "hlk_PROJELER_02062026/hlk_01_asistan/test_yeniden_uretim.py" `
        "hlk_PROJELER_02062026/hlk_01_asistan/RAPOR_YONETICI_YENIDEN_URETIM_PROSEDURU_18072026.md" `
        "hlk_PROJELER_02062026/hlk_01_asistan/RAPOR_DEPLOY_HAZIRLIK_DENETIMI_18072026.md"

# 3) CEE kanıt kayıtları (24 adet — dosya adları tek tek, küçük harf yolla)
Get-ChildItem "hlk_PROJELER_02062026\hlk_01_asistan\data\enforcement\CEE-20260718-*.json" |
  ForEach-Object { git add "hlk_PROJELER_02062026/hlk_01_asistan/data/enforcement/$($_.Name)" }

# 4) DOĞRULAMA (zorunlu): staged listede büyük harfli yol OLMAMALI — çıktı boş olmalı
git diff --cached --name-only | Select-String -CaseSensitive "HLK_01_asistan"

# 5) Commit
git commit -m "feat: AR-002_84 Yonetici Yeniden Uretim Proseduru — /yeniden komutu, REPRODUCTION karari, OLAY-107/108/109"

# 6) Push (Railway otomatik deploy tetikler) — TELEGRAM_ADMIN_USER_ID Railway'e eklendikten SONRA
git push origin main
```

Alakasız untracked dosyalar (Bölüm 1'deki liste) bu commit'e DAHİL EDİLMEZ.

---

---

# SONUÇ

## ✅ Hazır

1. **Kod ve mimari:** Tüm değişiklikler salt-ekleme; Handler yalnızca yönlendiriyor, tüm kararlar HLK Runtime'da (MASTER-013); Production Package / Workflow / State Engine / Event Collector / CEE korunuyor; mevcut üretim akışında regresyon yok (36/36 regresyon + 7/7 yeni test PASS).
2. **Python:** Syntax 8/8 OK, `main.py` import zinciri OK, çağrılan tüm semboller kaynak doğrulamasından geçti; kırık çağrı yok.
3. **ANA YASA:** AR-002_84 + OLAY-107/108/109 + 2 GC parametresi salt-ekleme olarak işlenmiş; mevcut maddeler değişmemiş. (MASTER-001 gereği anayasa değişikliğinin yürürlüğü Proje Yöneticisi onayına tabidir — bu deploy talimatı o onayın kendisidir.)
4. **Kalıcı veri:** Railway volume `/data` aktif; paketler, PID state, checkpoint ve CEE kayıtları deploy sonrası korunur. PID-20260718-0001 volume üzerinde olduğundan deploy ile silinmez.
5. **Geriye dönük uyumluluk:** Migration gerekmiyor; eski paketler yüklenebilir; rollback şema-güvenli.
6. **Rollback:** Railway "Redeploy previous" veya `git revert` ile anında geri dönüş; veri kaybı riski yok; son çalışan sürüm `7d738d7`.
7. **Test artıkları:** `data/production_packages` boş; PID state artığı yok.

## ⚠️ Düzeltilmesi Gerekenler

1. **`GC_ESCALATION_DIR` Railway'de tanımsız** → eskalasyon kayıtları geçici container diskine yazılıyor, redeploy'da kaybolur. Deploy öncesi Railway'e `GC_ESCALATION_DIR=/data/escalations` eklenmesi önerilir (yeniden üretim başarısızlık yolu eskalasyon üretir).
2. **`GC_REPRODUCE_MAX_CANDIDATES` kodda kullanılmıyor** (yalnızca tanımlı) ve `find_package` eşleşme skoru hesaplayıp sıralamada kullanmıyor (en güncel aday dönüyor). GC/AR-002_84 metniyle küçük kod-anayasa uyumsuzluğu (MASTER-003). Blocker değil; ayrı küçük bir düzeltme görevi olarak kayda alınmalı.
3. **REPLAY yolunda** `final_video`/`delivery_info` sıfırlanmadan önce eski değer `revision_history`'ye kopyalanmıyor (dijital varlık kayıtları korunuyor; yalnızca güncel işaretçi alanları). İyileştirme önerisi — ilk canlı test RETRY yolu olduğundan bu testi etkilemez.
4. **Lokal `.env`'e `TELEGRAM_ADMIN_USER_ID` eklenmeli** (lokal test botunda da prosedürün çalışabilmesi için).
5. **Commit kapsamı:** Bölüm 1'deki alakasız untracked dosyalar bu deploy commit'ine kesinlikle dahil edilmemeli.

## 🚨 Kritik Sorunlar

1. **`TELEGRAM_ADMIN_USER_ID` Railway'de TANIMSIZ.** Bu değişken eklenmeden deploy edilirse sistem bozulmaz (güvenli varsayılan) ancak `/yeniden` hiç kimse için çalışmaz → canlı test yapılamaz. **Deploy öncesi Railway'e eklenmesi ZORUNLU** (Yöneticinin Telegram kullanıcı ID'si).
2. **Git dizin büyük/küçük harf tuzağı.** Diskte `HLK_01_asistan` / index'te `hlk_01_asistan`. `git add .` veya büyük harfli yolla add yapılırsa Railway'de bot **açılışta ImportError ile çöker**. Yeni dosyalar yalnızca Bölüm 9'daki küçük harfli tam yollarla eklenmeli ve 4. adımdaki doğrulama komutu boş dönmeden push YAPILMAMALI.

## 📋 Deploy Öncesi Son Kontrol Listesi

- [ ] Railway → Variables: `TELEGRAM_ADMIN_USER_ID=<Yönetici Telegram ID>` eklendi
- [ ] Railway → Variables: `GC_ESCALATION_DIR=/data/escalations` eklendi (önerilen)
- [ ] Lokal `.env`'e `TELEGRAM_ADMIN_USER_ID` eklendi (lokal test için)
- [ ] (Önerilen) Disk klasörü `HLK_01_asistan` → `hlk_01_asistan` olarak yeniden adlandırıldı
- [ ] `git add` yalnızca Bölüm 9 listesindeki dosyalarla, KÜÇÜK harfli yollarla yapıldı
- [ ] Doğrulama: `git diff --cached --name-only | Select-String -CaseSensitive "HLK_01_asistan"` → çıktı BOŞ
- [ ] Alakasız untracked dosyaların staged olmadığı görüldü (`git status`)
- [ ] Commit + push → Railway deploy'un başarıyla tamamlandığı görüldü (● Online)
- [ ] Sıfır riskli canlı smoke test: `/yeniden PID-20260718-0001` → bilgi kartı → **[İptal]** (üretim başlatılmaz)
- [ ] Gerçek yeniden üretim yalnızca Proje Yöneticisi kararıyla [Evet, Başlat] ile

---

⚠️ DÜZELTME GEREKLİ
