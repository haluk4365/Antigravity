# 14 — Olay Kayıt Merkezi

HLK içerisinde gerçekleşen tüm önemli olayların (Event) resmi standart ve kayıt dosyasıdır.

---

## 1. Amaç

HLK içerisinde gerçekleşen tüm önemli olayları (Event) standart hale getirmek, State Engine, Workflow, Feature, Module ve HLK çekirdeği arasındaki olay iletişimini tek merkezden yönetmektir.

Bu dosya;

* Hangi olayların bulunduğunu,
* Her olayın hangi bilgileri içerdiğini,
* Olayların hangi kurallara göre oluşturulduğunu,
* Olayların hangi durumlar arasında geçiş sağladığını,
* Olayların hangi Workflow, Feature ve Modüller ile ilişkili olduğunu

tanımlar.

---

## 2. Kapsam

Bu dosya HLK içerisinde aşağıdaki bileşenler arasında kullanılan tüm resmi olayları kapsar:

* Kullanıcı Oturum Olayları
* Ürün Linki Olayları
* Araştırma Olayları
* Brief Olayları
* Senaryo Olayları
* Fiyatlandırma Olayları
* Ödeme Olayları
* Video Üretim Olayları
* Revizyon Olayları
* Oturum Kapatma Olayları
* Sistem Olayları

---

## 3. Temel İlkeler

1. Olaylar yalnızca gerçekleşmiş işlemleri temsil eder.
2. Olaylar geriye dönük değiştirilemez.
3. Her olay benzersiz bir Olay Kimliğine sahip olmalıdır.
4. Her olay yalnızca bir kez oluşturulmalıdır.
5. Aynı olay tekrar üretilemez.
6. Her olay Operasyon Hafızasına kaydedilebilir olmalıdır.
7. Her olay gerektiğinde Operasyon Analiz Motoru tarafından analiz edilebilir olmalıdır.
8. Olaylar açıklanabilir ve denetlenebilir olmalıdır.
9. Olaylar mevcut HLK mimarisini değiştirmez, yalnızca bileşenler arasındaki iletişim standardını tanımlar.
10. Her olay bir Kaynak Durum ve bir Hedef Durum arasında geçiş sağlar.

---

## 4. Olay Yaşam Döngüsü

HLK içerisinde her olay aşağıdaki yaşam döngüsünü izler:

```
Olay Oluşturuldu
↓
Olay Doğrulandı
↓
Olay İşleniyor
↓
Olay Tamamlandı
↓
Operasyon Hafızasına Kaydedildi
```

### Olay Oluşturuldu

Olay, bir tetikleyici tarafından oluşturulur. Tetikleyici; kullanıcı işlemi, sistem kararı, zamanlayıcı veya başka bir olayın sonucu olabilir.

### Olay Doğrulandı

Oluşturulan olay ilgili State Engine kurallarına göre doğrulanır. Geçersiz bir olay işlenmez ve hata kaydı oluşturulur.

### Olay İşleniyor

Doğrulanan olay ilgili modül veya bileşen tarafından işlenir. Bu aşamada olaya bağlı aksiyonlar gerçekleştirilir.

### Olay Tamamlandı

Olay başarıyla işlenir. Kaynak Durumdan Hedef Duruma geçiş tamamlanır.

### Operasyon Hafızasına Kaydedildi

Tamamlanan olay MR-0005_4 HLK Operasyon Hafızasına kaydedilir ve gelecekteki analizler için kullanılabilir hale gelir.

---

## 5. Olay Veri Standardı

HLK içerisinde her olay en az aşağıdaki standart bilgileri içermelidir:

| # | Alan | Türkçe Adı | Zorunluluk |
|---|------|-----------|:----------:|
| 1 | `EventID` | Olay Kimliği (ör. OLAY-001) | Zorunlu |
| 2 | `EventName` | Olay Adı | Zorunlu |
| 3 | `EventConstant` | Teknik Sabit | Zorunlu |
| 4 | `EventDescription` | Olay Açıklaması | Zorunlu |
| 5 | `SourceState` | Kaynak Durum | Zorunlu |
| 6 | `TargetState` | Hedef Durum | Zorunlu |
| 7 | `WorkflowID` | İlgili Workflow | İsteğe Bağlı |
| 8 | `FeatureID` | İlgili Feature | İsteğe Bağlı |
| 9 | `ModuleID` | İlgili Modül | İsteğe Bağlı |
| 9.1 | `PID` | Production ID | Üretim Event'lerinde Zorunlu |
| 10 | `Producer` | Üreten Bileşen | Zorunlu |
| 11 | `Consumers` | Kullanan Bileşenler | Zorunlu |
| 12 | `Trigger` | Tetikleyici | Zorunlu |
| 13 | `Condition` | Oluşturulma Koşulu | Zorunlu |
| 14 | `Priority` | Öncelik | Zorunlu |
| 15 | `RetryPolicy` | Tekrar Deneme Politikası | Zorunlu |
| 16 | `Notifications` | Bildirim Hedefleri | Zorunlu |
| 17 | `Outputs` | Olay Çıktıları | Zorunlu |
| 18 | `NextEvent` | Sonraki Olay | İsteğe Bağlı |
| 19 | `RecordPolicy` | Kayıt Politikası | Zorunlu |
| 20 | `Result` | Sonuç | Zorunlu |
| 21 | `Timestamp` | Zaman Damgası | Zorunlu |

### Üreten Bileşen

Olayı oluşturan bileşeni tanımlar. Örneğin: HLK, State Engine, Workflow, Fiyatlandırma Modülü, Ödeme Modülü, Servis Sağlığı ve Müdahale Motoru, Operasyon Hafızası, Operasyon Analiz Motoru.

### Kullanan Bileşenler

Olayı kullanan bileşenleri tanımlar. Örneğin: Workflow, Feature, State Engine, Telegram Bildirim Sistemi, Operasyon Hafızası, Operasyon Analiz Motoru, Log Sistemi, Yönetici Bildirim Sistemi, Kullanıcı Bildirim Sistemi.

### Olay Çıktıları

Olay tamamlandığında hangi çıktıların üretileceğini tanımlar.

### Sonraki Olay

Bu olayın ardından tetiklenmesi beklenen bir sonraki olayı tanımlar.

### Tekrar Deneme Politikası

Olay işlenirken hata oluşması durumunda kaç kez tekrar deneneceğini tanımlar. Değerler: Yok, 1 kez, 3 kez, GC üzerinden yönetilir, Otomatik tekrar, Yönetici onayı gerekir.

### Bildirim Hedefleri

Olay gerçekleştiğinde hangi hedeflere bildirim gönderileceğini tanımlar. Örneğin: Telegram Kullanıcısı, Telegram Yönetici, Log Sistemi, Dashboard, Operasyon Hafızası, Analiz Motoru.

### Kayıt Politikası

Olayın hangi kayıt sistemlerine yazılacağını tanımlar. Örneğin: Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır, Raporlamaya dahil edilir.

---

## 6. Olay Türleri

### Oturum Olayları

Kullanıcı oturumunun başlatılması ve yönetimi ile ilgili olayları içerir.

### Link Olayları

Ürün linki alımı ve doğrulama ile ilgili olayları içerir.

### Araştırma Olayları

Ürün araştırması ve görsel toplama ile ilgili olayları içerir.

### Brief Olayları

Kullanıcıdan bilgi toplama süreci ile ilgili olayları içerir.

### Senaryo Olayları

Senaryo oluşturma ve onay süreci ile ilgili olayları içerir.

### Fiyatlandırma Olayları

Fiyat teklifi oluşturma, onay ve ret süreci ile ilgili olayları içerir.

### Ödeme Olayları

Ödeme süreci ile ilgili olayları içerir.

### Üretim Olayları

Video üretim süreci ile ilgili olayları içerir.

### Revizyon Olayları

Kullanıcı revizyon talepleri ile ilgili olayları içerir.

### Sistem Olayları

Sistem yönetimi ve oturum kapatma ile ilgili olayları içerir.

---

## 7. Olay Öncelik Seviyeleri

HLK içerisinde her olay bir öncelik seviyesine sahip olmalıdır.

| Seviye | Teknik Sabit | Açıklama |
|:------:|-------------|----------|
| 1 | `PRIORITY_CRITICAL` | Kritik öncelik. Sistem kesintisi veya veri kaybı riski içeren olaylar. |
| 2 | `PRIORITY_HIGH` | Yüksek öncelik. Kullanıcı deneyimini doğrudan etkileyen olaylar. |
| 3 | `PRIORITY_MEDIUM` | Orta öncelik. Normal iş akışını etkileyen olaylar. |
| 4 | `PRIORITY_LOW` | Düşük öncelik. Bilgilendirme amaçlı olaylar. |
| 5 | `PRIORITY_INFO` | Bilgi seviyesi. Sistem durumu hakkında bilgi veren olaylar. |

---

## 8. Olay İşleme Kuralları

1. Her olay oluşturulduktan sonra doğrulanmalıdır.
2. Doğrulama başarısız olursa olay işlenmez ve hata kaydı oluşturulur.
3. Her olay yalnızca bir kez işlenebilir.
4. Aynı olay tekrar işlenemez.
5. Olay işlenirken hata oluşursa ilgili State, Workflow ve Module bilgilendirilmelidir.
6. Olay işleme sırası öncelik seviyesine göre belirlenmelidir.
7. Aynı öncelik seviyesindeki olaylar oluşturulma sırasına göre işlenmelidir.

---

## 9. Olay Kayıt Kuralları

1. Her olay oluşturulduğunda kayıt altına alınmalıdır.
2. Her olay tamamlandığında kayıt altına alınmalıdır.
3. Olay kayıtları değiştirilemez.
4. Olay kayıtları silinemez.
5. Olay kayıtları yalnızca okunabilir (Read Only) olarak saklanmalıdır.
6. Olay kayıtları MR-0005_4 HLK Operasyon Hafızası ile uyumlu olmalıdır.

---

## 10. Olay Günlükleme (Log) Kuralları

1. Her olay oluşturulduğunda sistem günlüğüne yazılmalıdır.
2. Günlük kaydı en az Olay Kimliği, Teknik Sabit, Zaman Damgası ve Sonuç bilgilerini içermelidir.
3. Başarılı olaylar INFO seviyesinde günlüklenmelidir.
4. Başarısız olaylar ERROR seviyesinde günlüklenmelidir.
5. Kritik öncelikli olaylar CRITICAL seviyesinde günlüklenmelidir.
6. Günlük kayıtları saklama süresi Global Configuration (GC) parametreleri ile yönetilmelidir.

---

## 11. Operasyon Hafızası İlişkisi

Bu dosya MR-0005_4 (HLK Operasyon Hafızası) ile doğrudan ilişkilidir.

Tamamlanan her olay MR-0005_4 HLK Operasyon Hafızasına kaydedilmelidir.

Operasyon Hafızasına kaydedilen olaylar MR-0005_5 (HLK Operasyon Analiz Motoru) tarafından analiz edilebilir olmalıdır.

Olay kayıtları, Operasyon Hafızasının 23 alanlı veri standardı ile uyumlu olmalıdır.

