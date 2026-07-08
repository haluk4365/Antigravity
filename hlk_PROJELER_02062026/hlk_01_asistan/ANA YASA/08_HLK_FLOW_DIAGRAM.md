# 08_HLK_FLOW_DIAGRAM

> Bu dosya HLK'nin resmi kullanıcı akış diyagramıdır.
> Bu dosya SE-007_3 (User Conversation State Architecture), SE-007_4 (User Conversation State Transition Rules),
> SE-007_5 (State Event Trigger Architecture) ve SE-007_6 (State Action Mapping Architecture) ile uyumludur.
>
> Bu dosya yaşayan bir dokümandır ve gelecekte güncellenebilir.

## FD-008_1

### Başlık

**Flow Diagram Operasyonel Bağlayıcılık Prensibi**

### Kural

Bu dosyada tanımlanan tüm sahneler, akışlar ve sahne davranışları açıklama amacıyla yazılmamıştır.

Bunlar HLK'nın çalışma sırasında uyması zorunlu olan operasyonel talimatlardır.

HLK ve Executor (Claude);

* Aktif sahneye ait tüm davranışları uygulamak,
* Sahne içerisinde belirtilen işlem sırasını korumak,
* Sahne davranışlarını eksiksiz yerine getirmek

zorundadır.

Flow Diagram içerisinde tanımlanmayan hiçbir sahne davranışı, konuşma akışı veya işlem sırası üretilemez.

Flow Diagram ile çalışma zamanı davranışı arasında çelişki oluşursa;

* Flow Diagram esas alınır.
* Çalışma zamanı davranışı düzeltilir.
* Gerekirse kod güncellenir.

### Temel İlke

`08_HLK_FLOW_DIAGRAM.md`, yalnızca dokümantasyon değil, HLK'nın çalışma anında uygulanması zorunlu olan resmi operasyonel akış referansıdır.

---

HLK MASTER FLOW DIAGRAM_V1
HLK MASTER FLOW DIAGRAM_V1
 
🚀 OTURUM BAŞLANGICI
│
▼
/START
 │
▼
🟦 SAHNE-01 
-Hlk asistanı girişi
‘’hlk_sahne-1,(Native Video v3.5)’’ hlk asistan giriş videosu oynar,video bitince silinir.
-8 ADET DİL BOTUNU EKRANDA KALIR
🌍 DİL SEÇİMİ
│
▼
‘’ hlk_sahne-2,(Native Video v3.5)’’  hlk asistan videosu SEÇİLEN DİLDE oynar,video bitince silinir.
-Ekrandaki herşey silinir ve ekranda sadece tektilo efektli yazı baloncuğu kalır.
‘’Lütfen şimdi Ürününüzün linkini gönderin’’
🔗 ÜRÜN LİNKİ BEKLENİYOR
│
▼
-KULLANICI LİNK GÖNDERİR.
🟦 LİNK DOĞRULAMA
Ⅰ. 🤖 Arka planda’’Link Ajan Seçimi’’
-Link ajanları seçilir,puanlanır,sırasi ile atanır.(ana yasa)
│
▼
Ⅱ. ✅ Link Doğrulama
│
▼
Başarısız
│
└──►-Link dogrulanmazsa kullanıcıya mesaj tekrar link gönderin.(sınırlı sayıda-ana yasa)
Başarılı
│
▼
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille ‘’ Linkinizi aldım,ürün analizini başaltıyorum’’gibi.
Ⅰ. 🤖 Arka planda ‘’HLK Ürün Ajan Seçimi’’
-ürüne en uygun ajanlar seçilir,puanlanır,sırasi ile atanır.(ana yasa)
▼
Ⅱ. 🔍 Ürün Arka Plan Araştırması
📦 Ürün Analizi
🏷️ Marka Analizi
🖼️ Görsel Araştırması
🎯 Rakip Analizi
💰 Fiyat Analizi
👥 Hedef Kitle Analizi
-vb (ve benzeri)
│
▼
-EKRAN SİLİNİR.
🟦 SAHNE-02
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille ‘’ EK MATERYAL İSTER’’
-"Ürününüze ait ek materyalleriniz var mı?"gibi
────────────────────────────
Ⅰ. VAR
Ⅱ. YOK
────────────────────────────
VAR
│
▼
STATE_COLLECT_PRODUCT_MATERIALS
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıya uygun bir dille ‘’ kaç meteryal göndermesi gerektiği ve ne kadar süresi oldugu nazik bir dille anlatır’’
📷 Fotoğraf
🎥 Video
📚 Katalog
📄 Teknik Doküman
📦 Diğer tamamlayıcı Materyaller
│
▼
ilk meteryal gelir.
-HER EK METERYAL ALINDIĞINDA EKRAN SİLİNİR.
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıya uygun bir dille ‘’ ilk tamamlayıcı Meteryali aldığını,bir sonrası beklediğini’’benzer kelimelerle söyler.ve  ekranda ‘’Bitti’’ butonu oluşur.
[BİTTİ]
│
▼
SAHNE-03
YOK
│
└────────────►SAHNE-03
-EKRAN SİLİNİR.

