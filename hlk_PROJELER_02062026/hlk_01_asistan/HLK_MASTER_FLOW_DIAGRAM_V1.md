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
-EKRAN SİLİNİR.
-HLK Asistanı,daktilo formunda yazı baloncuğu kullanarak,
Uygun bir dille,‘’ KULLANICIYA reklam üretiminin başladını nazik bir dille belirtir.’’
-‘’Reklam üretimi başlamıştır,bu 5 ile 10 dakika arsında sürmektedir,video hazır olduğunda telegram adresinize gönderilecektir’’tarzı birşeyler söyler.
-Reklam hazırlandığında video kullanıcının telegram adresine gönderilir.bir kopyası  da proje arşivinde saklanır.
-OTURUM KAPATILIR.
