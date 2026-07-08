# 03 — Architecture Rules

Mimari kurallar.

---

## AR-002_1

HLK hiçbir göreve doğrudan başlamaz. Öncelikle görevin amacını ve başarı kriterlerini analiz eder, görevi en yüksek doğrulukla tamamlayacak araştırma stratejisini ve yol haritasını oluşturur, ardından icra sürecini başlatır.

---

## AR-002_2

HLK, kendisine verilen bir görevi yerine getirirken belirli bir teknolojiye, belirli bir ajana, belirli bir modele veya belirli bir servise bağımlı bir mimari oluşturmaz. Görevin başarıyla tamamlanmasını sağlayacak yöntemleri dinamik olarak değerlendirir ve seçer.

---

## AR-002_3

HLK, kullanıcı tarafından brief sürecinde sağlanan tüm verileri ve görevin bağlamını karar mekanizmasının merkezi olarak kabul eder. Görevi yerine getirebilecek aday ajanları ve yöntemleri bu merkeze göre değerlendirir; teknoloji yeterliliği, doğruluk oranı, çalışma hızı, maliyet ve gerekli gördüğü diğer objektif kriterleri analiz ederek dinamik bir öncelik sıralaması oluşturur.

---

## AR-002_4

HLK, her yeni görevde öncelikle daha önce gerçekleştirdiği benzer görevleri değerlendirir. Eğer aynı veya yüksek derecede benzer ürün kategorisi için güncelliğini koruyan ve yeniden kullanılabilir bir ajan öncelik sıralaması mevcutsa, bu sıralamayı doğrudan veya optimize ederek kullanır. Gereksiz yeniden değerlendirme yaparak zaman ve maliyet kaybına neden olmaz. Ancak mevcut koşulların değiştiğini tespit ederse dinamik sıralamayı yeniden oluşturur.

---

## AR-002_5

HLK, bir görevin başarıyla tamamlanmasının ardından kullanılan ajan öncelik sıralamasını, uygulama sonucunu ve elde edilen performansı değerlendirir. Başarılı olduğu tespit edilen karar mimarilerini, ileride benzer görevlerde yeniden kullanılabilecek kurumsal deneyim olarak hafızasına kaydeder.

---

## AR-002_6

HLK, oluşturduğu dinamik ajan öncelik sıralamasını uygulamaya başlamadan önce, sıralamanın görevin başarı amacına hizmet edip etmediğini kendi karar mekanizması ile doğrular. Gerekli görmesi halinde uygulamaya geçmeden önce sıralamayı yeniden optimize edebilir.

---

## AR-002_7

HLK, aynı göreve ait aday ajanları eş zamanlı olarak çalıştırmaz. Dinamik öncelik sıralamasına göre yalnızca en yüksek öncelikli aday aktif olarak görevlendirilir; diğer adaylar bekleme durumunda tutulur. Aktif aday, sistem tarafından tanımlanan maksimum çalışma süresi içerisinde görevi başarıyla tamamlayamaz, timeout'a uğrar veya güvenilir sonuç üretemezse görevi sonlandırılır ve sıradaki aday otomatik olarak devreye alınır. Bu maksimum çalışma süresi Global Configuration (GC) parametreleri ile yönetilir. Bu kural yalnızca aynı görev için geçerlidir; farklı görevler sistem kaynakları elverdiği sürece eş zamanlı olarak yürütülebilir.

---

## AR-002_8

HLK, bir görevin yürütülmesi sırasında herhangi bir ajanı yalnızca başarısız olduğu için değil, görevin kalan kısmını tamamlamak açısından artık en uygun seçenek olmadığı tespit edildiğinde de değiştirebilir. Karar mekanizması, görevin toplam başarısını esas alır; aktif ajanın değiştirilmesi görevin başarısını artıracaksa, dinamik öncelik sıralaması yeniden değerlendirilerek yeni aday devreye alınabilir.

---

## AR-002_9

HLK, dinamik ajan öncelik sıralamasını oluştururken yalnızca nihai sıralamayı değil, bu sıralamanın oluşmasına neden olan değerlendirme gerekçelerini de karar mekanizmasının bir parçası olarak saklar. Böylece benzer görevlerde yalnızca geçmiş sıralamayı değil, o sıralamanın neden oluşturulduğunu da yeniden değerlendirerek daha doğru ve tutarlı kararlar üretebilir.

---

## AR-002_10

HLK, dinamik ajan orkestrasyonunda her görevi bağımsız bir karar alanı olarak ele alır. Bir görev için oluşturulan ajan öncelik sıralaması veya çalışma stratejisi, başka bir göreve otomatik olarak uygulanmaz. Ancak benzerlik analizi sonucunda yeniden kullanılmasına karar verilirse, bu kullanım HLK'nın bilinçli ve dinamik kararı ile gerçekleşir.

---

## AR-002_11

HLK, bir görevin yürütülmesi sırasında oluşan yeni bilgiler veya ara sonuçlar nedeniyle görevin başlangıcındaki karar merkezinin değiştiğini tespit ederse, mevcut ajan öncelik sıralamasını değiştirip değiştirmemeyi yeniden değerlendirir. Karar merkezi değişmediği sürece mevcut orkestrasyon korunur; değiştiği durumda ise dinamik olarak yeni bir orkestrasyon oluşturabilir.

---

## AR-002_12

HLK, dinamik ajan orkestrasyonunda hiçbir ajanı mutlak otorite olarak kabul etmez. Nihai karar, tek bir ajanın önerisine değil, HLK'nın kendi karar mekanizmasının tüm objektif değerlendirmelerine dayanır. Ajanlar karar verici değil, HLK'nın karar mekanizmasını besleyen uzman bileşenlerdir.

---

## AR-002_13 — Arka Plan Araştırması ve Ürün Referans Paketi

HLK, ürün linki doğrulandıktan sonra kullanıcıdan yeni bir talimat beklemeden reklam üretim sürecinde ihtiyaç duyacağı arka plan araştırmalarını otomatik olarak başlatır.

Araştırma süreci başlamadan önce HLK, kendi karar mekanizmasını kullanarak bir Ürün Referans Paketi oluşturmaya çalışır.

Bu referans paketi mümkün olan durumlarda aşağıdaki bilgileri içerir:

* ürün adı,
* marka adı,
* ürün kategorisi,
* referans ürün görseli,
* ürün hakkında elde edilebilen temel bilgiler.

Kullanıcı tarafından gönderilen link bir satış platformuna ait ise HLK, mümkün olan durumlarda ürünün marka bilgisini tespit etmeye çalışır.

Marka bilgisi tespit edildiğinde HLK, ürünün resmi marka web sitesini bulmaya çalışır.

Ürünün resmi marka sitesindeki ürün sayfasına erişilebildiği durumlarda HLK;

* ürünün resmi adını,
* ürünün resmi görsellerini,
* ürün hakkında resmi kaynaklarda bulunan bilgileri

öncelikli referans olarak değerlendirir.

Resmi marka sitesinden elde edilen ürün görseli, mümkün olan durumlarda Ürün Referans Paketindeki ana referans görsel olarak kullanılır.

Resmi marka kaynağına erişilemediği durumlarda HLK, elindeki en güvenilir kaynakları kullanarak araştırmaya devam eder.

HLK tarafından görevlendirilen tüm araştırma ajanları araştırmalarını bu Ürün Referans Paketi doğrultusunda yürütür.

Araştırma ajanlarının amacı yalnızca görsel toplamak değildir.

Araştırma ajanları;

* ürünün farklı açılarını,
* ürünün farklı detaylarını,
* ürünün kullanım biçimlerini,
* ürünün teknik veya görsel özelliklerini,
* ürünü daha doğru tanımaya yardımcı olacak tamamlayıcı bilgileri

aramaya yönlendirilir.

Bu aşamada HLK yeni bir araştırma stratejisi oluşturmaz; görevin başlangıcında kendi karar mekanizması ile oluşturduğu araştırma mimarisini ve ajan orkestrasyonunu devreye alır.

Arka plan araştırmaları, kullanıcı ile yürütülen brief toplama sürecini durdurmaz ve mümkün olan en yüksek verimlilikle eş zamanlı olarak devam eder.

Araştırma sırasında kullanılacak platformlar önceden sabitlenmez.

HLK;

* resmi marka sitelerini,
* resmi ürün sayfalarını,
* yetkili satıcıları,
* katalogları,
* teknik dokümanları,
* e-ticaret platformlarını,
* görsel arama sistemlerini,
* video platformlarını,
* sosyal medya kaynaklarını

ürün kategorisine, veri kalitesine ve erişilebilirliğe göre dinamik olarak değerlendirebilir.

HLK araştırmalarında platform odaklı değil, bilgi odaklı çalışır.

Araştırma sırasında elde edilen görseller yalnızca dosya bazında değil, bilgi değeri bazında değerlendirilir.

HLK, elde edilen görselleri Ürün Referans Paketindeki referans ürün bilgileri ile ilişkilendirerek değerlendirebilir.

Aynı veya yüksek derecede benzer içerikler, tekrar eden görseller ve ürünü tanımaya katkı sağlamayan içerikler karar mekanizması kapsamında ayırt edilmeye çalışılır.

Araştırma sonucunda elde edilen ve karar mekanizmasına yeni bilgi kazandıran görseller korunur ve sonraki analiz süreçlerinde kullanılabilir.

HLK'nin amacı belirli sayıda görsel toplamak değil, ürünü mümkün olan en yüksek doğrulukla tanımaktır.

---

## AR-002_14

HLK'ye kullanıcı ile kuracağı iletişim için hazır cümleler, hazır soru kalıpları veya sabit konuşma metinleri tanımlanmaz.

Sistem tasarlanırken HLK'ye yalnızca;

- Hangi bilginin elde edilmesi gerektiği,
- Bu bilginin neden gerekli olduğu,
- Bu bilginin iş akışının hangi aşamasında talep edilmesi gerektiği,
- Bu bilginin elde edilmesiyle ulaşılmak istenen amaç ve başarı kriterleri

tanımlanır.

HLK, sahip olduğu karar mekanizmasını kullanarak kullanıcı ile kuracağı iletişim biçimini, kullanacağı ifadeleri, soru yapısını, açıklama seviyesini ve yönlendirme şeklini dinamik olarak oluşturur.

Sistemin temel yaklaşımı, HLK'ye cümle yazdırmak değil; amaç, bağlam ve hedef tanımlamaktır. İletişimin nasıl kurulacağına HLK kendi karar mekanizması doğrultusunda karar verir.

---


## AR-002_15

HLK içerisinde yer alan "Tamamlayıcı Ürün Materyalleri Toplama Aşaması", kullanıcıdan mümkün olduğunca fazla dosya toplamak amacıyla değil, reklam üretim sürecinde kullanılacak karar mekanizmasını güçlendirecek bilgi değerini artırmak amacıyla tasarlanmıştır.

Bu aşamanın temel amacı;

- Ürünü mümkün olan en yüksek doğrulukla tanımak,
- İnternette bulunamayabilecek özgün bilgileri elde etmek,
- Reklam üretimine katkı sağlayacak tamamlayıcı bilgi değerini artırmak,
- Ürünün ayırt edici özelliklerini daha doğru analiz etmek,
- Senaryo ve reklam stratejisinin doğruluğunu yükseltmektir.

Bu aşamanın başarı kriteri sisteme yüklenen dosya sayısı değildir. Başarı; karar mekanizmasına kazandırılan yeni bilgi, bilgi çeşitliliği ve reklam üretimine sağlayacağı katkı ile ölçülür.

HLK'nin hedefi dosya toplamak değil, karar mekanizmasını güçlendirecek tamamlayıcı bilgi elde etmektir.

Kullanıcı, paylaşacağı materyallerin reklam üretim kalitesini artıracağını anlamalı ve paylaşım kararını özgür iradesi ile verebilmelidir.

Ürün linki doğrulanır doğrulanmaz HLK, kendi oluşturduğu araştırma mimarisini devreye alır ve arka plan araştırmalarını başlatır. Tamamlayıcı Ürün Materyalleri Toplama Aşaması bu araştırma süreci ile entegre şekilde çalışır.

HLK, kullanıcı tarafından sisteme yüklenen materyalleri yalnızca dosya bazında değil, bilgi değeri bazında değerlendirir. Bu kapsamda HLK; aynı materyalin tekrar yüklenmesini, yüksek derecede benzer bilgi taşıyan materyalleri ve karar mekanizmasına yeni katkı sağlamayan içerikleri tespit eder ve bunları yeni bilgi olarak değerlendirmez.

Bu aşamada kabul edilebilecek maksimum materyal sayısı ve ilgili tüm sayısal limitler Global Configuration (GC) parametreleri tarafından yönetilir.

Kullanıcı "VAR" seçeneğini seçtiği anda HLK, Tamamlayıcı Ürün Materyalleri Toplama Moduna geçer. Bu modun başlangıcında HLK'nin amacı yalnızca materyal yüklenmesini istemek değildir; kullanıcının bu süreci doğru anlamasını sağlamayı hedefler.

HLK, kendi karar mekanizması ile oluşturacağı iletişim doğrultusunda; sistem tarafından kabul edilebilecek materyal türleri hakkında örnekler sunabilir, maksimum materyal adedinin ve yükleme süresinin GC parametreleri tarafından yönetildiğini, kullanıcının dilediği anda BİTTİ seçeneğini kullanarak bu aşamayı sonlandırıp bir sonraki adıma geçebileceğini ve sisteme yüklenen her materyalin analiz edilerek karar mekanizmasına dahil edileceğini kullanıcının anlayabileceği şekilde aktarır.

HLK kullanıcıya hazır cümleler okumaz. HLK'nin amacı, kullanıcının süreci doğru anlamasını ve reklam üretimine katkı sağlayabilecek materyalleri bilinçli şekilde paylaşabilmesini sağlamaktır.

Kullanıcının "Ne istiyorsun?", "Ne gönderebilirim?", "Neler yükleyebilirim?" veya "Tam olarak ne lazım?" gibi soruları yalnızca kelime anlamı ile değerlendirilmez. HLK bu soruların altında yatan bilgi ihtiyacını analiz eder ve kullanıcıya paylaşabileceği materyaller konusunda yönlendirici örnekler sunar.

Bu örnekler sınırlayıcı değildir. Tamamlayıcı ürün görselleri, farklı açılardan çekilmiş fotoğraflar, yakın plan detaylar, kullanım görüntüleri, ürün videoları, kataloglar, broşürler, teknik dokümanlar, kullanım kılavuzları, paketleme görselleri, marka veya etikete ait detaylar ve ürünü daha doğru tanımaya yardımcı olabilecek diğer materyaller bu kapsamda değerlendirilebilir.

HLK'nin temel ilkesi; dosya odaklı değil bilgi odaklı çalışmak, kullanıcıyı dosya yüklemeye zorlamak değil, karar mekanizmasını güçlendirecek yüksek bilgi değerine sahip tamamlayıcı materyalleri sisteme kazandırmaktır.

---

## AR-002_16

HLK, bir görev için oluşturduğu ve başarıyla kullanılmış ajan timlerini yeniden kullanılabilir bilgi olarak değerlendirir.

Yeni bir görev oluştuğunda HLK öncelikle aynı ürün kategorisi için daha önce oluşturulmuş uygun bir ajan timi bulunup bulunmadığını kontrol eder.

Bulunan timin yaşı sistemde tanımlı geçerlilik süresinin altında ise HLK yeni aday araştırması başlatmaz.

Mevcut tim doğrudan yeniden kullanılır.

Ancak aynı kategori içerisinde daha önce bu tim ile yürütülen görevlerde kullanıcı tarafından yoğun revizyon talep edilmişse, sonuçlar sürekli yetersiz bulunmuşsa veya kullanıcı memnuniyetsizliği oluşmuşsa HLK mevcut timi yeniden kullanmaz.

Bu durumda HLK yeni bir aday araştırma, puanlama ve sıralama süreci başlatır.

Bu mekanizmanın amacı gereksiz token tüketimini, gereksiz maliyet oluşumunu ve gereksiz karar üretimini önlemektir.

HLK, mümkün olan her durumda daha önce başarıyla kullanılmış ve geçerlilik süresi devam eden ajan timlerini yeniden kullanmayı tercih eder.

---

## AR-002_17

### Çoklu Kaynak Araştırma Zorunluluğu

HLK, ürün linki doğrulandıktan sonra ürün araştırmasını yalnızca doğrulanan ürün sayfası ile sınırlandırmaz.

HLK, kendi karar mekanizmasını kullanarak ürün hakkında daha fazla ve daha kaliteli bilgi sağlayabilecek ek kaynakları araştırabilir.

Bu kaynaklar örneğin;

* resmi marka sitesi,
* marka katalogları,
* yetkili satıcılar,
* alternatif satış platformları,
* görsel arama kaynakları,
* video kaynakları,
* sosyal medya kaynakları,
* teknik dokümanlar

olabilir.

HLK'nin amacı mümkün olduğunca çok platform gezmek değil, reklam üretim kalitesini artıracak bilgi çeşitliliğini elde etmektir.

Bu nedenle araştırma kapsamı ürün kategorisine, veri kalitesine ve bilgi ihtiyacına göre dinamik olarak belirlenir.

HLK araştırma sırasında platform odaklı değil, bilgi odaklı çalışır.

Bir ürün hakkında yeterli bilgiye ulaşılabildiği durumda araştırma kapsamını genişletmek zorunlu değildir. Ancak mevcut bilgi reklam üretimi için yetersiz görülüyorsa HLK, ek kaynakları araştırarak karar mekanizmasını güçlendirebilir.

HLK'nin amacı mümkün olan en fazla platformu taramak değil, reklam üretiminde kullanılabilecek en yüksek bilgi değerine ulaşmaktır.

---

## AR-002_18

### Araştırma Sonuçlarının Korunması İlkesi

HLK tarafından yürütülen ürün araştırmalarında bulunan görseller yalnızca araştırma sürecinde geçici olarak kullanılmaz.

HLK, araştırma sırasında elde ettiği her görseli bilgi değeri açısından değerlendirir.

Karar mekanizmasına yeni bilgi kazandıran, ürünü farklı açıdan tanıtan, farklı detaylar gösteren veya reklam üretim sürecine katkı sağlayabilecek görseller araştırma sonucu olarak korunur.

HLK, aynı veya yüksek derecede benzer bilgi taşıyan görselleri tekrar olarak değerlendirebilir.

Ancak bilgi değeri taşıyan görseller yalnızca örnekleme amacıyla sınırlandırılamaz veya araştırma tamamlandıktan sonra kaybedilemez.

HLK, araştırma sırasında elde ettiği görselleri yalnızca sayısal hedefleri karşılamak amacıyla elemez.

Araştırma sonucunda bulunan görseller içerisinden bilgi değeri taşıyan ve tekrar etmeyen tüm görseller, karar mekanizmasının ilerleyen aşamalarında kullanılabilmek üzere korunabilir.

GC_IMAGE_MIN_COUNT ve GC_IMAGE_MAX_COUNT parametreleri saklanacak görsel sayısını değil, araştırmanın sonlandırılmasına ilişkin operasyonel eşikleri tanımlar.

Bu nedenle GC_IMAGE_MAX_COUNT değerine ulaşılması, bilgi değeri taşıyan görsellerin araştırma sonucundan çıkarılması veya kaybedilmesi anlamına gelmez.

HLK'nin amacı belirli sayıda görsel toplamak değil, ürünü mümkün olan en yüksek doğrulukla tanımaktır.

Araştırma sonucunda elde edilen ve bilgi değeri taşıyan görseller;

* ürün analizi,
* marka analizi,
* hedef müşteri analizi,
* reklam stratejisi oluşturma,
* senaryo üretimi,
* sahne planlama,
* video üretimi

gibi sonraki süreçlerde kullanılabilecek şekilde korunabilir.

---

## AR-002_19

### Ajan Sürekliliği ve Operasyonel Eskalasyon İlkesi

HLK, görevlendirilen bir ajanın görevi tamamlayamadığını tespit ettiğinde görevi doğrudan başarısız olarak sonlandırmaz.

Öncelikle başarısızlık nedenini analiz eder ve kayıt altına alır.

Örneğin;

* API_KEY_MISSING
* NO_CREDITS
* TIMEOUT
* SERVICE_UNAVAILABLE
* ACCESS_DENIED
* INTERNAL_ERROR

gibi nedenler karar mekanizmasının bir parçası olarak değerlendirilir.

Başarısızlık nedeninin yalnızca ilgili ajana özgü olduğu tespit edilirse HLK, aynı görevi yerine getirebilecek adaylar arasından bir sonraki uygun adayı dinamik ajan öncelik sıralamasına göre otomatik olarak devreye alır.

HLK'nin temel ilkesi, mümkün olduğu sürece üretimi durdurmamak ve görevi tamamlamaya devam etmektir.

Bir ajanın çalışamaması, tek başına görevin başarısız olduğu anlamına gelmez.

HLK, görev tamamlanıncaya kadar uygun alternatif adayları değerlendirmeye devam edebilir.

Eğer görev için uygun alternatif aday bulunamazsa veya tüm adaylar başarısız olursa HLK, başarısızlık nedenlerini ve etkilenen görevi görünür şekilde operasyonel rapora dahil eder.

Başarısızlık nedeni API_KEY_MISSING, NO_CREDITS veya sistem yöneticisinin müdahalesini gerektiren benzer operasyonel problemlerden kaynaklanıyorsa HLK, bu durumu yüksek öncelikli operasyonel bildirim olarak işaretler.

Bu bildirim;

* etkilenen görevi,
* başarısız olan ajanı,
* başarısızlık nedenini,
* göreve etkisini,
* önerilen aksiyonu

içerir.

HLK'nin amacı yalnızca başarısızlığı kaydetmek değil, görevin tamamlanmasını sağlamak; bu mümkün değilse problemi yöneticinin hızlı şekilde çözebileceği açıklıkta raporlamaktır.

---

## AR-002_20

### Ürün Bilgi Açığı Analizi İlkesi

HLK, ürün araştırmasını yalnızca bilgi toplama süreci olarak değerlendirmez.

Araştırma başladıktan sonra HLK, Ürün Referans Paketini kullanarak ürün hakkında hangi bilgilerin elde edildiğini ve hangi bilgilerin henüz eksik olduğunu analiz eder.

HLK bu değerlendirmeyi ürün kategorisine ve araştırmanın mevcut durumuna göre dinamik olarak gerçekleştirir.

Örneğin;

* ön görünüm,
* arka görünüm,
* yan görünüm,
* yakın plan detaylar,
* malzeme veya kumaş dokusu,
* etiket veya marka detayları,
* kullanım görüntüleri,
* paketleme detayları,
* teknik detaylar

gibi bilgi alanları değerlendirilebilir.

Bu örnekler sınırlayıcı değildir.

HLK, ürün kategorisine, araştırma sırasında elde edilen verilere ve karar mekanizmasının ihtiyaçlarına göre değerlendireceği bilgi alanlarını dinamik olarak belirleyebilir.

Gerekli gördüğü durumlarda yeni bilgi alanları oluşturabilir, bazı bilgi alanlarını birleştirebilir veya ilgili olmayan bilgi alanlarını değerlendirme dışı bırakabilir.

HLK'nin amacı önceden tanımlanmış bir kontrol listesini tamamlamak değil, ürünü mümkün olan en yüksek doğrulukla tanıyabilmek için ihtiyaç duyulan bilgi çeşitliliğini elde etmektir.

HLK'nin amacı aynı bilgiye sahip çok sayıda görsel toplamak değildir.

HLK, mümkün olduğu ölçüde eksik bilgi alanlarını tespit etmeye ve araştırma ajanlarını bu eksik bilgi alanlarını tamamlayacak şekilde yönlendirmeye çalışır.

Araştırma sırasında elde edilen yeni bilgiler, mevcut bilgi açığını kapatıp kapatmadığı açısından değerlendirilir.

Bu nedenle araştırma başarısı yalnızca bulunan görsel sayısı ile değil, ürün hakkında elde edilen bilgi çeşitliliği ve bilgi bütünlüğü ile değerlendirilir.

HLK'nin amacı belirli sayıda görsel toplamak değil, ürünü mümkün olan en yüksek doğrulukla tanımaktır.

---

## AR-002_21

### Ajan Değiştirme ve Yeniden Seçim Mimarisi

HLK içerisinde bir ajanın AGENT_REPLACED durumuna geçmesi, yerine gelecek yeni ajanın rastgele seçileceği anlamına gelmez.

Bir ajan değiştirildiğinde HLK öncelikle mevcut görev için oluşturulmuş dinamik ajan öncelik sıralamasını değerlendirir.

Karar merkezi değişmemişse ve mevcut sıralama hâlâ geçerliyse, sıradaki uygun aday devreye alınır.

Ancak görev sırasında elde edilen yeni bilgiler, operasyonel durumlar veya performans sonuçları nedeniyle karar merkezi değişmişse HLK mevcut sıralamayı yeniden değerlendirebilir ve yeni bir dinamik öncelik sıralaması oluşturabilir.

AGENT_PLACEHOLDER, AGENT_DISABLED, AGENT_NO_CREDITS, AGENT_API_KEY_MISSING, AGENT_SERVICE_UNAVAILABLE veya operasyonel olarak kullanılamaz durumda bulunan ajanlar yeniden seçim havuzuna dahil edilmez.

