# 16 — Sahne Kayıt Defteri

HLK Native Video Scene sahnelerinin resmi kayıt defteridir.

---

## Anayasal Konum

16_SAHNE_KAYIT_DEFTERİ.md, HLK'nın mevcut anayasal mimarisine yeni bir katman eklemez. Mevcut anayasal yapıyı destekleyen resmi referans kayıt dosyasıdır.

MASTER-001 Karar Hiyerarşisi içerisinde bu dosya, Flow Diagram (08_HLK_FLOW_DIAGRAM.md) ile Kod katmanı arasında konumlanan yardımcı referans kaydıdır. Karar hiyerarşisini değiştirmez.

Bu dosya;

- davranış tanımlamaz,
- state tanımlamaz,
- workflow tanımlamaz,
- kalite kuralı tanımlamaz,
- operasyonel kural tanımlamaz.

Yalnızca HLK içerisinde bulunan sahnelerin resmi kayıtlarını tutar.

---

## Kod ile İlişki — Otorite Hiyerarşisi

MASTER-001 Zorunlu Uygulama Kuralı gereği:

```
HLK MASTER RULE BOOK
        │
        ▼
16_SAHNE_KAYIT_DEFTERİ.md  (Referans)
        │
        ▼
scene_registry.py           (Uygulama)
```

Bu hiyerarşiye göre:

- **16_SAHNE_KAYIT_DEFTERİ.md referanstır.** Sahne tanımlarının nihai ve tek yetkili kaydı bu dosyadır.
- **scene_registry.py uygulamadır.** Bu dosyadaki sahne kayıtlarını Python koduna çeviren katmandır.
- Kod hiçbir zaman referansın önüne geçemez.
- Bir sahne tanımı ile kod arasında çelişki oluşursa referans (bu dosya) esas alınır, kod değiştirilir.

Bu ilişki MASTER-001'de tanımlanan "Kod, ANA YASA'nın altındadır" ilkesinin sahne yönetimi özelindeki uygulamasıdır.

---

## Amaç

Bu dosya, HLK içerisinde kullanılan Native Video Scene sahnelerinin tek resmi kayıt noktasıdır (Single Source of Truth).

---

## Kayıt Standardı

Her sahne kaydı aşağıdaki alanları içerir:

| Alan | Açıklama |
|---|---|
| Sahne Kimliği | Sahnenin sistem içi benzersiz kimliği |
| Sahne Adı | Sahnenin Türkçe adı |
| Sahne Türü | Native Video Scene / Text-Only Scene |
| Desteklenen Dil Sayısı | Kaç dilde varyantı bulunduğu |
| Başlatıldığı State | Sahnenin başlatıldığı User Conversation State |
| Tamamlanma Event'i | Sahnenin tamamlandığını belirten event |
| Sonraki State | Sahne tamamlandıktan sonra geçilen state |
| Durumu | Geliştirme durumu (FD-008_6 standardı) |
| Video Referansı | Mantıksal video referansı (fiziksel dosya yolu değil) |
| Açıklama | Sahnenin kısa açıklaması |

---

## Kayıtlı Sahneler

### SAHNE-01

| Alan | Değer |
|---|---|
| **Sahne Kimliği** | `SAHNE-01` |
| **Sahne Adı** | HLK Karşılama Sahnesi |
| **Sahne Türü** | Native Video Scene (v3.5) |
| **Desteklenen Dil Sayısı** | 1 (dil bağımsız) |
| **Başlatıldığı State** | `STATE_START` |
| **Tamamlanma Event'i** | `EVENT_START_INITIATED` |
| **Sonraki State** | `STATE_LANGUAGE_SELECTION` |
| **Durumu** | ✅ Tamamlandı |
| **Video Referansı** | `hlk_sahne1` (HLK karakter tanıtım videosu, 9:16 dikey) |
| **Açıklama** | Kullanıcı /start komutu verdiğinde oynatılan HLK karakter giriş videosu. Video tamamlandığında silinir, ekranda 8 dil seçim butonu kalır. Scene Lock mekanizması (AR-002_44) ile oturum başına tek seferlik oynatma garantisi sağlanır. |