→ MATERIALS_COLLECTED
-"📤 <b>Materyal yükleme modu</b> aktif.\n\nAşağıdaki materyalleri yükleyebilirsiniz:\n{category_list}\n\nHer materyal analiz edilerek reklam stratejisine dahil edilir.\n\nYüklemek istediğiniz <b>ilk materyali</b> gönderin 👇"

→ MATERIAL_UPLOADED
-"✅ <b>{count}. materyalinizi</b> aldım. Teşekkürler! 🙏\n\nVarsa bir sonraki materyali bekliyorum 👇"

🟦 SAHNE-03
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ VİDEO FORMATINI SEÇMESİNİ İSTER’’
-"Videonuzu hangi formatta hazırlamamı istersiniz?"gibi.
🟦◉ Dikey 9:16
📱 Telegram
🎵 TikTok
📸 Instagram Reels
▶️ YouTube Shorts
🟦 ○ Yatay 16:9
▶️ YouTube
📘 Facebook
🌐 Web Sitesi
🟦 ○ Kare 1:1
📸 Instagram Gönderi
📘 Facebook Gönderi
────────────────────────────
📌 Tek Seçim Yapılabilir
📌 Bir seçim yapıldığında
diğerleri iptal olur
    │
    ▼
-EKRAN SİLİNİR.
🟦 SAHNE-04
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ VİDEO ÇÖZÜNÜRLÜK SEÇİMİ YAPMASINI İSTER’’
-"Ürün tanıtım videonuzun görüntü çözünürlüğünün aşağıdakilerden hangisinin olmasını 
istersiniz?"gibi.
🟦 ○ 480p
(Ekonomik seçenek
Temel kullanım)
🟦 ◉ 720p HD ⭐
(Önerilen
Kalite ve bütçe dengesi)
🟦 ○ 1080p Full HD
(Daha yüksek kalite
Daha yüksek üretim maliyeti)
────────────────────────────
📌 Tek Seçim Yapılabilir
📌 Bir seçim yapıldığında
diğerleri iptal olur
    │
    ▼
-EKRAN SİLİNİR.
🟦 SAHNE-05
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ ÜRÜN VİDEOSUNUN ÜRETİM SÜRESİNİ BELİRLEMESİNİ İSTER  ’’
-‘’Reklam videonuzun süresini belirleyelim. Lütfen istediğiniz video süresini 4 ile 30 saniye arasında olacak şekilde aşağıya yazın.’’gibi.
-veriler 4-30 dışında ise
│
└────────────►hlk devreye girer,kullanıcıya uyarı (ana yasa)
Geçerli ise;
│
└────────────► SAHNE-06
◉ HLK'ya Bırak ⭐
(HLK 4 ile 30sn arası en uygun süreyi belirler)
    │
    ▼
-EKRAN SİLİNİR.
🟦 SAHNE-06
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ VİDEO’nun  TANITIM TARZI SEÇİMİ  YAPMASINI İSTER  ’’
-"Ürün tanıtım videonuzun tanıtım tarzı aşağıdakilerden hangisinin olmasını 
istersiniz?"gibi.
☐ UGC Tarzı ⭐(Ürün kullanıcısı gibi,infilüzür videosu tarzı)
☐ Geleneksel ile Modernin Buluşması
☐ Sanatsal / Sinematik
☐ Kendim Yazacağım
↓
HLK Özel İçerik Toplama Modu
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ Video için senaryo,promt,gönderme yol ve yöntemlerini anlatır  ’’
-"Ürün tanıtım videonuzun seneryosunu word formatında gönderebilirsiniz.?"gibi.
☐ HLK'ya Bırak ⭐
(HLK,Ürüne göre en uygun reklam tarzını belirler)
────────────────────────────
📌 Tek Seçim Yapılabilir
📌 Bir seçim yapıldığında
diğerleri iptal olur
    │
    ▼
