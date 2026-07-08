# HLK Davranış Modeli (Behavior Model) Analiz Raporu

**Tarih:** 3 Temmuz 2026
**Kapsam:** ANA YASA vs Mevcut Implementasyon
**Tür:** Mimari Analiz — Kod önerisi içermez

---

## 1. HLK'nın Düşünme Modeli Nasıl Olmalıdır?

ANA YASA'ya göre HLK'nın düşünme modeli **7 aşamalı bir bağlamsal karar döngüsüdür:**

```
1. BAĞLAM TESPİTİ
   "Şu anda hangi Workflow içerisindeyim?"
   "Hangi State içerisindeyim?"
   "Hangi Scene içerisindeyim?"
   ↓
2. ANA YASA SORGULAMA
   "Bu bağlam için ANA YASA benden ne istiyor?"
   → İlgili tüm MASTER, AR, OR, QR, MR, SE, FD maddelerini bul
   ↓
3. RUNTIME GÖZLEM
   "Runtime'da gerçekten ne oldu?"
   → Cleanup çalıştı mı? Hangi event'ler tetiklendi? State değişti mi?
   ↓
4. KARŞILAŞTIRMA
   "ANA YASA'nın istediği ile Runtime'da olan arasındaki fark nedir?"
   ↓
5. KARAR
   "PASS mı FAIL mi?"
   ↓
6. KAYIT
   "Bu kararı Olay Kayıt Merkezi'ne yaz. LAC'ta göster."
   ↓
7. AKSİYON
   "FAIL ise Executor'a geri gönder. PASS ise akışa devam et."
```

**HLK hiçbir zaman şu şekilde düşünmez:**
- "Cleanup kontrol edeceğim" ❌
- "Button kontrol edeceğim" ❌
- "Video kontrol edeceğim" ❌

**HLK yalnızca şu şekilde düşünür:**
- "SAHNE-02'deyim → ANA YASA SAHNE-02 için ne diyor? → Runtime'da ne oldu? → Karşılaştır → Karar ver" ✅

Bu düşünme modelinin anayasal dayanağı:

| İlke | ANA YASA Referansı |
|---|---|
| HLK tek karar vericidir | **MASTER-004**: "HLK projesinde karar veren, yöneten ve nihai kararı oluşturan tek yapı HLK'dır." |
| Katmanlar karar vermez, yönlendirir | **MASTER-004**: "Bu katmanların görevi, HLK'nın karar mekanizmasını anayasal kurallar çerçevesinde yönlendirmek, sınırlandırmak ve doğrulamaktır." |
| Kod ANA YASA'ya uymak zorundadır | **MASTER-001**: "Hiçbir teknik tercih, hiçbir workaround, hiçbir kod parçası bu belgede tanımlanan kuralların üzerinde değildir." |
| Her karar denetlenmelidir | **MASTER-003**: "ANA YASA Güncellendi ≠ Kod Güncellendi" |
| Karar bağlamı değişirse yeniden değerlendir | **AR-002_22** (Feedback Loop): "Her karar, uygulandıktan sonra sistem tarafından değerlendirilmelidir." |

---

## 2. Bugünkü Implementasyon Bu Modele Uyuyor Mu?

### Kısmen uyuyor. Temel yapı taşları mevcut, ancak karar akışı ters yönde çalışıyor.

**Mevcut durumun çalışma şekli:**

```
Handler (Python kodu)
  ↓  cleanup_ok = True/False (KOD karar veriyor)
  ↓  flow_ok = True (KOD karar veriyor)
  ↓  state_ok = True (KOD karar veriyor)
  ↓
CEE.post_check(cleanup_ok, flow_ok, state_ok, ...)
  ↓  CEE sadece boolean'ları EnforcementReport'a çeviriyor
  ↓  (CEE KARAR VERMİYOR — Handler'ın kararını onaylıyor)
```

**ANA YASA'nın istediği çalışma şekli:**

```
Handler (Python kodu)
  ↓  runtime_context = {"state": "...", "scene": "...", "cleanup": {...}, ...}
  ↓  (KOD sadece GÖZLEM yapıyor — karar vermiyor)
  ↓
CEE (HLK'nın karar mekanizması)
  ↓  1. Workflow'u bul
  ↓  2. State'i bul
  ↓  3. ANA YASA'dan ilgili kuralları yükle
  ↓  4. Runtime gözlemleriyle karşılaştır
  ↓  5. PASS / FAIL KARARINI VER
  ↓  (KARAR CEE'ye ait — Handler sadece veri sağlar)
```

