# HLK Davranış Modeli — Anayasal Kanıt Raporu

**Tarih:** 3 Temmuz 2026
**Amaç:** 4 tespitin ANA YASA referanslarıyla kanıtlanması
**Kapsam:** Yalnızca ANA YASA maddeleri — tahmin, yorum, kod önerisi yok

---

# TESPİT-1: Karar Akışı Ters Yönde

**Tespit:** Handler'lar karar veriyor (boolean üretiyor), CEE yalnızca sonucu onaylıyor. Oysa CEE karar vermeli, Handler sadece gözlem yapmalı.

---

## İlgili MASTER Maddeleri

**MASTER-004 — HLK KARAR MEKANİZMASI VE KURAL OTORİTESİ PRENSİBİ**

> "HLK projesinde karar veren, yöneten ve nihai kararı oluşturan tek yapı HLK'dır."
>
> "MASTER, Global Configuration (GC), General Rules (GK), Architecture Rules (AR), State Engine, Flow Diagram, Operational Rules (OR), Module Rules (MR), Quality Rules (QR) ve Kod katmanları bağımsız karar vericiler değildir."
>
> "Bu katmanların görevi, HLK'nın karar mekanizmasını anayasal kurallar çerçevesinde yönlendirmek, sınırlandırmak ve doğrulamaktır."
>
> "Hiçbir katman HLK'dan bağımsız olarak karar verme veya emir verme yetkisine sahip değildir."

**MASTER-001 — ANA YASA ÜSTÜNLÜĞÜ**

> "Hiçbir teknik tercih, hiçbir workaround, hiçbir yardımcı fonksiyon, hiçbir script, hiçbir modül, hiçbir ajan, hiçbir kod parçası, bu belgede tanımlanan kuralların üzerinde değildir."

**Analiz:** MASTER-004 açıkça "Kod katmanları bağımsız karar vericiler değildir" der. Handler bir Python fonksiyonudur — Kod katmanıdır. Dolayısıyla Handler'ın bağımsız karar vermesi (boolean üretmesi) MASTER-004'e aykırıdır. Karar yetkisi yalnızca HLK'ya (CEE'ye) aittir.

---

## İlgili Architecture Rules

**AR-002_60 — Constitution Enforcement Engine (CEE-001, CEE-004)**

> "CEE, HLK içerisinde **PASS ve FAIL verme yetkisine sahip tek katmandır.** CSE, CDE, Task Engine ve diğer katmanlar PASS/FAIL üretemez. Bu yetki münhasıran CEE'ye aittir." (03_Architecture_Rules.md:3781)

> "CEE-004: CEE PASS olmadan görev TAMAMLANDI kabul edilemez (MASTER-003 operasyonel uygulaması)." (03_Architecture_Rules.md:3778)

> "CEE-001: CEE olmadan hiçbir geliştirme görevi başlayamaz ve tamamlanamaz." (03_Architecture_Rules.md:3775)

**Analiz:** AR-002_60, PASS/FAIL yetkisini münhasıran CEE'ye verir. "Diğer katmanlar PASS/FAIL üretemez." Handler bir "diğer katman"dır. Handler'ın `operational_ok=True/False` gibi kararlar üretmesi, CEE'nin münhasır yetkisine müdahaledir.

---

## İlgili Operational Rules

**21_CONSTITUTION_ENFORCEMENT_ENGINE.md — CEE Operasyonel Tanımı**

> "Executor yalnızca uygulayıcıdır. Claude hiçbir zaman karar verici değildir; yalnızca CEE'nin hazırladığı anayasal paketi uygular." (21_CEE.md:80)

> "FAIL durumunda görev Executor'a geri gönderilir. Eksikler giderilene kadar döngü devam eder." (21_CEE.md:78)

> "CEE zorunlu geçiş noktasıdır. Hiçbir geliştirme görevi CEE'nin PRE-CHECK'inden geçmeden başlayamaz, POST-CHECK'inden geçmeden tamamlanamaz." (21_CEE.md:79)

**Analiz:** Executor (=Handler) "yalnızca uygulayıcıdır", "hiçbir zaman karar verici değildir." Bugünkü implementasyonda Handler'lar `post_check()`'e boolean parametreler geçirerek fiilen karar verici konumundadır. Bu, 21_CEE.md:80'e doğrudan aykırıdır.

---

## İlgili Flow Diagram