---

## 12. State Engine İlişkisi

Bu dosya SE-007_3 (User Conversation State Architecture), SE-007_4 (User Conversation State Transition Rules) ve SE-007_5 (State Event Trigger Architecture) ile doğrudan ilişkilidir.

Her olay bir Kaynak Durum (Source State) ve bir Hedef Durum (Target State) arasında geçiş sağlar.

Olay tanımları SE-007_5 içerisindeki event akışları ile tutarlı olmalıdır.

Yeni bir olay eklendiğinde SE-007_5 içerisindeki event tanımları da güncellenmelidir.

---

## 13. Workflow İlişkisi

Bu dosya 09_WORKFLOW_MANIFEST.md ile doğrudan ilişkilidir.

Her olay bir veya birden fazla Workflow tarafından kullanılabilir.

Olaylar Workflow'ların hangi aşamada olduğunu belirlemek için kullanılabilir.

Workflow içerisinde bir sonraki adıma geçiş, ilgili olayın oluşturulması ile tetiklenir.

---

## 14. Feature İlişkisi

Bu dosya 10_FEATURE_REGISTRY.md ile doğrudan ilişkilidir.

Her olay bir veya birden fazla Feature tarafından kullanılabilir.

Feature'ların hangi durumda olduğu ilgili olaylar aracılığıyla takip edilebilir.

---

## 15. Module İlişkisi

Bu dosya 06_Module_Rule.md ile doğrudan ilişkilidir.

Her olay bir veya birden fazla Modül tarafından işlenebilir.

MR-0005_3 (HLK Servis Sağlığı ve Müdahale Motoru) tarafından üretilen operasyon verileri olaylar aracılığıyla diğer modüllere iletilir.

MR-0005_4 (HLK Operasyon Hafızası) tamamlanan tüm olayları kayıt altına alır.

MR-0005_5 (HLK Operasyon Analiz Motoru) kayıtlı olayları analiz ederek karar mekanizmalarını iyileştirir.

---

## 16. Güvenlik Kuralları

1. Olay kayıtları yalnızca yetkili bileşenler tarafından okunabilir.
2. Olay kayıtları değiştirilemez ve silinemez.
3. Olay oluşturma yetkisi yalnızca ilgili State, Workflow veya Module'e aittir.
4. Hiçbir dış bileşen doğrudan olay oluşturamaz.
5. Olay kayıtları denetlenebilir olmalıdır.
6. Olay kayıtları gerektiğinde yönetici raporlarına dahil edilebilmelidir.

---

## 17. Başlangıç Olayları

### Oturum Olayları

---

### OLAY-001 — EVENT_SESSION_STARTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-001 |
| Teknik Sabit | `EVENT_SESSION_STARTED` |
| Olay Adı | Oturum Başlatıldı |
| Açıklama | Kullanıcının botu başlatması ile oturum açılır. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_START` |
| Hedef Durum | `STATE_SCENE_1` |
| İlgili Workflow | Tüm Workflow'lar |
| İlgili Feature | FEAT-003 |
| Tetikleyici | Kullanıcı `/start` komutu |
| Oluşturulma Koşulu | Kullanıcı botu başlattığında |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_SCENE_1 başlatılır → SAHNE-1 videosu hazırlanır |
| Sonraki Olay | EVENT_LANGUAGE_SELECTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Oturum başarıyla başlatıldı |

---

### OLAY-028 — EVENT_SESSION_CLOSED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-028 |
| Teknik Sabit | `EVENT_SESSION_CLOSED` |
| Olay Adı | Oturum Kapatıldı |
| Açıklama | Oturumun başarıyla veya hata ile sonlandırılması. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Log Sistemi, Operasyon Hafızası, Operasyon Analiz Motoru |
| Kaynak Durum | `STATE_SESSION_CLOSED` |
| Hedef Durum | - |
| İlgili Workflow | Tüm Workflow'lar |
| İlgili Feature | FEAT-003 |
| Tetikleyici | Oturum sonlandırma kararı |
| Oluşturulma Koşulu | Oturum kapatılırken |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | Kaynak temizlenir → Oturum kapatılır → Operasyon Hafızasına yazılır |
| Sonraki Olay | - |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası, Operasyon Analiz Motoru |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır, Raporlamaya dahil edilir |
| Sonuç | Oturum başarıyla kapatıldı |

### OLAY-035 — EVENT_SCENE_1_COMPLETED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-035 |
| Teknik Sabit | `EVENT_SCENE_1_COMPLETED` |
| Olay Adı | SAHNE-01 Tamamlandı |
| Açıklama | HLK karşılama videosu (SAHNE-01) başarıyla oynatıldı ve kaldırıldı. Kullanıcı dil seçimi aşamasına yönlendirilir. |
| Üreten Bileşen | Scene Engine |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_SCENE_1` |
| Hedef Durum | `STATE_LANGUAGE_SELECTION` |
| İlgili Workflow | Tüm Workflow'lar |
| İlgili Feature | FEAT-003, FEAT-009 |
| Tetikleyici | SAHNE-01 video oynatımının tamamlanması |
| Oluşturulma Koşulu | SAHNE-01 videosu son kareye ulaştığında ve Scene Cleanup tamamlandığında |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_LANGUAGE_SELECTION başlatılır → Dil seçim butonları gösterilir |
| Sonraki Olay | EVENT_LANGUAGE_SELECTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | SAHNE-01 başarıyla tamamlandı, dil seçimi başlatıldı |

---

### OLAY-036 — EVENT_SCENE_2_COMPLETED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-036 |
| Teknik Sabit | `EVENT_SCENE_2_COMPLETED` |
| Olay Adı | SAHNE-02 Tamamlandı |
| Açıklama | Dile özel AHU lip-sync karşılama videosu (SAHNE-02) başarıyla oynatıldı ve kaldırıldı. Kullanıcı ürün linki girişine yönlendirilir. |
| Üreten Bileşen | Scene Engine |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_SCENE_2` |
| Hedef Durum | `STATE_WAIT_PRODUCT_LINK` |
| İlgili Workflow | WF-001 |
| İlgili Feature | FEAT-003, FEAT-009 |
| Tetikleyici | SAHNE-02 video oynatımının tamamlanması |
| Oluşturulma Koşulu | SAHNE-02 videosu son kareye ulaştığında ve Scene Cleanup tamamlandığında |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_WAIT_PRODUCT_LINK başlatılır → Ürün linki istenir |
| Sonraki Olay | EVENT_PRODUCT_LINK_RECEIVED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | SAHNE-02 başarıyla tamamlandı, ürün linki bekleniyor |

---

### Dil Seçim Olayları

---

### OLAY-002 — EVENT_LANGUAGE_SELECTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-002 |
| Teknik Sabit | `EVENT_LANGUAGE_SELECTED` |
| Olay Adı | Dil Seçildi |
| Açıklama | Kullanıcının 8 dil arasından birini seçmesi. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Telegram Bildirim Sistemi |
| Kaynak Durum | `STATE_LANGUAGE_SELECTION` |
| Hedef Durum | `STATE_SCENE_2` |
| İlgili Workflow | WF-001 |
| İlgili Feature | FEAT-003 |
| Tetikleyici | Kullanıcı dil seçimi |
| Oluşturulma Koşulu | Kullanıcı bir dil seçtiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_SCENE_2 başlatılır → Seçilen dilde SAHNE-2 videosu hazırlanır |
| Sonraki Olay | EVENT_PRODUCT_LINK_RECEIVED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Dil seçimi başarıyla kaydedildi |

---

### Link Olayları

---

### OLAY-003 — EVENT_PRODUCT_LINK_RECEIVED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-003 |
| Teknik Sabit | `EVENT_PRODUCT_LINK_RECEIVED` |
| Olay Adı | Ürün Linki Alındı |
| Açıklama | Kullanıcı tarafından ürün linki gönderildi. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Log Sistemi |
| Kaynak Durum | `STATE_WAIT_PRODUCT_LINK` |
| Hedef Durum | `STATE_LINK_VALIDATION` |
| İlgili Workflow | WF-001 |
| İlgili Feature | FEAT-001 |
| Tetikleyici | Kullanıcı link gönderimi |
| Oluşturulma Koşulu | Kullanıcı geçerli bir link gönderdiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_LINK_VALIDATION başlatılır → Link doğrulama süreci başlar |
| Sonraki Olay | EVENT_PRODUCT_LINK_VALIDATED veya EVENT_PRODUCT_LINK_REJECTED |
| Tekrar Deneme Politikası | GC üzerinden yönetilir |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Link doğrulama süreci başlatıldı |

---

### OLAY-004 — EVENT_PRODUCT_LINK_VALIDATED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-004 |
| Teknik Sabit | `EVENT_PRODUCT_LINK_VALIDATED` |
| Olay Adı | Ürün Linki Doğrulandı |
| Açıklama | Gönderilen ürün linki tüm doğrulama kriterlerini başarıyla geçti. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_LINK_VALIDATION` |
| Hedef Durum | `STATE_LINK_VALIDATED` |
| İlgili Workflow | WF-001 |
| İlgili Feature | FEAT-001, FEAT-002 |
| Tetikleyici | Link doğrulama başarısı |
| Oluşturulma Koşulu | Link tüm doğrulama kriterlerini geçtiğinde |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | STATE_LINK_VALIDATED → Ürün Referans Paketi oluşturulur → Araştırma başlatılır |
| Sonraki Olay | EVENT_PRODUCT_ANALYSIS_STARTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası, Telegram Kullanıcısı |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır |
| Sonuç | Link başarıyla doğrulandı, araştırma süreci başlatıldı |

---

### OLAY-005 — EVENT_PRODUCT_LINK_REJECTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-005 |
| Teknik Sabit | `EVENT_PRODUCT_LINK_REJECTED` |
| Olay Adı | Ürün Linki Reddedildi |
| Açıklama | Gönderilen ürün linki doğrulama kriterlerini karşılamadı. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Log Sistemi |
| Kaynak Durum | `STATE_LINK_VALIDATION` |
| Hedef Durum | `STATE_WAIT_PRODUCT_LINK` |
| İlgili Workflow | WF-001 |
| İlgili Feature | FEAT-001, FEAT-002 |
| Tetikleyici | Link doğrulama başarısızlığı |
| Oluşturulma Koşulu | Link doğrulama kriterlerini karşılamadığında |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_WAIT_PRODUCT_LINK → Kullanıcıya hata bildirilir → Yeni link beklenir |
| Sonraki Olay | EVENT_PRODUCT_LINK_RECEIVED |
| Tekrar Deneme Politikası | GC üzerinden yönetilir |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Link reddedildi, kullanıcı yeni link bekleniyor |

---

### Araştırma Olayları

---

