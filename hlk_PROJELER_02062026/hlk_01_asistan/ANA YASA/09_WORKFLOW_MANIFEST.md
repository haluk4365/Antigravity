# 09 — Workflow Manifest

Business Workflow kayıtları.

---

## WF-001

### Workflow

HLK Decision and Management Center — Karar ve Yönetim Merkezi

### Açıklama

WF-001, HLK'nın oturum boyunca çalışan Karar ve Yönetim Merkezidir. Sistemdeki ilk karar vericidir; araştırma yapmaz, üretim sürecini yönetir.

**İş Akışı (13 Adım):**

1. **Product Link Validation** — Kullanıcıdan alınan ürün linki doğrulanır (GK-001_1..12). Link doğrulanmadan hiçbir alt süreç başlatılamaz.

2. **Reference Product** — Doğrulanmış link üzerinden referans ürün kaydı oluşturulur. Ürün tanınmadan araştırma başlatılmaz.

3. **Ürün Analizi** — Ürünün teknik özellikleri, kategorisi, pazar konumu ve temel nitelikleri analiz edilir.

4. **Dynamic Information Gaps** — HLK, "Bu ürünü eksiksiz, güvenilir ve en kaliteli şekilde tanıtabilmem için hangi bilgilere ihtiyacım var?" sorusunu değerlendirir. Ürün tipine göre dinamik Bilgi Açığı Listesi oluşturur. Sabit kontrol listesi kullanılmaz.

5. **Görev Planı** — Yapılacak işler, öncelik sırası ve uygun uzman ajanlar belirlenir.

6. **Selection Architecture** — Aşağıdaki seçimler anayasal kurallara göre yapılır:
   - Link Validation Agent seçimi (AR-002_46A)
   - Research Agent seçimi (AR-002_19, AR-002_46)
   - Service Provider seçimi (AR-002_21, AR-002_22, AR-002_75)
   - Aday sayısı ve yedek aday sayısı GC parametrelerine göre belirlenir (GC_PRIMARY_CANDIDATE_COUNT, GC_BACKUP_CANDIDATE_COUNT)

7. **Task Package Oluşturma** — Seçilen ajanlar için AR-002_47 hükümlerine uygun Task Package'ler oluşturulur. Her ajan yalnızca kendi görevini yerine getirebilmesi için gerekli minimum bilgiye erişebilir.

8. **Araştırma Sonuçlarının Değerlendirilmesi** — Bütün ajan sonuçları HLK tarafından değerlendirilir. Eksik bilgi varsa yeni görev oluşturulur. Yetersiz sonuç varsa uygun ajan tekrar görevlendirilir.

9. **Information Gaps Güncelleme** — Araştırma sonuçlarına göre Bilgi Açığı Listesi güncellenir. Tüm açıklar kapanana kadar görevlendirme devam eder.

10. **Production Package Hazırlama** — Toplanan tüm doğrulanmış bilgiler standart klasör yapısına yerleştirilir. Production Package eksiksiz oluşturulur (AR-002_58, 16_PRODUCTION_PACKAGE_STANDARD.md).

11. **WF-001 Work Package** — WF-001 kendi çalışma paketini oluşturur. Bu paket en az şu bölümleri içerir: Link Validation, Product Profile, Product Classification, Information Gaps, Task Plan, Agent Selection, Service Provider Selection, Assigned Tasks, Agent Results, Decision History, Production Package, Handover Report.

12. **Workflow Readiness Evaluation** — WF-001 Tamamlama Kriterleri, Production Package ve WF-001 Work Package anayasal olarak doğrulanır. Bu adım veri üretmez, workflow başlatmaz ve workflow'a devir yapmaz. Yalnızca iki karardan birini üretir: `READY FOR NEXT WORKFLOW` veya `NOT READY`. Karar, HLK Runtime tarafından üretilir (MASTER-013). Workflow devri yalnızca bu karar üretildikten sonra Workflow Engine tarafından gerçekleştirilir.

13. **Handover** — HLK "READY FOR NEXT WORKFLOW" kararını vermişse, Workflow Engine hazır hale gelen Production Package'i WF-002'ye devreder. "NOT READY" kararı verilmişse eksikler giderilir ve değerlendirme tekrarlanır.

**Temel İlkeler:**
- HLK = WF-001. Üretim süreci boyunca tek karar verici WF-001'dir.
- Hiçbir ajan karar veremez. Ajanlar yalnızca verilen görevi icra eder.
- WF-001 yeni raporlama sistemi oluşturmaz; mevcut anayasal kayıtları (Decision History, Production Package, Execution Event, Olay Kayıt Merkezi, LAC) ilişkilendirerek görünür hale getirir.
- Fake Progress üretilmez. Tüm kararlar izlenebilirdir.
- Production Package ve Work Package birbirinden bağımsız tutulur.

**Görev Tamamlama Kriteri (13 koşul):** Link doğrulanmış, Product Profile oluşturulmuş, Dynamic Information Gaps oluşturulmuş, Görev Planı hazırlanmış, Selection Architecture uygulanmış, Task Package'ler oluşturulmuş, araştırma sonuçları değerlendirilmiş, Information Gaps güncellenmiş, Production Package hazırlanmış, WF-001 Work Package hazırlanmış, Workflow Readiness Evaluation tamamlanmış, HLK "READY FOR NEXT WORKFLOW" kararını vermiş, Workflow Engine tarafından WF-002'ye devir gerçekleştirilmiş olmalıdır.

