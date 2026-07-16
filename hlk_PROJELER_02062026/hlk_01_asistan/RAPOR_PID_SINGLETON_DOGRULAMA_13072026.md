# PID Singleton Doğrulama Raporu

**Doğrulama Tarihi:** 13 Temmuz 2026
**İncelenen Dosya:** `services/pid_runtime.py` (668 satır)
**İnceleme Kapsamı:** PID Singleton mimarisi — multi-worker, persistence, anayasal uyum

---

## 1. Singleton Türü

**Process-bazlı Singleton.**

### Gerekçe

```python
# satır 656
pid_runtime = PIDRuntime()
```

Bu modül-level global değişken, Python'ın modül import mekanizmasına dayanır:

- Python'da her modül `sys.modules` içinde **process başına bir kez** yüklenir.
- `from services.pid_runtime import pid_runtime` çağrısı her yapıldığında aynı `PIDRuntime` instance'ı döner — **ama yalnızca aynı Python process'i içinde.**
- PIDRuntime sınıfının kendisi singleton değildir — `PIDRuntime()` çağırarak yeni instance oluşturulabilir (nitekim test kodunda `new_runtime = PIDRuntime()` ile restart simülasyonu yapılmıştır).
- `asyncio.Lock` (satır 165) yalnızca **aynı process içindeki coroutine'leri** sıralar.

Bu yapı **Application-bazlı** veya **Instance-bazlı** değildir. Her worker process kendi `pid_runtime` singleton'ına, kendi `_daily_counters` dict'ine ve kendi `_pid_registry` dict'ine sahiptir.

---

## 2. Multi-Worker Güvenliği

**FAIL**

### Gerekçe

Railway Production ortamında Multi-Worker / Horizontal Scaling senaryosunda:

**EVET — iki farklı worker aynı anda aynı PID'yi üretebilir.**

Senaryo:

```
Worker A                              Worker B
─────────                             ─────────
process başlar                        process başlar
_load_state() → sayaç=5               _load_state() → sayaç=5
generate() çağrılır                   generate() çağrılır
  lock.acquire() (process içi)          lock.acquire() (process içi)
  _next_sequence() → 6                 _next_sequence() → 6
  PID=PID-20260713-0006                PID=PID-20260713-0006  ← DUPLICATE!
  _save_state() → dosyaya yazar         _save_state() → Worker A'nın yazdığını EZER
```

Kök nedenler:

1. **`asyncio.Lock` process'ler arası çalışmaz.** Yalnızca aynı event loop içindeki coroutine'leri sıralar. Farklı process'lerdeki kilitler birbirinden tamamen bağımsızdır.

2. **`_daily_counters` her process'te ayrıdır.** Worker A'nın `_daily_counters['20260713'] = 6` yapması Worker B'nin dict'ini etkilemez.

3. **`_load_state()` yalnızca `__init__()`'te çağrılır (satır 168).** Çalışma anında diğer worker'ların ürettiği PID'leri görmek için periyodik reload yoktur. Worker B, Worker A'nın ürettiği PID'leri ancak restart olursa görebilir.

4. **Dosya persistence'ında last-write-wins yarışı vardır.** İki worker aynı `data/pid_runtime_state.json` dosyasına yazar. `replace()` atomik olsa da, okuma-değiştirme-yazma (read-modify-write) döngüsü atomik değildir.

---

## 3. PID Tekilliği — Koruma Mekanizması

PID tekilliği **iki katmanlı** korunur, ancak her ikisi de **process-sınırlıdır:**

### Katman 1: Process Belleği (aynı process içinde geçerli)

- `_pid_registry: dict[str, PIDRecord]` (satır 158): Oluşturulan tüm PID'ler burada saklanır
- `generate()` içinde duplicate kontrolü: `if pid in self._pid_registry` (satır 200)
- `asyncio.Lock` ile aynı process içindeki eşzamanlı generate çağrıları atomiktir
- **Sınır:** Yalnızca bu process'in kendi PID'lerini bilir. Başka process'lerin PID'lerini görmez.