**FD-008_1 — HLK MASTER FLOW DIAGRAM**

Akış diyagramı, her State'de HLK'nın ne yapması gerektiğini tanımlar. Handler'lar bu akışı uygular. Ancak akışın doğruluğuna karar verme yetkisi Flow Diagram'da değil, CEE'dedir.

---

## İlgili State Engine

**SE-007_5 — State Event Trigger Architecture**

> "HLK içerisinde hiçbir state değişimi sebepsiz veya rastgele gerçekleşemez. Her state değişimi bir olay (event) tarafından tetiklenmelidir."

State Engine durum geçişlerini yönetir, ancak geçişin anayasal uygunluğuna karar vermez. Bu karar CEE'nindir.

---

## Anayasal Sonuç

| Kaynak | Ne Diyor |
|---|---|
| MASTER-004 | Kod katmanları karar verici değildir |
| AR-002_60 (CEE-001) | CEE olmadan görev başlayamaz |
| AR-002_60 (CEE-004) | PASS/FAIL yetkisi münhasıran CEE'dedir |
| 21_CEE.md:80 | Executor yalnızca uygulayıcıdır, karar verici değildir |

---

## Bu davranış gerçekten zorunlu mu?

## ✅ EVET

**Gerekçe:** MASTER-004, AR-002_60 (CEE-001, CEE-004), ve 21_CEE.md:80 birlikte değerlendirildiğinde, Handler'ların (=Executor) karar vermesi ve CEE'nin yalnızca onaylaması anayasal olarak yasaklanmıştır. Karar akışının CEE'de başlayıp CEE'de bitmesi zorunludur.

---

# TESPİT-2: Bağlamsal Kural Yükleme Eksik

**Tespit:** HLK, bulunduğu Workflow, State, Scene bağlamından uygulanması gereken anayasa maddelerini otomatik belirleyemiyor.

---

## İlgili MASTER Maddeleri

**MASTER-006 — HLK MODÜLER VE ÖĞRENEN YAPAY ZEKÂ ASİSTANI İLKESİ**

> "HLK; modüler, genişleyebilir ve sürekli öğrenen bir Yapay Zekâ Asistanı platformudur."
>
> "HLK içerisinde geliştirilecek tüm mevcut ve gelecekteki modüller; Ortak State Engine'i, Ortak Flow Diagram'ı [...] kullanmak zorundadır."

**MASTER-001 Karar Hiyerarşisi:**

> "1. HLK MASTER RULE BOOK → 2. Global Configuration → 3. General Rules → 4. Architecture Rules → 5. State Engine → 6. Flow Diagram → 7. Operational Rules → 8. Quality Rules → 9. Module Rules → 10. Kod"

**Analiz:** MASTER-001'in Karar Hiyerarşisi, HLK'nın karar verirken State Engine ve Flow Diagram'ı referans almasını zorunlu kılar. HLK'nın hangi State'te olduğunu bilmeden hangi kuralların geçerli olduğunu belirlemesi mümkün değildir. Bağlamsız kural yükleme, Karar Hiyerarşisi'ne aykırıdır.

---

## İlgili Architecture Rules

**AR-002_22 — Constitutional Feedback / Control Loop (Adım 1-2)**

> "ADIM 1: EXECUTOR TAMAMLANDI — Executor, DecisionPacket'i uygular. ExecutionResult üretir."
>
> "ADIM 2: FEEDBACK LOOP DEĞERLENDİRMESİ — Feedback Loop, ExecutionResult'ı alır. DEĞERLENDİRME: ExecutionResult.status == SUCCESS? Sonraki state için yeni Event oluştur."

**Analiz:** Feedback Loop, her Executor tamamlanmasından sonra "Sonraki state için yeni Event oluştur" der. Bu, HLK'nın HER State geçişinde bağlamı yeniden değerlendirmesi gerektiği anlamına gelir. "Sonraki state" ifadesi, kuralların State'e göre seçilmesi gerektiğini gösterir.

---

## İlgili Flow Diagram

**FD-008_1 — HLK MASTER FLOW DIAGRAM**

Akış diyagramı her State için farklı davranışlar tanımlar:
- SAHNE-01: Karşılama videosu, dil seçimi
- SAHNE-02: Lip-sync video, daktilo, link isteği
- SAHNE-03: Format seçimi
- SAHNE-06 (SAHNE-08): Ses seçimi, DEVAM butonu zorunluluğu

