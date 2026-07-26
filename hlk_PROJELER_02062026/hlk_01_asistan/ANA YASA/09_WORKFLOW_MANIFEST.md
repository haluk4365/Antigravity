# 09 — Workflow Manifest

Business Workflow kayıtları.

---

## WF-001

### Workflow

HLK Karar ve Yönetim Merkezi — Product Link Validation & Production Planning

### Açıklama

WF-001, HLK'nın çalışma oturumudur. Sistemdeki ilk çalışan ajan değil, ilk karar vericidir.

WF-001'in temel görevi araştırma yapmak değil, üretim sürecini yönetmektir:
- Kullanıcıdan alınan ürün linkini doğrulamak (GK-001_1..12)
- Ürünü tanımak ve analiz etmek
- "Bu ürünü eksiksiz, güvenilir ve en kaliteli şekilde tanıtabilmem için hangi bilgilere ihtiyacım var?" sorusunu cevaplamak
- Ürün tipine göre dinamik Bilgi Açığı Listesi oluşturmak
- Yapılacak işleri, öncelik sırasını ve uygun uzman ajanları belirlemek
- Uzman ajanları görevlendirmek (Link Validation, Product Research, Image Research, Brand Research, Technical Research, Asset Organizer)
- Ajan sonuçlarını değerlendirmek, eksik bilgi varsa yeni görev oluşturmak
- Toplanan tüm doğrulanmış bilgileri standart klasör yapısına yerleştirmek
- Production Package'i eksiksiz oluşturmak
- Hazır hale gelen Production Package'i WF-002'ye devretmek

HLK = WF-001. Üretim süreci boyunca tek karar verici WF-001'dir. Hiçbir ajan karar veremez. Tüm kararlar WF-001 tarafından alınır.

Link doğrulanmadan hiçbir araştırma başlatılamaz. Ürün tanınmadan araştırma başlatılmaz.

### Durum

AKTİF

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