### Katman 2: Dosya Persistence (aynı process'te restart sonrası geçerli)

- `_save_state()` (satır 486): Her generate/deactivate sonrası `data/pid_runtime_state.json` dosyasına yazar
- `_load_state()` (satır 519): `__init__()`'te yalnızca bir kez çağrılır, diski okur
- Atomik yazım: önce `.tmp` dosyasına yaz, sonra `replace()` (satır 513-515)
- **Sınır:** Çalışma anında diğer process'lerin yazdığı güncellemeleri görmez. Dosya paylaşımlı tek kaynaktır ancak last-write-wins yarışına açıktır.

### Kalıcı kayıt sistemi var mı?

**Evet — ancak yalnızca single-process için güvenilir.** Dosya tabanlı JSON persistence mevcuttur, ancak multi-process senkronizasyonu yoktur. Gerçek bir veritabanı (PostgreSQL, Redis, vb.) veya dağıtık kilit mekanizması kullanılmamıştır.

---

## 4. Restart Persistence — Gerçek mi, Simülasyon mu?

**Gerçek persistence mevcuttur.**

### Kanıtlar

**1. Dosya yazma (`_save_state`, satır 486-517):**
```python
_PID_STATE_DIR.mkdir(parents=True, exist_ok=True)
state = {
    "daily_counters": dict(self._daily_counters),
    "pid_registry": [r.to_dict() for r in self._pid_registry.values()],
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "gc_prefix": _GC_PID_PREFIX,
    "gc_sequence_length": _GC_PID_SEQUENCE_LENGTH,
}
tmp_path = _PID_STATE_FILE.with_suffix(".tmp")
tmp_path.write_text(json.dumps(state, ...), encoding="utf-8")
tmp_path.replace(_PID_STATE_FILE)  # atomik rename
```

**2. Dosya okuma (`_load_state`, satır 519-564):**
```python
if not _PID_STATE_FILE.exists():
    return  # boş state ile başla
raw = _PID_STATE_FILE.read_text(encoding="utf-8")
state = json.loads(raw)
# sayaçları geri yükle
for date_key, count in loaded_counters.items():
    self._daily_counters[date_key] = int(count)
# PID kayıtlarını geri yükle
for entry in loaded_registry:
    record = PIDRecord.from_dict(entry)
    self._pid_registry[record.pid] = record
```

**3. Test kanıtı (daha önce çalıştırıldı):**
```
=== TEST 9: Restart simulasyonu (persistence) ===
  Restart oncesi: 22 PID, counters={'20260713': 22}
  Restart sonrasi: 22 PID, counters={'20260713': 22}
  Restart sonrasi PID=PID-20260713-0023 seq=23 (beklenen=23) OK
```

Bu test, yeni bir `PIDRuntime()` instance'ı oluşturarak restart'ı simüle etti. Yeni instance:
- Diskteki state dosyasından 22 PID kaydını geri yükledi
- Günlük sayacı 22 olarak geri yükledi
- Bir sonraki PID'yi 23. sıradan üretti → duplicate önlendi

**Ancak önemli sınırlama:** Bu test **single-process** ortamda yapıldı. Multi-worker senaryoda iki worker aynı dosyaya yazdığında last-write-wins yarışı oluşur ve persistence tek başına duplicate'i önleyemez.

---

## 5. Anayasal Uyum — Madde Madde Doğrulama

### MASTER-001 — ANA YASA Üstünlüğü

| Gereklilik | Durum | Kanıt |
|---|---|---|
| PID formatı AR-002_57'ye uygun | ✅ UYGUN | `_build_pid()` (satır 392): `f"{_GC_PID_PREFIX}-{date_part}-{seq_str}"` → `PID-YYYYMMDD-NNNN` |
| GC parametreleri kullanılır | ✅ UYGUN | satır 60-63: `os.getenv("GC_PID_PREFIX", "PID")` vb. |
| Hardcoded değer yok | ✅ UYGUN | Tüm sabitler GC'den veya env'den okunur |
| Karar hiyerarşisine uygun | ✅ UYGUN | MASTER → GC → AR → Kod sırası korunur |