### OLAY-006 — EVENT_PRODUCT_ANALYSIS_STARTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-006 |
| Teknik Sabit | `EVENT_PRODUCT_ANALYSIS_STARTED` |
| Olay Adı | Ürün Analizi Başlatıldı |
| Açıklama | Link doğrulandıktan sonra arka plan araştırma süreci başlatıldı. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_LINK_VALIDATED` |
| Hedef Durum | `STATE_BACKGROUND_RESEARCH_RUNNING` |
| İlgili Workflow | WF-002 |
| İlgili Feature | FEAT-004, FEAT-005, FEAT-006 |
| Tetikleyici | Link doğrulama başarısı |
| Oluşturulma Koşulu | Link doğrulandıktan hemen sonra |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | STATE_BACKGROUND_RESEARCH_RUNNING → Ajan görevleri oluşturulur → Araştırma başlar |
| Sonraki Olay | EVENT_IMAGES_RECEIVED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Arka plan araştırması başlatıldı |

---

### OLAY-007 — EVENT_IMAGES_RECEIVED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-007 |
| Teknik Sabit | `EVENT_IMAGES_RECEIVED` |
| Olay Adı | Görseller Alındı |
| Açıklama | Araştırma ajanı tarafından yeni bir ürün görseli bulundu. |
| Üreten Bileşen | Workflow |
| Kullanan Bileşenler | Feature, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_BACKGROUND_RESEARCH_RUNNING` |
| Hedef Durum | `STATE_BACKGROUND_RESEARCH_RUNNING` |
| İlgili Workflow | WF-002 |
| İlgili Feature | FEAT-005 |
| Tetikleyici | Araştırma ajanı görsel buldu |
| Oluşturulma Koşulu | Araştırma sırasında yeni görsel elde edildiğinde |
| Öncelik | `PRIORITY_LOW` |
| Olay Çıktıları | Görsel bilgi değeri analiz edilir → Araştırma sonucuna eklenir |
| Sonraki Olay | EVENT_IMAGES_COMPLETED |
| Tekrar Deneme Politikası | Otomatik tekrar |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Görsel araştırma sonucuna eklendi |

---

### OLAY-008 — EVENT_IMAGES_COMPLETED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-008 |
| Teknik Sabit | `EVENT_IMAGES_COMPLETED` |
| Olay Adı | Görsel Araştırması Tamamlandı |
| Açıklama | Görsel araştırma süreci tamamlandı. |
| Üreten Bileşen | Workflow |
| Kullanan Bileşenler | State Engine, Feature, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_BACKGROUND_RESEARCH_RUNNING` |
| Hedef Durum | `STATE_BACKGROUND_RESEARCH_RUNNING` |
| İlgili Workflow | WF-002 |
| İlgili Feature | FEAT-005 |
| Tetikleyici | Araştırma tamamlanma koşulu |
| Oluşturulma Koşulu | GC_IMAGE_MAX_COUT veya GC_IMAGE_RESEARCH_TIMEOUT |
| Öncelik | `PRIORITY_LOW` |
| Olay Çıktıları | Araştırma sonuçları kaydedilir → Analiz için hazırlanır |
| Sonraki Olay | EVENT_BRIEF_COMPLETED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Görsel araştırması tamamlandı |

---

### Brief Olayları

---

### OLAY-009 — EVENT_BRIEF_COMPLETED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-009 |
| Teknik Sabit | `EVENT_BRIEF_COMPLETED` |
| Olay Adı | Brief Tamamlandı |
| Açıklama | Kullanıcıdan tüm brief bilgileri başarıyla toplandı ve onaylandı. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_BRIEF_COMPLETED` |
| Hedef Durum | `STATE_SCENARIO_APPROVAL` |
| İlgili Workflow | WF-003 |
| İlgili Feature | FEAT-002, FEAT-003 |
| Tetikleyici | Kullanıcı brief onayı |
| Oluşturulma Koşulu | Kullanıcı brief'i onayladığında |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | STATE_SCENARIO_APPROVAL → Senaryo oluşturma süreci başlatılır |
| Sonraki Olay | EVENT_SCENARIO_CREATED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası, Telegram Kullanıcısı |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Brief tamamlandı, senaryo süreci başlatıldı |

---

### OLAY-038 — EVENT_MATERIAL_REQUEST_STARTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-038 |
| Teknik Sabit | `EVENT_MATERIAL_REQUEST_STARTED` |
| Olay Adı | Materyal Talep Süreci Başlatıldı |
| Açıklama | Arka plan araştırması tamamlandıktan sonra kullanıcıdan tamamlayıcı ürün materyalleri talep edilmeye başlandı. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Scene Engine, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_BACKGROUND_RESEARCH_RUNNING` |
| Hedef Durum | `STATE_COLLECT_PRODUCT_MATERIALS` |
| İlgili Workflow | WF-003 |
| İlgili Feature | FEAT-002, FEAT-003 |
| Tetikleyici | Araştırma sürecinin tamamlanması |
| Oluşturulma Koşulu | STATE_BACKGROUND_RESEARCH_RUNNING sonrası Conversation Scene Engine aktif konuşmayı başlattığında |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_COLLECT_PRODUCT_MATERIALS başlatılır → Tamamlayıcı materyal bilgilendirme sahnesi gösterilir |
| Sonraki Olay | EVENT_MATERIAL_COLLECTION_COMPLETED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Materyal talep süreci başlatıldı |

---

### OLAY-039 — EVENT_MATERIAL_COLLECTION_COMPLETED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-039 |
| Teknik Sabit | `EVENT_MATERIAL_COLLECTION_COMPLETED` |
| Olay Adı | Materyal Toplama Tamamlandı |
| Açıklama | Kullanıcı tamamlayıcı materyal yükleme işlemini tamamladı veya atladı. Platform seçimi aşamasına geçilir. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Material Upload Module, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_COLLECT_PRODUCT_MATERIALS` |
| Hedef Durum | `STATE_PLATFORM_SELECTION` |
| İlgili Workflow | WF-003 |
| İlgili Feature | FEAT-002, FEAT-003 |
| Tetikleyici | Kullanıcı "Bitti" butonu veya materyal yok seçeneği |
| Oluşturulma Koşulu | Materyal yükleme modu sonlandığında veya kullanıcı geç seçeneğini kullandığında |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_PLATFORM_SELECTION başlatılır → Platform seçenekleri gösterilir |
| Sonraki Olay | EVENT_PLATFORM_SELECTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Materyal toplama tamamlandı, platform seçimi başlatıldı |

---

### OLAY-040 — EVENT_PLATFORM_SELECTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-040 |
| Teknik Sabit | `EVENT_PLATFORM_SELECTED` |
| Olay Adı | Platform Seçildi |
| Açıklama | Kullanıcı reklam videosu için hedef platformu seçti. Çözünürlük seçimi aşamasına geçilir. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi |
| Kaynak Durum | `STATE_PLATFORM_SELECTION` |
| Hedef Durum | `STATE_VIDEO_RESOLUTION_SELECTION` |
| İlgili Workflow | WF-003 |
| İlgili Feature | FEAT-002, FEAT-003 |
| Tetikleyici | Kullanıcı platform seçimi |
| Oluşturulma Koşulu | Kullanıcı bir platform seçeneğini seçtiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_VIDEO_RESOLUTION_SELECTION başlatılır → Çözünürlük seçenekleri gösterilir |
| Sonraki Olay | EVENT_RESOLUTION_SELECTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Platform seçildi, çözünürlük seçimi başlatıldı |

---

### OLAY-041 — EVENT_RESOLUTION_SELECTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-041 |
| Teknik Sabit | `EVENT_RESOLUTION_SELECTED` |
| Olay Adı | Video Çözünürlüğü Seçildi |
| Açıklama | Kullanıcı reklam videosu için hedef çözünürlüğü seçti. Video süresi seçimi aşamasına geçilir. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi |
| Kaynak Durum | `STATE_VIDEO_RESOLUTION_SELECTION` |
| Hedef Durum | `STATE_VIDEO_DURATION_SELECTION` |
| İlgili Workflow | WF-003 |
| İlgili Feature | FEAT-002, FEAT-003 |
| Tetikleyici | Kullanıcı çözünürlük seçimi |
| Oluşturulma Koşulu | Kullanıcı bir çözünürlük seçeneğini seçtiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_VIDEO_DURATION_SELECTION başlatılır → Süre seçenekleri gösterilir |
| Sonraki Olay | EVENT_DURATION_SELECTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Çözünürlük seçildi, süre seçimi başlatıldı |

---

### OLAY-042 — EVENT_DURATION_SELECTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-042 |
| Teknik Sabit | `EVENT_DURATION_SELECTED` |
| Olay Adı | Video Süresi Seçildi |
| Açıklama | Kullanıcı reklam videosu için hedef süreyi seçti veya HLK'ya bıraktı. Ses yapılandırması aşamasına geçilir. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi |
| Kaynak Durum | `STATE_VIDEO_DURATION_SELECTION` |
| Hedef Durum | `STATE_AUDIO_SELECTION` |
| İlgili Workflow | WF-003 |
| İlgili Feature | FEAT-002, FEAT-003 |
| Tetikleyici | Kullanıcı süre girişi veya "HLK'ya Bırak" seçimi |
| Oluşturulma Koşulu | Geçerli bir video süresi belirlendiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_AUDIO_SELECTION başlatılır → Ses seçenekleri gösterilir |
| Sonraki Olay | EVENT_AUDIO_OPTION_SELECTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Video süresi seçildi, ses yapılandırması başlatıldı |

---

### OLAY-043 — EVENT_AUDIO_OPTION_SELECTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-043 |
| Teknik Sabit | `EVENT_AUDIO_OPTION_SELECTED` |
| Olay Adı | Ses Yapılandırması Tamamlandı |
| Açıklama | Kullanıcı ses, dil, karakter ve vurgu tercihlerini tamamladı. Brief tamamlanma aşamasına geçilir. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_AUDIO_SELECTION` |
| Hedef Durum | `STATE_BRIEF_COMPLETED` |
| İlgili Workflow | WF-003 |
| İlgili Feature | FEAT-002, FEAT-003 |
| Tetikleyici | Kullanıcı ses tercihlerini tamamlaması |
| Oluşturulma Koşulu | Ses seçenekleri tamamlandığında veya sessiz video seçildiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_BRIEF_COMPLETED başlatılır → Brief özeti gösterilir |
| Sonraki Olay | EVENT_BRIEF_APPROVED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Ses yapılandırması tamamlandı, brief özeti gösterildi |

---

### OLAY-044 — EVENT_BRIEF_APPROVED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-044 |
| Teknik Sabit | `EVENT_BRIEF_APPROVED` |
| Olay Adı | Brief Onaylandı |
| Açıklama | Kullanıcı brief özetini kontrol etti ve tüm bilgileri onayladı. Senaryo onayı aşamasına geçilir. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_BRIEF_COMPLETED` |
| Hedef Durum | `STATE_SCENARIO_APPROVAL` |
| İlgili Workflow | WF-004 |
| İlgili Feature | FEAT-002, FEAT-003 |
| Tetikleyici | Kullanıcı brief onayı |
| Oluşturulma Koşulu | Kullanıcı brief özetindeki tüm alanları onayladığında |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | STATE_SCENARIO_APPROVAL başlatılır → Senaryo hazırlanır ve onaya sunulur |
| Sonraki Olay | EVENT_SCENARIO_CREATED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası, Telegram Kullanıcısı |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Brief onaylandı, senaryo onayı başlatıldı |

