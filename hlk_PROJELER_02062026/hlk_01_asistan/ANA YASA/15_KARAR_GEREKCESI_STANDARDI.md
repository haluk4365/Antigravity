# 15 — Karar Gerekçesi Standardı

HLK'nın verdiği tüm önemli operasyonel kararların gerekçelerini standart hale getiren resmi mimari dosyasıdır.

---

## 1. Amaç

HLK yalnızca karar veren değil; kararını açıklayabilen, gerekçelendirebilen ve denetlenebilen bir sistem olmalıdır.

Bu dosyanın amacı;

* HLK'nın verdiği tüm önemli operasyonel kararların standart şekilde kayıt altına alınmasını,
* Kararların nedenlerinin açıklanabilir olmasını,
* Değerlendirilen alternatiflerin kaydedilmesini,
* Karar güven seviyesinin belirlenmesini,
* Kararların diğer sistem bileşenleri ile ilişkilendirilmesini

sağlamaktır.

---

## 2. Kapsam

Bu standart aşağıdaki tüm kritik kararlarda kullanılmalıdır.

* Servis seçimi
* Alternatif servis seçimi
* Risk değerlendirmesi
* Fiyatlandırma
* Kampanya kararı
* Revizyon kararı
* Üretim başlatma kararı
* Üretim durdurma kararı
* Yönetici müdahalesi
* Kullanıcı teklifi
* Ödeme sonrası üretim kararı

---

## 3. Karar Veri Standardı

HLK içerisinde her karar en az aşağıdaki standart bilgileri içermelidir.

| # | Alan | Türkçe Adı | Zorunluluk |
|---|------|-----------|:----------:|
| 1 | `DecisionID` | Karar Kimliği | Zorunlu |
| 2 | `DecisionName` | Karar Adı | Zorunlu |
| 3 | `DecisionDescription` | Karar Açıklaması | Zorunlu |
| 4 | `DecisionMaker` | Kararı Veren | Zorunlu |
| 5 | `DecisionTimestamp` | Karar Tarihi | Zorunlu |
| 6 | `EventID` | İlgili Olay | İsteğe Bağlı |
| 7 | `SourceState` | İlgili State | Zorunlu |
| 8 | `WorkflowID` | İlgili Workflow | İsteğe Bağlı |
| 9 | `FeatureID` | İlgili Feature | İsteğe Bağlı |
| 10 | `ModuleID` | İlgili Modül | İsteğe Bağlı |
| 11 | `Justifications` | Karar Gerekçeleri | Zorunlu |
| 12 | `Alternatives` | Alternatifler | Zorunlu |
| 13 | `ConfidenceLevel` | Karar Güven Seviyesi | Zorunlu |
| 14 | `DecisionOutcomes` | Karar Sonuçları | Zorunlu |

---

## 4. Karar Gerekçeleri

HLK verdiği kararın nedenlerini kayıt altına almalıdır.

Gerekçeler aşağıdaki standart değerlerden biri veya birkaçı kullanılarak oluşturulmalıdır.

Gerekçe teknik sabitleri İngilizce, açıklamaları Türkçe olmalıdır.

### Servis Seçim Gerekçeleri

| Teknik Sabit | Açıklama |
|-------------|----------|
| `API_ACCESSIBLE` | API erişilebilir |
| `API_ERROR` | API hatalı |
| `CREDIT_SUFFICIENT` | Kredi yeterli |
| `CREDIT_CRITICAL` | Kredi kritik seviyede |
| `CONFIDENCE_HIGH` | Güven skoru yüksek |
| `CONFIDENCE_LOW` | Güven skoru düşük |
| `COST_LOWEST` | Tahmini maliyet en düşük |
| `SUCCESS_RATE_HIGHEST` | Tahmini başarı oranı en yüksek |
| `DELIVERY_TIME_OPTIMAL` | Teslim süresi en uygun |
| `RISK_LOW` | Risk seviyesi düşük |
| `RISK_HIGH` | Risk seviyesi yüksek |
| `ADMIN_INTERVENTION_REQUIRED` | Yönetici müdahalesi gerekli |
| `ALTERNATIVE_MORE_SUITABLE` | Alternatif servis daha uygun |

### İşletme Gerekçeleri

| Teknik Sabit | Açıklama |
|-------------|----------|
| `COST_OPTIMAL` | Maliyet optimizasyonu sağlandı |
| `BUDGET_WITHIN_LIMITS` | Bütçe limitleri içinde |
| `REVENUE_EXPECTED_HIGH` | Beklenen gelir yüksek |
| `CAMPAIGN_ELIGIBLE` | Kampanya uygun |
| `DISCOUNT_APPLIED` | İndirim uygulandı |
| `MANUAL_PRICE_SET` | Fiyat yönetici tarafından belirlendi |

### Operasyonel Gerekçeler