**Sonuç: UYGUN** (single-process senaryoda)

---

### MASTER-003 — ANA YASA/Kod Uyumluluk Denetimi

| Gereklilik | Durum | Kanıt |
|---|---|---|
| AR-002_57 tüm maddeleri implemente | ✅ UYGUN | Format, tekillik, merkeziyet, zorunluluk, silinemezlik |
| AR-002_71 tüm adımları implemente | ✅ UYGUN | 6 adımın tamamı (Adım 1-6) |
| Denetlenebilir | ✅ UYGUN | `validate()` ile 4 denetim, `get_stats()` ile izleme |

**Sonuç: UYGUN** (single-process senaryoda)

---

### MASTER-004 — Karar Mekanizması ve Kural Otoritesi

| Gereklilik | Durum | Kanıt |
|---|---|---|
| PID Runtime karar vermez | ✅ UYGUN | Docstring (satır 17): "Karar vermez (MASTER-004)" |
| Yalnızca runtime katmanı | ✅ UYGUN | PID üretir, doğrular, döndürür — seçim/karar yapmaz |
| Decision Engine yerine geçmez | ✅ UYGUN | Sınıf tasarımı: veri + doğrulama, karar mantığı içermez |

**Sonuç: UYGUN**

---

### AR-002_57 — PID Mimari Standardı