### Durum

FREEZE v1.0 — Referans Workflow (Değişiklik Kısıtlı)

**Değişiklik Kuralları:** WF-001 yalnızca Bug Fix veya Anayasa Revizyonu sonrası referans güncellemesi kapsamında değiştirilebilir. Yeni özellik eklenemez, workflow akışı değiştirilemez, anayasa maddeleri workflow içine kopyalanamaz. WF-002 veya sonraki workflow'lar WF-001'i değiştiremez. İhtiyaç oluşursa önce Anayasa güncellenir, WF-001 yalnızca referans takibi yapar. Tüm workflow'lar tamamlandığında aynı freeze kuralı uygulanacaktır.

**Reference Workflow Standard:** WF-001, HLK Workflow mimarisinin referans uygulamasıdır. WF-002 ve sonraki tüm workflow'lar; tasarım dili, workflow mimarisi, karar mekanizması, anayasa referans kullanımı, dokümantasyon standardı, Workflow Readiness Evaluation mantığı, Work Package yapısı, Production Package entegrasyonu ve Handover yaklaşımı açısından WF-001 ile uyumlu olacak şekilde tasarlanmalıdır. Yeni workflow geliştirmelerinde mevcut standarttan sapılamaz. Bir workflow farklı mimariye ihtiyaç duyarsa önce Anayasa değerlendirilir, gerekirse Anayasa revize edilir, workflow'lar yalnızca ilgili anayasa referanslarını takip edecek şekilde güncellenir. Hiçbir workflow kendisinden önce freeze edilmiş bir workflow'un mimarisini doğrudan değiştiremez. Anayasa = Tek doğruluk kaynağı (Single Source of Truth). WF-001 = Referans uygulama (Reference Implementation).

---

## WF-002

### Workflow

Background Research

### Açıklama

Ürün doğrulandıktan sonra başlatılan arka plan araştırmalarını temsil eder.

### Durum

AKTİF

---

## WF-003

### Workflow

Brief Collection

### Açıklama

Kullanıcıdan reklam üretimi için gerekli bilgilerin toplanmasını temsil eder.

### Durum

AKTİF

---

## WF-004

### Workflow

Brief Approval

### Açıklama

Oluşturulan brief'in kullanıcı tarafından kontrol edilip onaylanmasını temsil eder.

### Durum

AKTİF

---

## WF-005

### Workflow

Scenario Generation

### Açıklama

Onaylı brief kullanılarak reklam senaryosunun oluşturulmasını temsil eder.

### Durum

AKTİF

---

## WF-006

### Workflow

Scenario Approval

### Açıklama

Oluşturulan senaryonun kullanıcı tarafından onaylanmasını temsil eder.

### Durum

AKTİF

---

## WF-007

### Workflow

Pricing

### Açıklama

Video üretimi için fiyat teklifinin hazırlanmasını temsil eder.

### Durum

AKTİF

---

## WF-008

### Workflow

Video Production

### Açıklama

Onaylanan senaryoya göre reklam videosunun üretilmesini temsil eder.

### Durum

AKTİF

---

## WF-009

### Workflow

Quality Control

### Açıklama

Üretilen video ve çıktılar için kalite kontrol sürecini temsil eder.

### Durum

AKTİF

---

## WF-010

### Workflow

Delivery

### Açıklama

Üretilen videonun kullanıcıya teslim edilmesini temsil eder.

### Durum

AKTİF

---

## WF-011

### Workflow

Session Completed

### Açıklama

Oturumun başarıyla tamamlanmasını temsil eder.

### Durum

AKTİF

---

## WF-015

### Workflow

Constitution Enforcement

### Açıklama

Constitution Enforcement Engine (CEE) tarafından yürütülen anayasal uygulatma ve denetim akışını temsil eder. PRE-CHECK → EXECUTE → POST-CHECK → PASS/FAIL fazlarından oluşur. Her geliştirme görevi öncesi ve sonrası otomatik tetiklenir.

### Durum

AKTİF

---

## WF-016

### Workflow

Execution Event Collection

### Açıklama

Execution Event Collector (EEC) tarafından yürütülen Executor işlemlerinin gerçek zamanlı Event'e dönüştürülmesi, Olay Kayıt Merkezi'ne kaydedilmesi ve Live Activity Center (LAC) tarafından anlık görüntülenmesi akışını temsil eder. LISTEN → TRANSFORM → REGISTER aşamalarından oluşur. 6 kategoride 28 Event tipi ile çalışır.

### Durum

AKTİF

---

## WF-017

### Workflow

Runtime Decision Request

### Açıklama

Yürütme katmanlarında karar gerektiren bir durum oluştuğunda uygulanan zorunlu karar talep akışını temsil eder (MASTER-013, AR-002_81, OR-004_12). Yürütme durdurulur → Karar talebi HLK Runtime'a iletilir → HLK Runtime kararını verir → Yürütme bu karara göre devam eder. Tereddüt halinde karar üretmek yasaktır; tereddüt bu workflow'u tetikler. Tüm karar talepleri ve kararlar PID, Decision History ve Event sistemi ile ilişkilendirilir.

### Durum

AKTİF

