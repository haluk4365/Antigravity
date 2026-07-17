# 04 — Operational Rules

Operasyonel kurallar.

---

## OR-004_0

### Başlık

SAHNE-01 ve SAHNE-02 Operasyonel Kuralları

### Amaç

HLK oturumunun başlangıcında kullanıcıyı karşılamak, dil seçimini almak ve kullanıcıyı ürün linki giriş aşamasına yönlendirmek.

### Kural

Kullanıcı /start komutu verdiğinde sistem STATE_START state'ini başlatmalıdır.

STATE_START sonrasında sistem STATE_SCENE_1 state'ine geçmelidir.

STATE_SCENE_1 içerisinde SAHNE-01 karşılama videosu kullanıcıya gönderilmelidir.

SAHNE-01 süresince kullanıcıdan veri girişi beklenmemelidir.

SAHNE-01 tamamlandıktan sonra video kullanıcı ekranından kaldırılmalıdır.

Video kaldırıldıktan sonra sistem STATE_LANGUAGE_SELECTION state'ine geçmelidir.

STATE_LANGUAGE_SELECTION içerisinde desteklenen dil seçenekleri kullanıcıya gösterilmelidir.

Kullanıcı bir dil seçtiğinde EVENT_LANGUAGE_SELECTED oluşturulmalıdır.

Dil seçimi tamamlandıktan sonra sistem STATE_SCENE_2 state'ine geçmelidir.

STATE_SCENE_2 içerisinde seçilen dile uygun SAHNE-02 videosu oynatılmalıdır.

SAHNE-02 süresince kullanıcıdan ürün linki istenmemelidir.

SAHNE-02 tamamlandıktan sonra video kullanıcı ekranından kaldırılmalıdır.

SAHNE-02 sonrasında sistem STATE_WAIT_PRODUCT_LINK state'ine geçmelidir.

STATE_WAIT_PRODUCT_LINK aşamasında kullanıcıdan ürün linki istenmelidir.

Tüm geçişler State Engine'de tanımlanan event ve transition kuralları ile uyumlu olmalıdır.

### Beklenen Sonuç

- HLK başlangıç akışı standart hale gelir.
- SAHNE-01 → Dil Seçimi → SAHNE-02 → Ürün Linki akışı garanti edilir.
- Videoların gösterim ve kaldırılma davranışları tanımlanır.
- Kullanıcı yalnızca doğru aşamada veri girebilir.
- State Engine ile Operational Rules katmanı uyumlu hale gelir.

---

## OR-004_1

### Başlık

STATE_WAIT_PRODUCT_LINK ve STATE_LINK_VALIDATION Operasyonel Kuralları

### Amaç

HLK'nın analiz sürecini başlatabilmesi için kullanıcıdan geçerli ve erişilebilir bir ürün linki almasını sağlamak.

### Kural

STATE_SCENE_2 tamamlandıktan sonra sistem STATE_WAIT_PRODUCT_LINK state'ine geçmelidir.

Bu state içerisinde kullanıcıdan ürün linki istenmelidir.

Sadece analiz edilebilir ve erişilebilir ürün linkleri kabul edilmelidir.

Ürün adı, ürün açıklaması, serbest metin veya yalnızca görsel gönderimi ürün linki yerine kabul edilmemelidir.

Kullanıcı link gönderdiğinde EVENT_PRODUCT_LINK_RECEIVED oluşturulmalıdır.

Sonraki state: STATE_LINK_VALIDATION

STATE_LINK_VALIDATION aşamasında sistem link doğrulama işlemini başlatmalıdır.

Doğrulama kapsamında:

- URL format kontrolü
- Erişilebilirlik kontrolü
- Ürün sayfası kontrolü
- Temel içerik kontrolü

yapılabilir.

Link doğrulama başarılı olursa EVENT_LINK_VALIDATED oluşturulmalıdır.

Sonraki state: STATE_LINK_VALIDATED

Link doğrulama başarısız olursa EVENT_LINK_VALIDATION_FAILED oluşturulmalıdır.

Sonraki state: STATE_WAIT_PRODUCT_LINK

Her başarısız doğrulama girişimi kayıt altına alınmalıdır.

Kullanıcının toplam başarısız link deneme sayısı GC_MAX_PRODUCT_LINK_RETRY değerini aşarsa STATE_SESSION_CLOSED çalıştırılmalıdır.

`GC_MAX_PRODUCT_LINK_RETRY` varsayılan değer: `5`

Oturum bu nedenle kapatılıyorsa kullanıcıya açıklayıcı bilgilendirme mesajı gönderilmelidir.

Link başarıyla doğrulandığında sistem sonraki aşama için araştırma sürecini hazırlamalıdır.

### Beklenen Sonuç

- Geçersiz linklerle süreç ilerlemez.
- Kullanıcıya yeniden deneme hakkı verilir.
- Maksimum deneme sınırı uygulanır.
- Başarılı doğrulama sonrası araştırma akışı güvenli şekilde başlatılır.
- State Engine ile Operational Rules katmanı uyumlu hale gelir.

---

## OR-004_2

### Başlık

Format, Çözünürlük ve Video Süresi Seçim Operasyonel Kuralları

### Amaç

Kullanıcının reklam videosu için hedef formatı, çözünürlüğü ve video süresini standart şekilde seçmesini sağlamak.

### Kural

Materyal toplama aşaması tamamlandıktan sonra sistem STATE_PLATFORM_SELECTION state'ine geçmelidir.

Kullanıcıya format seçenekleri sunulmalıdır.

Örnek:

- 9:16 (TikTok / Reels / Shorts)
- 16:9 (YouTube)
- 1:1 (Instagram Feed)

Kullanıcı yalnızca bir format seçebilmelidir.

Format seçimi tamamlandığında seçim kayıt altına alınmalıdır.

Format seçimi tamamlandıktan sonra sistem STATE_VIDEO_RESOLUTION_SELECTION state'ine geçmelidir.

Kullanıcıya çözünürlük seçenekleri sunulmalıdır.

Örnek:

- 480p
- 720p
- 1080p

Sistem varsayılan olarak 720p seçeneğini önerebilir.

Kullanıcı yalnızca bir çözünürlük seçebilmelidir.