-EKRAN SİLİNİR.
🟦 SAHNE-07  REKLAM HEDEF KİTLESİ
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ ÜRÜN VİDEO’sunun HEDEF KİTLESİNİN BELİRLENMESİN İSTER  ’’
-"Ürün tanıtım videonuzun hedef kitlesi aşağıdakilerden hangisidir.?"gibi.
☐ Çocuk (0-12)
☐ Genç (13-17)
☐ Genç Yetişkin (18-24)
☐ Yetişkin (25-34)
☐ Aile Kurmuş Yetişkin (35-44)
☐ Orta Yaş (45-54)
☐ Olgun Yetişkin (55-64)
☐ 65 Yaş ve Üzeri
────────────────────────────
📌 Tek Seçim Yapılabilir
📌 Bir seçim yapıldığında
diğerleri iptal olur
    │
    ▼
-EKRAN SİLİNİR.
🟦 SAHNE-08  VİDEO SESLİ/SESSİZ YAPISI
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ ÜRÜN VİDEO’sunun SESLİ/SESSİZ DURUMUNU BELİRLEMESİNİ İSTER  ’’
-"Ürün tanıtım videonuz için hedef ses seçiminiz nedir.?"gibi.
☐ 🎙️ Dış Seslendirme
☐ 🔊 Ortam Sesleri
☐ 🎵 Telifsiz Fon Müziği
════════════════════
☐🔇 SESSİZ
│
└────────────► SAHNE-11
(Video içerisinde
hiçbir ses kullanılmaz)
════════════════════
☐ 🔇 Sessiz
────────────────────────────
📌 Birden Fazla Seçim Yapılabilir
📌 Sessiz seçilirse diğer
seçenekler devre dışı kalır
    │
    ▼
-EKRAN SİLİNİR.
🟦 SAHNE-09    SESLİ VİDEO SESLENDİRME DİLİ SEÇİMİ
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ ÜRÜN VİDEO’sunun SESLENDİRME DİLİNİ BELİRLEMESİNİ İSTER  ’’
-"Ürün tanıtım videonuz için seslendirme dilini Yeryüzündeki resmi bütün dillerde seçebilirsiniz."gibi.
🇹🇷 Türkçe          EN English
🇩🇪 Deutsch        🇫🇷 Français
🇪🇸 Español         🇷🇺 Русский
AR العربية            🏳️Kurdî
────────────────────────────
🌍 Farklı Bir Dil Seçeceğim
────────────────────────────
📌 Tek Seçim Yapılabilir
📌 Bir seçim yapıldığında
diğerleri iptal olur
    │
    ▼
-EKRAN SİLİNİR.
🟦 SAHNE-10    SES KARAKTER SEÇİMİ
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ SES KARAKTERİNİN BELİRLEMESİNİ İSTER  ’’
-"Ürün tanıtım videonuz için Dış ses seçiminizi yapınız,kadın,erkek ve çoçuk herhangi birinini seçebilirsiniz"gibi.
☐ Kadın Ses
☐ Erkek Ses
☐ Çocuk Ses
────────────────────────────
📌 Tek Seçim Yapılabilir
📌 Ses yaşı, tonlama,
enerji, vurgu ve konuşma
ritmi HLK tarafından belirlenir.
    │
    │
    │
    ▼
-EKRAN SİLİNİR.
🟦 SAHNE-11    ÖZELLİKLE VURGULANACAKLAR SEÇİMİ
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ KULLANICIYA ÖZELLİKLE VURGULANMASINI İSTEDİĞİ ŞEY VAR MI ’’
-"Ürün tanıtım videonuz için özellikle dikkatimizi toplamamızı istediğiniz bir ayrıntı var mi?"gibi.
☐ 🏷️ İndirim
☐ 🚚 Ücretsiz Kargo
☐ 🎁 Hediye Paket Seçeneği
☐ ✨ Yeni Sezon Ürünü
☐ 🇹🇷 Yerli Üretim
☐ Ben Eklemek istiyorum
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ KULLANICIYA VERİ GİRMESİNİ SÖYLER ’’
-"Lütfen eklemek istediğiniz detayı birkaç kelime ile belirtiniz"gibi.
────────────────────────────
📌 Birden Fazla Seçim Yapılabilir
    │
    ▼