---

### Senaryo Olayları

---

### OLAY-010 — EVENT_SCENARIO_CREATED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-010 |
| Teknik Sabit | `EVENT_SCENARIO_CREATED` |
| Olay Adı | Senaryo Oluşturuldu |
| Açıklama | Brief verileri kullanılarak reklam senaryosu hazırlandı. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Log Sistemi, Telegram Bildirim Sistemi |
| Kaynak Durum | `STATE_SCENARIO_APPROVAL` |
| Hedef Durum | `STATE_SCENARIO_APPROVAL` |
| İlgili Workflow | WF-005 |
| İlgili Feature | FEAT-007 |
| Tetikleyici | Brief tamamlanması |
| Oluşturulma Koşulu | Brief onaylandıktan sonra senaryo hazırlandığında |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | Senaryo metni oluşturulur → Kullanıcı onayına sunulur |
| Sonraki Olay | EVENT_SCENARIO_APPROVED veya EVENT_SCENARIO_REJECTED |
| Tekrar Deneme Politikası | 1 kez |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Senaryo başarıyla oluşturuldu |

---

### OLAY-011 — EVENT_SCENARIO_APPROVED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-011 |
| Teknik Sabit | `EVENT_SCENARIO_APPROVED` |
| Olay Adı | Senaryo Onaylandı |
| Açıklama | Kullanıcı tarafından senaryo onaylandı ve fiyatlandırma sürecine geçildi. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Log Sistemi, Operasyon Hafızası, Yönetici Bildirim Sistemi |
| Kaynak Durum | `STATE_SCENARIO_APPROVAL` |
| Hedef Durum | `STATE_PRICING` |
| İlgili Workflow | WF-006 |
| İlgili Feature | FEAT-002, FEAT-003 |
| Tetikleyici | Kullanıcı onayı |
| Oluşturulma Koşulu | Kullanıcı senaryoyu onayladığında |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | STATE_PRICING → Yönetici Fiyatlandırma Formu hazırlanır → Log Kaydı → Operasyon Hafızası Kaydı → Yönetici Bildirimi |
| Sonraki Olay | EVENT_PRICING_STARTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası, Telegram Yönetici, Telegram Kullanıcısı |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır |
| Sonuç | Senaryo onaylandı, fiyatlandırma süreci başlatıldı |

---

### OLAY-012 — EVENT_SCENARIO_REJECTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-012 |
| Teknik Sabit | `EVENT_SCENARIO_REJECTED` |
| Olay Adı | Senaryo Reddedildi |
| Açıklama | Kullanıcı tarafından senaryo reddedildi ve oturum kapatıldı. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_SCENARIO_APPROVAL` |
| Hedef Durum | `STATE_SESSION_CLOSED` |
| İlgili Workflow | WF-006 |
| İlgili Feature | FEAT-002, FEAT-003 |
| Tetikleyici | Kullanıcı reddi |
| Oluşturulma Koşulu | Kullanıcı senaryoyu reddettiğinde |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | STATE_SESSION_CLOSED → Oturum sonlandırılır → Operasyon Hafızasına kaydedilir |
| Sonraki Olay | EVENT_SESSION_CLOSED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası, Telegram Kullanıcısı |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Raporlamaya dahil edilir |
| Sonuç | Senaryo reddedildi, oturum kapatıldı |

---

### Fiyatlandırma Olayları

---

### OLAY-013 — EVENT_PRICING_STARTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-013 |
| Teknik Sabit | `EVENT_PRICING_STARTED` |
| Olay Adı | Fiyatlandırma Başlatıldı |
| Açıklama | Senaryo onayı sonrası fiyatlandırma süreci başlatıldı ve Yönetici Formu hazırlandı. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Fiyatlandırma Modülü, Yönetici Bildirim Sistemi, Log Sistemi |
| Kaynak Durum | `STATE_PRICING` |
| Hedef Durum | `STATE_PRICING` |
| İlgili Workflow | WF-007 |
| İlgili Feature | FEAT-002, FEAT-003, FEAT-011, FEAT-012 |
| Tetikleyici | Senaryo onayı |
| Oluşturulma Koşulu | Senaryo onaylandıktan sonra |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | Yönetici Fiyatlandırma Formu oluşturulur → Yöneticiye gönderilir → Log Kaydı → Operasyon Hafızası |
| Sonraki Olay | EVENT_PRICE_APPROVED veya EVENT_PRICE_REJECTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Telegram Yönetici, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Fiyatlandırma süreci başlatıldı, Yönetici Formu hazırlandı |

---

### OLAY-014 — EVENT_PRICE_APPROVED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-014 |
| Teknik Sabit | `EVENT_PRICE_APPROVED` |
| Olay Adı | Yönetici Fiyatı Onayladı |
| Açıklama | Yönetici satış fiyatını belirledi ve onayladı. Kullanıcı Teklif Formu oluşturuldu. |
| Üreten Bileşen | Fiyatlandırma Modülü |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Telegram Bildirim Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_PRICING` |
| Hedef Durum | `STATE_PRICING` |
| İlgili Workflow | WF-007 |
| İlgili Feature | FEAT-011 |
| Tetikleyici | Yönetici onayı |
| Oluşturulma Koşulu | Yönetici satış fiyatını onayladığında |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | Kullanıcı Teklif Formu oluşturulur → Kullanıcıya gönderilir → Log Kaydı |
| Sonraki Olay | EVENT_OFFER_CREATED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Fiyat onaylandı, Kullanıcı Teklif Formu oluşturuldu |

---

### OLAY-015 — EVENT_PRICE_REJECTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-015 |
| Teknik Sabit | `EVENT_PRICE_REJECTED` |
| Olay Adı | Yönetici Fiyatı Reddetti |
| Açıklama | Yönetici fiyatlandırma işlemini iptal etti ve oturum kapatıldı. |
| Üreten Bileşen | Fiyatlandırma Modülü |
| Kullanan Bileşenler | State Engine, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_PRICING` |
| Hedef Durum | `STATE_SESSION_CLOSED` |
| İlgili Workflow | WF-007 |
| İlgili Feature | FEAT-011 |
| Tetikleyici | Yönetici reddi |
| Oluşturulma Koşulu | Yönetici fiyatlandırma işlemini iptal ettiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_SESSION_CLOSED → Oturum sonlandırılır → Operasyon Hafızasına kaydedilir |
| Sonraki Olay | EVENT_SESSION_CLOSED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası, Telegram Yönetici |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Fiyatlandırma iptal edildi, oturum kapatıldı |

---

### OLAY-016 — EVENT_OFFER_CREATED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-016 |
| Teknik Sabit | `EVENT_OFFER_CREATED` |
| Olay Adı | Teklif Oluşturuldu |
| Açıklama | Yönetici onayı sonrası kullanıcı için teklif formu hazırlandı. |
| Üreten Bileşen | Fiyatlandırma Modülü |
| Kullanan Bileşenler | Workflow, Feature, Operasyon Hafızası |
| Kaynak Durum | `STATE_PRICING` |
| Hedef Durum | `STATE_PRICING` |
| İlgili Workflow | WF-007 |
| İlgili Feature | FEAT-012 |
| Tetikleyici | Yönetici fiyat onayı |
| Oluşturulma Koşulu | Yönetici fiyatı onayladıktan sonra teklif hazırlandığında |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | Kullanıcı Teklif Formu hazırlanır → Gönderime hazır |
| Sonraki Olay | EVENT_OFFER_SENT |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Kullanıcı teklif formu oluşturuldu |

---

### OLAY-017 — EVENT_OFFER_SENT

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-017 |
| Teknik Sabit | `EVENT_OFFER_SENT` |
| Olay Adı | Teklif Gönderildi |
| Açıklama | Kullanıcı Fiyat Teklif Formu kullanıcıya başarıyla iletildi. |
| Üreten Bileşen | Fiyatlandırma Modülü |
| Kullanan Bileşenler | Workflow, Telegram Bildirim Sistemi, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_PRICING` |
| Hedef Durum | `STATE_PRICING` |
| İlgili Workflow | WF-007 |
| İlgili Feature | FEAT-012 |
| Tetikleyici | Teklifin kullanıcıya gönderilmesi |
| Oluşturulma Koşulu | Kullanıcı Fiyat Teklif Formu kullanıcıya iletildiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | Teklif kullanıcıya iletilir → Kullanıcı onayı beklenir |
| Sonraki Olay | EVENT_OFFER_ACCEPTED veya EVENT_OFFER_REJECTED |
| Tekrar Deneme Politikası | 3 kez |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Teklif kullanıcıya başarıyla gönderildi |

---

### OLAY-018 — EVENT_OFFER_ACCEPTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-018 |
| Teknik Sabit | `EVENT_OFFER_ACCEPTED` |
| Olay Adı | Teklif Kabul Edildi |
| Açıklama | Kullanıcı teklifi onayladı ve ödeme süreci başlatıldı. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Ödeme Modülü, Log Sistemi, Operasyon Hafızası, Yönetici Bildirim Sistemi |
| Kaynak Durum | `STATE_PRICING` |
| Hedef Durum | `STATE_PAYMENT_VERIFICATION` |
| İlgili Workflow | WF-007 |
| İlgili Feature | FEAT-012 |
| Tetikleyici | Kullanıcı onayı |
| Oluşturulma Koşulu | Kullanıcı teklifi onayladığında |
| Öncelik | `PRIORITY_CRITICAL` |
| Olay Çıktıları | STATE_PAYMENT_VERIFICATION → Ödeme doğrulama süreci başlar → Log Kaydı → Operasyon Hafızası → Yönetici Bildirimi |
| Sonraki Olay | EVENT_PAYMENT_DECLARED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı, Telegram Yönetici, Operasyon Hafızası, Dashboard |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır, Raporlamaya dahil edilir |
| Sonuç | Teklif kabul edildi, ödeme süreci başlatıldı |

---

### OLAY-019 — EVENT_OFFER_REJECTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-019 |
| Teknik Sabit | `EVENT_OFFER_REJECTED` |
| Olay Adı | Teklif Reddedildi |
| Açıklama | Kullanıcı teklifi reddetti ve oturum sonlandırıldı. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Log Sistemi, Operasyon Hafızası, Operasyon Analiz Motoru |
| Kaynak Durum | `STATE_PRICING` |
| Hedef Durum | `STATE_SESSION_CLOSED` |
| İlgili Workflow | WF-007 |
| İlgili Feature | FEAT-012 |
| Tetikleyici | Kullanıcı reddi |
| Oluşturulma Koşulu | Kullanıcı teklifi reddettiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | STATE_SESSION_CLOSED → Oturum sonlandırılır → Revizyon veya kapatma |
| Sonraki Olay | EVENT_SESSION_CLOSED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası, Telegram Yönetici |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır |
| Sonuç | Teklif reddedildi, oturum sonlandırıldı |

---

### Ödeme Olayları

---