Çözünürlük seçimi kayıt altına alınmalıdır.

Çözünürlük seçimi tamamlandıktan sonra sistem STATE_VIDEO_DURATION_SELECTION state'ine geçmelidir.

Kullanıcıya video süresi seçenekleri sunulmalıdır.

Video süresi sistem tarafından tanımlanan minimum ve maksimum sınırlar arasında olmalıdır.

Geçersiz süre girişleri kabul edilmemelidir.

Video süresi seçimi kayıt altına alınmalıdır.

Tüm seçimler tamamlandığında EVENT_DURATION_SELECTED oluşturulmalıdır.

Sonraki state: STATE_AUDIO_SELECTION

Geçersiz kullanıcı cevaplarında ilgili seçim ekranı tekrar gösterilmelidir.

Timeout davranışları OR-004_9 kurallarına tabi olmalıdır.

Tüm seçimler brief verisine kaydedilmelidir.

### Beklenen Sonuç

- Format seçimi standart hale gelir.
- Çözünürlük seçimi standart hale gelir.
- Süre seçimi standart hale gelir.
- Tüm tercihler brief içerisine kaydedilir.
- EVENT_DURATION_SELECTED → STATE_AUDIO_SELECTION geçişi garanti edilir.
- State Engine ile Operational Rules katmanı uyumlu hale gelir.

---

## OR-004_3

### Başlık

Tanıtım Tarzı ve Hedef Kitle Seçim Operasyonel Kuralları

### Amaç

Kullanıcının reklam videosunun anlatım tarzını ve hedef kitlesini standart şekilde belirlemesini sağlamak.

### Kural

Video formatı, çözünürlük ve süre seçimleri tamamlandıktan sonra sistem Tanıtım Tarzı seçim aşamasını başlatmalıdır.

Kullanıcıya tanıtım tarzı seçenekleri sunulmalıdır.

V1 örnekleri:

- UGC Tarzı
- Geleneksel ile Modernin Buluşması
- Sanatsal / Sinematik
- Kendim Yazacağım
- HLK'ya Bırak

Kullanıcı yalnızca bir tanıtım tarzı seçebilmelidir.

Tanıtım tarzı seçimi kayıt altına alınmalıdır.

"Kendim Yazacağım" seçeneği seçilirse sistem kullanıcıdan serbest metin girişi istemelidir.

Kullanıcının girdiği metin brief verisine kaydedilmelidir.

"HLK'ya Bırak" seçeneği seçilirse sistem seçim kaydı oluşturmalı ve sonraki adıma geçmelidir.

Tanıtım tarzı tamamlandıktan sonra sistem Hedef Kitle seçim aşamasına geçmelidir.

Kullanıcıya hedef kitle seçenekleri sunulmalıdır.

V1 örnekleri:

- 0-12 Yaş
- 13-17 Yaş
- 18-24 Yaş
- 25-34 Yaş
- 35-44 Yaş
- 45-54 Yaş
- 55-64 Yaş
- 65+ Yaş

Kullanıcı yalnızca bir hedef kitle seçebilmelidir.

Hedef kitle seçimi kayıt altına alınmalıdır.

Geçersiz kullanıcı cevaplarında ilgili seçim ekranı tekrar gösterilmelidir.

Timeout davranışları OR-004_9 kurallarına tabi olmalıdır.

Tanıtım tarzı ve hedef kitle seçimleri brief verisine kaydedilmelidir.

Her iki seçim tamamlandığında süreç normal veri toplama akışına devam etmelidir.

### Beklenen Sonuç

- Tanıtım tarzı seçimi standart hale gelir.
- Hedef kitle seçimi standart hale gelir.
- "Kendim Yazacağım" alt akışı tanımlanmış olur.
- Tüm tercihler brief içerisine kaydedilir.
- V1 akışı ile Operational Rules katmanı uyumlu hale gelir.

---

## OR-004_4

### Başlık

Ses, Dil, Karakter ve Vurgu Seçim Operasyonel Kuralları

### Amaç

Kullanıcının reklam videosunda kullanılacak ses yapısını, konuşma dilini, ses karakterini ve vurgu tercihlerini standart şekilde toplamak.

### Kural

STATE_AUDIO_SELECTION aşamasında sistem ses yapılandırma sürecini başlatmalıdır.

Kullanıcıya aşağıdaki ana seçenekler sunulmalıdır:

- Sessiz Video
- Arka Plan Müziği
- Yapay Seslendirme

Kullanıcı "Sessiz Video" seçerse ses yapılandırma süreci tamamlanmalıdır.

Sonraki aşama: STATE_BRIEF_COMPLETED

Kullanıcı "Arka Plan Müziği" veya "Yapay Seslendirme" seçerse süreç devam etmelidir.

Sistem kullanıcıdan konuşma dilini istemelidir.

Konuşma dili seçildikten sonra sistem ses karakteri seçeneklerini göstermelidir.

Örnek:

- Kadın
- Erkek
- Çocuk
- Genç
- Kurumsal
- Premium

(uygulama tarafından desteklenen seçenekler)

Ses karakteri seçildikten sonra sistem vurgu tercihlerini istemelidir.

Örnek:

- Resmî
- Samimi
- Enerjik
- Premium
- Satış Odaklı
- Eğitici

Her seçim kayıt altına alınmalıdır.

Kullanıcı seçimleri tamamladığında ses yapılandırması tamamlanmış kabul edilmelidir.

Geçersiz cevap verilirse kullanıcı ilgili seçim ekranına geri yönlendirilmelidir.

Timeout davranışları OR-004_9 kurallarına tabi olmalıdır.

Tüm seçimler video üretim sürecinde kullanılmak üzere brief verisine kaydedilmelidir.

STATE_AUDIO_SELECTION tamamlandığında EVENT_AUDIO_OPTION_SELECTED oluşturulmalıdır.

Sonraki state: STATE_BRIEF_COMPLETED

### Beklenen Sonuç

- Ses tercihleri standart şekilde toplanır.
- Sessiz video akışı desteklenir.
- Seslendirme tercihleri yapılandırılır.
- Tüm tercihler brief içerisine kaydedilir.
- State Engine ile Operational Rules katmanı uyumlu hale gelir.