-EKRAN SİLİNİR.
🟦 SAHNE-12    TÜM SEÇİMLER EKRAN DA GÖSTERİLİR
-Bu Ekranda kullanıcının brief sırasında verdiği tüm bilgiler tek tek sıralanır.her verilmiş cevabın sol tarafında onay kutucuğu vardır ve çek edilmiş durumdadır.
-
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Kullanıcıdan uygun bir dille,‘’ KULLANICIYA BU BRİEF SIRASINDA VERDİĞİNİZ BİLGİLER GÖSTERİLMEKTEDİR,DER ’’
-"Bu bilgileri onaylıyormusuz ?"tarzında birşeyler söyler,
-Ekrandaki bilgi tik’lerinde biri kullanıcı tarafından kaldırılırsa hlk o ‘’tik i’’kaldırılan ekrana döner,kullanıcının yeni tik oluşturması ile tekrar;
                hlk
                │
                └────────────► SAHNE-12 döner.
-bu arada Ekran altında bir buton belirir.
   🟦   EVET
      │
      ▼
-EKRAN SİLİNİR.
🟦 SAHNE-13   BRIEF TAMAMLANDI
-hlk VİDEOSU (seçilen Dilde) ekranda konuşur.
‘’Brief tamamlanmıştır,sabrınıza çok teşekkür ederiz,ürün tanıtım videonuzun senaryo hazırlıkları başlamıştır,hazırlanan senaryo ‘’SENARYO HAZIR’’formu ile Telegram adresinize birkaç dakika içerisinde onay için gönderilecektir.Bol kazançlar dileriz’’
-video biter.
-EKRAN SİLİNİR.
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
-‘’Senaryo hazır, formu hazırlanıyor yazısı ekrana gelir.’’gibi bir yazı ekranda yazılır ve kalır.
-Senaryo hazır formu ekrana gelir,kullanıcı telegram adresine gönderilir.Ekrandaki diğer daktilo yazı baloncuğu silinir.
Ekranda iki buton belirir;
ONAY             RET
              │
  │
  │        └────────────► -HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
     │                                                                        ‘’ HLK kullanıcıya uygun bir dille;
     │
     │                                                                          "Senaryoyu onaylamadığınızı görüyorum.
     │                                                                           Yeni bir reklam çalışması başlatmak için
     │                                                                           lütfen tekrar /start komutu ile giriş yapınız."
     │                                                                           benzeri bir bilgilendirme yapar.
     │                                                                           ve oturumu kapatır.
     │              
  │                                                   │      
                                                      ▼
  ▼                                            -OTURUM KAPATILIR.
-Yönetici’den ürün Fiyat teklifi vermesini ister.
bu istekde;
-Ürün adı,seneryo,kullanılacak sahne detayları ile,kullanılan ajan ve platform isimleri,kullanılacak krediler,kalan krediler ve API durumları listelenir.
-Yöneticinin  fiyat teklifini  Kullanıcı telegram adresine ve ekrana gönderir.
-Ekranın altında;       
         ONAY             RET
                 │
  │
  │           └────────────► -HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
     │                                                              ‘’Tesekkür konuşması yapar’’ ve oturumu kapatır.                  
  │                                                   │      
  │                                                   ▼
  │                                            -OTURUM KAPATILIR.
  │
  ▼
     -hlk reklam üretimini başlatır.

---

### 🟦 STATE_PRICING EKRAN AKIŞI

STATE_PRICING aşaması iki resmi operasyon ekranından oluşur.

**1. HLK Yönetici Fiyatlandırma Formu** (Yalnızca Yönetici)

│
▼
🟦 YÖNETİCİ FİYATLANDIRMA FORMU
-HLK tarafından otomatik oluşturulur, yalnızca yöneticiye gönderilir.
-Amaç: Yöneticinin satış fiyatını belirlemesini sağlamak.
────────────────────────────────────
📋 Ürün özeti, Marka, Platform
🎬 Video süresi, Çözünürlük, Teslim süresi
📝 Senaryo özeti
────────────────────────────────────
⚙️ Kullanılan ajanlar ve servis sağlayıcılar
⚠️ Kullanılmayan servisler ve nedenleri
✅ API durumları, Servis Güven Skorları
💰 Mevcut kredi, Tahmini kredi tüketimi
📊 Üretim sonrası tahmini kredi durumu
────────────────────────────────────
🔴 Risk Analizi
-API problemleri, Kritik kredi seviyeleri
-Kota problemleri, Alternatif servisler
-Yönetici müdahalesi gerektiren durumlar
────────────────────────────────────
📈 Tahmini Maliyet, Tahmini Üretim Süresi
💡 HLK Operasyon Değerlendirmesi
💡 HLK Önerisi
────────────────────────────────────
Yönetici İşlemleri:
💰 Satış Fiyatı Giriş Alanı
🏷️ Kampanya Uygula
📉 İndirim Uygula
✅ Fiyatı Onayla
❌ İptal
│
▼
(Onay sonrası otomatik geçiş)