Her State'in kendine özgü kuralları vardır. SAHNE-02'nin kuralları SAHNE-06'da geçerli değildir.

---

## İlgili State Engine

**SE-007_3 — User Conversation State Architecture**

> "HLK bulunduğu kullanıcı durumuna göre; Active Conversation Screen'i çalıştırabilir. Conversation Scene Engine'i çalıştırabilir. Kullanıcıdan bilgi isteyebilir."

**SE-007_6 — State Action Mapping Architecture**

> "Her state aynı zamanda belirli modüllerin, servislerin veya sistem davranışlarının çalıştırılmasını tetikleyebilir. Bir state aktif hale geldiğinde HLK ilgili state için tanımlanmış modülleri devreye alabilir."

**Analiz:** SE-007_6, "Her state belirli modüllerin çalıştırılmasını tetikleyebilir" der. Bu, State'e özgü davranışların olduğunu ve HLK'nın State bağlamına göre hareket etmesi gerektiğini gösterir. Dolayısıyla kurallar da State bağlamına göre seçilmelidir.

---

## Anayasal Sonuç

| Kaynak | Ne Diyor |
|---|---|
| MASTER-001 | Karar Hiyerarşisi: State Engine → Flow Diagram → Operational Rules sırasıyla |
| AR-002_22 | Feedback Loop: "Sonraki state için yeni Event oluştur" |
| FD-008_1 | Her State'in kendine özgü kuralları vardır |
| SE-007_6 | Her state belirli modülleri tetikler |

---

## Bu davranış gerçekten zorunlu mu?

## ✅ EVET

**Gerekçe:** MASTER-001 Karar Hiyerarşisi, State Engine ve Flow Diagram'ın referans alınmasını zorunlu kılar. SE-007_6 her State'in farklı modülleri tetiklediğini söyler. FD-008_1 her State için farklı kurallar tanımlar. Dolayısıyla HLK'nın kural yükleme işlemini State bağlamına göre yapması anayasal zorunluluktur.

---

# TESPİT-3: Rule Index Bağlam Çıkaramıyor

**Tespit:** Rule Index, anayasa maddelerinin hangi State, Scene, Workflow için geçerli olduğunu .md dosyalarından otomatik çıkaramıyor.

---

## İlgili MASTER Maddeleri

**MASTER-003 — ANA YASA / KOD UYUMLULUK DENETİM PRENSİBİ**

> "HLK sisteminde bir ANA YASA güncellemesinin tamamlanmış kabul edilebilmesi için yalnızca dokümantasyonun güncellenmiş olması yeterli değildir. İlgili çalışan kodların da yeni kurallarla uyumlu olduğunun doğrulanması zorunludur."
>
> "Bir kuralın ANA YASA'ya eklenmiş olması, çalışan sistemin bu kurala uyduğu anlamına gelmez."
>
> Tamamlanma Kriteri: "ANA YASA Güncellendi + Kod Güncellendi + Runtime Davranışı Doğrulandı = TAMAMLANDI"

