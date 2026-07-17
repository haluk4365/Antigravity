# 06 — Module Rule

Modül kuralları.

---

## MR-0005_1

### Kural

SAHNE-2 tamamlandıktan sonra HLK'nın kullanıcı ile gerçekleştireceği tüm dinamik konuşmalar ortak bir **Konuşma Arayüzü Modülü (Conversation UI Module)** standardına göre yürütülür.

HLK'nın söyleyeceği konuşmalar önceden tanımlanmaz.

HLK;

* bulunduğu STATE,
* elde etmesi gereken bilgi,
* ANA KURALLAR,
* mevcut oturum bilgisi,

doğrultusunda konuşmasını kendisi üretir.

Hazır soru veya hazır konuşma metni kullanılmaz.

Her yeni konuşma döngüsünde aşağıdaki işlem sırası uygulanır:

### Varsayılan mod — TEXT_ONLY_MODE

1. Kullanıcının son cevabı sisteme alınır.
2. HLK bulunduğu STATE'i belirler.
3. HLK elde etmesi gereken bilgiyi belirler.
4. HLK konuşma metnini kendisi oluşturur (veya Scene Registry'den alır).
5. Önceki konuşma baloncukları temizlenir.
6. Yeni konuşma baloncuğu oluşturulur.
7. Daktilo efekti çalışır (varsayılan hız: 0.06sn/kelime).
8. Metin tamamlanır.
9. Gerekliyse seçim butonları gösterilir.
10. HLK kullanıcının cevabını bekleme durumuna geçer.

**Bu modda ses üretimi, TTS, MP3 ve voice message kullanılmaz.**

### VOICE_ENABLED modu (opsiyonel, gelecek kullanım için)

`VOICE_ENABLED = TRUE` olarak etkinleştirildiğinde aşağıdaki adımlar 5. adımdan sonra uygulanır:

5. Seçilen kullanıcı diline göre arka planda ses üretimi başlatılır.
6. Ses hazırlanırken önceki konuşma baloncukları temizlenir.
7. Yeni konuşma baloncuğu oluşturulur.
8. Baloncuğun altında HLK'ya ait mavi renkli ses dalga animasyonu oluşturulur.
9. Ses hazır olduğunda:
   - ses oynatılır,
   - mavi ses dalga animasyonu çalışır,
   - konuşma balonundaki yazı daktilo efekti ile ses ile senkron şekilde oluşur.
10. Ses tamamlandığında baloncuk metni de tamamlanmış olmalıdır.
11. HLK kullanıcının cevabını bekleme durumuna geçer.

---

### Kullanıcı Arayüzü İlkesi

Kullanıcı hiçbir zaman;

* SORU-1,
* SORU-2,
* SORU-3,
* SORU-n,

veya benzeri teknik numaralandırmaları görmez.

Kullanıcı yalnızca;

* HLK'nın konuşma balonunu,
* daktilo efekti ile yazılan metni,
* seçim butonlarını

görür.

*VOICE_ENABLED modunda ayrıca mavi ses dalga animasyonu ve ses oynatma da gösterilir.*

Bir konuşma tamamlandıktan sonra sistem aynı kullanıcı arayüzü standardı ile bir sonraki konuşma döngüsüne geçer.

SORU-1, SORU-2, SORU-3 ... gibi ifadeler yalnızca HLK'nın iç çalışma mantığında kullanılan mantıksal (logical) state veya kod isimleridir.

Bu ifadeler;

* kullanıcı arayüzünde,
* Telegram ekranında,
* konuşma balonlarında,
* seslendirmede,

hiçbir şekilde gösterilemez veya seslendirilemez.

HLK ile yapılan görüşme, kullanıcı tarafından kesintisiz, doğal ve gerçek bir sohbet deneyimi olarak algılanmalıdır.

---

## MR-0005_2

### Language Display Mapping Rule

HLK içerisinde kullanılan dahili dil kodları ile kullanıcı arayüzünde gösterilen dil etiketleri ve sembolleri birbirinden bağımsız olarak yönetilir.

Dahili dil kodları sistemin operasyonel çalışması için kullanılır.

Kullanıcı arayüzünde gösterilen semboller, bayraklar ve dil etiketleri ise kullanıcı deneyimi amacıyla kullanılır.

### Kural

MR-DİL_KODLARI_001 kapsamında kullanılan:

`kr = Kürtçe`

tanımı sistem genelinde korunacaktır.

Hiçbir kullanıcı arayüzü bileşeni, "kr" dil kodunu Kore dili veya Kore bayrağı ile eşleştiremez.

Dil seçim ekranları, konuşma ekranları, Active Conversation Screen bileşenleri, log görüntüleme ekranları ve gelecekte eklenecek tüm kullanıcı arayüzlerinde;

"kr" kodu yalnızca Kürtçe dili olarak yorumlanmalıdır.

Kullanıcı arayüzünde gösterilecek sembol, bayrak veya dil etiketi sistemin dahili dil kodundan bağımsız olarak belirlenebilir.

Bu nedenle:

• kr kodu değiştirilemez.
• kr kodu Korece olarak yorumlanamaz.
• kr kodu Kore bayrağı ile gösterilemez.

HLK'nin amacı dahili sistem uyumluluğunu korurken kullanıcıya doğru dil bilgisini göstermektir.

### Beklenen Sonuç

İç sistem:

`kr = Kürtçe`

Kullanıcı arayüzü:

`☀️ Kürtçe`
veya
`☀️ KU`

olarak gösterilebilir.

Ancak hiçbir durumda:

`🇰🇷 KR`

gösterimi kullanılamaz.

---

## MR-0005_3

### HLK Servis Sağlığı ve Müdahale Motoru

### Amaç

HLK'nın reklam üretim sürecinde kullanacağı tüm servis sağlayıcıları, senaryo üretimine başlamadan önce otomatik olarak analiz etmek, servis sağlık durumlarını değerlendirmek, uygun servis sağlayıcılarını belirlemek, operasyonel riskleri önceden tespit etmek ve gerektiğinde yöneticiyi sürece dahil ederek güvenli üretim yapılmasını sağlamaktır.

### Modül Görevleri

* Tüm servis sağlayıcılarını analiz eder.
* Servis öncelik sıralamasını değerlendirir.
* Kullanılacak servis sağlayıcılarını belirler.
* Kullanılmayan servis sağlayıcılarını ve gerekçelerini kayıt altına alır.
* API durumlarını kontrol eder.
* API anahtarlarını doğrular.
* Mevcut kredi miktarlarını kontrol eder.
* Günlük ve aylık kota durumlarını kontrol eder.
* Servislerin çevrim içi / çevrim dışı durumlarını belirler.
* Servis yanıt sürelerini analiz eder.
* Tahmini üretim maliyetini hesaplar.
* Her servis için tahmini kredi tüketimini hesaplar.
* Üretim sonrası tahmini kredi bakiyesini hesaplar.
* Risk seviyesini belirler.
* Alternatif servis sağlayıcılarını değerlendirir.
* Gerekirse otomatik servis değişikliği yapar.
* Tüm kararlarını operasyon kayıtlarına işler.

### Servis Güven Skoru

HLK her servis sağlayıcısı için dinamik bir Servis Güven Skoru hesaplamalıdır.

Bu skor yalnızca API durumuna göre değil, geçmiş operasyonel performansa göre de belirlenmelidir.

Servis Güven Skoru hesaplanırken en az aşağıdaki kriterler birlikte değerlendirilmelidir.

* API erişilebilirliği
* API yanıt süresi
* Son dönem başarı oranı
* Son dönem hata oranı
* Mevcut kredi durumu
* Tahmini üretim sonrası kredi durumu
* Kota durumu
* Ortalama üretim süresi
* Servis kararlılığı
* Son başarılı işlem zamanı
* Son başarısız işlem zamanı
* Servis öncelik sırası

HLK servis seçimini yalnızca öncelik sırasına göre değil, Servis Güven Skoruna göre de yapmalıdır.

### Servis Sağlık Raporu

HLK her servis sağlayıcısı için aşağıdaki bilgileri üretmelidir.

* Servis sağlayıcı adı
* Öncelik sırası
* Kullanıldı / Kullanılmadı bilgisi
* Kullanılmama gerekçesi
* API durumu
* API hata açıklaması
* Mevcut kredi
* Bu reklam için tahmini kredi tüketimi
* Üretim sonrası tahmini kredi
* Kota durumu
* Servis sağlık durumu
* Risk seviyesi
* Servis Güven Skoru
* Alternatif servis sağlayıcıları
* HLK'nın servis seçim gerekçesi

### Yönetici Müdahalesi

HLK operasyonel risk tespit ettiğinde üretime başlamadan önce yöneticiyi bilgilendirmelidir.

Yöneticiye en az aşağıdaki seçenekler sunulmalıdır.

* Kredi Yükledim
* API Sorununu Giderdim
* Alternatif Servis Kullan
* Riski Kabul Ediyorum
* Üretimi Durdur

Yönetici işlem yaptıktan sonra HLK ilgili servis sağlayıcılarını yeniden analiz etmeli ve doğrulama başarılı olursa üretime devam etmelidir.

### Beklenen Kazanımlar

* Üretim başlamadan önce operasyonel risklerin tespit edilmesi.
* API ve kredi problemlerinin erken belirlenmesi.
* Servis seçim sürecinin tamamen şeffaf hale gelmesi.
* Tahmini kredi tüketiminin önceden görülebilmesi.
* Üretim sonrası oluşacak kredi durumunun öngörülebilmesi.
* Servis sağlayıcılarının performans geçmişine göre değerlendirilmesi.
* Yöneticiye gerçek zamanlı operasyon görünürlüğü sağlanması.
* Servis kaynaklarının verimli kullanılması.
* Reklam üretim sürecinin daha güvenilir, sürdürülebilir ve yönetilebilir hale getirilmesi.

---

## MR-0005_4

### HLK Operasyon Hafızası

### Amaç

HLK'nın gerçekleştirdiği tüm reklam üretim operasyonlarının sonuçlarını kayıt altına almak, geçmiş operasyonlardan öğrenmesini sağlamak ve gelecekteki kararlarını geçmiş veriler ışığında daha doğru verebilmesini sağlamaktır.

### Modül Görevleri

* Tamamlanan tüm operasyonları kayıt altına alır.
* Operasyon geçmişini güvenli şekilde saklar.
* Servis sağlayıcı performans geçmişini oluşturur.
* Ajan performans geçmişini oluşturur.
* Gerçek maliyetleri kayıt altına alır.
* Gerçek kredi tüketimlerini kayıt altına alır.
* Gerçek üretim sürelerini kayıt altına alır.
* Başarı ve başarısızlık oranlarını hesaplar.
* Operasyon istatistiklerini oluşturur.
* Geçmiş operasyonlardan eğilim analizi üretir.
* Servis Güven Skoru hesaplamalarına geçmiş verileri sağlar.
* Risk analizine geçmiş operasyon desteği sağlar.
* Yönetici raporlarını geçmiş operasyon verileri ile destekler.

### Operasyon Hafızasında Saklanacak Veriler

* Operasyon Kimliği
* Reklam Kimliği
* Ürün Kategorisi
* Kullanılan Servis Sağlayıcılar
* Kullanılan Ajanlar
* Servis Öncelik Sırası
* API Durumları
* Servis Güven Skorları
* Tahmini Kredi Tüketimi
* Gerçek Kredi Tüketimi
* Tahmini Üretim Maliyeti
* Gerçek Üretim Maliyeti
* Tahmini Üretim Süresi
* Gerçek Üretim Süresi
* Üretim Başarı Durumu
* Üretim Hata Nedenleri
* Kullanılan Alternatif Servisler
* Servis Değiştirme Nedenleri
* Yönetici Müdahaleleri
* Kullanıcı Revizyon Sayısı
* Operasyon Tamamlanma Durumu
* Operasyon Tarihi
* Operasyon Sonucu

### Operasyon Hafızasının Kullanım Alanları

HLK Operasyon Hafızası aşağıdaki sistemler tarafından kullanılmalıdır.

* HLK Servis Sağlığı ve Müdahale Motoru
* Servis Seçim Motoru
* Maliyet Hesaplama Motoru
* Fiyatlandırma Motoru
* Risk Analiz Sistemi
* Yönetici Bildirim Sistemi
* Operasyon Analiz Sistemi
* Raporlama Sistemi

### Öğrenme İlkesi

HLK geçmiş operasyon verilerini değiştirmez.

HLK yalnızca geçmiş operasyonlardan istatistiksel sonuçlar üretir ve gelecekteki karar süreçlerini desteklemek amacıyla kullanır.

Geçmiş operasyon kayıtları denetlenebilir, izlenebilir ve gerektiğinde raporlanabilir olmalıdır.

### Beklenen Kazanımlar

* HLK'nın operasyonel deneyim kazanması.
* Servis seçimlerinin geçmiş başarı oranlarına göre iyileştirilmesi.
* Servis Güven Skorlarının gerçek operasyon verileri ile desteklenmesi.
* Tahmini maliyet hesaplarının doğruluğunun artırılması.
* Tahmini üretim sürelerinin zamanla iyileştirilmesi.
* Operasyonel risklerin daha doğru tahmin edilmesi.
* Yönetici raporlarının geçmiş operasyonlarla desteklenmesi.
* HLK'nın sürekli öğrenen ve gelişen bir operasyon sistemi haline gelmesi.

---

## MR-0005_5

### HLK Operasyon Analiz Motoru

### Amaç

HLK Operasyon Hafızasında bulunan geçmiş operasyon verilerini analiz ederek servis seçimlerini, maliyet tahminlerini, üretim sürelerini, risk analizlerini ve karar mekanizmalarını sürekli iyileştirmek.

### Modül Görevleri

* Operasyon Hafızasını analiz eder.
* Geçmiş operasyonları karşılaştırır.
* Benzer reklam üretimlerini tespit eder.
* Servis sağlayıcı performanslarını analiz eder.
* Ajan performanslarını analiz eder.
* Gerçek maliyet analizleri yapar.
* Tahmini maliyet doğruluk oranlarını hesaplar.
* Gerçek üretim sürelerini analiz eder.
* Tahmini üretim sürelerinin doğruluk oranlarını hesaplar.
* Başarı ve başarısızlık nedenlerini sınıflandırır.
* Operasyonel eğilimleri analiz eder.
* Risk tahmin modellerini geliştirir.
* Servis Güven Skorlarının doğruluğunu iyileştirir.
* Karar motorlarını istatistiksel verilerle destekler.
* Yönetici raporları için analiz çıktıları üretir.

### Analiz Kriterleri

* Ürün kategorileri
* Reklam türleri
* Platform türleri
* Video süreleri
* Kullanılan servis sağlayıcılar
* Kullanılan ajanlar
* Gerçek maliyetler
* Tahmini maliyetler
* Gerçek üretim süreleri
* Tahmini üretim süreleri
* Başarı oranları
* Başarısızlık nedenleri
* API hata geçmişi
* Kredi tüketim eğilimleri
* Revizyon sayıları
* Yönetici müdahaleleri

### Üreteceği Analizler

* Servis başarı oranları
* Servis hata oranları
* Ortalama üretim süreleri
* Ortalama kredi tüketimleri
* Ortalama maliyetler
* Benzer reklam karşılaştırmaları
* Ürün kategorisi bazlı analizler
* Platform bazlı analizler
* Risk eğilim analizleri
* Performans eğilim analizleri
* Doğruluk oranı analizleri

### Diğer Modüllere Sağlayacağı Veriler

* Servis Seçim Motoru
* HLK Servis Sağlığı ve Müdahale Motoru
* Maliyet Hesaplama Motoru
* Fiyatlandırma Motoru
* Risk Analiz Sistemi
* Yönetici Bildirim Sistemi
* Operasyon Raporlama Sistemi

### Çalışma İlkesi

Bu modül geçmiş operasyon kayıtlarını değiştirmez.

Bu modül yalnızca geçmiş operasyonları analiz eder, istatistiksel sonuçlar üretir ve diğer modüllerin daha doğru karar vermesine yardımcı olur.

Tüm analiz sonuçları açıklanabilir, denetlenebilir ve raporlanabilir olmalıdır.

### Beklenen Kazanımlar

* HLK'nın geçmiş deneyimlerinden öğrenmesi.
* Servis seçimlerinin sürekli iyileştirilmesi.
* Maliyet tahminlerinin daha doğru hale gelmesi.
* Üretim sürelerinin daha isabetli tahmin edilmesi.
* Risk analizlerinin güçlendirilmesi.
* Operasyonel verimliliğin artırılması.
* Yönetici kararlarının güçlü analizlerle desteklenmesi.
* HLK'nın zamanla kendi operasyonlarını optimize eden öğrenen bir sisteme dönüşmesi.

---

## MR-0005_6

### Başlık

Senaryo Onay Formu Tasarım İlkeleri

### Kural

HLK, Senaryo Onay Formu oluştururken veya mevcut Senaryo Onay Formunu geliştirirken, `REFERANS_SENARYO_ONAY_FORMU.png` dosyasını resmi referans tasarım olarak kabul eder.

Bu referans tasarım;

* Sayfa yerleşimini,
* Kart sıralamasını,
* Başlık yapısını,
* Bilgi sunum mantığını,
* Buton yerleşimini,
* Görsel hiyerarşisini,
* Mobil kullanım önceliğini,
* Telegram ekran uyumluluğunu,
* Kurumsal tasarım dilini

tanımlar.

HLK, Senaryo Onay Formunda yapılacak tüm geliştirme ve revizyonlarda bu tasarım ilkelerini korumak zorundadır.

Referans tasarım yalnızca Proje Yöneticisinin açık onayı ile değiştirilebilir.

### Beklenen Sonuç

HLK yalnızca bir PNG dosyasını değil, bu PNG'nin temsil ettiği kurumsal tasarım mantığını da öğrenmiş olur.

Bundan sonra oluşturulacak tüm Senaryo Onay Formları aynı tasarım ilkelerine uygun olarak geliştirilir.

---

## MR-0005_7

### Başlık

**Modül Karar Bağımlılığı Kuralı — Module Decision Dependency Rule**

### Kural

HLK_01_asistan projesindeki tüm modüller, kullanıcının sistemi başlatan ilk tetikleyici komutundan (örneğin /start) oturum tamamen kapanıncaya kadar HLK Runtime'ın hiyerarşik kontrolü altında çalışır (MASTER-013).

Hiçbir modül;

* HLK Runtime adına karar veremez,
* kendi karar mekanizmasını oluşturamaz,
* karar niteliği taşıyan bir durumu kendi içinde karara bağlayamaz.

Karar gerektiren her durumda modül; yürütmeyi durdurur, karar talebini HLK Runtime'a iletir ve verilen kararı eksiksiz uygular (AR-002_81 Karar Talep Protokolü, OR-004_12).

Tereddüt halinde karar üretmek yasaktır; tereddüt halinde HLK Runtime'dan karar istenir.

### Kapsam

Bu kural;

* Workflow
* Production
* Research
* Agent
* Selection
* Delivery
* Quality Control
* Constitution Enforcement
* Feedback Loop
* gelecekte eklenecek tüm modüller

için geçerlidir.

Yeni eklenen her modül, bu kurala uyumu tasarım aşamasında sağlamak zorundadır (MASTER-006).

### Beklenen Sonuç

* Tüm modüller tek karar otoritesi (HLK Runtime) altında hiyerarşik olarak çalışır.
* Modül seviyesinde bağımsız karar mekanizması oluşmaz.
* Karar gerektiren durumlar Karar Talep Protokolü ile HLK Runtime'a taşınır.
* Gelecekte eklenecek modüller aynı karar hiyerarşisine otomatik olarak tabi olur.