**2. HLK Kullanıcı Fiyat Teklif Formu** (Yalnızca Kullanıcı)

│
▼
🟦 KULLANICI FİYAT TEKLİF FORMU
-Yönetici tarafından belirlenen satış teklifi profesyonel form olarak sunulur.
-Yalnızca kullanıcıya gönderilir.
────────────────────────────────────
📋 Ürün Adı, Platform
🎬 Video Süresi, Çözünürlük
📅 Teslim Süresi
────────────────────────────────────
🛠️ Hizmet Kapsamı:
-Senaryo hazırlama, Yapay zekâ reklam üretimi
-Video üretimi, Seslendirme, Kurgu, Teslim
────────────────────────────────────
💵 Satış Fiyatı, Para Birimi
🧾 Vergi Bilgisi
⏳ Teklif Geçerlilik Süresi
────────────────────────────────────
ℹ️ Ödeme alındıktan sonra üretim başlar
ℹ️ Üretim süreci hakkında kısa açıklama
────────────────────────────────────
Kullanıcı İşlemleri:
✅ Teklifi Onayla → Ödeme Sürecine Geç
❌ Teklifi Reddet → Revizyon / Oturum Sonlandırma
│
▼
(Onay → Ödeme Doğrulama → Video Üretimi)

---

### 🟦 ÖDEME DOĞRULAMA AKIŞI (STATE_PAYMENT_VERIFICATION)

Kullanıcı Fiyat Teklif Formunda "ÖDEMEM GERÇEKLEŞTİ" butonuna bastığında:

│
▼
EVENT_PAYMENT_DECLARED
│
▼
🟦 STATE_PAYMENT_VERIFICATION
-HLK, Yönetici Ödeme Onay Formunu oluşturur.
-Yalnızca yöneticiye gönderilir.
────────────────────────────────────
📋 Başlık: ÖDEME DOĞRULAMA
ℹ️  Kullanıcı "ÖDEMEM GERÇEKLEŞTİ" bildirimi göndermiştir.
ℹ️  Lütfen banka hesabınızı kontrol ediniz.
ℹ️  Ödeme hesabınıza ulaştıysa aşağıdaki butona basınız.
────────────────────────────────────
Yönetici İşlemleri:
✅ ÖDEMEYİ ONAYLA → EVENT_PAYMENT_APPROVED
❌ RET → STATE_SESSION_CLOSED
│
▼
(ÖDEMEYİ ONAYLA)
│
▼
EVENT_PAYMENT_APPROVED
│
▼
STATE_VIDEO_PRODUCTION
│
▼
🆔 PID OLUŞTURULUR
-HLK tarafından benzersiz Production ID (PID) oluşturulur.
-Format: PID-YYYYMMDD-NNNN (örn. PID-20260701-0001)
-PID, bu üretimin tüm kayıtlardaki tek resmi kimliğidir.
│
▼
📦 PRODUCTION PACKAGE OLUŞTURULUR
-HLK tarafından Production Package oluşturulur.
-PID'ye bağlı tüm üretim bileşenlerinin ana kapsayıcısı.
-Task Package'ler bu kapsayıcı altında oluşturulur.
│
▼
📋 TASK PACKAGE'LER OLUŞTURULUR
-Her Agent için özel Task Package hazırlanır.
-Agent'lar yalnızca kendi Task Package'ine erişebilir.
│
▼
🎬 VİDEO ÜRETİMİ BAŞLAR
│
▼
Kullanıcıya Telegram yazı balonu gönder:
"Ödemenizi aldık.
Video üretiminiz başlatılmıştır.
Bu süreç yaklaşık 10–15 dakika sürmektedir.
Video tamamlandığında otomatik olarak size gönderilecektir."
│
▼
Reklam Üretim Süreci (PID ile ilişkilendirilir)

---

### 🟦 EKRAN GEÇİŞ SIRASI

