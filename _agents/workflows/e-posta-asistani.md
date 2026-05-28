---
description: E-posta Asistanı — Her gün 12:00'da mailleri oku, gereksizleri temizle, önemlilere taslak cevap hazırla
---

# 🤖 E-posta Asistanı (Gelen Kutusu Yönetimi)

> **Amaç:** Her gün saat 12:00'da otomatik olarak çalışarak gelen kutusunu düzenlemek, gereksiz mailleri ayıklamak ve cevaplanması gereken mailler için taslak yanıtlar oluşturmak.

Bu akış, yapay zeka gücüyle e-postalarınızı analiz eder, önemsizleri okundu işaretleyip arşivler ve önemli olanlar için onayınıza sunulmak üzere taslak cevaplar hazırlar.

---

## 🧠 Tercih Edilen Yapay Zeka Modeli

Bu görev (metin sınıflandırma, bağlam anlama ve profesyonel e-posta taslağı yazma) için en iyi sonucu alacağımız model: **Claude 3.5 Sonnet** veya **Gemini 1.5 Pro**'dur. 
- **Neden?** Claude 3.5 Sonnet, insan benzeri ve doğal e-posta yazımında şu an endüstri lideridir. Gemini 1.5 Pro ise çok uzun e-posta zincirlerini tek seferde hatasız okuyup analiz edebilir. Akışta metin analizi için bu modellerin API'si kullanılacaktır.

---

## ⚙️ Akış Diyagramı ve Çalışma Mantığı

### Adım 1: Zamanlayıcı (Cron) ve Bağlantı
1. **Tetikleyici:** Sistem her gün tam saat **12:00**'da (öğlen) otomatik olarak uyanır.
2. **Bağlantı:** Gmail API üzerinden kullanıcının e-posta hesabına güvenli bir şekilde bağlanır.
3. **Okuma:** Son 24 saat içinde gelen veya "okunmamış" durumdaki tüm mailleri çeker.

### Adım 2: Yapay Zeka ile Analiz ve Sınıflandırma
Çekilen her bir mail, Yapay Zeka modeline gönderilir. YZ mailleri iki ana kategoriye ayırır:

- **Kategori A: Gereksiz / Operasyonel Mailler**
  - Tanıtımlar, reklamlar, spam benzeri mailler, bildirimler, otomatik fatura/sistem mesajları vb.

- **Kategori B: Önemli / Aksiyon Gerektiren Mailler**
  - Gerçek kişilerden gelenler, iş ile ilgili sorular, acil durumlar, kişisel talepler vb.

### Adım 3: Gereksiz Maillerin Temizlenmesi (Kategori A)
Kategori A'ya giren mailler için uygulanacak aksiyonlar:
1. **Okundu İşaretle:** Mail anında "Okundu" (Read) olarak işaretlenir.
2. **Dosyala/Arşivle:** Gmail'de önceden oluşturulmuş özel bir klasöre/etikete (Örn: `Gereksizler_AI` veya `Otomatik Arşiv`) taşınır.
3. *Gelen kutusu bu sayede tamamen temiz ve odaklanmaya hazır kalır.*

### Adım 4: "Gelen Mail Cevaplar Dosyası" ve Taslak Üretimi (Kategori B)
Kategori B'ye giren (önemli) mailler için uygulanacak aksiyonlar:
1. **Taslak Oluşturma:** YZ, gelen mailin bağlamına ve sizin daha önceki iletişim tarzınıza uygun profesyonel bir taslak cevap yazar.
2. **Dosyalama:** Bu mailler ve hazırlanan taslak cevaplar, sistemde **"Gelen Mail Cevaplar Dosyası"** adı verilen bir alanda toplanır. (Bu mailler için Gmail içinde özel bir etiket oluşturulabileceği gibi, okuması kolay olsun diye hepsi tek bir belgede de listelenebilir).
3. **KAYDET AMA GÖNDERME:** Hazırlanan taslaklar kesinlikle otomatik olarak **GÖNDERİLMEZ**. Sadece Gmail taslakları (Drafts) olarak kaydedilir.

### Adım 5: İnsan Onayı (Human-in-the-Loop)
1. **İnceleme:** Siz müsait olduğunuzda "Gelen Mail Cevaplar Dosyası"nı açarsınız.
2. **Düzenleme:** YZ'nin hazırladığı taslakları okur, gerekirse metinde ufak düzeltmeler (ton ayarı, eksik bilgi ekleme) yaparsınız.
3. **Gönderim:** Taslak son haline geldikten sonra sizin kontrolünüzle ve tek bir tıklamanız ile mailler karşı tarafa gönderilir.

---

## 🛠 Teknik Gereksinimler

*   **Otomasyon Aracı:** n8n, Make.com veya özel Python Script (Günlük zamanlayıcı ve API bağlantıları için)
*   **Mail Sağlayıcı:** Gmail API
*   **Yapay Zeka:** Anthropic API (Claude 3.5 Sonnet) veya Google Gemini API (Gemini 1.5 Pro)

---

## 🚀 Sonraki Adımlar

Bu taslak onaylandıktan sonra, sistemi çalışır hale getirmek için **n8n** üzerinde veya bir **Python scripti** (cron job ile çalışan) aracılığıyla teknik kurulumlara geçebiliriz.