| Teknik Sabit | Açıklama |
|-------------|----------|
| `QUOTA_AVAILABLE` | Kota mevcut |
| `QUOTA_EXCEEDED` | Kota aşıldı |
| `RATE_LIMIT_OK` | Hız sınırı uygun |
| `SERVICE_ONLINE` | Servis çevrim içi |
| `SERVICE_OFFLINE` | Servis çevrim dışı |
| `MAINTENANCE_MODE` | Bakım modunda |
| `TIMEOUT_EXCEEDED` | Zaman aşımı oluştu |

Bu listeler başlangıç standardıdır.

HLK sistem geliştikçe yeni gerekçeler eklenebilir veya mevcut gerekçeler güncellenebilir.

Gerekçeler gerektiğinde birden fazla olabilir.

---

## 5. Alternatiflerin Kaydedilmesi

HLK yalnızca seçilen alternatifi değil; değerlendirilen diğer alternatifleri de kayıt altına almalıdır.

Her alternatif için aşağıdaki bilgiler kaydedilmelidir.

* Alternatif Adı
* Seçildi / Seçilmedi bilgisi
* Seçilmeme gerekçesi
* Öncelik sırası

### Örnek

```
Hedra
↓
Seçildi
↓
Gerekçe: En yüksek güven skoru.

Runway
↓
Seçilmedi
↓
Gerekçe: API erişilemiyor.

Flux
↓
Seçilmedi
↓
Gerekçe: Tahmini maliyet daha yüksek.
```

Alternatif kaydı, HLK'nın karar sürecinin tamamen şeffaf olmasını sağlar.

---

## 6. Karar Güven Seviyesi

Her karar için bir güven seviyesi oluşturulmalıdır.

| Seviye | Teknik Sabit | Açıklama |
|:------:|-------------|----------|
| 1 | `CONFIDENCE_VERY_HIGH` | Çok Yüksek — Karardan neredeyse emin |
| 2 | `CONFIDENCE_HIGH` | Yüksek — Karar güçlü verilere dayanıyor |
| 3 | `CONFIDENCE_MEDIUM` | Orta — Karar yeterli veriye dayanıyor |
| 4 | `CONFIDENCE_LOW` | Düşük — Karar sınırlı veriye dayanıyor |
| 5 | `CONFIDENCE_UNCERTAIN` | Belirsiz — Karar için yeterli veri yok |

Bu değerler hardcoded değildir.

Güven seviyesi eşikleri ve karar kuralları Global Configuration (GC) üzerinden yönetilir.

---

## 7. Karar Sonuçları

Her kararın oluşturduğu sonuçlar kayıt altına alınmalıdır.

Sonuçlar aşağıdaki standart tiplerde olabilir.

* Workflow Başlatıldı
* Workflow Devam Ediyor
* Workflow Durduruldu
* STATE Değişti
* Telegram Bildirimi Gönderildi
* Yönetici Bildirimi Gönderildi
* Kullanıcı Bildirimi Gönderildi
* Operasyon Hafızasına Kaydedildi
* Olay Oluşturuldu
* Servis Değiştirildi
* Üretim Başlatıldı
* Üretim Durduruldu

### Örnek

```
↓
STATE_PRICING başlatıldı
↓
Yönetici Fiyatlandırma Formu oluşturuldu
↓
Telegram bildirimi gönderildi
↓
Operasyon Hafızasına kaydedildi
↓
EVENT_PRICING_STARTED oluşturuldu
```

---

## 8. Karar İlişkileri

Her karar aşağıdaki sistem bileşenleri ile ilişkilendirilmelidir.

| Bileşen | İlişki |
|---------|--------|
| Olay Kayıt Merkezi (14) | Karar bir veya birden fazla olayı tetikler |
| Operasyon Hafızası (MR-0005_4) | Karar kayıtları burada saklanır |
| Operasyon Analiz Motoru (MR-0005_5) | Kararlar analiz edilebilir |
| Servis Sağlığı ve Müdahale Motoru (MR-0005_3) | Servis kararları bu modülü kullanır |
| Workflow (09) | Karar ilgili workflow'u ilerletir |
| Feature Registry (10) | Karar ilgili feature'ı etkiler |
| State Engine (07) | Karar state geçişini tetikler |

---

## 9. Karar Yaşam Döngüsü

HLK içerisinde her karar aşağıdaki yaşam döngüsünü izler.

```
Karar İhtiyacı Belirlendi
↓
Alternatifler Değerlendirildi
↓
Gerekçeler Oluşturuldu
↓
Güven Seviyesi Belirlendi
↓
Karar Verildi
↓
Karar Kaydedildi
↓
İlgili Bileşenler Bilgilendirildi
↓
Operasyon Hafızasına Kaydedildi
```

### Karar İhtiyacı Belirlendi

HLK bir karar verilmesi gerektiğini tespit eder. Bu tespit; bir olay, bir state değişimi, bir analiz sonucu veya operasyonel bir durum nedeniyle oluşabilir.

### Alternatifler Değerlendirildi

HLK mevcut alternatifleri toplar, analiz eder ve değerlendirme kriterlerini uygular.

### Gerekçeler Oluşturuldu