Senaryo Onay Formu
↓
HLK Yönetici Fiyatlandırma Formu
↓
HLK Kullanıcı Fiyat Teklif Formu
↓
Ödeme Bildirimi (Kullanıcı "ÖDEMEM GERÇEKLEŞTİ")
↓
Yönetici Ödeme Onay Formu (ÖDEME DOĞRULAMA)
↓
Ödeme Onayı (Yönetici "ÖDEMEYİ ONAYLA")
↓
Reklam Üretim Süreci

---

Tasarım Standardı: HLK Premium Card Architecture, HLK UI Component Library, HLK Design Token Architecture

Her iki ekranda sol üst köşede aynı HLK karakteri kullanılır.

Her iki ekran aynı renk paletini, ikon yapısını, kart mimarisini ve buton tasarımını kullanır.

---
-EKRAN SİLİNİR.
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Uygun bir dille,‘’ KULLANICIYA reklam üretiminin başladını nazik bir dille belirtir.’’
-‘’Ödemenizi aldık. Video üretiminiz başlatılmıştır. Bu süreç yaklaşık 10–15 dakika sürmektedir. Video tamamlandığında otomatik olarak size gönderilecektir.’’tarzı birşeyler söyler.
-Reklam hazırlandığında video kullanıcının telegram adresine gönderilir.bir kopyası  da proje arşivinde saklanır.
-OTURUM KAPATILIR.

## FD-008_2

### State-Event-Action Referans Tablosu

HLK Flow Diagram içerisinde kullanılan tüm state, event ve modül eşleştirmelerinin referans tablosudur.

| State | Event | Açıklama | Modül |
|-------|-------|----------|-------|
| `STATE_START` | `EVENT_START_INITIATED` | Oturum başlangıcı | - |
| `STATE_LANGUAGE_SELECTION` | `EVENT_LANGUAGE_SELECTED` | Dil seçimi | Language Selection UI |
| `STATE_WAIT_PRODUCT_LINK` | `EVENT_PRODUCT_LINK_RECEIVED` | Ürün linki bekleniyor | Link Input Handler |
| `STATE_LINK_VALIDATION` | `EVENT_LINK_VALIDATED` / `EVENT_LINK_INVALID` | Link doğrulama | Link Validation Orchestrator |
| `STATE_LINK_VALIDATED` | `EVENT_RESEARCH_STARTED` | Link doğrulandı | - |
| `STATE_BACKGROUND_RESEARCH_RUNNING` | `EVENT_CONVERSATION_STARTED` | Arka plan araştırması | Product, Brand, Image Research |
| `STATE_ACTIVE_CONVERSATION` | `EVENT_MATERIALS_COLLECTED` | Aktif konuşma | Conversation Screen, Scene Engine, Daktilo Efekti |
| `STATE_COLLECT_PRODUCT_MATERIALS` | `EVENT_PLATFORM_SELECTED` | Materyal toplama | Material Upload, Validation |
| `STATE_PLATFORM_SELECTION` | `EVENT_VIDEO_SETTINGS_DONE` | Platform seçimi | - |
| `STATE_VIDEO_SETTINGS` | `EVENT_BRIEF_COMPLETED` | Video ayarları | - |
| `STATE_BRIEF_COMPLETED` | `EVENT_VIDEO_PRODUCTION_DONE` | Brief tamamlandı | - |
| `STATE_PAYMENT_VERIFICATION` | `EVENT_PAYMENT_DECLARED` / `EVENT_PAYMENT_APPROVED` | Ödeme doğrulama | Yönetici Ödeme Onay Formu |
| `STATE_VIDEO_PRODUCTION` | `EVENT_SESSION_ENDED` | Video üretimi (PID oluşturulur) | PID Generator, Prompt Builder, Video Gen, Render |
| `STATE_SESSION_COMPLETED` | - | Oturum tamamlandı | - |
| `STATE_SESSION_TIMEOUT` | `EVENT_SESSION_CLOSED` | Zaman aşımı | - |
| `STATE_SESSION_CLOSED` | - | Oturum kapatıldı | - |

---

## FD-008_3

### Hata ve İstisna Akışları

Normal akış dışında gerçekleşebilecek hata ve istisna durumlarını tanımlar.