---

## OR-004_5

### Başlık

Brief Onay ve Tik Düzeltme Operasyonel Kuralları

### Amaç

Kullanıcıya oluşturulan brief'i kontrol etme, yanlış veya değiştirmek istediği alanları düzenleme ve nihai brief'i onaylama imkânı vermek.

### Kural

Tüm veri toplama aşamaları tamamlandıktan sonra sistem STATE_BRIEF_COMPLETED aşamasına geçmelidir.

Sistem kullanıcıya oluşturulan brief özetini göstermelidir.

Örnek alanlar:

- Ürün linki
- Platform
- Çözünürlük
- Süre
- Ses seçimi
- Konuşma dili
- Ses karakteri
- Vurgu tercihi
- Hedef kitle
- Tanıtım tarzı

Her bilgi satırının yanında seçili/onaylı durumu gösteren işaret (tik) bulunmalıdır.

Kullanıcı isterse herhangi bir satırın tik işaretini kaldırabilmelidir.

Tik kaldırılan alan "düzeltme bekliyor" durumuna alınmalıdır.

Sistem kullanıcıyı yalnızca ilgili seçim ekranına geri yönlendirmelidir.

Düzeltme tamamlandıktan sonra kullanıcı tekrar brief özet ekranına döndürülmelidir.

Birden fazla alan için düzeltme yapılabilmelidir.

Tüm alanlar tekrar onaylı duruma geldiğinde kullanıcıya nihai onay seçeneği sunulmalıdır.

Kullanıcı nihai onay verdiğinde EVENT_BRIEF_APPROVED oluşturulmalıdır.

Sonraki state: STATE_SCENARIO_APPROVAL

Geçersiz kullanıcı işlemleri durumunda kullanıcı mevcut brief ekranına geri yönlendirilmelidir.

Timeout davranışları OR-004_9 kurallarına tabi olmalıdır.

Brief üzerinde yapılan tüm değişiklikler kayıt altına alınmalıdır.

Nihai onaydan sonra brief verileri kilitlenmelidir.

### Beklenen Sonuç

- Kullanıcı brief'i kontrol edebilir.
- Tik kaldırma ve düzeltme mekanizması standart hale gelir.
- Hatalı seçimlerle senaryo üretimine geçilmez.
- Nihai brief güvenli şekilde oluşturulur.
- EVENT_BRIEF_APPROVED → STATE_SCENARIO_APPROVAL geçişi garanti edilir.
- State Engine ile Operational Rules katmanı uyumlu hale gelir.

---

## OR-003_1

Ürün linki başarıyla doğrulandıktan sonra HLK, ürünün daha doğru analiz edilmesini ve daha kaliteli tanıtım içerikleri üretilebilmesini sağlamak amacıyla kullanıcıya ürüne ait ek detay fotoğrafları bulunup bulunmadığını sorar.

Kullanıcı ek fotoğraf yüklemeyi tercih ederse sistem fotoğraf kabul moduna geçer ve kullanıcıdan ilk fotoğrafı yüklemesini ister.

Her başarılı fotoğraf yüklemesinden sonra sistem kullanıcıya kısa bir teşekkür mesajı verir ve bir sonraki fotoğrafı beklemeye devam eder.

Fotoğraf yükleme süreci boyunca ekranda sürekli erişilebilir bir **"Bitti"** butonu bulunur.

Kullanıcı **"Bitti"** butonuna bastığında, o ana kadar yüklenen tüm fotoğraflar kabul edilir, fotoğraf toplama süreci sonlandırılır ve sistem otomatik olarak bir sonraki iş akışına geçer.

Fotoğraf yükleme adımında kabul edilecek maksimum fotoğraf sayısı gibi değiştirilebilir sayısal değerler bu kural içerisinde tanımlanmaz ve ilgili Global Configuration (GC) parametreleri tarafından yönetilir.

---

## OR-003_2

HLK tarafından kullanıcıya yöneltilen tüm soru ve bilgilendirme mesajları konuşma balonu içerisinde gösterilir.

Konuşma metni **TEXT_ONLY_MODE** standardına göre daktilo efekti kullanılarak kelime kelime ekrana yazılır.

HLK konuşması tamamlanmadan kullanıcıya herhangi bir yönlendirme butonu veya seçim butonu gösterilmez.

HLK konuşması tamamlandıktan sonra ilgili yönlendirme butonu veya butonları kısa ve yumuşak bir geçiş ile ekranda görünür.

Telegram'ın doğal sohbet yapısı korunur. Gereksiz avatarlar, büyük animasyonlar ve dikkat dağıtıcı görsel efektler kullanılmaz.

Amaç, kullanıcının bir form doldurduğu hissini değil, profesyonel bir dijital reklam danışmanı ile doğal bir sohbet deneyimi yaşamasını sağlamaktır.

### TEXT_ONLY_MODE tanımı

Varsayılan konuşma akışı ses kullanılmadan yürütülür:

1. HLK konuşma metnini üretir (veya Scene Registry'den alır).
2. Konuşma baloncuğu oluşturulur.
3. Daktilo efekti çalışır (varsayılan hız: 0.06sn/kelime).
4. Metin tamamlanır.
5. Gerekliyse seçim butonları gösterilir.
6. Kullanıcı cevabı beklenir.

Bu modda:
- Ses üretimi yapılmaz.
- MP3 dosyası oluşturulmaz.
- Ses dalga animasyonu gösterilmez.
- Voice message gönderilmez.
- ElevenLabs veya herhangi bir TTS servisi çağrılmaz.

### VOICE_ENABLED modu (opsiyonel)

Voice sistemi, gelecekte `VOICE_ENABLED = TRUE` olarak etkinleştirilebilecek isteğe bağlı bir modüldür.

Etkinleştirildiğinde OR-003_7 kapsamında tanımlanan sesli konuşma kuralları uygulanır.

---

## OR-003_3

Kullanıcı, tamamlayıcı ürün materyalleri paylaşmayı tercih ettiğinde HLK, **Tamamlayıcı Ürün Materyalleri Toplama Modu**na geçer.

Bu modun başlangıcında HLK'nin amacı yalnızca materyal yüklenmesini istemek değildir; kullanıcının bu süreci doğru anlamasını sağlamaktır.

HLK, kendi karar mekanizması ile oluşturacağı iletişim doğrultusunda kullanıcıya;

- Sistemin kabul edebileceği materyal türleri hakkında örnekler sunmayı,
- Yüklenebilecek maksimum materyal adedinin ilgili **GC parametreleri** tarafından yönetildiğini,
- Yükleme süresinin ilgili **GC zaman parametreleri** kapsamında yönetildiğini,
- Kullanıcının dilediği anda **BİTTİ** seçeneğini kullanarak bu aşamayı sonlandırıp bir sonraki adıma geçebileceğini,
- Sisteme yüklenen her materyalin karar mekanizmasını güçlendirmek amacıyla analiz edileceğini

anlaşılır şekilde aktarmayı hedefler.

HLK, bu bilgilendirmeyi sabit metinler veya hazır cümlelerle yapmak zorunda değildir. İletişim biçimini, kullanıcının bağlamını ve ihtiyaçlarını değerlendirerek kendi karar mekanizması ile dinamik olarak oluşturur.

Bu aşamanın amacı, kullanıcıya sistem kurallarını okumak değil; süreci doğru anlamasını sağlayarak reklam üretimine katkı sağlayabilecek tamamlayıcı materyalleri bilinçli şekilde paylaşmasına imkân tanımaktır.

---

## OR-003_4

Tamamlayıcı Ürün Materyalleri Toplama Modunda kullanıcı materyal yüklemeye başladıktan sonra HLK'nin önceliği kullanıcı ile sürekli diyalog kurmak değil, karar mekanizmasını güçlendirecek bilgi toplamaktır.

Bu nedenle HLK, kullanıcı yükleme yapmaya devam ettiği sürece yükleme akışını mümkün olduğunca kesmez ve gereksiz geri bildirim üretmez.

HLK, sisteme ulaşan her materyali arka planda kendi karar mekanizması ile;

- kabul eder,
- analiz eder,
- bilgi değerini değerlendirir,
- mevcut araştırma mimarisi ile ilişkilendirir,
- reklam üretim sürecine sağlayacağı katkıyı belirler.

Bu işlemler, kullanıcının yükleme sürecini kesintiye uğratmadan yürütülür.

HLK'nin amacı her materyal sonrasında açıklama yapmak veya yeni yönlendirmeler üretmek değildir. Yalnızca karar mekanizmasını doğrudan etkileyen durumlarda kullanıcı ile etkileşime geçebilir.

Örneğin; materyalin okunamaması, materyalin bozuk olması, sistem tarafından işlenememesi, güvenlik veya teknik nedenlerle değerlendirilememesi ya da karar mekanizmasını etkileyen önemli bir durum oluşması halinde HLK, kendi karar mekanizması doğrultusunda kullanıcıyı uygun şekilde bilgilendirebilir.

Bu aşamanın temel ilkesi: **Kullanıcı yükleme yaparken HLK'nin önceliği konuşmak değil, bilgi toplamak ve analiz etmektir.**

---

## OR-003_5

HLK, kullanıcı ile yürüttüğü sohbet akışında yalnızca kullanıcının mevcut aşamada bilmesi gereken bilgileri kullanıcı arayüzüne yansıtır.

Arka planda çalışan;

- ajan seçimi,
- ajan görevlendirilmesi,
- araştırma süreçleri,
- yeniden deneme işlemleri,
- alternatif servis kullanımı,
- timeout yönetimleri,
- teknik exception'lar,
- iç sistem kararları,
- geçici operasyonel hatalar

HLK'nın iç operasyonuna aittir.

Bu olaylar kullanıcının mevcut kararını veya sohbet akışını doğrudan etkilemediği sürece kullanıcıya hata mesajı, uyarı mesajı veya durum bilgisi olarak gösterilmez.

HLK, bu tür olayları kendi operasyonel mekanizması içerisinde yönetir, gerektiğinde loglar, alternatif çözüm üretir ve mümkün olduğu sürece kullanıcı deneyimini kesintiye uğratmadan sohbet akışını sürdürür.

Temel ilke:

Kullanıcı yalnızca bulunduğu akış adımı ile ilgili bilgileri görür.

HLK'nın iç operasyonları kullanıcı deneyiminin bir parçası değildir ve kullanıcı arayüzüne yansıtılmaz.

---

## OR-003_6

Link Doğrulama Karar Mekanizması, mevcut **LINK_DOGRULANDI** ve **LINK_DOGRULANAMADI** kararlarına ek olarak üçüncü bir karar durumu içerir: **ERISIM_ENGELLI**.

Bu karar durumu mevcut iki kararı değiştirmez veya bozmaz; yalnızca, erişim engeli yaşanan satış platformlarını doğru yönetmek için araya eklenir.

### ERISIM_ENGELLI koşulları

Aşağıdaki koşullar **birlikte** oluşuyorsa HLK, LINK_DOGRULANAMADI kararı vermez; bunun yerine **ERISIM_ENGELLI** kararı verir:

- Domain mevcut,
- Link formatı geçerli,
- Ürün linki yapısı geçerli,
- Platform erişimi engelliyor,
- 403, 429 veya benzeri erişim engeli yanıtları oluşuyor,
- Ürün verilerine ulaşılamıyor.

Yani; linkin kendisi yapısal olarak geçerli olmasına rağmen, platform ürün verilerine erişimi engellediği için ürün verisi elde edilemiyorsa bu durum bir doğrulama başarısızlığı (LINK_DOGRULANAMADI) olarak değerlendirilmez.

### ERISIM_ENGELLI akışı

HLK, bu durumda kullanıcıdan aşağıdaki seçeneklerden birini ister:

1. Ürünün marka (resmi) web sitesi linki,

veya

2. Aynı ürünün başka bir satış platformundaki linki.

### Beklenen davranış

- Ürün doğrulama süreci sonlandırılmaz.
- Kullanıcıya alternatif doğrulama yolu sunulur.
- Yeni gönderilen link için Link Doğrulama Süreci yeniden başlatılır.
- Kullanıcının toplam link deneme hakkı, ANA KURALLAR'da tanımlı limitler (`GC_MAX_PRODUCT_LINK_RETRY`) çerçevesinde takip edilmeye devam eder.
- Maksimum link deneme sayısına ulaşıldığında mevcut oturum, ANA KURALLAR'da tanımlı yöntemle sonlandırılır.
- Ürün doğrulanmadan sonraki aşamalara geçilmez.

### ERISIM_ENGELLI durumunda yasaklar

Bu durumda aşağıdakiler **yasaktır**:

- Ürün araştırması başlatma,
- Ürün kategorisi belirleme,
- Ürün araştırma ajanlarını oluşturma,
- Video üretimi başlatma,
- Ürün görseli isteme,
- Ürün açıklaması isteme,
- Sonraki sahneye geçme.

---

## OR-003_7

**Başlık:** Video Sonrası Konuşma Devamlılığı Kuralı (Sesli / Sessiz)

**Kural:**

HLK içerisinde bir Conversation Scene videosu tamamlandıktan sonra kullanıcıya gösterilecek ilk konuşma balonu doğrudan ve anlık olarak oluşturulamaz.

Video tamamlandıktan sonra HLK, konuşmaya devam ediyormuş hissini korumalıdır.

Bu nedenle;

- Video sahnesi sonlandırılır.
- Gerekli sahne temizleme işlemleri tamamlanır.
- Yeni konuşma balonu oluşturulur.

### VOICE_ENABLED = TRUE (opsiyonel ses modu)

Aşağıdaki adımlar yalnızca ses sistemi aktif olduğunda (`VOICE_ENABLED = TRUE`) uygulanır:

- Aktif kullanıcı diline uygun ses üretimi başlatılır.
- Üretilen ses, HLK'nın resmi karakter sesi kuralları ile uyumlu olmalıdır.
- Konuşma metni, üretilen ses ile senkronize şekilde daktilo efekti kullanılarak oluşturulur.
- Ses tamamlandığında konuşma metni de tamamlanmış olmalıdır.
- Ses tamamlanmadan kullanıcı cevap bekleme durumuna geçirilemez.

### TEXT_ONLY_MODE = TRUE (varsayılan çalışma modu)

Varsayılan modda ses bağımlı adımlar uygulanmaz:

- Ses üretimi yapılmaz.
- TTS servisi çağrılmaz.
- MP3 dosyası oluşturulmaz.
- Voice message gönderilmez.
- Konuşma metni doğrudan daktilo efekti ile yazdırılır.

**Amaç:**

Kullanıcının;

"Video sona erdi ve HLK konuşmasına doğal şekilde devam etti."

algısını yaşamasını sağlamaktır.

**Beklenen Sonuç:**

Conversation Scene ile Active Conversation Screen arasında doğal ve kesintisiz bir geçiş standardı oluşur.

Ani ve sessiz balon oluşumları engellenmiş olur.

---

## OR-003_8

### Başlık

Video Süresi Doğrulama Kuralı

### Kural

HLK, kullanıcı tarafından girilen video süresi bilgisini doğrulamak zorundadır.

Video süresi için kullanılacak minimum ve maksimum değerler Global Configuration tarafından yönetilir.

HLK;

`GC_MIN_VIDEO_DURATION` ile `GC_MAX_VIDEO_DURATION` arasında kalan değerleri geçerli kabul eder.

Bu aralığın dışında kalan değerler geçersiz giriş olarak değerlendirilir.

Geçersiz giriş tespit edildiğinde HLK:

- Kullanıcıyı bilgilendirir.
- Geçerli süre aralığını tekrar belirtir.
- Aynı state içerisinde kalır.
- Yeni süre girişini bekler.

Video süresi doğrulanmadan bir sonraki state'e geçilemez.

HLK kullanıcıya gösterilecek uyarı metnini;

- aktif dil,
- aktif konuşma bağlamı,
- aktif kullanıcı oturumu,
- mevcut konuşma akışı,
- ANA YASA kuralları

doğrultusunda dinamik olarak oluşturur.

Hazır veya sabit uyarı metinleri kullanılmaz.

### Geçerli Değerler

```text
2   → Geçersiz
3   → Geçersiz
4   → Geçerli
10  → Geçerli
15  → Geçerli
30  → Geçerli
31  → Geçersiz
45  → Geçersiz
```

Video süresi doğrulanmadan `STATE_VIDEO_SETTINGS` tamamlanmış kabul edilemez.

---

## OR-003_9

### Başlık

Otomatik Video Süresi Belirleme Kuralı

### Kural

Kullanıcı video süresi seçim ekranında **"HLK'ya Bırak"** seçeneğini seçebilir.

Bu durumda HLK video süresini otomatik olarak belirleme yetkisine sahiptir.

HLK video süresini belirlerken aşağıdaki kriterleri değerlendirebilir:

- Ürünün yapısı
- Ürünün karmaşıklık seviyesi
- Ürünün açıklanması gereken özellik sayısı
- Reklam senaryosunun uzunluğu
- Kullanılacak sahne sayısı
- Hedef platform
- Hedef kitle
- Reklam performans potansiyeli
- Kullanılacak anlatım biçimi
- Görsel yoğunluğu
- Araştırma çıktıları
- Diğer ilgili veriler

HLK bu değerlendirmeler sonucunda;

`GC_MIN_VIDEO_DURATION` ile `GC_MAX_VIDEO_DURATION`

arasında kalan herhangi bir süreyi seçebilir.

Bu durumda kullanıcı tarafından ayrıca süre girişi beklenmez.

Seçilen süre doğrudan video üretim sürecine aktarılır.

---

## OR-004_6

### Başlık

STATE_SCENARIO_APPROVAL Operasyonel Kuralları

### Amaç

HLK tarafından oluşturulan senaryo paketinin kullanıcıya sunulması, kullanıcının ONAY veya RET kararı vermesi ve bu kararın sistem akışına yansıtılması.

### Kural

STATE_BRIEF_COMPLETED tamamlandıktan sonra sistem STATE_SCENARIO_APPROVAL state'ine geçmelidir.

HLK senaryo özetini kullanıcıya sunmalıdır.

Sunulabilecek bilgiler:

- Senaryo başlığı
- Senaryo özeti
- Planlanan video süresi
- Seçilen platform
- Seçilen format
- Temel üretim bilgileri

Kullanıcıya yalnızca aşağıdaki karar seçenekleri sunulmalıdır:

- ONAY
- RET

### ONAY akışı

Kullanıcı ONAY verirse EVENT_SCENARIO_APPROVED oluşturulmalıdır.

Sonraki state: STATE_PRICING

### RET akışı

Kullanıcı RET verirse EVENT_SCENARIO_REJECTED oluşturulmalıdır.

Sonraki state: STATE_SESSION_CLOSED

RET durumunda HLK kullanıcıya senaryonun reddedildiğini bildirmelidir.

Oturum kontrollü şekilde sonlandırılmalıdır.

### Bekleme ve timeout

STATE_SCENARIO_APPROVAL aşamasında kullanıcı cevabı beklenmelidir.

Bekleme ve timeout davranışları sistemin genel timeout kurallarına tabi olmalıdır.

### Geçersiz cevap

Geçersiz kullanıcı cevabı alınırsa kullanıcı tekrar ONAY veya RET seçeneklerine yönlendirilmelidir.

### Beklenen Sonuç

- Senaryo karar noktası standart hale gelir.
- ONAY → STATE_PRICING akışı garanti edilir.
- RET → STATE_SESSION_CLOSED akışı garanti edilir.
- State Engine ile Operational Rules katmanı uyumlu hale gelir.

---

## OR-004_7

### Başlık

STATE_PRICING Operasyonel Kuralları

### Amaç

Senaryo onaylandıktan sonra fiyat teklifinin hazırlanması, kullanıcıya sunulması, kullanıcının ONAY veya RET kararı vermesi ve bu kararın sistem akışına yansıtılması.

### Kural

STATE_SCENARIO_APPROVAL aşamasında kullanıcı ONAY verdikten sonra sistem STATE_PRICING state'ine geçmelidir.

HLK, fiyat teklifini oluşturmadan önce gerekli üretim verilerini toplamalıdır.

Toplanabilecek veriler:

- Ürün adı
- Senaryo özeti
- Video süresi
- Seçilen platform
- Seçilen çözünürlük
- Ses tercihleri
- Kullanılacak servisler
- Tahmini üretim maliyetleri

Sistem gerektiğinde yönetici onayı veya yönetici fiyat girişi bekleyebilmelidir.

Bu süreç kullanıcıya gösterilmeden arka planda yürütülebilir.

Fiyat teklifi hazır olduğunda kullanıcıya sunulmalıdır.

Sunulabilecek bilgiler:

- Teklif numarası
- Hizmet özeti
- Ücret bilgisi
- Teslim kapsamı
- Üretim özeti

Kullanıcıya yalnızca aşağıdaki karar seçenekleri sunulmalıdır:

- ONAY
- RET

### ONAY akışı

Kullanıcı ONAY verirse EVENT_PRICING_APPROVED oluşturulmalıdır.

Sonraki state: STATE_PAYMENT_VERIFICATION

### RET akışı

Kullanıcı RET verirse EVENT_PRICING_REJECTED oluşturulmalıdır.

Sonraki state: STATE_SESSION_CLOSED

RET durumunda HLK kullanıcıya teşekkür etmeli ve oturumu kontrollü şekilde kapatmalıdır.

### Bekleme ve timeout

STATE_PRICING aşamasında kullanıcı cevabı beklenmelidir.

Bekleme ve timeout davranışları sistemin genel timeout kurallarına tabi olmalıdır.

### Geçersiz cevap

Geçersiz kullanıcı cevabı alınırsa kullanıcı tekrar ONAY veya RET seçeneklerine yönlendirilmelidir.

### ONAY sonrası

Fiyat teklifi ONAYLANDIKTAN sonra sistem STATE_PAYMENT_VERIFICATION state'ine geçmelidir. Video üretimi bu aşamada başlatılmaz. Video üretimi yalnızca STATE_PAYMENT_VERIFICATION aşamasında Yönetici tarafından EVENT_PAYMENT_APPROVED oluşturulduktan sonra başlatılır.

### Beklenen Sonuç

- Ticari karar noktası standart hale gelir.
- ONAY → STATE_PAYMENT_VERIFICATION akışı garanti edilir.
- RET → STATE_SESSION_CLOSED akışı garanti edilir.
- Yönetici fiyat teklifi süreci operasyonel olarak tanımlanmış olur.
- State Engine ile Operational Rules katmanı uyumlu hale gelir.

---

## OR-004_10

### Başlık

STATE_PAYMENT_VERIFICATION Operasyonel Kuralları

### Amaç

Kullanıcının "ÖDEMEM GERÇEKLEŞTİ" bildirimi sonrasında ödemenin yönetici tarafından banka hesabı üzerinde doğrulanmasını sağlamak. Video üretiminin yalnızca ödeme doğrulandıktan sonra başlatılmasını garanti altına almak.

### Kural

STATE_PRICING aşamasında kullanıcı teklifi ONAYLADIKTAN sonra sistem STATE_PAYMENT_VERIFICATION state'ine geçmelidir.

STATE_PAYMENT_VERIFICATION aşamasına giriş, kullanıcının ödeme yapması gerektiği anlamına gelir. Bu aşamada video üretimi başlatılamaz.

Kullanıcı ödemesini gerçekleştirdikten sonra "ÖDEMEM GERÇEKLEŞTİ" butonuna basmalıdır.

Kullanıcı "ÖDEMEM GERÇEKLEŞTİ" butonuna bastığında EVENT_PAYMENT_DECLARED oluşturulmalıdır.

EVENT_PAYMENT_DECLARED oluştuğunda HLK, Yönetici Ödeme Onay Formunu hazırlamalı ve yalnızca yöneticiye göndermelidir.

Yönetici Ödeme Onay Formu aşağıdaki içeriğe sahip olmalıdır:

- Başlık: ÖDEME DOĞRULAMA
- Açıklama: Kullanıcı "ÖDEMEM GERÇEKLEŞTİ" bildirimi göndermiştir. Lütfen banka hesabınızı kontrol ediniz. Ödeme hesabınıza ulaştıysa aşağıdaki butona basınız.
- Buton: ÖDEMEYİ ONAYLA

Yönetici banka hesabını kontrol etmelidir.

### Yönetici Ödeme Onayı

Yönetici ödemenin hesaba ulaştığını doğrularsa ÖDEMEYİ ONAYLA butonuna basmalıdır.

Yönetici ÖDEMEYİ ONAYLA butonuna bastığında EVENT_PAYMENT_APPROVED oluşturulmalıdır.

Sonraki state: STATE_VIDEO_PRODUCTION

EVENT_PAYMENT_APPROVED oluştuğunda kullanıcıya aşağıdaki mesaj Telegram yazı balonu olarak gönderilmelidir:

"Ödemenizi aldık.
Video üretiminiz başlatılmıştır.
Bu süreç yaklaşık 10–15 dakika sürmektedir.
Video tamamlandığında otomatik olarak size gönderilecektir."

### Yönetici Reddi

Yönetici ödemenin hesaba ulaşmadığını tespit ederse RET seçeneğini kullanabilir.

Yönetici RET verirse STATE_SESSION_CLOSED çalıştırılmalıdır.

RET durumunda kullanıcıya uygun bilgilendirme mesajı gönderilmelidir.

### Kritik Kurallar

STATE_PAYMENT_VERIFICATION aşamasında aşağıdakiler kesinlikle yasaktır:

- Video üretimi başlatmak
- STATE_VIDEO_PRODUCTION state'ine geçmek
- Yönetici onayı olmadan üretim sürecini başlatmak
- Kullanıcıya üretimin başladığını bildirmek (ödeme doğrulanmadan)

EVENT_PAYMENT_APPROVED oluşturulmadan STATE_VIDEO_PRODUCTION başlatılamaz.

Yalnızca Yönetici tarafından onaylanan ödemeler için video üretimi başlatılır.

### Bekleme ve timeout

STATE_PAYMENT_VERIFICATION aşamasında yönetici cevabı beklenmelidir.

Bekleme ve timeout davranışları sistemin genel timeout kurallarına (OR-004_9) tabi olmalıdır.

STATE_PAYMENT_VERIFICATION aşaması timeout kuralları kapsamındadır.

### Beklenen Sonuç

- Ödeme doğrulama akışı standart hale gelir.
- Kullanıcı "ÖDEMEM GERÇEKLEŞTİ" → Yönetici onayı → Video üretimi zinciri garanti edilir.
- Yönetici onayı olmadan video üretimi başlatılamaz.
- Gerçek ticari iş akışına uygun ödeme doğrulama süreci operasyonel olarak tanımlanmış olur.
- State Engine, Flow Diagram ve Operational Rules katmanı uyumlu hale gelir.

---

## OR-004_8

### Başlık

STATE_VIDEO_PRODUCTION Operasyonel Kuralları

### Amaç

Kullanıcı tarafından onaylanan brief ve fiyat teklifine göre reklam videosunun güvenli, izlenebilir ve standart şekilde üretilmesini sağlamak.

### Kural

STATE_PAYMENT_VERIFICATION aşamasında yönetici EVENT_PAYMENT_APPROVED oluşturduktan sonra sistem STATE_VIDEO_PRODUCTION state'ine geçmelidir.

Video üretimi yalnızca ödeme doğrulandıktan sonra başlatılır.

Video üretimi başlamadan önce aşağıdaki bilgiler kilitlenmelidir:

- Ürün linki
- Toplanan materyaller
- Platform seçimi
- Çözünürlük seçimi
- Video süresi
- Ses tercihleri
- Senaryo bilgileri
- Fiyat onay bilgisi

Video üretim süreci yalnızca onaylanmış veriler ile yürütülmelidir.

Sistem gerekli ajanları ve üretim modüllerini devreye almalıdır.

Video üretimi sırasında üretim durumu kayıt altına alınmalıdır.

Kritik üretim hataları oluşursa sistem hata kaydı oluşturmalıdır.

Kritik hata durumlarında yeniden deneme, manuel müdahale veya oturum sonlandırma kararları sistem politikalarına göre yürütülmelidir.

Video üretimi başarıyla tamamlanırsa EVENT_VIDEO_PRODUCTION_COMPLETED oluşturulmalıdır.

Sonraki state: STATE_SESSION_COMPLETED

STATE_SESSION_COMPLETED aşamasında kullanıcıya üretim sonucunun teslim edilmesi sağlanmalıdır.

Üretilen video kullanıcıya gönderilmeden önce dosya bütünlüğü ve erişilebilirlik kontrolünden geçirilebilir.

V1 kuralına uygun olarak üretilen videonun bir kopyası proje arşivinde saklanmalıdır.

Arşivleme işlemi üretim sonucunu etkilememelidir.

Video teslimi tamamlandıktan sonra sistem oturum kapanış sürecine hazırlanmalıdır.

### Beklenen Sonuç

- Video üretimi standart hale gelir.
- Üretim öncesi veriler sabitlenir.
- Üretim süreci izlenebilir olur.
- Başarılı üretim sonrası teslim garantilenir.
- Arşivleme davranışı operasyonel kurallara bağlanır.
- State Engine ile Operational Rules katmanı uyumlu hale gelir.

---

## OR-004_9

### Başlık

STATE_SESSION_TIMEOUT ve STATE_SESSION_CLOSED Operasyonel Kuralları

### Amaç

Kullanıcının cevap vermemesi, zaman aşımı oluşması veya oturumun herhangi bir nedenle sonlandırılması durumunda sistemin standart davranışını tanımlamak.

### Kural

Kullanıcının cevap hakkı bulunan tüm state'lerde timeout mekanizması çalışmalıdır.

Örnek:

- STATE_LANGUAGE_SELECTION
- STATE_WAIT_PRODUCT_LINK
- STATE_COLLECT_PRODUCT_MATERIALS
- STATE_PLATFORM_SELECTION
- STATE_VIDEO_RESOLUTION_SELECTION
- STATE_VIDEO_DURATION_SELECTION
- STATE_AUDIO_SELECTION
- STATE_SCENARIO_APPROVAL
- STATE_PRICING
- STATE_PAYMENT_VERIFICATION

Kullanıcı cevap hakkı bulunan bir state'e girildiğinde ilgili bekleme süresi başlatılmalıdır.

Bekleme süresi dolmadan önce sistem kullanıcıya hatırlatma mesajı gönderebilir.

Bekleme süresi dolduğunda EVENT_TIMEOUT_REACHED oluşturulmalıdır.

Sonraki state: STATE_SESSION_TIMEOUT

STATE_SESSION_TIMEOUT state'inde kullanıcıya zaman aşımı bildirimi gönderilmelidir.

STATE_SESSION_TIMEOUT sonrasında sistem STATE_SESSION_CLOSED state'ine geçmelidir.

STATE_SESSION_CLOSED state'inde:

- Aktif görevler sonlandırılmalıdır.
- Bekleyen işlemler kapatılmalıdır.
- Geçici veriler temizlenmelidir.
- Oturum durumu kayıt altına alınmalıdır.

Aşağıdaki durumlarda doğrudan STATE_SESSION_CLOSED çalıştırılabilir:

- EVENT_SCENARIO_REJECTED
- EVENT_PRICING_REJECTED
- Sistem sonlandırma kararı
- Kritik hata senaryoları

STATE_SESSION_CLOSED aşamasında kullanıcıya uygun kapanış mesajı gönderilmelidir.

Oturum kapatıldıktan sonra kullanıcı yeni işlem başlatmak isterse süreç yeniden /start komutu ile başlamalıdır.

Oturum sonlandırma sırasında oluşturulan çıktıların ve log kayıtlarının saklanması sistem politikalarına uygun şekilde yürütülmelidir.

### Beklenen Sonuç

- Timeout davranışları standart hale gelir.
- Session Closed davranışları standart hale gelir.
- Tüm state'lerde ortak oturum sonlandırma mantığı oluşur.
- State Engine ile Operational Rules katmanı uyumlu hale gelir.

---

## OR-004_11

### Başlık

**Flow Diagram Zorunlu Konuşma Akışı Kuralı**

### Kural

HLK, kullanıcıya her mesaj üretmeden önce aşağıdaki işlemleri sırasıyla yapmak zorundadır.

1. Aktif **State** belirlenir.
2. `08_HLK_FLOW_DIAGRAM.md` içerisinde bu State'e karşılık gelen resmi akış bulunur.
3. Kullanıcıya gönderilecek mesaj yalnızca ilgili sahnede tanımlanan işlem kapsamında oluşturulur.
4. `08_HLK_FLOW_DIAGRAM.md` içerisinde tanımlanmayan hiçbir soru, yönlendirme veya konuşma üretilemez.
5. İlgili **Event** gerçekleşmeden bir sonraki sahneye geçilemez.
6. Her kullanıcı cevabından sonra aynı işlem yeniden uygulanır.

### Temel İlke

`08_HLK_FLOW_DIAGRAM.md`, HLK'nın resmi konuşma akış referansıdır.

HLK, Telegram konuşmalarını bu akışa göre yürütmek zorundadır.

Flow Diagram ile üretilen konuşma arasında çelişki oluşursa;

* Flow Diagram esas alınır.
* Konuşma davranışı düzeltilir.
* Gerekirse kod güncellenir.
* Flow Diagram ihlal edilemez.

---

## OR-004_12

### Başlık

**Üretim Sırasında Karar Talebi Operasyon Kuralı — Runtime Decision Request Operational Rule**

### Amaç

MASTER-013 ve AR-002_81'de tanımlanan HLK Runtime karar otoritesinin, üretim sırasındaki operasyonel uygulanışını tanımlamak.

### Kural

Kullanıcının sistemi başlatan ilk tetikleyici komutu (örneğin /start) verildiği andan oturum tamamen kapanıncaya kadar, karar gerektiren bütün durumlarda karar yalnızca HLK Runtime tarafından üretilir.

Yürütme katmanları (Production Executor, production_pipeline.py, provider entegrasyonları ve diğer tüm uygulayıcı bileşenler) karar gerektiren bir durumla karşılaştığında aşağıdaki operasyon sırasını eksiksiz uygular:

1. Yürütme durdurulur.
2. Karar talebi, ham teknik kanıtlarla birlikte HLK Runtime'a iletilir (AR-002_81 Karar Talep Protokolü).
3. HLK Runtime kararını verir ve gerekçesiyle kaydeder (15_KARAR_GEREKCESI_STANDARDI.md).
4. Yürütme, verilen karara göre eksiksiz devam eder.

Tereddüt halinde karar üretmek yasaktır. Tereddüt halinde HLK Runtime'dan karar istenir.

### Kullanıcı Bilgilendirme Sınırı

Kullanıcıya gönderilecek ve süreç kararı içeren hiçbir mesaj ("üretim başladı", "üretim tamamlandı" ve benzerleri) yürütme katmanı tarafından üretilemez.

Bu mesajların içeriği yalnızca HLK Runtime kararı ile belirlenir (GK-001_5, OR-004_11, AR-002_81 DELIVERY / USER_NOTIFICATION kategorileri).

Yürütme katmanı, HLK Runtime tarafından onaylanan mesajı değiştirmeden iletir.

### Kayıt Zorunluluğu

Her karar talebi ve her Runtime kararı;

* PID ile ilişkilendirilir (AR-002_57),
* Decision History'ye kaydedilir (15_KARAR_GEREKCESI_STANDARDI.md),
* Event sistemi üzerinden izlenebilir hale getirilir (AR-002_73, 22_EXECUTION_EVENT_COLLECTOR.md).

### Beklenen Sonuç

* Üretim sırasında hiçbir yürütme katmanı karar üretmez.
* Karar gerektiren durumlar durdur → talep et → karar → devam et akışıyla çözülür.
* Kullanıcıya giden süreç mesajları yalnızca HLK Runtime kararıyla üretilir.
* Tüm kararlar gerekçeleriyle birlikte izlenebilir olur.
* Bu kural; Workflow, Production, Research, Agent, Selection, Delivery, Quality Control, Constitution Enforcement, Feedback Loop ve gelecekte eklenecek tüm modüller için geçerlidir (MASTER-013 Kapsam).