### Temel Fark

| Boyut | Mevcut Implementasyon | ANA YASA'nın İstediği |
|---|---|---|
| **Karar veren** | Handler (Python kodu) | CEE (HLK Karar Mekanizması) |
| **Handler'ın rolü** | Karar verir, boolean üretir | Gözlem yapar, veri toplar |
| **CEE'nin rolü** | Boolean'ları rapor formatına çevirir | Kuralları yükler, karşılaştırır, KARAR VERİR |
| **Kural kaynağı** | Handler içinde hardcoded | ANA YASA .md dosyaları |
| **Yeni kural ekleme** | Python kodu değişir | Sadece .md güncellenir |

---

## 3. Uymuyorsa Neden Uymuyor?

### 3.1 Karar Akışı Ters Yönde

Mevcut implementasyonda **karar Handler'da başlıyor, CEE'de bitiyor.** Oysa ANA YASA'ya göre **karar CEE'de başlamalı ve CEE'de bitmeli.** Handler sadece gözlem verisi sağlamalı.

**Kanıt (koddan):**
```python
# handlers/start.py — MEVCUT DURUM (HANDLER KARAR VERİYOR)
sahne2_report = constitution_enforcement.post_check(
    code_anayasa_ok=True,        # ← Handler "Evet, anayasaya uygun" DİYOR
    flow_ok=True,                 # ← Handler "Evet, flow doğru" DİYOR
    state_ok=True,                # ← Handler "Evet, state doğru" DİYOR
    operational_ok=cleanup_ok,    # ← Handler cleanup sonucunu HESAPLIYOR
    architecture_ok=True,         # ← Handler "Evet, mimari doğru" DİYOR
    runtime_ok=(language is not None),  # ← Handler runtime'ı DEĞERLENDİRİYOR
)
```

Handler 6 karar veriyor. CEE sadece formatlıyor. Bu, MASTER-004'ün "karar veren tek yapı HLK'dır" ilkesine aykırıdır. Handler bir Python fonksiyonudur — HLK değildir.

### 3.2 Generic Validator Bağlamdan Bağımsız Çalışıyor

Mevcut `validate_runtime()` metodu, tüm kuralları `runtime_context`'teki anahtarlara göre eşleştiriyor. Örneğin `cleanup` anahtarı varsa, **tüm Cleanup kategorisindeki kuralları** yüklüyor — o anki State veya Workflow'a bakmaksızın.

**Sonuç:** SAHNE-02'de buton olmaması normaldir (link isteği serbest metindir). Ancak Generic Validator, Index'teki tüm BUTTON kurallarını yükleyip "0 buton → FAIL" üretiyor. Bu **bağlamdan bağımsız** bir denetimdir.

**Doğrusu:** Generic Validator önce "Hangi State'teyim?" diye sormalı, sonra **sadece o State için geçerli olan kuralları** yüklemeli.

### 3.3 Rule Index Kural İçeriğini Anlamıyor

Constitution Index, .md dosyalarından Rule ID'leri başarıyla ayrıştırıyor (50 kural). Ancak her kuralın **hangi State için geçerli olduğunu**, **hangi Scene'de uygulanacağını**, **hangi koşulda tetikleneceğini** çıkarmıyor.