```
Link Doğrulama Başarısız
STATE_LINK_VALIDATION
→ EVENT_LINK_INVALID
→ STATE_WAIT_PRODUCT_LINK
→ Kullanıcı yeni link gönderir

Platform Erişim Engeli
STATE_LINK_VALIDATION
→ ERISIM_ENGELLI
→ Alternatif link istenir
→ STATE_WAIT_PRODUCT_LINK

Oturum Zaman Aşımı
STATE_WAIT_PRODUCT_LINK / STATE_ACTIVE_CONVERSATION / STATE_COLLECT_PRODUCT_MATERIALS
→ EVENT_TIMEOUT_REACHED
→ STATE_SESSION_TIMEOUT
→ EVENT_SESSION_CLOSED
→ STATE_SESSION_CLOSED

Maksimum Deneme Sayısı
STATE_WAIT_PRODUCT_LINK (5 başarısız deneme)
→ Oturum sonlandırılır
→ STATE_SESSION_CLOSED

Eksik Brief
STATE_BRIEF_COMPLETED
→ Eksik bilgi tespit edildi
→ İlgili sahneye geri dönülür
```

---

## FD-008_4

### Gelecek Genişletmeler için Rezerve Alan

Bu bölüm ileride eklenecek yeni akış şemaları, alt diyagramlar ve genişletmeler için ayrılmıştır.

Planlanan genişletmeler:

* Session Resume Flow (Kesinti sonrası oturum devam)
* Multi-Product Flow (Aynı anda birden fazla ürün)
* A/B Test Flow (Farklı reklam varyantları)
* Analytics Flow (Performans takibi ve optimizasyon)

---

## FD-008_5

### Conversation Scene Presentation Standard

HLK içerisinde kullanılan Conversation Scene videoları varsayılan olarak orijinal boyutlarında sunulur.

Conversation Scene sunumu sırasında:

• Zoom In uygulanmaz.
• Zoom Out uygulanmaz.
• Yapay küçültme uygulanmaz.
• Karakter görünürlüğünü azaltan ölçekleme işlemleri uygulanmaz.

HLK'nin amacı video alanını küçültmek değil, karakter görünürlüğünü korumaktır.

Bu nedenle kullanıcı önce HLK karakterini görmeli, ardından konuşma içeriğini okumalıdır.

Conversation Scene tasarımı sırasında HLK karakteri sahnenin ana görsel unsuru olarak kabul edilir.

Konuşma balonları mümkün olan durumlarda video içerisine entegre edilmelidir.

Video dışı konuşma katmanları yalnızca teknik zorunluluk veya özel kullanım senaryolarında kullanılabilir.

Conversation Scene videoları;

• Telegram arayüzünü taklit etmek,
• Yapay boşluk oluşturmak,
• Karakter alanını küçültmek,
• Video alanını daraltmak

amacıyla yeniden ölçeklendirilmemelidir.

Beklenen Sonuç

AR-002_41 Native Video Presentation Architecture ile uyumlu resmi sunum standardı oluşturulmuş olur.

Conversation Scene tasarımlarında eski "%70 Small Video" yaklaşımı kullanım dışı bırakılmış olur.

Orijinal Hedra videolarının doğal boyutlarında kullanılması sistem standardı haline gelir.

Bu standart, Active Conversation Screen ve Conversation Scene Engine üzerinde oluşturulan tüm gelecekteki sahneler için referans kabul edilir.

---

## FD-008_6

### Development Status Annotation Standard

Flow Diagram yalnızca kullanıcı akışını değil, ilgili akışın geliştirme durumunu da gösterebilir.

Bu nedenle aşağıdaki durum işaretleri tanımlanmıştır.

────────────────────────────────

⚪ **Başlanmadı**

İlgili sahne, modül veya akış henüz geliştirilmemiştir.

────────────────────────────────

🟡 **Geliştirme Aşamasında**

İlgili sahne, modül veya akış üzerinde aktif geliştirme devam etmektedir.

Kod bulunabilir.

Ancak tamamlanmış kabul edilmez.

────────────────────────────────

🟠 **Test Aşamasında**

Geliştirme tamamlanmıştır.

Ancak kullanıcı testleri veya sistem testleri devam etmektedir.

Tamamlanmış kabul edilmez.

────────────────────────────────

✅ **Tamamlandı**

İlgili sahne, modül veya akış:

• geliştirilmiştir

• test edilmiştir

• Proje Yöneticisi tarafından onaylanmıştır

Tamamlanmış kabul edilir.

────────────────────────────────

🔒 **Canlı Sistem**

İlgili bileşen üretim ortamında aktif olarak kullanılmaktadır.

────────────────────────────────

**Raporlama Kuralı**