**İlgili Anayasal Referanslar:** OR-004_0, AR-002_39, AR-002_40, AR-002_41, AR-002_42, AR-002_44

---

### SAHNE-02

| Alan | Değer |
|---|---|
| **Sahne Kimliği** | `SAHNE-02` |
| **Sahne Adı** | HLK Dil Karşılama Sahnesi |
| **Sahne Türü** | Native Video Scene (v3.5) |
| **Desteklenen Dil Sayısı** | 8 (TR, EN, DE, FR, ES, AR, RU, KR) |
| **Başlatıldığı State** | `STATE_LANGUAGE_SELECTION` |
| **Tamamlanma Event'i** | `EVENT_LANGUAGE_SELECTED` |
| **Sonraki State** | `STATE_WAIT_PRODUCT_LINK` |
| **Durumu** | ✅ Tamamlandı |
| **Video Referansı** | `hlk_sahne2_{dil_kodu}` (AHU lip-sync karşılama videosu, dile özel) |
| **Açıklama** | Kullanıcı dil seçtikten sonra seçilen dilde oynatılan AHU lip-sync karşılama videosu. Video içerisinde dudak senkronizasyonu, konuşma balonu ve daktilo efekti bulunur (Native Video Scene standardı). Video tamamlandığında silinir, daktilo efekti ile ürün linki istenir. Her dil için ayrı video varyantı mevcuttur. |

**İlgili Anayasal Referanslar:** OR-004_0, AR-002_29, AR-002_30, AR-002_31, AR-002_37, AR-002_39, AR-002_40

---

### SAHNE-03

| Alan | Değer |
|---|---|
| **Sahne Kimliği** | `SAHNE-03` |
| **Sahne Adı** | Video Format Seçim Sahnesi |
| **Sahne Türü** | Text-Only Scene (TEXT_ONLY_MODE) |
| **Desteklenen Dil Sayısı** | 8 (dinamik, oturum diline göre) |
| **Başlatıldığı State** | `STATE_VIDEO_SETTINGS` |
| **Tamamlanma Event'i** | `EVENT_VIDEO_SETTINGS_DONE` |
| **Sonraki State** | `STATE_BRIEF_COMPLETED` |
| **Durumu** | 🟡 Geliştirme Aşamasında |
| **Video Referansı** | Yok (Text-Only Scene) |
| **Açıklama** | Materyal toplama aşaması tamamlandıktan veya atlandıktan sonra kullanıcıya video formatı seçeneklerini sunan metin tabanlı sahne. Dikey 9:16, Yatay 16:9 ve Kare 1:1 olmak üzere üç format seçeneği sunulur. Kullanıcı yalnızca bir format seçebilir. Konuşma balonu ve daktilo efekti kullanılır. |

**İlgili Anayasal Referanslar:** OR-004_2, FD-008_1, MR-0005_1

---

### SAHNE-04

| Alan | Değer |
|---|---|
| **Sahne Kimliği** | `SAHNE-04` |
| **Sahne Adı** | Video Çözünürlük Seçim Sahnesi |
| **Sahne Türü** | Text-Only Scene (TEXT_ONLY_MODE) |
| **Desteklenen Dil Sayısı** | 8 (dinamik, oturum diline göre) |
| **Başlatıldığı State** | `STATE_VIDEO_RESOLUTION_SELECTION` |
| **Tamamlanma Event'i** | `EVENT_RESOLUTION_SELECTED` |
| **Sonraki State** | `STATE_VIDEO_DURATION_SELECTION` |
| **Durumu** | 🟡 Geliştirme Aşamasında |
| **Video Referansı** | Yok (Text-Only Scene) |
| **Açıklama** | Video formatı seçildikten sonra kullanıcıya çözünürlük seçeneklerini sunan metin tabanlı sahne. 480p, 720p HD ve 1080p Full HD olmak üzere üç çözünürlük seçeneği sunulur. Kullanıcı yalnızca bir çözünürlük seçebilir. |

**İlgili Anayasal Referanslar:** OR-004_2, FD-008_1

---

### SAHNE-05