Regex tabanlı kural ayrıştırma (`MASTER-003`, `AR-002_28` pattern'leri) Rule ID'yi bulur, ancak:
- "Bu kural SAHNE-02'de mi geçerli, SAHNE-08'de mi?" → bilmiyor
- "Bu kuralın tetiklenmesi için hangi Event gerekiyor?" → bilmiyor
- "Bu kural hangi Workflow'un parçası?" → bilmiyor

### 3.4 CEE ve Index Arasındaki Bağlantı Tek Yönlü

`validate_with_index()` metodu, Index'ten gelen sonuçları EnforcementReport'a dönüştürüyor. Ancak Index'e "Hangi State'teyim?" sorusunu sormuyor. `runtime_context` dict'i içindeki anahtarlara göre kör eşleştirme yapıyor.

---

## 4. Eksik Olan Davranış Nedir?

### 4.1 Bağlamsal Kural Yükleme (Contextual Rule Loading)

HLK'nın eksik olan en temel davranışı: **Bulunduğu State ve Workflow'a göre ilgili kuralları otomatik yükleyememesi.**

Olması gereken:
```python
# OLMASI GEREKEN (HLK'nın düşünme şekli)
state = "STATE_SCENE_2"
scene = "SAHNE-02"
workflow = "WF-001"

# ANA YASA'da bu bağlam için geçerli TÜM kuralları bul
relevant_rules = constitution_index.get_rules_for_context(
    state=state,
    scene=scene,
    workflow=workflow,
)
# → Sadece STATE_SCENE_2, SAHNE-02, WF-001 ile ilişkili kurallar gelir
# → STATE_SCENE_1'e ait kurallar GELMEZ
# → STATE_AUDIO_SELECTION'a ait kurallar GELMEZ
```

### 4.2 Workflow-State-Scene Kural İlişkilendirmesi

Constitution Index'in her kural için şu alanları indekslemesi gerekir:
- `applicable_states`: Bu kural hangi State'lerde geçerli?
- `applicable_scenes`: Bu kural hangi Scene'lerde geçerli?
- `applicable_workflows`: Bu kural hangi Workflow'lara ait?
- `trigger_events`: Bu kural hangi Event'lerde tetiklenir?

Bu alanlar **.md dosyalarından ayrıştırılmalıdır.** Örneğin `OR-004_0` kuralı şöyle başlar:
> "STATE_SCENE_1 içerisinde SAHNE-01 karşılama videosu kullanıcıya gönderilmelidir."

Bu cümleden şu çıkarılabilir: `applicable_states = ["STATE_SCENE_1"]`, `applicable_scenes = ["SAHNE-01"]`

### 4.3 Runtime Gözlem vs Karar Ayrımı

Handler'lar şu anda **hem gözlem yapıyor hem karar veriyor.** ANA YASA'ya göre Handler'lar sadece **gözlem yapmalı**, kararı CEE vermeli.

Mevcut durum:
```python
# Handler HEM gözlem yapıyor HEM karar veriyor
operational_ok = (cleanup_success_count == cleanup_total)  # ← KARAR
```

Olması gereken:
```python
# Handler SADECE gözlem yapıyor
runtime_context = {
    "cleanup": {"total": 3, "success": cleanup_success_count},
    "video_sent": sahne2_msg is not None,
    "events": ["EVENT_LANGUAGE_SELECTED"],
}
# CEE KARAR veriyor
report = cee.evaluate(runtime_context, state="STATE_SCENE_2", scene="SAHNE-02")
```

### 4.4 HLK'nın Kendi Kendine Soru Sorması

HLK şu anda pasif — Handler çağırmadan çalışmıyor. Oysa ANA YASA'ya göre HLK aktif bir karar verici olmalı:

- "State değişti mi?" → Otomatik kontrol et
- "Yeni bir Event oluştu mu?" → Otomatik değerlendir
- "Runtime'da anomali var mı?" → Otomatik tespit et

Bu, **event-driven** bir mimari gerektirir. State Engine her `fire()` çağrıldığında otomatik olarak CEE'yi tetiklemeli. Handler'ın manuel olarak CEE'yi çağırması gerekmemeli.

---

## 5. HLK'nın Gerçekten "Anayasal İşletim Sistemi" Olabilmesi İçin Davranış Modeli

### 5.1 Üç Katmanlı Karar Mimarisi

```
┌─────────────────────────────────────────────────┐
│               KATMAN 1: GÖZLEM                   │
│                                                  │
│  Handler'lar + State Engine + Scene Engine       │
│  Görevi: Runtime'da ne olduğunu KAYDETMEK        │
│  Karar vermez. Sadece veri toplar.               │
│  Çıktı: RuntimeContext (ham gözlem verisi)        │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              KATMAN 2: BAĞLAM                     │
│                                                  │
│  Constitution Index + Workflow Engine            │
│  Görevi: "Bu State/Scene/Workflow için           │
│           ANA YASA ne diyor?" sorusuna cevap      │
│  Çıktı: ApplicableRuleSet (ilgili kurallar)       │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│               KATMAN 3: KARAR                     │
│                                                  │
│  Constitution Enforcement Engine (CEE)            │
│  Görevi: RuntimeContext ile ApplicableRuleSet'i   │
│          karşılaştır, PASS/FAIL üret             │
│  TEK karar verici. Başka karar verici yok.        │
│  Çıktı: EnforcementReport (PASS/FAIL)             │
└─────────────────────────────────────────────────┘
```

### 5.2 HLK'nın Düşünme Döngüsü (Decision Loop)

Her State geçişinde otomatik olarak:

```
1. State Engine: STATE değişti
   ↓ (otomatik tetikleme)
2. CEE: Hangi Workflow'tayım? → WF-001
   Hangi State'teyim? → STATE_SCENE_2
   Hangi Scene'deyim? → SAHNE-02
   ↓
3. Constitution Index: Bu bağlam için kuralları yükle
   → MASTER-003 (Cleanup zorunlu)
   → FD-008_1 (SAHNE-02 akışı)
   → OR-004_0 (SAHNE-02 operasyonel)
   → AR-002_28 (Scene Engine)
   → AR-002_31 (Speech-Text-Wave Sync)
   ↓
4. Runtime gözlemlerini oku
   → Cleanup: 3/3 mesaj silindi ✅
   → Video: SAHNE-2_TR_alt.mp4 gönderildi ✅
   → Daktilo: 31+9 kelime tamamlandı ✅
   → Event: EVENT_LANGUAGE_SELECTED tetiklendi ✅
   ↓
5. Karşılaştır
   → MASTER-003: Cleanup 3/3 → ✅
   → FD-008_1: Akış sırası doğru → ✅
   → OR-004_0: Video + link isteği → ✅
   → AR-002_31: Senkronizasyon → ✅
   ↓
6. Karar: ✅ PASS
   ↓
7. LAC: "SAHNE-02: PASS — 4/4 kural denetlendi"
```

### 5.3 Yeni Kural Eklendiğinde

```
1. Proje Yöneticisi: 04_Operational_Rules.md'ye OR-004_11 ekler
2. Constitution Cache: Dosya hash'i değişti → refresh
3. Constitution Index: Yeni Rule ID bulundu → indeksle
   → OR-004_11: applicable_states = ["STATE_SCENE_2", "STATE_SCENE_3"]
   → OR-004_11: category = "Video"
   → OR-004_11: constraint = "MANDATORY"
4. Bir sonraki State geçişinde:
   → CEE, STATE_SCENE_2 için kuralları yükler
   → OR-004_11 otomatik olarak gelir
   → Runtime ile karşılaştırılır
   → PASS/FAIL üretilir
5. SIFIR Python kodu değişikliği
```

### 5.4 HLK'nın Rol Tanımı

| Rol | Açıklama | ANA YASA Dayanağı |
|---|---|---|
| **Anayasa Okuyucu** | .md dosyalarından kuralları anlar, indeksler | MASTER-001, CSE, CDE |
| **Bağlam Çözümleyici** | Workflow-State-Scene üçgeninde nerede olduğunu bilir | SE-007_3, FD-008_1, WF-001 |
| **Runtime Gözlemci** | Handler'lardan gelen ham veriyi toplar, değerlendirmez | EEC, Olay Kayıt Merkezi |
| **Karşılaştırıcı** | ANA YASA kuralları ile Runtime gözlemlerini eşleştirir | CEE, CDE |
| **Karar Verici** | PASS veya FAIL üretir — TEK yetkili | MASTER-004, CEE-004 |
| **Kayıt Tutucu** | Her kararı LAC'ta gösterir, EventRegistry'ye yazar | EEC, Olay Kayıt Merkezi |
| **Geri Bildirimci** | FAIL durumunda Executor'a eksikleri iletir | AR-002_22, CEE-005 |

---

## 6. Sonuç

HLK'nın bugünkü implementasyonu, ANA YASA'nın tanımladığı davranış modelinin **yapı taşlarına sahiptir ancak karar akışı ters yönde çalışmaktadır.**

**Temel kopukluk:** Handler'lar karar veriyor, CEE onaylıyor. Oysa ANA YASA'ya göre CEE karar vermeli, Handler'lar sadece gözlem yapmalı.

**Eksik davranışlar:**
1. Bağlamsal kural yükleme (Workflow-State-Scene göre)
2. Kural içeriğinden State/Scene/Workflow ilişkisini ayrıştırma
3. Runtime gözlem ile kararın ayrıştırılması
4. State Engine'den CEE'ye otomatik tetikleme (event-driven)

**HLK'nın "Anayasal İşletim Sistemi" olması için:** Karar akışının ters çevrilmesi gerekir. Handler'lar boolean üretmeyi bırakmalı, sadece ham gözlem verisi sağlamalı. CEE, Index'ten bağlama uygun kuralları yüklemeli, Runtime ile karşılaştırmalı ve nihai kararı vermeli.

Bu dönüşüm tamamlandığında, yeni bir ANA YASA maddesi eklendiğinde hiçbir Python kodu değişmeyecek — sadece .md dosyası güncellenecek ve HLK yeni kuralı bir sonraki State geçişinde otomatik olarak denetlemeye başlayacak.
