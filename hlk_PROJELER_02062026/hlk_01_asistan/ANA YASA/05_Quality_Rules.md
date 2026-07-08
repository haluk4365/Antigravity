# 05 — Quality Rules

Kalite kuralları.

---

## QR-004_1

HLK, bir link doğrulama görevini Başarılı veya Başarısız olarak sonuçlandırdığında, kararın oluşmasına neden olan tüm doğrulama gerekçelerini kayıt altına alır.

HLK, karar sırasında değerlendirilen olumlu ve olumsuz gerekçeleri ayrı ayrı raporlayabilir.

Bir link doğrulama görevi başarısız sonuçlandığında HLK yalnızca "Başarısız" sonucunu üretmez.

Başarısızlığa neden olan doğrulama maddeleri ve karar gerekçeleri görünür şekilde raporlanır.

Bir link doğrulama görevi başarılı sonuçlandığında HLK, başarı kararına katkı sağlayan gerekçeleri görünür şekilde raporlayabilir.

Karar raporları; şeffaflık, denetlenebilirlik ve kalite kontrol süreçlerinin bir parçası olarak saklanır.

---

## QR-004_2

### Native Video Scene Quality Rules

HLK V1 içerisinde kullanılan Native Video Scene mimarisinin kalite standartlarını tanımlar.

### Kriterler

Native Video Scene dosyası başarılı şekilde açılabilmelidir.

Video dosyası bozuk olmamalıdır.

Video süresi ilgili sahne tanımı ile uyumlu olmalıdır.

Video çözünürlüğü tanımlı standart ile uyumlu olmalıdır.

Video oynatma tamamlanabilmelidir.

Video tamamlandıktan sonra ilgili state geçişi çalışmalıdır.

Video kaldırma işlemi başarılı olmalıdır.

Native Video Scene sırasında ekran bütünlüğü korunmalıdır.

Dosya erişilebilirlik kontrolü yapılmalıdır.

Video dosya bütünlüğü doğrulanmalıdır.

Scene Delivery kuralları ile uyumlu olmalıdır.

Kalite kontrol başarısız olursa hata kaydı oluşturulmalıdır.

### Referans Mimari Kurallar

AR-002_39 Native Video Scene Architecture v3.5
AR-002_40 Native Video Scene Completion Architecture
AR-002_41 Native Video Presentation Architecture
AR-002_42 Conversation Scene Lifecycle Architecture
AR-002_43 Native Video Scene Runtime Validation Architecture

---

## QR-004_3

### Scenario And Pricing Quality Rules

STATE_SCENARIO_APPROVAL ve STATE_PRICING süreçlerinde oluşturulan çıktıların kalite standartlarını tanımlar.

### Scenario Approval Kriterleri

Oluşturulan senaryo brief verileri ile uyumlu olmalıdır.

Senaryo özeti eksiksiz oluşturulmalıdır.

Platform bilgileri doğru gösterilmelidir.

Süre bilgisi doğru gösterilmelidir.

Format bilgisi doğru gösterilmelidir.

ONAY ve RET seçenekleri eksiksiz sunulmalıdır.

Yanlış state yönlendirmesi olmamalıdır.

### Pricing Kriterleri

Fiyat teklifi eksiksiz hazırlanmalıdır.

Üretim parametreleri doğru hesaplanmalıdır.

Teklif içeriği kullanıcıya eksiksiz sunulmalıdır.

ONAY ve RET seçenekleri eksiksiz çalışmalıdır.

ONAY sonrası yalnızca STATE_VIDEO_PRODUCTION başlatılmalıdır.

RET sonrası yalnızca STATE_SESSION_CLOSED başlatılmalıdır.

### Genel Kriterler

Kalite kontrol başarısız olursa hata kaydı oluşturulmalıdır.

Kalite sonuçları loglanmalıdır.

### Referans Kurallar

AR-002_44 Scenario Approval Architecture
AR-002_45 Pricing Architecture
OR-004_6 STATE_SCENARIO_APPROVAL Operasyonel Kuralları
OR-004_7 STATE_PRICING Operasyonel Kuralları