| Gereklilik | Single-Process | Multi-Worker |
|---|---|---|
| Format: `PID-YYYYMMDD-NNNN` | ✅ UYGUN | ✅ UYGUN |
| Tekillik: "Aynı PID birden fazla üretim için kullanılamaz" | ✅ UYGUN (`_pid_registry` + lock) | ❌ **İHLAL** (iki worker aynı PID'yi üretebilir) |
| Merkeziyet: "Hiçbir modül kendi PID'sini oluşturamaz" | ✅ UYGUN (tek singleton) | ❌ **İHLAL** (her worker kendi PID'sini üretir — merkezi değil) |
| Değiştirilemezlik: "PID değiştirilemez" | ✅ UYGUN (`PIDRecord.pid` sabit) | ✅ UYGUN |
| Silinemezlik: "PID silinemez" | ✅ UYGUN (`deactivate()` pasif yapar) | ✅ UYGUN |
| Zorunluluk: "PID alanı zorunlu" | ✅ UYGUN | ✅ UYGUN |

**Sonuç: Single-process'te UYGUN, Multi-worker'da Tekillik ve Merkeziyet İHLALİ var.**

---

### AR-002_71 — PID Runtime Architecture

| Adım | Gereklilik | Durum |
|---|---|---|
| Adım 1 | PID oluşturma koşullarının doğrulanması | ✅ `validate()` ile 4 denetim |
| Adım 2 | GC parametrelerinin kullanılması | ✅ `_GC_PID_PREFIX`, `_GC_PID_SEQUENCE_LENGTH` vb. |
| Adım 3 | Benzersiz PID üretilmesi | ✅ Single-process / ❌ Multi-worker |
| Adım 4 | PID'nin Production Runtime'a bağlanması | ✅ `get_record()` ile erişim |
| Adım 5 | PID oluşturma Event'i | ⚠️ PID Runtime Event üretmez (görev kapsamı dışı — AR-002_71 Adım 5 caller sorumluluğunda) |
| Adım 6 | PID'nin Production Package referansı olarak kullanılması | ⚠️ Production Package bu görev kapsamı dışında |

**Sonuç: Single-process'te UYGUN.**

---

## 6. Özet Değerlendirme

| Kriter | Sonuç |
|---|---|
| **Singleton Türü** | Process-bazlı |
| **Multi-Worker Güvenliği** | **FAIL** — İki worker aynı PID'yi üretebilir |
| **Race Condition Güvenliği** (aynı process) | PASS — `asyncio.Lock` ile atomik |
| **Race Condition Güvenliği** (farklı process) | **FAIL** — Process'ler arası senkronizasyon yok |
| **Persistence** | Gerçek (dosya tabanlı JSON, atomik yazım) |
| **Duplicate PID Riski** (single-process) | **Yok** |
| **Duplicate PID Riski** (multi-worker) | **Var** — last-write-wins dosya yarışı |
| **Anayasal Uyum** (single-process) | **PASS** |
| **Anayasal Uyum** (multi-worker) | **FAIL** — AR-002_57 Tekillik ve Merkeziyet ihlali |

---

## 7. Kritik Riskler

### Risk 1 — Multi-Worker Duplicate PID (KRİTİK)

Railway'de 2+ worker çalıştığında aynı PID iki farklı üretime atanabilir. Bu, AR-002_57'nin doğrudan ihlalidir.

**Etki:** İki farklı müşterinin üretimi aynı PID'yi alır. Production Package'ler çakışır, event kayıtları karışır, dijital varlıklar yanlış üretime bağlanır.

### Risk 2 — Dosya Last-Write-Wins Yarışı (YÜKSEK)

İki worker aynı `pid_runtime_state.json` dosyasına aynı anda yazdığında, son yazan öncekinin state'ini ezer. Sayaç değerleri kaybolabilir.

### Risk 3 — State Dosyası Bozulması (ORTA)

`_save_state()` exception durumunda sessizce log basar ve devam eder (satır 516-517). Bu, state dosyası bozulduğunda veya disk dolu olduğunda PID üretiminin durmamasını sağlar — ancak aynı zamanda persistence olmadan PID üretilmeye devam edilmesine yol açar. Process restart olursa, kaydedilememiş PID'ler kaybolur ve duplicate riski artar.

### Risk 4 — `_load_state()` Tek Seferlik Çağrı (ORTA)

`_load_state()` yalnızca `__init__()`'te çağrılır (satır 168). Çalışma anında başka bir worker'ın ürettiği PID'leri görmek için mekanizma yoktur. Bu, dosya persistence'ının multi-worker senaryoda etkisiz kalmasının ana nedenidir.

---

## 8. Sonuç

**Bu implementasyon, tek worker (single-process) Production ortamına alınabilir. Multi-worker / Horizontal Scaling ortamına alınamaz.**

### Gerekçe

**Alınabilir olduğu senaryo (single-worker):**
- `asyncio.Lock` aynı process içindeki tüm race condition'ları önler
- Dosya persistence'ı restart sonrası duplicate PID üretilmesini engeller
- AR-002_57 (Tekillik, Merkeziyet, Değiştirilemezlik, Silinemezlik) single-process'te tam olarak sağlanır
- AR-002_71 çalışma sırası eksiksiz uygulanmıştır
- MASTER-001, MASTER-003, MASTER-004 ile uyumludur

**Alınamaz olduğu senaryo (multi-worker):**
- `asyncio.Lock` process'ler arası çalışmaz
- `_daily_counters` ve `_pid_registry` her process'te bağımsızdır
- Dosya persistence'ı last-write-wins yarışına açıktır
- İki worker aynı anda aynı PID'yi üretebilir → AR-002_57 Tekillik Kuralı doğrudan ihlal
- AR-002_57 Merkeziyet Kuralı ihlal: "PID yalnızca HLK tarafından merkezi olarak oluşturulur" — her worker kendi PID'sini üretmektedir

### Multi-Worker için Gereken (bu görev kapsamı dışında)

Bu görev kapsamında implementasyon değişikliği yapılmamıştır. Ancak multi-worker güvenliği için ihtiyaç duyulanlar referans olarak belirtilmiştir:

1. Process'ler arası kilit (Redis lock, PostgreSQL advisory lock, veya dosya tabanlı `fcntl.flock`)
2. `_load_state()`'in her `generate()` öncesi çağrılması (diğer worker'ların PID'lerini görmek için)
3. Veya gerçek bir veritabanı ile `INSERT ... ON CONFLICT` veya atomik `UPDATE counter SET value = value + 1 WHERE date = ? RETURNING value`

Bunlar yeni özellik/mimari değişikliği kapsamına girer ve bu doğrulama görevinin dışındadır.