HLK rapor üretirken:

Kodun mevcut olmasını "tamamlandı" kriteri olarak kullanamaz.

Öncelikle ilgili akışın veya sahnenin Flow Diagram üzerindeki resmi durumunu kontrol etmelidir.

Flow Diagram üzerinde:

✅ bulunuyorsa → Tamamlandı

🟠 bulunuyorsa → Test Aşamasında

🟡 bulunuyorsa → Geliştirme Aşamasında

⚪ bulunuyorsa → Başlanmadı

olarak raporlanmalıdır.

────────────────────────────────

**Temel İlke**

Kodun var olması tamamlandığı anlamına gelmez.

Tamamlandı durumu yalnızca Proje Yöneticisi onayı ile verilir.

Flow Diagram üzerindeki resmi durum işaretleri, HLK'nın raporlama sırasında kullanacağı tek geliştirme durumu referansıdır.

────────────────────────────────

**Uygulama Notu**

Bu işaretler proje geliştirme sürecinde kullanılır.

Proje canlıya alındığında veya Proje Yöneticisi uygun gördüğünde kaldırılabilir.

Ancak geliştirme süresince HLK'nın ilerleme durumunu takip etmek için resmi referans kabul edilir.

────────────────────────────────

**Beklenen Sonuç**

HLK artık bir sahnenin veya modülün durumunu raporlarken yalnızca kodun varlığına göre karar veremez.

Flow Diagram üzerindeki resmi geliştirme durumu işaretlerini esas almak zorundadır.

Böylece:

**Kod Var ≠ Tamamlandı**

kuralı proje genelinde standart hale gelir.

---

## FD-008_7

### Development Status Approval Workflow

Bir bileşenin geliştirme durumunun nasıl değiştirileceğini ve Proje Yöneticisi onay sürecini tanımlar.

────────────────────────────────

**Tamamlandı Adaylığı**

HLK bir sahnenin, modülün veya akışın:

• geliştirmesinin tamamlandığını,

• testlerinin başarıyla geçtiğini,

• ANA YASA ile uyumlu olduğunu

tespit ederse ilgili bileşeni:

"Tamamlandı Adayı"

olarak işaretleyebilir.

────────────────────────────────

**Yönetici Onayı**

HLK aşağıdaki formatta Proje Yöneticisine bildirim sunar:

Bu bileşen "Tamamlandı" durumuna adaydır.

Kararınızı belirtiniz:

1- Evet → ✅ Tamamlandı

2- Hayır → Mevcut durum korunur

────────────────────────────────

**Yetki Kuralı**

HLK:

• analiz yapabilir,

• test yapabilir,

• adaylık önerebilir.

Ancak:

✅ **Tamamlandı**

durumunu doğrudan veremez.

Bu işaret yalnızca Proje Yöneticisi tarafından atanabilir.

────────────────────────────────

**Temel İlke**

HLK önerir.

Proje Yöneticisi karar verir.

Karar sonrasında Flow Diagram üzerindeki resmi durum güncellenir.

---
---
## SİSTEM EVENT KONUŞMALARI

Aşağıdaki event'ler sahneye özgü değildir. Sistem seviyesinde çalışır.
Tüm konuşmalar Conversation Scene Engine tarafından üretilir.

→ LINK_INVALID
-"❌ Geçersiz URL! Lütfen geçerli bir web sitesi linki gönderin.\n\nÖrnek: https://www.orneksite.com"

→ LINK_RECEIVED
-"⏳ Link alındı! Ürün bilgileri analiz ediliyor..."

→ LINK_VALIDATED_INFO
-"✅ Link doğrulandı!\n\n🔍 Ürün araştırması başlatılıyor..."

→ LINK_ERROR
-"❌ Bir hata oluştu!\n\nLütfen /start yazarak baştan başlayın."

→ SESSION_CANCELLED
-"❌ İşlem iptal edildi.\n\nBaşlamak için /start yazın."

→ SESSION_NOT_STARTED
-"🤖 Henüz bir oturum başlatılmadı.\nLütfen /start yazarak görüşmeye başlayınız."

→ LANGUAGE_REQUIRED
-"🌐 Lütfen kullanacağınız dili seçiniz."

→ AUDIO_SELECTION_SAVED
-"✅ Ses seçiminiz kaydedildi.\n\n📋 Brief hazırlanıyor..."

→ SAHNE_TRANSITION
-"⏳ Devam ediliyor..."