### OLAY-020 — EVENT_PAYMENT_STARTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-020 |
| Teknik Sabit | `EVENT_PAYMENT_STARTED` |
| Olay Adı | Ödeme Başlatıldı |
| Açıklama | Kullanıcı teklif onayı sonrası STATE_PAYMENT_VERIFICATION aşamasına geçildi. Kullanıcının ödeme yapması bekleniyor. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_PRICING` |
| Hedef Durum | `STATE_PAYMENT_VERIFICATION` |
| İlgili Workflow | WF-007 |
| Tetikleyici | Kullanıcı teklif onayı |
| Oluşturulma Koşulu | Kullanıcı teklifi onayladıktan sonra |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | STATE_PAYMENT_VERIFICATION başlatılır → Kullanıcı ödeme beklenir |
| Sonraki Olay | EVENT_PAYMENT_DECLARED |
| Tekrar Deneme Politikası | GC üzerinden yönetilir |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Ödeme doğrulama süreci başlatıldı |

---

### OLAY-021 — EVENT_PAYMENT_COMPLETED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-021 |
| Teknik Sabit | `EVENT_PAYMENT_COMPLETED` |
| Olay Adı | Ödeme Tamamlandı |
| Açıklama | Ödeme başarıyla tamamlandı ve video üretim süreci başlatıldı. |
| Üreten Bileşen | Ödeme Modülü |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Operasyon Hafızası, Yönetici Bildirim Sistemi, Telegram Bildirim Sistemi |
| Kaynak Durum | `STATE_VIDEO_PRODUCTION` |
| Hedef Durum | `STATE_VIDEO_PRODUCTION` |
| İlgili Workflow | WF-007 |
| Tetikleyici | Ödeme onayı |
| Oluşturulma Koşulu | Ödeme başarıyla tamamlandığında |
| Öncelik | `PRIORITY_CRITICAL` |
| Olay Çıktıları | Video üretim süreci başlatılır → Kullanıcıya bildirim → Log Kaydı → Operasyon Hafızası |
| Sonraki Olay | EVENT_VIDEO_PRODUCTION_STARTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı, Telegram Yönetici, Operasyon Hafızası, Dashboard |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Raporlamaya dahil edilir |
| Sonuç | Ödeme onaylandı, video üretim süreci başlatıldı |

---

### OLAY-022 — EVENT_PAYMENT_FAILED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-022 |
| Teknik Sabit | `EVENT_PAYMENT_FAILED` |
| Olay Adı | Ödeme Başarısız Oldu |
| Açıklama | Ödeme işlemi başarısız oldu ve oturum hata durumunda kapatıldı. |
| Üreten Bileşen | Ödeme Modülü |
| Kullanan Bileşenler | State Engine, Log Sistemi, Operasyon Hafızası, Yönetici Bildirim Sistemi |
| Kaynak Durum | `STATE_VIDEO_PRODUCTION` |
| Hedef Durum | `STATE_SESSION_CLOSED` |
| İlgili Workflow | WF-007 |
| Tetikleyici | Ödeme hatası |
| Oluşturulma Koşulu | Ödeme işlemi başarısız olduğunda |
| Öncelik | `PRIORITY_CRITICAL` |
| Olay Çıktıları | Hata kaydı oluşturulur → Yönetici bilgilendirilir → Oturum kapatılır |
| Sonraki Olay | EVENT_SESSION_CLOSED |
| Tekrar Deneme Politikası | GC üzerinden yönetilir |
| Bildirim Hedefleri | Log Sistemi, Telegram Yönetici, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır |
| Sonuç | Ödeme başarısız, oturum hata durumunda kapatıldı |

---

### OLAY-029 — EVENT_PAYMENT_DECLARED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-029 |
| Teknik Sabit | `EVENT_PAYMENT_DECLARED` |
| Olay Adı | Ödeme Bildirimi Alındı |
| Açıklama | Kullanıcı "ÖDEMEM GERÇEKLEŞTİ" butonuna basarak ödeme yaptığını bildirdi. Yönetici Ödeme Onay Formu hazırlandı ve yöneticiye gönderildi. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Yönetici Bildirim Sistemi, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_PAYMENT_VERIFICATION` |
| Hedef Durum | `STATE_PAYMENT_VERIFICATION` |
| İlgili Workflow | WF-007 |
| İlgili Feature | FEAT-012 |
| Tetikleyici | Kullanıcı "ÖDEMEM GERÇEKLEŞTİ" butonu |
| Oluşturulma Koşulu | Kullanıcı ödeme yaptığını bildirdiğinde |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | Yönetici Ödeme Onay Formu oluşturulur → Yöneticiye gönderilir → Banka hesabı kontrolü beklenir → Log Kaydı → Operasyon Hafızası |
| Sonraki Olay | EVENT_PAYMENT_APPROVED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Telegram Yönetici, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Kullanıcı ödeme bildirimi alındı, yönetici onayı bekleniyor |

---