HLK seçilen alternatifin neden tercih edildiğini ve diğer alternatiflerin neden tercih edilmediğini standart gerekçeler ile açıklar.

### Güven Seviyesi Belirlendi

HLK kararın güven seviyesini değerlendirilen verilere göre belirler.

### Karar Verildi

HLK nihai kararını verir ve uygulamaya başlar.

### Karar Kaydedildi

Karar, gerekçeleri, alternatifleri, güven seviyesi ve sonuçları ile birlikte Operasyon Hafızasına kaydedilir.

### İlgili Bileşenler Bilgilendirildi

Karar sonucunda etkilenen State Engine, Workflow, Feature ve diğer bileşenler bilgilendirilir.

### Operasyon Hafızasına Kaydedildi

Karar MR-0005_4 HLK Operasyon Hafızasına kaydedilir ve gelecekteki analizler için kullanılabilir hale gelir.

---

## 10. Karar Kayıt Kuralları

1. Her kritik karar oluşturulduğunda kayıt altına alınmalıdır.
2. Karar kayıtları değiştirilemez.
3. Karar kayıtları silinemez.
4. Karar kayıtları yalnızca okunabilir (Read Only) olarak saklanmalıdır.
5. Karar kayıtları MR-0005_4 HLK Operasyon Hafızası ile uyumlu olmalıdır.
6. Karar kayıtları gerektiğinde MR-0005_5 HLK Operasyon Analiz Motoru tarafından analiz edilebilir olmalıdır.

---

## 11. Temel İlkeler

1. Son karar her zaman HLK'ya aittir.
2. Hiçbir modül bağımsız karar veremez.
3. Modüller yalnızca analiz, öneri ve veri üretir.
4. HLK tüm verileri değerlendirerek karar verir.
5. Her kritik karar açıklanabilir olmalıdır.
6. Her karar denetlenebilir olmalıdır.
7. Her karar Operasyon Hafızasında saklanabilir olmalıdır.
8. Her karar gerektiğinde Operasyon Analiz Motoru tarafından analiz edilebilir olmalıdır.

---

## 12. State Engine İlişkisi

Bu standart SE-007_3 (User Conversation State Architecture) ve SE-007_6 (State Action Mapping Architecture) ile doğrudan ilişkilidir.

Her state geçişi bir karar sonucunda gerçekleşir.

State değişim kararları standart karar formatında kaydedilmelidir.

---

## 13. Olay Kayıt Merkezi İlişkisi

Bu standart 14_OLAY_KAYIT_MERKEZI.md ile doğrudan ilişkilidir.

Her karar bir veya birden fazla olayı tetikleyebilir.

Tetiklenen olaylar Olay Kayıt Merkezinde tanımlanan standart formatta kaydedilmelidir.

---

## 14. Production Package İlişkisi

Bu standart, Production Package (16_PRODUCTION_PACKAGE_STANDARD.md) ile doğrudan ilişkilidir.

Production Package'in **Karar Gerekçeleri (Decision History)** bölümü, bu standart ile uyumlu olarak aşağıdaki kararları saklar:

* Yönetici fiyatlandırma kararı
* Yönetici ödeme onay kararı
* Yönetici video üretim onay kararı
* HLK servis seçim kararları
* HLK ajan seçim kararları
* Revizyon kararları
* Üretim sürecinde alınan diğer tüm kritik kararlar

Her karar; Karar Veri Standardı'na (Bölüm 3) uygun olarak, gerekçesi, alternatifleri, güven seviyesi ve sonuçları ile birlikte Production Package içerisinde PID üzerinden ilişkilendirilerek saklanır.

Production Package'teki Decision History, üretim yaşam döngüsü boyunca alınan tüm kritik kararların tek resmi kayıt noktasıdır.

---

## 16. Gelecekte Genişletilebilirlik

Bu dosya başlangıç standardıdır.

HLK sistem geliştikçe aşağıdaki durumlarda yeni karar türleri eklenebilir:

* Yeni bir Workflow eklendiğinde,
* Yeni bir Feature eklendiğinde,
* Yeni bir Modül eklendiğinde,
* Mevcut bir State yapısı değiştiğinde,
* Yeni bir servis sağlayıcı eklendiğinde,
* Yeni bir karar noktası tanımlandığında.

Yeni karar türü ekleme kuralları:

1. Her yeni karar türü mevcut Karar Veri Standardına uygun olmalıdır.
2. Her yeni karar en az bir gerekçe içermelidir.
3. Her yeni karar bir güven seviyesi belirtmelidir.
4. Yeni karar eklendiğinde ilgili Workflow, Feature ve Module referansları kontrol edilmelidir.

---

## 17. Temel İlke

Bu standart;

yeni bir karar motoru oluşturmaz.

Son karar verme yetkisini HLK'dan almaz.

Karar verme sürecini değiştirmez.

Yalnızca HLK'nın verdiği kararların standart şekilde açıklanmasını ve kayıt altına alınmasını sağlar.