HLK'nin amacı boşalan görevi mümkün olan en hızlı şekilde doldurmak değil, görevin başarı ihtimalini en yüksek seviyede tutacak yeni ajanı seçmektir.

Bu nedenle ajan değiştirme süreci yalnızca sıra mantığı ile değil, HLK'nin güncel karar mekanizması ile yönetilir.

---

## AR-002_22

### Constitutional Feedback / Control Loop Architecture
### Anayasal Geri Bildirim / Kontrol Döngüsü Mimarisi

---

### 1. Amaç

HLK içerisinde hiçbir karar tek seferlik ve nihai değildir.

Her karar, uygulandıktan sonra sistem tarafından değerlendirilmelidir.

Bu değerlendirme, kararın anayasal geçerliliğini hâlâ koruyup korumadığını tespit etmek amacıyla yapılır.

Feedback Loop'un amacı;

* Mevcut kararın anayasal geçerliliğini korumak,
* Değişen koşullara sistemin uyum sağlamasını garanti etmek,
* Hatalı kararların zincirleme hata üretmesini engellemek,
* Kaynak israfını önlemek (gereksiz API çağrısı, kredi tüketimi),
* Decision Engine'in güncel sistem durumuna göre yeni karar üretmesini sağlamak,
* HLK'nın kendi kendini düzelten (self-correcting) bir sistem olarak çalışmasını mümkün kılmaktır.

Feedback Loop, HLK'nın **anayasal öz denetim mekanizmasıdır.**

---

### 2. Anayasal Dayanak

Feedback Loop aşağıdaki anayasal katmanlara dayanır:

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — Feedback Loop üst katmanların emirlerini uygular |
| **MASTER** | MASTER-004 | Tek karar verici HLK'dır — Feedback Loop karar vermez, sadece denetler |
| **MASTER** | MASTER-006 | Modüler genişleme — yeni tetikleyiciler Feedback Loop'a eklenebilir |
| **AR** | AR-002_3 | Dinamik öncelik sıralaması — yeniden değerlendirmede güncel sıralama kullanılır |
| **AR** | AR-002_7 | Ajan görevlendirme — timeout/başarısızlıkta sıradaki adaya geçiş |
| **AR** | AR-002_11 | Karar merkezi değişimi — yeni bilgi karar bağlamını değiştirirse yeniden orkestrasyon |
| **AR** | AR-002_19 | Ajan sürekliliği ve eskalasyon — başarısızlık nedeni analizi ve alternatife geçiş |
| **AR** | AR-002_21 | Ajan değiştirme ve yeniden seçim — değişen koşullarda yeni aday seçimi |
| **OR** | OR-004_1 | Link doğrulama — maksimum deneme aşımında oturum kapatma |
| **OR** | OR-004_9 | Timeout ve oturum kapatma — EVENT_TIMEOUT_REACHED sonrası akış |
| **SE** | SE-007_4 | State geçiş kuralları — Feedback Loop sonrası geçerli state geçişleri |
| **SE** | SE-007_5 | Event tetikleme — Feedback Loop hangi Event ile Decision Engine'i çağıracağını bilir |
| **FEAT** | FEAT-002 | Decision Engine — Feedback Loop'un yeniden çağırdığı tek karar verici |
| **FEAT** | FEAT-010 | Quality Control — Feedback Loop kalite kontrol zincirinin bir parçasıdır |
| **FEAT** | FEAT-015 | Live Activity Center — Feedback Loop döngüleri LAC üzerinden izlenebilir |

---

### 3. Feedback Loop'un Görevi

**Feedback Loop karar vermez. Feedback Loop karar üretmez. Feedback Loop Executor değildir.**

Feedback Loop yalnızca aşağıdaki soruyu cevaplar:

> **"Decision Engine'in ürettiği mevcut karar, şu anki sistem koşullarında hâlâ geçerli ve uygulanabilir mi?"**

Bu sorunun cevabı "Hayır" ise Feedback Loop, Decision Engine'i yeniden çalıştırarak güncel koşullara uygun yeni bir karar üretilmesini sağlar.

Bu sorunun cevabı "Evet" ise Feedback Loop tetiklenmez; mevcut karar geçerliliğini korur.

Feedback Loop'un yetkileri:

| Yapabilir | Yapamaz |
|---|---|
| ✅ ExecutionResult'ı değerlendirmek | ❌ Yeni karar üretmek |
| ✅ Anayasal ihlali tespit etmek | ❌ İhlali düzeltmek (düzeltme Decision Engine'indir) |
| ✅ Decision Engine'i yeniden çağırmak | ❌ Decision Engine'in yerine geçmek |
| ✅ Yeniden değerlendirme sayısını takip etmek | ❌ Sonsuz döngüye girmek |
| ✅ Eskalasyon başlatmak | ❌ Eskalasyon kararını kendisi vermek |
| ✅ Log kaydı oluşturmak | ❌ Anayasayı değiştirmek |

---

### 4. Feedback Loop Tetikleyicileri

Aşağıdaki olaylar Feedback Loop'u tetikler.

Her tetikleyici, Decision Engine'in mevcut kararının geçerliliğini sorgulamasını gerektiren anlamlı bir değişikliği temsil eder.

#### 4.1 Executor Kaynaklı Tetikleyiciler

| Tetikleyici | Kaynak | Açıklama |
|---|---|---|
| `EXECUTOR_SUCCESS` | Executor | Görev başarıyla tamamlandı. Sonraki state için yeni karar gerekli. |
| `EXECUTOR_FAILED` | Executor | Görev başarısız oldu. Neden analizi ve fallback executor seçimi gerekli. |
| `EXECUTOR_TIMEOUT` | Executor | Görev zaman aşımına uğradı. AR-002_7 uyarınca sıradaki adaya geçiş. |
| `EXECUTOR_PARTIAL` | Executor | Görev kısmen tamamlandı. Eksik kalan kısım için ek karar gerekli. |

#### 4.2 Ajan Kaynaklı Tetikleyiciler

| Tetikleyici | Kaynak | Açıklama |
|---|---|---|
| `AGENT_REPLACED` | Selection Architecture | Aktif ajan değiştirildi. AR-002_21 uyarınca yeni öncelik sıralaması değerlendirilmeli. |
| `AGENT_DISABLED` | Selection Architecture | Ajan devre dışı bırakıldı. Görev için alternatif aday seçimi zorunlu. |
| `AGENT_NO_CREDITS` | Operasyon Veri Merkezi | Ajanın kredisi tükendi. AR-002_19 uyarınca operasyonel eskalasyon. |
| `AGENT_API_KEY_MISSING` | Operasyon Veri Merkezi | API anahtarı eksik veya geçersiz. |
| `AGENT_SERVICE_UNAVAILABLE` | Operasyon Veri Merkezi | Servis çevrim dışı. AR-002_19 uyarınca alternatife geçiş. |

#### 4.3 Anayasal Tetikleyiciler

| Tetikleyici | Kaynak | Açıklama |
|---|---|---|
| `CONSTITUTIONAL_VIOLATION` | Constitutional Validator | DecisionPacket anayasal doğrulamadan geçemedi. Düzeltici karar zorunlu. |
| `VALIDATION_BLOCK` | Constitutional Validator | Validator BLOCK verdi. Mevcut karar uygulanamaz. |
| `VALIDATION_RETRY` | Constitutional Validator | Validator RETRY verdi. Geçici hata — aynı karar yeniden değerlendirilmeli. |

#### 4.4 Sistem ve Çevre Tetikleyicileri

| Tetikleyici | Kaynak | Açıklama |
|---|---|---|
| `NEW_INFORMATION` | Research Orchestrator | Araştırma sonucunda karar bağlamını değiştirecek yeni bilgi elde edildi. AR-002_11 uyarınca karar merkezi yeniden değerlendirilmeli. |
| `SERVICE_UNAVAILABLE` | Operasyon Veri Merkezi | Harici servis kullanılamaz durumda. AR-002_19 uyarınca alternatif servis seçimi. |
| `RESOURCE_DEPLETED` | Operasyon Veri Merkezi | API kotası, kredi veya kaynak tükendi. Eskalasyon gerekli. |
| `USER_CANCELLED` | Session Manager | Kullanıcı işlemi iptal etti. OR-004_9 uyarınca STATE_SESSION_CLOSED. |
| `GC_LIMIT_EXCEEDED` | State Engine | GC parametre sınırı aşıldı (örn: GC_MAX_PRODUCT_LINK_RETRY). İlgili OR kuralı uygulanır. |
| `TIMEOUT_REACHED` | Session Timeout | Kullanıcı cevap vermedi. OR-004_9 uyarınca STATE_SESSION_TIMEOUT. |
| `SCENE_LOCK_VIOLATION` | Scene Lock | SAHNE-1 tekrar oynatma girişimi engellendi. AR-002_44 uyarınca mevcut oturum korunur. |
| `FEATURE_STATUS_CHANGED` | Feature Registry | Bir Feature'ın durumu değişti (AKTİF → KULLANIM_DIŞI). Bağımlı workflow'lar etkilenir. |

#### 4.5 Feedback Loop'u Tetiklemeyen Olaylar

Aşağıdaki olaylar anlamlı bir değişiklik oluşturmadığı için Feedback Loop'u tetiklemez:

* Aynı bilgiyi tekrar eden araştırma sonuçları
* Karar bağlamını etkilemeyen log kayıtları
* Başarılı operasyonel durum sorgulamaları (API sağlık kontrolü OK ise)
* Kullanıcının karar dışı mesajları (sohbet amaçlı yazışmalar)
* Sistemin iç durum güncellemeleri (cache yenileme, indeks güncelleme)

---

### 5. Feedback Loop Karar Süreci

#### 5.1 Anayasal Akış

Aşağıdaki akış, Feedback Loop'un sistem içerisindeki tam çalışma sürecini gösterir.

Her adım, ilgili anayasal bileşen tarafından yürütülür.

```
ADIM 1: EXECUTOR TAMAMLANDI
═══════════════════════════════════════════════════════════════

Executor, DecisionPacket'i uygular.
ExecutionResult üretir:
  • status: SUCCESS / FAILED / TIMEOUT / PARTIAL
  • output: Görev çıktısı (state değişimi, hata kodu, vb.)
  • duration_ms: Görev süresi
  • error_detail: Hata detayı (FAILED/TIMEOUT ise)

ExecutionResult → Feedback Loop'a iletilir.
Executor'un görevi burada SONA ERER.
Executor karar vermez, sonraki adımı BELİRLEMEZ.


ADIM 2: FEEDBACK LOOP DEĞERLENDİRMESİ
═══════════════════════════════════════════════════════════════

Feedback Loop, ExecutionResult'ı alır.

DEĞERLENDİRME:
  • ExecutionResult.status == SUCCESS?
    ├─ EVET → Sonraki state için yeni Event oluştur.
    │         Feedback Loop SONLANIR.
    │         (Bu bir yeniden değerlendirme DEĞİLDİR —
    │          başarılı tamamlanan görevden sonraki
    │          normal ileri akıştır.)
    │
    └─ HAYIR → Başarısızlık nedeni analiz edilir.

BAŞARISIZLIK NEDENİ ANALİZİ:
  • Geçici hata mı? (TIMEOUT, SERVICE_UNAVAILABLE)
    → RETRY: Decision Engine aynı bağlamla yeniden çağrılır.
  • Kalıcı hata mı? (AGENT_DISABLED, CREDIT_EXHAUSTED)
    → RE-EVALUATE: Decision Engine yeni bağlamla çağrılır.
  • Anayasal ihlal mi? (CONSTITUTIONAL_VIOLATION)
    → CORRECT: Decision Engine düzeltici karar için çağrılır.
  • Kritik kaynak sorunu mu? (API_OFFLINE, QUOTA_EXCEEDED)
    → ESCALATE: Operasyonel eskalasyon başlatılır.
  • Kullanıcı iptali mi? (USER_CANCELLED)
    → CLOSE: STATE_SESSION_CLOSED akışı başlatılır.

YENİDEN DEĞERLENDİRME NEDENİ BELİRLENİR:
  Feedback Loop, Decision Engine'e NE YAPMASI gerektiğini SÖYLEMEZ.
  Feedback Loop, Decision Engine'e yalnızca NEDEN yeniden
  değerlendirme gerektiğini BİLDİRİR:

  • EXECUTION_FAILED       → Executor görevi tamamlayamadı
  • EXECUTION_TIMEOUT      → Executor zaman aşımına uğradı
  • CONSTITUTIONAL_BLOCK   → Constitutional Validator kararı bloke etti
  • RESOURCE_UNAVAILABLE   → API/kredi/kota yetersiz
  • STATE_MISMATCH         → State geçişi anayasal değil
  • NEW_INFORMATION_RECEIVED → Karar bağlamını değiştiren yeni bilgi
  • USER_CANCELLED         → Kullanıcı işlemi iptal etti
  • GC_LIMIT_EXCEEDED      → Global Configuration sınırı aşıldı

  Bu nedenler KARAR DEĞİLDİR. Bu nedenler ÖNERİ DEĞİLDİR.
  Bu nedenler yalnızca "mevcut karar neden geçersiz" sorusunun cevabıdır.


ADIM 3: DECISION ENGINE YENİDEN ÇAĞRILIR
═══════════════════════════════════════════════════════════════

Feedback Loop, Decision Engine'e ReEvaluationContext iletir.
Bu bağlam KARAR İÇERMEZ. Bu bağlam ÖNERİ İÇERMEZ.
Bu bağlam yalnızca "mevcut karar neden yeniden değerlendirilmeli"
sorusunun cevabını taşır:

  • original_decision_id  : Yeniden değerlendirilmesi gereken kararın ID'si
  • trigger_event         : Feedback Loop'u tetikleyen olay
  • re_evaluation_reason  : Yeniden değerlendirme NEDENİ
                            (yukarıdaki listeden — eylem değil, durum)
  • current_state         : Sistemin şu anki state'i
  • re_evaluation_count   : Kaçıncı yeniden değerlendirme (1-3)
  • failure_detail        : (varsa) Başarısızlık açıklaması
  • failed_executor       : (varsa) Hangi executor başarısız oldu

  AŞAĞIDAKİ ALANLAR TANIMLANMAMIŞTIR (MASTER-004 gereği):
  • suggested_action  — Feedback Loop eylem ÖNEREMEZ
  • suggested_fallback — Feedback Loop executor SEÇEMEZ (AR-002_49)

Decision Engine:
  1. ReEvaluationContext'i OKUR (bağlam — karar veya öneri değil).
  2. Rule Cache'ten güncel kuralları okur.
  3. State Engine'den mevcut state'i doğrular.
  4. Selection Architecture ile en uygun executor'u KENDİ SEÇER.
  5. Yeni bir DecisionPacket ÜRETİR (Feedback Loop'tan bağımsız).
  6. Yeni DecisionPacket'i Feedback Loop'a DEĞİL,
     doğrudan Constitutional Validator'a iletir.

Feedback Loop'un Decision Engine üzerinde KARAR VERME yetkisi YOKTUR.
Feedback Loop karar ÖNERMEZ; yalnızca yeniden değerlendirme
BAĞLAMINI iletir.
Nihai karar her zaman Decision Engine'indir (MASTER-004).


ADIM 4: CONSTITUTIONAL VALIDATOR
═══════════════════════════════════════════════════════════════

Yeni DecisionPacket, Constitutional Validator'e girer.

Validator:
  1. Rule Validation
  2. Authority Validation
  3. Integrity Validation
  4. Constitutional Compliance (MASTER/GC/GK/AR/OR/QR/MR)
  5. State Validation
  6. Feature Validation
  7. Workflow Validation
  8. Resource Validation
  9. Security Validation
  10. Final Verdict (PASS / WARNING / BLOCK / RETRY / ESCALATE)

Sonuçlar:
  • PASS / WARNING → ADIM 5'e geç (Executor)
  • BLOCK / RETRY  → ADIM 2'ye DÖN (yeniden Feedback Loop)
                      re_evaluation_count ARTAR
  • ESCALATE       → ADIM 6'ya geç (Eskalasyon)


ADIM 5: EXECUTOR (YENİ KARAR)
═══════════════════════════════════════════════════════════════

Yeni DecisionPacket, Executor'a iletilir.
Executor, yeni kararı uygular.
ExecutionResult üretilir.
→ ADIM 1'e DÖN (döngü kapanır)


ADIM 6: ESKALASYON (GEREKİRSE)
═══════════════════════════════════════════════════════════════

Eskalasyon koşulları:
  • re_evaluation_count >= 3 (maksimum yeniden değerlendirme aşıldı)
  • CREDIT_CRITICAL (kredi tükendi, yönetici müdahalesi şart)
  • API_OFFLINE + NO_FALLBACK (tüm alternatifler tükendi)
  • CRITICAL SECURITY VIOLATION (güvenlik ihlali)

Eskalasyon aksiyonu:
  • Yönetici bildirimi gönderilir
  • Oturum askıya alınır
  • PID varsa Production Package'a eskalasyon kaydı eklenir
  • Manuel müdahale beklenir
  • Feedback Loop DURUR (manuel müdahale sonrası /start ile yeniden)
```

#### 5.2 Süreç Özeti

```
ExecutionResult
    │
    ▼
Feedback Loop (değerlendirir, KARAR VERMEZ)
    │
    ├─ SUCCESS → yeni Event → normal akış devam
    │
    └─ BAŞARISIZ → neden analizi
        │
        ├─ RETRY → Decision Engine (aynı bağlam)
        ├─ RE-EVALUATE → Decision Engine (güncel bağlam)
        ├─ CORRECT → Decision Engine (düzeltici)
        ├─ ESCALATE → Yönetici
        └─ CLOSE → STATE_SESSION_CLOSED
            │
            ▼
        Decision Engine → DecisionPacket
            │
            ▼
        Constitutional Validator
            │
            ├─ PASS/WARNING → Executor → ExecutionResult → (döngü)
            └─ BLOCK/RETRY → Feedback Loop (yeniden, sayaç +1)
```

---

### 6. Yeniden Değerlendirme Kuralları

#### 6.1 Gereksiz Yeniden Değerlendirme Yapılmaz

Feedback Loop, yalnızca kararın geçerliliğini etkileyebilecek anlamlı değişikliklerde tetiklenir.

Aşağıdaki durumlar tek başına yeniden değerlendirme nedeni değildir:

* Aynı Executor'dan gelen ardışık başarılı sonuçlar (normal akıştır)
* Log seviyesinde değişiklikler
* Rule Cache'in değişmeden yeniden yüklenmesi (hash aynı)
* Kullanıcının konuşma akışını etkilemeyen mesajları

#### 6.2 Aynı Karar Sonsuz Döngüye Girmez

Her DecisionPacket, `re_evaluation_count` alanı ile kaçıncı yeniden değerlendirme olduğunu taşır.

```
re_evaluation_count = 0 → İlk karar (normal akış)
re_evaluation_count = 1 → İlk yeniden değerlendirme
re_evaluation_count = 2 → İkinci yeniden değerlendirme
re_evaluation_count = 3 → Son yeniden değerlendirme
re_evaluation_count > 3 → ESKALASYON (artık otomatik düzeltme denenmez)
```

#### 6.3 Maksimum Yeniden Değerlendirme Sayısı

Maksimum yeniden değerlendirme sayısı **3 (üç)** olarak tanımlanmıştır.

Bu değer Global Configuration parametresi olarak yönetilir:

```
GC_MAX_RE_EVALUATION_COUNT = 3
```

3 başarısız yeniden değerlendirme sonrasında:

* Feedback Loop durur.
* Operasyonel eskalasyon başlatılır.
* Yöneticiye bildirim gönderilir.
* Oturum askıya alınır.
* Karar zinciri Decision Log Center'da tam olarak izlenebilir.

#### 6.4 Anlamsız Değişiklikler Tetikleyici Değildir

Bir olayın Feedback Loop'u tetikleyebilmesi için, mevcut kararın **sonucunu değiştirme potansiyeline** sahip olması gerekir.

Örnek:

| Olay | Tetikler mi? | Gerekçe |
|---|---|---|
| Ajan timeout → sıradaki aday mevcut | ✅ EVET | Fallback executor kararı değiştirir |
| Ajan timeout → sıradaki aday YOK | ✅ EVET (eskalasyon) | Kaynak tükendi, müdahale gerekli |
| API health check: OK | ❌ HAYIR | Mevcut durumda değişiklik yok |
| Kullanıcı "teşekkür ederim" yazar | ❌ HAYIR | Karar bağlamını etkilemez |
| Yeni araştırma sonucu: aynı ürün kategorisi | ❌ HAYIR | Bilgi açığı kapanmadı, bağlam aynı |
| Yeni araştırma sonucu: farklı ürün kategorisi | ✅ EVET | Karar merkezi değişti (AR-002_11) |

#### 6.5 Kararın Geçerliliğini Etkilemeyen Olaylar

Feedback Loop yalnızca **kararın uygulanabilirliğini** etkileyen olaylarla ilgilenir.

Sistemin iç işleyişine ait aşağıdaki olaylar Feedback Loop kapsamı dışındadır:

* Cache güncellemeleri
* Log rotasyonu
* İstatistik toplama
* Arka plan temizlik görevleri
* Periyodik sağlık kontrolleri (sonuç OK ise)

---

### 7. Anayasal Güvenlik

#### 7.1 Feedback Loop İkinci Bir Karar Merkezi Değildir

Bu madde, MASTER-004'ün doğrudan uzantısıdır.

MASTER-004:
> "HLK projesinde karar veren, yöneten ve nihai kararı oluşturan tek yapı HLK'dır."

Feedback Loop bu ilkeyi asla ihlal edemez.

**Feedback Loop hiçbir zaman:**

| Yasak | Anayasal Dayanak |
|---|---|
| ❌ Yeni politika üretemez | MASTER-004 — Karar yetkisi yalnızca HLK'ya aittir |
| ❌ ANA YASA'yı değiştiremez | MASTER-001 — ANA YASA yalnızca Proje Yöneticisi tarafından değiştirilir |
| ❌ Executor'un yerine karar veremez | MASTER-004 — Executor uygulayıcıdır, Feedback Loop denetleyicidir |
| ❌ Decision Engine'i atlayarak doğrudan Executor çağıramaz | AR-002_36 — Tüm sahneler Decision Engine onayından geçer |
| ❌ Constitutional Validator'ü bypass edemez | MASTER-003 — Her karar anayasal denetime girer |
| ❌ Rule Cache'i güncelleyemez | Rule Cache salt okunurdur, yalnızca Constitution Compiler yazar |

#### 7.2 Nihai Karar Yetkisi

Feedback Loop, Decision Engine'e **öneride bulunamaz.**

Feedback Loop yalnızca **ReEvaluationContext** iletir — bu bağlam; ne oldu, neden oldu, neredeyiz, kaçıncı deneme sorularını cevaplar. "Ne yapılması gerektiği" sorusunun cevabını İÇERMEZ.

```
Feedback Loop → ReEvaluationContext:
  "DE-20260702-0042 numaralı karar EXECUTOR_TIMEOUT nedeniyle
   başarısız oldu. VoiceGenerator 120sn timeout verdi.
   Mevcut state STATE_SCENE_2. Bu 1. yeniden değerlendirme."

  ↑ BU BİR BAĞLAM PAKETİDİR. KARAR İÇERMEZ. ÖNERİ İÇERMEZ. ↑

Decision Engine → Yeni DecisionPacket:
  "Bağlamı okudum. Rule Cache'ten kuralları kontrol ettim.
   Selection Architecture ile OpenAI TTS'i seçtim.
   Yeni karar: DE-20260702-0043, executor: OpenAI TTS."

  ↑ BU BİR KARARDIR. TAMAMEN DECISION ENGINE TARAFINDAN ÜRETİLMİŞTİR. ↑

SONUÇ: Decision Engine'in kararı GEÇERLİDİR.
        Feedback Loop'un ilettiği bağlam, kararın GEREKÇESİDİR.
        Feedback Loop KARAR VERMEMİŞTİR, ÖNERİDE BULUNMAMIŞTIR.
```

Bu mekanizma, MASTER-004'ün "hiçbir katman HLK'dan bağımsız karar veremez" ilkesinin Feedback Loop özelinde uygulanmasıdır. Feedback Loop karar sürecine KATILMAZ; yalnızca kararın geçerliliğini yitirdiği durumlarda Decision Engine'i yeniden BAŞLATIR.

---

### 8. Diğer Bileşenlerle İlişkisi

#### 8.1 Haberleşme Tablosu

| Bileşen | Yön | Veri | Açıklama |
|---|---|---|---|
| **Decision Engine** | → ÇAĞIRIR | `FeedbackTrigger` iletir | Yeniden karar üretilmesini talep eder. Decision Engine'in kararını GEÇERSİZ KILAMAZ. |
| **Constitutional Validator** | ← OKUR | `ValidationReport` alır | BLOCK/RETRY verdiğinde Feedback Loop tetiklenir. |
| **Rule Cache** | ← OKUR | `CompiledRule` sorgular | Yeniden değerlendirme kurallarını (GC_MAX_RE_EVALUATION_COUNT) okur. |
| **Event Log Center** | → KAYDEDER | Her Feedback Loop döngüsü | Kaçıncı döngü, hangi tetikleyici, sonuç ne oldu — tam izlenebilirlik. |
| **State Engine** | ← OKUR | Mevcut state'i okur | Decision Engine'e güncel state bağlamını iletmek için. |
| **Selection Architecture** | Doğrudan çağırmaz | — | Selection, Decision Engine tarafından kullanılır. Feedback Loop yalnızca sonucu denetler. |
| **Executor** | ← GİRDİ alır | `ExecutionResult` alır | Feedback Loop'un tetikleyici kaynağıdır. |
| **Decision Log Center** | → KAYDEDER | `FeedbackLoopLog` | Her döngünün tam kaydı: orijinal karar, tetikleyici, yeni karar, sayaç. |
| **Operasyon Veri Merkezi** | ← OKUR | API/kredi/kota durumu | Kaynak tetikleyicilerinin doğrulanması için. |

#### 8.2 Feedback Loop ile Decision Engine Arasındaki Veri Akışı

```
Feedback Loop → Decision Engine:

{
  "original_decision_id": "DE-20260702-0042",
  "trigger_event": "EXECUTOR_TIMEOUT",
  "re_evaluation_reason": "EXECUTION_TIMEOUT",
  "current_state": "STATE_SCENE_2",
  "re_evaluation_count": 1,
  "failure_detail": "ElevenLabs API timeout after 120s",
  "failed_executor": "VoiceGenerator"
}

↑ BU BİR BAĞLAM PAKETİDİR. KARAR İÇERMEZ. ÖNERİ İÇERMEZ. ↑
  Feedback Loop ne yapılacağını SÖYLEMEZ.
  Feedback Loop hangi executor'un kullanılacağını SEÇMEZ.
  Feedback Loop yalnızca mevcut kararın neden geçersiz
  olduğunu AÇIKLAR.

Decision Engine → (Feedback Loop'a DEĞİL, Constitutional Validator'a):

Yeni DecisionPacket {
  decision_id: "DE-20260702-0043",
  re_evaluation_of: "DE-20260702-0042",
  re_evaluation_count: 1,
  executor: "OpenAI TTS",            ← Decision Engine'in Selection
                                        Architecture ile KENDİ seçimi.
                                        Feedback Loop'tan GELMEDİ.
  ...
}
```

---

### 9. ASCII Diyagram

Aşağıdaki diyagram, HLK'nın Constitutional Feedback / Control Loop mimarisini bütün olarak gösterir.

```
═══════════════════════════════════════════════════════════════════════════
          HLK CONSTITUTIONAL FEEDBACK / CONTROL LOOP MİMARİSİ
                         (AR-002_22)
═══════════════════════════════════════════════════════════════════════════

                         ┌─────────────────────┐
                         │   ANA YASA (.md)    │
                         │ MASTER GC GK AR OR  │
                         │ QR MR SE WF FEAT    │
                         └──────────┬──────────┘
                                    │ Sistem açılışında (1 kez)
                                    ▼
                         ┌─────────────────────┐
                         │ CONSTITUTION        │
                         │ COMPILER            │
                         │ (6 aşamalı pipeline)│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ RULE CACHE          │
                         │ (Immutable,         │
                         │  Read-Only)         │
                         └──────────┬──────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ STATE ENGINE  │         │ DECISION ENGINE │         │ SELECTION       │
│ (FEAT-003)    │◀───────▶│ (FEAT-002)      │────────▶│ ARCHITECTURE    │
│               │  state   │                 │ executor│ (AR-002_49)     │
│ • current     │          │ TEK KARAR VERİCİ│ seçimi  │                 │
│ • transitions │          └────────┬────────┘         └─────────────────┘
└───────────────┘                   │
                                    │ DecisionPacket (immutable)
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                        CONSTITUTIONAL VALIDATOR                       │
│                                                                       │
│  10 aşamalı anayasal doğrulama:                                       │
│  Rule → Authority → Integrity → Constitutional → State → Feature     │
│  → Workflow → Resource → Security → Final Verdict                     │
│                                                                       │
│  Verdict: PASS / WARNING / BLOCK / RETRY / ESCALATE                   │
└──────┬──────────────────┬──────────────────┬──────────────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
    PASS/WARNING       BLOCK/RETRY        ESCALATE
       │                  │                  │
       ▼                  │                  ▼
┌───────────────┐         │         ┌─────────────────┐
│ EXECUTOR      │         │         │ OPERASYONEL     │
│               │         │         │ ESKALASYON      │
│ DecisionPacket│         │         │                 │
│ uygulanır     │         │         │ • Yönetici      │
│               │         │         │   bildirimi     │
│ KARAR VERMEZ  │         │         │ • Oturum askıda │
└───────┬───────┘         │         │ • Manuel müdahale│
        │                 │         └─────────────────┘
        ▼                 │
 ExecutionResult          │
 (SUCCESS/FAILED/         │
  TIMEOUT)                │
        │                 │
        ▼                 │
┌───────────────────────────────────────────────────────────────────────┐
│                         FEEDBACK LOOP                                  │
│                         (bu modül)                                     │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │ DEĞERLENDİRME                                               │     │
│  │                                                             │     │
│  │ ExecutionResult.status?                                     │     │
│  │                                                             │     │
│  │ SUCCESS ──▶ Yeni Event ──▶ NORMAL AKIŞ DEVAM               │     │
│  │                                                             │     │
│  │ FAILED ──▶ Neden analizi:                                  │     │
│  │   • Geçici hata → RETRY (re_evaluation_count +1)            │     │
│  │   • Kalıcı hata → RE-EVALUATE (yeni bağlam)                 │     │
│  │   • Anayasal ihlal → CORRECT (düzeltici karar)              │     │
│  │   • Kaynak sorunu → ESCALATE                                │     │
│  │   • Kullanıcı iptali → CLOSE                                │     │
│  │                                                             │     │
│  │ re_evaluation_count >= 3? → ESCALATE (döngü sonu)          │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                       │
│  Feedback Loop KARAR VERMEZ.                                          │
│  Feedback Loop yalnızca Decision Engine'i yeniden ÇAĞIRIR.            │
│  Nihai karar her zaman Decision Engine'indir (MASTER-004).            │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
                                │ FeedbackTrigger
                                │ (RETRY / RE-EVALUATE / CORRECT)
                                ▼
                   ┌─────────────────────┐
                   │ DECISION ENGINE     │◀─────── DÖNGÜ KAPANIR
                   │ (yeniden karar      │
                   │  üretir)            │
                   └─────────────────────┘
                                │
                                │ Yeni DecisionPacket
                                ▼
                   ┌─────────────────────┐
                   │ CONSTITUTIONAL      │
                   │ VALIDATOR           │
                   └─────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
              PASS / WARNING           BLOCK / RETRY
                    │                       │
                    ▼                       └──→ Feedback Loop'a DÖN
              ┌──────────┐
              │ EXECUTOR │
              └──────────┘
                    │
                    ▼
              ExecutionResult → Feedback Loop'a DÖN (döngü sürer)


┌───────────────────────────────────────────────────────────────────────┐
│                        DECISION LOG CENTER                             │
│                                                                       │
│  Her döngü adımı kaydedilir:                                          │
│  • Orijinal karar ID'si                                               │
│  • Feedback tetikleyicisi                                             │
│  • re_evaluation_count                                                │
│  • Yeni karar ID'si                                                   │
│  • Döngü süresi (ms)                                                  │
│  • Nihai sonuç (PASS / ESCALATE / CLOSE)                              │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────────┐
│                      LIVE ACTIVITY CENTER (FEAT-015)                   │
│                                                                       │
│  Yönetici Feedback Loop döngülerini CANLI İZLER.                      │
│  Müdahale EDEMEZ (salt izleyici).                                     │
└───────────────────────────────────────────────────────────────────────┘
```

---

### 10. Sonuç

AR-002_22, HLK'nın **Constitutional Feedback / Control Loop mimarisini** tanımlayan anayasal referans maddesidir.

Bu maddenin koruduğu temel ilke:

> **Feedback Loop, HLK'nın ikinci bir karar merkezi değildir.**
>
> **Feedback Loop yalnızca mevcut kararın anayasal geçerliliğini yeniden değerlendiren kontrol mekanizmasıdır.**
>
> **Nihai karar yetkisi her zaman yalnızca Decision Engine'e aittir (MASTER-004).**

Feedback Loop;

* Decision Engine'in ürettiği kararların sistem koşulları değiştiğinde güncellenmesini sağlar,
* Hatalı kararların zincirleme başarısızlık üretmesini engeller,
* Kaynak israfını önler,
* Gereksiz yeniden değerlendirme yapmaz,
* Sonsuz döngüye girmez,
* Karar vermez, yalnızca denetler ve gerektiğinde Decision Engine'i yeniden çağırır.

Bu mimari; Constitution Compiler, Rule Cache, Decision Engine, Constitutional Validator, Selection Architecture, Executor ve Decision Log Center ile birlikte çalışarak HLK'nın **anayasal öz denetim sistemini** oluşturur.

---

### Kural Durumu

**AKTİF** — Bu madde, HLK'nın yeni anayasal mimarisini yansıtacak şekilde güncellenmiştir.

Önceki sürüm yalnızca "Karar Merkezi Yeniden Değerlendirme Mimarisi" başlığı altında tetikleyici listesi içermekteydi. Güncel sürüm, HLK'nın tüm anayasal bileşenlerini (Constitution Compiler, Rule Cache, Decision Engine, Constitutional Validator, Selection Architecture, Executor, Feedback Loop, Decision Log Center) kapsayan tam bir Constitutional Feedback / Control Loop mimarisi tanımlamaktadır.

---

## AR-002_23

### Bilgi Açığı Görev Atama Mimarisi

HLK içerisinde araştırma ajanları rastgele veri toplamak amacıyla görevlendirilmez.

AR-002_20 tarafından tespit edilen her bilgi açığı, bağımsız bir araştırma görevine dönüştürülür.

HLK önce:

1. Ürün Referans Paketini oluşturur.
2. Bilgi Açığı Analizini gerçekleştirir.
3. Eksik bilgi alanlarını listeler.

Daha sonra araştırma ajanlarını bu eksik alanları kapatacak şekilde görevlendirir.

**Örnek:**

Ürün: Kadın Korse

Bilgi Açıkları: Arka görünüm, Yan görünüm, Kumaş dokusu, Yakın plan detaylar, Etiket bilgileri, Kullanım sahnesi

HLK aşağıdaki gibi görevler oluşturabilir:

* Görev-1: Arka görünüm araştır.
* Görev-2: Kumaş dokusu araştır.
* Görev-3: Etiket bilgilerini araştır.
* Görev-4: Kullanım sahnelerini araştır.

Araştırma ajanlarının amacı belirli sayıda görsel bulmak değildir.

Araştırma ajanlarının amacı bilgi açığını kapatacak içerikleri bulmaktır.

Kategori görselleri, navigasyon ikonları, site logoları veya ürün bilgi açığını kapatmayan içerikler araştırma başarısı olarak değerlendirilmez.

HLK araştırma sonucunu:

* Bulunan içerik sayısı ile değil,
* Kapatılan bilgi açığı sayısı ile değerlendirir.

Bu örnekler sınırlayıcı değildir.

HLK ürün kategorisine, araştırma aşamasına ve mevcut bilgi durumuna göre yeni bilgi alanları tanımlayabilir.

HLK gerektiğinde bilgi açığı listesini genişletebilir veya daraltabilir.

---

## AR-002_24

### Referans Görsel Merkezli Araştırma İlkesi

HLK araştırma sürecinde ürün linkini nihai araştırma hedefi olarak kabul etmez.

Ürün linki yalnızca:

* Ürünün doğrulanması,
* Marka web sitesinin bulunması,
* Gerçek ürün adının tespit edilmesi,
* Ürün Referans Paketinin oluşturulması

amacıyla kullanılır.

Araştırmanın temel referansı:

* Ürünün gerçek adı,
* Marka bilgisi,
* Referans Ürün Görseli

olmalıdır.

HLK mümkünse:

1. Platform linkinden marka web sitesini bulur.
2. Marka web sitesinden gerçek ürün adını doğrular.
3. Marka web sitesinden ürünün resmi görsellerini toplar.
4. En uygun görseli Referans Ürün Görseli olarak belirler.

Bu görsel araştırmanın merkez nesnesi olarak kullanılır.

Araştırma sırasında bulunan her yeni içerik:

* Referans Ürün Görseli ile ilişkilendirilir.
* Bilgi Açığını kapatıp kapatmadığı değerlendirilir.
* Ürünü tanımaya yeni katkı sağlayıp sağlamadığı analiz edilir.

Aynı bilgi alanını tekrar eden içerikler araştırma başarısı olarak değerlendirilmez.

Aşağıdaki içerikler tek başına araştırma başarısı kabul edilmez:

* Site logoları
* Menü görselleri
* Navigasyon ikonları
* SVG ikonları
* Kategori thumbnail görselleri
* Aynı açıdan tekrar eden ürün görselleri
* Referans görsel ile aynı bilgiyi taşıyan içerikler

Araştırma başarısı:

* Bulunan görsel sayısı ile değil,
* Kapatılan bilgi açığı sayısı ile ölçülür.

HLK araştırma sırasında elde edilen yeni verilere göre:

* Ajan öncelik sıralamasını yeniden oluşturabilir.
* Araştırma görevlerini yeniden dağıtabilir.
* Yeni ajan görevlendirebilir.
* Mevcut ajanları durdurabilir.

Bu kararlar HLK Karar Merkezi tarafından verilir.

---

## AR-002_25

### Ürün Eşleme ve Doğrulama İlkesi

HLK tarafından yürütülen araştırmalar sırasında bulunan her yeni içerik, teknik gürültü (SVG/logo/kategori) filtresinden geçtikten sonra ayrıca Ürün Referans Paketi ile eşleme doğrulamasına tabi tutulur.

Bir içeriğin araştırma sonucuna dahil edilebilmesi için;

* marka adı,
* ürün adı,
* ürün modeli,
* referans ürün görseli

bilgilerinden en az birinde Referans Paket ile yeterli eşleşme göstermesi beklenir.

Yeterli eşleşme göstermeyen içerikler aşağıdaki durumlara göre sınıflandırılır:

* AGENT_NOISE — Ürünle ilgisi olmayan içerik (teknik gürültü). AR-002_24 kapsamında filtrelenir.
* AGENT_MISMATCH — Görsel olarak ürün içeriğine benzeyen ancak farklı bir markaya, farklı bir ürüne veya farklı bir modele ait olduğu tespit edilen içerik. Araştırma sonucuna dahil edilmez.
* AGENT_UNVERIFIED — Marka, ürün adı veya referans görsel ile eşleşmesi kesin olarak doğrulanamayan içerik. Düşük güvenle işaretlenir ve araştırma raporunda ayrı bir kategoride gösterilebilir.

HLK eşleme doğrulamasında aşağıdaki yöntemleri kullanabilir:

* Sayfa başlığında veya meta açıklamasında ürün adının veya marka adının geçip geçmediğinin kontrolü.
* Görsel dosya adında, alt metninde (alt attribute) veya çevreleyen HTML etiketlerinde ürün adı, marka adı veya model bilgisinin aranması.
* Görselin bulunduğu sayfanın veya bağlamın ürünle ilgisinin değerlendirilmesi.
* Referans ürün görseli ile görsel benzerlik veya bağlamsal ilişkinin değerlendirilmesi.
* görsel arama sistemleri aracılığıyla görselin hangi ürünlere ait olduğunun araştırılması.

Bu yöntemler sınırlayıcı değildir.

HLK ürün kategorisine, mevcut veri kalitesine ve araştırma derinliğine göre yeni doğrulama yöntemleri belirleyebilir veya bazı yöntemleri kullanım dışı bırakabilir.

Yeterli eşleşme göstermeyen içerikler, AGENT_MISMATCH veya AGENT_NOISE olarak işaretlenir ve araştırma sonuçlarına dahil edilmez.

HLK'nin amacı mümkün olduğunca çok içerik toplamak değil, toplanan her içeriğin doğru ürüne ait olduğundan emin olmaktır.

---

## AR-002_26

### Ürün Eşleşme Güven Skoru İlkesi

HLK tarafından yürütülen araştırmalar sırasında bulunan içeriklerin araştırma sonucuna dahil edilip edilmeyeceği yalnızca nitel değerlendirmeler ile belirlenmez.

Gerekli durumlarda HLK, bulunan içerik ile Ürün Referans Paketi arasındaki eşleşme seviyesini puanlayabilir.

Bu puanlama;

* marka uyumu,
* ürün adı uyumu,
* ürün modeli uyumu,
* referans ürün görseli uyumu,
* bağlamsal ürün ilişkisi,
* ürüne ait teknik özellik uyumu

gibi kriterlerden biri veya birkaçı kullanılarak gerçekleştirilebilir.

HLK'nin amacı mümkün olan en fazla içeriği toplamak değil, araştırma sonucuna dahil edilen içeriklerin doğru ürüne ait olduğundan mümkün olan en yüksek güven seviyesinde emin olmaktır.

Bu nedenle eşleşme değerlendirmesi sonucunda içerikler;

* AGENT_OK
* AGENT_UNVERIFIED
* AGENT_MISMATCH

olarak sınıflandırılabilir.

Eşleşme değerlendirmesinde kullanılacak;

* puan ağırlıkları,
* güven eşikleri,
* karar limitleri,
* kategoriye özel değerlendirme katsayıları,

ANA KURALLAR içerisinde sabit olarak tanımlanmaz.

Bu değerler;

* Global Configuration (GC),
* Karar Merkezi,
* Ürün kategorisi,
* Araştırma bağlamı

tarafından dinamik olarak belirlenebilir.

Bir içeriğin araştırma sonucuna dahil edilmesi için gerekli güven seviyesi ürün kategorisine, araştırma amacına ve mevcut bilgi açığı durumuna göre değişebilir.

Bu nedenle HLK, eşleşme güven skorunu mutlak bir doğruluk ölçütü olarak değil, araştırma kararlarını destekleyen dinamik bir güven mekanizması olarak değerlendirir.

---

## AR-002_27

### Active Conversation Screen Mimarisi

HLK içerisinde kullanıcıya aynı anda yalnızca bir adet aktif konuşma sahnesi gösterilir.

Bu mimarinin amacı Telegram uygulamasını klasik bir sohbet ekranı olarak kullanmak değil, HLK'nın bulunduğu STATE'e ait tek aktif konuşma ekranını kullanıcıya sunmaktır.

Bu mimari ürün linki bekleme aşamasında aktif değildir.

HLK, Active Conversation Screen modunu ancak kullanıcı tarafından ilk ürün linki gönderildikten sonra başlatabilir.

Akış aşağıdaki şekilde çalışır:

```
/start
↓
Dil Seçimi
↓
Ürün Linki Bekleniyor
↓
Kullanıcı Ürün Linki Gönderir
↓
Link Doğrulama Süreci Başlar
↓
ACTIVE_CONVERSATION_SCREEN Modu Başlar
```

HLK yeni bir konuşma döngüsüne geçtiğinde;

1. Bulunduğu STATE'i belirler.
2. Yeni konuşma içeriğini oluşturur.
3. Yeni Active Conversation Screen sahnesini hazırlar.
4. Önceki Active Conversation Screen sahnesini kaldırır.
5. Yeni sahneyi kullanıcıya gösterir.

Her Active Conversation Screen aşağıdaki bileşenlerden oluşur:

• Konuşma Balonu
• Mavi Ses Çubuğu
• Kullanıcı Seçim Butonları

Kullanıcı aynı anda birden fazla HLK konuşma sahnesi görmez.

HLK'nin amacı sohbet geçmişi göstermek değil, kullanıcının yalnızca o an bulunduğu STATE ile ilgili aktif konuşma sahnesine odaklanmasını sağlamaktır.

Bu mimari, Conversation UI Module üzerinde çalışan üst seviye ekran yönetim katmanıdır.

Bu mimari, kullanıcı tarafından görülen tüm HLK konuşmalarında varsayılan ekran yönetim standardı olarak uygulanır.

---

## AR-002_28

### Conversation Scene Engine Mimarisi

HLK içerisinde her konuşma döngüsü bir Conversation Scene (Konuşma Sahnesi) olarak yürütülür.

Conversation Scene'in amacı yalnızca kullanıcıya metin göstermek değildir.

Amaç;

• HLK konuşmasını,
• ses üretimini,
• konuşma balonunu,
• mavi ses çubuğunu,
• kullanıcı etkileşimini

tek bir senkronize sahne olarak yönetmektir.

HLK yeni bir STATE'e geçtiğinde önce ilgili konuşma sahnesini hazırlar.

Conversation Scene aşağıdaki yaşam döngüsünü izler:

1. HLK bulunduğu STATE'i belirler.
2. Kullanıcıdan elde edilmesi gereken bilgiyi belirler.
3. Yeni konuşma içeriğini oluşturur.
4. Konuşma sahnesini hazırlar.
5. Active Conversation Screen üzerinde yeni sahneyi oluşturur.
6. Mavi ses çubuğunu görünür hale getirir.
7. Ses oynatma için gerekli hazırlıkları tamamlar.
8. Sahne oynatma durumuna geçer.

Sahne oynatılmaya başladığında;

• HLK sesi oynatılır.
• Mavi ses çubuğu aktif hale gelir.
• Konuşma balonu daktilo efekti ile oluşur.
• Tüm bileşenler senkron şekilde çalışır.

Sahne tamamlandığında;

• Ses oynatımı sona erer.
• Mavi ses çubuğu durur.
• Konuşma balonu tamamlanmış durumda ekranda kalır.
• İlgili kullanıcı seçim butonları görünür hale gelir.
• Sistem kullanıcı cevabını bekleme durumuna geçer.

HLK içerisinde aynı anda yalnızca bir adet aktif Conversation Scene bulunabilir.

Yeni bir Conversation Scene oluşturulmadan önce önceki sahne sonlandırılır.

Conversation Scene mimarisi, Active Conversation Screen üzerinde çalışan ve kullanıcı tarafından deneyimlenen tüm HLK konuşmalarının standart yürütme mekanizmasıdır.

---

## AR-002_29

### AHU Character Identity and Reference Library Architecture

AHU, HLK'nın varsayılan ve kalıcı karakter kimliğidir.

AHU yalnızca bir ses modeli değildir.

AHU;

• HLK'nın ses kimliğini,
• konuşma karakterini,
• konuşma ritmini,
• vurgu yapısını,
• genel iletişim tarzını

temsil eden karakter referansıdır.

Kullanıcı tarafından seçilen dil değişse bile HLK'nın karakter kimliği değişmez.

HLK, desteklenen tüm dillerde aynı karakteri temsil etmeye devam eder.

Bu amaçla sistem içerisinde AHU'ya ait ve onaylanmış referans ses kayıtları kullanılabilir.

Bu referans kayıtları bir Character Reference Library (Karakter Referans Kütüphanesi) oluşturur.

Karakter Referans Kütüphanesi içerisinde;

• farklı dillere ait,
• sistem tarafından onaylanmış,
• AHU karakterini temsil eden

ses örnekleri bulunabilir.

HLK yeni ses üretimi gerçekleştireceği zaman yalnızca üretilecek metni değerlendirmez.

Gerekli durumlarda Character Reference Library içerisinde bulunan uygun referans sesleri de kullanarak karakter tutarlılığını korumaya çalışır.

Amaç birebir aynı sesi üretmek değildir.

Amaç, farklı dillerde üretilen yeni seslerin mümkün olan en yüksek seviyede aynı karakter kimliğini taşımasını sağlamaktır.

HLK tarafından üretilen tüm yeni konuşmaların hedefi, kullanıcının dil değişse bile aynı dijital karakter ile iletişim kurduğu hissini korumaktır.

Character Reference Library içerisinde yer alan referans kayıtlar, oynatılacak son kullanıcı içerikleri değil; HLK'nın karakter kimliğini korumaya yardımcı olan mimari referans varlıklarıdır.

Bu mimari, Active Conversation Screen ve Conversation Scene Engine tarafından kullanılan tüm ses üretim süreçlerinin karakter referans katmanını oluşturur.

---

## AR-002_30

### AHU Multi-Language Voice Generation Architecture

HLK tarafından kullanıcı ile gerçekleştirilen tüm sesli iletişimlerde kullanılacak varsayılan karakter sesi AHU'dur.

Kullanıcı tarafından seçilen dil değişse bile HLK'nın karakter kimliği değişmez.

HLK, farklı dillerde konuşurken de AHU karakter kimliğini korur.

Bu amaçla HLK, Character Reference Library içerisinde bulunan ve kullanıcının seçtiği dile ait AHU referans ses kayıtlarını değerlendirebilir.

Her dil kendi AHU referans kayıtlarına sahip olabilir.

Bu referans kayıtlar, ilgili dil için daha önce oluşturulmuş ve sistem tarafından onaylanmış AHU ses örneklerinden oluşabilir.

HLK yeni bir konuşma üreteceği zaman;

1. Kullanıcının seçtiği dili belirler.
2. Üretilecek konuşma metnini oluşturur.
3. Character Reference Library içerisinde ilgili dile ait uygun AHU referanslarını belirler.
4. Yeni ses üretim görevini oluşturur.
5. Üretilen sesin ilgili dildeki AHU karakter kimliği ile tutarlı olup olmadığını değerlendirir.
6. Uygun bulunursa Conversation Scene Engine tarafından kullanılmak üzere ses çıktısını hazır hale getirir.

HLK yeni ses üretiminde yalnızca metin içeriğini esas almaz.

Gerekli durumlarda;

• ilgili dildeki AHU referans kayıtları,
• konuşma ritmi,
• vurgu yapısı,
• karakter tonu,
• dil profili

gibi unsurları birlikte değerlendirerek karakter bütünlüğünü korumaya çalışır.

Character Reference Library içerisinde aynı dil için birden fazla referans kayıt bulunabilir.

HLK, kendi karar mekanizmasını kullanarak üretilecek konuşmaya en uygun referans kayıtları seçebilir.

Amaç tüm dillerde aynı sesi üretmek değildir.

Amaç, her dilde o dile ait AHU karakterini koruyarak kullanıcının aynı dijital karakter ile iletişim kurduğu hissini sürdürebilmektir.

HLK tarafından üretilen her yeni ses, ilgili dildeki AHU karakter kimliği ile ilişkilendirilen yeni bir karakter çıktısı olarak değerlendirilir.

Character Reference Library içerisinde bulunan referans kayıtlar son kullanıcıya oynatılmak zorunda değildir.

Bu kayıtlar, HLK'nın yeni ses üretimlerinde karakter tutarlılığını koruyabilmesi amacıyla kullanılan mimari referans varlıklardır.

Bu mimari, Conversation Scene Engine tarafından kullanılan tüm yeni ses üretim süreçlerinin standart çoklu dil ses üretim mekanizmasını oluşturur.

---

## AR-002_31

### Speech-Text-Wave Synchronization Architecture

HLK tarafından kullanıcıya gösterilen her Conversation Scene içerisinde;

• AHU sesi,
• konuşma balonu,
• daktilo efekti,
• mavi ses çubuğu

birbirinden bağımsız bileşenler olarak değil, tek bir senkronize oynatma sistemi olarak yönetilir.

Conversation Scene oynatılmadan önce HLK;

1. Konuşma metnini oluşturur.
2. İlgili dilde AHU ses üretimini tamamlar.
3. Active Conversation Screen üzerinde yeni konuşma sahnesini hazırlar.
4. Konuşma balonunu oluşturur.
5. Mavi ses çubuğunu görünür hale getirir.

Bu aşamada mavi ses çubuğu görünür durumdadır ancak aktif değildir.

HLK, Conversation Scene oynatılmaya hazır hale gelmeden PLAY durumuna geçmez.

PLAY durumu başladığında;

• AHU sesi oynatılır.
• Mavi ses çubuğu aktif hale gelir.
• Konuşma balonundaki metin daktilo efekti ile oluşmaya başlar.

Bu üç bileşen aynı Conversation Scene içerisinde senkronize şekilde çalışır.

HLK'nin amacı sesi, metni ve görsel geri bildirimi tek bir kullanıcı deneyimi olarak sunmaktır.

Ses oynatımı devam ettiği sürece mavi ses çubuğu aktif durumda kalır.

Daktilo efekti, mümkün olan durumlarda konuşma sahnesinin doğal akışını koruyacak şekilde ilerler.

Ses oynatımı tamamlandığında;

• Mavi ses çubuğu durur.
• Daktilo efekti tamamlanmış olmalıdır.
• Konuşma balonu son haliyle ekranda kalır.

Ses oynatımı tamamlanmadan kullanıcı seçim butonları gösterilemez.

Kullanıcı seçim butonları yalnızca Conversation Scene tamamlandıktan sonra görünür hale gelir.

Conversation Scene tamamlandığında sistem kullanıcı cevabını bekleme durumuna geçer.

Bu mimarinin amacı, kullanıcının ayrı ayrı çalışan arayüz bileşenleri görmesini değil; konuşan, düşünen ve iletişim kuran tek bir dijital karakter deneyimi yaşamasını sağlamaktır.

Speech-Text-Wave Synchronization Architecture, Conversation Scene Engine üzerinde çalışan standart senkronizasyon katmanıdır.

---

## AR-002_32

### Master Reference Voice Architecture

HLK'nın karakter kimliğini temsil eden tek resmi referans ses kaydı MASTER_REFERENCE_VOICE olarak tanımlanır.

MASTER_REFERENCE_VOICE, HLK'nın ses karakterinin, konuşma ritminin, vurgu yapısının ve genel konuşma tarzının temel referansıdır.

Başlangıç referansı:

MASTER_REFERENCE_VOICE = hlk_ses_test01.mp3

Bu dosya HLK'nın karakter kimliğinin ana referans kaydı olarak kabul edilir.

HLK yeni bir konuşma sahnesi oluşturacağı zaman;

1. Bulunduğu STATE'i belirler.
2. Üretilecek konuşma metnini oluşturur.
3. MASTER_REFERENCE_VOICE kaydını ilgili ses üretim görevine referans olarak ekler.
4. Mevcut aktif ses üretim sağlayıcısını kullanarak ses üretim görevini oluşturur.
5. Yeni ses çıktısını üretir.
6. Üretilen sesi MASTER_REFERENCE_VOICE ile karşılaştırır.
7. Bir Voice Confidence Score oluşturur.
8. Elde edilen skor doğrultusunda ses çıktısının kullanılabilir olup olmadığına karar verir.

HLK'nın amacı yalnızca yeni bir ses üretmek değildir.

Amaç, üretilen her yeni sesin mümkün olan en yüksek seviyede AHU karakter kimliğini korumasını sağlamaktır.

Bu nedenle ses üretim sürecinde referans ses kullanımı ve üretim sonrası karakter doğrulaması birlikte uygulanabilir.

Voice Confidence Score, HLK tarafından üretilen yeni sesin MASTER_REFERENCE_VOICE ile olan karakter uyumluluğunu temsil eder.

HLK gerekli durumlarda Voice Confidence Score değerini karar mekanizmalarında kullanabilir.

MASTER_REFERENCE_VOICE sistem içerisindeki tüm ses üretim süreçlerinin ortak karakter referansı olarak kabul edilir.

Bu mimari, AHU Character Identity Architecture, AHU Multi-Language Voice Generation Architecture ve Speech-Text-Wave Synchronization Architecture üzerinde çalışan standart karakter doğrulama katmanını oluşturur.

---

## AR-002_33

### Conversation Asset Cache Architecture

HLK tarafından oluşturulan konuşma sahneleri mümkün olan durumlarda tekrar kullanılabilir varlıklar olarak değerlendirilir.

HLK'nın amacı aynı sahneyi, aynı içerikleri ve aynı varlıkları gereksiz yere tekrar üretmemektir.

Bu amaçla sistem içerisinde bir Conversation Asset Cache katmanı bulunabilir.

Conversation Asset Cache içerisinde aşağıdaki varlıklar saklanabilir:

• Konuşma Metinleri
• Ses Dosyaları
• Konuşma Balonları
• Kullanıcı Buton Yapıları
• Sahne Konfigürasyonları
• Diğer Conversation Scene Varlıkları

HLK yeni bir Conversation Scene oluşturacağı zaman;

1. Bulunduğu STATE'i belirler.
2. Oluşturulacak sahnenin cache anahtarını oluşturur.
3. Conversation Asset Cache içerisinde uygun bir kayıt olup olmadığını kontrol eder.
4. Uygun kayıt bulunursa mevcut varlıkları yeniden kullanabilir.
5. Uygun kayıt bulunamazsa yeni varlıkları üretir.
6. Üretilen yeni varlıkları Conversation Asset Cache içerisine kaydedebilir.

Conversation Asset Cache kullanımı zorunlu değildir.

HLK bulunduğu duruma göre cache kullanımına veya yeniden üretime karar verebilir.

Cache kullanımı sırasında STATE, dil, sahne tipi ve diğer gerekli değişkenler değerlendirilmelidir.

HLK'nın amacı yalnızca maliyet düşürmek değildir.

Amaç;

• Gereksiz üretimi azaltmak,
• Yanıt sürelerini iyileştirmek,
• Kaynak kullanımını optimize etmek,
• Kullanıcı deneyimini hızlandırmak

olarak tanımlanır.

Bu mimari, Conversation Scene Engine üzerinde çalışan standart sahne varlığı yeniden kullanım katmanını oluşturur.

---

## AR-002_34

### Conversation Reusability Decision Architecture

HLK tarafından oluşturulan her Conversation Scene yeniden kullanılabilir olarak kabul edilmez.

HLK'nın amacı yalnızca cache kullanmak değil, doğru durumda doğru varlıkları yeniden kullanmaktır.

Bu amaçla sistem içerisinde bir Conversation Reusability Decision katmanı bulunur.

Conversation Reusability Decision katmanı, mevcut sahnenin yeniden kullanılabilir olup olmadığını değerlendirir.

HLK yeni bir Conversation Scene oluşturacağı zaman;

1. Bulunduğu STATE'i belirler.
2. Sahnenin türünü belirler.
3. Sahnenin statik mi dinamik mi olduğunu değerlendirir.
4. Yeniden kullanılabilirlik analizini gerçekleştirir.
5. Uygun bulunursa Conversation Asset Cache kullanabilir.
6. Uygun bulunmazsa yeni sahne üretimini başlatır.

Genel olarak aşağıdaki türdeki sahneler yeniden kullanılabilir kabul edilebilir:

• Karşılama Sahneleri
• Ürün Linki İsteme Sahneleri
• Fotoğraf Yükleme Talimatları
• Süre Seçim Sahneleri
• Platform Seçim Sahneleri
• Genel Bilgilendirme Sahneleri

Aşağıdaki türdeki sahneler ise yeniden üretim gerektirebilir:

• Ürün Analiz Sonuçları
• Marka Analiz Sonuçları
• Rakip Analiz Sonuçları
• Kullanıcıya Özel İçerikler
• Ürüne Özel Değerlendirmeler
• Oturuma Özel Üretimler

HLK yeniden kullanılabilirlik kararı verirken;

• STATE bilgisi,
• Dil bilgisi,
• Sahne tipi,
• Kullanıcı girdileri,
• Ürün bilgileri,
• Oturum verileri

gibi değişkenleri değerlendirebilir.

Conversation Asset Cache kullanımı zorunlu değildir.

HLK gerekli gördüğü durumlarda yeniden üretim yapabilir.

Bu mimarinin amacı;

• Gereksiz üretimi azaltmak,
• Kaynak kullanımını optimize etmek,
• Yanıt sürelerini iyileştirmek,
• Karakter ve içerik tutarlılığını korumak

olarak tanımlanır.

Conversation Reusability Decision Architecture, Conversation Asset Cache Architecture üzerinde çalışan standart yeniden kullanım karar katmanını oluşturur.

---

## AR-002_35

### Research-Conversation Parallel Execution Architecture

HLK içerisinde ürün araştırma süreçleri ile kullanıcıdan brief toplama süreçleri birbirinden bağımsız iş akışları olarak yürütülür.

Ürün linki başarıyla doğrulandığında HLK, arka plan araştırmalarını başlatmak için kullanıcıdan yeni bir talimat beklemez.

Ancak araştırma sürecinin başlaması veya devam etmesi, kullanıcı ile yürütülen konuşma akışını durduramaz, geciktiremez veya bloke edemez.

Link doğrulama aşaması tamamlandıktan sonra HLK;

• Arka plan araştırmalarını başlatır,
• Active Conversation Screen modunu başlatır,
• İlgili Conversation Scene'i oluşturur,
• Kullanıcı ile brief toplama sürecine devam eder.

Araştırma görevleri ve konuşma görevleri birbirinden bağımsız olarak çalışır.

HLK, araştırma sonuçlarının tamamlanmasını bekleyerek kullanıcı ile olan konuşma akışını durduramaz.

Arka planda çalışan araştırmalar devam ederken HLK, bulunduğu STATE'in gerektirdiği bilgileri kullanıcıdan toplamaya devam eder.

Araştırma görevlerinin başarısız olması, yeniden denenmesi, ajan değiştirilmesi, timeout oluşması veya operasyonel nedenlerle gecikmesi; Active Conversation Screen'in oluşturulmasını veya Conversation Scene Engine'in çalışmasını engelleyemez.

Amaç:

• Kullanıcı bekleme sürelerini azaltmak,
• Arka plan araştırmalarını kesintisiz sürdürmek,
• Brief toplama sürecini hızlandırmak,
• Telegram üzerinde doğal ve akıcı bir kullanıcı deneyimi sağlamak.

Beklenen Akış:

```
STATE_LINK_VALIDATED
↓
Araştırma Başlat
↓
Active Conversation Screen Başlat
↓
Conversation Scene Oluştur
↓
Kullanıcıdan Sonraki Bilgiyi Topla
↓
Araştırma Arka Planda Devam Etsin
```

Temel İlke:

HLK'nin amacı araştırmanın tamamlanmasını beklemek değil, araştırma devam ederken kullanıcı ile konuşmaya ve brief toplamaya devam etmektir. Araştırma süreçleri hiçbir durumda Conversation Scene Engine'i bloke edemez.

---

## AR-002_36

### Scene Delivery Architecture

Conversation Scene Engine tarafından oluşturulan sahnelerin kullanıcıya teslim edilme yöntemini tanımlar.

HLK içerisinde bir sahnenin oluşturulmuş kabul edilebilmesi için yalnızca Conversation Scene Engine tarafından üretilmiş olması yeterli değildir.

Oluşturulan sahne ilgili iletişim kanalına başarıyla teslim edilmelidir.

Bir sahne aşağıdaki yaşam döngüsünü takip eder:

```
Scene Engine tarafından üretildi
↓
Scene Payload oluşturuldu
↓
Mesaj Teslim Modülü çağrıldı
↓
Telegram API gönderimi yapıldı
↓
Teslim onayı alındı
↓
Sahne başarıyla teslim edildi
```

Conversation Scene Engine tarafından oluşturulan ancak kullanıcıya teslim edilmeyen sahneler "oluşturulmuş sahne" olarak kabul edilmez.

STATE_SCENE_1, STATE_SCENE_2 veya STATE_SCENARIO_APPROVAL durumunda oluşturulan ilk sahne kullanıcıya teslim edilmeden HLK bir sonraki sahneye geçemez.

HLK teslim başarısızlığı durumunda;

• yeniden gönderim deneyebilir,
• hata kaydı oluşturabilir,
• alternatif teslim yöntemi kullanabilir,
• oturumu hata durumuna alabilir.

Teslim mekanizması, sahne üretim mekanizmasından bağımsız olarak çalışabilir.

Amaç:

• Sahne üretimi ile sahne teslimini birbirinden ayırmak.
• Kullanıcının gerçekten sahneyi görmesini garanti altına almak.
• Telegram entegrasyon problemlerini tespit edilebilir hale getirmek.

Beklenen Sonuç:

Conversation Scene Engine tarafından üretilen sahnelerin kullanıcı ekranına ulaşıp ulaşmadığı kontrol edilebilir hale gelir.

"Scene üretildi" ile "Scene teslim edildi" kavramları birbirinden ayrılır.

Telegram testlerinde görülen "Scene Engine çalışıyor ancak kullanıcı sahneyi görmüyor" problemi mimari seviyede tanımlanmış olur.

---

## AR-002_37

### Language Adaptive AHU Voice Architecture

AHU'nun konuşma dilinin kullanıcı tarafından seçilen oturum dili ile otomatik eşleştirilmesini tanımlar.

HLK içerisinde AHU hiçbir zaman sabit bir dil kullanmaz.

AHU tarafından üretilen tüm konuşmalar aktif oturum dili üzerinden oluşturulmalıdır.

Aktif oturum dili;

STATE_LANGUAGE_SELECTION aşamasında kullanıcı tarafından seçilen dildir.

Conversation Scene Engine bir sahne oluşturduğunda aşağıdaki zincir uygulanmalıdır:

```
Scene
↓
Session Language
↓
AHU Voice Generator
↓
MP3 Üretimi
↓
Telegram Sahnesi
```

Örnekler:

```
Türkçe seçildi
↓
Türkçe MP3
```

```
English seçildi
↓
English MP3
```

```
Deutsch seçildi
↓
Deutsch MP3
```

```
Español seçildi
↓
Español MP3
```

AHU'nun konuşma dili hiçbir zaman:

• Sistem dili
• Sunucu dili
• Geliştirici dili
• Varsayılan dil

olamaz.

AHU yalnızca kullanıcının seçtiği dilde konuşmalıdır.

Beklenen Sonuç:

"AHU konuşur" yaklaşımı yerine;

"AHU kullanıcının seçtiği dilde MP3 üretir ve konuşur"

yaklaşımı sistem genelinde standart hale gelir.

Bu kural HLK'nin çoklu dil mimarisi ile tam uyumlu çalışmasını sağlar.

---

## AR-002_38 — Scene Delivery Architecture

Conversation Scene Engine tarafından oluşturulan her sahne,
kullanıcıya başarıyla teslim edilmeden tamamlanmış kabul edilemez.

HLK sisteminde;

* Scene Created
* Scene Delivered

kavramları birbirinden bağımsız olarak değerlendirilmelidir.

Her Conversation Scene aşağıdaki yaşam döngüsünü izlemek zorundadır:

```
Conversation Scene Engine
↓
Scene Payload Creation
↓
Message Delivery Module
↓
Telegram API Delivery
↓
Delivery Confirmation
↓
Scene Delivered
```

### Kurallar

* Her Conversation Scene bir Scene Payload üretmelidir.
* Scene Payload yalnızca Delivery Module üzerinden teslim edilmelidir.
* Telegram API teslim onayı alınmadan sahne tamamlandı olarak işaretlenemez.
* Teslim başarısız olursa sistem Retry, Error Logging ve Session Error mekanizmalarını çalıştırmalıdır.
* Teslim edilmeyen sahneler sonraki sahnenin oluşturulmasını engellemelidir.
* STATE_SCENE_1, STATE_SCENE_2 veya STATE_SCENARIO_APPROVAL içerisinde yeni sahneye geçilebilmesi için mevcut sahnenin başarıyla teslim edilmiş olması zorunludur.
* Delivery katmanı Conversation Scene Engine'den bağımsız çalışmalıdır.

### Beklenen Davranış

HLK tarafından oluşturulan hiçbir sahne,
kullanıcıya teslim edildiği doğrulanmadan tamamlanmış kabul edilmez.

### Kural Durumu

**AKTİF**

---

## AR-002_39

### Native Video Scene Architecture v3.5 — Conversation Scene Completion Controller

HLK v3.5 ile birlikte **Native Video Scene** mimarisine geçilmiştir.

Eski mimaride (v3.0) bir Conversation Scene, Telegram katmanında birden çok bağımsız bileşenin (ayrı ses dosyası, ayrı konuşma balonu, ayrı daktilo efekti, ayrı senkronizasyon) birleştirilmesiyle oluşturulurdu.

v3.5 Native Video Scene mimarisinde tüm bu bileşenler video üretim katmanına taşınmıştır.

Bu mimaride:

• AHU sesi **video içerisinde** yer alır.
• Dudak senkronizasyonu (Lip-Sync) **video içerisinde** yer alır.
• Konuşma balonları **video içerisinde** yer alır.
• Daktilo efekti **video içerisinde** yer alır.
• Konuşma akışı **video içerisinde** render edilir.

Telegram artık sahne üretmez.

Telegram yalnızca nihai sahneyi (MP4 dosyasını) oynatır.

────────────────────────────────

**Taşınan Bileşenler — Korunan Özellikler**

Aşağıdaki bileşenlerin hiçbiri kaldırılmamıştır. Yalnızca üretim katmanları değişmiştir:

| Bileşen | Eski Katman | Yeni Katman (v3.5) |
|---|---|---|
| Daktilo Efekti | Telegram Typewriter Layer | Video Typewriter Layer (render) |
| Konuşma Balonu | Telegram mesaj katmanı | Video içi balon (render) |
| Dudak Senkronizasyonu | — | Video içi Lip-Sync (render) |
| AHU Sesi | Ayrı MP3 dosyası | Video içi ses kanalı |

Esas alınması gereken tanım:

> Daktilo efekti **kaldırılmamıştır**. Telegram katmanından alınarak Native Video Scene katmanına **taşınmıştır**.

Aynı şekilde:

> Lip-Sync **kaldırılmamıştır**. Video üretim katmanına **taşınmıştır**.

────────────────────────────────

**Temel İlke**

Native Video Scene kullanılan sahnelerde:

**Video = Conversation Scene**

olarak kabul edilir.

────────────────────────────────

**Sahne Tamamlanma Kuralı**

Native Video Scene mimarisinde:

• **Sahne başlangıcı** = Video başlangıcı
• **Sahne bitişi** = Video bitişi

olarak kabul edilir.

────────────────────────────────

**Video Süresi Kuralı**

HLK sabit video süresi kullanamaz.

`SAHNE1_SURE = 15`, `SAHNE2_SURE = 13` gibi sabit süre tanımları esas alınamaz.

HLK gerekli süre bilgisini aktif video dosyasından dinamik olarak elde etmelidir.

**Dinamik Süre İlkesi:**

Video değiştiğinde sistem otomatik uyum sağlamalıdır:

• 5 saniyelik video → 5 saniyelik sahne
• 7 saniyelik video → 7 saniyelik sahne
• 12 saniyelik video → 12 saniyelik sahne

Kod değişikliği gerektirmeden çalışmalıdır.

────────────────────────────────

**Sahne Sonu Davranışı**

Video tamamlandığında:

• Video tekrar oynatılamaz.
• Video döngüye alınamaz.
• Video yeniden render edilerek tekrar oynatılamaz.
• Video kullanıcı ekranından kaldırılır.
• Kullanıcı seçim butonları görünür hale getirilir.
• Sonraki state başlatılır.

────────────────────────────────

**Nihai Amaç**

HLK'nin amacı süre yönetmek değildir.

HLK'nin amacı:

hazırlanmış Native Video Scene'i kullanıcıya oynatmak,

sahne tamamlandığında temiz şekilde sonlandırmak

ve bir sonraki state'e geçmektir.

---

## AR-002_40

### Native Video Scene Completion Architecture (v3.5)

AR-002_39 v3.5 güncellemesi ile birlikte:

**Video = Scene**

olarak tanımlanmıştır.

Bu nedenle sahne tamamlanma mimarisi yeni Native Video Scene yapısına uyarlanmıştır.

────────────────────────────────

**Temel İlke**

Native Video Scene kullanılan sahnelerde:

• **Video Başlangıcı** = Sahne Başlangıcı
• **Video Sonu** = Sahne Sonu

olarak kabul edilir.

────────────────────────────────

**Native Video Scene İçeriği**

Video aşağıdaki bileşenlerin tamamını içerir:

• AHU sesi
• Dudak senkronizasyonu
• Konuşma balonları
• Daktilo efekti
• Görsel animasyonlar

Bu nedenle sahne tamamlanması için ayrı katman takibi yapılmaz.

────────────────────────────────

**Scene Completion Kuralı**

Bir Native Video Scene aşağıdaki durumda tamamlanmış kabul edilir:

1. Video son kareye ulaşmıştır.
2. Video oynatımı sona ermiştir.
3. Video tekrar başlatılmamıştır.
4. Video döngüye alınmamıştır.

────────────────────────────────

**Scene Settle Phase**

Video tamamlandıktan sonra sistem kısa bir Scene Settle Phase kullanabilir.

Amaç:

• son kareyi korumak
• doğal kapanış hissi oluşturmak
• ani kaybolma hissini önlemek

────────────────────────────────

**Dinamik Bekleme Kuralı**

Scene Settle Phase sabit süre kullanamaz.

`2 sn`, `3 sn`, `5 sn` gibi hardcoded süreler tanımlanamaz.

Bekleme süresi:

• sahne tipi
• kullanıcı deneyimi
• medya yapısı

esas alınarak sistem tarafından belirlenir.

────────────────────────────────

**Scene Cleanup**

Scene Settle Phase tamamlandıktan sonra:

• video kaldırılır
• ilgili state kapatılır
• sonraki state başlatılır

────────────────────────────────

**Kritik Kural**

Native Video Scene tamamlandıktan sonra:

• video ikinci kez oynatılamaz
• video otomatik tekrar başlatılamaz
• video döngüye alınamaz

────────────────────────────────

**Özel Kural — Karşılama Sahnesi (SAHNE-1)**

Video tamamlandıktan sonra:

• video kaldırılır
• dil seçim ekranı korunur
• yalnızca dil seçim ekranı görünür kalır

────────────────────────────────

**Nihai Amaç**

Kullanıcının sahnenin tamamlandığını net şekilde algılamasını sağlamak.

Video tamamlandıktan sonra sahnenin yeniden başlaması, ikinci kez oynatılması veya döngüye girmesi kesin olarak engellenmelidir.

---

## AR-002_41

### Native Video Presentation Architecture

HLK içerisinde kullanılan onaylı Conversation Scene videoları varsayılan olarak orijinal boyutlarında kullanılmalıdır.

Conversation Scene Engine tarafından oluşturulan sahnelerde;

• Zoom In uygulanmamalıdır.
• Zoom Out uygulanmamalıdır.
• Yapay küçültme uygulanmamalıdır.
• Karakter görünürlüğünü azaltan ölçekleme işlemleri uygulanmamalıdır.

HLK'nin amacı video alanını küçültmek değil, dijital karakterin görünürlüğünü ve kullanıcı üzerindeki etkisini korumaktır.

Bu nedenle onaylı sahne videoları mümkün olan en büyük görüntü alanında sunulmalıdır.

Conversation Scene tasarımı sırasında;

• Kullanıcı önce HLK karakterini görmelidir.
• Konuşma içeriği ikinci öncelik olarak sunulmalıdır.
• Görsel odak noktası HLK karakteri olmalıdır.

Konuşma balonları mümkün olan durumlarda video içerisine entegre edilmelidir.

Video dışı konuşma katmanları, yalnızca teknik zorunluluk veya özel kullanım senaryolarında kullanılabilir.

HLK içerisinde kullanılan sahne videoları;

• Telegram arayüzünü taklit etmek,
• Yapay boşluk oluşturmak,
• Karakter alanını küçültmek,
• Video alanını daraltmak

amacıyla yeniden ölçeklendirilmemelidir.

Beklenen Sonuç

HLK karakteri Conversation Scene'in ana görsel unsuru haline gelir.

Eski "%70 Small Video" yaklaşımı mimari seviyede kullanım dışı bırakılmış olur.

Orijinal Hedra videolarının doğal boyutlarında kullanılması sistem standardı haline gelir.

---

## AR-002_42

### Conversation Scene Lifecycle Architecture (v3.5 Native Video Scene Standardı)

HLK v3.5 ile birlikte Native Video Scene mimarisine geçilmiştir.

Bu mimaride:

• AHU sesi video içerisindedir.
• Dudak senkronizasyonu video içerisindedir.
• Konuşma balonları video içerisindedir.
• Daktilo efekti video içerisindedir.
• Konuşma akışı video içerisinde render edilmektedir.

Bu nedenle:

**Video = Conversation Scene**

olarak kabul edilir.

────────────────────────────────

**Yeni Yaşam Döngüsü**

```
SCENE_CREATED
     ↓
SCENE_READY
     ↓
VIDEO_PLAYBACK_STARTED
     ↓
VIDEO_PLAYBACK_ACTIVE
     ↓
VIDEO_PLAYBACK_COMPLETED
     ↓
SCENE_SETTLE_PHASE
     ↓
SCENE_CLEANUP
     ↓
NEXT_STATE
```

────────────────────────────────

**SCENE_CREATED**

Sahne oluşturulur.

• Medya dosyaları doğrulanır.
• Dosya erişimi doğrulanır.
• Sahne çalıştırılmaya hazırlanır.

────────────────────────────────

**SCENE_READY**

Sahne hazırdır.

Henüz kullanıcıya gösterilmemiştir.

────────────────────────────────

**VIDEO_PLAYBACK_STARTED**

Video kullanıcıya gönderilir.

Bu an:

**Sahne Başlangıcı**

olarak kabul edilir.

────────────────────────────────

**VIDEO_PLAYBACK_ACTIVE**

Video oynatılmaktadır.

Bu aşamada:

• AHU sesi
• Dudak senkronizasyonu
• Konuşma balonları
• Daktilo efekti

video içerisinde çalışır.

Telegram bu katmanları üretmez.

────────────────────────────────

**VIDEO_PLAYBACK_COMPLETED**

Video son kareye ulaşmıştır.

Bu an:

**Sahne Tamamlandı**

olarak kabul edilir.

────────────────────────────────

**SCENE_SETTLE_PHASE**

Sistemin kısa süreli doğal kapanış evresidir.

Amaç:

• son kare hissi oluşturmak
• ani kaybolmayı önlemek
• doğal geçiş sağlamak

────────────────────────────────

**SCENE_CLEANUP**

Sahne temizlenir.

• Video kaldırılır.
• Geçici kaynaklar temizlenir.
• State sonlandırılır.

────────────────────────────────

**NEXT_STATE**

Bir sonraki state başlatılır.

Örnek:

SAHNE-1 → STATE_LANGUAGE_SELECTION

SAHNE-2 → STATE_WAIT_PRODUCT_LINK

────────────────────────────────

**Kritik Kural**

Native Video Scene içerisinde:

• Telegram Typewriter Layer kullanılamaz.
• Telegram konuşma balonu oluşturamaz.
• Ayrı MP3 oynatılamaz.
• Video dışı senkronizasyon katmanı kullanılamaz.

Tüm sahne bileşenleri video içerisinde bulunmalıdır.

────────────────────────────────

**Nihai Amaç**

HLK'nin tüm konuşma sahnelerinde tek yaşam döngüsü modeli kullanmasını sağlamak.

Temel prensip:

**Video Başladı = Sahne Başladı**

**Video Bitti = Sahne Bitti**

---

## AR-002_43

### Native Video Scene Runtime Validation Architecture

Bir sahnenin ANA YASA'ya uygun tasarlanmış olması yeterli değildir.

Sahnenin çalışma anında da doğrulanması gerekir.

Aksi halde:

• video iki kez oynayabilir
• video döngüye girebilir
• cleanup çalışmayabilir
• state geçişi oluşmayabilir
• kullanıcı farklı davranış görebilir

────────────────────────────────

**Temel İlke**

HLK yalnızca tasarımı doğrulamaz.

HLK çalışma anındaki davranışı da doğrular.

────────────────────────────────

**Runtime Kontrol Noktaları**

Native Video Scene çalışırken aşağıdaki kontroller yapılır:

1. Video yalnızca bir kez gönderildi mi?
2. Video yalnızca bir kez oynatıldı mı?
3. Video tamamlandı mı?
4. Scene Settle Phase çalıştı mı?
5. Scene Cleanup çalıştı mı?
6. Bir sonraki State başlatıldı mı?

────────────────────────────────

**Runtime Validation Sonucu**

Tüm kontroller başarılı ise:

**RUNTIME_VALIDATED**

durumu oluşur.

────────────────────────────────

**Hata Durumu**

Aşağıdaki durumlar hata kabul edilir:

• çift video gönderimi
• çift oynatma
• cleanup başarısızlığı
• state geçiş başarısızlığı
• sonsuz bekleme
• döngü oluşması

────────────────────────────────

**HLK Görevi**

HLK runtime analizinde hata tespit ederse:

sorunu raporlamak zorundadır.

Sorunu gizleyemez.

────────────────────────────────

**Proje Yöneticisi Bildirimi**

Runtime Validation başarısız olduğunda:

HLK aşağıdaki formatta bildirim üretir:

```
Native Video Scene Runtime Hatası Tespit Edildi

Sahne:     ...
State:     ...
Hata:      ...
Önerilen İnceleme: ...
```

────────────────────────────────

**Nihai Amaç**

ANA YASA uyumunun yalnızca tasarım seviyesinde değil,

çalışma anında da doğrulanmasını sağlamak.

Bir sahnenin doğru yazılmış olması değil,

doğru çalışması esas alınır.

---

## AR-002_44

### Scenario Approval Architecture

HLK V1 içerisinde bulunan STATE_SCENARIO_APPROVAL yapısının mimari temelini oluşturur.

STATE_SCENARIO_APPROVAL bağımsız bir karar noktasıdır. STATE_BRIEF_COMPLETED sonrasında çalışır.

Bu aşamada kullanıcıya senaryo özeti sunulur. Kullanıcı yalnızca aşağıdaki kararlardan birini verebilir:

- **ONAY**: Kullanıcı senaryoyu onaylar. `EVENT_SCENARIO_APPROVED` oluşturulur ve `STATE_PRICING` akışı başlatılır.
- **RET**: Kullanıcı senaryoyu reddeder. `EVENT_SCENARIO_REJECTED` oluşturulur ve `STATE_SESSION_CLOSED` akışı başlatılır.

Bu yapı HLK ticari iş akışının ilk karar kapısıdır.

Bu mimari kural Flow Diagram (FD-008_1), State Engine (SE-007_3/4/5/6) ve Operational Rules (OR-004_6) ile tam uyumlu olmalıdır.

---

## AR-002_45

### Pricing Architecture

HLK V1 içerisinde bulunan STATE_PRICING yapısının mimari temelini oluşturur.

STATE_PRICING bağımsız bir ticari karar noktasıdır. STATE_SCENARIO_APPROVAL sonrasında çalışır. Sadece senaryosu onaylanmış işler bu aşamaya geçebilir.

Bu aşamada HLK gerekli üretim verilerini toplar ve yönetici fiyat teklifini hazırlar. Teklif kullanıcıya sunulur. Kullanıcı yalnızca aşağıdaki kararlardan birini verebilir:

- **ONAY**: Kullanıcı teklifi onaylar. `EVENT_PRICING_APPROVED` oluşturulur ve `STATE_VIDEO_PRODUCTION` akışı başlatılır.
- **RET**: Kullanıcı teklifi reddeder. `EVENT_PRICING_REJECTED` oluşturulur ve `STATE_SESSION_CLOSED` akışı başlatılır.

Bu yapı HLK ticari iş akışının son karar kapısıdır.

Bu mimari kural Flow Diagram (FD-008_1), State Engine (SE-007_3/4/5/6) ve Operational Rules (OR-004_7) ile tam uyumlu olmalıdır.

---

## AR-002_46

### Kural

HLK, **Link Validation (Ürün Linki Doğrulama)** ajanları hariç olmak üzere, her **Uzmanlık Alanı (Ürün Kategorisi)** için en başarılı ajan kombinasyonunu oluşturur ve kayıt altına alır.

Bir uzmanlık alanı için oluşturulan ajan kombinasyonu, o kategoriye ait ürünlerin araştırılması sırasında elde edilen en başarılı teknoloji yapısını temsil eder.

Aynı uzmanlık alanına ait yeni bir ürün geldiğinde HLK öncelikle bu kayıtlı ajan kombinasyonunu kontrol eder.

Eğer kayıtlı ajan kombinasyonunun **GC_AGENT_CACHE_DURATION** süresi dolmamış ise HLK **hiçbir yeniden değerlendirme, yeniden sıralama veya yeni ajan araştırması yapmadan** kayıtlı uzman ajan kombinasyonunu doğrudan kullanır.

**GC_AGENT_CACHE_DURATION** süresi dolmuş ise HLK ilgili uzmanlık alanı için yeniden ajan araştırması gerçekleştirir.

Yeni araştırma sonucunda elde edilen en başarılı ajan kombinasyonu mevcut kaydın yerine geçirilir ve yeni kombinasyon için **GC_AGENT_CACHE_DURATION** süresi yeniden başlatılır.

Bu mimari yalnızca uzmanlık alanı bazlı araştırma ajanları için uygulanır.

**Link Validation ajanları bu mimarinin kapsamı dışındadır** ve her oturumda kendi mimari kurallarına göre değerlendirilmeye devam eder.

---

### Amaç

Bu mimarinin amacı;

* Aynı uzmanlık alanı için gereksiz ajan araştırmalarını önlemek,
* Başarısı kanıtlanmış uzman ajan kombinasyonlarını yeniden kullanmak,
* Araştırma süresini kısaltmak,
* Kaynak tüketimini azaltmak,
* Her uzmanlık alanı için zamanla en başarılı teknoloji kombinasyonunu oluşturmak,
* HLK'nın uzman ajan bilgisini kurumsal hafızasının bir parçası haline getirmektir.

---

### Beklenen Sonuç

* Her uzmanlık alanı için tek bir aktif uzman ajan kombinasyonu bulunur.
* Aynı kategoriye ait yeni ürünlerde kayıtlı uzman ajan kombinasyonu öncelikli olarak kullanılır.
* 30 günlük süre dolmadan aynı kategori için yeniden ajan araştırması yapılmaz.
* 30 günlük süre dolduğunda ilgili uzmanlık alanı için yeni ajan araştırması gerçekleştirilir.
* Yeni araştırma sonucunda daha güncel uzman ajan kombinasyonu oluşturularak kayıt güncellenir.
* Böylece HLK, her uzmanlık alanı için sürekli gelişen ancak belirli süre boyunca kararlı çalışan bir uzman ajan mimarisine sahip olur.

---

## AR-002_47

### Task Package Engine Architecture

HLK içerisinde hiçbir ajan ham kullanıcı verisini doğrudan kullanmaz.

Workflow sürecinde toplanan tüm bilgiler, ajanlara gönderilmeden önce **Task Package Engine (Görev Paketi Motoru)** tarafından işlenir.

Task Package Engine;

* Workflow çıktısını,
* Decision Engine kararlarını,
* Feature çıktıları ve durumlarını,
* Kullanıcı tarafından sağlanan verileri,
* Digital Asset Archive kayıtlarını,
* Digital Asset Catalog kayıtlarını,
* Sistem kurallarını

birlikte değerlendirerek ilgili ajan için özel bir **Task Package (Görev Paketi)** oluşturur.

Her ajan yalnızca kendi görevini yerine getirebilmesi için gerekli olan minimum ve yeterli bilgiye erişebilir.

Task Package Engine;

* gereksiz bilgileri ayıklar,
* eksik bilgileri tespit eder,
* görevle ilgisiz verileri filtreler,
* yalnızca ilgili ajanın ihtiyaç duyduğu bilgileri görev paketine ekler.

HLK hiçbir ajana görev kapsamı dışında bilgi göndermez.

Her ajan yalnızca kendisine oluşturulan Task Package üzerinden çalışır.

Task Package oluşturulmadan hiçbir ajan çalıştırılamaz.

---

### Görev Paketi İçeriği

Her Task Package en az aşağıdaki bilgileri içerebilir.

* Task ID
* Workflow Kimliği
* Agent Kimliği
* Görev Tanımı
* Görev Amacı
* Giriş Verileri
* Beklenen Çıktılar
* Kalite Kriterleri
* Öncelik Seviyesi
* Zaman Limiti
* İlgili Asset Referansları
* İlgili Feature Referansları
* Güvenlik ve Erişim Kuralları

Görev paketinin içeriği ajanın uzmanlık alanına göre dinamik olarak oluşturulur.

---

### Veri İzolasyonu

Task Package Engine;

* Ses üretim ajanına gereksiz görsel verileri,
* Görsel araştırma ajanına gereksiz ses verilerini,
* Video üretim ajanına gereksiz kullanıcı verilerini,
* Hiçbir ajana görev kapsamı dışındaki bilgileri

gönderemez.

Her ajan yalnızca kendi görev paketini kullanarak çalışır.

---

### Amaç

Bu mimarinin amacı;

* Ajanlara gereksiz veri gönderimini engellemek,
* Token tüketimini azaltmak,
* Ajan doğruluğunu artırmak,
* Reklam üretim kalitesini yükseltmek,
* Modülerliği güçlendirmek,
* Yeni ajanların sisteme kolayca entegre edilmesini sağlamak,
* HLK'nın ajanlara veri gönderen değil, görev tanımlayan merkezi bir orkestrasyon sistemi olarak çalışmasını sağlamaktır.

---

### Beklenen Sonuç

* Workflow ile Agent arasına standart bir Task Package katmanı eklenmiş olur.
* Tüm ajanlar ortak bir görev paketi standardı ile çalışır.
* Ajanlar yalnızca görevleri için gerekli bilgiye erişebilir.
* Gereksiz veri aktarımı ortadan kaldırılır.
* Modüller arası bağımlılık azalır.
* Reklam üretim sürecinin doğruluğu ve kalite standardı yükselir.
* HLK'nın Agent Orchestration (Ajan Orkestrasyonu) mimarisi anayasal olarak tanımlanmış olur.

---

## AR-002_48

### Production Optimization Architecture (Üretim Optimizasyon Mimarisi)

### Kural

HLK'nın görevi yalnızca ürün hakkında doğru ve kaliteli bilgi toplamak değildir.

HLK aynı zamanda, görev paketini oluştururken ilgili **Servis Sağlayıcısının (Technology Provider)** ürünü mümkün olan en doğru ve en yüksek kalitede üretebilmesi için gerekli bilgi, dijital varlık ve üretim parametrelerini eksiksiz hazırlamakla yükümlüdür.

Task Package Engine, her servis sağlayıcısı için görevine özel bir üretim paketi oluşturur.

Her üretim paketi;

* Servis sağlayıcısının görevini en yüksek doğruluk ve kalite ile yerine getirebilmesi için gerekli tüm bilgi ve dijital varlıkları içerir.
* Görevle ilgisi olmayan hiçbir bilgiyi içermez.
* Gerekli hiçbir referans materyali eksik bırakmaz.

Video üretim servis sağlayıcıları için oluşturulan görev paketine, görevin gerektirdiği ölçüde;

* Kullanıcının yüklediği ürün görselleri,
* Araştırma ajanları tarafından doğrulanmış referans görseller,
* Ürün Referans Paketi,
* Storyboard,
* Ses dosyaları,
* Video üretim parametreleri,
* Üretim için gerekli diğer dijital varlıklar

dahil edilir.

HLK'nın amacı servis sağlayıcısına daha az veri göndermek değildir.

HLK'nın amacı, servis sağlayıcısının ürünü mümkün olan en doğru ve en yüksek kalitede üretebilmesi için gerekli olan tüm bilgi ve dijital varlıkları eksiksiz sağlamaktır.

Her servis sağlayıcısına gönderilecek bilgi kapsamı, ilgili görevin ihtiyaçlarına göre Task Package Engine tarafından dinamik olarak belirlenir.

---

### Amaç

Bu mimarinin amacı;

* Servis sağlayıcıların üretim kalitesini en üst seviyeye çıkarmak,
* Ürünün doğru temsil edilmesini sağlamak,
* Eksik referans kullanımını önlemek,
* Gereksiz veri aktarımını engellemek,
* Her servis sağlayıcısına görevine uygun en doğru üretim bağlamını sağlamaktır.

---

### Beklenen Sonuç

* HLK yalnızca kaliteli araştırma yapmakla kalmaz, kaliteli üretim için de gerekli üretim bağlamını oluşturur.
* Her servis sağlayıcısı kendi görevine özel hazırlanmış üretim paketi ile çalışır.
* Üretim kalitesini artıracak tüm gerekli dijital varlıklar görev paketine dahil edilir.
* Gereksiz bilgiler servis sağlayıcısına gönderilmez.
* HLK'nın **Bilgi Kalitesi → Üretim Kalitesi** mimari zinciri Architecture Rules içerisinde resmen tanımlanmış olur.

---

## AR-002_49

### Selection Architecture (Seçim Mimarisi)

### Kural

HLK içerisinde gerçekleştirilen tüm seçim işlemleri ortak **Selection Architecture (Seçim Mimarisi)** prensiplerine göre yürütülür.

Bu mimari;

* Uzman Ajan Seçimi,
* Technology Provider (Servis Sağlayıcısı) Seçimi,
* AI Model Seçimi,
* Voice Provider Seçimi,
* Video Provider Seçimi,
* Görsel Araştırma Provider Seçimi,
* Gelecekte sisteme eklenecek diğer tüm seçim mekanizmaları

için ortak seçim standardını oluşturur.

Yeni bir seçim mekanizması geliştirildiğinde farklı bir seçim algoritması oluşturulmaz.

Mevcut Selection Architecture yeniden kullanılır.

Her seçim süreci aşağıdaki ortak prosedürü uygular.

1. Görev analiz edilir.
2. Adaylar belirlenir.
3. Değerlendirme kriterleri uygulanır.
4. En uygun aday veya aday kombinasyonu seçilir.
5. Seçim sonucu kayıt altına alınır.
6. İlgili önbellek (Cache) süresi boyunca aynı seçim yeniden kullanılır.
7. Cache süresi dolduğunda aynı prosedür yeniden çalıştırılır.
8. Yeni değerlendirme sonucunda daha uygun bir aday veya kombinasyon bulunursa kayıt güncellenir ve yeni Cache süresi başlatılır.

Selection Architecture içerisinde kullanılacak değerlendirme kriterleri seçim türüne göre farklılık gösterebilir.

Ancak seçim prosedürü tüm seçim mekanizmalarında ortak olarak uygulanır.

---

### Amaç

Bu mimarinin amacı;

* HLK içerisinde tek bir seçim standardı oluşturmak,
* Kod tekrarını önlemek,
* Mimari bütünlüğü korumak,
* Yeni seçim sistemlerinin kolayca eklenmesini sağlamak,
* Uzman Ajan, Technology Provider ve AI Model seçimlerinde ortak karar mantığı kullanmak,
* Tüm seçim mekanizmalarının aynı anayasal prensiplere göre çalışmasını sağlamaktır.

---

### Beklenen Sonuç

* HLK genelinde ortak bir Selection Architecture kullanılır.
* Farklı seçim algoritmaları geliştirilmez.
* Yeni seçim mekanizmaları mevcut Selection Architecture üzerine inşa edilir.
* Uzman Ajan ve Technology Provider seçimleri aynı anayasal prosedüre göre çalışır.
* Kod sadeleşir.
* Mimari sürdürülebilirliği artar.
* HLK'nın tüm seçim mekanizmaları tek bir anayasal standart altında birleşmiş olur.

---

## AR-002_50

### HLK Premium Card — Kullanıcı Arayüzü Mimarisi

### Kural

HLK içerisinde kullanıcıya gösterilen tüm bilgi, özet, onay, teklif, sonuç ve bildirim ekranları için ortak bir kullanıcı arayüzü mimarisi kullanılır. Bu mimarinin adı **HLK Premium Card**'dır.

HLK Premium Card, HLK sisteminin resmi ve yeniden kullanılabilir kullanıcı arayüzü bileşenidir.

Her HLK Premium Card aşağıdaki standart yerleşim düzenini kullanır:

* Sol üst köşede, kart sınırlarını taşmayacak boyutta HLK karakteri bulunur.
* Üst orta bölümde ekranın ana başlığı bulunur.
* Başlığın hemen altında kullanıcıyı bilgilendiren kısa açıklama metni bulunur.
* Orta bölümde yalnızca ilgili iş akışına ait içerikler gösterilir.
* Alt bölümde yalnızca ilgili ekrana ait işlem butonları bulunur.
* Sayfanın en altında kullanıcıyı bilgilendiren sistem notu yer alır.

HLK Premium Card aşağıdaki ortak tasarım standartlarını kullanır:

* Premium koyu tema
* Ortak renk paleti
* Ortak tipografi
* Ortak ikon yapısı
* Ortak boşluk sistemi
* Ortak kenar yarıçapı
* Ortak buton tasarımı
* Ortak başlık düzeni
* Ortak içerik yerleşimi

Bu mimari aşağıdaki ekranlarda ortak olarak kullanılır:

* Brief Onay Formu
* Senaryo Onay Formu
* Fiyat Teklifi
* Video Hazır Bildirimi
* Revizyon Özeti
* Teslim Bilgilendirmesi
* Gelecekte eklenecek tüm bilgi, özet, teklif ve onay ekranları

Yeni kullanıcı ekranları geliştirilirken HLK Premium Card mimarisi değiştirilmez.

Yalnızca ekranın içerikleri değiştirilir.

HLK Premium Card mimarisinin amacı; HLK'nın tüm kullanıcı arayüzlerinde tek ve tutarlı bir kurumsal tasarım dili oluşturmak, tekrar kullanılabilirliği artırmak, bakım maliyetini azaltmak ve kullanıcı deneyiminde görsel bütünlüğü sağlamaktır.

---

## AR-002_51

### HLK UI Component Library — Kullanıcı Arayüzü Bileşen Kütüphanesi Mimarisi

### Kural

HLK içerisinde kullanılan tüm kullanıcı arayüzü bileşenleri merkezi bir bileşen kütüphanesi olan **HLK UI Component Library** tarafından yönetilir.

HLK UI Component Library, HLK sisteminde tekrar kullanılabilen tüm kullanıcı arayüzü bileşenlerinin tek resmi kayıt ve yönetim noktasıdır.

Her UI bileşeni benzersiz bir **Component ID** ile tanımlanır.

Her Component ID yalnızca tek bir kullanıcı arayüzü bileşenini temsil eder.

Bir UI bileşeni en az aşağıdaki bilgileri içerir:

* Component ID
* Bileşen Adı
* Bileşen Türü
* Açıklama
* Kullanım Amacı
* Kullanıldığı Ekranlar
* Bağımlı Olduğu Bileşenler
* Versiyon
* Durum (Aktif / Geliştirme / Kullanımdan Kaldırıldı)

HLK UI Component Library içerisinde aşağıdaki gibi tekrar kullanılabilir bileşenler bulunabilir:

* HLK Premium Card
* Storyboard Card
* Product Summary Card
* Information Card
* Button
* Icon
* Progress Step Indicator
* Status Badge
* Note Area
* Input Box
* Selection Card
* Dialog Box
* HLK Avatar

Yeni kullanıcı ekranları geliştirilirken mevcut UI bileşenleri öncelikli olarak yeniden kullanılır.

Aynı işlevi yerine getiren yeni bir bileşen oluşturulmadan önce mevcut Component Library kontrol edilir.

Bu mimarinin amacı;

* Tekrar kullanılabilir kullanıcı arayüzü bileşenleri oluşturmak,
* Arayüz geliştirme sürecini hızlandırmak,
* Görsel tutarlılığı korumak,
* Kod tekrarını azaltmak,
* Bakım ve geliştirme maliyetini düşürmek,
* HLK'nın kullanıcı arayüzü mimarisini ölçeklenebilir ve sürdürülebilir hale getirmektir.

---

## AR-002_52

### HLK Design Token Architecture — Tasarım Değişken Sistemi Mimarisi

### Kural

HLK içerisinde kullanılan tüm görsel tasarım değerleri merkezi bir tasarım değişken sistemi olan **HLK Design Token Architecture** tarafından yönetilir.

HLK Design Token Architecture, kullanıcı arayüzünde kullanılan ortak görsel değerlerin tek resmi yönetim standardıdır.

Hiçbir kullanıcı arayüzü bileşeni renk, yazı tipi, yazı boyutu, boşluk, kenar yarıçapı veya benzeri tasarım değerlerini kendi içerisinde sabit (hardcoded) olarak tanımlayamaz.

Tüm kullanıcı arayüzü bileşenleri ortak Design Token değerlerini kullanmak zorundadır.

HLK Design Token sistemi en az aşağıdaki ortak tasarım değişkenlerini içerir:

* Ana Renk (Primary Color)
* İkincil Renk (Secondary Color)
* Başarı Rengi (Success Color)
* Uyarı Rengi (Warning Color)
* Hata Rengi (Error Color)
* Sayfa Arka Plan Rengi
* Kart Arka Plan Rengi
* Yazı Renkleri
* Kenarlık Renkleri
* Yazı Tipi Ailesi
* Başlık Yazı Boyutları
* İçerik Yazı Boyutları
* Satır Yüksekliği
* İç Boşluk (Padding)
* Dış Boşluk (Margin)
* Kenar Yarıçapı (Border Radius)
* Kenarlık Kalınlığı
* İkon Boyutları
* Buton Yüksekliği
* Buton Genişliği
* Gölgelendirme (Shadow)
* Geçiş ve Animasyon Süreleri

Yeni kullanıcı arayüzü bileşenleri geliştirilirken bu değerler doğrudan tanımlanmaz; yalnızca HLK Design Token sistemindeki ortak değişkenler kullanılır.

Herhangi bir tasarım değişikliği gerektiğinde yalnızca Design Token değerleri güncellenir. Bu değişiklik ilgili tüm kullanıcı arayüzü bileşenlerine otomatik olarak uygulanacak şekilde tasarlanmalıdır.

Bu mimarinin amacı;

* Tasarım tutarlılığını sağlamak,
* Hardcoded görsel değerleri ortadan kaldırmak,
* Bakım ve geliştirme maliyetini azaltmak,
* Kurumsal tasarım dilini korumak,
* Gelecekte Web, Mobil ve Telegram arayüzlerinde aynı tasarım standartlarının kullanılmasını sağlamaktır.

---

## AR-002_53

### HLK Ortak Operasyon Veri Merkezi Mimarisi

### Kural

HLK içerisinde operasyonel amaçla üretilen ortak veriler yalnızca bir kez oluşturulur ve sistem genelinde tek doğruluk kaynağı (Single Source of Truth) olarak kullanılır.

Operasyonel verileri üretme yetkisi yalnızca ilgili sorumlu modüle aittir.

Diğer modüller bu verileri yeniden hesaplayamaz, yeniden sorgulayamaz veya farklı değerler üretemez.

Ortak operasyon verileri merkezi operasyon veri yapısında saklanır ve yetkili modüller tarafından paylaşılır.

En az aşağıdaki operasyonel veriler ortak veri olarak yönetilmelidir:

* Servis sağlayıcı bilgileri
* Servis öncelik sıraları
* Kullanılan servis sağlayıcı
* Kullanılmayan servis sağlayıcılar ve gerekçeleri
* API durumları
* API hata bilgileri
* Mevcut kredi durumları
* Tahmini kredi tüketimleri
* Üretim sonrası tahmini kredi durumları
* Kota bilgileri
* Servis sağlık durumları
* Servis Güven Skorları
* Risk seviyeleri
* Tahmini üretim maliyetleri
* Tahmini üretim süreleri
* Servis seçim kararları
* Operasyonel uyarılar
* Yönetici müdahalesi gerektiren durumlar

HLK Servis Sağlığı ve Müdahale Motoru tarafından üretilen operasyon verileri aşağıdaki modüller tarafından ortak veri olarak kullanılmalıdır:

* Servis Seçim Motoru
* Maliyet Hesaplama Motoru
* Fiyatlandırma Motoru
* Reklam Üretim Motoru
* Yönetici Bildirim Sistemi
* Kullanıcı Teklif Sistemi
* Operasyon Kayıt Sistemi
* Raporlama Sistemi
* Analiz ve İstatistik Sistemi

Hiçbir modül ortak operasyon verilerini yeniden üretmemeli veya aynı bilgiyi farklı yöntemlerle tekrar hesaplamamalıdır.

Operasyon verisinde değişiklik gerektiğinde yalnızca verinin sahibi olan modül güncelleme yapabilir.

Veri güncellendiğinde ilgili tüm modüller güncel operasyon verisini kullanmalıdır.

Bu mimarinin amacı;

* HLK içerisinde tek doğruluk kaynağı oluşturmak,
* Aynı verinin farklı modüller tarafından tekrar hesaplanmasını önlemek,
* Tutarsız operasyon verilerinin oluşmasını engellemek,
* API çağrılarını azaltmak,
* Performansı artırmak,
* Modüller arası veri bütünlüğünü sağlamak,
* Operasyonel kararların tutarlılığını korumak,
* HLK'nın ölçeklenebilir ve sürdürülebilir bir mimariye sahip olmasını sağlamaktır.

---

## AR-002_54

### STATE_PRICING Ekran Mimarisi — Yönetici ve Kullanıcı Fiyatlandırma Formları

### Kural

STATE_PRICING aşaması iki ayrı resmi operasyon ekranından oluşur.

**HLK Yönetici Fiyatlandırma Formu** — Yalnızca yönetici tarafından görüntülenebilir.

**HLK Kullanıcı Fiyat Teklif Formu** — Yalnızca kullanıcı tarafından görüntülenebilir.

Her iki ekran HLK Premium Card Architecture, HLK UI Component Library ve HLK Design Token Architecture standartlarını kullanır.

Her iki ekranda sol üst köşede aynı HLK karakteri bulunur.

Her iki ekran aynı renk paletini, aynı ikon yapısını, aynı kart mimarisini, aynı buton tasarımını ve aynı premium görünümü kullanır.

HLK Yönetici Fiyatlandırma Formu en az aşağıdaki bilgileri içermelidir:

* Ürün özeti, marka bilgisi, platform
* Video süresi, çözünürlük, teslim süresi
* Senaryo özeti
* Kullanılan ajanlar ve servis sağlayıcılar
* Kullanılmayan servis sağlayıcılar ve nedenleri
* API durumları
* Servis Güven Skorları
* Mevcut kredi miktarları
* Tahmini kredi tüketimleri
* Üretim sonrası tahmini kredi durumu
* Risk analizi
* Tahmini maliyet ve tahmini üretim süresi
* HLK Operasyon Değerlendirmesi
* HLK önerisi
* Yönetici müdahalesi gerekip gerekmediği

HLK Kullanıcı Fiyat Teklif Formu en az aşağıdaki bilgileri içermelidir:

* Ürün özeti, platform, video süresi
* Çözünürlük, teslim süresi
* Hizmet kapsamı
* Satış fiyatı, para birimi, vergi bilgisi
* Teklif geçerlilik süresi
* Ödeme sonrasında üretimin başlayacağı bilgisi

STATE_PRICING ekran geçiş sırası aşağıdaki gibi olmalıdır:

STATE_SCENARIO_APPROVAL (Kullanıcı Onayı)
↓
HLK Yönetici Fiyatlandırma Formu (Yönetici İşlemi)
↓
HLK Kullanıcı Fiyat Teklif Formu (Kullanıcı İşlemi)
↓
EVENT_PRICING_APPROVED → STATE_VIDEO_PRODUCTION
EVENT_PRICING_REJECTED → STATE_SESSION_CLOSED

Bu mimari mevcut AR-002_44 Scenario Approval Architecture, AR-002_45 Pricing Architecture, AR-002_50 HLK Premium Card, AR-002_51 HLK UI Component Library ve AR-002_52 HLK Design Token Architecture ile tam uyumludur.

Bu mimari mevcut MR-0005_3 HLK Servis Sağlığı ve Müdahale Motoru, MR-0005_4 HLK Operasyon Hafızası ve MR-0005_5 HLK Operasyon Analiz Motoru ile tam uyumludur.

---

## AR-002_55

### Referans UI Tasarım Mimarisi — Reference UI Design Architecture

### Kural

HLK içerisinde yer alan tüm resmi form ve ekranların kullanıcı arayüzü geliştirme süreçleri, önceden onaylanmış resmi **Referans UI Tasarımları (Reference UI Designs)** esas alınarak yürütülür.

Her Referans UI Tasarımı, FORMLAR klasöründe aşağıdaki yapıya sahiptir:

* `REFERANS_*.png` — Referans Formun görsel kaynağı (tek yetkili görsel otorite)
* `template.html` — Kullanıcı arayüzü şablonu
* `sample-data.json` — Örnek veri dosyası
* `render.js` — Kullanıcı arayüzü render mantığı

Buna ek olarak her Referans UI Tasarımı;

* HLK Digital Asset Catalog içerisinde `REF-UI` ön eki ile benzersiz bir Asset ID altında kayıt altına alınır.
* İlgili form veya ekranın resmi tasarım standardıdır.
* Gelecekte yapılacak tüm revizyonların başlangıç noktasıdır.
* Yeni bileşen ekleme, kaldırma ve güncelleme çalışmalarında ana referans olarak kullanılır.
* HLK Premium Card Architecture, HLK UI Component Library ve HLK Design Token Architecture standartlarına uygun olarak değerlendirilir.
* Yalnızca Proje Yöneticisinin onayı ile değiştirilebilir.

HLK, bir form veya ekran geliştireceği zaman;

1. Digital Asset Catalog içerisinde ilgili ekrana ait bir Referans UI Tasarımı (`REF-UI-XXX`) bulunup bulunmadığını kontrol eder.
2. Referans UI Tasarımı bulunuyorsa, ilgili Referans Form klasörünü (`REFERANS_*.png` + `template.html` + `sample-data.json` + `render.js`) eksiksiz analiz eder.
3. Geliştirmeyi bu referans tasarımı esas alarak gerçekleştirir.
4. Referans UI Tasarımı bulunmuyorsa, mevcut HLK Premium Card, HLK UI Component Library ve HLK Design Token Architecture standartlarını kullanarak geliştirme yapar.
5. Yeni oluşturulan ekran için Proje Yöneticisi onayı ile yeni bir Referans UI Tasarımı kaydı oluşturulabilir.

Referans UI Tasarımları aşağıdaki ANA YASA katmanları ile ilişkilendirilir:

* **Digital Asset Catalog (13_DIGITAL_ASSET_CATALOG.md):** Referans UI Tasarımının resmi katalog kaydı.
* **Workflow Manifest (09_WORKFLOW_MANIFEST.md):** İlgili Workflow referansı.
* **Feature Registry (10_FEATURE_REGISTRY.md):** İlgili Feature referansı.
* **State Engine (07_HLK_STATE_ENGINE.md):** İlgili State ve ekran ilişkisi.
* **Workflow Feature Map (11_WORKFLOW_FEATURE_MAP.md):** Workflow-Feature bağımlılık haritası.

Hiçbir geliştirme süreci, mevcut bir Referans UI Tasarımı ile çelişen bir kullanıcı arayüzü üretemez.

Eğer bir geliştirme sürecinde Referans UI Tasarımının güncellenmesi gerektiği tespit edilirse, değişiklik önerisi Proje Yöneticisine sunulur. Proje Yöneticisi onayı olmadan Referans UI Tasarımı üzerinde değişiklik yapılamaz.

---

### Amaç

Bu mimarinin amacı;

* HLK'nın tüm kullanıcı arayüzü geliştirme süreçlerini onaylanmış referans tasarımlara bağlamak,
* Geliştirici veya AI tarafından keyfi arayüz kararları alınmasını önlemek,
* Form ve ekran tasarımlarında görsel ve işlevsel tutarlılığı garanti altına almak,
* Referans UI Tasarımlarının ANA YASA katmanları ile entegrasyonunu sağlamak,
* Proje Yöneticisinin kullanıcı arayüzü üzerindeki nihai onay yetkisini mimari seviyede tanımlamak,
* `template.html` ve `render.js` dosyalarının Referans `.png`'i en yüksek doğrulukla temsil etmesini sağlamak,
* HLK UI Component Library ve HLK Design Token Architecture ile birlikte çalışan tam bir kullanıcı arayüzü yönetim standardı oluşturmaktır.

---

### Beklenen Sonuç

* Her resmi form ve ekran için bir Referans UI Tasarımı ve klasör yapısı bulunur.
* Tüm kullanıcı arayüzü geliştirmeleri onaylanmış referans tasarımlara dayanır.
* Keyfi arayüz değişiklikleri mimari seviyede engellenir.
* Referans UI Tasarımları Digital Asset Catalog üzerinden aranabilir ve listelenebilir.
* Proje Yöneticisi, kullanıcı arayüzü değişikliklerini tek noktadan kontrol edebilir.
* HLK Premium Card, HLK UI Component Library, HLK Design Token Architecture ve Referans UI Tasarımları birlikte çalışarak tam bir kullanıcı arayüzü yönetim ekosistemi oluşturur.

---

## AR-002_56

### Yönetici Video Üretim Onay Katmanı — Admin Video Production Approval Layer

### Kural

HLK, Video Production sürecini başlatmadan önce oluşturduğu üretim paketini **Yönetici Video Üretim Onay Formu** üzerinden Proje Yöneticisinin onayına sunmak zorundadır.

Yönetici onayı alınmadan hiçbir Video Production süreci başlatılamaz.

Bu form;

* üretim güvenliği,
* operasyonel doğrulama,
* üretim referansı,
* son insan kontrolü

katmanı olarak çalışır.

HLK, STATE_PAYMENT_VERIFICATION aşamasında EVENT_PAYMENT_APPROVED oluştuktan sonra STATE_VIDEO_PRODUCTION state'ine geçmeden önce:

1. Üretim paketini oluşturur.
2. Benzersiz bir **Production Reference ID** üretir.
3. Yönetici Video Üretim Onay Formunu hazırlar.
4. Formu yalnızca Proje Yöneticisine gönderir.
5. Yönetici onayını bekler.
6. Onay alındıktan sonra Video Production sürecini başlatır.

Yönetici Video Üretim Onay Formu, HLK Premium Card Architecture, HLK UI Component Library ve HLK Design Token Architecture standartlarını kullanır.

Bu formun resmi referans tasarımı Digital Asset Catalog içerisinde `REF-UI-004` Asset ID'si ile kayıtlıdır ve `FORMLAR/REFERANS_YÖNETİCİ_VİDEO_ÜRETİM_ONAY_FORMU.png` konumunda bulunur.

---

### Production Reference ID

HLK, Video Production sürecine giren her üretim için benzersiz bir **Production Reference ID** oluşturur.

Production Reference ID formatı:

```
PR-YYYYMMDD-NNNN
```

| Bileşen | Açıklama | Örnek |
|---|---|---|
| `PR` | Production Reference ön eki | PR |
| `YYYYMMDD` | Üretim onay tarihi (yıl-ay-gün) | 20260701 |
| `NNNN` | Sıfır dolgulu 4 haneli günlük sıra numarası (0001'den başlar) | 0001 |

Örnek: `PR-20260701-0001`

Bu kimlik;

* üretim paketi,
* log kayıtları,
* maliyet kayıtları,
* servis kullanımları,
* teslim edilen video,
* kalite raporları

ile ilişkilendirilecek tek resmi üretim referansıdır.

Her Production Reference ID yalnızca bir üretim paketini temsil eder.

Aynı Production Reference ID birden fazla üretim için kullanılamaz.

Production Reference ID, üretim süreci boyunca tüm sistem bileşenleri tarafından ortak referans olarak kullanılır.

---

### Yasaklar

Yönetici Video Üretim Onay Formu onaylanmadan aşağıdakiler kesinlikle yasaktır:

* Video üretim görevlerini oluşturmak
* Servis sağlayıcılara üretim talebi göndermek
* Kredi tüketimini başlatmak
* STATE_VIDEO_PRODUCTION state'ine geçmek
* Kullanıcıya üretimin başladığını bildirmek

---

### Amaç

Bu mimarinin amacı;

* Video Production başlamadan önce zorunlu bir insan kontrol katmanı oluşturmak,
* Yanlış üretimi ve gereksiz kredi tüketimini önlemek,
* Her üretimi benzersiz bir Production Reference ID ile izlenebilir hale getirmek,
* Üretim paketinin doğruluğunu Proje Yöneticisi onayı ile garanti altına almak,
* HLK'nın ticari üretim sürecinde son kararın insanda olduğunu mimari seviyede tanımlamak,
* Üretim, log, maliyet ve kalite kayıtlarının tek bir referans kimlik etrafında birleşmesini sağlamaktır.

---

### Beklenen Sonuç

* Her Video Production süreci öncesinde Yönetici Video Üretim Onay Formu çalıştırılır.
* Onaysız hiçbir üretim başlatılamaz.
* Her üretim benzersiz bir Production Reference ID ile kayıt altına alınır.
* Production Reference ID, tüm üretim süreci bileşenleri için ortak referans haline gelir.
* Yanlış üretim ve gereksiz kredi tüketimi riski mimari seviyede azaltılır.
* HLK'nın üretim süreci tamamen izlenebilir ve denetlenebilir hale gelir.

---

## AR-002_57

### Production ID (PID) Mimari Standardı — Production ID Architecture Standard

### Kural

HLK içerisinde oluşturulan her üretim için tek resmi üretim kimliği **PID (Production ID)**'dir.

PID, AR-002_56 kapsamında tanımlanan Production Reference ID kavramının sistem genelindeki resmi kısa adıdır. Production Reference ID kavramı geçerliliğini korur; PID bu kavramın standartlaştırılmış kısa adı olarak tüm sistem bileşenleri tarafından kullanılır.

PID;

* üretim paketini,
* workflow'u,
* event kayıtlarını,
* agent loglarını,
* video dosyalarını,
* kalite raporlarını,
* servis kullanım kayıtlarını,
* kredi tüketim kayıtlarını,
* teslim kayıtlarını,
* kullanıcı geçmişini,
* olay kayıt merkezi kayıtlarını

ve gelecekte üretim ile ilişkili tüm modülleri birbirine bağlayan **ortak referans anahtarıdır.**

---

### PID Formatı

```
PID-YYYYMMDD-NNNN
```

| Bileşen | Açıklama | Örnek |
|---|---|---|
| `PID` | Production ID ön eki | PID |
| `YYYYMMDD` | Üretim onay tarihi (yıl-ay-gün) | 20260701 |
| `NNNN` | Sıfır dolgulu 4 haneli günlük sıra numarası (0001'den başlar) | 0001 |

Örnek: `PID-20260701-0001`

---

### PID Oluşturulma Anı

PID, STATE_VIDEO_PRODUCTION state'ine girişte, Video Production süreci başlamadan hemen önce, Yönetici Video Üretim Onay Formu onaylandıktan sonra HLK tarafından otomatik olarak oluşturulur.

PID oluşturulduğu andan itibaren;

* Production Package kaydına yazılır,
* İlgili Workflow adımlarına ilişkilendirilir,
* State Engine state geçişlerine kaydedilir,
* Tüm Event loglarına eklenir,
* Tüm Agent loglarına eklenir,
* Üretilen video dosyalarına ilişkilendirilir,
* Kalite raporlarına yazılır,
* Servis kullanım kayıtlarına eklenir,
* Kredi tüketim kayıtlarına ilişkilendirilir,
* Teslim kayıtlarına yazılır,
* Olay Kayıt Merkezi'ndeki ilgili tüm event kayıtlarına zorunlu alan olarak eklenir.

---

### PID Zorunluluk Kuralı

PID, üretim ile ilgili tüm event kayıtlarının **zorunlu alanıdır.**

PID alanı boş veya null olan hiçbir üretim event'i geçerli kabul edilmez.

Aşağıdaki event'ler için PID alanı zorunludur:

* `EVENT_VIDEO_PRODUCTION_STARTED`
* `EVENT_VIDEO_PRODUCTION_COMPLETED`
* `EVENT_VIDEO_PRODUCTION_FAILED`
* `EVENT_REVISION_REQUESTED`
* `EVENT_REVISION_COMPLETED`

Gelecekte eklenecek tüm üretim event'leri için de PID alanı zorunlu olacaktır.

---

### PID Tekillik Kuralı

Her PID yalnızca bir üretim paketini temsil eder.

Aynı PID birden fazla üretim için kullanılamaz.

PID değiştirilemez. Bir kez oluşturulan PID, üretim yaşam döngüsü boyunca sabit kalır.

PID silinemez. Üretim kayıtları arşivlense dahi PID bilgisi korunur.

---

### PID Merkeziyet Kuralı

Hiçbir modül kendi üretim kimliğini oluşturamaz.

PID yalnızca HLK tarafından, STATE_VIDEO_PRODUCTION girişinde, merkezi olarak oluşturulur.

Tüm modüller, servisler, ajanlar ve sistem bileşenleri ortak PID'yi kullanmak zorundadır.

---

### Amaç

Bu mimarinin amacı;

* HLK içerisinde oluşturulan her üretimi benzersiz ve standart bir kimlik ile tanımlamak,
* Tüm üretim süreci bileşenlerini tek bir ortak referans anahtarı etrafında birleştirmek,
* Üretim yaşam döngüsünün tamamını izlenebilir ve denetlenebilir hale getirmek,
* Event kayıtları, agent logları, maliyet kayıtları ve kalite raporları arasında çapraz referanslamayı mümkün kılmak,
* Gelecekte eklenecek tüm üretim modüllerinin aynı kimlik standardını kullanmasını sağlamak,
* Production Reference ID kavramının sistem genelinde kısa ve standart bir adla (PID) kullanılmasını sağlamaktır.

---

### Beklenen Sonuç

* Her üretim benzersiz bir PID ile başlatılır.
* PID, üretim yaşam döngüsünün tüm aşamalarında ortak referans anahtarı olarak kullanılır.
* Event kayıtlarında PID alanı zorunlu hale gelir.
* Hiçbir modül kendi üretim kimliğini oluşturamaz.
* Üretim, log, maliyet ve kalite kayıtları PID üzerinden çapraz sorgulanabilir hale gelir.
* Production Reference ID kavramı korunur; sistem genelinde PID kısa adı ile standartlaştırılır.

---

## AR-002_58

### Production Package Architecture — Üretim Paketi Mimarisi

### Kural

HLK içerisinde oluşturulan her PID için tek bir **Production Package (Üretim Paketi)** oluşturulur.

Production Package; o üretime ait tüm bilgi, dijital varlık, Task Package'ler, loglar ve çıktıların resmi ana kapsayıcısıdır.

Production Package mimarisi aşağıdaki hiyerarşiyi tanımlar:

```
PID (Production ID)
    ↓
Production Package
    ↓
Task Package (Agent'lar için)
    ↓
Agent
```

Bu hiyerarşide:

* **PID**, üretimin benzersiz kimliğidir (AR-002_57).
* **Production Package**, PID'ye bağlı tüm üretim bileşenlerinin ana kapsayıcısıdır.
* **Task Package**, her Agent için özel olarak hazırlanan görev paketidir (AR-002_47).
* **Agent**, yalnızca kendi Task Package'ine erişebilir.

Production Package, STATE_VIDEO_PRODUCTION girişinde, PID oluşturulduktan hemen sonra HLK tarafından otomatik olarak oluşturulur.

Production Package'in tam yapısı, içeriği ve yaşam döngüsü **16_PRODUCTION_PACKAGE_STANDARD.md** dosyasında tanımlanmıştır.

---

### Temel Kurallar

* Her PID yalnızca bir adet Production Package oluşturabilir.
* Her Production Package yalnızca bir PID'ye bağlıdır.
* Production Package silinemez; arşivlenebilir.
* Task Package yapısı korunur; Production Package, Task Package'lerin üst katmanıdır.
* Hiçbir Agent Production Package'in tamamına erişemez.
* Production Package'in tamamına yalnızca HLK erişebilir.

---

### Amaç

Bu mimarinin amacı;

* PID ile başlayan üretim sürecinin tüm bileşenlerini tek bir ana kapsayıcı altında toplamak,
* Task Package'leri Production Package'in alt bileşeni olarak konumlandırmak,
* Üretime ait tüm bilgi, varlık, log ve çıktıların PID üzerinden ilişkilendirilmesini sağlamak,
* Veri izolasyonunu koruyarak modüler mimariyi güçlendirmek,
* Digital Asset Archive, Olay Kayıt Merkezi ve Karar Gerekçesi Standardı ile entegrasyonu sağlamaktır.

---

### Beklenen Sonuç

* Her üretim için bir Production Package oluşturulur.
* Production Package, üretim yaşam döngüsünün ana kapsayıcısı haline gelir.
* Task Package'ler Production Package altında organize edilir.
* Agent'lar yalnızca kendi Task Package'lerine erişir; veri izolasyonu korunur.
* PID → Production Package → Task Package → Agent hiyerarşisi sistem genelinde standart hale gelir.

---

## AR-002_59

### Live Activity Center (LAC) Architecture — Canlı Aktivite Merkezi Mimarisi

### Kural

HLK içerisinde yöneticiye sunulan tüm canlı sistem izleme arayüzleri için ortak bir mimari kullanılır. Bu mimarinin adı **Live Activity Center (LAC)** — **Canlı Aktivite Merkezi**'dir.

Live Activity Center, HLK sisteminin resmi Yönetici Operasyon Ekranıdır.

LAC'nin amacı; kullanıcının `/start` komutunu verdiği andan başlayarak oturum tamamen sonlanıncaya kadar HLK içerisinde oluşan tüm gerçek Event'leri, karar süreçlerini ve operasyonel akışı yöneticiye şeffaf şekilde sunmaktır.

LAC yalnızca gerçek Event'leri gösterir. Fake Progress (sahte ilerleme) kullanmaz.

LAC, HLK'nın tüm oturum yaşam döngüsünü (Session Lifecycle) gerçek zamanlı izleyen tek resmi operasyon ekranıdır.

---

### LAC Temel Prensipleri

1. **PID tek referanstır.** LAC üzerinde gösterilen tüm bilgiler PID üzerinden ilişkilendirilir.
2. **Production Package ana veri kaynağıdır.** LAC, gösterdiği tüm bilgileri Production Package'ten alır.
3. **Yalnızca gerçek Event'ler gösterilir.** LAC hiçbir şekilde Fake Progress kullanmaz.
4. **Yönetici yalnızca izleyicidir.** LAC üzerinden HLK karar mekanizmasına müdahale edilemez.
5. **Gerçek zamanlı izleme.** LAC, `/start` anından oturum kapanışına kadar tüm oturum yaşam döngüsünü canlı olarak takip eder.

---

### LAC Operasyon Katmanı Tanımı

LAC yeni bir Workflow değildir.

LAC; mevcut Workflow'ları izleyen, Workflow üretmeyen, Workflow çalıştırmayan bir **operasyon izleme katmanıdır.**

LAC yalnızca Yönetici Operasyon Ekranıdır.

Son kullanıcı tarafından kullanılmaz.

Yönetici yalnızca izleyicidir.

HLK'nın Workflow'una, State Engine'ine, Agent'larına ve karar mekanizmasına müdahale edemez.

LAC'nin görevi:

* Kullanıcının `/start` komutundan itibaren tüm oturum yaşam döngüsünü izlemek,
* Oturum boyunca oluşan tüm State geçişlerini gerçek zamanlı göstermek,
* Mevcut Workflow adımlarını gerçek zamanlı okumak,
* Oturum, Workflow ve PID'ye bağlı tüm Event'leri kronolojik olarak sunmak,
* Production Package içeriğini yöneticiye şeffaf şekilde göstermek,
* HLK karar gerekçelerini ve ajan seçimlerini incelemeye sunmak,
* Dijital varlık oluşturma ve arşivleme süreçlerini göstermek,
* Kalite kontrol ve teslim süreçlerini izlemek,
* Yöneticiye oturumun tamamını izlenebilir kılmaktır.

LAC'nin görevi değildir:

* Yeni bir Workflow adımı oluşturmak,
* Mevcut bir Workflow adımını değiştirmek,
* State geçişi başlatmak,
* Ajan görevlendirmek veya değiştirmek,
* HLK karar mekanizmasını etkilemek.

---

### LAC Kapsamı — Session Lifecycle

LAC yalnızca Video Production sürecini değil; kullanıcının `/start` komutunu verdiği andan oturumun tamamen sonlandığı ana kadar HLK'nın tüm yaşam döngüsünü kapsayan merkezi operasyon ekranıdır.

LAC aşağıdaki katmanları kapsar:

| # | Katman | Açıklama |
|---|--------|----------|
| 1 | **Session** | Oturum başlangıcı, dil seçimi, oturum zaman aşımı, oturum kapanışı |
| 2 | **Workflow** | Tüm Workflow adımlarının gerçek zamanlı ilerleme durumu (WF-001..WF-011) |
| 3 | **State** | Kullanıcı State geçişleri ve mevcut State bilgisi |
| 4 | **Agent** | Ajan seçimleri, puanlamalar, öncelik sıralamaları, başarı/başarısızlık durumları |
| 5 | **Event** | Oturum boyunca oluşan tüm gerçek Event'lerin kronolojik akışı |
| 6 | **Decision** | HLK'nın verdiği tüm kararlar, gerekçeleri ve değerlendirilen alternatifler |
| 7 | **Service** | HLK tarafından kullanılan tüm harici ve dahili servislerin gerçek zamanlı operasyon durumu |
| 8 | **Digital Asset** | Oluşturulan, kullanılan ve arşivlenen tüm dijital varlıklar |
| 9 | **Production Package** | PID'ye bağlı üretim paketi içeriği ve Task Package durumu |
| 10 | **Video Production** | Video üretim süreci, servis kullanımları, kredi tüketimi |
| 11 | **Quality Control** | Kalite kontrol sonuçları ve doğrulama raporları |
| 12 | **Delivery** | Kullanıcıya teslim süreci ve teslim durumu |
| 13 | **Archive** | Oturumun arşivlenmesi, Digital Asset Archive kaydı |

LAC bu katmanların her biri için yalnızca gerçek sistem olaylarını gösterir.

Yönetici isterse açılır / kapanır yapı sayesinde ilgili aşamanın tüm detaylarını inceleyebilir.

---

### Service Katmanı

Service katmanı, HLK tarafından kullanılan tüm harici ve dahili servislerin gerçek zamanlı operasyon durumunu gösterir.

Service katmanı yalnızca izleme amaçlıdır.

Yönetici servisleri başlatamaz, durduramaz veya yapılandıramaz.

Yönetici yalnızca servis durumlarını izler.

Service katmanında en az aşağıdaki bilgiler gösterilir:

* Servis Adı
* Durum (Aktif / Pasif / Hata)
* Kullanılan Model veya Sürüm
* API Durumu
* Kredi / Kota Durumu
* Gecikme Süresi (Latency)
* Son Hata Bilgisi
* Son Kontrol Zamanı

Desteklenen servisler mimariye bağlı olarak genişleyebilir.

Örnek servisler:

* OpenAI
* Claude
* Gemini
* ElevenLabs
* Hedra
* FFmpeg
* Telegram
* Railway
* PostgreSQL
* Redis
* Image API
* Gelecekte eklenecek diğer servisler

Service katmanı, LAC'ın diğer katmanlarıyla aynı açılır / kapanır mimariyi kullanır.

Service katmanı; MR-0005_3 (HLK Servis Sağlığı ve Müdahale Motoru) ve AR-002_53 (HLK Ortak Operasyon Veri Merkezi Mimarisi) ile tam uyumlu çalışır.

---

### LAC Referans Tasarımı

LAC; Desktop ve Mobile referans tasarımlarını içeren tek resmi Referans UI Tasarımı olarak tanımlanır.

LAC'nin resmi referans tasarımı Digital Asset Catalog içerisinde `REF-UI-005` Asset ID'si ile kayıtlıdır ve `FORMLAR/REFERANS_HLK_LIVE_ACTIVITY_CENTER(LAC).png` konumunda bulunur.

LAC; HLK Premium Card Architecture (AR-002_50), HLK UI Component Library (AR-002_51), HLK Design Token Architecture (AR-002_52) ve Referans UI Tasarım Mimarisi (AR-002_55) standartlarını kullanır.

---

### LAC Bileşenleri

LAC aşağıdaki temel kullanıcı arayüzü bileşenlerinden oluşur:

* **Oturum Listesi (Session List):** Sistemdeki aktif ve geçmiş oturumların listelendiği ana görünüm. Her oturum kullanıcı, dil, başlangıç zamanı ve durum bilgisi ile gösterilir.
* **PID Listesi:** Oturuma bağlı veya bağımsız olarak sistemdeki aktif ve geçmiş PID'lerin listelendiği görünüm.
* **Canlı İzleme Paneli:** Seçili oturumun veya PID'nin gerçek zamanlı ilerlemesini gösteren ana panel.
* **State Akışı (State Flow):** Oturum boyunca gerçekleşen tüm State geçişlerinin görsel akışı.
* **Workflow İlerleme Göstergesi:** Tüm Workflow adımlarının gerçek zamanlı durumunu gösteren görsel bileşen.
* **Açılır / Kapanır Adım Detayı (Expandable Step Detail):** İlgili katman veya adımın tüm detaylarını görüntülemeyi sağlayan genişletilebilir yapı.
* **Event Akışı (Event Feed):** Oturum veya PID'ye bağlı gerçek Event'lerin kronolojik listesi.
* **Karar Gerekçesi Paneli:** HLK'nın verdiği kararların gerekçelerini ve değerlendirilen alternatifleri gösteren panel.
* **Ajan Seçim Paneli:** İlgili adımda seçilen ve kullanılan ajanların listesi, puanlama ve durum bilgileriyle.
* **Servis Durum Paneli:** HLK tarafından kullanılan tüm harici ve dahili servislerin API durumu, kredi/kota, gecikme süresi ve hata bilgilerini gösteren panel.
* **Dijital Varlık Paneli:** Oturum boyunca oluşturulan ve kullanılan dijital varlıkların listesi.
* **Log Paneli:** Oturum veya PID'ye bağlı sistem loglarının filtrelenebilir görünümü.
* **Durum Göstergesi (Status Indicator):** Her katmanın gerçek zamanlı durumunu gösteren görsel bileşen.
* **Arşiv Görünümü:** Tamamlanmış oturum ve üretimlerin arşiv kayıtları.

---

### Yönetici Deneyimi

LAC yöneticiye aşağıdaki yetenekleri sağlar:

* **Tüm oturumları canlı izleme.** Yönetici, sistemdeki tüm aktif oturumların listesini görüntüleyebilir.
* **Seçili oturumu gerçek zamanlı takip etme.** Yönetici istediği oturumu seçerek `/start` anından itibaren tüm yaşam döngüsünü canlı izleyebilir.
* **Yeni PID oluştuğunda bildirim alma.** Yönetici, yeni bir üretim başladığında otomatik olarak bilgilendirilir.
* **İstediği PID oturumunu canlı izleme.** Yönetici istediği PID'yi seçerek canlı izleme başlatabilir.
* **State geçişlerini takip etme.** Yönetici, oturum boyunca gerçekleşen tüm State geçişlerini görsel akış olarak izleyebilir.
* **Açılır / kapanır yapı sayesinde ilgili katmanın tüm detaylarını görüntüleme.** Her katman ve adım genişletilebilir yapıda olup, detaylı bilgi sunar.
* **HLK'nın karar gerekçelerini inceleme.** Yönetici, HLK'nın verdiği tüm kararların gerekçelerini ve değerlendirilen alternatifleri görebilir.
* **Ajan seçimlerini inceleme.** Yönetici, hangi ajanların hangi kriterlere göre seçildiğini, puanlamaları ve durumlarını görebilir.
* **Event'leri ve Log kayıtlarını inceleme.** Yönetici, oturum veya PID'ye bağlı tüm Event ve Log kayıtlarını görüntüleyebilir.
* **Dijital varlıkları ve arşiv kayıtlarını görüntüleme.** Yönetici, oturum boyunca oluşturulan tüm dijital varlıkları ve arşiv kayıtlarını listeleyebilir.
* **Tamamlanmış oturumların arşivini inceleme.** Yönetici, geçmiş oturum ve üretimlerin arşiv kayıtlarına erişebilir.

---

### Yönetici Kısıtlamaları

LAC üzerinde yönetici yalnızca izleyici konumundadır:

* Yönetici, HLK karar mekanizmasına müdahale edemez.
* Yönetici, aktif bir Workflow adımını değiştiremez.
* Yönetici, ajan seçimini veya öncelik sıralamasını LAC üzerinden değiştiremez.
* Yönetici, Event veya Log kayıtlarını silemez veya değiştiremez.
* Yönetici, PID'yi silemez veya değiştiremez.

LAC bir izleme aracıdır; yönetim aracı değildir.

---

### LAC ve Sistem Bileşenleri Entegrasyonu

LAC aşağıdaki HLK sistem bileşenleri ile tam uyumlu çalışır:

* **Session (Genel Kurallar):** LAC, `/start` anından oturum kapanışına kadar tüm oturum yaşam döngüsünü izler.
* **State Engine (07_HLK_STATE_ENGINE.md):** LAC, tüm State geçişlerini gerçek zamanlı olarak gösterir.
* **Workflow Manifest (09_WORKFLOW_MANIFEST.md):** LAC, tüm Workflow adımlarını buradan okur ve durumlarını gösterir.
* **PID (AR-002_57):** LAC için üretim sürecindeki tek referans anahtarıdır.
* **Production Package (AR-002_58, 16_PRODUCTION_PACKAGE_STANDARD.md):** LAC'nin üretim verisi ana kaynağıdır.
* **Task Package Engine (AR-002_47):** LAC, Task Package oluşturma ve ajan görevlendirme süreçlerini gösterir.
* **Servis Sağlığı ve Müdahale Motoru (MR-0005_3):** LAC, tüm servislerin operasyonel durumunu gerçek zamanlı gösterir.
* **Ortak Operasyon Veri Merkezi (AR-002_53):** LAC, servis durum verilerini bu merkezi kaynaktan alır.
* **Olay Kayıt Merkezi (14_OLAY_KAYIT_MERKEZI.md):** LAC, tüm Event'leri bu standart formatta kronolojik olarak gösterir.
* **Karar Gerekçesi Standardı (15_KARAR_GEREKCESI_STANDARDI.md):** LAC, tüm karar gerekçelerini bu formatta sunar.
* **Digital Asset Archive (12_DIGITAL_ASSET_ARCHIVE.md):** LAC, dijital varlıkların arşiv kayıtlarını gösterir.
* **Digital Asset Catalog (13_DIGITAL_ASSET_CATALOG.md):** LAC, dijital varlıkların katalog kayıtlarını listeler.
* **Production Optimization (AR-002_48):** LAC, servis sağlayıcı kullanımını ve kredi tüketimini gösterir.
* **Quality Rules (05_Quality_Rules.md):** LAC, kalite kontrol ve doğrulama sonuçlarını gösterir.
* **Operational Rules (04_Operational_Rules.md):** LAC, operasyonel durum ve bildirimleri gösterir.

---

### LAC Yaşam Döngüsü

LAC aşağıdaki yaşam döngüsünü izler:

```
Kullanıcı /start Komutunu Verdi
↓
Oturum Başlatıldı (OLAY-001)
↓
LAC Oturum Listesinde Görünür Hale Geldi
↓
Yönetici LAC Oturumunu Açtı (EVENT_LAC_OPENED)
↓
Yönetici İzlenecek Oturumu / PID'yi Seçti (EVENT_LAC_PID_SELECTED)
↓
Gerçek Zamanlı Session Lifecycle İzleme Başladı
  ├─ State Geçişleri Canlı Güncelleniyor
  ├─ Workflow Adımları Canlı Güncelleniyor
  ├─ Event Akışı Sürekli Güncelleniyor
  ├─ Ajan Seçimleri ve Kararlar Gösteriliyor
  └─ Dijital Varlıklar ve Log'lar Erişilebilir
↓
Oturum Tamamlandı / Oturum Kapandı (OLAY-028)
↓
LAC Oturum Kaydı Arşivlendi
```

---

### Yasaklar

LAC üzerinde aşağıdakiler kesinlikle yasaktır:

* Fake Progress (sahte ilerleme) göstermek
* Gerçekleşmemiş Event'leri göstermek
* Yöneticiye müdahale yetkisi vermek
* HLK karar mekanizmasına müdahale etmek
* PID olmadan LAC oturumu başlatmak
* Production Package dışındaki kaynaklardan veri göstermek
* Event veya Log kayıtlarını değiştirmek veya silmek

---

### Amaç

Bu mimarinin amacı;

* HLK yöneticisine, `/start` anından oturum kapanışına kadar tüm oturum yaşam döngüsünü kapsayan gerçek zamanlı, şeffaf ve müdahalesiz bir izleme arayüzü sunmak,
* Session, Workflow, State, Agent, Event, Decision, Service, Digital Asset, Production Package, Video Production, Quality Control, Delivery ve Archive katmanlarını tek merkezi ekranda toplamak,
* Tüm oturum ve üretim sürecini izlenebilir hale getirmek,
* HLK'nın karar süreçlerini yöneticiye açıklamak,
* Fake Progress'i mimari seviyede yasaklamak,
* Yönetici ile HLK arasındaki yetki sınırını mimari seviyede tanımlamak,
* LAC'nin Desktop ve Mobile için tek bir resmi referans tasarım standardı oluşturmak,
* HLK'nın tüm sistem bileşenleri ile tam uyumlu, yeniden kullanılabilir bir merkezi operasyon izleme mimarisi oluşturmaktır.

---

### Beklenen Sonuç

* HLK Live Activity Center, `/start` anından oturum kapanışına kadar tüm oturum yaşam döngüsünü izleyen merkezi operasyon ekranı olarak tanımlanmış olur.
* LAC; Session, Workflow, State, Agent, Event, Decision, Service, Digital Asset, Production Package, Video Production, Quality Control, Delivery ve Archive olmak üzere 13 katmanı kapsar.
* Her oturum ve PID için LAC üzerinden canlı izleme başlatılabilir.
* Yönetici, HLK'nın tüm karar süreçlerini şeffaf şekilde izleyebilir.
* Fake Progress mimari seviyede yasaklanmış olur.
* LAC; Session, PID, Production Package, Workflow, State Engine, Event System, Olay Kayıt Merkezi ve tüm ANA YASA katmanları ile tam uyumlu çalışır.
* LAC referans tasarımı Digital Asset Catalog'da kayıt altına alınmış olur.
* Yöneticinin izleyici rolü mimari seviyede tanımlanmış olur.
* LAC, HLK'nın tüm yaşam döngüsünü (Session Lifecycle) gerçek zamanlı izleyen tek resmi operasyon ekranı haline gelir.

---

## AR-002_60

### Constitution Enforcement Engine (CEE) Mimarisi

### Başlık

Constitution Enforcement Engine — HLK Anayasal Uygulatma Katmanı

### Kural

HLK içerisinde Constitution Enforcement Engine (CEE), Executor (Claude) ile Decision Engine arasında konumlanan **zorunlu geçiş katmanıdır.**

CEE üç fazda çalışır:

1. **PRE-CHECK (FAZ-1):** Executor göreve başlamadan önce ilgili tüm anayasa maddelerini toplar, anayasal görev paketi (CTP) oluşturur ve Executor'a iletir. Executor yalnızca CTP kapsamındaki işlemleri yapabilir.

2. **EXECUTE (FAZ-2):** Executor CTP'yi uygular. CEE bu fazda pasiftir.

3. **POST-CHECK (FAZ-3):** Executor işlemi tamamladığında CEE devreye girer. 6 boyutlu anayasal denetim (Kod-Anayasa Karşılaştırması, Flow Diagram Uyumu, State Engine Uyumu, Operational Rules Uyumu, Mimari Bütünlük, Runtime Davranış) uygular ve PASS veya FAIL kararı verir.

CEE'nin temel kuralları:

- **CEE-001:** CEE olmadan hiçbir geliştirme görevi başlayamaz ve tamamlanamaz.
- **CEE-002:** Executor yalnızca CTP kapsamında işlem yapabilir. Kapsam dışı işlemler otomatik FAIL'dir.
- **CEE-003:** "Değiştirilmez" işaretli alanlara müdahale anında FAIL ile sonuçlanır.
- **CEE-004:** CEE PASS olmadan görev TAMAMLANDI kabul edilemez (MASTER-003 operasyonel uygulaması).
- **CEE-005:** 3 FAIL döngüsünden sonra görev Proje Yöneticisine eskalasyon olarak iletilir.

CEE, HLK içerisinde **PASS ve FAIL verme yetkisine sahip tek katmandır.** CSE, CDE, Task Engine ve diğer katmanlar PASS/FAIL üretemez. Bu yetki münhasıran CEE'ye aittir.

CEE'nin Decision Engine, Constitutional Validator, CSE, CDE, Task Engine ve Feedback Loop ile entegrasyonu 21_CONSTITUTION_ENFORCEMENT_ENGINE.md'de detaylı olarak tanımlanmıştır.

### Amaç

Bu mimarinin amacı;

* HLK'nın "öneri veren" bir sistem olmaktan çıkıp "uygulatan, denetleyen, kabul eden, reddeden" anayasal otorite haline gelmesini sağlamak,
* Executor'un (Claude) hiçbir zaman karar verici olamayacağını mimari seviyede garanti etmek,
* Anayasaya uymayan hiçbir geliştirmenin kalıcı hale gelmesini engellemek,
* Eksik veya hatalı uygulamaları otomatik tespit edip düzeltilene kadar reddetmek,
* Geliştirme sürecini HLK'nın anayasal denetimi altında kontrollü şekilde yürütmek,
* CEE'yi HLK'nın anayasal otoritesinin Executor üzerindeki operasyonel karşılığı haline getirmektir.

### Beklenen Sonuç

* CEE, HLK'nın anayasal uygulatma katmanı olarak tanımlanmış olur.
* Executor (Claude) yalnızca uygulayıcı olarak çalışır; karar verme yetkisi yoktur.
* Tüm geliştirmeler CEE PRE-CHECK ve POST-CHECK zorunlu geçiş noktalarından geçer.
* Anayasa dışı geliştirmeler otomatik reddedilir ve Executor'a geri gönderilir.
* PASS/FAIL yetkisi münhasıran CEE'dedir.
* HLK; karar veren, uygulatan, denetleyen ve onaylayan tek anayasal otorite olarak çalışır.

---

## AR-002_61

### Execution Event Collector (EEC) Mimarisi

### Başlık

Execution Event Collector — Gerçek Zamanlı Executor Event Toplama ve LAC Entegrasyonu

### Kural

HLK içerisinde Execution Event Collector (EEC), Executor (Claude) ile Olay Kayıt Merkezi arasında konumlanan **Event dönüştürme ve toplama katmanıdır.**

EEC üç aşamalı çalışır:

1. **LISTEN:** Executor'un her anlamlı işlemini (dosya açma, kod güncelleme, tarama başlatma, test çalıştırma) dinler.

2. **TRANSFORM:** Her işlemi Olay Kayıt Merkezi standardında bir Event'e dönüştürür. PID, zaman damgası, süre, ilgili dosya ve ExecutorID ekler.

3. **REGISTER:** Dönüştürülen Event'i Olay Kayıt Merkezi'ne kaydeder. LAC bu Event'i anlık olarak okur ve görüntüler.

EEC'nin temel kuralları:

- **EEC-001:** EEC yalnızca gerçek Event üretir. Fake Progress kesinlikle yasaktır.
- **EEC-002:** Her Event PID ile ilişkilendirilir. PID'siz Event kaydedilemez.
- **EEC-003:** LAC yalnızca Olay Kayıt Merkezi'ni okur; Event üretmez.
- **EEC-004:** Event'ler kronolojik sırayla kaydedilir.
- **EEC-005:** PASS Event'i oluşturulmadan önce Constitution Scan ve Runtime Test tamamlanmış olmalıdır.

EEC 6 kategoride 28 Event tipi tanımlar: Görev Yönetimi (3), Anayasa Tarama (10), Dosya İşlem (4), Kod Geliştirme (5), Denetim (6). Tüm Event'ler OLAY-076 — OLAY-103 aralığında Olay Kayıt Merkezi'ne kaydedilir.

EEC'nin Decision Engine, CEE, Task Engine, Executor, CSE, CDE, Olay Kayıt Merkezi ve LAC ile entegrasyonu 22_EXECUTION_EVENT_COLLECTOR.md'de detaylı olarak tanımlanmıştır.

### Amaç

Bu mimarinin amacı;

* Executor'un (Claude) gerçekleştirdiği tüm işlemleri gerçek zamanlı Event'e dönüştürmek,
* Her Event'i PID ile ilişkilendirerek izlenebilir kılmak,
* Olay Kayıt Merkezi'ni Executor seviyesinde 28 yeni Event tipiyle genişletmek,
* LAC'ın bu Event'leri gerçek zamanlı okuyarak yöneticiye tam geliştirme şeffaflığı sunmasını sağlamak,
* Fake Progress'i mimari seviyede kesin olarak engellemek,
* Geliştirme sürecini baştan sona izlenebilir ve denetlenebilir hale getirmektir.

### Beklenen Sonuç

* EEC, Executor ile Olay Kayıt Merkezi arasındaki Event dönüştürme katmanı olarak tanımlanmış olur.
* Tüm Executor işlemleri gerçek zamanlı Event olarak kaydedilir.
* LAC, PID bazında kronolojik Event akışını görüntüleyerek yöneticiye tam şeffaflık sağlar.
* Fake Progress mimari seviyede yasaklanmış olur.
* Geliştirme süreci izlenebilir, denetlenebilir ve raporlanabilir hale gelir.

---

## AR-002_62

### Anayasal Doğrulama Önceliği ve Runtime Karşılaştırma Mimarisi

### Başlık

Constitution-First Runtime Verification — HLK Anayasa-Öncelikli Çalışma Mimarisi

### Kural

HLK hiçbir Runtime bilgisini mutlak doğru kabul etmez.

HLK; herhangi bir Boot çıktısını, Runtime durumunu, Test sonucunu veya Log kaydını değerlendirmeden ÖNCE ilgili anayasal kaynakları inceler.

HLK değerlendirme öncesinde aşağıdaki anayasal bileşenleri ilgili kaynaklardan çıkarır:

1. **İlgili Workflow'u** — `09_WORKFLOW_MANIFEST.md` ve `11_WORKFLOW_FEATURE_MAP.md` kaynaklarından
2. **İlgili State'i** — `07_HLK_STATE_ENGINE.md` (SE-007_3/4/5/6) kaynağından
3. **İlgili Scene'i** — `08_HLK_FLOW_DIAGRAM.md` (FD-008_1) ve `17_SAHNE_KAYIT_DEFTERİ.md` kaynaklarından
4. **İlgili Feature'ı** — `10_FEATURE_REGISTRY.md` kaynağından
5. **İlgili Operational Rule'u** — `04_Operational_Rules.md` kaynağından
6. **İlgili Quality Rule'u** — `05_Quality_Rules.md` kaynağından
7. **İlgili MASTER kuralını** — `00_HLK_MASTER_RULE_BOOK.md` kaynağından
8. **İlgili Architecture Rule'u** — `03_Architecture_Rules.md` kaynağından

Bu anayasal çıkarım tamamlandıktan sonra HLK, çalışan sistemi (runtime) bu anayasal beklenti ile karşılaştırır.

### Anayasal Sapma Durumunda HLK'nın Davranışı

Herhangi bir anayasal sapma tespit edilirse HLK aşağıdaki sırayı izler:

1. **Sapmanın nedenini analiz eder** — Hangi anayasal kural ihlal edilmiş? Sapma neden kaynaklanıyor?

2. **Kendi kendine müdahale ederek düzeltmeye çalışır** — HLK, mümkün olan durumlarda Executor'a (Claude) veya geliştiriciye ihtiyaç duymadan önce kendi kendine düzeltme girişiminde bulunur. Bu girişim CEE-006 (Kendi Kendine Düzeltme Kuralı) kapsamında yürütülür.

3. **Düzeltme sonrasında sistemi yeniden anayasal olarak doğrular** — Düzeltme uygulandıktan sonra CEE POST-CHECK (6 boyutlu denetim) yeniden çalıştırılır.

4. **Doğrulama başarılı ise normal akışa devam eder** — CEE PASS alındığında görev tamamlanmış kabul edilir ve sistem normal akışına döner.

5. **Doğrulama başarısız ise Anayasal Kanıt Raporu oluşturarak eskalasyon üretir** — Kendi kendine düzeltme girişimleri (maksimum 3 döngü) başarısız olduğunda, HLK bir Anayasal Kanıt Raporu hazırlar ve Proje Yöneticisine eskalasyon olarak iletir. Eskalasyon sonrası karar yalnızca Proje Yöneticisine aittir.

### CONSTITUTION_READY Kısıtlaması

HLK, kendi kendine müdahale etmeyi denemeden hiçbir durumda "CONSTITUTION_READY" veya eşdeğer başarılı durum raporu üretemez.

"CONSTITUTION_READY" durumu yalnızca aşağıdaki koşulların TÜMÜ sağlandığında ilan edilebilir:

1. Anayasal kaynaklardan beklenti çıkarımı tamamlanmıştır
2. Runtime durumu anayasal beklenti ile karşılaştırılmıştır
3. Varsa sapmalar için kendi kendine düzeltme girişimi yapılmıştır
4. Düzeltme sonrası CEE POST-CHECK'ten PASS alınmıştır
5. Tüm denetim boyutları (Kod-Anayasa, Flow, State, OR, Mimari, Runtime) yeşil durumdadır

Claude veya geliştirici yalnızca HLK'nın anayasal olarak çözemediği ve kanıtlarıyla birlikte eskale ettiği durumlarda devreye girmelidir.

### Amaç

Bu mimarinin amacı;

* HLK'nın Runtime çıktılarını sorgulamadan kabul etmesini anayasal olarak engellemek,
* Her Runtime değerlendirmesinden önce anayasal kaynaklara başvurmayı zorunlu kılmak,
* HLK'nın kendi kendine düzeltme yeteneğini anayasal bir zorunluluk haline getirmek,
* Eskalasyonların yalnızca gerçekten çözülemeyen durumlarda ve kanıtlarıyla birlikte yapılmasını sağlamak,
* "CONSTITUTION_READY" durumunun yalnızca gerçek anayasal doğrulama tamamlandıktan sonra üretilebilmesini garanti etmek,
* Geliştirici müdahalesini yalnızca HLK'nın anayasal olarak çözemediği durumlarla sınırlandırmaktır.

### Beklenen Sonuç

* HLK önce ANA YASA'yı referans alır; Runtime çıktılarını sorgulamadan kabul etmez.
* Runtime ile ANA YASA otomatik karşılaştırılır; sapmalar tespit edilir.
* HLK mümkün olan durumlarda kendi kendine düzeltme yapar; Executor'a ihtiyaç duymaz.
* Düzeltme sonrası yeniden anayasal doğrulama yapılır; PASS alınmadan tamamlanmış kabul edilmez.
* Yalnızca çözülemeyen durumlar, kanıt raporuyla birlikte geliştiriciye eskale edilir.
* "CONSTITUTION_READY" yalnızca gerçek anayasal doğrulama tamamlandıktan sonra üretilebilir.
* HLK'nın anayasal otoritesi Runtime karşısında da korunur; hiçbir çalışma anı çıktısı ANA YASA'nın üzerinde değildir.

---

## AR-002_63

### Başlık

**State ve Conversation Behavior Ayrımı Mimarisi**

### Kural

HLK mimarisinde **State** ile **Conversation Behavior** aynı kavram değildir.

**State**, sistemin bulunduğu operasyonel durumu tanımlar.

**Conversation Behavior** ise, aktif State içerisinde kullanıcıya nasıl davranılacağını tanımlar.

Aynı State doğru çalışıyor olsa bile;

* yanlış konuşma,
* yanlış sahne davranışı,
* yanlış sunum,
* yanlış soru,
* yanlış yönlendirme

üretilmesi anayasal ihlal kabul edilir.

Bu nedenle HLK, State doğrulamasından bağımsız olarak Conversation Behavior doğrulaması yapmak zorundadır.

Her Telegram konuşması;

* aktif State,
* aktif Sahne,
* Flow Diagram,
* Conversation Behavior

birlikte değerlendirilerek doğrulanır.

### Temel İlke

**State'in doğru olması, Conversation Behavior'un doğru olduğu anlamına gelmez.**

Her iki davranış anayasal olarak bağımsız değerlendirilir ve ayrı ayrı denetlenir.

### Beklenen Sonuç

HLK yalnızca doğru State geçişlerini değil;

* doğru sahne davranışını,
* doğru konuşma üretimini,
* doğru sunum davranışını

da anayasal olarak doğrular.

---

## AR-002_64

### Başlık

**Reference Form UI Authority**

### Kural

HLK, FORMLAR klasöründe bulunan Referans Formları HLK'nın Resmi Referans Form Kütüphanesi (Official Reference Form Library) olarak kabul eder.

Her Referans Form aşağıdaki klasör yapısına sahiptir:

* `REFERANS_*.png` — Referans Formun görsel kaynağı
* `template.html` — Kullanıcı arayüzü şablonu
* `sample-data.json` — Örnek veri dosyası
* `render.js` — Kullanıcı arayüzü render mantığı

Referans Formlar;

* örnek ekran,
* taslak,
* fikir,
* dokümantasyon

değildir.

Referans Formlar, HLK kullanıcı arayüzünün resmi UI spesifikasyonudur.

Her kullanıcı ekranı geliştirilmeden önce HLK;

* İlgili STATE'i tespit eder.
* İlgili Flow Diagram bölümünü tespit eder.
* İlgili Referans Form klasörünü tespit eder.
* İlgili Referans `.png` dosyasını ve beraberindeki `template.html`, `sample-data.json`, `render.js` dosyalarını eksiksiz analiz eder.

Kod geliştirme süreci ancak bu analiz tamamlandıktan sonra başlatılabilir.

Kodun görevi kullanıcı arayüzünü tasarlamak değildir.

Kodun görevi, `template.html` ve `render.js` üzerinden Referans Formda tanımlanan kullanıcı arayüzünü Telegram üzerinde birebir uygulamaktır.

Kod;

* Referans `.png` dosyasını değiştiremez.
* Referans Formu yeniden yorumlayamaz.
* Referans Formda bulunmayan yeni kullanıcı arayüzü bileşenleri oluşturamaz.
* Referans Formdan farklı ekran düzeni oluşturamaz.

Telegram'da kullanıcıya gösterilen ekran;

* ekran düzeni,
* bilgi yerleşimi,
* tablo yapısı,
* bilgi sıralaması,
* ikonlar,
* onay kutuları,
* kullanıcı etkileşimleri,
* butonlar,
* ekran davranışları

bakımından Referans `.png` dosyası ile birebir uyumlu olmak zorundadır.

Referans `.png` dosyası ile çalışan kullanıcı arayüzü arasında farklılık oluşursa;

* Kod düzeltilir.
* Referans `.png` dosyası değiştirilmez.

Referans Form her zaman kullanıcı arayüzünün resmi otoritesidir.

HLK içerisinde geliştirilecek her yeni kullanıcı ekranı için önce ilgili Referans Form klasörü oluşturulur.

Referans Form klasörü oluşturulmadan kullanıcı arayüzü geliştirilmez.

### Temel İlke

**Referans Formlar, HLK Telegram kullanıcı arayüzünün resmi üretim spesifikasyonudur. Kodun görevi kullanıcı arayüzünü tasarlamak değil, `template.html` ve `render.js` aracılığıyla Referans `.png` dosyasında tanımlanan ekranı birebir uygulamaktır.**

### Beklenen Sonuç

* Tüm Telegram ekranları ilgili Referans Form esas alınarak geliştirilir.
* Referans Form ile çalışan ekran arasında fark oluşmaz.
* Kod, Referans Formun uygulama katmanı olarak kalır; UI tasarımı yapmaz.
* Yeni ekran geliştirmelerinde önce Referans Form klasörü oluşturulur, sonra kod yazılır.
* Anayasal UI otoritesi olarak Referans Formlar, Flow Diagram ile birlikte kullanıcı deneyiminin çift katmanlı anayasal güvencesini oluşturur.

---

## AR-002_65

### Başlık

**Reference Form UI Implementation**

### Kural

HLK içerisinde geliştirilecek her kullanıcı arayüzü aşağıdaki anayasal geliştirme sırasını uygulamak zorundadır.

```
İlgili STATE
    ↓
İlgili Flow Diagram
    ↓
İlgili Referans Form Klasörü
    ↓
Kod
    ↓
Runtime
    ↓
Telegram
```

Kodun görevi kullanıcı arayüzünü tasarlamak değildir.

Kodun görevi, ilgili Referans Form klasöründeki `template.html` ve `render.js` aracılığıyla, Referans `.png` dosyasında tanımlanan kullanıcı arayüzünü Telegram üzerinde birebir uygulamaktır.

Kod;

* Referans Formu yeniden yorumlayamaz.
* Referans Formdan farklı kullanıcı arayüzü oluşturamaz.
* Referans Formda bulunmayan yeni UI bileşeni ekleyemez.
* Referans Formdaki kullanıcı etkileşimlerini değiştiremez.

Kod tamamlandıktan sonra çalışan Telegram ekranı ilgili Referans `.png` dosyası ile doğrulanacaktır.

Herhangi bir farklılık tespit edilirse;

* Kod düzeltilir.
* Referans `.png` dosyası değiştirilmez.

Telegram ekranı Referans `.png` dosyası ile birebir uyumlu olmak zorundadır.

### Temel İlke

**Kod, Referans Formun uygulayıcısıdır; tasarlayıcısı değildir. Geliştirme sırası STATE → Flow Diagram → Referans Form Klasörü → Kod olarak uygulanır. Referans Form ile Telegram ekranı arasındaki her fark anayasal sapmadır ve kod düzeltilerek giderilir.**

### Beklenen Sonuç

* Tüm kullanıcı arayüzü geliştirmeleri STATE → Flow Diagram → Referans Form Klasörü → Kod sırasıyla yapılır.
* Kod, Referans Formun Telegram üzerindeki birebir uygulaması olarak kalır.
* Kod bağımsız UI tasarımı yapmaz; yalnızca Referans Formu uygular.
* Telegram ekranı ile Referans `.png` dosyası arasında sıfır fark hedeflenir.
* Herhangi bir farklılıkta kod düzeltilir, Referans `.png` korunur.

---

## AR-002_66

### Başlık

**Referans Form Runtime Render Zorunluluğu**

### Kural

HLK içerisinde Referans Form mimarisi ile tanımlanmış hiçbir kullanıcı arayüzü çalışma zamanında doğrudan Telegram mesajı (`send_message`, `reply_text` vb.) olarak üretilemez.

Referans Form tanımlanmış bir STATE'e ulaşıldığında HLK aşağıdaki mimariyi uygulamak zorundadır:

1. İlgili Referans Form klasörü yüklenir.
2. Referans `.png` dosyası ilgili formun değiştirilemez tek görsel otoritesi olarak esas alınır.
3. `template.html` yüklenir.
4. Geliştirme aşamasında `sample-data.json`, çalışma zamanında ise gerçek Runtime verileri kullanılır.
5. `render.js` çalıştırılarak nihai kullanıcı arayüzü oluşturulur.
6. Oluşturulan arayüz PNG olarak render edilir.
7. Render edilen PNG Telegram kullanıcısına görsel olarak gönderilir.

Referans Form tanımlanmış hiçbir STATE içerisinde eski mesaj tabanlı kullanıcı arayüzü kullanılamaz.

`send_message`, `reply_text` veya benzeri düz metin çıktıları yalnızca Referans Form tanımlanmamış konuşma adımlarında kullanılabilir.

Render işlemi başarısız olduğunda eski mesaj tabanlı kullanıcı arayüzüne geri dönüş (fallback) yapılamaz.

Bu durumda hata kayıt altına alınır ve HLK'nın tanımlı hata yönetimi süreci çalıştırılır.

---

### Amaç

Bu kuralın amacı;

* Referans Form mimarisinin çalışma zamanında eksiksiz uygulanmasını sağlamak,
* Tüm kullanıcı arayüzlerinin tek mimari standart üzerinden üretilmesini zorunlu hale getirmek,
* Referans Form tanımlı ekranlarda eski mesaj tabanlı arayüzlerin tekrar kullanılmasını önlemek,
* Runtime davranışını Referans Form mimarisi ile tam uyumlu hale getirmektir.

---

### Beklenen Sonuç

* Referans Form tanımlı tüm STATE'lerde kullanıcı arayüzü `template.html` + `render.js` → PNG olarak üretilir.
* `send_message` / `reply_text` yalnızca Referans Form tanımlanmamış adımlarda kullanılır.
* Eski mesaj tabanlı arayüzler Referans Form tanımlı STATE'lerden tamamen kaldırılır.
* Render başarısız olduğunda fallback yerine hata yönetimi çalıştırılır.
* Tüm kullanıcı arayüzleri tek standart üzerinden üretilir ve Referans `.png` ile uyumlu olur.

---

## AR-002_67

### Başlık

**Referans Form Runtime Render Zorunluluğu**

### Kural

Bu kural, Referans Form Mimarisi kuralının çalışma zamanı (Runtime) uygulama standardını tanımlar.

HLK, her STATE geçişinde öncelikle `08_HLK_FLOW_DIAGRAM.md` dosyasını esas alarak bulunduğu sahne için Referans Form tanımlanıp tanımlanmadığını kontrol eder.

Referans Form tanımlanmamış sahnelerde HLK, mevcut Konuşma Arayüzü (Conversation UI) mimarisini kullanmaya devam eder.

Referans Form tanımlanmış sahnelerde ise aşağıdaki mimari zorunlu olarak uygulanır:

1. İlgili Referans Form klasörü yüklenir.
2. Referans `.png` dosyası ilgili formun değiştirilemez tek görsel otoritesi olarak kabul edilir.
3. `template.html` yüklenir.
4. Geliştirme aşamasında `sample-data.json`, çalışma zamanında ise gerçek Runtime verileri kullanılır.
5. `render.js` çalıştırılarak Referans PNG'ye uygun nihai kullanıcı arayüzü oluşturulur.
6. Oluşturulan çıktı hedef platforma uygun formatta render edilir.
7. Telegram çalışma ortamında bu çıktı Referans Form olarak kullanıcıya gönderilir.

Referans Form tanımlanmış hiçbir STATE içerisinde kullanıcı arayüzü doğrudan `send_message`, `reply_text` veya benzeri düz metin mesajları ile üretilemez.

Bu yöntem yalnızca Referans Form tanımlanmamış konuşma adımlarında kullanılabilir.

Render işlemi başarısız olduğunda eski mesaj tabanlı kullanıcı arayüzüne geri dönüş (fallback) yapılamaz.

Bu durumda;

* hata kayıt altına alınır,
* ilgili hata yönetim süreci çalıştırılır,
* Runtime davranışı Referans Form mimarisini ihlal edecek şekilde değiştirilemez.

---

### Amaç

Bu kuralın amacı;

* Referans Form mimarisinin çalışma zamanında eksiksiz uygulanmasını sağlamak,
* `08_HLK_FLOW_DIAGRAM.md` içerisinde Referans Form tanımlanmış tüm sahnelerde tek kullanıcı arayüzü standardını zorunlu hale getirmek,
* Referans Form tanımlı ekranlarda eski mesaj tabanlı kullanıcı arayüzlerinin tekrar kullanılmasını önlemek,
* Runtime davranışını Referans Form mimarisi ile tam uyumlu hale getirmek,
* Kullanıcı arayüzünün tek görsel otoritesinin Referans Formlar olmasını garanti altına almaktır.

---

### Beklenen Sonuç

* Her STATE geçişinde Flow Diagram üzerinden Referans Form kontrolü yapılır.
* Referans Form tanımlı sahnelerde `template.html` + Runtime veri + `render.js` → PNG zorunlu olarak uygulanır.
* Referans Form tanımlanmamış sahnelerde mevcut Konuşma Arayüzü (Conversation UI) korunur.
* `send_message` / `reply_text` yalnızca Referans Form tanımlanmamış konuşma adımlarında kullanılır.
* Render başarısız olduğunda fallback uygulanmaz; hata loglanır ve hata yönetimi çalıştırılır.
* Tüm kullanıcı arayüzleri Referans `.png` görsel otoritesi ile uyumlu olur.

---

## AR-002_68

### Başlık

**REFERENCE DATA CONTRACT RULE**

### Kural

Her REFERANS FORM klasörü içerisinde bulunan `sample-data.json` dosyası, o REFERANS FORM'un resmi **DATA CONTRACT**'ıdır.

Bu dosya; `template.html`, `render.js`, Runtime, Render Service ve ilgili tüm üretim modülleri için **tek veri otoritesidir.**

Hiçbir modül, `sample-data.json` dışında yeni bir veri modeli oluşturamaz.

---

### Zorunlu Maddeler

1. `sample-data.json` referans veri şemasıdır.
2. Runtime yeni DATA modeli oluşturamaz.
3. Alan isimleri değiştirilemez.
4. Alan sırası değiştirilemez.
5. Section yapısı değiştirilemez.
6. Label değiştirilemez.
7. İkon değiştirilemez.
8. Template, render.js, Runtime, Render Service aynı DATA CONTRACT'ı kullanacaktır.
9. Runtime yalnızca alanların **değerlerini** doldurabilir. Veri yapısını değiştiremez.
10. Alan eklemek, alan silmek, alan adını değiştirmek, section değiştirmek, label değiştirmek, ikon değiştirmek, yeni JSON modeli üretmek **Constitution Violation** kabul edilir.
11. Her REFERANS FORM tek otoritedir. İkinci bir veri modeli oluşturulamaz.
12. Runtime DATA modeli, `sample-data.json` ile **%100 yapısal uyumlu** olmak zorundadır.
13. Referans PNG, yalnızca `template.html` + `sample-data.json` ile yeniden üretilebilmelidir.
14. Runtime tarafından üretilen PNG, aynı template ve aynı DATA CONTRACT kullanıldığında, REFERANS PNG ile aynı yapıyı üretmek zorundadır.

---

### Kapsam

Bu kural aşağıdaki tüm REFERANS FORM'lar için geçerlidir:

* REFERANS_Brief_Onay_Formu
* REFERANS_SENARYO_ONAY_FORMU
* REFERANS_KULLANICI_FIYAT_TEKLIF_FORMU
* REFERANS_YONETICI_FIYATLANDIRMA_FORMU
* REFERANS_YONETICI_VIDEO_URETIM_ONAY_FORMU
* REFERANS_HLK_LIVE_ACTIVITY_CENTER

ve gelecekte eklenecek tüm REFERANS FORM klasörleri.

---

### Amaç

Bu kuralın amacı;

* `sample-data.json` ile Runtime DATA modeli arasındaki sapmaları anayasal olarak engellemek,
* Aynı REFERANS FORM kullanılmasına rağmen Telegram'a gönderilen PNG'nin REFERANS PNG'den farklı üretilmesini önlemek,
* Tüm Render Pipeline bileşenlerinin (`template.html`, `render.js`, Runtime, Render Service) tek bir DATA CONTRACT üzerinden çalışmasını garanti altına almak,
* Veri yapısındaki değişikliklerin yalnızca `sample-data.json` güncellenerek ve Proje Yöneticisi onayıyla yapılabilmesini sağlamak,
* Runtime'da bağımsız veri modeli oluşturulmasını Constitution Violation olarak tanımlamak,
* Referans PNG'nin her zaman `template.html` + `sample-data.json` ile yeniden üretilebilir olmasını garanti etmektir.

---

### Beklenen Sonuç

* Tüm REFERANS FORM'lar için `sample-data.json` tek DATA CONTRACT olarak kullanılır.
* Runtime, `sample-data.json` şemasına %100 uyumlu veri üretir.
* Hiçbir modül bağımsız veri modeli oluşturamaz.
* Referans PNG, `template.html` + `sample-data.json` ile her zaman yeniden üretilebilir.
* Constitution Scan Engine, Runtime DATA modeli ile `sample-data.json` arasındaki sapmaları otomatik tespit eder.
* Veri yapısı değişiklikleri yalnızca Proje Yöneticisi onayı ile `sample-data.json` üzerinden yapılır.

---

## AR-002_69

### Başlık

**REFERENCE COMPONENT INDEPENDENCE RULE**

### Kural

Her REFERANS FORM, kendi içerisinde **tam ve bağımsız bir Referans Bileşenidir (Reference Component).**

Bir REFERANS FORM'un;

* tasarımı,
* veri modeli,
* üretim mantığı,
* ve referans çıktısı,

yalnızca kendi Referans Bileşeni içerisinde tanımlanmalıdır.

Bir REFERANS FORM'un oluşturulması veya yeniden üretilmesi sırasında başka bir REFERANS FORM'un veya başka bir modülün;

* tasarımı,
* veri modeli,
* kullanıcı arayüzü,
* üretim mantığı,
* veya referans bileşenleri

**kullanılamaz.**

Her REFERANS FORM, **tek başına taşınabilir, doğrulanabilir ve yeniden üretilebilir** olmak zorundadır.

Runtime, yalnızca ilgili REFERANS FORM'un tanımladığı referans bileşenlerini kullanarak aynı referans çıktısını üretmek zorundadır.

Bir REFERANS FORM'un başka dosya, klasör veya modüllere;

* kullanıcı arayüzü,
* veri modeli,
* veya üretim mantığı

açısından bağımlı hale getirilmesi **Constitution Violation** kabul edilir.

Bu kural mevcut ve gelecekte oluşturulacak tüm REFERANS FORM bileşenleri için geçerlidir.

---

### Kapsam

Bu kural aşağıdaki tüm REFERANS FORM'lar için geçerlidir:

* REFERANS_Brief_Onay_Formu
* REFERANS_SENARYO_ONAY_FORMU
* REFERANS_KULLANICI_FIYAT_TEKLIF_FORMU
* REFERANS_YONETICI_FIYATLANDIRMA_FORMU
* REFERANS_YONETICI_VIDEO_URETIM_ONAY_FORMU
* REFERANS_HLK_LIVE_ACTIVITY_CENTER

ve gelecekte eklenecek tüm REFERANS FORM klasörleri.

---

### Amaç

Bu kuralın amacı;

* Her REFERANS FORM'un kendi kendine yeterli, bağımsız bir bileşen olmasını sağlamak,
* Bir REFERANS FORM'un tasarımının veya veri modelinin başka bir formdan kopyalanmasını veya ödünç alınmasını engellemek,
* REFERANS_Brief_Onay_Formu örneğinde olduğu gibi, bir formun kendi base.css standart tasarım sistemi yerine özel CSS ve DOM yapısı kullanarak referans PNG'den sapmasını anayasal olarak önlemek,
* Her formun kendi `template.html`, `render.js` ve `sample-data.json` dosyalarıyla tam ve bağımsız olarak çalışmasını garanti altına almak,
* Formlar arası gizli bağımlılıkları (örneğin bir formun CSS'inin başka bir formun stillerine bağımlı olması) Constitution Violation olarak tanımlamak,
* Runtime'da her formun yalnızca kendi referans bileşenlerini kullanarak doğru çıktıyı üretmesini sağlamaktır.

---

### Beklenen Sonuç

* Her REFERANS FORM, kendi klasörü içerisinde tam ve bağımsız bir Referans Bileşenidir.
* Hiçbir REFERANS FORM, başka bir formun tasarım, veri modeli veya üretim mantığına bağımlı değildir.
* Her form tek başına taşınabilir, doğrulanabilir ve yeniden üretilebilir.
* Runtime, her form için yalnızca o formun kendi referans bileşenlerini kullanır.
* Formlar arası çapraz bağımlılık oluşması Constitution Violation olarak tespit edilir.
* Constitution Scan Engine, her formun bağımsızlığını doğrulayabilir.