| Alan | Değer |
|---|---|
| **Sahne Kimliği** | `SAHNE-05` |
| **Sahne Adı** | Video Süre Seçim Sahnesi |
| **Sahne Türü** | Text-Only Scene (TEXT_ONLY_MODE) |
| **Desteklenen Dil Sayısı** | 8 (dinamik, oturum diline göre) |
| **Başlatıldığı State** | `STATE_VIDEO_DURATION_SELECTION` |
| **Tamamlanma Event'i** | `EVENT_DURATION_SELECTED` |
| **Sonraki State** | `STATE_AUDIO_SELECTION` |
| **Durumu** | 🟡 Geliştirme Aşamasında |
| **Video Referansı** | Yok (Text-Only Scene) |
| **Açıklama** | Çözünürlük seçildikten sonra kullanıcıya video süresini belirleme imkanı sunan metin tabanlı sahne. Kullanıcı 4-30 saniye arası bir değer girebilir veya "HLK'ya Bırak" seçeneği ile süreyi HLK'nın belirlemesini isteyebilir. Geçersiz girişte HLK uyarı verir. |

**İlgili Anayasal Referanslar:** OR-004_2, FD-008_1

---

## Anayasal Bağımlılıklar

Bu kayıt defteri aşağıdaki anayasal kaynaklardan beslenir:

| Kaynak | İlişki |
|---|---|
| **MASTER-001** | Karar Hiyerarşisi — bu dosyanın sistem içerisindeki konumunu ve otorite seviyesini tanımlar |
| **MASTER-004** | HLK Karar Mekanizması ve Kural Otoritesi Prensibi — bu dosyanın bağımsız karar verici değil, HLK'nın karar mekanizmasını yönlendiren referans katmanı olduğunu tanımlar |
| **07_HLK_STATE_ENGINE.md** | Sahne-State ilişkisi — her sahnenin hangi state'te başlatılıp hangi state'e geçtiğini tanımlayan State Engine referansı |
| **08_HLK_FLOW_DIAGRAM.md** | Sahne akışı — sahnelerin kullanıcı akışı içerisindeki sırasını ve geliştirme durumlarını (FD-008_6) tanımlayan Flow Diagram referansı |

---

## Durum İşaretleri (FD-008_6 Standardı)

| İşaret | Anlamı |
|---|---|
| ⚪ | Başlanmadı |
| 🟡 | Geliştirme Aşamasında |
| 🟠 | Test Aşamasında |
| ✅ | Tamamlandı |
| 🔒 | Canlı Sistem |

---

## Gelecek Genişletmeler

Bu bölüm, sisteme eklenecek yeni sahnelerin (SAHNE-04, SAHNE-05, ... SAHNE-14) kayıtları için ayrılmıştır.

Yeni bir sahne eklendiğinde:

1. Bu dosyada ilgili sahne için yukarıdaki standarda uygun kayıt oluşturulur.
2. Sahne kaydı, sahnenin mevcut durumunu gösteren FD-008_6 işareti ile işaretlenir.
3. Sahnenin geliştirme durumu değiştiğinde yalnızca bu dosyadaki durum işareti güncellenir.

---

## Temel İlke

Bu dosya, HLK içerisinde bulunan tüm Native Video Scene ve Text-Only Scene sahnelerinin tek resmi kayıt noktasıdır (Single Source of Truth).

Bir sahnenin varlığı, özellikleri ve geliştirme durumu hakkında nihai referans bu dosyadır.

Sahne davranışları burada tanımlanmaz; ilgili anayasal katmanlar (State Engine, Flow Diagram, Operational Rules, Module Rules) tarafından yönetilir.

---

## Anayasal Yetki

Bu dosya, MASTER-001 Karar Hiyerarşisi'nde tanımlanan otorite sıralamasına tabidir.

Bu dosya;

- MASTER RULE BOOK'u uygulamak için vardır.
- MASTER RULE BOOK bu dosyayı uygulamak için var değildir.

Eğer bu dosyadaki herhangi bir kayıt ile ANA YASA arasında çelişki oluşursa:

- Bu dosya düzeltilir.
- Kod düzeltilir.
- ANA YASA değiştirilmez.

---