### OLAY-030 — EVENT_PAYMENT_APPROVED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-030 |
| Teknik Sabit | `EVENT_PAYMENT_APPROVED` |
| Olay Adı | Ödeme Yönetici Tarafından Onaylandı |
| Açıklama | Yönetici banka hesabını kontrol etti ve ödemenin ulaştığını doğruladı. Video üretim süreci başlatıldı. |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Telegram Bildirim Sistemi, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_PAYMENT_VERIFICATION` |
| Hedef Durum | `STATE_VIDEO_PRODUCTION` |
| İlgili Workflow | WF-007 |
| İlgili Feature | FEAT-011 |
| Tetikleyici | Yönetici "ÖDEMEYİ ONAYLA" butonu |
| Oluşturulma Koşulu | Yönetici banka hesabını kontrol edip ödemenin ulaştığını onayladığında |
| Öncelik | `PRIORITY_CRITICAL` |
| Olay Çıktıları | STATE_VIDEO_PRODUCTION başlatılır → Kullanıcıya "Ödemenizi aldık, video üretiminiz başlatılmıştır" mesajı gönderilir → Log Kaydı → Operasyon Hafızası |
| Sonraki Olay | EVENT_VIDEO_PRODUCTION_STARTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı, Telegram Yönetici, Operasyon Hafızası, Dashboard |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Raporlamaya dahil edilir |
| Sonuç | Ödeme onaylandı, video üretim süreci başlatıldı |

---

### Üretim Olayları

---

### OLAY-031 — EVENT_PRODUCTION_PACKAGE_CREATED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-031 |
| Teknik Sabit | `EVENT_PRODUCTION_PACKAGE_CREATED` |
| Olay Adı | Production Package Oluşturuldu |
| Açıklama | PID oluşturulduktan hemen sonra HLK tarafından Production Package oluşturuldu. Üretime ait tüm bileşenler bu paket altında toplanacak. |
| PID | Zorunlu — `PID-YYYYMMDD-NNNN` |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Task Package Engine, Log Sistemi, Operasyon Hafızası, Digital Asset Archive |
| Kaynak Durum | `STATE_VIDEO_PRODUCTION` |
| Hedef Durum | `STATE_VIDEO_PRODUCTION` |
| İlgili Workflow | WF-008 |
| İlgili Feature | FEAT-014 |
| Tetikleyici | PID oluşturulması |
| Oluşturulma Koşulu | PID oluşturulduktan hemen sonra |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | Production Package oluşturulur → Task Package'ler hazırlanır → Agent'lar görevlendirilir → Log Kaydı → Operasyon Hafızası |
| Sonraki Olay | EVENT_VIDEO_PRODUCTION_STARTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Raporlamaya dahil edilir |
| Sonuç | Production Package başarıyla oluşturuldu, Task Package'ler hazırlanıyor |

---

### OLAY-023 — EVENT_VIDEO_PRODUCTION_STARTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-023 |
| Teknik Sabit | `EVENT_VIDEO_PRODUCTION_STARTED` |
| Olay Adı | Video Üretimi Başlatıldı |
| Açıklama | Ödeme onayı sonrası reklam videosu üretim süreci başlatıldı. |
| PID | Zorunlu — `PID-YYYYMMDD-NNNN` |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Servis Sağlığı ve Müdahale Motoru, Log Sistemi, Operasyon Hafızası |
| Kaynak Durum | `STATE_VIDEO_PRODUCTION` |
| Hedef Durum | `STATE_VIDEO_PRODUCTION` |
| İlgili Workflow | WF-008 |
| İlgili Feature | FEAT-008, FEAT-009 |
| Tetikleyici | Ödeme onayı |
| Oluşturulma Koşulu | Ödeme tamamlandıktan sonra video üretimi başladığında |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | Video üretim görevleri oluşturulur → Servis sağlayıcılar devreye alınır |
| Sonraki Olay | EVENT_VIDEO_PRODUCTION_COMPLETED veya EVENT_VIDEO_PRODUCTION_FAILED |
| Tekrar Deneme Politikası | Otomatik tekrar |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır |
| Sonuç | Video üretim süreci başlatıldı |

---

### OLAY-024 — EVENT_VIDEO_PRODUCTION_COMPLETED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-024 |
| Teknik Sabit | `EVENT_VIDEO_PRODUCTION_COMPLETED` |
| Olay Adı | Video Üretimi Tamamlandı |
| Açıklama | Reklam videosu başarıyla üretildi ve kalite kontrol süreci başlatıldı. |
| PID | Zorunlu — `PID-YYYYMMDD-NNNN` |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Feature, Servis Sağlığı ve Müdahale Motoru, Log Sistemi, Operasyon Hafızası, Telegram Bildirim Sistemi |
| Kaynak Durum | `STATE_VIDEO_PRODUCTION` |
| Hedef Durum | `STATE_SESSION_COMPLETED` |
| İlgili Workflow | WF-008 |
| İlgili Feature | FEAT-008, FEAT-009 |
| Tetikleyici | Video üretim başarısı |
| Oluşturulma Koşulu | Video başarıyla üretildiğinde |
| Öncelik | `PRIORITY_CRITICAL` |
| Olay Çıktıları | Video kullanıcıya teslim edilir → Log Kaydı → Operasyon Hafızası → Raporlama |
| Sonraki Olay | EVENT_REVISION_REQUESTED veya EVENT_SESSION_CLOSED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı, Telegram Yönetici, Operasyon Hafızası, Dashboard |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır, Raporlamaya dahil edilir |
| Sonuç | Video üretimi tamamlandı, kalite kontrol süreci başlatıldı |

---

### OLAY-025 — EVENT_VIDEO_PRODUCTION_FAILED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-025 |
| Teknik Sabit | `EVENT_VIDEO_PRODUCTION_FAILED` |
| Olay Adı | Video Üretimi Başarısız Oldu |
| Açıklama | Video üretim sürecinde hata oluştu ve oturum kapatıldı. |
| PID | Zorunlu — `PID-YYYYMMDD-NNNN` |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Servis Sağlığı ve Müdahale Motoru, Operasyon Hafızası, Yönetici Bildirim Sistemi |
| Kaynak Durum | `STATE_VIDEO_PRODUCTION` |
| Hedef Durum | `STATE_SESSION_CLOSED` |
| İlgili Workflow | WF-008 |
| İlgili Feature | FEAT-008, FEAT-009 |
| Tetikleyici | Video üretim hatası |
| Oluşturulma Koşulu | Video üretimi başarısız olduğunda |
| Öncelik | `PRIORITY_CRITICAL` |
| Olay Çıktıları | Hata kaydı oluşturulur → Servis sağlığı raporu güncellenir → Yönetici bilgilendirilir |
| Sonraki Olay | EVENT_SESSION_CLOSED |
| Tekrar Deneme Politikası | Yönetici onayı gerekir |
| Bildirim Hedefleri | Log Sistemi, Telegram Yönetici, Operasyon Hafızası, Dashboard |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır, Raporlamaya dahil edilir |
| Sonuç | Video üretimi başarısız, hata kaydı oluşturuldu |

---

### Revizyon Olayları

---

### OLAY-026 — EVENT_REVISION_REQUESTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-026 |
| Teknik Sabit | `EVENT_REVISION_REQUESTED` |
| Olay Adı | Revizyon Talep Edildi |
| Açıklama | Kullanıcı teslim edilen videoda değişiklik talep etti. |
| PID | Zorunlu — `PID-YYYYMMDD-NNNN` |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Operasyon Hafızası, Yönetici Bildirim Sistemi |
| Kaynak Durum | `STATE_SESSION_COMPLETED` |
| Hedef Durum | `STATE_VIDEO_PRODUCTION` |
| İlgili Workflow | WF-008 |
| Tetikleyici | Kullanıcı revizyon talebi |
| Oluşturulma Koşulu | Kullanıcı teslim edilen videoda değişiklik talep ettiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | Revizyon süreci başlatılır → Yönetici bilgilendirilir |
| Sonraki Olay | EVENT_REVISION_COMPLETED |
| Tekrar Deneme Politikası | GC üzerinden yönetilir |
| Bildirim Hedefleri | Log Sistemi, Telegram Yönetici, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | Revizyon süreci başlatıldı |

---

### OLAY-027 — EVENT_REVISION_COMPLETED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-027 |
| Teknik Sabit | `EVENT_REVISION_COMPLETED` |
| Olay Adı | Revizyon Tamamlandı |
| Açıklama | Revizyon videosu başarıyla üretildi ve kullanıcıya teslim edildi. |
| PID | Zorunlu — `PID-YYYYMMDD-NNNN` |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Operasyon Hafızası, Telegram Bildirim Sistemi |
| Kaynak Durum | `STATE_VIDEO_PRODUCTION` |
| Hedef Durum | `STATE_SESSION_COMPLETED` |
| İlgili Workflow | WF-008 |
| Tetikleyici | Revizyon üretim başarısı |
| Oluşturulma Koşulu | Revizyon videosu başarıyla üretildiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | Revizyon videosu kullanıcıya teslim edilir → Log Kaydı → Operasyon Hafızası |
| Sonraki Olay | EVENT_SESSION_CLOSED |
| Tekrar Deneme Politikası | 1 kez |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı, Telegram Yönetici, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır |
| Sonuç | Revizyon tamamlandı, video kullanıcıya teslim edildi |

---

### Sistem Olayları

Sistem yönetimi, oturum zaman aşımı ve operasyonel sistem olaylarını içerir.

---

### OLAY-037 — EVENT_TIMEOUT_REACHED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-037 |
| Teknik Sabit | `EVENT_TIMEOUT_REACHED` |
| Olay Adı | Zaman Aşımı Oluştu |
| Açıklama | Kullanıcının cevap hakkı bulunan bir state'te bekleme süresi doldu. Oturum zaman aşımı süreci başlatılır. |
| Üreten Bileşen | Session Timeout Module |
| Kullanan Bileşenler | State Engine, Workflow, Log Sistemi, Operasyon Hafızası, Telegram Bildirim Sistemi |
| Kaynak Durum | Kullanıcı cevap bekleyen tüm state'ler |
| Hedef Durum | `STATE_SESSION_TIMEOUT` |
| İlgili Workflow | Tüm Workflow'lar |
| İlgili Feature | FEAT-003 |
| Tetikleyici | Oturum zamanlayıcısının dolması |
| Oluşturulma Koşulu | GC parametrelerinde tanımlı bekleme süresinin aşılması |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | STATE_SESSION_TIMEOUT başlatılır → Kullanıcıya zaman aşımı bildirimi gönderilir → STATE_SESSION_CLOSED zinciri başlatılır |
| Sonraki Olay | EVENT_SESSION_CLOSED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Telegram Kullanıcısı, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, Analiz Motoruna aktarılır |
| Sonuç | Zaman aşımı oluştu, oturum kapatma süreci başlatıldı |

---

### LAC Operasyon Olayları

Live Activity Center (LAC) kapsamında kullanılan olayları tanımlar.

LAC Event'leri; yönetici tarafından gerçekleştirilen LAC oturum açma, PID seçme ve görünüm değiştirme gibi operasyonel işlemleri temsil eder.

LAC Event yapısı genişleyebilir olarak tasarlanmıştır. Gelecekte LAC'a özgü yeni operasyonel Event'ler gerektiğinde aynı standartta eklenebilir.

Her LAC Event'i:

* PID üzerinden ilişkilendirilir.
* Yalnızca yönetici işlemlerini temsil eder.
* HLK Workflow'una, State Engine'ine veya karar mekanizmasına müdahale etmez.
* Operasyon Hafızasına kaydedilir.

---

### OLAY-032 — EVENT_LAC_OPENED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-032 |
| Teknik Sabit | `EVENT_LAC_OPENED` |
| Olay Adı | LAC Oturumu Açıldı |
| Açıklama | Yönetici tarafından LAC arayüzü açıldı ve operasyon izleme katmanı başlatıldı. |
| Üreten Bileşen | LAC |
| Kullanan Bileşenler | Operasyon Hafızası, Log Sistemi |
| Kaynak Durum | - |
| Hedef Durum | - |
| İlgili Feature | FEAT-015 |
| Tetikleyici | Yönetici LAC arayüzünü açtığında |
| Oluşturulma Koşulu | Yönetici LAC erişimi başlattığında |
| Öncelik | `PRIORITY_LOW` |
| Olay Çıktıları | LAC oturumu açılır → PID listesi yüklenir → Log Kaydı → Operasyon Hafızası |
| Sonraki Olay | EVENT_LAC_PID_SELECTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | LAC oturumu başarıyla açıldı |

---

### OLAY-033 — EVENT_LAC_PID_SELECTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-033 |
| Teknik Sabit | `EVENT_LAC_PID_SELECTED` |
| Olay Adı | LAC PID Seçildi |
| Açıklama | Yönetici tarafından LAC üzerinde izlenmek üzere bir PID seçildi. |
| PID | Zorunlu — `PID-YYYYMMDD-NNNN` |
| Üreten Bileşen | LAC |
| Kullanan Bileşenler | Operasyon Hafızası, Log Sistemi |
| Kaynak Durum | - |
| Hedef Durum | - |
| İlgili Feature | FEAT-015 |
| Tetikleyici | Yönetici LAC üzerinde bir PID seçtiğinde |
| Oluşturulma Koşulu | PID mevcut ve Production Package oluşturulmuş olduğunda |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | PID'ye bağlı Workflow adımları yüklenir → Event akışı başlar → Log Kaydı → Operasyon Hafızası |
| Sonraki Olay | EVENT_LAC_VIEW_CHANGED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | PID başarıyla seçildi, canlı izleme başlatıldı |

---

### OLAY-034 — EVENT_LAC_VIEW_CHANGED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-034 |
| Teknik Sabit | `EVENT_LAC_VIEW_CHANGED` |
| Olay Adı | LAC Görünüm Değiştirildi |
| Açıklama | Yönetici LAC üzerinde farklı bir görünüme veya detay seviyesine geçiş yaptı. |
| PID | İsteğe Bağlı — `PID-YYYYMMDD-NNNN` |
| Üreten Bileşen | LAC |
| Kullanan Bileşenler | Operasyon Hafızası, Log Sistemi |
| Kaynak Durum | - |
| Hedef Durum | - |
| İlgili Feature | FEAT-015 |
| Tetikleyici | Yönetici LAC üzerinde görünüm değiştirdiğinde (Adım detayı açma/kapama, panel değiştirme) |
| Oluşturulma Koşulu | LAC oturumu aktif olduğunda |
| Öncelik | `PRIORITY_LOW` |
| Olay Çıktıları | Yeni görünüm yüklenir → İlgili veriler güncellenir → Log Kaydı → Operasyon Hafızası |
| Sonraki Olay | - |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır |
| Sonuç | LAC görünümü başarıyla değiştirildi |

---

### LAC Event Genişletme Standardı

Gelecekte LAC'a özgü yeni Event'ler aşağıdaki kurallara göre eklenir:

1. Her yeni LAC Event'i `EVENT_LAC_` ön eki ile başlar.
2. Her yeni LAC Event'i mevcut Olay Veri Standardına (Bölüm 5) uygun olur.
3. Her yeni LAC Event'i için sıradaki OLAY numarası kullanılır.
4. LAC Event'leri yalnızca yönetici operasyonlarını temsil eder.
5. LAC Event'leri HLK Workflow'una, State Engine'ine veya karar mekanizmasına müdahale etmez.
6. Her LAC Event'i Operasyon Hafızasına kaydedilir.

---

## 18. Gelecekte Genişletilebilirlik

Bu dosya başlangıç standardıdır.

HLK sistem geliştikçe aşağıdaki durumlarda yeni olaylar eklenebilir:

* Yeni bir Workflow eklendiğinde,
* Yeni bir Feature eklendiğinde,
* Yeni bir Modül eklendiğinde,
* Mevcut bir State yapısı değiştiğinde,
* Yeni bir iş akışı tanımlandığında.

Yeni olay ekleme kuralları:

1. Her yeni olay benzersiz bir Teknik Sabit almalıdır.
2. Her yeni olay `EVENT_` ön eki ile başlamalıdır.
3. Her yeni olay bir Kaynak Durum ve Hedef Durum belirtmelidir.
4. Her yeni olay mevcut Olay Veri Standardına uygun olmalıdır.
5. Yeni olay eklendiğinde SE-007_5 (State Event Trigger Architecture) güncellenmelidir.
6. Yeni olay eklendiğinde ilgili Workflow, Feature ve Module referansları kontrol edilmelidir.

---

## 19. Olay Standart Şablonu

HLK içerisine yeni bir olay eklenirken aşağıdaki standart şablon kullanılmalıdır.

Her yeni olay için Olay Kimliği sıradaki numara ile belirlenir (OLAY-029, OLAY-030 ...).

Her yeni olay `EVENT_` ön eki ile başlayan benzersiz bir Teknik Sabit alır.

Tüm alanlar Olay Veri Standardı bölümünde tanımlanan kurallara uygun olarak doldurulmalıdır.

```
### OLAY-XXX — EVENT_NEW_EVENT_NAME

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-XXX |
| Teknik Sabit | `EVENT_NEW_EVENT_NAME` |
| Olay Adı | [Türkçe olay adı] |
| Açıklama | [Olayın kısa açıklaması] |
| Üreten Bileşen | [HLK / State Engine / Workflow / Modül] |
| Kullanan Bileşenler | [Virgülle ayrılmış bileşen listesi] |
| Kaynak Durum | `[STATE_NAME]` |
| Hedef Durum | `[STATE_NAME]` |
| İlgili Workflow | [WF-XXX] |
| İlgili Feature | [FEAT-XXX] |
| Tetikleyici | [Olayı tetikleyen durum] |
| Oluşturulma Koşulu | [Olayın oluşma koşulu] |
| Öncelik | `[PRIORITY_LEVEL]` |
| Olay Çıktıları | [Çıktı tanımı → çıktı → çıktı] |
| Sonraki Olay | `EVENT_NEXT_EVENT_NAME` |
| Tekrar Deneme Politikası | [Yok / 1 kez / 3 kez / GC / Otomatik / Yönetici] |
| Bildirim Hedefleri | [Virgülle ayrılmış hedef listesi] |
| Kayıt Politikası | [Virgülle ayrılmış kayıt yöntemleri] |
| Sonuç | [Olayın tamamlanma sonucu] |
```

---

## 20. Executor Event'leri — Execution Event Collector (EEC)

> Bu bölümdeki Event'ler 22_EXECUTION_EVENT_COLLECTOR.md tarafından tanımlanmıştır.
> EEC, Executor (Claude) işlemlerini gerçek zamanlı Event'lere dönüştürür ve
> LAC tarafından anlık görüntülenebilmesini sağlar.

### Görev Yönetimi Event'leri

---

### OLAY-076 — EVENT_TASK_STARTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-076 |
| Teknik Sabit | `EVENT_TASK_STARTED` |
| Olay Adı | Görev Başladı |
| Açıklama | Executor görevi almış ve çalışmaya başlamıştır. |
| Üreten Bileşen | Execution Event Collector (EEC) |
| Kullanan Bileşenler | LAC, Operasyon Hafızası, Log Sistemi |
| Kaynak Durum | `STATE_CEE_PRE_CHECK` |
| Hedef Durum | `STATE_CEE_PRE_CHECK` |
| İlgili Workflow | WF-016 |
| İlgili Feature | FEAT-020 |
| PID | Zorunlu |
| Tetikleyici | Executor görevi aldı |
| Oluşturulma Koşulu | CTP Executor'a iletildiğinde |
| Öncelik | `PRIORITY_MEDIUM` |
| Olay Çıktıları | LAC'ta görev başlangıcı gösterilir |
| Sonraki Olay | EVENT_MASTER_SCAN_STARTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | LAC, Log Sistemi, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, LAC'ta görünür |
| Sonuç | Görev başlatıldı |

---

### OLAY-077 — EVENT_TASK_CREATED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-077 |
| Teknik Sabit | `EVENT_TASK_CREATED` |
| Olay Adı | Görev Paketi Oluşturuldu |
| Açıklama | CEE tarafından Constitutional Task Package (CTP) oluşturulmuştur. |
| Üreten Bileşen | Execution Event Collector (EEC) |
| Kullanan Bileşenler | LAC, Task Engine, Operasyon Hafızası |
| Kaynak Durum | `STATE_CEE_PRE_CHECK` |
| Hedef Durum | `STATE_CEE_PRE_CHECK` |
| İlgili Workflow | WF-015, WF-016 |
| İlgili Feature | FEAT-019, FEAT-020 |
| PID | Zorunlu |
| Tetikleyici | CEE PRE-CHECK tamamlandı |
| Oluşturulma Koşulu | CTP başarıyla oluşturulduğunda |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | CTP detayları LAC'ta görünür |
| Sonraki Olay | EVENT_EXECUTOR_ASSIGNED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | LAC, Task Engine, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, LAC'ta görünür |
| Sonuç | CTP oluşturuldu |

---

### OLAY-078 — EVENT_EXECUTOR_ASSIGNED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-078 |
| Teknik Sabit | `EVENT_EXECUTOR_ASSIGNED` |
| Olay Adı | Executor Görevlendirildi |
| Açıklama | Executor (Claude) göreve atanmış ve çalışmaya hazırdır. |
| Üreten Bileşen | Execution Event Collector (EEC) |
| Kullanan Bileşenler | LAC, Task Engine, Operasyon Hafızası |
| Kaynak Durum | `STATE_CEE_PRE_CHECK` |
| Hedef Durum | `STATE_CEE_POST_CHECK` |
| İlgili Workflow | WF-016 |
| İlgili Feature | FEAT-020 |
| PID | Zorunlu |
| Tetikleyici | Task Engine, Executor'a görevi atadı |
| Oluşturulma Koşulu | CTP Claude'a iletildiğinde |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | LAC EXECUTE fazına geçer |
| Sonraki Olay | EVENT_FILE_OPENED / EVENT_CODE_ANALYSIS_STARTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | LAC, Task Engine, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, LAC'ta görünür |
| Sonuç | Executor görevlendirildi |

---

### Anayasa Tarama Event'leri

---

### OLAY-079 — EVENT_MASTER_SCAN_STARTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-079 |
| Teknik Sabit | `EVENT_MASTER_SCAN_STARTED` |
| Olay Adı | MASTER Taraması Başladı |
| Açıklama | Executor, MASTER RULE BOOK'u taramaya başlamıştır. |
| Üreten Bileşen | Execution Event Collector (EEC) |
| Kullanan Bileşenler | LAC, Operasyon Hafızası |
| Kaynak Durum | `STATE_CEE_PRE_CHECK` |
| Hedef Durum | `STATE_CEE_PRE_CHECK` |
| İlgili Workflow | WF-016 |
| İlgili Feature | FEAT-020 |
| PID | Zorunlu |
| Tetikleyici | Executor MASTER kurallarını okumaya başladı |
| Oluşturulma Koşulu | PRE-CHECK aşamasında |
| Öncelik | `PRIORITY_LOW` |
| Olay Çıktıları | LAC'ta "MASTER taranıyor" gösterilir |
| Sonraki Olay | EVENT_MASTER_SCAN_COMPLETED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | LAC, Log Sistemi |
| Kayıt Politikası | Loglanır, LAC'ta görünür |
| Sonuç | MASTER taraması başladı |

---

### OLAY-080 — EVENT_MASTER_SCAN_COMPLETED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-080 |
| Teknik Sabit | `EVENT_MASTER_SCAN_COMPLETED` |
| Olay Adı | MASTER Taraması Tamamlandı |
| Açıklama | Executor, tüm MASTER kurallarını okumuş ve anlamıştır. |
| Üreten Bileşen | Execution Event Collector (EEC) |
| Kullanan Bileşenler | LAC, Operasyon Hafızası |
| Kaynak Durum | `STATE_CEE_PRE_CHECK` |
| Hedef Durum | `STATE_CEE_PRE_CHECK` |
| İlgili Workflow | WF-016 |
| İlgili Feature | FEAT-020 |
| PID | Zorunlu |
| Tetikleyici | Executor tüm MASTER kurallarını okudu |
| Oluşturulma Koşulu | MASTER taraması bittiğinde |
| Öncelik | `PRIORITY_LOW` |
| Olay Çıktıları | LAC'ta "MASTER taraması tamam" gösterilir |
| Sonraki Olay | EVENT_FLOW_SCAN_STARTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | LAC, Log Sistemi |
| Kayıt Politikası | Loglanır, LAC'ta görünür |
| Sonuç | MASTER taraması tamamlandı |

---

### OLAY-081 — OLAY-088 (Tarama Event'leri)

> OLAY-081 — OLAY-088; Flow, State, Architecture ve Operational tarama
> başlangıç/bitiş event'leridir. Her biri OLAY-079/080 ile aynı formatta
> olup ilgili kaynağa göre isimlendirilir:
> - OLAY-081: `EVENT_FLOW_SCAN_STARTED`
> - OLAY-082: `EVENT_FLOW_SCAN_COMPLETED`
> - OLAY-083: `EVENT_STATE_SCAN_STARTED`
> - OLAY-084: `EVENT_STATE_SCAN_COMPLETED`
> - OLAY-085: `EVENT_ARCHITECTURE_SCAN_STARTED`
> - OLAY-086: `EVENT_ARCHITECTURE_SCAN_COMPLETED`
> - OLAY-087: `EVENT_OPERATIONAL_SCAN_STARTED`
> - OLAY-088: `EVENT_OPERATIONAL_SCAN_COMPLETED`
>
> Tüm tarama event'leri için ortak alanlar: Üreten=EEC, WF=WF-016, FEAT=FEAT-020,
> PID=Zorunlu, Öncelik=PRIORITY_LOW, Kayıt=Loglanır+LAC'ta görünür.

---

### Dosya İşlem Event'leri

---

### OLAY-089 — EVENT_FILE_OPENED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-089 |
| Teknik Sabit | `EVENT_FILE_OPENED` |
| Olay Adı | Dosya Açıldı |
| Açıklama | Executor bir dosyayı okumak veya düzenlemek için açmıştır. |
| Üreten Bileşen | Execution Event Collector (EEC) |
| Kullanan Bileşenler | LAC, Operasyon Hafızası |
| Kaynak Durum | `STATE_CEE_POST_CHECK` |
| Hedef Durum | `STATE_CEE_POST_CHECK` |
| İlgili Workflow | WF-016 |
| İlgili Feature | FEAT-020 |
| PID | Zorunlu |
| Tetikleyici | Executor dosya açtı |
| Oluşturulma Koşulu | EXECUTE fazında dosya erişimi |
| Öncelik | `PRIORITY_LOW` |
| Olay Çıktıları | LAC'ta dosya adı gösterilir |
| Sonraki Olay | EVENT_FILE_READ / EVENT_FILE_UPDATED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | LAC, Log Sistemi |
| Kayıt Politikası | Loglanır, LAC'ta görünür |
| Sonuç | Dosya açıldı: `<dosya_adı>` |

---

### OLAY-090 — OLAY-092 (Dosya Event'leri)

> OLAY-090 (`EVENT_FILE_READ`), OLAY-091 (`EVENT_FILE_UPDATED`),
> OLAY-092 (`EVENT_FILE_CREATED`) — OLAY-089 ile aynı formatta olup
> ilgili dosya işlemine göre isimlendirilir.

---

### Kod Geliştirme Event'leri

---

### OLAY-093 — EVENT_CODE_ANALYSIS_STARTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-093 |
| Teknik Sabit | `EVENT_CODE_ANALYSIS_STARTED` |
| Olay Adı | Kod Analizi Başladı |
| Açıklama | Executor mevcut kodu analiz etmeye başlamıştır. |
| Üreten Bileşen | Execution Event Collector (EEC) |
| Kullanan Bileşenler | LAC, Operasyon Hafızası |
| Kaynak Durum | `STATE_CEE_POST_CHECK` |
| Hedef Durum | `STATE_CEE_POST_CHECK` |
| İlgili Workflow | WF-016 |
| İlgili Feature | FEAT-020 |
| PID | Zorunlu |
| Tetikleyici | Executor kod incelemesine başladı |
| Oluşturulma Koşulu | EXECUTE fazında |
| Öncelik | `PRIORITY_LOW` |
| Olay Çıktıları | LAC'ta "Kod analizi başladı" |
| Sonraki Olay | EVENT_CODE_ANALYSIS_COMPLETED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | LAC, Log Sistemi |
| Kayıt Politikası | Loglanır, LAC'ta görünür |
| Sonuç | Kod analizi başladı |

---

### OLAY-094 — OLAY-097 (Kod Event'leri)

> OLAY-094 (`EVENT_CODE_ANALYSIS_COMPLETED`), OLAY-095 (`EVENT_CODE_IMPLEMENTATION_STARTED`),
> OLAY-096 (`EVENT_CODE_IMPLEMENTATION_COMPLETED`), OLAY-097 (`EVENT_CODE_COMPLETED`) —
> OLAY-093 ile aynı formatta olup ilgili kod geliştirme aşamasına göre isimlendirilir.

---

### Denetim Event'leri

---

### OLAY-098 — EVENT_CONSTITUTION_SCAN_STARTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-098 |
| Teknik Sabit | `EVENT_CONSTITUTION_SCAN_STARTED` |
| Olay Adı | Constitution Scan Başladı |
| Açıklama | CEE POST-CHECK: Anayasal uyumluluk taraması başlamıştır. |
| Üreten Bileşen | Execution Event Collector (EEC) |
| Kullanan Bileşenler | LAC, CDE, Operasyon Hafızası |
| Kaynak Durum | `STATE_CEE_POST_CHECK` |
| Hedef Durum | `STATE_CEE_POST_CHECK` |
| İlgili Workflow | WF-015, WF-016 |
| İlgili Feature | FEAT-019, FEAT-020 |
| PID | Zorunlu |
| Tetikleyici | CEE POST-CHECK başladı |
| Oluşturulma Koşulu | Executor kodu tamamladığında |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | LAC'ta "Constitution Scan başladı" |
| Sonraki Olay | EVENT_CONSTITUTION_SCAN_COMPLETED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | LAC, CDE, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Operasyon Hafızasına yazılır, LAC'ta görünür |
| Sonuç | Constitution Scan başladı |

---

### OLAY-099 — OLAY-103 (Denetim Event'leri)

> OLAY-099 (`EVENT_CONSTITUTION_SCAN_COMPLETED`),
> OLAY-100 (`EVENT_RUNTIME_TEST_STARTED`), OLAY-101 (`EVENT_RUNTIME_TEST_COMPLETED`),
> OLAY-102 (`EVENT_SYNTAX_CHECK_STARTED`), OLAY-103 (`EVENT_SYNTAX_CHECK_COMPLETED`) —
> OLAY-098 ile aynı formatta olup ilgili denetim aşamasına göre isimlendirilir.

---

### Yeniden Üretim Olayları (AR-002_84 — Yönetici Yeniden Üretim Prosedürü)

> Bu olay grubu, OLAY-025 (`EVENT_VIDEO_PRODUCTION_FAILED`) kaydında tanımlı
> **"Tekrar Deneme Politikası: Yönetici onayı gerekir"** hükmünün runtime
> uygulamasıdır. Yeniden üretimin tamamlanması ve başarısızlığı için yeni olay
> tanımlanmaz; mevcut OLAY-024 (`EVENT_VIDEO_PRODUCTION_COMPLETED`) ve
> OLAY-025 (`EVENT_VIDEO_PRODUCTION_FAILED`) olayları kullanılır
> (Single Source of Truth — MASTER-001).

---

### OLAY-107 — EVENT_REPRODUCTION_REQUESTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-107 |
| Teknik Sabit | `EVENT_REPRODUCTION_REQUESTED` |
| Olay Adı | Yeniden Üretim Talep Edildi |
| Açıklama | Yönetici, başarısız veya yarım kalmış bir üretim için yeniden üretim prosedürünü onayladı. Prosedür yalnızca Yönetici tarafından başlatılabilir; kullanıcı başlatamaz (AR-002_84). |
| PID | Zorunlu — `PID-YYYYMMDD-NNNN` |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | Production Runtime, HLK Runtime, Log Sistemi, Operasyon Hafızası, LAC |
| Kaynak Durum | `STATE_VIDEO_PRODUCTION` |
| Hedef Durum | `STATE_VIDEO_PRODUCTION` |
| İlgili Workflow | WF-008, WF-017 |
| İlgili Feature | FEAT-002, FEAT-014 |
| Tetikleyici | Yönetici onayı ([Evet, Başlat]) |
| Oluşturulma Koşulu | Yönetici, yeniden üretim onay ekranını onayladığında |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | PID doğrulanır → Anayasal kayıtlar yüklenir → HLK Runtime REPRODUCTION kararı istenir |
| Sonraki Olay | EVENT_REPRODUCTION_STARTED veya EVENT_REPRODUCTION_REJECTED |
| Tekrar Deneme Politikası | Yok |
| Bildirim Hedefleri | Log Sistemi, Operasyon Hafızası, LAC |
| Kayıt Politikası | Loglanır, Production Package Event Loglarına yazılır, Operasyon Hafızasına yazılır |
| Sonuç | Yeniden üretim değerlendirme süreci başlatıldı |

---

### OLAY-108 — EVENT_REPRODUCTION_STARTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-108 |
| Teknik Sabit | `EVENT_REPRODUCTION_STARTED` |
| Olay Adı | Yeniden Üretim Başlatıldı |
| Açıklama | HLK Runtime, REPRODUCTION kararını (RESUME / RETRY / REPLAY / START_AS_NEW) üretti ve yeniden üretim süreci mevcut PID ve Production Package üzerinde başlatıldı (AR-002_57 PID tekilliği korunur). |
| PID | Zorunlu — `PID-YYYYMMDD-NNNN` |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | Production Runtime, Production Executor, Decision Engine, Log Sistemi, Operasyon Hafızası, LAC |
| Kaynak Durum | `STATE_VIDEO_PRODUCTION` |
| Hedef Durum | `STATE_VIDEO_PRODUCTION` |
| İlgili Workflow | WF-008, WF-017 |
| İlgili Feature | FEAT-002, FEAT-008, FEAT-009, FEAT-014 |
| Tetikleyici | HLK Runtime REPRODUCTION kararı (REJECT dışında) |
| Oluşturulma Koşulu | Production Package yeniden üretime hazırlandığında |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | Üretim görevleri checkpoint'ten devam eder → Servis sağlayıcılar Decision Packet'e göre devreye alınır |
| Sonraki Olay | EVENT_VIDEO_PRODUCTION_COMPLETED (OLAY-024) veya EVENT_VIDEO_PRODUCTION_FAILED (OLAY-025) |
| Tekrar Deneme Politikası | AR-002_79 / AR-002_83 Recovery Policy kapsamında HLK Runtime yönetir |
| Bildirim Hedefleri | Log Sistemi, Telegram Yönetici, Operasyon Hafızası, LAC |
| Kayıt Politikası | Loglanır, Production Package Event Loglarına yazılır, Operasyon Hafızasına yazılır, Raporlamaya dahil edilir |
| Sonuç | Yeniden üretim süreci başlatıldı |

---

### OLAY-109 — EVENT_REPRODUCTION_REJECTED

| Alan | Değer |
|------|-------|
| Olay Kimliği | OLAY-109 |
| Teknik Sabit | `EVENT_REPRODUCTION_REJECTED` |
| Olay Adı | Yeniden Üretim Reddedildi |
| Açıklama | PID doğrulanamadı, Production Package bulunamadı/arşivlenmiş veya HLK Runtime REPRODUCTION kararı REJECT üretti. Prosedür başlatılmaz; durum anayasal gerekçesiyle Yöneticiye bildirilir ve işlem güvenli şekilde sonlandırılır (AR-002_84 İstisna Akışı). |
| PID | Zorunlu — `PID-YYYYMMDD-NNNN` (sorgulanan değer) |
| Üreten Bileşen | HLK |
| Kullanan Bileşenler | HLK Runtime, Log Sistemi, Operasyon Hafızası, Yönetici Bildirim Sistemi |
| Kaynak Durum | `STATE_VIDEO_PRODUCTION` |
| Hedef Durum | `STATE_VIDEO_PRODUCTION` |
| İlgili Workflow | WF-017 |
| İlgili Feature | FEAT-002 |
| Tetikleyici | HLK Runtime REPRODUCTION kararı: REJECT |
| Oluşturulma Koşulu | Yeniden üretim ön koşulları sağlanamadığında |
| Öncelik | `PRIORITY_HIGH` |
| Olay Çıktıları | Karar gerekçesi Decision History'ye yazılır → Yönetici bilgilendirilir → Güvenli sonlandırma |
| Sonraki Olay | Yok (güvenli sonlandırma) |
| Tekrar Deneme Politikası | Yok — Yönetici yeni bir talep başlatabilir |
| Bildirim Hedefleri | Log Sistemi, Telegram Yönetici, Operasyon Hafızası |
| Kayıt Politikası | Loglanır, Production Package Event Loglarına yazılır (paket mevcutsa), Operasyon Hafızasına yazılır |
| Sonuç | Yeniden üretim başlatılmadı, işlem güvenli şekilde sonlandırıldı |

---

## 21. Temel İlke

Bu dosya;

* State Engine'in yerine geçmez.
* Workflow'un yerine geçmez.
* Feature Registry'nin yerine geçmez.
* Module Rules'un yerine geçmez.

Bu dosya yalnızca HLK içerisindeki olayların standartlarını tanımlayan ortak mimari katmandır.

Bu dosyada tanımlanan olaylar mevcut HLK mimarisini değiştirmez, yalnızca bileşenler arasındaki iletişim standardını tanımlar.

---

## 22. Conversation Runtime Event Standard

Telegram üzerinde kullanıcıya gösterilen her konuşma davranışı olay (Event) olarak kayıt altına alınmalıdır.

Her konuşma olayı aşağıdaki bilgileri içermelidir:

* Aktif Session ID
* Production ID (PID)
* Aktif State
* Aktif Sahne
* Flow Diagram Referansı
* Gösterilen Konuşma Metni
* Konuşma Baloncuğu Oluşturuldu (Evet/Hayır)
* Daktilo Efekti Uygulandı (Evet/Hayır)
* "EKRAN SİLİNİR" Adımı Uygulandı (Evet/Hayır)
* Sonraki Event
* Sonraki State
* Runtime Zamanı
* Sonuç (PASS / FAIL)

### Temel İlke

HLK'nın kullanıcıya gösterdiği her konuşma davranışı doğrulanabilir ve geriye dönük denetlenebilir olmalıdır.

Hiçbir konuşma davranışı kayıt altına alınmadan tamamlanmış kabul edilemez.

### Beklenen Sonuç

Telegram üzerinde gerçekleşen konuşma davranışları;

* Flow Diagram,
* State Engine,
* Constitution Enforcement Engine,
* Constitution Diff Engine

ile karşılaştırılabilir hale gelir.

Böylece çalışma zamanı davranışı ile ANA YASA arasındaki tüm sapmalar kanıtlarıyla birlikte tespit edilebilir.