**Analiz:** MASTER-003'ün Tamamlanma Kriteri, her ANA YASA değişikliğinin Runtime'da doğrulanmasını zorunlu kılar. Rule Index, .md'den kural çıkaramazsa, bu doğrulama yapılamaz. Dolayısıyla Index'in kural içeriğini (hangi State'te geçerli olduğunu) anlaması, MASTER-003'ün Runtime doğrulama zorunluluğunun ön koşuludur.

---

## İlgili Architecture Rules

**CSE — Constitution Scan Engine (19_CSE.md:13)**

> "CSE'nin tek görevi; HLK'nın tüm katmanlarını okuyarak **tek bir Constitution Snapshot** oluşturmak ve bu snapshot'ı Constitution Diff Engine'e (CDE) aktarmaktır."
>
> "CSE: ANA YASA (.md) dosyalarını tarar, Kod (.py) dosyalarını tarar, Runtime log'larını tarar, Registry, Workflow, Feature, Event ve Production verilerini toplar."

**CDE — Constitution Diff Engine (18_CDE.md:40)**

> "ANA YASA'da tanımlanmış fakat kodda karşılığı olmayan bileşenleri, Kodda var olan fakat ANA YASA'da tanımlanmamış bileşenleri, ANA YASA ile kod arasında çelişki oluşturan bileşenleri otomatik olarak tespit etmek."

**Analiz:** CSE "tüm katmanları okuyarak Snapshot oluşturur." CDE "ANA YASA ile kod arasında çelişki oluşturan bileşenleri otomatik tespit eder." Bu iki motorun çalışabilmesi için, .md dosyalarındaki kuralların hangi State/Scene/Workflow'a ait olduğunun bilinmesi gerekir. Aksi takdirde CDE, "FD-008_1'de tanımlı SAHNE-02 Cleanup kuralı kodda karşılık buluyor mu?" sorusunu soramaz.

---

## İlgili Operational Rules

**OR-004_0 — SAHNE-01 ve SAHNE-02 Operasyonel Kuralları**

> "STATE_SCENE_1 içerisinde SAHNE-01 karşılama videosu kullanıcıya gönderilmelidir."
> "STATE_SCENE_2 içerisinde seçilen dile uygun SAHNE-02 videosu oynatılmalıdır."
> "STATE_WAIT_PRODUCT_LINK aşamasında kullanıcıdan ürün linki istenmelidir."

**Analiz:** OR kuralları açıkça "STATE_SCENE_1 içerisinde...", "STATE_SCENE_2 içerisinde..." ifadelerini kullanır. Her kural hangi State için geçerli olduğunu KENDİ İÇERİSİNDE belirtir. Rule Index'in bu bilgiyi .md'den çıkarması gerekir.

---

## İlgili Flow Diagram

**FD-008_1** her sahneyi ayrı ayrı tanımlar. SAHNE-08 için "DEVAM butonu" kuralı SAHNE-02 için geçerli değildir.

---

## Anayasal Sonuç

| Kaynak | Ne Diyor |
|---|---|
| MASTER-003 | Runtime doğrulaması zorunlu — Index bağlam çıkaramazsa doğrulama eksik kalır |
| CSE/CDE | Tüm katmanları tara, çelişkileri otomatik tespit et |
| OR-004_0 | Her kural hangi State için geçerli olduğunu kendi içinde belirtir |
| FD-008_1 | Her sahnenin kendine özgü kuralları vardır |

---

## Bu davranış gerçekten zorunlu mu?

## ✅ EVET

**Gerekçe:** CSE'nin "tüm katmanları okuyarak Snapshot oluşturma" görevi, kuralların bağlamsal olarak indekslenmesini gerektirir. OR kuralları State bilgisini kendi içinde taşır. CDE'nin "ANA YASA ile kod arasında çelişki tespiti" yapabilmesi için Index'in kural-State ilişkisini bilmesi zorunludur.

---

# TESPİT-4: Gözlem ve Karar Ayrışmamış

**Tespit:** Runtime gözlemi ile anayasal karar birbirinden ayrılmamış. Handler hem gözlem yapıyor hem karar veriyor.

---

## İlgili MASTER Maddeleri

**MASTER-004 — HLK KARAR MEKANİZMASI VE KURAL OTORİTESİ PRENSİBİ**

> "Kod ise tüm bu katmanların uygulama seviyesindeki karşılığıdır."
>
> "HLK, tüm kararlarını bu anayasal katmanları birlikte değerlendirerek oluşturur."

**MASTER-003 — Gerçek Tamamlanma Tanımı**

> "ANA YASA Güncellendi + Kod Güncellendi + Runtime Davranışı Doğrulandı = TAMAMLANDI"

**Analiz:** MASTER-004, Kod'un "uygulama seviyesindeki karşılık" olduğunu söyler — karar verici değil. MASTER-003, Runtime Davranışı Doğrulandı aşamasını Kod Güncellendi'den AYRI bir aşama olarak tanımlar. Bu iki madde birlikte, gözlem (Runtime Davranışı) ile kararın (Doğrulandı) ayrı aşamalar olduğunu gösterir.

---

## İlgili Architecture Rules

**AR-002_22 — Constitutional Feedback Loop (Adım 1-2-3)**

> "ADIM 1: Executor, DecisionPacket'i uygular. ExecutionResult üretir. Executor'un görevi burada SONA ERER. Executor karar vermez, sonraki adımı BELİRLEMEZ."
>
> "ADIM 2: Feedback Loop, ExecutionResult'ı alır. DEĞERLENDİRME yapar."
>
> "ADIM 3: Decision Engine yeniden çağrılır. Nihai karar her zaman Decision Engine'indir (MASTER-004)."

**Analiz:** AR-002_22'nin Adım 1-2-3 zinciri, gözlem ve kararın AYRI aşamalar olduğunu açıkça tanımlar:
- Adım 1 (Executor): UYGULAR, ExecutionResult üretir. Karar VERMEZ.
- Adım 2 (Feedback Loop): ExecutionResult'ı DEĞERLENDİRİR.
- Adım 3 (Decision Engine): Yeniden KARAR ÜRETİR.

Bugünkü implementasyonda Handler (Executor) hem uyguluyor hem değerlendiriyor hem karar veriyor. Bu üç adımın tek bir fonksiyonda birleşmesi AR-002_22'ye aykırıdır.

---

## İlgili Operational Rules

**21_CEE.md — FAZ 1-2-3**

> "FAZ 1 (PRE-CHECK): CEE, anayasal görev paketini oluşturur."
> "FAZ 2 (EXECUTE): Executor çalışır. CEE pasiftir."
> "FAZ 3 (POST-CHECK): CEE, 6 boyutlu denetim yapar, PASS/FAIL üretir."

**Analiz:** CEE'nin 3 fazlı mimarisi, gözlem (FAZ 2) ile kararın (FAZ 3) ayrı fazlar olduğunu tanımlar. Handler'ın FAZ 2'de çalışıp FAZ 3'ün kararını da vermesi (boolean üretmesi), bu faz ayrımını ihlal eder.

---

## İlgili State Engine

**SE-007_5 — State Event Trigger Architecture**

> "HLK'nin amacı yalnızca mevcut state'i takip etmek değil, state değişiminin neden gerçekleştiğini de kayıt altına alabilmektir."

State Engine state değişimini kaydeder, ancak bu değişimin anayasal uygunluğuna karar vermez.

---

## Anayasal Sonuç

| Kaynak | Ne Diyor |
|---|---|
| MASTER-004 | Kod uygulama katmanıdır, karar verici değil |
| MASTER-003 | Runtime Doğrulama ayrı bir aşamadır |
| AR-002_22 Adım 1 | Executor karar vermez, sonraki adımı belirlemez |
| 21_CEE.md FAZ 2-3 | Execute ve Post-Check ayrı fazlardır |

---

## Bu davranış gerçekten zorunlu mu?

## ✅ EVET

**Gerekçe:** AR-002_22'nin 3 adımlı Feedback Loop'u, Executor'un "karar vermez, sonraki adımı belirlemez" kuralını açıkça tanımlar. 21_CEE.md'nin 3 fazlı mimarisi, gözlem (FAZ 2) ve karar (FAZ 3) ayrımını zorunlu kılar. Handler'ın hem gözlem yapıp hem karar vermesi, bu iki anayasal yapıya aynı anda aykırıdır.

---

# NİHAİ SORU

## HLK_BEHAVIOR_MODEL_ANALYSIS.md raporunda belirtilen dört eksiklik; gerçekten implementasyon eksikliği midir, yoksa yalnızca mimari yorum mudur?

## ✅ GERÇEKTEN İMPLEMENTASYON EKSİKLİĞİDİR

Aşağıdaki ANA YASA maddeleri, her dört tespitin de anayasal zorunluluk olduğunu kanıtlamaktadır:

| # | Tespit | Zorunlu Kılan Anayasa Maddeleri |
|---|---|---|
| 1 | Karar akışı ters yönde | MASTER-004, AR-002_60/CEE-001, AR-002_60/CEE-004, 21_CEE.md:80 |
| 2 | Bağlamsal kural yükleme eksik | MASTER-001 (Karar Hiyerarşisi), AR-002_22, FD-008_1, SE-007_6 |
| 3 | Rule Index bağlam çıkaramıyor | MASTER-003, CSE (19_CSE.md:13), CDE (18_CDE.md:40), OR-004_0 |
| 4 | Gözlem ve karar ayrışmamış | MASTER-004, MASTER-003, AR-002_22 (Adım 1-2-3), 21_CEE.md (FAZ 2-3) |

**Her dört tespit de en az 4 farklı ANA YASA maddesi tarafından zorunlu kılınmaktadır.**

**Bunlar mimari yorum değil, doğrudan anayasal gerekliliklerdir.**

---

*Rapor, yalnızca ANA YASA maddeleri referans alınarak hazırlanmıştır. Tahmin, yorum veya kod önerisi içermez.*