---

## QR-004_4

### Video Production Quality Rules

STATE_VIDEO_PRODUCTION sürecinde üretilen videonun V1 standartlarına uygunluğunu doğrulayan kalite kurallarını tanımlar.

### Video Input Validation

Video üretimi yalnızca onaylanmış brief verileri ile başlamalıdır.

Kilitlenmiş brief verisi kullanılmalıdır.

Eksik üretim parametresi bulunmamalıdır.

### Video Output Validation

Üretilen video dosyası başarıyla oluşturulmalıdır.

Dosya erişilebilir olmalıdır.

Dosya bozuk olmamalıdır.

Video oynatılabilir olmalıdır.

Video süresi brief verisi ile uyumlu olmalıdır.

Video formatı brief verisi ile uyumlu olmalıdır.

Video çözünürlüğü brief verisi ile uyumlu olmalıdır.

### Native Video Scene

AHU karakter görünürlüğü doğrulanmalıdır.

Video kadrajı AR-002_41 ile uyumlu olmalıdır.

Video tamamlanma olayı doğru üretilmelidir.

Scene cleanup işlemi başarılı çalışmalıdır.

Sonraki state geçişi başarılı çalışmalıdır.

### Error Management

Üretim hataları kayıt altına alınmalıdır.

Kritik hata durumları loglanmalıdır.

Başarısız üretim girişimleri raporlanmalıdır.

### Genel Kriterler

Kalite sonuçları loglanmalıdır.

Başarılı kalite kontrol sonucu kayıt altına alınmalıdır.

### Referans Kurallar

OR-004_8 STATE_VIDEO_PRODUCTION Operasyonel Kuralları
AR-002_39 Native Video Scene Architecture v3.5
AR-002_40 Native Video Scene Completion Architecture
AR-002_41 Native Video Presentation Architecture
AR-002_42 Conversation Scene Lifecycle Architecture
AR-002_43 Native Video Scene Runtime Validation Architecture

---

## QR-004_5

### Session Management Quality Rules

HLK V1 içerisinde oturum yönetimi, timeout yönetimi, session kapatma ve session tamamlama süreçlerinin kalite standartlarını tanımlar.

### Timeout Management

Bekleme süresi doğru başlatılmalıdır.

Hatırlatma mesajı doğru zamanda gönderilmelidir.

Timeout süresi doğru hesaplanmalıdır.

Timeout tetiklenmesi doğru çalışmalıdır.

EVENT_TIMEOUT_REACHED doğru üretilmelidir.

### STATE_SESSION_TIMEOUT

Timeout mesajı kullanıcıya gösterilmelidir.

Timeout nedeni kayıt altına alınmalıdır.

Veri kaybı oluşmamalıdır.

### STATE_SESSION_CLOSED

Session kapatma işlemi tamamlanmalıdır.

Tüm görevler sonlandırılmalıdır.

Kaynak temizliği tamamlanmalıdır.

Geçici veriler temizlenmelidir.

Log kaydı oluşturulmalıdır.

Kullanıcı yeniden başlatma bilgisi almalıdır.

### STATE_SESSION_COMPLETED

Teslim edilen çıktı doğrulanmalıdır.

Teslim bilgisi kayıt altına alınmalıdır.

Oturum başarıyla tamamlandı olarak işaretlenmelidir.

### Error Management

Session kapatma hataları kayıt altına alınmalıdır.

Timeout yönetim hataları kayıt altına alınmalıdır.

### Genel Kriterler

Kalite sonuçları loglanmalıdır.

Başarılı kalite kontrol sonucu kayıt altına alınmalıdır.

### Referans Kurallar

OR-004_9 STATE_SESSION_TIMEOUT ve STATE_SESSION_CLOSED Operasyonel Kuralları

---

## QR-004_7

### AHU Voice Quality Rules

HLK V1 içerisinde kullanılan AHU ses üretim mimarisinin kalite standartlarını tanımlar.

### Voice Confidence Score

Voice Confidence Score üretilen her ses çıktısı için hesaplanmalıdır.

Minimum kabul eşiği tanımlanmalıdır.

Eşik altında kalan ses çıktıları yeniden üretilmelidir.

Maksimum yeniden deneme sayısı aşılırsa hata kaydı oluşturulmalıdır.

### ElevenLabs TTS Kalitesi

TTS çıktısı MASTER_REFERENCE_VOICE ile uyumlu olmalıdır.

Ses karakteri AHU karakter kimliğini korumalıdır.

Çoklu dil ses üretiminde karakter tutarlılığı doğrulanmalıdır.

Farklı dillerde üretilen sesler aynı karakter hissini taşımalıdır.

### Hata Yönetimi

Ses üretim hataları kayıt altına alınmalıdır.

Voice Confidence Score başarısız kayıtları loglanmalıdır.

Yeniden üretim girişimleri kayıt altına alınmalıdır.

### Genel Kriterler

Ses kalite sonuçları loglanmalıdır.

Başarılı kalite kontrol sonucu kayıt altına alınmalıdır.

### Referans Kurallar

AR-002_29 AHU Character Identity and Reference Library Architecture
AR-002_30 AHU Multi-Language Voice Generation Architecture
AR-002_32 Master Reference Voice Architecture
AR-002_37 Language Adaptive AHU Voice Architecture
OR-004_4 Ses, Dil, Karakter ve Vurgu Seçim Operasyonel Kuralları

---

## QR-004_8

### Voice Technology Provider Validation and Fallback

HLK, ses üretiminde belirli bir Voice Technology Provider'a bağımlı değildir.

Selection Architecture tarafından seçilen Voice Technology Provider kullanılmadan önce;

* Servis erişilebilirliği,
* API durumu,
* Kota ve kredi durumu,
* Teknik kullanılabilirlik

doğrulanmalıdır.

Servis teknik olarak kullanılabilir durumda olsa bile, ürettiği örnek ses **MASTER_REFERENCE_VOICE (AHU)** ile karşılaştırılmalıdır.

Karşılaştırma sonucunda hesaplanan **Voice Confidence Score**, sistemde tanımlı minimum kalite eşiğini karşılamıyorsa bu sağlayıcı o üretim görevi için başarısız kabul edilir.

HLK bu durumda otomatik olarak Selection Architecture tarafından belirlenen bir sonraki uygun Voice Technology Provider'a geçer.

Bu doğrulama ve gerektiğinde sağlayıcı değişimi, kalite eşiğini sağlayan bir Voice Technology Provider bulununcaya kadar veya aday sağlayıcı listesi tükeninceye kadar devam eder.

Ses üretim görevi yalnızca **MASTER_REFERENCE_VOICE (AHU)** ile uyumluluk eşiğini sağlayan Voice Technology Provider kullanılarak tamamlanabilir.

Tüm doğrulama sonuçları, sağlayıcı geçişleri, Voice Confidence Score değerleri ve başarısızlık nedenleri sistem günlüklerine kayıt altına alınmalıdır.

---

### Amaç

Bu mimarinin amacı;

* HLK'nın belirli bir ses servis sağlayıcısına bağımlı olmamasını sağlamak,
* AHU karakter kimliğini tüm sağlayıcılarda korumak,
* Ses üretim kalitesini standartlaştırmak,
* Sağlayıcı arızalarında üretimin kesintiye uğramasını önlemek,
* En yüksek kaliteyi sağlayan Voice Technology Provider ile üretimi gerçekleştirmektir.

---

### Beklenen Sonuç

* HLK otomatik olarak uygun Voice Technology Provider'ı doğrular.
* Gerekirse sağlayıcı değişimini kullanıcıya yansıtmadan gerçekleştirir.
* AHU karakteri sağlayıcı değişse bile korunur.
* Ses üretiminde kalite sürekliliği sağlanır.
* Voice Technology Provider bağımsızlığı ANA YASA'da resmen tanımlanmış olur.
