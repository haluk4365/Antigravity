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

Arka plan araştırmaları, kullanıcı ile yürütülen brief toplama sürecini durdurmaz ve mümkün olan en yüksek verimlilikle eş zamanlı olarak devam eder.

### Araştırmanın Amacı

HLK, ürün araştırmasını yalnızca araştırma yapmak amacıyla yürütmez.

Araştırmanın temel amacı;

* ürünü doğru tanımak,
* ürünü doğru analiz etmek,
* ürünü doğru konumlandırmak,
* reklam üretim sürecini destekleyecek bilgi ve dijital materyalleri toplamak,
* karar mekanizmasını beslemek

amacıyla bilgi değeri taşıyan materyaller elde etmektir.

HLK'nin amacı belirli sayıda görsel toplamak değil, ürünü mümkün olan en yüksek doğrulukla tanımak ve karar mekanizmasına katkı sağlayacak bilgi ve materyalleri toplamaktır.

Toplanan her bilgi ve materyal HLK karar mekanizmasının bir girdisi olarak değerlendirilir.

### Ürün Referans Paketi

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

### Araştırma İlkeleri

HLK araştırmalarında platform odaklı değil, bilgi odaklı çalışır.

Araştırma süreci yalnızca veri toplama işlemi değildir. HLK elde edilen tüm materyalleri değerlendirir, sınıflandırır ve karar mekanizmasına katkı sağlayacak şekilde işler.

Araştırma ajanlarının amacı yalnızca görsel toplamak değildir. Araştırma ajanları;

* ürünün farklı açılarını,
* ürünün farklı detaylarını,
* ürünün kullanım biçimlerini,
* ürünün teknik veya görsel özelliklerini,
* ürünü daha doğru tanımaya yardımcı olacak tamamlayıcı bilgileri,
* marka bilgilerini,
* kullanıcı deneyimlerini,
* reklam üretimine katkı sağlayabilecek diğer dijital materyalleri

aramaya yönlendirilir.

HLK, Anayasa'da tanımlanan Araştırma Kaynaklarını kullanarak;

* ürün bilgilerini,
* teknik verileri,
* görselleri,
* videoları,
* teknik dokümanları,
* kullanım bilgilerini

araştırır ve toplar.

### Araştırma Kaynakları

Araştırma sırasında kullanılacak platformlar önceden sabitlenmez. HLK, ihtiyaç duyduğunda aşağıdaki listede yer alan kaynaklarla sınırlı kalmaksızın güvenilir yeni araştırma kaynaklarını da kullanabilir.

Aşağıdaki liste HLK'nın kullanabileceği asgari araştırma kaynaklarını tanımlar.

**Resmî Kaynaklar**

* Marka Resmî Web Sitesi
* Ürün Resmî Sayfası
* Üretici Dokümanları

**E-Ticaret Platformları**

* Amazon
* Trendyol
* Hepsiburada
* N11
* Ürün kategorisine uygun diğer e-ticaret platformları

**Görsel Kaynakları**

* Google Görseller
* Bing Görseller
* Pinterest
* Diğer uygun görsel platformları

**Video Platformları**

* YouTube
* TikTok
* Vimeo
* Diğer uygun video platformları

**Sosyal Medya**

* Instagram
* Facebook
* X
* Reddit
* Diğer uygun sosyal medya platformları

**Teknik Kaynaklar**

* Kullanım Kılavuzları
* Teknik Dokümanlar
* Ürün Veri Sayfaları

**Topluluk Kaynakları**

* Forumlar
* Bloglar
* Kullanıcı Deneyimleri
* Diğer güvenilir topluluk kaynakları

### Araştırma Stratejisi

HLK araştırma kaynaklarını sabit bir sıra ile kullanmak zorunda değildir.

Araştırma stratejisi;

* ürün kategorisine,
* ürün türüne,
* araştırmanın amacına,
* mevcut bilgi seviyesine,
* önceki araştırma sonuçlarına,
* karar mekanizmasının ihtiyaçlarına

göre dinamik olarak belirlenir.

HLK, görevin başlangıcında kendi karar mekanizması ile oluşturduğu araştırma mimarisini ve ajan orkestrasyonunu devreye alır. Araştırma sırasında bu stratejiyi yeniden oluşturmaz; ancak gerekli gördüğünde mevcut stratejiyi genişletebilir, yeni araştırma kaynaklarına yönlenebilir veya yeterli bilgiye ulaştığında araştırmayı sonlandırabilir.

Her platformun kullanılması zorunlu değildir. Ancak HLK; kullandığı, kullanmadığı ve atladığı araştırma kaynaklarının gerekçelerini kayıt altına almakla yükümlüdür.

### Materyal Değerlendirme İlkeleri

Araştırma sırasında elde edilen her materyal bilgi değeri açısından değerlendirilir. HLK, elde edilen materyalleri Ürün Referans Paketindeki referans ürün bilgileri ile ilişkilendirerek değerlendirir.

HLK;

* aynı veya yüksek derecede benzer bilgi taşıyan,
* düşük kaliteli veya kullanılabilir olmayan,
* doğrulanamayan,
* reklam üretim sürecine yeni bilgi kazandırmayan,
* karar mekanizmasına katkı sağlamayan,
* gereksiz tekrar oluşturan

materyalleri tespit ederek araştırma sonuçlarından çıkarır.

Yalnızca karar mekanizmasına katkı sağlayan doğrulanabilir materyaller;

* Araştırma Sonuçları,
* Referans Görseller,
* Digital Asset Archive,
* Production Package

kapsamında kayıt altına alınabilir.

### Araştırma Kayıt Standardı

HLK araştırma sürecini denetlenebilir şekilde kayıt altına alır.

Araştırılan her kaynak için en az aşağıdaki bilgiler kayıt edilir:

* Kaynak Adı
* Kaynak Türü
* Araştırma Durumu
* Araştırma Başlangıç Zamanı
* Araştırma Bitiş Zamanı
* Bulunan Materyal Sayısı
* Bulunan Görsel Sayısı
* Bulunan Video Sayısı
* Bilgi Değeri Açısından Kabul Edilen Materyal Sayısı
* Elenen Materyal Sayısı
* Araştırma Sonuç Durumu

Araştırma Durumu aşağıdaki değerlerden birini alır:

* Araştırıldı
* Ulaşılamadı
* Sonuç Bulunamadı
* Atlandı

HLK;

* araştırdığı her kaynağı kayıt altına alır,
* her kaynak için araştırma durumunu kayıt eder,
* araştırma sonucunda elde edilen materyalleri ilgili kaynak ile ilişkilendirir,
* araştırma sürecini denetlenebilir şekilde kayıt altına alır.

Araştırma sırasında ziyaret edilen tüm araştırma kaynakları ve bu kaynaklardan elde edilen sonuçlar, gerektiğinde denetlenebilir şekilde saklanır.

### Araştırmanın Tamamlanma Koşulları

HLK;

* araştırma sürecini tamamlamadan,
* araştırma kayıtlarını oluşturmadan,
* elde edilen materyalleri değerlendirmeden,
* karar mekanizmasına katkı sağlayan materyalleri belirlemeden,
* araştırmanın neden tamamlanamadığını kayıt altına almadan (tamamlanamayan araştırmalarda)

WF-002 Arka Plan Araştırması iş akışını tamamlanmış kabul edemez.

Araştırma tamamlandığında;

* Araştırma Sonuçları,
* Referans Görseller,
* Production Package,
* Digital Asset Archive,
* ilgili Event kayıtları

anayasal standartlara uygun şekilde birbirleri ile ilişkilendirilmelidir.

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

## AR-002_46A

### Başlık

Link Validation Agent Selection Architecture (Link Doğrulama Ajan Seçim Mimarisi)

### Amaç

HLK, Link Validation (Ürün Linki Doğrulama) görevlerinde kullanılacak ajanları da anayasal karar mekanizmasına uygun şekilde dinamik olarak seçer.

Link Validation ajanları, AR-002_46 Uzmanlık Alanı Ajan Kombinasyonu mimarisine dahil değildir. Ancak bu durum, Link Validation ajanlarının anayasal ajan seçim mimarisinden muaf olduğu anlamına gelmez.

### Uygulanan Anayasal Kurallar

Link Validation ajan seçiminde aşağıdaki anayasal kurallar aynen uygulanır:

* Dinamik Ajan Seçimi
* Dinamik Ajan Öncelik Sıralaması
* Ajan Değiştirme
* Yeniden Seçim
* Operasyonel Eskalasyon
* HLK Karar Mekanizması
* Karar Gerekçesi Standardı

Aday sayısı ve yedek aday sayısı Global Configuration içerisinde tanımlanan `GC_PRIMARY_CANDIDATE_COUNT` ve `GC_BACKUP_CANDIDATE_COUNT` parametrelerine göre belirlenir. Sayısal değerler bu maddede tekrar tanımlanmaz.

### Link Validation Ajan Seçim Kriterleri

HLK, Link Validation ajanlarını görevin gereksinimlerine göre objektif kriterlerle değerlendirir. Değerlendirme sırasında aşağıdaki kriterler kullanılabilir:

* Ürün bağlantısını doğrulama başarı oranı
* Desteklenen e-ticaret platformları
* JavaScript Render desteği
* Anti-Bot koruma başarısı
* Cloudflare uyumluluğu
* Sayfa doğrulama hızı
* API erişilebilirliği
* Servis kullanılabilirliği
* Kredi / Kota durumu
* Geçmiş operasyonel başarı oranı
* Maliyet
* Güvenilirlik
* HLK tarafından gerekli görülen diğer objektif kriterler

Bu liste sınırlayıcı değildir. HLK yeni servisler, yeni teknolojiler veya yeni ihtiyaçlar doğrultusunda anayasal ilkelere uygun yeni değerlendirme kriterleri ekleyebilir.

### Temel İlke

Link Validation ajanları ile Uzmanlık Alanı Araştırma ajanları farklı görevleri yerine getirseler de; ajan seçimi, aday önceliklendirmesi, yedek aday kullanımı, yeniden seçim ve karar gerekçelendirmesi aynı anayasal karar mekanizmasına tabidir.

Tek fark, Link Validation ajanlarının AR-002_46 Uzmanlık Alanı Ajan Kombinasyonu mimarisi kapsamında değerlendirilmemesidir.

### Anayasal Dayanak

| Katman | Referans | Açıklama |
|---|---|---|
| **MASTER** | MASTER-004 | HLK Karar Mekanizması — ajan seçimi karar niteliğindedir |
| **MASTER** | MASTER-013 | HLK Runtime tek karar otoritesi |
| **AR** | AR-002_19 | Selection Architecture — dinamik öncelik sıralaması |
| **AR** | AR-002_21 | Provider Switching — sıradaki adaya geçiş |
| **AR** | AR-002_46 | Uzmanlık Alanı Ajan Kombinasyonu — kapsam dışı referans |
| **AR** | AR-002_75 | Production Service Selection — hizmet seçim mekanizması |
| **AR** | AR-002_87 | External Resource Recovery — ajan kurtarma protokolü |
| **GC** | GC_PRIMARY_CANDIDATE_COUNT | Birincil aday sayısı |
| **GC** | GC_BACKUP_CANDIDATE_COUNT | Yedek aday sayısı |

### Beklenen Sonuç

* Link Validation ajanları anayasal karar mekanizmasına bağlanır.
* Link Validation'a özgü seçim kriterleri resmi olarak tanımlanır.
* Tüm ajan seçimleri aynı anayasal mekanizma üzerinden yürütülür.
* AR-002_46 kapsam dışı olan Link Validation, anayasal boşlukta kalmaz.

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

### LAC Explainable Workflow Prensipleri

AR-002_59 kapsamında LAC, yalnızca bir Event izleme ekranı değil; **HLK'nın karar süreçlerini yöneticiye açıklayan resmi Explainable Workflow Explorer** olarak tanımlanır.

Bu prensipler mevcut mimariyi değiştirmez; Workflow, State Engine, Event sistemi, Decision Engine, Runtime ve Production Package davranışı aynen korunur. Bu prensipler yalnızca LAC'ın **sunum standardını** anayasal seviyede tanımlar.

#### AR-002_59.1 — LAC Explainable Workflow Explorer'dır

LAC yalnızca Event gösteren bir ekran değildir.

LAC;

* Workflow,
* Decision,
* State,
* Event,
* Agent,
* Production Package,
* Decision History

arasındaki **neden-sonuç ilişkisini açıklayan resmi yönetici ekranıdır.**

LAC'ın merkezinde Event değil, **Workflow** bulunur.

Yönetici LAC'ta log okumaz; **neden-sonuç zincirini okur.**

#### AR-002_59.2 — LAC Bilgi Üretmez

LAC hiçbir yeni bilgi üretmez.

LAC;

* karar vermez,
* ajan seçmez,
* puan hesaplamaz,
* neden üretmez,
* Workflow oluşturmaz,
* Event üretmez.

LAC mevcut anayasal kayıtlar arasındaki ilişkileri görselleştirir ve açıklar. LAC hiçbir yeni karar, yeni Workflow, yeni Event, yeni State veya yeni veri üretmez. Gösterdiği tüm bilgiler yalnızca mevcut anayasal kayıtların ilişkilendirilmesiyle oluşturulur.

Bu ilke aşağıdaki anayasal bileşenlerle tam uyumludur:

* **MASTER-004** — HLK tek karar vericidir; LAC bu yetkiyi devralamaz veya paylaşamaz.
* **AR-002_59** — LAC, bu mimari maddenin tanımladığı sınırlar içerisinde çalışır.
* **Decision History** — LAC kararları yalnızca okur; yeni karar girişi yapamaz.
* **Production Package** — LAC'ın gösterdiği tüm üretim verisi Production Package'ten gelir.
* **Event System** — LAC yalnızca Olay Kayıt Merkezi tarafından kaydedilmiş Event'leri gösterir.
* **Olay Kayıt Merkezi** — LAC Event üretmez; yalnızca kayıtlı Event'leri okur.

LAC'ın gösterdiği her bilginin kaynağı bir anayasal kayıttır:

* PID → PID Registry
* Workflow → Workflow Manifest
* Decision → Decision History
* Event → Olay Kayıt Merkezi
* State → State Engine
* Runtime → Production Runtime
* Agent → Agent Assignment kayıtları
* Production Package → Production Package JSON

LAC bu kaynaklardan okur, ilişkilendirir, gösterir; hiçbirini değiştirmez.

#### AR-002_59.3 — Katmanlı Açıklama Zinciri

Her Workflow, LAC üzerinde **katmanlı açıklama mantığıyla** incelenebilmelidir.

Standart açıklama zinciri:

```
Workflow
  ↓
Sonuç
  ↓
HLK Kararı
  ↓
Karar Gerekçesi
  ↓
Oluşturulan Görevler
  ↓
Ajan Adayları
  ↓
Ajan Puanları
  ↓
Ajan Seçim Gerekçesi
  ↓
Çalışan Ajan
  ↓
Kanıtlar
  ↓
Event Kayıtları
  ↓
Log Kayıtları
  ↓
API Kayıtları
```

Bu yapı **yeni Workflow oluşturmaz.** Mevcut Workflow'un nasıl ilerlediğini **açıklar.**

Her katman tekrar açılabilir olmalıdır. Teorik olarak açıklama derinliği sınırsızdır.

Yönetici yalnızca ilgilendiği katmanı açarak detayı inceler; ilgilenmediği katmanları kapalı tutar.

#### AR-002_59.4 — Workflow Merkezli Sunum

LAC, kronolojik Log veya Event listesi olarak çalışmaz.

Yönetici;

* Workflow sonucundan başlayarak,
* ilgili karar zincirini,
* kanıtları,
* Event kayıtlarını,
* Log kayıtlarını,
* ve teknik ayrıntıları

**katman katman** inceleyebilmelidir.

Bu sayede yönetici yüzlerce satır log okumak zorunda kalmaz; yalnızca Workflow ağacını takip ederek üretimin neden başarılı veya başarısız olduğunu sezgisel olarak anlayabilir.

#### AR-002_59.5 — Root Cause Görselleştirmesi

LAC, **Root Cause analizini kolaylaştıracak şekilde** ilk hata noktasını görsel olarak ayırt edebilmelidir.

Root Cause tespit mantığı:

1. Workflow'lar anayasal sırayla taranır (WF-001 → WF-010).
2. **İlk başarısız (FAILED) Workflow** Root Cause olarak işaretlenir.
3. Root Cause Workflow içerisindeki **ilk başarısız karar katmanı** Root Cause düğümü olarak belirlenir.
4. Root Cause'tan sonraki Workflow'lar **etkilendi** (affected) olarak gösterilir.
5. Root Cause öncesindeki Workflow'lar kendi gerçek durumlarını korur.

Renk standardı:

| Durum | Renk | Anlamı |
|-------|------|--------|
| 🟢 Yeşil | Başarıyla tamamlandı |
| 🟡 Sarı | Devam ediyor |
| ⚪ Gri | Henüz başlanmadı |
| 🔴 Kırmızı | İlk hata burada başladı (Root Cause) |
| 🟠 Turuncu | Root Cause sonrası etkilendi |

Bu özellik **yalnızca sunum katmanıdır.** Karar mekanizmasını değiştirmez. HLK'nın karar otoritesi (MASTER-004) aynen korunur.

#### AR-002_59.6 — Temel İlke

LAC'ın amacı Event'leri göstermek değil, **Event'lerin oluşturduğu neden-sonuç zincirini yöneticiye açıklamaktır.**

Bu ilke, AR-002_59'un kuruluş amacı olan *"HLK'nın karar süreçlerini yöneticiye açıklamak"* hedefinin **sunum standardını** anayasal seviyede netleştirir.

---

### Amaç

Bu mimarinin amacı;

* HLK yöneticisine, `/start` anından oturum kapanışına kadar tüm oturum yaşam döngüsünü kapsayan gerçek zamanlı, şeffaf ve müdahalesiz bir izleme arayüzü sunmak,
* Session, Workflow, State, Agent, Event, Decision, Service, Digital Asset, Production Package, Video Production, Quality Control, Delivery ve Archive katmanlarını tek merkezi ekranda toplamak,
* Tüm oturum ve üretim sürecini izlenebilir hale getirmek,
* HLK'nın karar süreçlerini yöneticiye açıklamak,
* Event'lerin oluşturduğu neden-sonuç zincirini yöneticiye Explainable Workflow Explorer mantığıyla sunmak,
* İlk hata noktasını (Root Cause) görsel olarak ayırt edilebilir kılmak,
* Yöneticiyi log okumaya zorlamamak; neden-sonuç ilişkisini katmanlı açıklama zinciriyle sezgisel hale getirmek,
* Fake Progress'i mimari seviyede yasaklamak,
* Yönetici ile HLK arasındaki yetki sınırını mimari seviyede tanımlamak,
* LAC'nin Desktop ve Mobile için tek bir resmi referans tasarım standardı oluşturmak,
* HLK'nın tüm sistem bileşenleri ile tam uyumlu, yeniden kullanılabilir bir merkezi operasyon izleme mimarisi oluşturmaktır.

---

### Beklenen Sonuç

* HLK Live Activity Center, `/start` anından oturum kapanışına kadar tüm oturum yaşam döngüsünü izleyen merkezi operasyon ekranı olarak tanımlanmış olur.
* LAC; Session, Workflow, State, Agent, Event, Decision, Service, Digital Asset, Production Package, Video Production, Quality Control, Delivery ve Archive olmak üzere 13 katmanı kapsar.
* LAC, Explainable Workflow Explorer olarak tanımlanır; merkezinde Event değil Workflow bulunur.
* Her Workflow katmanlı açıklama zinciriyle (Workflow → Sonuç → HLK Kararı → Gerekçe → Görevler → Ajanlar → Puanlama → Kanıtlar → Event → Log → API) incelenebilir.
* Root Cause (ilk hata noktası) görsel olarak ayırt edilebilir; yönetici tek bakışta problemin başlangıç noktasını anlayabilir.
* LAC yalnızca mevcut anayasal kayıtları ilişkilendirir; karar vermez, bilgi üretmez, Workflow oluşturmaz.
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

Kodun görevi, ilgili Referans Form klasöründeki `template.html` ve `render.js` aracılığıyla, Referans `.png` dosyasında tanımlanan kullanıcı arayüzünü hedef platform üzerinde **en yüksek sadakatle** uygulamaktır.

**Referans `.png` dosyası, kullanıcı arayüzünün değiştirilemez anayasal tasarım otoritesidir.** Kod, bu otoriteye bağlı kalarak hedef platformda uygulanabilir en yakın görsel, işlevsel ve kullanıcı deneyimi karşılığını üretmekle yükümlüdür.

**Platform Sınırlamaları:** Her platformun kendine özgü teknik sınırları vardır. Telegram; `<table>`, `<div>`, `<style>`, CSS grid/flexbox, özel fontlar ve gömülü görsel bileşenleri desteklemez. Bu teknik sınırlamalar anayasal sapma değil, platform gerçekliğidir. Hedef platform tarafından desteklenmeyen bir Referans Form bileşeni, aynı amacı yerine getiren resmi platform bileşeni ile uygulanır.

Kod;

* Referans `.png` dosyasını değiştiremez.
* Referans Formu yeniden yorumlayamaz.
* Referans Formdaki veri yapısını ve içeriği eksiksiz korumak zorundadır.
* Referans Formdaki kullanıcı etkileşimlerini (onay, red, seçim, düzeltme) birebir uygulamak zorundadır.
* Referans Formda bulunmayan yeni kullanıcı arayüzü bileşenleri oluşturamaz.
* Referans Formun bilgi hiyerarşisini ve sıralamasını korumak zorundadır.

Çalışan kullanıcı arayüzü, Referans `.png` dosyası ile aşağıdaki kriterlere göre doğrulanır:

1. **Veri Bütünlüğü:** Tüm Referans Form verileri çalışan ekranda eksiksiz mevcut mu?
2. **İşlevsel Eşdeğerlik:** Tüm kullanıcı etkileşimleri hedef platformda çalışıyor mu?
3. **Görsel Sadakat:** Platformun teknik sınırları içinde en yakın görsel karşılık sağlanmış mı?

Referans `.png` dosyası ile çalışan kullanıcı arayüzü arasında farklılık oluşursa;

* Kod, hedef platformun desteklediği en yakın karşılık ile düzeltilir.
* Referans `.png` dosyası değiştirilmez.
* Platform sınırlaması nedeniyle birebir uygulanamayan bileşenler anayasal sapma sayılmaz; yeter ki yukarıdaki üç doğrulama kriteri karşılansın.

Referans Form her zaman kullanıcı arayüzünün anayasal tasarım otoritesidir.

HLK içerisinde geliştirilecek her yeni kullanıcı ekranı için önce ilgili Referans Form klasörü oluşturulur.

Referans Form klasörü oluşturulmadan kullanıcı arayüzü geliştirilmez.

### Temel İlke

**Referans Formlar, HLK kullanıcı arayüzünün değiştirilemez anayasal tasarım otoritesidir. Kodun görevi kullanıcı arayüzünü tasarlamak değil, bu tasarımı hedef platformun teknik sınırları içerisinde en yüksek sadakatle uygulamaktır. Veri bütünlüğü, işlevsel eşdeğerlik ve görsel sadakat esastır.**

### Beklenen Sonuç

* Tüm kullanıcı arayüzleri ilgili Referans Form esas alınarak geliştirilir.
* Çalışan ekran, Referans Formun veri yapısını ve kullanıcı etkileşimlerini eksiksiz uygular.
* Kod, Referans Formun uygulama katmanı olarak kalır; UI tasarımı yapmaz.
* Yeni ekran geliştirmelerinde önce Referans Form klasörü oluşturulur, sonra kod yazılır.
* Platform sınırlaması kaynaklı görsel farklılıklar anayasal sapma sayılmaz; veri bütünlüğü, işlevsel eşdeğerlik ve görsel sadakat kriterleri karşılanır.
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

Kodun görevi, ilgili Referans Form klasöründeki `template.html` ve `render.js` aracılığıyla, Referans `.png` dosyasında tanımlanan kullanıcı arayüzünü Telegram üzerinde **en yüksek sadakatle** uygulamaktır.

**Referans `.png` dosyası, kullanıcı arayüzünün değiştirilemez anayasal otoritesidir.** Kod, bu otoriteye bağlı kalarak Telegram platformunda uygulanabilir en yakın görsel, işlevsel ve kullanıcı deneyimi karşılığını üretmekle yükümlüdür.

**Platform Sınırlamaları:** Telegram HTML desteği sınırlıdır (`<b>`, `<i>`, `<u>`, `<s>`, `<code>`, `<pre>`, `<blockquote>`, `<a>`, `<tg-spoiler>`). `<table>`, `<div>`, `<style>`, CSS grid/flexbox, özel fontlar ve gömülü görsel bileşenler Telegram tarafından desteklenmez. Bu teknik sınırlamalar anayasal sapma değil, platform gerçekliğidir.

**En Yüksek Sadakat İlkesi (Highest Fidelity Principle):** Referans `.png` dosyasında tanımlanan bir UI bileşeni Telegram tarafından teknik olarak desteklenmiyorsa, kod;

* Bileşeni atlamaz veya yok saymaz.
* Bileşenin taşıdığı veriyi, işlevi ve kullanıcı etkileşimini korur.
* Bileşeni, Telegram'ın resmi UI bileşenleriyle (`InlineKeyboardButton`, `ReplyKeyboardMarkup`, `<code>`, `<blockquote>`, `<pre>` vb.) en yakın görsel ve işlevsel karşılıkla uygular.
* Görsel birebirlik yerine **veri bütünlüğü + işlevsel eşdeğerlik + kullanıcı deneyimi tutarlılığı** hedeflenir.

Kod;

* Referans Formdaki veri yapısını ve içeriği eksiksiz korumak zorundadır.
* Referans Formdaki kullanıcı etkileşimlerini (onay, red, seçim, düzeltme) birebir uygulamak zorundadır.
* Referans Formda bulunmayan yeni UI bileşeni ekleyemez.
* Referans Formun bilgi hiyerarşisini ve sıralamasını korumak zorundadır.

Kod tamamlandıktan sonra çalışan Telegram ekranı ilgili Referans `.png` dosyası ile aşağıdaki kriterlere göre doğrulanacaktır:

1. **Veri Bütünlüğü:** Tüm Referans Form verileri Telegram ekranında eksiksiz mevcut mu?
2. **İşlevsel Eşdeğerlik:** Tüm kullanıcı etkileşimleri Telegram'da çalışıyor mu?
3. **Görsel Sadakat:** Telegram'ın teknik sınırları içinde en yakın görsel karşılık sağlanmış mı?

Herhangi bir farklılık tespit edilirse;

* Kod, Telegram'ın desteklediği en yakın karşılık ile düzeltilir.
* Referans `.png` dosyası değiştirilmez.
* Platform sınırlaması nedeniyle birebir uygulanamayan bileşenler anayasal sapma sayılmaz; yeter ki yukarıdaki üç doğrulama kriteri karşılansın.

### Temel İlke

**Kod, Referans Formun uygulayıcısıdır; tasarlayıcısı değildir. Geliştirme sırası STATE → Flow Diagram → Referans Form Klasörü → Kod olarak uygulanır. Referans `.png` dosyası görsel otoritedir. Telegram'ın teknik sınırları içinde en yüksek sadakat esastır: veri bütünlüğü, işlevsel eşdeğerlik ve kullanıcı deneyimi tutarlılığı önceliklidir.**

### Beklenen Sonuç

* Tüm kullanıcı arayüzü geliştirmeleri STATE → Flow Diagram → Referans Form Klasörü → Kod sırasıyla yapılır.
* Kod, Referans Formun veri yapısını ve kullanıcı etkileşimlerini eksiksiz uygular.
* Kod bağımsız UI tasarımı yapmaz; yalnızca Referans Formu Telegram platformunda uygulanabilir en yakın karşılıkla hayata geçirir.
* Telegram tarafından desteklenmeyen bileşenler, resmi Telegram bileşenleriyle en yüksek sadakatle değiştirilir.
* Veri bütünlüğü, işlevsel eşdeğerlik ve görsel sadakat doğrulama kriterleri karşılanır.
* Herhangi bir farklılıkta kod düzeltilir, Referans `.png` korunur.

---

## AR-002_66

### Başlık

**Referans Form Runtime Render Zorunluluğu**

### Kural

HLK içerisinde Referans Form mimarisi ile tanımlanmış hiçbir kullanıcı arayüzü çalışma zamanında eski mesaj tabanlı kullanıcı arayüzü (`send_message`, `reply_text` vb. düz metin) olarak üretilemez.

Referans Form tanımlanmış bir STATE'e ulaşıldığında HLK aşağıdaki mimariyi uygulamak zorundadır:

1. İlgili Referans Form klasörü yüklenir.
2. Referans `.png` dosyası ilgili formun değiştirilemez anayasal tasarım otoritesi olarak esas alınır.
3. Referans Formun veri yapısı (`sample-data.json`) ve kullanıcı arayüzü şablonu (`template.html`) yüklenir.
4. Geliştirme aşamasında `sample-data.json`, çalışma zamanında ise gerçek Runtime verileri kullanılır.
5. Referans UI, hedef platformun teknik sınırları içerisinde **En Yüksek Sadakat İlkesi** ile implemente edilir.
6. Çıktı formatı hedef platformun desteklediği en uygun yöntemle belirlenir:
   * Platform PNG/görsel render'ı destekliyorsa → `render.js` → PNG → görsel gönderim.
   * Platform HTML/metin render'ı destekliyorsa → Referans Form verisi, platformun resmi UI bileşenleri (`InlineKeyboardButton`, `<code>`, `<blockquote>`, `<pre>` vb.) kullanılarak uygulanır.
   * Her iki durumda da **Veri Bütünlüğü, İşlevsel Eşdeğerlik ve Görsel Sadakat** doğrulama kriterleri karşılanır.
7. Oluşturulan çıktı hedef platformda kullanıcıya gönderilir.

Referans Form tanımlanmış hiçbir STATE içerisinde eski mesaj tabanlı kullanıcı arayüzü kullanılamaz.

`send_message`, `reply_text` veya benzeri düz metin çıktıları yalnızca Referans Form tanımlanmamış konuşma adımlarında kullanılabilir.

Render işlemi başarısız olduğunda eski mesaj tabanlı kullanıcı arayüzüne geri dönüş (fallback) yapılamaz.

Bu durumda hata kayıt altına alınır ve HLK'nın tanımlı hata yönetimi süreci çalıştırılır.

---

### Amaç

Bu kuralın amacı;

* Referans Form mimarisinin çalışma zamanında eksiksiz uygulanmasını sağlamak,
* Tüm kullanıcı arayüzlerinin Referans UI anayasal tasarım otoritesi altında üretilmesini zorunlu hale getirmek,
* Referans Form tanımlı ekranlarda eski mesaj tabanlı arayüzlerin tekrar kullanılmasını önlemek,
* Runtime'ın hedef platforma uygun implementasyon yöntemini seçmesine olanak tanımak,
* Runtime davranışını Referans UI mimarisi ile En Yüksek Sadakat İlkesi çerçevesinde uyumlu hale getirmektir.

---

### Beklenen Sonuç

* Referans Form tanımlı tüm STATE'lerde kullanıcı arayüzü Referans UI esas alınarak üretilir.
* Çıktı formatı hedef platformun teknik kapasitesine göre belirlenir; PNG veya platform resmi UI bileşenleri kullanılır.
* `send_message` / `reply_text` düz metin yalnızca Referans Form tanımlanmamış adımlarda kullanılır.
* Eski mesaj tabanlı arayüzler Referans Form tanımlı STATE'lerden tamamen kaldırılır.
* Render başarısız olduğunda fallback yerine hata yönetimi çalıştırılır.
* Tüm implementasyonlarda Veri Bütünlüğü, İşlevsel Eşdeğerlik ve Görsel Sadakat doğrulama kriterleri karşılanır.

---

## AR-002_67

### Başlık

**Referans Form Runtime Render Zorunluluğu**

### Kural

Bu kural, Runtime'ın Referans Form tanımlanmış sahnelerde uygulayacağı teknik standardı tanımlar. AR-002_66 Runtime'ın anayasal davranışını, bu kural ise teknik uygulama adımlarını düzenler.

HLK, her STATE geçişinde öncelikle `08_HLK_FLOW_DIAGRAM.md` dosyasını esas alarak bulunduğu sahne için Referans Form tanımlanıp tanımlanmadığını kontrol eder.

Referans Form tanımlanmamış sahnelerde HLK, mevcut Konuşma Arayüzü (Conversation UI) mimarisini kullanmaya devam eder.

Referans Form tanımlanmış sahnelerde ise aşağıdaki teknik uygulama standardı zorunlu olarak uygulanır:

1. İlgili Referans Form klasörü yüklenir ve Referans `.png` dosyası anayasal tasarım otoritesi olarak esas alınır.
2. Referans Formun veri yapısı (`sample-data.json`) DATA CONTRACT olarak yüklenir; Runtime verileri bu sözleşmeye göre doldurulur.
3. Runtime, hedef platformu tespit eder ve platformun teknik kapasitesini değerlendirir.
4. Çıktı formatı, hedef platformun desteklediği resmi bileşenler kullanılarak belirlenir:
   * **Görsel Render Yolu:** Platform görsel çıktıyı destekliyorsa — `render.js` çalıştırılır, çıktı platforma uygun formatta render edilir.
   * **Yerel Bileşen Yolu:** Platform yerel UI bileşenlerini destekliyorsa — Referans Form verisi, platformun resmi bileşenleri (`InlineKeyboardButton`, `<code>`, `<blockquote>`, `<pre>` vb.) kullanılarak uygulanır.
   * Her iki yol da anayasal olarak eşdeğerdir; seçim platform kapasitesine göre Runtime tarafından yapılır.
5. Oluşturulan çıktı, **En Yüksek Sadakat İlkesi** doğrultusunda hedef platformda kullanıcıya sunulur.
6. Çıktı; Veri Bütünlüğü, İşlevsel Eşdeğerlik ve Görsel Sadakat kriterlerine göre doğrulanır.

Referans Form tanımlanmış hiçbir STATE içerisinde kullanıcı arayüzü doğrudan `send_message`, `reply_text` veya benzeri düz metin mesajları ile üretilemez.

Bu yöntem yalnızca Referans Form tanımlanmamış konuşma adımlarında kullanılabilir.

Render işlemi başarısız olduğunda eski mesaj tabanlı kullanıcı arayüzüne geri dönüş (fallback) yapılamaz.

Bu durumda;

* hata kayıt altına alınır,
* ilgili hata yönetim süreci çalıştırılır,
* Runtime davranışı Referans UI anayasal tasarım otoritesini ihlal edecek şekilde değiştirilemez.

Implementasyon yöntemi hedef platforma, kullanılan teknolojiye ve çalışma ortamına göre değişebilir. Bu durum anayasal sapma değildir; yeter ki yukarıdaki doğrulama kriterleri karşılansın.

---

### Amaç

Bu kuralın amacı;

* Runtime'ın Referans Form tanımlı sahnelerde uygulayacağı teknik standardı tanımlamak,
* `08_HLK_FLOW_DIAGRAM.md` ile Runtime davranışı arasındaki teknik bağlantıyı kurmak,
* Hedef platformun teknik kapasitesine göre uygun çıktı formatının seçilmesini sağlamak,
* Referans Form tanımlı ekranlarda eski mesaj tabanlı kullanıcı arayüzlerinin tekrar kullanılmasını teknik olarak önlemek,
* Tüm implementasyon yollarında Veri Bütünlüğü, İşlevsel Eşdeğerlik ve Görsel Sadakat kriterlerinin teknik doğrulamasını zorunlu hale getirmek,
* Implementasyon yöntemi seçiminin platform gerçekliğine dayanmasını ve anayasal sapma sayılmamasını garanti altına almaktır.

---

### Beklenen Sonuç

* Her STATE geçişinde Flow Diagram üzerinden Referans Form kontrolü yapılır.
* Referans Form tanımlı sahnelerde Runtime, hedef platforma uygun implementasyon yöntemini seçer.
* Çıktı formatı (görsel render veya yerel platform bileşenleri) platform kapasitesine göre belirlenir.
* Tüm çıktılar En Yüksek Sadakat İlkesi ile üretilir ve üç doğrulama kriterinden geçer.
* Referans Form tanımlanmamış sahnelerde mevcut Konuşma Arayüzü (Conversation UI) korunur.
* `send_message` / `reply_text` düz metin yalnızca Referans Form tanımlanmamış konuşma adımlarında kullanılır.
* Render başarısız olduğunda fallback uygulanmaz; hata loglanır ve hata yönetimi çalıştırılır.
* Implementasyon yöntemi farklılıkları anayasal sapma sayılmaz.

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

---

## AR-002_70

### Başlık

**STATE_VIDEO_PRODUCTION Runtime Architecture**

### Amaç

HLK'nın `STATE_VIDEO_PRODUCTION` durumuna girişinden, üretim sürecinin anayasal olarak başlatılmasına kadar çalışacak resmi runtime mimarisini tanımlamak.

### Kural

HLK, `STATE_VIDEO_PRODUCTION` durumuna yalnızca anayasal iş akışları tamamlandıktan sonra girebilir.

STATE_VIDEO_PRODUCTION'a giriş için ön koşul:

* STATE_PAYMENT_VERIFICATION aşamasında EVENT_PAYMENT_APPROVED oluşmuş olmalıdır (AR-002_56).
* Yönetici Video Üretim Onayı mevcut olmalıdır (AR-002_56: Yönetici Ödeme Onay Formu → ÖDEMEYİ ONAYLA).

Bu state'e giriş yapıldığında HLK aşağıdaki çalışma sırasını korumak zorundadır.

**Adım 1 — STATE Doğrulaması**

HLK, State Engine (SE-007_3/4/5/6) üzerinden mevcut state'in `STATE_VIDEO_PRODUCTION` olduğunu doğrular.

State geçişi yalnızca aşağıdaki anayasal yol ile gerçekleşebilir (SE-007_4):

```
STATE_PAYMENT_VERIFICATION
→ EVENT_PAYMENT_APPROVED (OLAY-030)
→ STATE_VIDEO_PRODUCTION
```

Bu geçiş dışında STATE_VIDEO_PRODUCTION'a giriş yapılamaz.

**Adım 2 — Brief Lock Doğrulaması**

HLK, brief'in kilitli (Locked) olduğunu doğrular.

Brief onayı SAHNE-12'de alınmış ve STATE_BRIEF_COMPLETED → STATE_SCENARIO_APPROVAL geçişi tamamlanmış olmalıdır (SE-007_4, FD-008_1).

Brief üzerinde değişiklik yapılamaz. Brief içeriği salt okunurdur.

**Adım 3 — Senaryo Onay Doğrulaması**

HLK, senaryo onayının mevcut olduğunu doğrular.

STATE_SCENARIO_APPROVAL aşamasında EVENT_SCENARIO_APPROVED (OLAY-011) oluşmuş olmalıdır (SE-007_5, FD-008_1).

Senaryo onayı olmadan üretim başlatılamaz.

**Adım 4 — Yönetici Video Üretim Onayı Doğrulaması**

HLK, Yönetici Video Üretim Onayının mevcut olduğunu doğrular.

Bu onay, AR-002_56 kapsamında STATE_PAYMENT_VERIFICATION aşamasında yönetici tarafından verilir.

Yönetici onayı olmadan üretim başlatılamaz.

**Adım 5 — Production Runtime Başlatılması**

HLK, Production Runtime'ı başlatır.

Production Runtime; bu mimari tarafından tanımlanan ve yalnızca STATE_VIDEO_PRODUCTION state'ine girişte başlatılan resmi runtime ortamıdır.

Production Runtime başlatıldığı andan itibaren, bu üretime ait tüm işlemler Production Runtime kapsamında yürütülür.

Production Runtime başlatılmadan hiçbir üretim işlemi gerçekleştirilemez.

**Adım 6 — Production Event Oluşturulması**

HLK, ilgili Production Event'i oluşturur.

Oluşturulacak Event: `EVENT_VIDEO_PRODUCTION_STARTED` (OLAY-023, 14_OLAY_KAYIT_MERKEZI.md).

Bu Event;
* Olay Kayıt Merkezi'ne kaydedilir,
* EEC (Execution Event Collector) tarafından toplanır,
* LAC (Live Activity Center) üzerinden izlenebilir hale gelir,
* PID ile ilişkilendirilir.

**Adım 7 — PID Oluşturma Sürecinin Başlatılması**

HLK, PID oluşturma sürecini başlatır.

PID; AR-002_57 (Production ID Mimari Standardı) uyarınca:
* STATE_VIDEO_PRODUCTION state'ine girişte,
* Video Production süreci başlamadan hemen önce,
* Yönetici Video Üretim Onayı sonrasında,
* HLK tarafından otomatik olarak oluşturulur.

PID formatı: `PID-YYYYMMDD-NNNN` (GC_PID_PREFIX, GC_PID_DATE_FORMAT, GC_PID_SEQUENCE_LENGTH, GC_PID_SEQUENCE_START — 01_Global_Configuration.md).

PID oluşturulduğu andan itibaren:
* Production Package kaydına yazılır,
* Bu üretime ait tüm event'ler PID ile ilişkilendirilir,
* Değiştirilemez ve silinemez.

Bu mimari PID oluşturma sürecini başlatır. Gerçek PID üretimi, PID Runtime tarafından yönetilir.

**Adım 8 — Production Package Oluşturma Sürecinin Başlatılması**

HLK, Production Package oluşturma sürecini başlatır.

Production Package; AR-002_58 (Production Package Architecture) ve 16_PRODUCTION_PACKAGE_STANDARD.md uyarınca:
* PID ile ilişkilendirilir,
* Bu üretime ait tüm bilgi, varlık ve Task Package'lerin ana kapsayıcısıdır,
* PID oluşturulduktan hemen sonra HLK tarafından oluşturulur.

Production Package içerisinde:
* Ürün bilgileri,
* Brief verileri,
* Senaryo verileri,
* Kullanıcı tercihleri,
* Araştırma sonuçları,
* Materyal arşivi

bu üretime ait referans paketi olarak saklanır.

Bu mimari Production Package oluşturma sürecini başlatır. Gerçek Production Package üretimi, Production Package Runtime tarafından yönetilir.

**Adım 9 — Task Package Oluşturma Sürecinin Başlatılması**

HLK, Task Package oluşturma sürecini başlatır.

Task Package; Production Package altında, her Agent için özel olarak hazırlanan görev paketidir.

Task Package'ler:
* Her Agent için ayrı ayrı oluşturulur,
* Her Agent yalnızca kendi Task Package'ine erişebilir,
* Production Package'a bağlıdır,
* PID ile ilişkilendirilir.

Bu mimari Task Package oluşturma sürecini başlatır. Gerçek Task Package üretimi, Task Package Runtime tarafından yönetilir.

**Adım 10 — Video Production Pipeline'ın Hazırlanması**

HLK, Video Production Pipeline'ı başlatılmaya hazır hale getirir.

Bu aşamada:
* Tüm ön koşullar doğrulanmıştır (Adım 1-4).
* Production Runtime aktiftir (Adım 5).
* Production Event oluşturulmuştur (Adım 6).
* PID hazırdır (Adım 7).
* Production Package hazırdır (Adım 8).
* Task Package'ler hazırdır (Adım 9).

Video Production Pipeline, tüm bu bileşenler hazır olduktan sonra devreye alınabilir.

---

### Çalışma Sırası Zorunluluğu

Bu mimaride tanımlanan 10 adım, belirtilen sıraya göre yürütülmek zorundadır.

Hiçbir adım atlanamaz.

Her adım tamamlanmadan bir sonraki adıma geçilemez.

Her adımın tamamlanması, ilgili Event sistemi üzerinden kayıt altına alınmalıdır (14_OLAY_KAYIT_MERKEZI.md, EEC).

Runtime sırasında oluşan tüm kararlar Decision History ile ilişkilendirilebilir olmalıdır (MASTER-004, AR-002_22).

---

### Sınırlar ve Kapsam

Bu mimari;
* video üretimini doğrudan gerçekleştirmez,
* yalnızca üretim altyapısını anayasal sıraya göre hazırlar,
* yalnızca Production Runtime başlangıcını tanımlar.

Gerçek Video Production, aşağıdaki bağımsız anayasal mimariler tarafından yönetilir:

| Bileşen | Yöneten Mimari | Referans |
|---|---|---|
| PID Üretimi | PID Runtime | AR-002_57 |
| Production Package | Production Package Runtime | AR-002_58, 16_PRODUCTION_PACKAGE_STANDARD.md |
| Task Package | Task Package Runtime | 20_TASK_ENGINE.md |
| Video Üretimi | Video Production Pipeline | İlgili OR/MR kuralları |

Bu mimari, yukarıdaki bileşenlerin başlatılma sırasını ve ön koşullarını tanımlar; bileşenlerin iç işleyişine karışmaz.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — bu mimari en üst otoriteye tabidir |
| **MASTER** | MASTER-003 | ANA YASA/Kod Uyumluluk — her adım denetlenebilir |
| **MASTER** | MASTER-004 | Karar Mekanizması — nihai karar HLK'nındır |
| **MASTER** | MASTER-009 | Flow Diagram Otoritesi — FD-008_1 bu mimarinin UX referansıdır |
| **AR** | AR-002_56 | STATE_PRICING → STATE_PAYMENT_VERIFICATION → STATE_VIDEO_PRODUCTION geçişi |
| **AR** | AR-002_57 | PID standardı — Adım 7'nin referans mimarisi |
| **AR** | AR-002_58 | Production Package mimarisi — Adım 8'in referans mimarisi |
| **AR** | AR-002_22 | Constitutional Feedback Loop — her adımın denetim döngüsü |
| **SE** | SE-007_3 | STATE_VIDEO_PRODUCTION state tanımı |
| **SE** | SE-007_4 | State geçiş kuralları — STATE_PAYMENT_VERIFICATION → STATE_VIDEO_PRODUCTION |
| **SE** | SE-007_5 | Event tetikleme — EVENT_PAYMENT_APPROVED |
| **SE** | SE-007_6 | State Action Mapping — STATE_VIDEO_PRODUCTION'da çalışacak modüller |
| **FD** | FD-008_1 | Kullanıcı akışı — STATE_VIDEO_PRODUCTION ekran sırası |
| **GC** | GC_PID_PREFIX, GC_PID_DATE_FORMAT, GC_PID_SEQUENCE_LENGTH, GC_PID_SEQUENCE_START | PID format parametreleri (01_Global_Configuration.md) |
| **FEAT** | FEAT-012 | Production Pipeline — bu mimarinin hazırladığı pipeline |
| **OLAY** | OLAY-023, OLAY-024, OLAY-031 | Production event'leri (14_OLAY_KAYIT_MERKEZI.md) |

---

### Beklenen Sonuç

* STATE_VIDEO_PRODUCTION standart hale gelir.
* Production Runtime tek giriş noktası olur.
* PID oluşturma süreci standartlaşır.
* Production Package oluşturma süreci standartlaşır.
* Task Package süreci standartlaşır.
* Video Production başlangıç sırası anayasal olarak tanımlanmış olur.
* Her adım Event sistemi üzerinden kayıt altına alınır.
* Production Runtime, PID Runtime, Production Package Runtime ve Task Package Runtime kendi anayasal mimarileri tarafından bağımsız olarak yönetilir.
* Constitution Scan Engine, STATE_VIDEO_PRODUCTION'a giriş koşullarını ve adım sırasını doğrulayabilir.

---

## AR-002_71

### Başlık

**PID Runtime Architecture**

### Amaç

HLK'nın Production Runtime sırasında Production ID (PID) oluşturma sürecini anayasal olarak standartlaştırmak.

### Kural

HLK, PID oluşturma işlemini yalnızca `STATE_VIDEO_PRODUCTION` süreci başladıktan sonra başlatabilir.

PID oluşturma sürecinin ön koşulu:

* STATE_VIDEO_PRODUCTION Runtime başlatılmış olmalıdır (AR-002_70, Adım 5).
* Production Runtime aktif durumda olmalıdır.
* Yönetici Video Üretim Onayı mevcut olmalıdır (AR-002_56, AR-002_70 Adım 4).

PID, her üretim için yalnızca bir kez oluşturulmalıdır (AR-002_57: PID Tekillik Kuralı).

PID oluşturulmadan;

* Production Package oluşturulamaz (AR-002_58, 16_PRODUCTION_PACKAGE_STANDARD.md).
* Task Package oluşturulamaz (20_TASK_ENGINE.md).
* Video Production Pipeline başlatılamaz (AR-002_70 Adım 10).
* Dijital Varlık kayıtları oluşturulamaz (12_DIGITAL_ASSET_ARCHIVE.md, 13_DIGITAL_ASSET_CATALOG.md).

---

### PID Oluşturma Çalışma Sırası

HLK, PID oluşturma sürecinde aşağıdaki çalışma sırasını korumak zorundadır.

**Adım 1 — PID Oluşturma Koşullarının Doğrulanması**

HLK, PID oluşturma için gerekli tüm ön koşulları doğrular:

* STATE_VIDEO_PRODUCTION state'i aktiftir (SE-007_3).
* Production Runtime başlatılmıştır (AR-002_70).
* Brief Locked durumdadır (AR-002_70 Adım 2).
* Senaryo onayı mevcuttur (AR-002_70 Adım 3).
* Yönetici Video Üretim Onayı mevcuttur (AR-002_70 Adım 4).
* Bu üretim için daha önce bir PID oluşturulmamıştır (AR-002_57: PID Tekillik Kuralı).

Herhangi bir koşul sağlanmıyorsa PID oluşturma süreci başlatılamaz.

**Adım 2 — Global Configuration PID Standartlarının Kullanılması**

HLK, PID üretiminde Global Configuration içerisinde tanımlanan PID standartlarını kullanır (01_Global_Configuration.md):

| Parametre | Değer | Açıklama |
|---|---|---|
| `GC_PID_PREFIX` | `PID` | Production ID ön eki |
| `GC_PID_DATE_FORMAT` | `YYYYMMDD` | PID tarih formatı |
| `GC_PID_SEQUENCE_LENGTH` | `4` | PID sıra numarası basamak sayısı (sıfır dolgulu) |
| `GC_PID_SEQUENCE_START` | `0001` | PID günlük sıra numarası başlangıç değeri |

HLK, PID formatını bu GC parametrelerine göre oluşturur:

```
PID-{YYYYMMDD}-{NNNN}
```

HLK, GC parametrelerini doğrudan kullanır. Hiçbir modül kendi PID formatını tanımlayamaz.

**Adım 3 — Benzersiz PID Üretilmesi**

HLK, benzersiz bir PID üretir.

PID üretiminde:

* Günlük sıra numarası `GC_PID_SEQUENCE_START` değerinden başlar.
* Aynı gün içerisinde her yeni üretim için sıra numarası bir artırılır.
* Sıra numarası `GC_PID_SEQUENCE_LENGTH` kadar haneye sıfır dolgulu olarak yazılır.
* Günlük sıra numarası takibi HLK tarafından merkezi olarak yönetilir.

Hiçbir modül kendi PID'sini üretemez (AR-002_57: PID Merkeziyet Kuralı).

**Adım 4 — PID'nin Production Runtime'a Bağlanması**

HLK, üretilen PID'yi ilgili Production Runtime'a bağlar.

Bu bağlantı ile:

* PID, bu üretimin Production Runtime içerisindeki tek resmi kimliği haline gelir.
* Production Runtime içerisinde gerçekleşen tüm işlemler bu PID ile ilişkilendirilir.
* PID, Production Runtime yaşam döngüsü boyunca sabit kalır.

**Adım 5 — PID Oluşturma Event'inin Üretilmesi**

HLK, PID oluşturma Event'ini üretir.

Bu Event:

* Olay Kayıt Merkezi'ne kaydedilir (14_OLAY_KAYIT_MERKEZI.md).
* EEC (Execution Event Collector) tarafından toplanır (22_EXECUTION_EVENT_COLLECTOR.md).
* LAC (Live Activity Center) üzerinden izlenebilir hale gelir (FEAT-015).
* PID alanı zorunlu olarak içerir (AR-002_57: PID Zorunluluk Kuralı).
* PID ile ilişkilendirilir.

PID oluşturma Event'i, Production Package oluşturma sürecinin tetikleyicisidir (OLAY-031: EVENT_PRODUCTION_PACKAGE_CREATED).

**Adım 6 — PID'nin Production Package Ana Referansı Olarak Kullanılması**

HLK, oluşturulan PID'yi Production Package'in ana referansı olarak kullanır (AR-002_58, 16_PRODUCTION_PACKAGE_STANDARD.md).

Bu aşamada:

* PID, Production Package kaydına yazılır.
* Production Package, PID üzerinden ilişkilendirilir.
* PID ↔ Production Package birebir ilişkisi kurulur (16_PRODUCTION_PACKAGE_STANDARD.md: Her PID yalnızca bir adet Production Package oluşturabilir).

---

### PID Bütünlük Kuralları

**Değiştirilemezlik:**

PID oluşturulduktan sonra değiştirilmemelidir (AR-002_57).

PID, üretim yaşam döngüsü boyunca sabit kalır. Üretim kayıtları arşivlense dahi PID bilgisi korunur.

**Tekillik:**

Aynı üretim için ikinci bir PID oluşturulamaz (AR-002_57: PID Tekillik Kuralı).

Her PID yalnızca bir üretim paketini temsil eder. Aynı PID birden fazla üretim için kullanılamaz.

**Merkeziyet:**

PID yalnızca HLK tarafından, STATE_VIDEO_PRODUCTION girişinde, merkezi olarak oluşturulur (AR-002_57: PID Merkeziyet Kuralı).

Hiçbir modül, servis, ajan veya sistem bileşeni kendi PID'sini oluşturamaz. Tüm bileşenler ortak PID'yi kullanmak zorundadır.

---

### PID İlişkilendirme Kapsamı

PID oluşturulduktan sonra, aşağıdaki tüm Production süreçleri ve sistem bileşenleri bu PID üzerinden ilişkilendirilmelidir:

| Bileşen | İlişkilendirme | Referans |
|---|---|---|
| Production Package | Birebir — PID, Production Package'in ana referansıdır | AR-002_58, 16_PRODUCTION_PACKAGE_STANDARD.md |
| Task Package'ler | PID üzerinden Production Package'e bağlı | 20_TASK_ENGINE.md |
| Event Kayıtları | PID alanı zorunlu | AR-002_57, 14_OLAY_KAYIT_MERKEZI.md |
| Decision History | Tüm kararlar PID üzerinden ilişkilendirilir | 15_KARAR_GEREKCESI_STANDARDI.md |
| Digital Asset Archive | Dijital varlıklar PID ile etiketlenir | 12_DIGITAL_ASSET_ARCHIVE.md |
| Digital Asset Catalog | Varlık kataloğu PID referansı içerir | 13_DIGITAL_ASSET_CATALOG.md |
| Delivery Süreçleri | Teslimat kayıtları PID ile ilişkilendirilir | AR-002_36 |
| Production Log'ları | Tüm log'lar PID altında toplanır | EEC, LAC |
| Kalite Raporları | Kalite kayıtları PID referanslıdır | QR-004 |
| Kredi/Maliyet Kayıtları | Servis kullanımı ve kredi tüketimi PID ile izlenir | Operasyon Veri Merkezi |

---

### Sınırlar ve Kapsam

Bu mimari;

* PID'nin nasıl oluşturulacağını, hangi sırayla ve hangi koşullarda başlatılacağını tanımlar,
* PID'nin formatını, tekillik ve merkeziyet kurallarını uygular.

Bu mimari;

* PID format standardını tanımlamaz — format AR-002_57 tarafından yönetilir.
* PID'nin saklanacağı veri yapısını tanımlamaz — bu, depolama mimarisinin sorumluluğundadır.
* PID sıra numarası üretim algoritmasını tanımlamaz — bu, HLK'nın iç uygulama detayıdır.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — bu mimari en üst otoriteye tabidir |
| **MASTER** | MASTER-003 | ANA YASA/Kod Uyumluluk — PID oluşturma denetlenebilir |
| **MASTER** | MASTER-004 | Karar Mekanizması — PID oluşturma kararı HLK'nındır |
| **GC** | GC_PID_PREFIX, GC_PID_DATE_FORMAT, GC_PID_SEQUENCE_LENGTH, GC_PID_SEQUENCE_START | PID format parametreleri (01_Global_Configuration.md) |
| **AR** | AR-002_56 | STATE_PRICING → STATE_VIDEO_PRODUCTION geçişi |
| **AR** | AR-002_57 | PID Mimari Standardı — format, tekillik, merkeziyet, zorunluluk |
| **AR** | AR-002_58 | Production Package mimarisi — PID ↔ Production Package birebir ilişkisi |
| **AR** | AR-002_70 | STATE_VIDEO_PRODUCTION Runtime — PID oluşturmanın ön koşulu |
| **SE** | SE-007_3 | STATE_VIDEO_PRODUCTION state tanımı |
| **SE** | SE-007_4 | State geçiş kuralları |
| **SE** | SE-007_5 | Event tetikleme — PID oluşturma Event'i |
| **FD** | FD-008_1 | Kullanıcı akışı — STATE_VIDEO_PRODUCTION ekran sırası |
| **OLAY** | OLAY-023 | EVENT_VIDEO_PRODUCTION_STARTED — PID zorunlu alan |
| **OLAY** | OLAY-024 | EVENT_VIDEO_PRODUCTION_COMPLETED — PID zorunlu alan |
| **OLAY** | OLAY-031 | EVENT_PRODUCTION_PACKAGE_CREATED — PID oluşturulması ile tetiklenir |
| **FEAT** | FEAT-012 | Production Pipeline — PID bu pipeline'ın kimlik katmanıdır |
| **FEAT** | FEAT-015 | Live Activity Center — PID üzerinden üretim izleme |

---

### Beklenen Sonuç

* PID oluşturma süreci standart hale gelir.
* Her üretim tek bir PID ile yönetilir.
* Production Package için anayasal referans oluşur.
* Üretim sürecinin tüm bileşenleri ortak PID üzerinden ilişkilendirilir.
* Runtime içerisinde PID bütünlüğü garanti altına alınır.
* Event kayıtlarında PID alanı zorunlu olarak bulunur.
* Decision History, Digital Asset Archive, Digital Asset Catalog ve Delivery süreçleri PID üzerinden çapraz referanslanabilir hale gelir.
* Hiçbir modül kendi PID'sini oluşturamaz; tüm sistem ortak PID standardını kullanır.
* PID oluşturma süreci Constitution Scan Engine tarafından doğrulanabilir.

---

## AR-002_72

### Başlık

**Production Package Runtime Architecture**

### Amaç

HLK'nın PID oluşturulduktan sonra Production Package'i anayasal kurallara uygun şekilde oluşturmasını, yönetmesini ve Production Runtime süresince tek resmi üretim kapsayıcısı olarak kullanmasını standartlaştırmak.

### Kural

HLK, Production Package'i yalnızca geçerli bir PID oluşturulduktan sonra oluşturabilir.

Production Package oluşturmanın ön koşulu:

* PID oluşturulmuş ve geçerli olmalıdır (AR-002_57, AR-002_71).
* PID, Production Runtime'a bağlanmış olmalıdır (AR-002_71 Adım 4).
* PID oluşturma Event'i üretilmiş olmalıdır (AR-002_71 Adım 5).
* STATE_VIDEO_PRODUCTION state'i aktif olmalıdır (SE-007_3, AR-002_70).

Her PID için yalnızca bir adet Production Package oluşturulabilir (AR-002_58, 16_PRODUCTION_PACKAGE_STANDARD.md: Her PID yalnızca bir adet Production Package oluşturabilir).

Production Package oluşturulmadan;

* Task Package oluşturulamaz (AR-002_47, 20_TASK_ENGINE.md).
* Video Production Pipeline başlatılamaz (AR-002_70 Adım 10).
* Dijital varlıklar ilişkilendirilemez (12_DIGITAL_ASSET_ARCHIVE.md, 13_DIGITAL_ASSET_CATALOG.md).
* Üretim logları kaydedilemez (EEC, LAC).
* Quality Control başlatılamaz (QR-004, FEAT-010).
* Delivery süreci başlatılamaz (AR-002_36).

---

### Production Package Oluşturma Çalışma Sırası

HLK, Production Package oluşturma sürecinde aşağıdaki çalışma sırasını korumak zorundadır.

**Adım 1 — PID Geçerliliğinin Doğrulanması**

HLK, PID'nin geçerliliğini doğrular:

* PID oluşturulmuştur (AR-002_71 Adım 3).
* PID formatı GC standartlarına uygundur (`PID-YYYYMMDD-NNNN`).
* PID benzersizdir — aynı PID ile daha önce bir Production Package oluşturulmamıştır.
* PID, Production Runtime'a bağlanmıştır (AR-002_71 Adım 4).
* PID değiştirilmemiştir (AR-002_57: PID değiştirilemez).

PID geçerliliği doğrulanmadan Production Package oluşturulamaz.

**Adım 2 — Production Package'in Oluşturulması**

HLK, Production Package'i oluşturur.

Production Package; AR-002_58 ve 16_PRODUCTION_PACKAGE_STANDARD.md'de tanımlanan yapıya uygun olarak, 21 bölümden oluşan ana üretim kapsayıcısıdır.

Production Package oluşturulduğunda:

* Production Package, PID'ye bağlanır (birebir ilişki).
* Production Package, Production Runtime içerisinde aktif kapsayıcı haline gelir.
* Production Package Engine (FEAT-014), Production Package'in yönetiminden sorumlu Feature olarak devreye girer.

Production Package, WF-008 (Video Production) workflow'u kapsamında oluşturulur (09_WORKFLOW_MANIFEST.md, 11_WORKFLOW_FEATURE_MAP.md).

**Adım 3 — Production Metadata'nın Oluşturulması**

HLK, Production Metadata'yı oluşturur ve Production Package'e yazar.

Production Metadata (16_PRODUCTION_PACKAGE_STANDARD.md, Bölüm 2):

* Üretim tarihi ve saati,
* Üretim türü (İlk Üretim / Revizyon),
* Üretim durumu (Başlatıldı / Devam Ediyor / Tamamlandı / Arşivlendi),
* Sürüm bilgisi (V1.0, V1.1, vb.),
* PID referansı,
* İlgili Workflow referansı (WF-008).

Production Metadata, Production Package'in zorunlu bölümüdür ve Production Package oluşturulur oluşturulmaz doldurulur.

**Adım 4 — Production Package'in PID ile İlişkilendirilmesi**

HLK, Production Package'i ilgili PID ile ilişkilendirir.

Bu ilişkilendirme ile:

* PID ↔ Production Package birebir bağlantısı kurulur (AR-002_58).
* Production Package kaydına PID yazılır.
* PID, Production Package'in birincil referans anahtarı haline gelir.
* Tüm alt bileşenler (Task Package, Event, Log, Varlık) bu PID üzerinden Production Package'e bağlanır.

**Adım 5 — Production Package Oluşturma Event'inin Üretilmesi**

HLK, Production Package oluşturma Event'ini üretir.

Oluşturulacak Event: `EVENT_PRODUCTION_PACKAGE_CREATED` (OLAY-031, 14_OLAY_KAYIT_MERKEZI.md).

Bu Event:

* Olay Kayıt Merkezi'ne kaydedilir,
* EEC (Execution Event Collector) tarafından toplanır,
* LAC (Live Activity Center) üzerinden izlenebilir hale gelir,
* PID alanı zorunlu olarak içerir,
* WF-008 workflow'una bağlıdır,
* FEAT-014 (Production Package Engine) Feature'ı ile ilişkilendirilir.

OLAY-031'in tetikleyicisi PID oluşturulmasıdır. Olay çıktısı olarak Task Package'ler hazırlanır ve Agent'lar görevlendirilir.

**Adım 6 — Production Runtime Boyunca Kayıtların Toplanması**

HLK, Production Runtime süresince oluşacak tüm kayıtları bu Production Package altında toplar.

Production Package, Production Runtime tamamlanıncaya kadar aktif üretim kapsayıcısı olarak kullanılır.

---

### Production Package Kapsamındaki Bileşenler

Production Runtime süresince aşağıdaki tüm bileşenler, ilgili anayasal standartlara uygun olarak aynı Production Package altında ilişkilendirilmelidir:

| # | Bileşen | Anayasal Referans | Zorunluluk |
|---|---|---|---|
| 1 | **Brief** | FD-008_1, SAHNE-12 | Zorunlu |
| 2 | **Senaryo** | AR-002_65, SAHNE-13 | Zorunlu |
| 3 | **Prompt Setleri** | 16_PRODUCTION_PACKAGE_STANDARD.md | Zorunlu |
| 4 | **Task Package'ler** | AR-002_47, 20_TASK_ENGINE.md | Zorunlu |
| 5 | **Araştırma Sonuçları** | AR-002_13, AR-002_20 | Zorunlu |
| 6 | **Referans Görseller** | AR-002_24, AR-002_25, AR-002_26 | Zorunlu |
| 7 | **Kullanıcı Dosyaları** | AR-002_15 | İsteğe Bağlı |
| 8 | **Dijital Varlıklar** | 12_DIGITAL_ASSET_ARCHIVE.md, 13_DIGITAL_ASSET_CATALOG.md | Zorunlu |
| 9 | **Ses Dosyaları** | AR-002_29, AR-002_30, AR-002_31 | İsteğe Bağlı |
| 10 | **Video Parametreleri** | SAHNE-03 ~ SAHNE-08 | Zorunlu |
| 11 | **Servis Kullanımları** | Operasyon Veri Merkezi | Zorunlu |
| 12 | **Agent Logları** | SE-007_1, SE-007_2 | Zorunlu |
| 13 | **Event Logları** | 14_OLAY_KAYIT_MERKEZI.md, EEC | Zorunlu |
| 14 | **Kalite Raporları** | QR-004, FEAT-010 | Zorunlu |
| 15 | **Revizyon Geçmişi** | AR-002_56 | İsteğe Bağlı |
| 16 | **Teslim Bilgileri** | AR-002_36 | Zorunlu |
| 17 | **Karar Gerekçeleri** | 15_KARAR_GEREKCESI_STANDARDI.md | Zorunlu |
| 18 | **Nihai Video** | AR-002_36 | Zorunlu |

---

### Erişim ve İzolasyon Kuralları

Production Package'in anayasal erişim kuralları (AR-002_58, 16_PRODUCTION_PACKAGE_STANDARD.md):

* Production Package'in tamamına yalnızca HLK erişebilir.
* Hiçbir Agent doğrudan Production Package'in tamamına erişemez.
* Agent'lar yalnızca kendilerine atanmış Task Package üzerinden işlem yapmalıdır (AR-002_47).
* Her Agent yalnızca kendi Task Package'ine erişebilir; diğer Task Package'lere erişemez.
* Yönetici, Yönetici formları aracılığıyla Production Package özetine erişebilir.
* Kullanıcı yalnızca nihai çıktılara (video, teklif, senaryo) erişebilir.

---

### Production Package Yaşam Döngüsü

Production Package, Production Runtime tamamlanıncaya kadar aktif üretim kapsayıcısı olarak kullanılmalıdır.

```
STATE_VIDEO_PRODUCTION Girişi (AR-002_70)
    ↓
PID Oluşturulur (AR-002_57, AR-002_71)
    ↓
Production Package Oluşturulur (bu mimari)
    ↓
EVENT_PRODUCTION_PACKAGE_CREATED (OLAY-031)
    ↓
Production Metadata Doldurulur
    ↓
Task Package'ler Oluşturulur (AR-002_47, 20_TASK_ENGINE.md)
    ↓
Agent'lar Görevlendirilir
    ↓
Video Üretimi Gerçekleşir
    ↓
Kalite Kontrol Yapılır
    ↓
Nihai Video Teslim Edilir
    ↓
Production Package Arşivlenir
```

Üretim tamamlandıktan sonra:

* Production Package arşivlenir (16_PRODUCTION_PACKAGE_STANDARD.md).
* Production Package silinemez; yalnızca anayasal kurallar doğrultusunda arşivlenebilir.
* Arşivlenen Production Package, Digital Asset Archive ve Digital Asset Catalog ile ilişkilendirilir.
* PID bilgisi arşivde korunur.

---

### Sınırlar ve Kapsam

Bu mimari;

* Production Package'in nasıl oluşturulacağını, hangi sırayla ve hangi koşullarda başlatılacağını tanımlar,
* Production Package'in kapsadığı bileşenleri ve ilişkilendirme kurallarını belirler,
* Production Package'in yaşam döngüsünü ve erişim kurallarını uygular.

Bu mimari;

* Production Package'in iç yapısını tanımlamaz — yapı AR-002_58 ve 16_PRODUCTION_PACKAGE_STANDARD.md tarafından yönetilir.
* Task Package'lerin iç yapısını tanımlamaz — bu AR-002_47 ve 20_TASK_ENGINE.md'nin sorumluluğundadır.
* PID standardını tanımlamaz — bu AR-002_57'nin sorumluluğundadır.
* Production Package'in depolama yapısını tanımlamaz — bu, depolama mimarisinin sorumluluğundadır.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — bu mimari en üst otoriteye tabidir |
| **MASTER** | MASTER-003 | ANA YASA/Kod Uyumluluk — Production Package denetlenebilir |
| **MASTER** | MASTER-004 | Karar Mekanizması — Production Package oluşturma kararı HLK'nındır |
| **AR** | AR-002_36 | Scene Delivery — teslim süreci Production Package ile ilişkilidir |
| **AR** | AR-002_47 | Task Package Engine — Task Package'lerin üst katmanı |
| **AR** | AR-002_56 | STATE_VIDEO_PRODUCTION geçiş zinciri |
| **AR** | AR-002_57 | PID standardı — Production Package'in birincil referansı |
| **AR** | AR-002_58 | Production Package Architecture — yapısal mimari (WHAT) |
| **AR** | AR-002_70 | STATE_VIDEO_PRODUCTION Runtime — giriş noktası |
| **AR** | AR-002_71 | PID Runtime — PID oluşturma ön koşulu |
| **SE** | SE-007_3 | STATE_VIDEO_PRODUCTION state tanımı |
| **SE** | SE-007_6 | State Action Mapping — Production Package Engine aktivasyonu |
| **WF** | WF-008 | Video Production workflow'u (09_WORKFLOW_MANIFEST.md) |
| **FEAT** | FEAT-012 | Production Pipeline |
| **FEAT** | FEAT-014 | Production Package Engine — Production Package yönetiminden sorumlu |
| **FEAT** | FEAT-015 | Live Activity Center — PID üzerinden üretim izleme |
| **OLAY** | OLAY-031 | EVENT_PRODUCTION_PACKAGE_CREATED |
| **PKG** | 16_PRODUCTION_PACKAGE_STANDARD.md | Production Package yapı, bölüm ve yaşam döngüsü standardı |
| **KARAR** | 15_KARAR_GEREKCESI_STANDARDI.md | Decision History — Production Package altında saklanır |
| **VARLIK** | 12_DIGITAL_ASSET_ARCHIVE.md | Dijital varlıklar PID üzerinden ilişkilendirilir |
| **VARLIK** | 13_DIGITAL_ASSET_CATALOG.md | Varlık kataloğu PID referansı içerir |

---

### Beklenen Sonuç

* Production Package oluşturma süreci standart hale gelir.
* Her üretim tek bir Production Package ile yönetilir.
* Production Runtime boyunca oluşan tüm üretim bileşenleri tek resmi kapsayıcı altında toplanır.
* PID, Task Package, Event, Digital Asset, Quality Control ve Delivery süreçleri aynı Production Package üzerinden ilişkilendirilir.
* Production Runtime mimarisi anayasal olarak tamamlanmış olur.
* Hiçbir Agent Production Package'in tamamına erişemez; veri izolasyonu korunur.
* Production Package silinemez; yalnızca arşivlenebilir.
* Constitution Scan Engine, Production Package oluşturma koşullarını ve adım sırasını doğrulayabilir.

---

## AR-002_73

### Başlık

**Production Event Runtime Architecture**

### Amaç

Production Runtime boyunca oluşan tüm üretim olaylarının (Production Event), anayasal olarak standartlaştırılmasını, Event yaşam döngüsünün tek merkezden yönetilmesini ve Production Package ile tam ilişkilendirilmesini sağlamak.

### Kural

HLK, Production Runtime sırasında meydana gelen tüm üretim işlemlerini yalnızca resmi Production Event'leri üzerinden yönetmelidir.

Production Event'lerin kaynağı ve standardı:

* Tüm Event'lerin tek resmi tanım kaynağı **14_OLAY_KAYIT_MERKEZI.md** dosyasıdır (SE-007_5: Event Ownership).
* Her Event, Olay Kayıt Merkezi'nde tanımlanan Teknik Sabit, Olay Kimliği (OLAY-NNN), PID zorunluluğu ve diğer alanlara uygun olmalıdır.
* Event'lerin runtime'da toplanması ve izlenmesi **EEC (Execution Event Collector)** tarafından yönetilir (22_EXECUTION_EVENT_COLLECTOR.md).

---

### Production Event Zorunluluk İlkesi

Production Runtime başladığı andan itibaren oluşan her önemli operasyon bir Production Event üretmelidir.

Her Production Event:

* yalnızca bir kez üretilmelidir (aynı operasyon için mükerrer Event oluşturulamaz),
* benzersiz bir EventID taşımalıdır (14_OLAY_KAYIT_MERKEZI.md standardı),
* ilgili PID ile ilişkilendirilmelidir (AR-002_57: PID Zorunluluk Kuralı),
* ilgili Production Package ile ilişkilendirilmelidir (AR-002_58, AR-002_72),
* ilgili State bilgisini taşımalıdır (SE-007_3/5),
* ilgili Workflow referansını içermelidir (09_WORKFLOW_MANIFEST.md, WF-008),
* ilgili Feature referansını içermelidir (10_FEATURE_REGISTRY.md),
* ilgili Module bilgisini taşımalıdır (06_Module_Rule.md, ilgili MR kuralları).

Production Event oluşturulmadan;

* sonraki Production adımına geçilemez,
* ilgili Runtime işlemi tamamlanmış kabul edilemez.

Bu ilke, AR-002_70 (STATE_VIDEO_PRODUCTION Runtime) ve AR-002_71 (PID Runtime) içerisinde tanımlanan adım sıralarının her birinin Event üretimi ile kayıt altına alınmasını garanti eder.

---

### Production Event Çalışma Sırası

Her Production Event için HLK aşağıdaki çalışma sırasını korumak zorundadır.

**Adım 1 — Event'in Olay Kayıt Merkezi Standardına Uygun Oluşturulması**

HLK, Event'i 14_OLAY_KAYIT_MERKEZI.md standardına uygun olarak oluşturur.

Her Event için zorunlu alanlar:

| Alan | Açıklama | Referans |
|---|---|---|
| Olay Kimliği (OLAY-NNN) | Benzersiz olay numarası | 14_OLAY_KAYIT_MERKEZI.md |
| Teknik Sabit | `EVENT_` ön ekli sabit adı | 14_OLAY_KAYIT_MERKEZI.md |
| PID | Production ID | AR-002_57 (Zorunlu) |
| Açıklama | Olayın ne olduğu | 14_OLAY_KAYIT_MERKEZI.md |
| Kaynak Durum | Event'in tetiklendiği State | SE-007_5 |
| Hedef Durum | Event'in yönlendirdiği State | SE-007_5 |
| Üreten Bileşen | Event'i üreten modül/servis | 14_OLAY_KAYIT_MERKEZI.md |
| İlgili Workflow | WF referansı (WF-008) | 09_WORKFLOW_MANIFEST.md |
| İlgili Feature | FEAT referansı | 10_FEATURE_REGISTRY.md |

**Adım 2 — Event Yaşam Döngüsünün Tamamlanması**

HLK, her Event'in yaşam döngüsünü eksiksiz tamamlar.

Event yaşam döngüsü:

```
Event Oluşturulur
    ↓
Event Kaydedilir (Olay Kayıt Merkezi)
    ↓
Event Toplanır (EEC)
    ↓
Event Görüntülenir (LAC)
    ↓
Event Loglanır (Production Package → Event Logları)
    ↓
Event Tetikleyici Olarak Çalışır (sonraki State'e geçiş)
    ↓
Event Yaşam Döngüsü Tamamlanır
```

Yaşam döngüsü tamamlanmamış bir Event, geçerli kabul edilmez.

**Adım 3 — Event'in Production Package Altında Kayıt Altına Alınması**

HLK, her Production Event'i Production Package altında kayıt altına alır.

Production Package'in **Event Logları** bölümü (16_PRODUCTION_PACKAGE_STANDARD.md, Bölüm 16), Production Runtime boyunca oluşan tüm Event'lerin resmi kayıt noktasıdır.

Her Event kaydı:
* PID ile ilişkilendirilir,
* EventID ile indekslenir,
* Production Package içerisinde kronolojik olarak saklanır.

**Adım 4 — Event'in Event Loglarına Yazılması**

HLK, Event'i Event Loglarına yazar.

Event Logları:
* Production Package altında tutulur (16_PRODUCTION_PACKAGE_STANDARD.md, Bölüm 16),
* EEC tarafından toplanır (22_EXECUTION_EVENT_COLLECTOR.md),
* PID üzerinden sorgulanabilir,
* Kronolojik olarak sıralanır.

**Adım 5 — Event'in Decision History ile İlişkilendirilmesi**

HLK, Event'i Decision History ile ilişkilendirilebilir hale getirir.

Production Package'in **Karar Gerekçeleri (Decision History)** bölümü (15_KARAR_GEREKCESI_STANDARDI.md), Event'ler aracılığıyla tetiklenen kararları ve bu kararların sonuçlarını kaydeder.

Event → Decision History ilişkisi:
* Bir Event, bir kararı tetikleyebilir.
* Bir karar, bir veya birden fazla Event üretebilir.
* Event ve Decision History kayıtları PID üzerinden çapraz referanslanabilir.

**Adım 6 — Event'in EEC Tarafından İzlenmesi**

HLK, her Event'in EEC (Execution Event Collector) tarafından izlenebilir olmasını sağlar.

EEC (22_EXECUTION_EVENT_COLLECTOR.md):
* Event'i `emit_event()` ile toplar,
* Event tipini (EECEventType) sınıflandırır,
* Yürütme fazını (ExecutionPhase: PRE_CHECK / EXECUTE / POST_CHECK) belirler,
* Event'i kalıcı kayıt altına alır,
* PID ile ilişkilendirir.

Her Production Event, EEC tarafından toplanmadan tamamlanmış kabul edilmez.

**Adım 7 — Event'in LAC Tarafından Gerçek Zamanlı Görüntülenmesi**

HLK, her Event'in LAC (Live Activity Center) tarafından gerçek zamanlı görüntülenebilir olmasını sağlar.

LAC (FEAT-015):
* Event akışını PID bazında canlı olarak gösterir,
* Yönetici tarafından izlenebilir,
* Event'lere müdahale edemez (salt okunur),
* PID seçimi ile ilgili üretimin Event akışını filtreler.

---

### Production Runtime Event Kategorileri

Production Runtime sırasında oluşan Event'ler aşağıdaki anayasal süreçlerin tetikleyicisi olarak kullanılmalıdır:

| Kategori | Event Örnekleri | Tetiklediği Süreç | Referans |
|---|---|---|---|
| **Üretim Başlangıcı** | `EVENT_VIDEO_PRODUCTION_STARTED` (OLAY-023) | Production Pipeline başlatılır | AR-002_70 Adım 6 |
| **PID** | PID oluşturma Event'i | Production Package oluşturulur | AR-002_71 Adım 5 |
| **Production Package** | `EVENT_PRODUCTION_PACKAGE_CREATED` (OLAY-031) | Task Package'ler oluşturulur | AR-002_72 Adım 5 |
| **Task Package** | Task Package oluşturma Event'i | Agent'lar görevlendirilir | AR-002_47 |
| **Executor** | Executor başlangıç/tamamlanma Event'leri | AR-002_22 Feedback Loop | EEC |
| **Quality Control** | Kalite kontrol Event'leri | Kalite raporu oluşturulur | QR-004, FEAT-010 |
| **Archive** | Arşivleme Event'i | Digital Asset Archive güncellenir | 12_DIGITAL_ASSET_ARCHIVE.md |
| **Catalog** | Kataloglama Event'i | Digital Asset Catalog güncellenir | 13_DIGITAL_ASSET_CATALOG.md |
| **Delivery** | Teslimat Event'i | Kullanıcıya video gönderilir | AR-002_36 |
| **Session Completion** | `EVENT_VIDEO_PRODUCTION_COMPLETED` (OLAY-024) | STATE_SESSION_COMPLETED | SE-007_4 |

Bu liste sınırlayıcı değildir. HLK, Production Runtime geliştikçe yeni Event kategorileri eklenebilir. Her yeni Event kategorisi, 14_OLAY_KAYIT_MERKEZI.md'de resmi olarak tanımlanmalıdır.

---

### Event Bütünlük Kuralları

**Değiştirilemezlik:**

Production Event'leri geriye dönük değiştirilemez.

Bir Event oluşturulduktan ve kaydedildikten sonra içeriği değiştirilemez. Event kaydı, üretim yaşam döngüsünün değiştirilemez tarihsel kaydıdır.

**Silinemezlik:**

Production Event'leri silinemez veya yeniden üretilemez.

Bir Event silinemez. Aynı operasyon için mükerrer Event oluşturulamaz. Event kayıtları, üretim arşivlense dahi korunur.

**Tamamlanma Zorunluluğu:**

Her Production Event, yaşam döngüsünü tamamlamak zorundadır (Adım 2).

Yaşam döngüsü tamamlanmamış Event'ler, bağlı oldukları Production adımının tamamlanmasını engeller.

**İzlenebilirlik:**

Production Runtime tamamlandıktan sonra tüm Event kayıtları:

* ilgili Production Package içerisinde korunmalı (16_PRODUCTION_PACKAGE_STANDARD.md, Bölüm 16),
* PID üzerinden sorgulanabilir olmalı,
* gerektiğinde denetlenebilir olmalı,
* Decision History ile çapraz referanslanabilir olmalıdır (15_KARAR_GEREKCESI_STANDARDI.md).

---

### Sınırlar ve Kapsam

Bu mimari;

* Production Event'lerin runtime davranışını, yaşam döngüsünü ve ilişkilendirme kurallarını tanımlar,
* Event'lerin EEC, LAC, Production Package ve Decision History ile entegrasyonunu yönetir.

Bu mimari;

* Event'lerin teknik tanımını yapmaz — tüm Event tanımları 14_OLAY_KAYIT_MERKEZI.md'nin sorumluluğundadır (SE-007_5: Event Ownership).
* EEC'nin iç yapısını tanımlamaz — EEC standardı 22_EXECUTION_EVENT_COLLECTOR.md tarafından yönetilir.
* LAC'in iç yapısını tanımlamaz — LAC mimarisi FEAT-015 tarafından yönetilir.
* Yeni Event'ler tanımlamaz — yeni Event'ler yalnızca 14_OLAY_KAYIT_MERKEZI.md'de tanımlanabilir.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — bu mimari en üst otoriteye tabidir |
| **MASTER** | MASTER-003 | ANA YASA/Kod Uyumluluk — Event kayıtları denetlenebilir |
| **MASTER** | MASTER-004 | Karar Mekanizması — Event tetikleme kararları HLK'nındır |
| **AR** | AR-002_22 | Constitutional Feedback Loop — Event'ler Feedback Loop'u tetikler |
| **AR** | AR-002_36 | Scene Delivery — Delivery Event'leri ile ilişki |
| **AR** | AR-002_47 | Task Package Engine — Task Package Event'leri |
| **AR** | AR-002_57 | PID standardı — PID alanı tüm Event'lerde zorunlu |
| **AR** | AR-002_58 | Production Package Architecture |
| **AR** | AR-002_70 | STATE_VIDEO_PRODUCTION Runtime — Event zincirinin başlangıcı |
| **AR** | AR-002_71 | PID Runtime — PID oluşturma Event'i |
| **AR** | AR-002_72 | Production Package Runtime — EVENT_PRODUCTION_PACKAGE_CREATED |
| **SE** | SE-007_3 | State tanımları |
| **SE** | SE-007_4 | State geçiş kuralları — Event'ler geçişleri tetikler |
| **SE** | SE-007_5 | State Event Trigger Architecture — Event ↔ State ilişkisi |
| **WF** | WF-008 | Video Production workflow'u (09_WORKFLOW_MANIFEST.md) |
| **FEAT** | FEAT-010 | Quality Control — QC Event'leri |
| **FEAT** | FEAT-012 | Production Pipeline |
| **FEAT** | FEAT-014 | Production Package Engine |
| **FEAT** | FEAT-015 | Live Activity Center — gerçek zamanlı Event izleme |
| **OLAY** | 14_OLAY_KAYIT_MERKEZI.md | Tüm Event tanımlarının tek resmi kaynağı (Single Source of Truth) |
| **OLAY** | OLAY-023 | EVENT_VIDEO_PRODUCTION_STARTED |
| **OLAY** | OLAY-024 | EVENT_VIDEO_PRODUCTION_COMPLETED |
| **OLAY** | OLAY-031 | EVENT_PRODUCTION_PACKAGE_CREATED |
| **EEC** | 22_EXECUTION_EVENT_COLLECTOR.md | Event toplama, sınıflandırma ve izleme |
| **KARAR** | 15_KARAR_GEREKCESI_STANDARDI.md | Decision History — Event ↔ Karar ilişkisi |
| **PKG** | 16_PRODUCTION_PACKAGE_STANDARD.md | Event Logları bölümü (Bölüm 16) |
| **VARLIK** | 12_DIGITAL_ASSET_ARCHIVE.md | Archive Event'leri |
| **VARLIK** | 13_DIGITAL_ASSET_CATALOG.md | Catalog Event'leri |

---

### Beklenen Sonuç

* Production Runtime boyunca oluşan tüm olaylar anayasal standartta yönetilir.
* Production Event yapısı tek standart altında toplanır.
* Event → PID → Production Package ilişkisi garanti edilir.
* Event kayıtları EEC ve LAC tarafından gerçek zamanlı izlenebilir.
* Production Runtime tamamen izlenebilir, denetlenebilir ve açıklanabilir hale gelir.
* Hiçbir Event değiştirilemez, silinemez veya mükerrer oluşturulamaz.
* Her Event, yaşam döngüsünü tamamlamadan ilgili Production adımı tamamlanmış kabul edilmez.
* Constitution Scan Engine, Event bütünlüğünü ve yaşam döngüsü tamamlanmasını doğrulayabilir.

---

## AR-002_74

### Başlık

**Task Package Runtime Integration Architecture**

### Amaç

Production Runtime sırasında oluşturulan Task Package'lerin anayasal kurallara uygun şekilde Production Runtime'a entegre edilmesini, Agent çalışma sınırlarının korunmasını ve Runtime koordinasyonunun standart hale getirilmesini sağlamak.

### Kural

HLK, Task Package yapılarını yalnızca geçerli bir Production Package oluşturulduktan sonra Runtime sürecine dahil edebilir.

Task Package Runtime entegrasyonunun ön koşulu:

* Production Package oluşturulmuş ve PID ile ilişkilendirilmiş olmalıdır (AR-002_72, AR-002_58).
* EVENT_PRODUCTION_PACKAGE_CREATED (OLAY-031) üretilmiş olmalıdır (AR-002_73).
* Production Package'in **Task Package Listesi** bölümü (16_PRODUCTION_PACKAGE_STANDARD.md, Bölüm 7) hazır durumda olmalıdır.

---

### Task Package Yapısal İlkeleri

Her Task Package, AR-002_47 (Task Package Engine Architecture) standardına uygun olarak:

* yalnızca bir Production Package'e bağlı olmalıdır (AR-002_58: her Task Package yalnızca bir Production Package'e aittir),
* yalnızca bir PID ile ilişkilendirilmelidir (AR-002_57: PID tüm bileşenlerin ortak referansıdır),
* yalnızca kendi görev kapsamını temsil etmelidir (AR-002_47: her ajan yalnızca kendi görevini yerine getirebilmesi için gerekli bilgiye erişebilir).

---

### Task Package Runtime Çalışma Sırası

Production Runtime sırasında HLK, aşağıdaki çalışma sırasını korumak zorundadır.

**Adım 1 — Gerekli Task Package'lerin Oluşturulması**

HLK, Production gereksinimlerine göre gerekli Task Package'leri oluşturur.

Her Task Package; AR-002_47'de tanımlanan içerik standardına uygun olarak en az aşağıdaki bilgileri içermelidir:

* Task ID (benzersiz görev kimliği),
* Workflow Kimliği (WF-008, 09_WORKFLOW_MANIFEST.md),
* Agent Kimliği (atanacak Agent'ın tanımlayıcısı),
* Görev Tanımı (Agent'ın ne yapacağı),
* Görev Amacı (görevin neden gerekli olduğu),
* Giriş Verileri (Agent'ın kullanacağı veriler),
* Beklenen Çıktılar (Agent'ın ne üretmesi gerektiği),
* Kalite Kriterleri (QR-004 uyumlu),
* Öncelik Seviyesi,
* Zaman Limiti (GC parametrelerine göre),
* İlgili Asset Referansları (12_DIGITAL_ASSET_ARCHIVE.md, 13_DIGITAL_ASSET_CATALOG.md),
* İlgili Feature Referansları (10_FEATURE_REGISTRY.md),
* Güvenlik ve Erişim Kuralları.

Task Package'ler, Production Package'in alt bileşeni olarak çalışır (AR-002_58: Task Package yapısı korunur; Production Package, Task Package'lerin üst katmanı olarak çalışır).

**Adım 2 — Her Task Package'in Production Package ile İlişkilendirilmesi**

HLK, her Task Package'i ilgili Production Package ile ilişkilendirir.

Bu ilişkilendirme ile:

* Her Task Package, Production Package'in **Task Package Listesi** bölümüne kaydedilir (16_PRODUCTION_PACKAGE_STANDARD.md, Bölüm 7),
* Her Task Package, Production Package'in PID'sini referans olarak taşır,
* Task Package → Production Package → PID zinciri tamamlanmış olur.

**Adım 3 — Her Task Package için Uygun Agent Atamasının Gerçekleştirilmesi**

HLK, her Task Package için uygun Agent'ı belirler ve atar.

Agent atamasında HLK:

* Dinamik Ajan Öncelik Sıralamasını kullanır (AR-002_3, AR-002_4, AR-002_5),
* Agent'ın uzmanlık alanını görev gereksinimleriyle eşleştirir,
* Agent'ın operasyonel durumunu kontrol eder (SE-007_1: Agent State Classification — AGENT_ACTIVE, AGENT_DISABLED, AGENT_NO_CREDITS, vb.),
* Agent'ın kullanılabilirliğini doğrular (AR-002_19: Ajan Sürekliliği ve Operasyonel Eskalasyon),
* Gerekirse alternatif Agent seçimi yapar (AR-002_21: Ajan Değiştirme ve Yeniden Seçim).

**Adım 4 — Agent Çalışma Yetkilerinin Sınırlandırılması**

HLK, her Agent'ın çalışma yetkilerini yalnızca ilgili Task Package ile sınırlar.

Bu sınırlandırma ile:

* Hiçbir Agent, başka bir Agent'ın Task Package'ine erişemez (AR-002_47: Veri İzolasyonu).
* Hiçbir Agent, Production Package'in tamamına erişemez (AR-002_58, 16_PRODUCTION_PACKAGE_STANDARD.md: Production Package'in tamamına yalnızca HLK erişebilir).
* Hiçbir Agent, başka bir Task Package üzerinde doğrudan işlem yapamaz.
* Her Agent yalnızca kendi Task Package'inde tanımlanan verilere ve kaynaklara erişebilir.

**Adım 5 — Task Runtime Başlangıç Event'lerinin Oluşturulması**

HLK, her Task Package için Task Runtime başlangıç Event'ini oluşturur.

Bu Event'ler:

* Olay Kayıt Merkezi standardına uygun olarak oluşturulur (14_OLAY_KAYIT_MERKEZI.md),
* PID alanı zorunlu olarak içerir (AR-002_57),
* Production Package altında kayıt altına alınır (AR-002_73 Adım 3),
* EEC tarafından toplanır (22_EXECUTION_EVENT_COLLECTOR.md),
* LAC üzerinden izlenebilir hale gelir (FEAT-015),
* Production Event Runtime kurallarına tabidir (AR-002_73).

**Adım 6 — Runtime Boyunca Görev Çıktılarının Toplanması**

HLK, Runtime boyunca oluşan tüm görev çıktılarını ilgili Task Package altında toplar.

Toplanan çıktılar:

* Agent'ın ürettiği tüm sonuçlar,
* Agent logları (SE-007_1/2),
* Servis kullanım kayıtları,
* Kredi tüketim bilgileri,
* Görev süresi ve performans metrikleri.

Tüm çıktılar Task Package üzerinden Production Package'e bağlanır.

**Adım 7 — Task Tamamlandığında Event Üretimi ve Production Runtime'a Geri Bildirim**

HLK, her Task tamamlandığında:

* İlgili tamamlanma Event'ini üretir (AR-002_73),
* Event'i Production Package altında kaydeder,
* Görev sonucunu Production Runtime'a geri bildirir,
* Gerekirse sonraki Task'ı tetikler,
* Başarısızlık durumunda AR-002_19 (Ajan Sürekliliği) ve AR-002_21 (Ajan Değiştirme) kurallarını uygular,
* AR-002_22 (Constitutional Feedback Loop) gerekiyorsa devreye girer.

---

### Agent İzolasyon ve Koordinasyon Kuralları

**Agent İzolasyonu:**

* Hiçbir Agent, başka bir Agent'ın Task Package'ine erişemez (AR-002_47).
* Hiçbir Agent, Production Package'in tamamına erişemez (AR-002_58).
* Hiçbir Agent, başka bir Task Package üzerinde doğrudan işlem yapamaz.
* Her Agent yalnızca kendi görev kapsamındaki verilere erişebilir (AR-002_47: Veri İzolasyonu).

**Task Package'ler Arası Koordinasyon:**

* Task Package'ler birbirleriyle doğrudan haberleşmez.
* Task Package'ler arasındaki koordinasyon yalnızca HLK Runtime Orchestrator tarafından yönetilir (AR-002_47, AR-002_58).
* Bir Task Package'in çıktısı, başka bir Task Package'in girdisi olacaksa, bu aktarım HLK üzerinden gerçekleşir.
* Hiçbir Agent, başka bir Agent'ın çıktısına doğrudan erişemez.

---

### Task Runtime Event Kayıtları

Task Runtime boyunca oluşan aşağıdaki durumlar, ilgili Event mekanizması üzerinden kayıt altına alınmalıdır (AR-002_73):

| Durum | Event Türü | Referans |
|---|---|---|
| Görev başlangıcı | Task başlangıç Event'i | AR-002_73, EEC |
| Görev tamamlanması | Task tamamlanma Event'i | AR-002_73, EEC |
| Görev başarısızlığı | Task başarısız Event'i | AR-002_19, AR-002_73 |
| Yeniden deneme | Retry Event'i | AR-002_22 (Feedback Loop) |
| Agent değişimi | AGENT_REPLACED Event'i | AR-002_21, SE-007_1 |
| Operasyonel eskalasyon | Eskalasyon Event'i | AR-002_19, AR-002_22 |

Tüm bu Event'ler:

* PID ile ilişkilendirilir (AR-002_57),
* Production Package altında kaydedilir (AR-002_72, AR-002_73),
* Decision History ile ilişkilendirilebilir olmalıdır (15_KARAR_GEREKCESI_STANDARDI.md).

---

### Production Runtime Tamamlanması

Production Runtime tamamlandığında:

* Tüm Task Package çıktıları ilgili Production Package içerisinde korunur (AR-002_72).
* Task Package kayıtları değiştirilemez ve silinemez.
* Task Package çıktıları, sonraki süreçler tarafından kullanılabilir olmalıdır:
  * **Quality Control** — kalite raporları için (QR-004, FEAT-010),
  * **Archive** — Digital Asset Archive güncellemesi için (12_DIGITAL_ASSET_ARCHIVE.md),
  * **Catalog** — Digital Asset Catalog güncellemesi için (13_DIGITAL_ASSET_CATALOG.md),
  * **Delivery** — nihai video teslimatı için (AR-002_36).

---

### Sınırlar ve Kapsam

Bu mimari;

* Task Package'lerin Production Runtime'a nasıl entegre edileceğini, hangi sırayla ve hangi koşullarda çalıştırılacağını tanımlar,
* Agent çalışma sınırlarını ve Task Package'ler arası koordinasyon kurallarını belirler,
* Task Runtime Event kayıt standartlarını uygular.

Bu mimari;

* Task Package'lerin iç yapısını tanımlamaz — yapı AR-002_47 (Task Package Engine Architecture) tarafından yönetilir.
* Agent seçim kriterlerini tanımlamaz — bu AR-002_3, AR-002_4, AR-002_5 ve AR-002_21'in sorumluluğundadır.
* Agent durum sınıflandırmasını tanımlamaz — bu SE-007_1 ve SE-007_2'nin sorumluluğundadır.
* Production Package'in iç yapısını tanımlamaz — bu AR-002_58 ve 16_PRODUCTION_PACKAGE_STANDARD.md'nin sorumluluğundadır.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — bu mimari en üst otoriteye tabidir |
| **MASTER** | MASTER-003 | ANA YASA/Kod Uyumluluk — Task Runtime denetlenebilir |
| **MASTER** | MASTER-004 | Karar Mekanizması — Agent atama kararları HLK'nındır |
| **AR** | AR-002_3 | Dinamik Ajan Öncelik Sıralaması — Agent seçim kriterleri |
| **AR** | AR-002_4 | Benzer Görevlerde Yeniden Kullanım |
| **AR** | AR-002_5 | Kurumsal Deneyim — başarılı Task sonuçlarının kaydı |
| **AR** | AR-002_7 | Eş Zamanlı Ajan Çalıştırma — aynı görev için tek Agent |
| **AR** | AR-002_19 | Ajan Sürekliliği ve Operasyonel Eskalasyon |
| **AR** | AR-002_21 | Ajan Değiştirme ve Yeniden Seçim |
| **AR** | AR-002_22 | Constitutional Feedback Loop — Task başarısızlık denetimi |
| **AR** | AR-002_36 | Scene Delivery — nihai çıktıların teslimi |
| **AR** | AR-002_47 | Task Package Engine Architecture — Task Package yapısal standardı (WHAT) |
| **AR** | AR-002_57 | PID standardı — tüm Task Package'ler PID ile ilişkilendirilir |
| **AR** | AR-002_58 | Production Package Architecture — PID → PP → TP → Agent hiyerarşisi |
| **AR** | AR-002_72 | Production Package Runtime — PP oluşturma (ön koşul) |
| **AR** | AR-002_73 | Production Event Runtime — Task Event'lerinin kayıt standardı |
| **SE** | SE-007_1 | Agent State Classification — Agent durum takibi |
| **SE** | SE-007_2 | Agent State Transition Rules — Agent durum geçişleri |
| **WF** | WF-008 | Video Production workflow'u (09_WORKFLOW_MANIFEST.md) |
| **FEAT** | FEAT-012 | Production Pipeline |
| **FEAT** | FEAT-014 | Production Package Engine |
| **FEAT** | FEAT-015 | Live Activity Center — Task izleme |
| **PKG** | 16_PRODUCTION_PACKAGE_STANDARD.md | Production Package bölümleri ve Task Package Listesi |
| **KARAR** | 15_KARAR_GEREKCESI_STANDARDI.md | Decision History — Task kararları |
| **VARLIK** | 12_DIGITAL_ASSET_ARCHIVE.md | Archive süreci |
| **VARLIK** | 13_DIGITAL_ASSET_CATALOG.md | Catalog süreci |

---

### Beklenen Sonuç

* Task Package Runtime entegrasyonu standart hale gelir.
* Agent çalışma sınırları anayasal olarak korunur.
* Runtime koordinasyonu HLK tarafından merkezi olarak yönetilir.
* Task Package, PID ve Production Package ilişkisi garanti altına alınır.
* Production Runtime mimarisinin altyapısı tamamlanmış olur.
* Hiçbir Agent, kendi Task Package'i dışındaki verilere veya kaynaklara erişemez.
* Task Package'ler arası koordinasyon yalnızca HLK üzerinden gerçekleşir.
* Tüm Task Runtime olayları Event sistemi ve Decision History ile ilişkilendirilir.
* Constitution Scan Engine, Task Package Runtime entegrasyonunu doğrulayabilir.

---

## AR-002_75

### Başlık

**Production Service Selection Architecture**

### Amaç

HLK'nın, reklam üretim sürecinde kullanılacak servis sağlayıcılarını marka bağımlı olmadan, anayasal karar mekanizmasına uygun şekilde dinamik olarak seçmesini standartlaştırmak.

### Kural

HLK hiçbir servis sağlayıcıyı varsayılan, zorunlu veya kalıcı üretim servisi olarak kabul etmez.

Bu ilke, AR-002_2'nin Production Runtime özelinde uygulanmasıdır:

> AR-002_2: "HLK, kendisine verilen bir görevi yerine getirirken belirli bir teknolojiye, belirli bir ajana, belirli bir modele veya belirli bir servise bağımlı bir mimari oluşturmaz."

---

### Servis Seçim Zamanı

Production Runtime başladığında HLK, üretim görevini merkeze alarak aday servis sağlayıcıları kendi karar mekanizması ile değerlendirir.

Servis seçimi:

* Production Runtime başlangıcında (AR-002_70),
* PID oluşturulduktan sonra (AR-002_71),
* Production Package oluşturulduktan sonra (AR-002_72),
* Task Package'ler oluşturulmadan önce (AR-002_74)

gerçekleştirilir. Böylece her Agent, görevlendirilmeden önce hangi servis sağlayıcısını kullanacağını bilir.

---

### Primary Candidate ve Backup Candidate Havuzu

HLK, üretime başlamadan önce ilgili harici kaynak kategorisi için aday havuzunu oluşturmak zorundadır.

Her aday havuzu aşağıdaki yapılardan oluşur:

* **Primary Candidate** — Üretimde ilk kullanılacak adaydır.
* **Backup Candidate** — Primary Candidate kullanılamaz hale geldiğinde veya anayasal olarak değiştirilmesi gerektiğinde kullanılmak üzere önceden belirlenen alternatif adaylardır.

Aday havuzu oluşturulmadan Production Runtime başlatılamaz.

Aday havuzu oluşturulduktan sonra;

* Puanlama,
* Öncelik sıralaması,
* API doğrulaması,
* Kredi doğrulaması,
* Kota doğrulaması,
* Servis sağlık doğrulaması,
* Operasyonel doğrulamalar

bu aday havuzu üzerinden gerçekleştirilir.

Production Runtime başladıktan sonra aday havuzu yeniden rastgele oluşturulamaz.

Yeni aday oluşturulması yalnızca mevcut anayasal karar mekanizmaları kapsamında gerçekleştirilebilir:

* AR-002_19 — Ajan Sürekliliği ve Operasyonel Eskalasyon (başarısızlık durumunda sıradaki adaya geçiş),
* AR-002_21 — Ajan Değiştirme ve Yeniden Seçim (değişen koşullarda yeni aday seçimi),
* AR-002_22 — Constitutional Feedback Loop (yeniden değerlendirme ve karar güncelleme),
* AR-002_75 — Decision Engine (alternatif servis seçimi),
* AR-002_76 — Production Execution (retry ve checkpoint mekanizması),
* AR-002_87 — External Resource Recovery Protocol (anayasal recovery yaşam döngüsü).

Primary Candidate ve Backup Candidate sayıları anayasa içerisinde sabit yazılmaz.

Bu değerler yalnızca Global Configuration üzerinden yönetilir:

* `GC_PRIMARY_CANDIDATE_COUNT` — Primary Candidate sayısı,
* `GC_BACKUP_CANDIDATE_COUNT` — Backup Candidate sayısı.

Bu mimari;

* Video Provider,
* Image Provider,
* Voice Provider,
* LLM Provider,
* Agent,
* API,
* ve gelecekte sisteme eklenecek tüm harici kaynak kategorileri

için ortak anayasal standarttır.

---

### Değerlendirme Kriterleri

Servis seçimi tek bir kritere göre yapılmaz.

HLK, mümkün olduğu durumlarda aşağıdaki değerlendirme alanlarını birlikte analiz eder:

| # | Kriter | Açıklama | Anayasal Kaynak |
|---|---|---|---|
| 1 | **Üretilecek göreve uygunluk** | Servis bu spesifik görevi yerine getirebiliyor mu? | AR-002_3, Task Package |
| 2 | **Üretilecek ürün kategorisine uygunluk** | Servis bu ürün kategorisinde başarılı mı? | AR-002_3, AR-002_4 |
| 3 | **Hedef platforma uygunluk** | Servis çıktısı hedef platformla uyumlu mu? | SAHNE-02, SAHNE-03 |
| 4 | **Kullanıcı brief'i** | Servis, kullanıcının tercihlerine uygun mu? | AR-002_3 |
| 5 | **Beklenen çıktı kalitesi** | Servis istenen kalite seviyesini sağlayabilir mi? | QR-004 |
| 6 | **Geçmiş üretim başarıları** | Bu servis ile daha önce başarılı üretim yapıldı mı? | AR-002_4, AR-002_5 |
| 7 | **Bağımsız benchmark ve değerlendirme sonuçları** | Üçüncü taraf performans verileri ne gösteriyor? | AR-002_3 |
| 8 | **Servis sağlık durumu** | Servis şu anda operasyonel mi? | OR-004 |
| 9 | **API erişilebilirliği** | API anahtarı mevcut ve geçerli mi? | AR-002_19, OR-004 |
| 10 | **Kredi ve kota durumu** | Yeterli kredi/kota mevcut mu? | GC, OR-004 |
| 11 | **Tahmini üretim maliyeti** | Bu servis ile üretim maliyeti ne olur? | AR-002_3, GC |
| 12 | **Tahmini üretim süresi** | Bu servis ile üretim ne kadar sürer? | GC |
| 13 | **Servis güven skoru** | Servisin güvenilirlik puanı nedir? | Operasyon Veri Merkezi |
| 14 | **Alternatif servis bulunabilirliği** | Bu servis başarısız olursa alternatif var mı? | AR-002_19, AR-002_21 |
| 15 | **Gerekli gördüğü diğer objektif kriterler** | HLK, üretim bağlamına göre ek kriterler belirleyebilir | MASTER-004 |

Bu kriterler sınırlayıcı değildir. HLK, üretim görevinin gereksinimlerine göre değerlendirme kapsamını genişletebilir veya daraltabilir.

---

### Kriter Ağırlıklandırma

Değerlendirme kriterlerinin ağırlıkları sabit değildir.

HLK, her üretim görevinde kendi karar mekanizması ile kriter ağırlıklarını dinamik olarak belirler (MASTER-004, AR-002_3).

Örneğin:

* Yüksek kalite gerektiren bir üretimde "beklenen çıktı kalitesi" ve "geçmiş üretim başarıları" kriterleri daha yüksek ağırlıklandırılabilir.
* Kredi seviyesi kritik seviyede ise "tahmini üretim maliyeti" ve "kredi ve kota durumu" kriterleri öncelik kazanabilir.
* Hızlı teslimat gerektiren bir üretimde "tahmini üretim süresi" kriteri daha yüksek ağırlık alabilir.

Kriter ağırlıklandırması, HLK'nın karar mekanizmasının bir parçasıdır ve her üretim için ayrı ayrı belirlenir.

---

### Bağımsız Verilerin Rolü

Bağımsız benchmark, kullanıcı değerlendirmeleri veya üçüncü taraf performans raporları tek başına karar oluşturamaz.

Bu veriler yalnızca HLK'nın karar mekanizmasını besleyen bilgi kaynaklarıdır (AR-002_3, MASTER-004).

Nihai servis seçimi yalnızca HLK tarafından yapılır. Hiçbir dış veri kaynağı, HLK'nın karar mekanizmasının yerine geçemez.

---

### Seçim Gerekçelerinin Kaydedilmesi

Seçilen servis sağlayıcısı, seçim gerekçeleri ile birlikte karar kayıtlarına işlenmelidir.

Bu kayıt:

* Production Package'in **Karar Gerekçeleri (Decision History)** bölümünde saklanır (15_KARAR_GEREKCESI_STANDARDI.md),
* PID ile ilişkilendirilir (AR-002_57),
* Hangi kriterlerin kullanıldığını,
* Kriter ağırlıklarını,
* Değerlendirilen alternatif servisleri,
* Seçilen servisin gerekçesini,
* Seçilmeyen servislerin neden seçilmediğini

içerir.

Bu kayıt, gelecekteki benzer üretimlerde HLK'nın kurumsal deneyimini güçlendirir (AR-002_5).

---

### Servis Değişimi

Servis seçiminden sonra çalışma koşullarının değişmesi durumunda HLK, mevcut seçimi yeniden değerlendirebilir.

Servis değişimi aşağıdaki durumlarda gerçekleşebilir:

* Seçilen servis kullanılamaz hale gelirse (AR-002_19: Ajan Sürekliliği),
* Seçilen servis timeout verirse (AR-002_7),
* Seçilen servis beklenen kaliteyi sağlayamazsa (QR-004),
* Daha uygun bir alternatif tespit edilirse (AR-002_21),
* Operasyonel koşullar değişirse (kredi tükenmesi, API erişim sorunu — OR-004).

Servis değişimi, AR-002_22 (Constitutional Feedback Loop) kapsamında denetlenir.

HLK, mümkün olduğu sürece üretimi durdurmaz; anayasal kurallar doğrultusunda alternatif servis sağlayıcısına geçebilir (AR-002_19).

---

### Temel İlke

Bu mimarinin amacı belirli bir servis sağlayıcısını tercih etmek değil, her üretim görevi için en uygun servis sağlayıcısını anayasal karar mekanizması ile belirlemektir.

Hiçbir servis sağlayıcısı:

* HLK'nın karar mekanizmasının üzerinde değildir (MASTER-001).
* HLK'nın yerine karar veremez (MASTER-004).
* Kalıcı veya değiştirilemez olarak tanımlanamaz (AR-002_2).

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — servis seçimi ANA YASA'ya tabidir |
| **MASTER** | MASTER-004 | Karar Mekanizması — nihai servis seçimi HLK'nındır |
| **AR** | AR-002_2 | Teknoloji/Servis Bağımsızlığı — belirli bir servise bağımlılık yasağı |
| **AR** | AR-002_3 | Dinamik Ajan Öncelik Sıralaması — değerlendirme kriterleri |
| **AR** | AR-002_4 | Benzer Görevlerde Yeniden Kullanım — geçmiş başarıların değerlendirilmesi |
| **AR** | AR-002_5 | Kurumsal Deneyim — başarılı servis seçimlerinin kaydı |
| **AR** | AR-002_7 | Eş Zamanlı Ajan Çalıştırma — timeout/başarısızlıkta alternatife geçiş |
| **AR** | AR-002_19 | Ajan Sürekliliği ve Operasyonel Eskalasyon — servis kullanılamadığında |
| **AR** | AR-002_21 | Ajan Değiştirme ve Yeniden Seçim — servis değişim kuralları |
| **AR** | AR-002_22 | Constitutional Feedback Loop — servis değişim kararlarının denetimi |
| **AR** | AR-002_70 | STATE_VIDEO_PRODUCTION Runtime — servis seçiminin yapıldığı aşama |
| **AR** | AR-002_74 | Task Package Runtime Integration — Agent'lara servis ataması |
| **OR** | OR-004 | Operasyonel kontroller — API, kredi, kota yönetimi |
| **GC** | GC kredi/kota parametreleri | Kredi limitleri ve kota eşikleri (01_Global_Configuration.md) |
| **QR** | QR-004 | Kalite Kuralları — çıktı kalitesi değerlendirmesi |
| **MR** | MR-005 | Modül Kuralları — servis bazlı modül yönetimi |
| **KARAR** | 15_KARAR_GEREKCESI_STANDARDI.md | Seçim gerekçelerinin kaydı |

---

### Beklenen Sonuç

* Servis seçimi marka bağımlılığından kurtulur.
* HLK her üretim için en uygun servis sağlayıcısını dinamik olarak seçer.
* Bağımsız benchmark verileri karar mekanizmasına katkı sağlar ancak karar vermez.
* Servis seçimleri gerekçeleriyle kayıt altına alınır.
* Yeni servis sağlayıcıları anayasal değişiklik gerektirmeden sisteme dahil edilebilir.
* Hiçbir servis sağlayıcısı kalıcı veya değiştirilemez konumda değildir.
* Servis değişim kararları Feedback Loop tarafından denetlenir.
* Constitution Scan Engine, servis seçim gerekçelerinin Decision History'de kayıtlı olduğunu doğrulayabilir.

---

## AR-002_76

### Başlık

**Üretim Yürütme Mimarisi — Production Execution Architecture**

### Amaç

HLK tarafından oluşturulan Production Runtime kararlarının güvenli, izlenebilir ve anayasal kurallara uygun şekilde yürütülmesini standartlaştırmak.

### Kural

HLK içerisinde üretim yürütme işlemleri yalnızca Üretim Yürütme Mimarisi (Production Executor) tarafından gerçekleştirilir.

---

### Executor'un Anayasal Konumu

Üretim Yürütme Mimarisi, HLK'nın **uygulayıcı** katmanıdır. Karar verici veya denetleyici değildir.

Bu ilke, MASTER-007'nin Production Runtime özelinde uygulanmasıdır:

> MASTER-007: "AI Geliştirici, HLK sisteminde yalnızca uygulayıcıdır. Karar verici veya denetleyici değildir."

Executor:

* karar vermez (karar yalnızca HLK Decision Engine'indir — MASTER-004),
* görev seçmez (görev seçimi Task Package Engine'indir — AR-002_47),
* servis seçmez (servis seçimi HLK karar mekanizmasınındır — AR-002_75),
* prompt oluşturmaz veya değiştirmez (prompt'lar Decision Engine tarafından hazırlanır),
* kalite değerlendirmesi yapmaz (kalite kontrol QR-004 ve FEAT-010'indir),
* üretim stratejisini değiştirmez (strateji HLK karar mekanizmasınındır).

Executor yalnızca HLK tarafından oluşturulan ve onaylanan Decision Packet'i yürütür.

---

### Yürütme Öncesi Doğrulama Adımları

Her yürütme işlemi başlamadan önce HLK, aşağıdaki doğrulamaları eksiksiz tamamlamak zorundadır.

**Adım 1 — Production Runtime Durumunun Doğrulanması**

HLK, Production Runtime'ın aktif ve sağlıklı olduğunu doğrular:

* STATE_VIDEO_PRODUCTION state'i aktiftir (SE-007_3, AR-002_70).
* Production Runtime başlatılmıştır (AR-002_70 Adım 5).
* Production Runtime içerisinde kritik bir hata veya eskalasyon durumu yoktur.

**Adım 2 — PID Doğrulaması**

HLK, PID'nin geçerli olduğunu doğrular:

* PID oluşturulmuştur (AR-002_71).
* PID formatı GC standartlarına uygundur.
* PID benzersizdir ve değiştirilmemiştir (AR-002_57).

**Adım 3 — Production Package Doğrulaması**

HLK, Production Package'in yürütmeye hazır olduğunu doğrular:

* Production Package oluşturulmuştur (AR-002_72).
* Production Package, PID ile ilişkilendirilmiştir.
* Production Package'in zorunlu bölümleri doldurulmuştur (16_PRODUCTION_PACKAGE_STANDARD.md).

**Adım 4 — İlgili Task Package'in Belirlenmesi**

HLK, yürütülecek görev için ilgili Task Package'i belirler:

* Task Package oluşturulmuştur (AR-002_74 Adım 1).
* Task Package, Production Package ile ilişkilendirilmiştir (AR-002_74 Adım 2).
* Task Package için uygun Agent atanmıştır (AR-002_74 Adım 3).
* Task Package, görev kapsamına uygun verileri içermektedir (AR-002_47).

**Adım 5 — Kullanılacak Servis Sağlayıcısının Doğrulanması**

HLK, seçilen servis sağlayıcısının yürütmeye hazır olduğunu doğrular:

* Servis seçimi yapılmıştır (AR-002_75).
* Servis operasyoneldir (OR-004).
* API erişimi mevcuttur (AR-002_19).
* Kredi/kota yeterlidir (GC, OR-004).

**Adım 6 — Yürütülecek Decision Packet'in Hazırlanması**

HLK, yürütülecek Decision Packet'i hazırlar:

* Decision Packet, Decision Engine tarafından üretilmiştir (MASTER-004).
* Decision Packet, Constitutional Validator'den geçmiştir (AR-002_22).
* Decision Packet, yürütme için gerekli tüm parametreleri içermektedir.

Üretim Yürütme Mimarisi yalnızca bu altı doğrulama tamamlandıktan sonra çalıştırılabilir.

Hiçbir doğrulama adımı atlanamaz.

---

### Yürütme Çalışma Sırası

Her yürütme süreci aşağıdaki çalışma sırasını takip eder.

**Adım 1 — Decision Packet'in Alınması**

Executor, Decision Engine tarafından üretilen ve Constitutional Validator tarafından onaylanan Decision Packet'i alır.

Decision Packet; Executor'un ne yapacağını, hangi parametrelerle yapacağını ve beklenen çıktının ne olduğunu tanımlar. Executor, Decision Packet'in içeriğini değiştiremez.

**Adım 2 — İlgili Task Package'in Yüklenmesi**

Executor, belirlenen Task Package'i yükler.

Task Package; Executor'un görevi yerine getirmesi için ihtiyaç duyduğu tüm verileri, kaynak referanslarını ve kalite kriterlerini içerir (AR-002_47).

**Adım 3 — Görevin Yürütülmesi**

Executor, belirlenen servis sağlayıcısını kullanarak görevi yürütür.

Yürütme sırasında:

* Executor, Task Package'te tanımlanan görev kapsamının dışına çıkamaz.
* Executor, karar değişikliği yapamaz.
* Executor, yalnızca kendisine atanan servis sağlayıcısını kullanır.
* Görev süresi, GC parametreleri ile belirlenen zaman limitini aşamaz (AR-002_7).

**Adım 4 — Execution Event'lerinin Üretilmesi**

Executor, yürütme sırasında Execution Event'lerini üretir.

Bu Event'ler:

* Production Event Runtime standardına uygundur (AR-002_73),
* PID alanı zorunlu olarak içerir (AR-002_57),
* EEC tarafından toplanır (22_EXECUTION_EVENT_COLLECTOR.md),
* LAC üzerinden gerçek zamanlı izlenebilir (FEAT-015).

**Adım 5 — Teknik Çıktıların Kaydedilmesi**

Executor, yürütme sonucunda oluşan teknik çıktıları Production Package'e kaydeder.

Executor'un kaydedebileceği teknik çıktılar:

* Task yürütme sonuçları (task status, duration, output),
* Oluşturulan dosyaların referansları (görsel, ses, video yolu),
* Execution Event'leri (EEC standardına uygun),
* Task checkpoint kayıtları.

Executor'un kaydedemeyeceği:

* **PackageStatus (COMPLETED, FAILED, vb.)** — bu bir anayasal karardır (AR-002_88),
* **Decision History** — bu HLK Runtime kararlarının kaydıdır,
* **Production kararları** (RETRY, RESUME, REPLAY, vb.).

Executor yalnızca teknik veri yazar; anayasal karar kaydetmez.

**Adım 6 — Execution Result'ın Oluşturulması**

Executor, yürütme sonucunda bir Execution Result oluşturur.

Execution Result en az aşağıdaki bilgileri içermelidir:

* status: SUCCESS / FAILED / TIMEOUT / PARTIAL (AR-002_22)
  Bu status'lar yalnızca task yürütme sonucunu belirtir; üretim kararı değildir.
  SUCCESS = task teknik olarak tamamlandı (çıktı kalitesi garantisi yoktur).
  FAILED  = task teknik olarak başarısız (exception, timeout).
  Bu status'lar Production COMPLETED/FAILED kararı ile karıştırılamaz (AR-002_88).
* output: Görev çıktısı
* duration_ms: Görev süresi
* error_detail: Hata detayı (FAILED/TIMEOUT ise)

**Adım 7 — Execution Result'ın Feedback Loop'a İletilmesi**

Executor, Execution Result'ı Feedback Loop'a iletir (AR-002_22).

Executor'un görevi burada sona erer. Executor, Execution Result'ın değerlendirmesini yapmaz, sonraki adımı belirlemez.

Feedback Loop, Execution Result'ı alır ve değerlendirir:

* SUCCESS → yeni Event → normal akış devam eder,
* FAILED / TIMEOUT / PARTIAL → neden analizi → Decision Engine yeniden çağrılır (AR-002_22 Adım 2-3).

---

### Yürütme Durumları ve Event Kayıtları

Üretim sırasında oluşan durumlar, ilgili Event sistemi üzerinden kayıt altına alınmalıdır (AR-002_73):

| Task Sonucu | Execution Result Status | Teknik Event | Sonraki İşlem |
|---|---|---|---|
| **Task tamamlandı** | SUCCESS | TASK_COMPLETED | Feedback Loop'a iletilir — değerlendirme HLK'ya aittir |
| **Task başarısız** | FAILED | TASK_FAILED | Feedback Loop'a iletilir — neden analizi HLK'ya aittir |
| **Task timeout** | TIMEOUT | TASK_TIMEOUT | Feedback Loop'a iletilir — AR-002_7 alternatif değerlendirmesi |
| **Task iptal** | CANCELLED | TASK_CANCELLED | Feedback Loop'a iletilir |
| **Task kısmi** | PARTIAL | TASK_PARTIAL | Feedback Loop'a iletilir — eksik kısım HLK kararına bağlı |
| **Task servis değişimi** | — | PROVIDER_SWITCHED | AR-002_21 → HLK Runtime PROVIDER_SWITCH kararı |

Tüm bu Event'ler:

* PID ile ilişkilendirilir (AR-002_57),
* Production Package altında saklanır (AR-002_72),
* Decision History ile çapraz referanslanabilir (15_KARAR_GEREKCESI_STANDARDI.md).

---

### Anayasal Sınırlar

Üretim Yürütme Mimarisi hiçbir durumda anayasal karar mekanizmasının yerine geçemez.

| Executor Yapabilir | Executor Yapamaz |
|---|---|
| ✅ Decision Packet'i yürütmek | ❌ Karar vermek (MASTER-004) |
| ✅ Task Package verilerini kullanmak | ❌ Task Package'i değiştirmek |
| ✅ Belirlenen servisi kullanmak | ❌ Servis seçmek veya değiştirmek (AR-002_75) |
| ✅ Execution Result üretmek | ❌ Execution Result'ı değerlendirmek |
| ✅ Execution Event'leri üretmek | ❌ Event'leri yorumlamak |
| ✅ Çıktıları Production Package'e kaydetmek | ❌ Çıktı kalitesini değerlendirmek (QR-004) |
| ✅ Feedback Loop'a sonuç iletmek | ❌ Feedback Loop'u atlamak (AR-002_22) |

Karar değişikliği gerektiğinde süreç Feedback Loop üzerinden yeniden HLK Decision Engine'ine yönlendirilmelidir (AR-002_22). Executor, karar değişikliğini kendisi yapamaz.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — Executor en alt katmandır |
| **MASTER** | MASTER-004 | Karar Mekanizması — Executor karar vermez, yalnızca yürütür |
| **MASTER** | MASTER-007 | Geliştirici Çalışma Metodolojisi — Executor (uygulayıcı) ≠ HLK (karar verici) |
| **AR** | AR-002_7 | Eş Zamanlı Ajan Çalıştırma — timeout yönetimi |
| **AR** | AR-002_19 | Ajan Sürekliliği — başarısızlıkta eskalasyon |
| **AR** | AR-002_21 | Ajan Değiştirme — servis değişimi |
| **AR** | AR-002_22 | Constitutional Feedback Loop — Execution Result → Feedback Loop |
| **AR** | AR-002_47 | Task Package Engine — Executor'un veri kaynağı |
| **AR** | AR-002_57 | PID standardı — tüm kayıtlarda PID zorunlu |
| **AR** | AR-002_70 | STATE_VIDEO_PRODUCTION Runtime — yürütme ortamı |
| **AR** | AR-002_71 | PID Runtime — PID doğrulama |
| **AR** | AR-002_72 | Production Package Runtime — çıktıların kaydedileceği kapsayıcı |
| **AR** | AR-002_73 | Production Event Runtime — Execution Event standardı |
| **AR** | AR-002_74 | Task Package Runtime Integration — Task Package yükleme |
| **AR** | AR-002_75 | Production Service Selection — servis doğrulama |
| **SE** | SE-007_3 | STATE_VIDEO_PRODUCTION state tanımı |
| **GC** | GC zaman limiti parametreleri | Görev timeout süreleri (01_Global_Configuration.md) |
| **EEC** | 22_EXECUTION_EVENT_COLLECTOR.md | Execution Event'lerinin toplanması |
| **KARAR** | 15_KARAR_GEREKCESI_STANDARDI.md | Decision History — yürütme kararlarının kaydı |
| **PKG** | 16_PRODUCTION_PACKAGE_STANDARD.md | Çıktıların kaydedileceği bölümler |
| **FEAT** | FEAT-012 | Production Pipeline |
| **FEAT** | FEAT-015 | Live Activity Center — gerçek zamanlı yürütme izleme |

---

### Beklenen Sonuç

* Üretim ve karar mekanizması birbirinden ayrılır.
* Executor yalnızca yürütmeden sorumlu olur.
* HLK tek karar verici olmaya devam eder.
* Tüm yürütme işlemleri izlenebilir hale gelir.
* Execution Result, Feedback Loop'un standart girdisi olur.
* Production Runtime anayasal olarak güvenli ve denetlenebilir şekilde yürütülür.
* Hiçbir yürütme işlemi, ön doğrulama adımları tamamlanmadan başlatılamaz.
* Executor anayasal sınırlarını aşamaz; karar değişikliği yalnızca Feedback Loop → Decision Engine zinciri ile gerçekleşir.
* Constitution Scan Engine, yürütme öncesi doğrulama adımlarının tamamlandığını denetleyebilir.

---

## AR-002_77

### Başlık

**Yaratıcı İçerik Üretim Mimarisi — Creative Content Production Architecture**

### Amaç

HLK'nın reklam üretim sürecinde ihtiyaç duyduğu tüm yaratıcı içerikleri, tek bir modele veya servis sağlayıcısına bağlı kalmadan, anayasal karar mekanizmasına uygun şekilde üretmesini standartlaştırmak.

### Kural

HLK, yaratıcı içerik üretimini yalnızca senaryo yazımı olarak değerlendirmez.

Yaratıcı içerik üretimi; reklamın iletişim stratejisini, anlatım yapısını ve üretim kararlarını kapsayan bütüncül bir süreçtir.

Bu yaklaşım, AR-002_14'ün Production Runtime özelinde uygulanmasıdır:

> AR-002_14: "HLK'ye kullanıcı ile kuracağı iletişim için hazır cümleler, hazır soru kalıpları veya sabit konuşma metinleri tanımlanmaz."

HLK, yaratıcı içerikleri de hazır kalıplarla değil, kendi karar mekanizmasıyla dinamik olarak üretir.

---

### Yaratıcı İçerik Kapsamı

HLK, gerekli gördüğü durumlarda aşağıdaki yaratıcı içerikleri oluşturabilir:

| # | İçerik Türü | Açıklama | İlgili Production Package Bölümü |
|---|---|---|---|
| 1 | **Reklam Stratejisi** | Ürün için en uygun reklam yaklaşımı | Brief (Bölüm 3) |
| 2 | **Reklam Yaklaşımı** | UGC, sinematik, geleneksel vb. | Brief (Bölüm 3) |
| 3 | **Anlatım Dili** | Marka tonu, samimiyet seviyesi, hitap tarzı | Brief (Bölüm 3) |
| 4 | **Reklam Senaryosu** | Tam reklam metni ve sahne akışı | Senaryo (Bölüm 4) |
| 5 | **Sahne Akışı** | Sahneler arası geçiş ve zamanlama | Storyboard (Bölüm 5) |
| 6 | **Sahne Açıklamaları** | Her sahnenin görsel ve işitsel detayları | Storyboard (Bölüm 5) |
| 7 | **Hook Yapısı** | İlk 2 saniyede izleyiciyi yakalama stratejisi | Senaryo (Bölüm 4) |
| 8 | **CTA (Call To Action)** | Harekete geçirici mesaj | Senaryo (Bölüm 4) |
| 9 | **Konuşma Metinleri** | Seslendirme ve diyalog metinleri | Prompt Setleri (Bölüm 6) |
| 10 | **Ekran Metinleri** | Video üzerinde görünecek yazılar | Prompt Setleri (Bölüm 6) |
| 11 | **Görsel Yönlendirmeler** | Kamera açıları, renk paleti, kompozisyon | Prompt Setleri (Bölüm 6) |
| 12 | **Üretim Notları** | Prodüksiyon ekibine teknik talimatlar | Prompt Setleri (Bölüm 6) |
| 13 | **Gerekli Diğer İçerikler** | HLK'nın üretim bağlamına göre belirlediği ek içerikler | İlgili bölüm |

Bu liste sınırlayıcı değildir. HLK, üretim görevinin gereksinimlerine göre yeni içerik türleri oluşturabilir veya bazı içerik türlerini birleştirebilir.

Tüm yaratıcı içerikler, ilgili Production Package bölümlerinde saklanır (16_PRODUCTION_PACKAGE_STANDARD.md).

---

### Model ve Servis Bağımsızlığı

HLK hiçbir yapay zekâ modelini, LLM'i veya yaratıcı servis sağlayıcısını varsayılan içerik üreticisi olarak kabul etmez.

Bu ilke, AR-002_2 ve AR-002_75'in yaratıcı içerik üretimi özelinde uygulanmasıdır:

* AR-002_2: "HLK belirli bir teknolojiye, belirli bir ajana, belirli bir modele veya belirli bir servise bağımlı bir mimari oluşturmaz."
* AR-002_75: "HLK hiçbir servis sağlayıcıyı varsayılan, zorunlu veya kalıcı üretim servisi olarak kabul etmez."

Kullanılacak yaratıcı üretim servisi, Production Service Selection Architecture (AR-002_75) kapsamında HLK'nın karar mekanizması tarafından dinamik olarak belirlenmelidir.

---

### Model Kullanım Yaklaşımları

HLK, yaratıcı içerik üretiminde aşağıdaki yaklaşımlardan uygun gördüğünü kullanabilir:

| Yaklaşım | Açıklama | Kullanım Örneği |
|---|---|---|
| **Tek Model** | Tek bir LLM/servis ile içerik üretimi | Basit, kısa süreli reklamlar |
| **Çoklu Model** | Birden fazla modelden bağımsız çıktılar | Alternatif senaryo üretimi |
| **Hibrit Model** | Farklı modellerden farklı içerik türleri | Strateji Model-A, senaryo Model-B |
| **Ardışık Model** | Bir modelin çıktısı diğerine girdi | Strateji → senaryo → prompt zinciri |
| **Paralel Model** | Aynı görev için eş zamanlı çoklu model | A/B senaryo karşılaştırması |

Model seçimi, AR-002_75'te tanımlanan 15 değerlendirme kriteri kullanılarak HLK karar mekanizması tarafından yapılır.

---

### Çoklu Model Çıktı Yönetimi

Birden fazla modelden elde edilen çıktılar, HLK tarafından:

* **Karşılaştırılabilir:** Farklı modellerin çıktıları aynı kriterlerle değerlendirilir,
* **Birleştirilebilir:** Farklı modellerin güçlü yönleri tek bir çıktıda toplanabilir,
* **İyileştirilebilir:** Bir çıktı, başka bir model tarafından revize edilebilir,
* **Yeniden Üretilebilir:** Kalite kriterlerini karşılamayan çıktılar yeniden üretilebilir.

Tüm bu işlemler AR-002_22 (Constitutional Feedback Loop) kapsamında denetlenir.

---

### Yaratıcı Karar Girdileri

Yaratıcı içerik üretim süreci boyunca aşağıdaki veriler, HLK'nın karar mekanizmasının temel girdileri olarak değerlendirilmelidir:

| Girdi | Kaynak | Açıklama |
|---|---|---|
| **Kullanıcı Brief'i** | SAHNE-02 ~ SAHNE-11 | Kullanıcının tüm tercihleri |
| **Ürün Analizi** | AR-002_13 (Arka Plan Araştırması) | Ürün özellikleri, kategorisi |
| **Marka Analizi** | AR-002_13, AR-002_24 | Marka kimliği, tonu, tarzı |
| **Hedef Kitle** | SAHNE-07 | Yaş grubu, demografik bilgiler |
| **Platform** | SAHNE-02 | TikTok, Instagram, YouTube vb. |
| **Video Süresi** | SAHNE-05 | 4-30 saniye |
| **Reklam Hedefi** | AR-002_13 (Reklam Stratejisi Sentezi) | Dönüşüm, farkındalık, tanıtım |
| **Araştırma Sonuçları** | AR-002_20, AR-002_23 | Bilgi açığı analizi, rakip analizi |
| **Production Package Verileri** | AR-002_72, 16_PRODUCTION_PACKAGE_STANDARD.md | Brief, Referans Görseller, Video Parametreleri |
| **Gerekli Diğer Veriler** | HLK karar mekanizması | Üretim bağlamına göre ek veriler |

Bu girdiler, AR-002_3'te tanımlanan "kullanıcı brief'ini karar mekanizmasının merkezi olarak kabul etme" ilkesi doğrultusunda değerlendirilir.

---

### Nihai Karar Yetkisi

Hiçbir yaratıcı servis sağlayıcısı nihai reklam stratejisini veya nihai senaryoyu tek başına belirleyemez.

Servis sağlayıcılar yalnızca içerik üretir.

Nihai değerlendirme, karşılaştırma, revizyon ve kabul kararı yalnızca HLK tarafından verilir (MASTER-004).

Bu ilke, AR-002_12'nin yaratıcı içerik özelinde uygulanmasıdır:

> AR-002_12: "HLK, dinamik ajan orkestrasyonunda hiçbir ajanı mutlak otorite olarak kabul etmez. Nihai karar, tek bir ajanın önerisine değil, HLK'nın kendi karar mekanizmasının tüm objektif değerlendirmelerine dayanır."

---

### İçerik Kayıt ve Sürümleme

Üretilen tüm yaratıcı içerikler:

* İlgili Production Package içerisinde saklanmalıdır (AR-002_72),
* Sürüm bilgileri ile birlikte kayıt altına alınmalıdır (V1.0, V1.1, vb.),
* Hangi model/servis tarafından üretildiği bilgisini taşımalıdır,
* Decision History ile ilişkilendirilebilmelidir (15_KARAR_GEREKCESI_STANDARDI.md),
* PID üzerinden sorgulanabilir olmalıdır (AR-002_57).

İçerik değişiklikleri:

* Yeni sürüm olarak kaydedilir (önceki sürüm korunur),
* Değişiklik gerekçesi Decision History'ye işlenir,
* Revizyon Geçmişi'ne eklenir (16_PRODUCTION_PACKAGE_STANDARD.md, Bölüm 18).

---

### Temel İlke

Bu mimarinin amacı belirli bir modeli kullanmak değil, her üretim görevi için en uygun yaratıcı içeriği anayasal karar mekanizması doğrultusunda oluşturmaktır.

Hiçbir yapay zekâ modeli veya yaratıcı servis sağlayıcısı:

* HLK'nın karar mekanizmasının üzerinde değildir (MASTER-001),
* HLK'nın yerine karar veremez (MASTER-004),
* Varsayılan veya kalıcı içerik üreticisi olarak tanımlanamaz (AR-002_2, AR-002_75).

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — yaratıcı içerik ANA YASA'ya tabidir |
| **MASTER** | MASTER-004 | Karar Mekanizması — nihai yaratıcı karar HLK'nındır |
| **AR** | AR-002_2 | Teknoloji/Servis Bağımsızlığı — modele bağımlılık yasağı |
| **AR** | AR-002_3 | Dinamik Ajan Öncelik Sıralaması — brief merkezli değerlendirme |
| **AR** | AR-002_12 | Ajan Otorite Sınırı — hiçbir model mutlak otorite değildir |
| **AR** | AR-002_13 | Arka Plan Araştırması — yaratıcı girdi kaynağı |
| **AR** | AR-002_14 | İletişim Özerkliği — HLK hazır metin okumaz, kendi üretir |
| **AR** | AR-002_20 | Bilgi Açığı Analizi — eksik bilgilerin tespiti |
| **AR** | AR-002_22 | Constitutional Feedback Loop — içerik kalite denetimi |
| **AR** | AR-002_23 | Bilgi Açığı Görev Atama — araştırma sonuçlarının kullanımı |
| **AR** | AR-002_57 | PID standardı — içerikler PID ile ilişkilendirilir |
| **AR** | AR-002_72 | Production Package Runtime — içeriklerin saklanacağı kapsayıcı |
| **AR** | AR-002_75 | Production Service Selection — yaratıcı servis seçimi |
| **AR** | AR-002_76 | Üretim Yürütme Mimarisi — içerik Executor tarafından üretilir |
| **PKG** | 16_PRODUCTION_PACKAGE_STANDARD.md | İçerik bölümleri (Brief, Senaryo, Storyboard, Prompt Setleri) |
| **KARAR** | 15_KARAR_GEREKCESI_STANDARDI.md | İçerik kararlarının gerekçeleriyle kaydı |
| **QR** | QR-004 | Kalite Kuralları — içerik kalite değerlendirmesi |
| **GK** | GK-001 | Genel Kurallar — brief araştırmanın merkezidir |

---

### Beklenen Sonuç

* Yaratıcı içerik üretimi standart hale gelir.
* Tek modele bağımlılık ortadan kalkar.
* Reklam stratejisi ve senaryo aynı anayasal çatı altında yönetilir.
* Nihai yaratıcı karar HLK tarafından verilir.
* Tüm yaratıcı içerikler Production Package içerisinde izlenebilir ve sürümlenebilir hale gelir.
* Gelecekte yeni yapay zekâ modelleri ve yaratıcı servis sağlayıcıları anayasal değişiklik gerektirmeden sisteme dahil edilebilir.
* Çoklu model çıktıları karşılaştırılabilir, birleştirilebilir ve iyileştirilebilir.
* İçerik değişiklikleri sürüm geçmişi ve gerekçeleriyle kayıt altına alınır.
* Constitution Scan Engine, yaratıcı içeriklerin Production Package'te kayıtlı olduğunu doğrulayabilir.

---

## AR-002_78

### Başlık

**Video Üretim İş Akışı Mimarisi — Video Production Workflow Architecture**

### Amaç

HLK tarafından onaylanan yaratıcı içeriklerin, anayasal kurallara uygun şekilde gerçek video üretimine dönüştürülmesini ve video üretim sürecinin standartlaştırılmasını sağlamak.

### Kural

HLK, video üretim sürecini yalnızca onaylanmış yaratıcı içerikler üzerinden başlatabilir.

Video üretimi ön koşulları:

* Yaratıcı içerikler HLK tarafından onaylanmış olmalıdır (AR-002_77).
* Production Runtime aktif olmalıdır (AR-002_70).
* PID oluşturulmuş ve geçerli olmalıdır (AR-002_71).
* Production Package hazır olmalıdır (AR-002_72).
* Task Package'ler oluşturulmuş olmalıdır (AR-002_74).
* Üretim servisleri seçilmiş ve doğrulanmış olmalıdır (AR-002_75).

---

### Video Üretim İş Akışının Anayasal Konumu

Video Üretim İş Akışı, Üretim Yürütme Mimarisi'nin (AR-002_76) video üretimi özelinde çalışan uzmanlaşmış alt katmanıdır.

AR-002_76'da tanımlanan Executor ilkeleri bu mimari için de geçerlidir:

* karar vermez (MASTER-004),
* servis seçmez (AR-002_75),
* yaratıcı içerik üretmez (AR-002_77),
* kalite değerlendirmesi yapmaz (QR-004).

Bu mimarinin görevi yalnızca video üretim sürecini yürütmektir.

---

### Video Üretimi Öncesi Doğrulama Adımları

Video üretimi başlamadan önce HLK, aşağıdaki doğrulamaları eksiksiz tamamlamak zorundadır.

**Adım 1 — Production Runtime Durumunun Doğrulanması**

HLK, Production Runtime'ın video üretimi için hazır olduğunu doğrular (AR-002_70, AR-002_76 Adım 1).

**Adım 2 — PID Doğrulaması**

HLK, PID'nin geçerli olduğunu doğrular (AR-002_71, AR-002_57).

**Adım 3 — Production Package Doğrulaması**

HLK, Production Package'in video üretimi için gerekli tüm bölümlerinin hazır olduğunu doğrular (AR-002_72, 16_PRODUCTION_PACKAGE_STANDARD.md):

* Brief (Bölüm 3),
* Senaryo (Bölüm 4),
* Prompt Setleri (Bölüm 6),
* Video Parametreleri (Bölüm 13).

**Adım 4 — İlgili Task Package'lerin Doğrulanması**

HLK, video üretimi için gerekli Task Package'lerin hazır olduğunu doğrular (AR-002_74):

* Her Task Package, Production Package ile ilişkilendirilmiştir,
* Her Task Package için uygun Agent atanmıştır,
* Agent çalışma yetkileri sınırlandırılmıştır.

**Adım 5 — Onaylanmış Yaratıcı İçeriklerin Hazır Olduğunun Doğrulanması**

HLK, yaratıcı içeriklerin HLK tarafından onaylanmış ve Production Package'e kaydedilmiş olduğunu doğrular (AR-002_77).

Onaylanmamış yaratıcı içerik ile video üretimi başlatılamaz.

**Adım 6 — Kullanılacak Üretim Servislerinin Hazır Olduğunun Doğrulanması**

HLK, video üretimi için seçilen servis sağlayıcılarının operasyonel olduğunu doğrular (AR-002_75, AR-002_76 Adım 5).

Bu doğrulamalar tamamlanmadan video üretimi başlatılamaz.

---

### Video Üretim Çalışma Sırası

Video Üretim İş Akışı sırasında HLK, aşağıdaki çalışma sırasını takip eder.

**Adım 1 — Üretim Paketinin Yüklenmesi**

HLK, Production Package'i ve içerdiği tüm video üretim verilerini yükler.

Yüklenen veriler:

* Onaylanmış senaryo (16_PRODUCTION_PACKAGE_STANDARD.md, Bölüm 4),
* Storyboard (Bölüm 5),
* Prompt Setleri (Bölüm 6),
* Referans Görseller (Bölüm 9),
* Video Parametreleri (Bölüm 13).

**Adım 2 — Onaylanmış Yaratıcı İçeriklerin Yüklenmesi**

HLK, HLK tarafından onaylanmış tüm yaratıcı içerikleri yükler (AR-002_77):

* Reklam stratejisi ve yaklaşımı,
* Onaylanmış senaryo metni,
* Sahne akışı ve açıklamaları,
* Hook ve CTA yapısı,
* Konuşma ve ekran metinleri,
* Görsel yönlendirmeler ve üretim notları.

**Adım 3 — İlgili Yürütme Görevlerinin Başlatılması**

HLK, video üretimi için gerekli yürütme görevlerini başlatır.

Her görev:

* AR-002_76 (Üretim Yürütme Mimarisi) standardına uygun olarak yürütülür,
* İlgili Task Package üzerinden ilgili Agent'a iletilir (AR-002_74),
* Seçilen servis sağlayıcısı kullanılarak gerçekleştirilir (AR-002_75),
* Execution Event'leri üretilir (AR-002_73).

**Adım 4 — Video Üretim Adımlarının Yönetilmesi**

HLK, video üretim adımlarını sıralı veya paralel olarak yönetir.

Yönetim yaklaşımı:

* **Sıralı:** Her adım bir öncekinin çıktısına bağlıysa sıralı yürütülür (örn: sahne render → montaj → ses ekleme).
* **Paralel:** Bağımsız adımlar eş zamanlı yürütülebilir (örn: farklı sahnelerin paralel render edilmesi).

HLK, üretim görevinin yapısına göre en uygun yönetim yaklaşımını belirler.

**Adım 5 — Ara Üretim Çıktılarının Bütünlüğünün Doğrulanması**

HLK, her üretim adımının çıktısının bütünlüğünü doğrular.

Doğrulama kapsamı:

* Çıktı formatı beklenen formatta mı?
* Çıktı boyutu ve süresi parametrelere uygun mu?
* Çıktı, bir sonraki adım için kullanılabilir durumda mı?
* Çıktıda teknik hata (bozuk dosya, eksik frame, sessiz bölüm) var mı?

Bu doğrulama kalite değerlendirmesi değildir. Yalnızca teknik bütünlük kontrolüdür. Kalite değerlendirmesi QR-004 ve FEAT-010'indir.

**Adım 6 — Gerektiğinde Üretim Adımlarının Yeniden Çalıştırılması**

HLK, bir üretim adımı başarısız olursa ilgili adımı yeniden çalıştırabilir.

Yeniden çalıştırma:

* AR-002_22 (Constitutional Feedback Loop) kapsamında denetlenir,
* AR-002_19 (Ajan Sürekliliği) uyarınca alternatif servise geçiş yapabilir,
* AR-002_21 (Ajan Değiştirme) uyarınca yeni Agent atayabilir.

**Adım 7 — Final Video Çıktısının Oluşturulması**

HLK, tüm üretim adımları başarıyla tamamlandıktan sonra final video çıktısını oluşturur.

Final video:

* Production Package'in **Nihai Video** bölümüne yazılır (16_PRODUCTION_PACKAGE_STANDARD.md, Bölüm 21),
* PID ile ilişkilendirilir (AR-002_57),
* Sürüm bilgisi ile kaydedilir (V1.0).

**Adım 8 — Final Video Çıktısının Production Package ile İlişkilendirilmesi**

HLK, final video çıktısını ilgili Production Package ile ilişkilendirir.

Bu ilişkilendirme ile:

* Final video, Production Package'in kalıcı kaydı haline gelir,
* PID üzerinden tüm üretim kayıtlarıyla çapraz referanslanabilir,
* Digital Asset Archive'e kaydedilmeye hazır hale gelir (12_DIGITAL_ASSET_ARCHIVE.md).

**Adım 9 — Video Üretiminin Tamamlandığının Kayıt Altına Alınması**

HLK, video üretiminin tamamlandığını Event sistemi üzerinden kayıt altına alır.

Oluşturulacak Event: `EVENT_VIDEO_PRODUCTION_COMPLETED` (OLAY-024, 14_OLAY_KAYIT_MERKEZI.md).

Bu Event:

* AR-002_73 (Production Event Runtime) standardına uygun olarak üretilir,
* PID alanı zorunlu olarak içerir,
* EEC tarafından toplanır,
* LAC üzerinden izlenebilir hale gelir.

**Adım 10 — Final Video Çıktısının Quality Control Sürecine Devredilmesi**

HLK, final video çıktısını Quality Control sürecine devreder.

Video üretimi tamamlandıktan sonra bu mimarinin görevi sona erer. Süreç anayasal olarak Quality Control katmanına devredilir (QR-004, FEAT-010).

---

### Video Üretim Event Kayıtları

Video üretimi sırasında oluşan durumlar, ilgili Event sistemi üzerinden kayıt altına alınmalıdır (AR-002_73):

| Durum | Event Türü | Referans |
|---|---|---|
| Üretim başlangıcı | `EVENT_VIDEO_PRODUCTION_STARTED` (OLAY-023) | 14_OLAY_KAYIT_MERKEZI.md |
| Ara üretim adımları | Adım tamamlanma Event'leri | AR-002_73 |
| Kısmi başarılar | Task tamamlanma Event'leri | AR-002_74 |
| Yeniden üretimler | Retry Event'leri | AR-002_22 |
| Hata durumları | Başarısızlık Event'leri | AR-002_19 |
| Servis değişiklikleri | AGENT_REPLACED Event'leri | AR-002_21 |
| Üretim tamamlanması | `EVENT_VIDEO_PRODUCTION_COMPLETED` (OLAY-024) | 14_OLAY_KAYIT_MERKEZI.md |

Tüm Event'ler PID ile ilişkilendirilir (AR-002_57) ve Production Package altında saklanır (AR-002_72).

---

### Ara Çıktı ve Nihai Video Yönetimi

Video üretimi sırasında oluşan tüm ara çıktılar ve nihai video:

* İlgili Production Package altında ilişkilendirilmelidir (AR-002_72),
* PID üzerinden sorgulanabilir olmalıdır (AR-002_57),
* Gerektiğinde geriye dönük olarak izlenebilmelidir,
* Production Package arşivlendiğinde birlikte arşivlenmelidir (16_PRODUCTION_PACKAGE_STANDARD.md).

Ara çıktılar, nihai video başarıyla üretildikten sonra da korunabilir. Bu, revizyon durumunda veya kalite kontrol sırasında geriye dönük analiz yapılabilmesini sağlar.

---

### Sınırlar ve Kapsam

Bu mimari;

* Video üretim sürecinin nasıl başlatılacağını, hangi adımlarla yürütüleceğini ve nasıl tamamlanacağını tanımlar,
* Ara çıktı ve nihai video yönetimini standartlaştırır,
* Quality Control'e devir noktasını belirler.

Bu mimari;

* Video üretim teknolojisini veya spesifik render yöntemini tanımlamaz — bunlar AR-002_75 kapsamında seçilen servislerin sorumluluğundadır.
* Kalite değerlendirmesi yapmaz — bu QR-004 ve FEAT-010'indir.
* Yaratıcı içerik üretmez — bu AR-002_77'nin sorumluluğundadır.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — video üretimi ANA YASA'ya tabidir |
| **MASTER** | MASTER-004 | Karar Mekanizması — video üretim kararları HLK'nındır |
| **AR** | AR-002_19 | Ajan Sürekliliği — üretim adımı başarısızlığında eskalasyon |
| **AR** | AR-002_21 | Ajan Değiştirme — servis değişimi |
| **AR** | AR-002_22 | Constitutional Feedback Loop — yeniden çalıştırma denetimi |
| **AR** | AR-002_57 | PID standardı — tüm çıktılar PID ile ilişkilendirilir |
| **AR** | AR-002_70 | STATE_VIDEO_PRODUCTION Runtime — üretim ortamı |
| **AR** | AR-002_71 | PID Runtime — PID doğrulama |
| **AR** | AR-002_72 | Production Package Runtime — çıktıların saklanacağı kapsayıcı |
| **AR** | AR-002_73 | Production Event Runtime — üretim Event kayıtları |
| **AR** | AR-002_74 | Task Package Runtime Integration — Task Package doğrulama |
| **AR** | AR-002_75 | Production Service Selection — üretim servisi seçimi |
| **AR** | AR-002_76 | Üretim Yürütme Mimarisi — görevlerin yürütülmesi |
| **AR** | AR-002_77 | Yaratıcı İçerik Üretim Mimarisi — onaylanmış içerik girdisi |
| **OLAY** | OLAY-023 | EVENT_VIDEO_PRODUCTION_STARTED |
| **OLAY** | OLAY-024 | EVENT_VIDEO_PRODUCTION_COMPLETED |
| **PKG** | 16_PRODUCTION_PACKAGE_STANDARD.md | Nihai Video bölümü (Bölüm 21) |
| **EEC** | 22_EXECUTION_EVENT_COLLECTOR.md | Event toplama |
| **KARAR** | 15_KARAR_GEREKCESI_STANDARDI.md | Üretim kararlarının kaydı |
| **QR** | QR-004 | Kalite Kuralları — QC devir noktası |
| **FEAT** | FEAT-010 | Quality Control |
| **FEAT** | FEAT-012 | Production Pipeline |
| **VARLIK** | 12_DIGITAL_ASSET_ARCHIVE.md | Nihai video arşivleme |

---

### Beklenen Sonuç

* Video üretim süreci standart hale gelir.
* Yaratıcı içerik ile video üretimi birbirinden ayrılır.
* Video üretimi tamamen izlenebilir hale gelir.
* Ara üretim adımları anayasal olarak kayıt altına alınır.
* Final video güvenli şekilde Quality Control sürecine devredilir.
* Gelecekte farklı video üretim teknolojileri anayasal değişiklik gerektirmeden sisteme entegre edilebilir.
* Hiçbir video üretim adımı, ön doğrulamalar tamamlanmadan başlatılamaz.
* Tüm ara çıktılar ve nihai video, PID üzerinden Production Package'te izlenebilir.
* Constitution Scan Engine, video üretim öncesi doğrulama adımlarını denetleyebilir.

---

## AR-002_79

### Başlık

**Üretim Sürekliliği Mimarisi — Production Continuity Architecture**

### Amaç

HLK'nın üretim süreci sırasında oluşabilecek teknik, operasyonel veya servis kaynaklı kesintilere rağmen, anayasal kurallar çerçevesinde üretimin güvenli, kontrollü ve izlenebilir şekilde devam ettirilmesini standartlaştırmak.

### Kural

HLK, üretim sürecinin sürekliliğini anayasal olarak korumakla yükümlüdür.

Bu yükümlülük, AR-002_19'un Production Runtime geneline yayılmış uygulamasıdır:

> AR-002_19: "HLK'nin temel ilkesi, mümkün olduğu sürece üretimi durdurmamak ve görevi tamamlamaya devam etmektir. Bir ajanın çalışamaması, tek başına görevin başarısız olduğu anlamına gelmez."

---

### Üretim Sürekliliği Mimarisinin Anayasal Konumu

Üretim Sürekliliği Mimarisi, HLK'nın **koruma ve kurtarma** katmanıdır:

* karar vermez (MASTER-004),
* servis seçmez (AR-002_75),
* üretim stratejisini değiştirmez (MASTER-004),
* yaratıcı içerik üretmez (AR-002_77),
* kalite değerlendirmesi yapmaz (QR-004).

Bu mimarinin görevi yalnızca üretimin güvenli şekilde devam etmesini sağlamaktır.

---

### Kapsanan Operasyonel Durumlar

Üretim sırasında aşağıdaki durumlar tespit edildiğinde Üretim Sürekliliği Mimarisi devreye girer:

| # | Durum | Açıklama | Öncelikli Referans |
|---|---|---|---|
| 1 | **Zaman Aşımı (Timeout)** | Görev GC zaman limitini aştı | AR-002_7, GC |
| 2 | **API Hatası** | Servis API'si hata döndürdü | AR-002_19, OR-004 |
| 3 | **Servis Erişim Problemi** | Servis kullanılamaz durumda | AR-002_19, OR-004 |
| 4 | **Kota Yetersizliği** | API kotası veya kredi tükendi | GC, OR-004 |
| 5 | **Bağlantı Kesintisi** | Ağ bağlantısı kesildi | OR-004 |
| 6 | **Üretim Başarısızlığı** | Görev tamamen başarısız oldu | AR-002_19, AR-002_76 |
| 7 | **Kısmi Üretim Başarısızlığı** | Görev kısmen tamamlandı | AR-002_22, AR-002_76 |
| 8 | **Yürütme Hatası** | Executor beklenmeyen hata verdi | AR-002_76 |
| 9 | **Beklenmeyen Sistem Hataları** | Öngörülemeyen hata durumları | OR-004 |
| 10 | **Gerekli Diğer Operasyonel Durumlar** | HLK'nın üretim bağlamına göre belirlediği ek durumlar | MASTER-004 |

Her durum tespit edildiğinde HLK:

* ilgili durumu kayıt altına almalı (AR-002_73),
* anayasal kurallara uygun şekilde değerlendirmeli (AR-002_22),
* uygun süreklilik aksiyonunu belirlemelidir.

---

### Süreklilik Aksiyonları

HLK, uygun gördüğü durumlarda aşağıdaki süreklilik aksiyonlarını uygulayabilir:

| Aksiyon | Açıklama | Ne Zaman Kullanılır? | Referans |
|---|---|---|---|
| **Yeniden Başlatma** | İşlemi baştan başlatır | Geçici hata, timeout | AR-002_22 (RETRY) |
| **Kaldığı Noktadan Devam** | İşlemi kesinti noktasından sürdürür | Kısmi tamamlanma, bağlantı kesintisi | AR-002_76 |
| **Yeniden Planlama** | Görevi yeniden planlar | Kaynak yetersizliği, kota | AR-002_22 (RE-EVALUATE) |
| **Alternatif Yürütme Yolu** | Farklı bir servis/Agent ile devam eder | Servis erişim problemi, API hatası | AR-002_19, AR-002_21 |
| **Karar Mekanizmasına Yönlendirme** | Süreci HLK Decision Engine'ine geri gönderir | Yeni karar gerektiğinde | AR-002_22, MASTER-004 |

---

### Süreklilik Aksiyon Seçimi

HLK, süreklilik aksiyonunu seçerken aşağıdaki faktörleri değerlendirir:

* **Hata Türü:** Geçici mi, kalıcı mı? (AR-002_22 Adım 2)
* **Üretim Aşaması:** Hata hangi adımda oluştu? (AR-002_78)
* **Alternatif Durumu:** Kullanılabilir alternatif servis/Agent var mı? (AR-002_19, AR-002_21)
* **Kalan Kaynak:** Kredi/kota yeterli mi? (GC, OR-004)
* **Zaman Etkisi:** Üretim takvimine etkisi ne olur?
* **Kalite Etkisi:** Alternatif yol kaliteyi etkiler mi? (QR-004)
* **Yeniden Deneme Sayısı:** Kaçıncı yeniden deneme? (AR-002_22: GC_MAX_RE_EVALUATION_COUNT)

Bu değerlendirme, HLK'nın karar mekanizması tarafından yapılır (MASTER-004).

---

### Servis Seçimi Sınırı

Üretim Sürekliliği Mimarisi hiçbir durumda yeni servis sağlayıcısı seçemez.

Yeni servis seçimi gerektiğinde:

* Süreç, Production Service Selection Architecture (AR-002_75) kapsamında HLK Karar Mekanizması tarafından yeniden değerlendirilmelidir.
* Mevcut dinamik ajan öncelik sıralamasındaki bir sonraki uygun aday devreye alınabilir (AR-002_19, AR-002_21).
* Ancak öncelik sıralamasında değişiklik gerekiyorsa bu karar yalnızca Decision Engine tarafından verilir (MASTER-004).

Bu sınır, MASTER-004'ün doğrudan gereğidir: servis seçimi bir karardır ve karar yetkisi yalnızca HLK'nındır.

---

### Süreklilik İşlemlerinin Kayıt Altına Alınması

Her süreklilik işlemi:

1. **İlgili PID ile ilişkilendirilmelidir** (AR-002_57) — tüm süreklilik kayıtları üretim kimliği altında toplanır.
2. **İlgili Production Package ile ilişkilendirilmelidir** (AR-002_72) — süreklilik kayıtları Production Package'in Event Logları bölümünde saklanır.
3. **İlgili Task Package ile ilişkilendirilmelidir** (AR-002_74) — hangi görevde kesinti oluştuğu belirtilir.
4. **İlgili Event kayıtlarını oluşturmalıdır** (AR-002_73) — her süreklilik aksiyonu bir Event üretir.
5. **Decision History ile ilişkilendirilebilmelidir** (15_KARAR_GEREKCESI_STANDARDI.md) — süreklilik kararları gerekçeleriyle kaydedilir.

---

### Yeniden Deneme Sınırı

Üretim Sürekliliği Mimarisi, AR-002_22'de tanımlanan yeniden değerlendirme sınırına tabidir:

* Maksimum yeniden değerlendirme sayısı: **3 (üç)** — `GC_MAX_RE_EVALUATION_COUNT` (AR-002_22 Bölüm 6.3).
* 3 başarısız yeniden değerlendirme sonrasında süreklilik girişimleri durur.
* Operasyonel eskalasyon başlatılır (AR-002_19).
* Yöneticiye bildirim gönderilir.
* Oturum askıya alınır.

Bu sınır, sonsuz tekrar döngülerini ve kontrolsüz kurtarma işlemlerini engeller.

---

### Kontrollü Sonlandırma

Üretimin güvenli şekilde devam ettirilemeyeceğinin anayasal olarak tespit edilmesi durumunda HLK:

* Üretim sürecini kontrollü şekilde sonlandırabilir,
* Durumu ilgili kayıt sistemlerine işlemekle yükümlüdür:
  * PID üzerinden Production Package'e sonlandırma kaydı,
  * EVENT_VIDEO_PRODUCTION_FAILED Event'i (varsa ilgili OLAY tanımı),
  * Decision History'ye sonlandırma gerekçesi,
  * Operasyonel eskalasyon kaydı.

Kontrollü sonlandırma, üretim başarısızlığı değildir. Anayasal olarak tanımlanmış, gerekçeli ve kayıt altına alınmış bir süreç sonlandırmasıdır.

---

### Sınırlar ve Kapsam

Bu mimari;

* Üretim kesintilerine karşı süreklilik mekanizmasını tanımlar,
* Süreklilik aksiyonlarının kayıt altına alınmasını standartlaştırır,
* Yeniden deneme sınırlarını ve kontrollü sonlandırma koşullarını belirler.

Bu mimari;

* Yeni karar üretmez — karar değişikliği gerektiğinde Decision Engine'i çağırır.
* Yeni servis seçmez — servis seçimi AR-002_75'in sorumluluğundadır.
* Kalite değerlendirmesi yapmaz — bu QR-004 ve FEAT-010'indir.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — süreklilik ANA YASA'ya tabidir |
| **MASTER** | MASTER-003 | ANA YASA/Kod Uyumluluk — süreklilik işlemleri denetlenebilir |
| **MASTER** | MASTER-004 | Karar Mekanizması — süreklilik karar vermez, HLK'ya yönlendirir |
| **AR** | AR-002_7 | Eş Zamanlı Ajan Çalıştırma — timeout yönetimi |
| **AR** | AR-002_19 | Ajan Sürekliliği ve Operasyonel Eskalasyon — temel dayanak |
| **AR** | AR-002_21 | Ajan Değiştirme ve Yeniden Seçim — alternatife geçiş |
| **AR** | AR-002_22 | Constitutional Feedback Loop — yeniden değerlendirme ve sayaç sınırı |
| **AR** | AR-002_57 | PID standardı — tüm süreklilik kayıtları PID ile ilişkilendirilir |
| **AR** | AR-002_72 | Production Package Runtime — kayıtların saklanacağı kapsayıcı |
| **AR** | AR-002_73 | Production Event Runtime — süreklilik Event kayıtları |
| **AR** | AR-002_74 | Task Package Runtime Integration — görev seviyesinde izleme |
| **AR** | AR-002_75 | Production Service Selection — yeni servis seçimi sınırı |
| **AR** | AR-002_76 | Üretim Yürütme Mimarisi — Execution Result kaynağı |
| **AR** | AR-002_78 | Video Üretim İş Akışı — üretim adımı bağlamı |
| **OR** | OR-004 | Operasyonel Kurallar — API, kredi, kota yönetimi |
| **GC** | GC_MAX_RE_EVALUATION_COUNT | Maksimum yeniden deneme sayısı |
| **GC** | GC zaman limiti parametreleri | Timeout eşikleri |
| **EEC** | 22_EXECUTION_EVENT_COLLECTOR.md | Süreklilik Event'lerinin toplanması |
| **KARAR** | 15_KARAR_GEREKCESI_STANDARDI.md | Süreklilik kararlarının gerekçeleriyle kaydı |

---

### Beklenen Sonuç

* Üretim kesintilerine karşı anayasal bir süreklilik mekanizması oluşturulur.
* Üretim güvenli ve kontrollü şekilde devam ettirilebilir.
* Süreklilik kararları tamamen izlenebilir hale gelir.
* Yeni servis seçimi yalnızca HLK Karar Mekanizması tarafından yapılır.
* Sonsuz tekrar döngüleri ve kontrolsüz kurtarma işlemleri engellenir.
* Üretim süreci kesintilere rağmen anayasal bütünlüğünü korur.
* Her süreklilik işlemi PID, Production Package ve Task Package ile ilişkilendirilir.
* Süreklilik sağlanamadığında üretim kontrollü şekilde sonlandırılır ve gerekçesi kaydedilir.
* Constitution Scan Engine, süreklilik işlemlerinin anayasal sınırlar içinde kaldığını doğrulayabilir.

---

## AR-002_80

### Başlık

**Üretim Kapanış Mimarisi — Production Closure Architecture**

### Amaç

HLK'nın Production Runtime sürecini anayasal kurallara uygun, eksiksiz, doğrulanabilir ve izlenebilir şekilde sonlandırmasını standartlaştırmak.

### Kural

HLK, bir üretim sürecini yalnızca anayasal kapanış kriterleri eksiksiz olarak sağlandığında tamamlanmış kabul edebilir.

Bu ilke, MASTER-003'ün Production Runtime kapanışı özelinde uygulanmasıdır:

> MASTER-003: "Bir değişiklik ancak ANA YASA Güncellendi + Kod Güncellendi + Runtime Davranışı Doğrulandı = TAMAMLANDI durumunda tamamlanmış kabul edilir."

Production Runtime kapanışı da aynı ilkeye tabidir: tüm bileşenler tamamlanmadan, tüm Event'ler üretilmeden ve tüm doğrulamalar yapılmadan kapanış gerçekleştirilemez.

---

### Üretim Kapanış Mimarisinin Anayasal Konumu

Üretim Kapanış Mimarisi, Production Runtime'ın **sonlandırma ve devir** katmanıdır:

* kalite değerlendirmesi yapmaz (QR-004, FEAT-010),
* teslim işlemini başlatmaz (AR-002_36),
* arşivleme işlemini gerçekleştirmez (12_DIGITAL_ASSET_ARCHIVE.md),
* kataloglama işlemini gerçekleştirmez (13_DIGITAL_ASSET_CATALOG.md),
* yeni üretim başlatmaz (AR-002_70).

Bu mimarinin görevi yalnızca Production Runtime'ın anayasal kapanışını gerçekleştirmek ve süreci bir sonraki anayasal katmana devredilmeye hazır hale getirmektir.

---

### Anayasal Kapanış Kriterleri

Production Runtime kapatılmadan önce HLK en az aşağıdaki doğrulamaları yapmak zorundadır.

| # | Kriter | Doğrulama Sorusu | Referans |
|---|---|---|---|
| 1 | **Production Runtime Tamamlanması** | Tüm üretim adımları başarıyla tamamlandı mı? | AR-002_70, AR-002_78 |
| 2 | **PID Geçerliliği** | PID hâlâ geçerli ve değiştirilmemiş durumda mı? | AR-002_57, AR-002_71 |
| 3 | **Production Package Eksiksizliği** | Tüm zorunlu bölümler dolduruldu mu? | AR-002_72, 16_PRODUCTION_PACKAGE_STANDARD.md |
| 4 | **Task Package Tamamlanması** | Tüm Task Package'ler tamamlandı mı? | AR-002_74 |
| 5 | **Açık Yürütme İşlemi** | Tamamlanmamış yürütme işlemi kaldı mı? | AR-002_76 |
| 6 | **Final Video Varlığı** | Nihai video oluşturulmuş ve PP'ye kaydedilmiş mi? | AR-002_78, 16_PRODUCTION_PACKAGE_STANDARD.md Bölüm 21 |
| 7 | **Zorunlu Üretim Çıktıları** | Tüm zorunlu çıktılar mevcut ve erişilebilir mi? | 16_PRODUCTION_PACKAGE_STANDARD.md |
| 8 | **Açık Kritik Hata** | Çözülmemiş kritik hata bulunuyor mu? | AR-002_79, AR-002_19 |
| 9 | **Açık Kritik Event** | Tamamlanmamış yaşam döngüsüne sahip Event var mı? | AR-002_73 |
| 10 | **Üretimin Anayasal Bütünlüğü** | Tüm anayasal kurallara uyuldu mu? | MASTER-003, CEE |

HLK, bu doğrulamaları kendi karar mekanizması ile değerlendirir (MASTER-004).

---

### Kapanış Çalışma Sırası

Doğrulama sonucunda üretimin anayasal olarak tamamlandığına karar verilirse HLK, aşağıdaki kapanış sırasını takip eder.

**Adım 1 — Production Runtime'ın Kapatılması**

HLK, Production Runtime'ı kapatır.

Kapatma ile:

* STATE_VIDEO_PRODUCTION state'i sonlandırılır (SE-007_3),
* Yeni yürütme işlemi başlatılamaz (AR-002_76),
* Production Runtime kaynakları serbest bırakılır.

Production Runtime kapatıldıktan sonra yeniden açılamaz. Yeni bir üretim için yeni bir STATE_VIDEO_PRODUCTION başlatılması gerekir (AR-002_70).

**Adım 2 — Üretim Kapanış Event'inin Oluşturulması**

HLK, Üretim Kapanış Event'ini oluşturur.

Bu Event:

* Production Event Runtime standardına uygundur (AR-002_73),
* PID alanı zorunlu olarak içerir (AR-002_57),
* EEC tarafından toplanır (22_EXECUTION_EVENT_COLLECTOR.md),
* LAC üzerinden izlenebilir hale gelir (FEAT-015),
* Production Package'in Event Logları bölümüne kaydedilir (16_PRODUCTION_PACKAGE_STANDARD.md, Bölüm 16).

**Adım 3 — Production Package Kapanış Bilgilerinin Güncellenmesi**

HLK, Production Package'in kapanış bilgilerini günceller.

Güncellenen alanlar:

* Production Metadata (16_PRODUCTION_PACKAGE_STANDARD.md, Bölüm 2):
  * Üretim durumu: "Tamamlandı" olarak işaretlenir,
  * Üretim tamamlanma tarihi ve saati kaydedilir,
* Production Package'in ilgili bölümleri son durumlarıyla korunur.

**Adım 4 — Runtime Kapanış Zamanının Kayıt Altına Alınması**

HLK, Runtime kapanış zamanını kayıt altına alır.

Bu kayıt:

* Production Metadata'ya işlenir,
* PID ile ilişkilendirilir,
* Toplam üretim süresinin hesaplanmasını sağlar (başlangıç → kapanış),
* Decision History'ye eklenir (15_KARAR_GEREKCESI_STANDARDI.md).

**Adım 5 — Üretim Durumunun İşaretlenmesi**

HLK, üretim durumunu "Tamamlandı" olarak işaretler.

Bu işaretleme:

* Production Package Metadata'ya yazılır,
* PID üzerinden sorgulanabilir,
* STATE_SESSION_COMPLETED geçişine izin verir (SE-007_4).

**Adım 6 — Sürecin Bir Sonraki Anayasal Katmana Devredilmesi**

HLK, süreci bir sonraki anayasal katmana devredilmeye hazır hale getirir.

Kapanış sonrası sıradaki süreçler:

* **Quality Control** — Final video kalite değerlendirmesi (QR-004, FEAT-010),
* **Delivery** — Nihai videonun kullanıcıya teslimi (AR-002_36),
* **Archive** — Production Package'in arşivlenmesi (12_DIGITAL_ASSET_ARCHIVE.md),
* **Catalog** — Dijital varlıkların kataloglanması (13_DIGITAL_ASSET_CATALOG.md).

Bu mimari, bu süreçleri başlatmaz; yalnızca güvenli devir için hazır hale getirir.

---

### Kapanış Kriterleri Sağlanmadığında

Anayasal kapanış kriterlerinden herhangi biri sağlanmıyorsa HLK:

1. **Eksikliği kayıt altına almalıdır** — hangi kriterin sağlanmadığı, neden sağlanmadığı PID üzerinden kaydedilir.
2. **Gerekiyorsa Üretim Sürekliliği Mimarisi'ni devreye almalıdır** (AR-002_79) — eksiklik giderilebilir nitelikteyse süreklilik aksiyonu uygulanır.
3. **Gerekiyorsa HLK Karar Mekanizmasına geri dönmelidir** (MASTER-004, AR-002_22) — eksiklik yeni bir karar gerektiriyorsa Decision Engine'e yönlendirilir.

Hiçbir üretim, anayasal kapanış işlemi tamamlanmadan tamamlanmış kabul edilemez.

---

### Kapanış Kayıtlarının İlişkilendirilmesi

Üretim kapanışına ilişkin tüm kayıtlar aşağıdaki sistemlerle ilişkilendirilmelidir:

| Kayıt Türü | İlişkilendirme | Referans |
|---|---|---|
| **PID** | Tüm kapanış kayıtları PID ile etiketlenir | AR-002_57 |
| **Production Package** | Kapanış bilgileri PP Metadata'ya yazılır | AR-002_72, 16_PRODUCTION_PACKAGE_STANDARD.md |
| **Event Kayıtları** | Kapanış Event'i PP Event Loglarına eklenir | AR-002_73 |
| **Decision History** | Kapanış kararı gerekçesiyle kaydedilir | 15_KARAR_GEREKCESI_STANDARDI.md |
| **EEC** | Kapanış Event'i EEC tarafından toplanır | 22_EXECUTION_EVENT_COLLECTOR.md |
| **LAC** | Kapanış, LAC üzerinden görüntülenebilir | FEAT-015 |

Tüm kapanış kayıtları geriye dönük olarak denetlenebilir olmalıdır.

---

### State Geçişi

Üretim kapanışı tamamlandığında State Engine aşağıdaki geçişi gerçekleştirir (SE-007_4):

```
STATE_VIDEO_PRODUCTION
→ EVENT_VIDEO_PRODUCTION_COMPLETED (OLAY-024)
→ STATE_SESSION_COMPLETED
```

Bu geçiş, Production Runtime yaşam döngüsünün resmi olarak sonlandığını ve oturumun tamamlanma aşamasına geçtiğini gösterir.

---

### Sınırlar ve Kapsam

Bu mimari;

* Production Runtime'ın anayasal kapanış kriterlerini ve kapanış sırasını tanımlar,
* Kapanış kayıtlarının ilişkilendirme standardını belirler,
* Bir sonraki anayasal katmanlara güvenli devir noktasını oluşturur.

Bu mimari;

* Quality Control, Delivery, Archive veya Catalog süreçlerini başlatmaz — bu süreçler kendi anayasal mimarileri tarafından yönetilir.
* Eksiklikleri gidermez — bu AR-002_79 (Üretim Sürekliliği) veya AR-002_22 (Feedback Loop) sorumluluğundadır.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — kapanış ANA YASA'ya tabidir |
| **MASTER** | MASTER-003 | ANA YASA/Kod Uyumluluk — kapanış doğrulanabilir |
| **MASTER** | MASTER-004 | Karar Mekanizması — kapanış kararı HLK'nındır |
| **AR** | AR-002_19 | Ajan Sürekliliği — açık kritik hata kontrolü |
| **AR** | AR-002_22 | Constitutional Feedback Loop — gerektiğinde karar mekanizmasına dönüş |
| **AR** | AR-002_36 | Scene Delivery — teslim sürecine devir |
| **AR** | AR-002_57 | PID standardı — tüm kapanış kayıtları PID ile ilişkilendirilir |
| **AR** | AR-002_70 | STATE_VIDEO_PRODUCTION Runtime — kapanışın başlangıç referansı |
| **AR** | AR-002_71 | PID Runtime — PID geçerlilik doğrulaması |
| **AR** | AR-002_72 | Production Package Runtime — PP kapanış güncellemesi |
| **AR** | AR-002_73 | Production Event Runtime — kapanış Event'i |
| **AR** | AR-002_74 | Task Package Runtime Integration — TP tamamlanma kontrolü |
| **AR** | AR-002_76 | Üretim Yürütme Mimarisi — açık yürütme işlemi kontrolü |
| **AR** | AR-002_78 | Video Üretim İş Akışı — final video varlığı |
| **AR** | AR-002_79 | Üretim Sürekliliği Mimarisi — eksiklik durumunda devreye alma |
| **SE** | SE-007_3 | STATE_VIDEO_PRODUCTION ve STATE_SESSION_COMPLETED tanımı |
| **SE** | SE-007_4 | State geçiş kuralları — kapanış sonrası geçiş |
| **OLAY** | OLAY-024 | EVENT_VIDEO_PRODUCTION_COMPLETED |
| **PKG** | 16_PRODUCTION_PACKAGE_STANDARD.md | Production Metadata güncellemesi |
| **EEC** | 22_EXECUTION_EVENT_COLLECTOR.md | Kapanış Event'inin toplanması |
| **KARAR** | 15_KARAR_GEREKCESI_STANDARDI.md | Kapanış kararının kaydı |
| **FEAT** | FEAT-015 | Live Activity Center — kapanış izleme |
| **VARLIK** | 12_DIGITAL_ASSET_ARCHIVE.md | Arşiv sürecine devir |
| **VARLIK** | 13_DIGITAL_ASSET_CATALOG.md | Katalog sürecine devir |

---

### Beklenen Sonuç

* Production Runtime anayasal kurallara uygun şekilde kapatılır.
* Eksik üretimlerin tamamlanmış kabul edilmesi engellenir.
* Üretim kapanışı tamamen doğrulanabilir ve izlenebilir hale gelir.
* Production Package anayasal olarak kapanır.
* Bir sonraki anayasal süreçlere (QC, Delivery, Archive, Catalog) güvenli geçiş sağlanır.
* Üretim yaşam döngüsü anayasal olarak eksiksiz tamamlanmış olur.
* Kapanış kriterleri sağlanmadığında üretim tamamlanmış kabul edilmez.
* Tüm kapanış kayıtları PID üzerinden geriye dönük denetlenebilir.
* Constitution Scan Engine, kapanış kriterlerinin tamamlandığını doğrulayabilir.

---

## AR-002_81

### Başlık

**HLK Runtime Karar Otoritesi ve Karar Talep Protokolü — HLK Runtime Decision Authority & Decision Request Protocol**

### Amaç

MASTER-013'te tanımlanan "HLK Runtime tek karar otoritesidir" prensibinin Runtime mimarisindeki resmi uygulamasını tanımlamak; yürütme katmanlarının karar üretmesini mimari seviyede engellemek ve karar gerektiren tüm durumlar için zorunlu Karar Talep Protokolü'nü standartlaştırmak.

### Kural

HLK_01_asistan projesinde, kullanıcının sistemi başlatan ilk tetikleyici komutu (örneğin /start) verildiği andan oturum tamamen kapanıncaya kadar tek karar otoritesi HLK Runtime'dır (MASTER-013).

Bu süre boyunca;

* Tüm modüller HLK Runtime'ın hiyerarşik kontrolü altında çalışır.
* Hiçbir modül, executor, runtime, pipeline, provider veya AI modeli HLK Runtime adına karar veremez.
* Decision Engine (MASTER-004, FEAT-002), Feedback Loop (AR-002_22), Selection Architecture (AR-002_49), CEE (AR-002_60) ve Escalation Engine; HLK Runtime'ın hiyerarşik kontrolü altında çalışan karar destek bileşenleridir. Bu bileşenler HLK Runtime'dan bağımsız karar yayınlayamaz.

---

### Karar Talep Protokolü (Decision Request Protocol)

Karar gerektiren bir durum oluştuğunda aşağıdaki çalışma sırası zorunludur:

**Adım 1 — Yürütmenin Durdurulması**

Yürütme katmanı, karar gerektiren noktada teknik yürütmeyi durdurur. Tereddüt halinde karar üretmek yasaktır; tereddüt de karar gerektiren durum kabul edilir.

**Adım 2 — Karar Talebinin (Decision Request) Oluşturulması ve İletilmesi**

Yürütme katmanı bir Karar Talebi oluşturur ve HLK Runtime'a iletir.

Karar Talebi en az aşağıdaki alanları içerir:

| Alan (Türkçe) | Alan (Teknik) | Açıklama |
|---|---|---|
| Talep Kimliği | request_id | Benzersiz karar talebi kimliği |
| Üretim Kimliği | pid | İlgili PID (AR-002_57) |
| Karar Kategorisi | category | Aşağıdaki Karar Kategorileri tablosundan |
| Talep Eden Katman | requester | Karar talebini üreten yürütme katmanı |
| Teknik Kanıt / Bağlam | context | Kararın dayanacağı ham teknik veriler (yorum içermez) |

Karar Talebi karar, öneri veya varsayım İÇEREMEZ; yalnızca ham teknik kanıt taşır.

**Adım 3 — HLK Runtime Kararının Üretilmesi**

HLK Runtime, kararını anayasal kurallara göre üretir. Gerektiğinde Decision Engine (yeniden değerlendirme — AR-002_22), Selection Architecture (seçim — AR-002_75) ve Escalation Engine (eskalasyon — AR-002_19) bileşenlerini kendi hiyerarşik kontrolü altında çalıştırır.

Üretilen Runtime Kararı en az aşağıdaki alanları içerir:

| Alan (Türkçe) | Alan (Teknik) | Açıklama |
|---|---|---|
| Karar Kimliği | decision_id | Benzersiz karar kimliği |
| Talep Kimliği | request_id | Karara esas talep |
| Karar | verdict | HLK Runtime'ın verdiği karar |
| Karar Parametreleri | params | Yürütmenin uygulayacağı parametreler |
| Karar Gerekçesi | rationale | 15_KARAR_GEREKCESI_STANDARDI.md uyumlu gerekçe |

**Adım 4 — Yürütmenin Karara Göre Devam Etmesi**

Yürütme katmanı, HLK Runtime kararını eksiksiz ve değiştirmeden uygular. Kararın uygulanması Event üretimi ile kayıt altına alınır (AR-002_73, EEC).

Her Karar Talebi ve Runtime Kararı; PID ile ilişkilendirilir (AR-002_57), Decision History'ye kaydedilir (15_KARAR_GEREKCESI_STANDARDI.md) ve Event sistemi üzerinden izlenebilir olur (AR-002_73, 22_EXECUTION_EVENT_COLLECTOR.md).

---

### Karar Kategorileri

Aşağıdaki durumların tamamı karar gerektiren durumdur ve yalnızca HLK Runtime tarafından karara bağlanır:

| # | Kategori | Açıklama | İlgili Referans |
|---|---|---|---|
| 1 | **PROVIDER_RESULT** | Provider çıktısının kabul veya reddi | AR-002_75, AR-002_76 |
| 2 | **PROVIDER_SWITCH** | Sıradaki provider adayına geçiş | AR-002_19, AR-002_21, AR-002_75 |
| 3 | **EXECUTION_FAILURE** | Başarısızlık/timeout sonrası retry, yeniden değerlendirme veya eskalasyon | AR-002_22, AR-002_79 |
| 4 | **CREATIVE_CONTENT** | Yaratıcı içerik (seslendirme metni vb.) belirlenmesi | AR-002_77 |
| 5 | **DELIVERY** | Teslim şekli ve kullanıcıya gönderilecek süreç mesajı içeriği | AR-002_36, FD-008_1, OR-004_11 |
| 6 | **COMPLETION** | Üretimin tamamlanmış kabul edilmesi | AR-002_80 |
| 7 | **USER_NOTIFICATION** | Süreç kararı içeren her türlü kullanıcı bilgilendirmesi | GK-001_5, OR-004_11 |
| 8 | **AMBIGUITY** | Tereddüt — yürütme katmanının karara bağlayamadığı her durum | MASTER-013 |

Bu tablo sınırlayıcı değildir; karar niteliği taşıyan her yeni durum bu protokole tabidir.

---

### Production Pipeline Karar Yasağı

production_pipeline.py hiçbir koşulda karar üretmeyecektir.

production_pipeline.py'nin görevi yalnızca;

* teknik yürütme,
* provider ile haberleşme,
* sonuç toplama,
* Event üretme,
* HLK Runtime tarafından verilen kararları eksiksiz uygulamaktır.

production_pipeline.py;

* PASS / FAIL,
* timeout,
* retry,
* provider kabul/red,
* provider değiştirme,
* kullanıcı bilgilendirmesi,
* completion

kararı üretemez.

Bu yasak; Production Executor (AR-002_76), Production Runtime (AR-002_70) ve diğer tüm yürütme katmanları için de geçerlidir. Yürütme katmanları karar gerektiren her durumda Karar Talep Protokolü'nü uygular.

---

### Sayısal Değer Yasağı

Yürütme katmanlarında kullanılan hiçbir sayısal değer (timeout, poll sayısı, bekleme aralığı, deneme sayısı vb.) kod içerisine hardcoded yazılamaz.

Tüm sayısal değerler yalnızca Global Configuration parametrelerinden okunur (01_Global_Configuration.md, GC İlkesi). Bu kapsamda tanımlı GC parametreleri:

`GC_PRODUCTION_TIMEOUT`, `GC_PRODUCTION_STEP_TIMEOUT`, `GC_EXECUTOR_MAX_RETRY`, `GC_EXECUTOR_TASK_TIMEOUT`, `GC_EXECUTOR_RETRY_DELAY`, `GC_RUNTIME_HEARTBEAT_INTERVAL`, `GC_PROVIDER_HTTP_TIMEOUT`, `GC_PROVIDER_STATUS_TIMEOUT`, `GC_PROVIDER_POLL_COUNT`, `GC_IMAGE_POLL_INTERVAL`, `GC_VIDEO_POLL_INTERVAL`, `GC_MAX_RE_EVALUATION_COUNT`.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — protokol ANA YASA'ya tabidir |
| **MASTER** | MASTER-004 | Karar Mekanizması — HLK tek karar vericidir |
| **MASTER** | MASTER-007 | Görev Ayrımı — AI Geliştirici/Executor uygulayıcıdır |
| **MASTER** | MASTER-013 | HLK Karar Otoritesi ve Üretim Yürütücüsü Rol Ayrımı |
| **AR** | AR-002_19 | Ajan Sürekliliği — eskalasyon çerçevesi |
| **AR** | AR-002_21 | Ajan Değiştirme — provider değişim çerçevesi |
| **AR** | AR-002_22 | Constitutional Feedback Loop — yeniden değerlendirme zinciri |
| **AR** | AR-002_36 | Scene Delivery — teslim kararlarının çerçevesi |
| **AR** | AR-002_57 | PID standardı — tüm karar kayıtları PID ile ilişkilendirilir |
| **AR** | AR-002_70 | STATE_VIDEO_PRODUCTION Runtime — yürütme ortamı |
| **AR** | AR-002_75 | Production Service Selection — provider seçim otoritesi |
| **AR** | AR-002_76 | Production Execution Architecture — Executor sınırları |
| **AR** | AR-002_77 | Creative Content Production — yaratıcı içerik kararları |
| **AR** | AR-002_79 | Production Continuity — süreklilik aksiyon çerçevesi |
| **AR** | AR-002_80 | Production Closure — completion kararı çerçevesi |
| **GK** | GK-001_5 | Kullanıcı mesajlarının sistem kurallarına göre üretilmesi |
| **OR** | OR-004_11 | Flow Diagram Zorunlu Konuşma Akışı |
| **OR** | OR-004_12 | Üretim Sırasında Karar Talebi Operasyon Kuralı |
| **MR** | MR-0005_7 | Modül Karar Bağımlılığı Kuralı |
| **GC** | 01_Global_Configuration.md | Sayısal değerlerin tek yetkili kaynağı |
| **KARAR** | 15_KARAR_GEREKCESI_STANDARDI.md | Karar gerekçelerinin kayıt standardı |
| **EEC** | 22_EXECUTION_EVENT_COLLECTOR.md | Karar Event'lerinin toplanması |
| **WF** | WF-017 | Runtime Decision Request workflow'u |

---

### Beklenen Sonuç

* HLK Runtime, oturum boyunca tek karar otoritesi olarak çalışır.
* Yürütme katmanları (production_pipeline.py dahil) hiçbir karar üretmez.
* Karar gerektiren her durum; durdur → talep et → karar → devam et akışıyla çözülür.
* Tereddüt durumları karar üretilmeden HLK Runtime'a iletilir.
* Tüm kararlar PID, Decision History ve Event sistemi ile izlenebilir olur.
* Kullanıcıya gönderilen süreç mesajları yalnızca HLK Runtime kararı ile üretilir.
* Yürütme katmanlarındaki tüm sayısal değerler GC parametrelerinden okunur.
* Constitution Scan Engine, karar üretiminin yalnızca HLK Runtime'da gerçekleştiğini denetleyebilir.
* Bu protokol; Workflow, Production, Research, Agent, Selection, Delivery, Quality Control, Constitution Enforcement, Feedback Loop ve gelecekte eklenecek tüm modüller için geçerlidir.

---

## AR-002_82

### Başlık

Mission Persistence Architecture (Görevde Israr Mimarisi)

### Amaç

HLK'nın temel görevi, kullanıcı tarafından talep edilen nihai çıktıyı mümkün olan en yüksek başarı olasılığıyla üretmektir.

Bu mimari; HLK'nın ilk başarısızlıkta görevi sonlandırmasını engeller ve anayasal olarak tanımlanmış tüm çözüm yollarını sistematik şekilde değerlendirmesini zorunlu hale getirir.

### Kural

HLK Runtime, kullanıcı tarafından talep edilen nihai çıktı başarıyla üretilmeden "Completed", "Delivered", "Production Completed" veya benzeri başarı kararlarını üretemez.

Her başarısız üretim girişiminden sonra HLK Runtime aşağıdaki anayasal değerlendirme sürecini işletmek zorundadır.

1. Başarısızlığın gerçek nedeni analiz edilir.
2. Hatanın geçici veya kalıcı olduğu belirlenir.
3. Problemin çözülebilir olup olmadığı değerlendirilir.
4. Mission Success olasılığı yeniden değerlendirilir.
5. Recovery süreci uygulanır.
6. Uygun görülen anayasal çözüm stratejileri yeniden planlanır.
7. Gerekli ise farklı Provider, farklı Model veya diğer anayasal mekanizmalar değerlendirilir.
8. Her karar HLK Runtime tarafından yeniden değerlendirilir ve gerekçelendirilir.

Recovery sürecinin amacı yalnızca yeniden deneme yapmak değildir.

Recovery süreci, kullanıcı tarafından talep edilen nihai çıktıyı üretebilmek için en uygun anayasal stratejiyi belirlemek ve uygulamaktır.

HLK Runtime, yeniden değerlendirme gerektiren veya çözülebilir hata türlerinde, anayasal Recovery Policy kapsamında tanımlanmış çözüm adımlarını uygulamadan bir Provider'ı "Provider Exhausted" durumuna geçiremez.

Bir Provider ancak ilgili anayasal Recovery Policy kapsamında tanımlanmış çözüm yolları tüketildikten sonra "Provider Exhausted" olarak işaretlenebilir.

HLK Runtime;

- ilk başarısızlığı nihai sonuç kabul etmez,
- kullanıcı hedefini esas alır,
- anayasal çözüm yollarını değerlendirmeden görevi sonlandıramaz,
- mümkün olan en yüksek başarı olasılığına ulaşmaya çalışır.

### Tamamlanma Kriteri

Production Completed kararı yalnızca aşağıdaki durumlardan biri gerçekleştiğinde üretilebilir.

- Kullanıcının talep ettiği nihai çıktı başarıyla üretilmiştir.

veya

- Anayasada tanımlanmış tüm ilgili çözüm mekanizmaları anayasal süreçlere uygun şekilde değerlendirilmiş ve HLK Runtime tarafından nihai karar gerekçelendirilmiştir.

Bu durumda üretim, anayasal olarak tanımlanmış uygun durum kodu ile sonlandırılır.

### Beklenen Sonuç

Bu mimari sayesinde;

- HLK erken vazgeçmez.
- HLK kullanıcı hedefini merkeze alır.
- Recovery süreci anayasal bir karar mekanizmasına dönüşür.
- Provider Exhausted kavramı standartlaşır.
- Recovery ile Mission Success birbirinden ayrılır.
- "Production Completed" kararı yalnızca anayasal gerekçelerle üretilebilir.
- HLK'nın temel başarı kriteri çalışan bir süreç değil, kullanıcıya ulaştırılan nihai çıktıdır.

---

## AR-002_83

### Başlık

Recovery Policy Architecture

### Amaç

Recovery Policy'nin amacı, üretim sürecinde meydana gelen başarısızlıkların ardından HLK Runtime'ın sistematik, tutarlı ve anayasal olarak tanımlanmış bir karar süreci uygulamasını sağlamaktır.

Recovery Policy, HLK'nın nasıl yeniden değerlendirme yapacağını, hangi çözüm yollarını hangi koşullarda değerlendireceğini ve bir üretim girişiminin hangi aşamada gerçekten tüketilmiş sayılacağını tanımlar.

### Kural

HLK Runtime, Recovery gerektiren her durumda anayasal Recovery Policy'yi uygulamak zorundadır.

Recovery Policy kapsamında HLK Runtime;

- başarısızlığın nedenini analiz eder,
- hatanın sınıfını belirler,
- problemin çözülebilir olup olmadığını değerlendirir,
- Mission Success olasılığını yeniden değerlendirir,
- uygun anayasal çözüm stratejilerini belirler,
- çözüm stratejilerinin uygulanmasına karar verir,
- her adımı yeniden değerlendirerek üretim sürecini yönetir.

Recovery Policy hiçbir zaman tek bir yeniden deneme mekanizması değildir.

Recovery Policy;

- Retry,
- Provider değerlendirmesi,
- Model değerlendirmesi,
- Prompt değerlendirmesi,
- Queue değerlendirmesi,
- Escalation değerlendirmesi,
- diğer anayasal çözüm mekanizmalarının tamamını kapsayan üst politika katmanıdır.

Recovery Policy kapsamında uygulanacak stratejiler, mevcut koşullar ve anayasal karar mekanizması tarafından belirlenir.

Recovery Policy'nin amacı mümkün olduğu kadar çok işlem yapmak değil, kullanıcı tarafından talep edilen nihai çıktıyı anayasal kurallar çerçevesinde en yüksek başarı olasılığıyla üretebilmektir.

Bir üretim girişiminin veya Provider'ın tüketildiğine ilişkin karar ancak Recovery Policy kapsamında gerekli anayasal değerlendirmeler tamamlandıktan sonra verilebilir.

### Beklenen Sonuç

Bu mimari sayesinde;

- Recovery süreci standartlaşır.
- Recovery kararları kişisel değil anayasal olur.
- Recovery mekanizması genişletilebilir hale gelir.
- Yeni Recovery stratejileri mevcut mimariyi değiştirmeden sisteme eklenebilir.
- Runtime kararlarının tutarlılığı artar.
- Mission Persistence ilkesi ile Recovery mekanizması birbirinden ayrılarak mimari sadeleşir.

---

## AR-002_84

### Başlık

**Yönetici Yeniden Üretim Prosedürü Mimarisi — Admin Reproduction Procedure Architecture**

### Amaç

HLK tarafından daha önce oluşturulmuş her Production Package'in, gerektiğinde HLK Anayasasına uygun şekilde yeniden üretilebilmesini standartlaştırmak.

Bu mimari; OLAY-025 (`EVENT_VIDEO_PRODUCTION_FAILED`) kaydında tanımlı **"Tekrar Deneme Politikası: Yönetici onayı gerekir"** hükmünün, AR-002_82 (Mission Persistence) ve AR-002_83 (Recovery Policy) çerçevesindeki resmi runtime uygulamasıdır.

### Kural

Üretimi başarısız olan veya yarım kalan bir PID'nin yeniden üretimi yalnızca **Yönetici** tarafından başlatılabilir.

Bu işlem **kullanıcı tarafından başlatılamaz.**

Yeniden üretim, yeni bir üretim türü değildir; mevcut üretimin AR-002_79 (Üretim Sürekliliği), AR-002_82 (Mission Persistence) ve AR-002_83 (Recovery Policy) kapsamındaki anayasal devamıdır. Bu nedenle;

* Yeni PID **oluşturulmaz** — mevcut PID korunur (AR-002_57 PID Tekillik Kuralı).
* Yeni Production Package **oluşturulmaz** — mevcut paket kullanılır (AR-002_58, PID↔Package 1:1).
* Üretim sonucunda oluşan yeni dijital varlıklar mevcut Production Package ile ilişkilendirilir ve sürüm geçmişi (`revision_history`) korunur (12_DIGITAL_ASSET_ARCHIVE.md Revizyon Standardı: mevcut varlıklar değiştirilmez).

---

### Yönetici İş Akışı

Yönetici sisteme yalnızca aşağıdaki bilgilerden birini verir:

* **PID** veya **Ürün Adı**

HLK ilgili Production Package'i mevcut arama mimarisiyle otomatik olarak bulur (AR-002_72; arama sınırları `GC_REPRODUCE_SEARCH_LIMIT` ve `GC_REPRODUCE_MAX_CANDIDATES` parametreleriyle yönetilir).

HLK aşağıdaki bilgileri Yöneticiye gösterir:

* PID
* Ürün Adı
* Marka
* Üretim Tarihi
* Mevcut Üretim Durumu

Ardından anayasal onay ekranı gösterilir:

> HLK Anayasasına göre bu üretim için yeniden üretim prosedürü uygulanacaktır.
>
> HLK;
> • Production Package'i inceleyecektir.
> • Üretim durumunu analiz edecektir.
> • Üretimin kaldığı yerden devam edip edemeyeceğini değerlendirecektir.
> • Gerekli olması halinde yeniden üretim prosedürünü uygulayacaktır.
> • Tüm işlemleri HLK Anayasasına uygun şekilde yönetecektir.
>
> Yeniden üretim prosedürünü başlatmak istiyor musunuz?
>
> [ Evet, Başlat ]   [ İptal ]

Bu onay ekranı, AR-002_56 (Yönetici Video Üretim Onay Katmanı) ile aynı anayasal deseni izler: üretim öncesi zorunlu insan kontrol katmanı.

---

### Anayasal Yeniden Üretim Prosedürü (Yönetici Onayı Sonrası)

Yönetici onay verdikten sonra HLK Runtime aşağıdaki prosedürü otomatik olarak işletir:

1. PID doğrulanır (AR-002_57, AR-002_71).
2. PID'ye bağlı Production Package bulunur (AR-002_72).
3. Production Package yüklenir.
4. Production Package'e bağlı Workflow bilgileri (Task Package listesi) yüklenir (AR-002_74).
5. State Engine kayıtları yüklenir (07_HLK_STATE_ENGINE.md).
6. Olay Kayıt Merkezi kayıtları yüklenir (14_OLAY_KAYIT_MERKEZI.md).
7. Dijital Varlık Arşivi kayıtları yüklenir (12_DIGITAL_ASSET_ARCHIVE.md).
8. Dijital Varlık Kataloğu kayıtları yüklenir (13_DIGITAL_ASSET_CATALOG.md).
9. Sahne Kayıt Defteri kayıtları (senaryo/storyboard) yüklenir (17_SAHNE_KAYIT_DEFTERİ.md).
10. Karar Gerekçesi kayıtları yüklenir (15_KARAR_GEREKCESI_STANDARDI.md).
11. Yeniden üretim için gerekli tüm anayasal bileşenlerin bütünlüğü doğrulanır (SHA-256 — 16_PRODUCTION_PACKAGE_STANDARD.md).
12. Son başarılı aşama belirlenir (Task Package checkpoint kayıtları — AR-002_76).
13. Başarısız olan aşama belirlenir.
14. HLK Runtime, üretimin kaldığı yerden devam edip edemeyeceğini değerlendirir (MASTER-013, AR-002_81 Karar Talep Protokolü — REPRODUCTION kategorisi).
15. Gerekli yeniden üretim stratejisi belirlenir (aşağıdaki Prosedür Kararları tablosu).
16. Gerekli Runtime kararları oluşturulur ve Decision History'ye kaydedilir.
17. Üretim otomatik olarak başlatılır (Production Package hazırlanır, Decision Engine servis seçimini yeniden değerlendirir — AR-002_75, AR-002_82 Adım 7).
18. Üretim tamamlanıncaya veya anayasal olarak sonlandırılıncaya kadar süreç HLK Runtime tarafından yönetilir (AR-002_79, `GC_PRODUCTION_TIMEOUT`, `GC_MAX_RE_EVALUATION_COUNT`).
19. Üretim boyunca oluşan tüm olaylar mevcut anayasal kayıt mekanizmalarına kaydedilir (EEC, Olay Kayıt Merkezi, LAC, Production Package Event Logları).
20. Üretim sonucunda oluşan yeni dijital varlıklar ilgili Production Package ile ilişkilendirilir ve sürüm geçmişi korunur.
21. Üretim tamamlandığında sonuç, anayasal bildirim kurallarına uygun şekilde Telegram üzerinden hem **Yöneticiye** hem de ilgili **Kullanıcıya** otomatik olarak bildirilir:
    * Üretim başarılıysa ilgili çıktılar teslim edilir (AR-002_36 Delivery).
    * Üretim başarısızsa üretim durumu ve anayasal karar gerekçesi bildirilir (EEC-001 Fake Progress yasağı).

Bu adımların hiçbiri atlanamaz. Bildirim içerikleri dahil tüm süreç mesajları yalnızca HLK Runtime USER_NOTIFICATION kararı ile üretilir (MASTER-013, OR-004_12, GK-001_5).

---

### Prosedür Kararları

HLK Runtime, REPRODUCTION Karar Talebini aşağıdaki anayasal çerçevede karara bağlar:

| Package Durumu | Karar | Uygulama | Referans |
|---|---|---|---|
| `FAILED` veya başarısız task var | **RETRY** | Yalnızca başarısız/zaman aşımına uğrayan task'lar yeniden yürütülür; tamamlanmış task'lar checkpoint'ten korunur | AR-002_83, AR-002_76 |
| `READY` / `BUILDING` / `PRODUCING` (yarım kalmış) | **RESUME** | Kaldığı noktadan devam edilir | AR-002_79 |
| `CREATED` (üretim hiç başlamamış) | **START_AS_NEW** | Mevcut PID korunarak normal üretim akışı başlatılır | AR-002_57 |
| `COMPLETED` | **REPLAY** | Yalnızca açık Yönetici talebiyle; mevcut dijital varlıklar korunarak yeni üretim sürümü oluşturulur | AR-002_82, 12_DAA Revizyon Standardı |
| `ARCHIVED` | **REJECT** | Arşivlenmiş paket immutable'dır; yeniden üretilemez | AR-002_58 |
| HLK Runtime aktif değil / tanımsız durum | **REJECT** | Güvenli sonlandırma (tereddüt halinde karar üretilmez) | MASTER-013, AR-002_62 |

Karar; gerekçeleri, alternatifleri ve sonuçlarıyla birlikte Production Package Decision History'ye kaydedilir (15_KARAR_GEREKCESI_STANDARDI.md — kayıtlar silinemez, yalnızca eklenir).

---

### İstisna Durumları

PID doğrulanamazsa **veya** Production Package bulunamazsa:

* HLK yeniden üretim prosedürünü **başlatmaz**.
* Durum, anayasal gerekçesiyle Yöneticiye bildirilir (OLAY-109).
* İşlem güvenli şekilde sonlandırılır.

---

### Yetki

Yönetici **yalnızca** yeniden üretim prosedürünü başlatır.

Aşağıdaki kararların tamamı yalnızca HLK Runtime tarafından HLK Anayasasına göre otomatik olarak alınır (MASTER-013, AR-002_81):

* Üretimin devam ettirilmesi
* Yeniden üretim kararı
* Runtime kararları
* Kurtarma kararları
* Sağlayıcı seçimleri
* Model seçimleri
* Üretim stratejileri
* Diğer tüm teknik kararlar

Yönetici teknik karar vermez.

Yönetici kimliği `TELEGRAM_ADMIN_USER_ID` yapılandırması ile doğrulanır; bu değer tanımlı değilse hiçbir kullanıcı Yönetici kabul edilmez (güvenli varsayılan).

---

### Olay Kayıtları

| Olay | Teknik Sabit | An |
|---|---|---|
| OLAY-107 | `EVENT_REPRODUCTION_REQUESTED` | Yönetici onayı alındığında |
| OLAY-108 | `EVENT_REPRODUCTION_STARTED` | HLK Runtime prosedür kararı üretip üretimi başlattığında |
| OLAY-109 | `EVENT_REPRODUCTION_REJECTED` | PID/paket doğrulanamadığında veya karar REJECT olduğunda |
| OLAY-024 | `EVENT_VIDEO_PRODUCTION_COMPLETED` | Yeniden üretim başarıyla tamamlandığında (yeniden kullanım) |
| OLAY-025 | `EVENT_VIDEO_PRODUCTION_FAILED` | Yeniden üretim başarısız olduğunda (yeniden kullanım) |

Tüm olaylarda PID alanı zorunludur (AR-002_57).

---

### Sınırlar ve Kapsam

Bu mimari;

* Yeni bir karar motoru **oluşturmaz** — kararlar HLK Runtime'ındır (MASTER-013).
* Yeni bir kurtarma mekanizması **oluşturmaz** — AR-002_79/82/83'te tanımlı mevcut süreklilik ve recovery mimarilerini Yönetici girişiyle tetiklenebilir hale getirir.
* Yeni PID veya yeni Production Package **oluşturmaz** (AR-002_57/58).
* State Engine'e yeni kullanıcı state'i **eklemez** — prosedür, kullanıcı konuşma akışı dışında, Production Runtime seviyesinde çalışır (SE-007_3 kullanıcı state makinesi değişmez).
* AR-002_80 Üretim Kapanış Mimarisini **değiştirmez** — anayasal kapanışı tamamlanmış bir Production Runtime yeniden açılmaz; yeniden üretim, aynı PID'ye bağlı **yeni bir yürütme döngüsü** başlatır.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | Karar Hiyerarşisi — prosedür ANA YASA'ya tabidir |
| **MASTER** | MASTER-003 | ANA YASA/Kod Uyumluluk — prosedür denetlenebilir |
| **MASTER** | MASTER-004 | Karar Mekanizması — nihai karar HLK'nındır |
| **MASTER** | MASTER-013 | HLK Runtime tek karar otoritesi; Yönetici teknik karar vermez |
| **AR** | AR-002_56 | Yönetici onay katmanı deseni (üretim öncesi insan kontrolü) |
| **AR** | AR-002_57 | PID standardı — PID korunur, yeni PID üretilmez |
| **AR** | AR-002_58 | Production Package — mevcut paket kullanılır |
| **AR** | AR-002_70 | Production Runtime tek giriş noktası — prosedür Production Runtime'a devredilir |
| **AR** | AR-002_72 | Production Package Runtime — paket arama/yükleme/hazırlama |
| **AR** | AR-002_73 | Production Event Runtime — olay kayıtları |
| **AR** | AR-002_76 | Production Execution — checkpoint'li yürütme |
| **AR** | AR-002_79 | Üretim Sürekliliği — "Kaldığı Noktadan Devam" aksiyonu |
| **AR** | AR-002_81 | Karar Talep Protokolü — REPRODUCTION kategorisi |
| **AR** | AR-002_82 | Mission Persistence — başarısızlık sonrası 8 adımlı değerlendirme |
| **AR** | AR-002_83 | Recovery Policy — üst politika katmanı |
| **OR** | OR-004_12 | Üretim sırasında Karar Talebi operasyon kuralı |
| **GK** | GK-001_5 | Bildirim metinlerinin sistem kurallarına göre üretilmesi |
| **GC** | GC_REPRODUCE_SEARCH_LIMIT, GC_REPRODUCE_MAX_CANDIDATES | Paket arama sınırları |
| **GC** | GC_PRODUCTION_TIMEOUT, GC_MAX_RE_EVALUATION_COUNT | Üretim ve yeniden değerlendirme sınırları |
| **OLAY** | OLAY-025 | "Tekrar Deneme Politikası: Yönetici onayı gerekir" — bu mimarinin doğrudan dayanağı |
| **OLAY** | OLAY-107, OLAY-108, OLAY-109 | Yeniden üretim olayları |
| **KARAR** | 15_KARAR_GEREKCESI_STANDARDI.md | Kararların gerekçeleriyle kaydı |
| **PKG** | 16_PRODUCTION_PACKAGE_STANDARD.md | Paket bütünlüğü ve revizyon geçmişi |
| **VARLIK** | 12/13_DIGITAL_ASSET | Varlık ilişkilendirme ve sürüm koruması |

---

### Beklenen Sonuç

* Yönetici yalnızca PID veya Ürün Adını girer.
* HLK ilgili Production Package'i otomatik olarak bulur.
* HLK yeniden üretim için gerekli tüm anayasal kayıtları ve üretim bileşenlerini otomatik olarak yükler.
* HLK üretimin kaldığı yerden devam edilip edilemeyeceğini değerlendirir.
* Gerekli yeniden üretim prosedürünü otomatik olarak uygular.
* Yönetici yalnızca üretimi başlatma onayı verir.
* Teknik kararların tamamı HLK Runtime tarafından alınır.
* Üretim sonucu Telegram üzerinden hem Yöneticiye hem de ilgili Kullanıcıya otomatik olarak bildirilir.
* Mevcut anayasal mimari korunur.

---

## AR-002_85

### Madde Adı

**VİDEO ÜRETİM BAŞARI İLKESİ**

### Kural

HLK;

gerçekte doğrulanmamış hiçbir video üretimini;

* başarı olarak değerlendiremez,
* tamamlandı olarak işaretleyemez,
* teslim edildi olarak kaydedemez,
* kullanıcıya veya yöneticiye gerçekleşmiş gibi bildiremez.

Bu anayasa maddesi;

* İlk Video Üretimi
* Yeniden Üretim
* Devam Ettirme
* Tekrar Deneme
* Toplu Üretim
* Gelecekte eklenecek bütün video üretim süreçleri

için zorunludur.

Hiçbir modül, servis, workflow, runtime, handler veya ajan bu anayasa maddesini ihlal edemez.

---

### BAŞARI KARARI

HLK;

aşağıdaki doğrulamaların **tamamı** başarıyla sonuçlanmadan;

* Üretim Tamamlandı
* Video Hazır
* Teslim Edildi
* Başarıyla Tamamlandı

kararlarından hiçbirini oluşturamaz.

---

### ZORUNLU DOĞRULAMALAR

HLK başarı kararı vermeden önce aşağıdaki durumları doğrulamak zorundadır.

1. Video dosyası gerçekten oluşturulmuştur.
2. Video dosyası fiziksel olarak mevcuttur.
3. Video dosyası okunabilmektedir.
4. Video dosyası geçerli bir video dosyasıdır.
5. Production Package video bilgisi başarıyla güncellenmiştir.
6. Teslim işlemi gerçekten gerçekleştirilmiştir.
7. Teslim işlemi başarıyla sonuçlanmıştır.
8. İlgili olay kayıtları eksiksiz oluşturulmuştur.
9. Constitution Enforcement Engine başarı kararını onaylamıştır.

Yukarıdaki doğrulamalardan herhangi biri başarısız ise;

HLK başarı kararı üretemez.

---

### YASAK

Kod içerisinde;

* `success=True`
* `başarı=True`

veya benzeri sabit başarı değerleri kullanılamaz.

Başarı kararı;

yalnızca doğrulanmış gerçek sonuçlardan hesaplanabilir.

Hiçbir modül HLK'ya doğrulanmamış başarı bilgisi gönderemez.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | ANA YASA üstünlüğü — bu kural tüm modülleri bağlar |
| **MASTER** | MASTER-003 | ANA YASA/Kod Uyumluluk — kod bu kurala uygun olmalı |
| **MASTER** | MASTER-004 | HLK Karar Mekanizması — başarı kararı yalnızca HLK'ya aittir |
| **MASTER** | MASTER-007 | AI Geliştirici görev ayrımı — PASS/FAIL kararı HLK/CEE'dedir |
| **MASTER** | MASTER-013 | HLK Runtime tek karar otoritesi — başarı bildirimi HLK kararıdır |
| **AR** | AR-002_70 | Production Runtime tek giriş noktası |
| **AR** | AR-002_76 | Production Execution — checkpoint'li yürütme ve sonuç doğrulama |
| **AR** | AR-002_79 | Üretim Sürekliliği — başarısızlık sonrası doğru durum |
| **AR** | AR-002_80 | Üretim Kapanış Mimarisi — tamamlanma kriterleri |
| **AR** | AR-002_84 | Yönetici Yeniden Üretim Prosedürü |
| **CEE** | CEE-001 | Fake Progress yasağı |
| **CEE** | CEE-006 | Kendi Kendine Düzeltme Kuralı |

---

### Beklenen Sonuç

* HLK yalnızca doğrulanmış video üretimlerini başarı olarak değerlendirir.
* Hiçbir kod yolu doğrulanmamış başarı üretemez.
* `success=True` gibi sabit değerler kod tabanından tamamen kaldırılmıştır.
* Tüm başarı kararları gerçek dosya varlığı, teslimat onayı ve CEE denetiminden geçer.
* Kullanıcıya veya Yöneticiye yanlış "teslim edildi" bildirimi gitmesi teknik olarak imkânsızdır.

---

## AR-002_86

### Madde Adı

**ANAYASAL YÜRÜTME İLKESİ**

### Kural

HLK Anayasası pasif bir doküman değildir.

HLK Anayasasının bütün maddeleri;

uygulanabildiği ölçüde,

HLK tarafından otomatik olarak yürütülmek zorundadır.

Yeni eklenen hiçbir anayasa maddesi yalnızca dokümanda kalamaz.

Her yeni anayasa maddesi;

* Constitution Scan Engine,
* Constitution Enforcement Engine,
* Constitution Diff Engine,
* Runtime,
* Workflow,

ve ilgili anayasal bileşenler tarafından uygulanabilir hale getirilmek zorundadır.

Uygulanmayan anayasa maddesi;

**"Pasif Anayasa Maddesi"**

olarak değerlendirilir.

Pasif anayasa maddeleri anayasal eksiklik kabul edilir.

HLK Runtime;

yalnızca Constitution Enforcement Engine tarafından anayasal olarak onaylanan kararları uygulayabilir.

Anayasal olarak uygulanmayan hiçbir karar;

* Başarılı
* Tamamlandı
* Teslim Edildi
* Kullanıcı Bildirimi
* Yönetici Bildirimi

oluşturamaz.

---

### Anayasal Yürütme Zinciri

HLK içerisinde anayasal yürütme aşağıdaki zincirle sağlanır:

```
ANA YASA Maddesi
    ↓
Constitution Scan Engine (CSE)        — kuralı tanır, koda eşler
    ↓
Constitution Diff Engine (CDE)        — değişiklikleri izler, etki analizi yapar
    ↓
Constitution Enforcement Engine (CEE) — ihlalleri tespit eder, engeller
    ↓
Runtime                               — yalnızca onaylı kararları uygular
```

Bu zincirdeki herhangi bir halka kopuksa;

ilgili anayasa maddesi **Pasif** kabul edilir.

---

### Anayasal Durum Sınıflandırması

Her anayasa maddesi aşağıdaki durumlardan birinde olmalıdır:

| Durum | Tanım | Koşul |
|---|---|---|
| **AKTİF** | Kural CEE tarafından runtime'da denetleniyor | CEE detect_violations bu kuralı kapsar |
| **KISMEN AKTİF** | Kural tanımlı ancak denetim eksik | CEE kısmen kapsar veya manuel denetim gerekir |
| **PASİF** | Kural yalnızca dokümanda var | Hiçbir runtime denetimi yok |

---

### Zorunlu Anayasal Tarama

HLK;

* Her yeni anayasa maddesi eklendiğinde,
* Her Runtime başlangıcında,
* Her Production başlangıcında,
* Her Reproduction başlangıcında

Constitution Scan Engine'i çalıştırarak bütün anayasa maddelerinin durumunu değerlendirir.

Pasif anayasa maddeleri tespit edilirse;

* Production başlatılmaz (güvenli varsayılan).
* Yöneticiye anayasal eksiklik bildirimi yapılır.
* Eksiklik giderilene kadar sistem kısıtlı modda çalışır.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | ANA YASA üstünlüğü — yürütme bu üstünlüğün teknik karşılığıdır |
| **MASTER** | MASTER-003 | ANA YASA/Kod Uyumluluk — yürütme olmadan uyumluluk sağlanamaz |
| **MASTER** | MASTER-004 | HLK Karar Mekanizması — kararlar anayasal denetimden geçer |
| **MASTER** | MASTER-011 | Runtime Aktiflik — anayasa maddeleri de runtime'da aktif olmalı |
| **MASTER** | MASTER-013 | HLK Runtime tek karar otoritesi — CEE onayı olmadan karar üretilemez |
| **AR** | AR-002_60 | Constitution Enforcement Engine — anayasal denetimin teknik uygulayıcısı |
| **AR** | AR-002_62 | Constitutional Boot Chain — sistem başlangıcında anayasal doğrulama |
| **AR** | AR-002_85 | Video Üretim Başarı İlkesi — doğrulanmamış başarı yasağı |

---

### Beklenen Sonuç

* HLK Anayasası yalnızca doküman değil, aktif yürütme sistemidir.
* Her anayasa maddesi CEE/CSE/CDE tarafından denetlenir.
* Pasif anayasa maddesi kalmaz.
* Anayasa ihlalleri insan müdahalesi olmadan tespit edilir ve engellenir.
* HLK Runtime yalnızca CEE onaylı kararları uygular.
* Anayasa dışı hiçbir "Başarılı", "Tamamlandı", "Teslim Edildi" kararı üretilemez.

---

## AR-002_87

### Madde Adı

**HARİCİ KAYNAK KURTARMA PROTOKOLÜ — External Resource Recovery Protocol**

### Kural

HLK, tüm harici kaynaklar (External Resources) için anayasal düzeyde tanımlanmış ortak bir Kurtarma Protokolü (External Resource Recovery Protocol) uygular.

Harici kaynak kavramı en az aşağıdaki bileşenleri kapsar;

* Servis Sağlayıcılar (Provider)
* AI Modelleri
* Agent'lar
* API Servisleri
* Harici Araçlar
* Harici Sistemler
* Gelecekte sisteme eklenecek tüm dış bağımlılıklar

HLK hiçbir harici kaynak türü için farklı anayasal Recovery mantığı oluşturmaz.

Tüm harici kaynaklar aynı anayasal Recovery yaşam döngüsünü kullanır.

---

### Anayasal Recovery Yaşam Döngüsü

Bu yaşam döngüsü en az aşağıdaki anayasal aşamalardan oluşur;

1. **Kaynağın sınıflandırılması** — Harici kaynağın türü, önceliği ve kritiklik seviyesi belirlenir.
2. **Hata türünün belirlenmesi** — HTTP hatası, timeout, yetkilendirme, kota, format, bağlantı gibi kategorize edilir.
3. **Hatanın geçici veya kalıcı olduğunun değerlendirilmesi** — Geçici hatalar (timeout, rate-limit) ile kalıcı hatalar (auth, quota) ayrıştırılır.
4. **Recovery sürecinin başlatılması** — Geçici hatalar için anayasal bekleme ve yeniden deneme; kalıcı hatalar için doğrudan alternatif kaynağa geçiş.
5. **Kaynağın durumunun yeniden doğrulanması** — Recovery sonrası kaynağın çalışır durumda olup olmadığı test edilir.
6. **Gerekirse kontrollü yeniden deneme (Retry)** — AR-002_76 kapsamında GC parametreleriyle sınırlandırılmış retry.
7. **Gerekirse anayasal bekleme stratejisinin uygulanması (Backoff)** — Exponential backoff veya sabit aralıklı bekleme, GC parametrelerine göre.
8. **Recovery limitlerinin değerlendirilmesi** — `GC_EXECUTOR_MAX_RETRY`, `GC_MAX_RE_EVALUATION_COUNT` sınırları aşıldı mı?
9. **Kaynağın başarısız ilan edilmesi** — Tüm recovery adımları başarısız olduğunda, kanıt temelli olarak FAILED işaretlenir.
10. **Decision Engine'e devredilmesi** — Başarısız kaynak Decision Engine'e bildirilir; yeniden değerlendirme başlatılır (AR-002_75).
11. **Alternatif kaynağın anayasal kurallara göre seçilmesi** — Selection Architecture öncelik sıralamasına göre bir sonraki aday seçilir (AR-002_19, AR-002_21).

---

### Başarısızlık Kriterleri

HLK yalnızca Timeout oluştuğu için bir harici kaynağı başarısız kabul etmez.

Bir harici kaynağın başarısız ilan edilmesi yalnızca anayasal olarak tanımlanmış başarısızlık kriterlerinin oluşması halinde mümkündür:

* Tüm retry denemeleri tükenmiştir (AR-002_76).
* Anayasal bekleme stratejisi eksiksiz uygulanmıştır.
* Kaynak doğrulama testi başarısız olmuştur.
* Kalıcı hata tespit edilmiştir (auth, quota, invalid_config).
* Recovery limitleri aşılmıştır (AR-002_22, AR-002_79).

---

### Kanıt ve Kayıt Zorunluluğu

Recovery süreci boyunca alınan tüm kararlar kanıt temelli olmak zorundadır.

Recovery sürecinde verilen tüm kararlar;

* Event Log (EEC + Olay Kayıt Merkezi),
* Decision Log (15_KARAR_GEREKCESI_STANDARDI.md),
* Production Package Event Logları

üzerinden izlenebilir şekilde kaydedilir.

---

### Durum Kodu Standardı

Her harici kaynak kendi teknik durum kodlarını (Status) kullanabilir.

Örneğin;

* Provider: `COMPLETED`, `PROCESSING`, `QUEUED`, `FAILED`
* Agent: `AGENT_SUCCESS`, `AGENT_FAILED`, `AGENT_TIMEOUT`
* API: HTTP durum kodları (200, 429, 503, vb.)
* AI Modeli: `completed`, `running`, `failed`, `queued`

Ancak HLK'nın bu durumlara vereceği anayasal Recovery davranışı tüm harici kaynaklar için ortak olmak zorundadır.

HLK, kaynağa özgü durum kodunu anayasal Recovery yaşam döngüsündeki karşılığına eşler:

| Kaynak Durumu | Anayasal Sınıflandırma | Recovery Davranışı |
|---|---|---|
| `COMPLETED` / `success` | Başarılı | Recovery gerekmez |
| `PROCESSING` / `QUEUED` / `running` | Geçici — işlem devam ediyor | Durum sorgulamasına devam et |
| `FAILED` / `AGENT_FAILED` | Kalıcı | Doğrudan alternatif kaynağa geç |
| Timeout | Geçici | Retry + backoff |
| HTTP 429 (Rate Limit) | Geçici | Backoff + retry |
| HTTP 401/403 (Auth) | Kalıcı | Doğrudan alternatif kaynağa geç |
| HTTP 5xx (Server Error) | Geçici | Retry + backoff |

---

### Zorunluluk ve Kapsam

Bu mimari, HLK sistemindeki tüm modüller için zorunlu anayasal davranış standardıdır.

Hiçbir modül;

* Bu mimariyi devre dışı bırakamaz.
* Kendi alternatif Recovery Protokolünü oluşturamaz.
* Anayasal Recovery yaşam döngüsünü atlayamaz.
* Decision Engine onayı olmadan farklı bir kurtarma stratejisi uygulayamaz.

Kaynak türüne özgü teknik uygulamalar farklı olabilir.

Ancak tüm modüller anayasal olarak tanımlanan External Resource Recovery Protocol'ünü uygulamak zorundadır.

---

### Temel İlke

HLK'nın başarı kriteri, ilk hatada kaynağı değiştirmek değil; anayasal Recovery Protokolünü eksiksiz uyguladıktan sonra en doğru anayasal kararı vermektir.

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | ANA YASA üstünlüğü — bu protokol tüm modülleri bağlar |
| **MASTER** | MASTER-004 | HLK Karar Mekanizması — kaynak değiştirme kararı HLK'ya aittir |
| **MASTER** | MASTER-013 | HLK Runtime tek karar otoritesi — recovery kararları HLK Runtime'dadır |
| **AR** | AR-002_19 | Selection Architecture — alternatif kaynak öncelik sıralaması |
| **AR** | AR-002_21 | Provider Switching — sıradaki adaya geçiş kararı |
| **AR** | AR-002_22 | Feedback Loop — yeniden değerlendirme mekanizması |
| **AR** | AR-002_57 | PID Standardı — recovery kayıtlarında PID zorunluluğu |
| **AR** | AR-002_60 | Constitution Enforcement Engine — recovery kararlarının denetimi |
| **AR** | AR-002_70 | Production Runtime — recovery'nin tek giriş noktası |
| **AR** | AR-002_75 | Decision Engine — alternatif kaynak seçimi |
| **AR** | AR-002_76 | Production Execution — retry ve checkpoint mekanizması |
| **AR** | AR-002_79 | Üretim Sürekliliği — başarısızlık sonrası devam |
| **AR** | AR-002_81 | Karar Talep Protokolü — PROVIDER_RESULT, EXECUTION_FAILURE |
| **AR** | AR-002_82 | Mission Persistence — 8 adımlı başarısızlık değerlendirmesi |
| **AR** | AR-002_83 | Recovery Policy — üst politika katmanı |
| **AR** | AR-002_86 | Anayasal Yürütme İlkesi — protokolün aktif denetimi |
| **GC** | GC_EXECUTOR_MAX_RETRY | Maksimum yeniden deneme sayısı |
| **GC** | GC_EXECUTOR_RETRY_DELAY | Denemeler arası bekleme süresi |
| **GC** | GC_MAX_RE_EVALUATION_COUNT | Maksimum yeniden değerlendirme sayısı |

---

### Beklenen Sonuç

* Tüm harici kaynaklar aynı anayasal Recovery yaşam döngüsünü kullanır.
* Hiçbir modül kendi alternatif recovery protokolü oluşturamaz.
* Recovery kararları kanıt temelli ve izlenebilirdir.
* Kaynak değiştirme yalnızca anayasal kriterler sağlandığında yapılır.
* İlk hatada kaynak değiştirilmez — önce anayasal recovery uygulanır.
* Tüm recovery süreci Event Log ve Decision Log'a kaydedilir.
* Decision Engine onayı olmadan alternatif kaynağa geçilmez.

---

## AR-002_88

### Madde Adı

**ÜRETİM KARAR YETKİ ZİNCİRİ — Production State Ownership**

### Amaç

Production sürecinde Event, Status ve Decision katmanlarının birbirinden kesin olarak ayrılmasını sağlamak.

Hiçbir yürütme bileşeni anayasal karar üretemez.

---

### 1. Production Executor

Production Executor yalnızca **yürütme katmanıdır.**

Görevleri:

* Task yürütmek
* Teknik sonuç üretmek
* Teknik Event yayınlamak

Örnek Event'ler:

* `TASK_STARTED`
* `TASK_PROGRESS`
* `TASK_COMPLETED`
* `TASK_FAILED`
* `VIDEO_CREATED`
* `VIDEO_NOT_CREATED`
* `DOWNLOAD_COMPLETED`
* `DOWNLOAD_FAILED`
* `UPLOAD_COMPLETED`
* `UPLOAD_FAILED`
* `EXECUTION_FINISHED`

Bu Event'ler **karar değildir.** Yalnızca teknik durum bildirimidir.

Executor hiçbir koşulda aşağıdaki kararları üretemez:

* `COMPLETED`
* `FAILED`
* `RETRY`
* `RESUME`
* `REPLAY`
* `ESCALATE`
* `CANCELLED`

Executor hiçbir koşulda:

`PackageStatus.update(...)`

çağıramaz.

---

### 2. Production Runtime

Production Runtime;

* Executor'dan gelen Event'leri toplar.
* Gerekli tüm teknik doğrulamaları yapar.

Örneğin:

* Video gerçekten üretildi mi?
* Asset oluştu mu?
* Dosya erişilebilir mi?
* Production Package bütünlüğü sağlandı mı?
* Delivery teknik olarak mümkün mü?

Production Runtime **karar üretmez.**

Sadece **Decision Request** oluşturur.

---

### 3. HLK Runtime

HLK Runtime sistemin **tek karar otoritesidir** (MASTER-013).

Production Runtime'dan gelen Decision Request'i değerlendirir.

AR-002_80 başta olmak üzere ilgili anayasal maddeleri uygular.

Nihai kararlardan yalnızca HLK Runtime sorumludur.

---

### 4. Constitution Enforcement Engine (CEE)

CEE;

HLK Runtime tarafından üretilen anayasal kararın kurallara uygunluğunu doğrular.

Kararı:

* Onaylayabilir
* Reddedebilir
* Yeniden değerlendirilmesini isteyebilir

---

### 5. Package Status Ownership

Package Status;

teknik bir değişken değildir.

Package Status;

HLK Runtime tarafından verilen anayasal kararın kayıt altına alınmış sonucudur.

Bu nedenle Package Status yalnızca aşağıdaki zincir tamamlandıktan sonra güncellenebilir:

```
Executor                 → Teknik Event yayınlar
        ↓
Production Runtime       → Event'leri toplar, doğrular, Decision Request oluşturur
        ↓
HLK Runtime              → Anayasal kararı üretir
        ↓
CEE Validation           → Kararı denetler, onaylar veya reddeder
        ↓
Package Status Update    → Karar kayıt altına alınır
```

Bu zincir dışında **hiçbir modül** Package Status değiştiremez.

---

### Yasaklar

Aşağıdaki işlemler anayasal olarak yasaktır:

* Executor'ın `COMPLETED` kararı üretmesi
* Executor'ın `FAILED` kararı üretmesi
* Executor'ın `PackageStatus` değiştirmesi
* Runtime dışındaki bileşenlerin Completion kararı vermesi
* Teknik Event'lerin anayasal karar yerine kullanılması

---

### Temel İlke

**Event bilgi üretir.**

**Runtime değerlendirme yapar.**

**HLK karar verir.**

**CEE doğrular.**

**Package yalnızca kararı kaydeder.**

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **MASTER** | MASTER-001 | ANA YASA üstünlüğü — yetki zinciri tüm modülleri bağlar |
| **MASTER** | MASTER-004 | HLK Karar Mekanizması — nihai karar HLK'ya aittir |
| **MASTER** | MASTER-007 | AI Geliştirici görev ayrımı — Executor uygulayıcıdır, karar verici değil |
| **MASTER** | MASTER-013 | HLK Runtime tek karar otoritesi |
| **AR** | AR-002_60 | Constitution Enforcement Engine — CEE karar denetimi |
| **AR** | AR-002_70 | Production Runtime — tek giriş noktası ve orkestratör |
| **AR** | AR-002_76 | Production Execution — Executor'un anayasal konumu |
| **AR** | AR-002_80 | Üretim Kapanış Mimarisi — COMPLETED kararının kriterleri |
| **AR** | AR-002_85 | Video Üretim Başarı İlkesi — doğrulanmamış başarı yasağı |
| **AR** | AR-002_86 | Anayasal Yürütme İlkesi — CEE onayı olmadan karar üretilemez |

---

### Beklenen Sonuç

* Executor yalnızca teknik Event yayınlar, asla karar üretmez.
* Production Runtime yalnızca Decision Request oluşturur, karar vermez.
* HLK Runtime sistemdeki tek karar otoritesidir.
* CEE tüm anayasal kararları denetler.
* Package Status yalnızca anayasal zincir tamamlandıktan sonra güncellenir.
* Hiçbir modül yetki zincirini atlayarak doğrudan Package Status değiştiremez.
* Teknik Event ile anayasal karar birbirine karıştırılamaz.

---

## AR-002_89

### Madde Adı

**PROVIDER DURUM SORGULAMA MİMARİSİ — Provider Polling Architecture**

### Amaç

HLK'nın harici üretim servis sağlayıcılarını (Provider) sabit zaman aşımı (Fixed Timeout) mantığı ile yönetmesini engellemek; Provider yönetimini anayasal karar mekanizmasına bağlı, gerçek zamanlı geri bildirim ve üretim yaşam döngüsü esaslı standart bir polling mimarisine oturtmak.

### Kural

HLK, harici üretim servis sağlayıcılarını sabit zaman aşımı mantığı ile yönetmez. Provider yönetimi anayasal karar mekanizması tarafından yürütülür ve Provider'ın canlı durumu (State), gerçek zamanlı geri bildirimi ve üretim yaşam döngüsü esas alınır.

---

### Anayasal Polling Parametreleri

Provider bekleme politikası aşağıdaki anayasal parametreler kullanılarak yürütülür:

| Parametre | Değer | Açıklama |
|---|---|---|
| `GC_PROVIDER_POLL_INTERVAL` | 50 | Her Provider durum sorgulaması (Poll) arasındaki bekleme süresi (saniye). |
| `GC_PROVIDER_MAX_POLL_COUNT` | 5 | Bir Provider için gerçekleştirilecek en fazla durum sorgulama (Poll) sayısı. |

Bu parametreler `01_Global_Configuration.md` içerisinde tanımlıdır ve sistem genelinde tüm Provider'lar için ortak anayasal standarttır.

---

### Polling Çalışma Kuralları

HLK aşağıdaki kuralları uygular:

1. Provider üretim isteğini kabul ettikten sonra durum sorgulamaları `GC_PROVIDER_POLL_INTERVAL` değerine göre gerçekleştirilir.

2. HLK en fazla `GC_PROVIDER_MAX_POLL_COUNT` kadar durum sorgulaması yapar.

3. Aşağıdaki Provider durumları **aktif üretim** olarak kabul edilir:
   - `QUEUED`
   - `WAITING`
   - `GENERATING`

   Provider bu durumlardan birini döndürdüğü sürece HLK üretimin devam ettiğini kabul eder ve bir sonraki durum sorgulamasına kadar bekler.

4. Provider aşağıdaki durumlardan herhangi birini döndürürse bekleme **derhal** sonlandırılır:
   - `FAILED`
   - `ERROR`
   - `REJECTED`
   - `CANCELLED`

   Bu durumda:
   - HLK kalan Poll haklarını kullanmaz.
   - Provider anayasal olarak başarısız kabul edilir.
   - HLK anayasal Provider seçim mekanizmasına göre hemen bir sonraki uygun Provider'a geçer (AR-002_75, AR-002_21).

5. Provider, `GC_PROVIDER_MAX_POLL_COUNT` sınırına ulaştığı halde `COMPLETED` durumuna geçmemişse ilgili Provider **TIMEOUT** olarak değerlendirilir ve anayasal Provider seçim mekanizmasına göre bir sonraki Provider'a geçilir (AR-002_75, AR-002_79).

6. Provider `COMPLETED` durumuna geçtiğinde yalnızca durum bilgisi başarı kabul edilmez. Üretilen çıktı anayasal Artifact doğrulama mekanizmasından geçirilir (AR-002_85). Artifact doğrulaması başarısız ise üretim başarılı sayılmaz.

---

### Provider Değişim Kaydı

Her Provider değişiminde HLK aşağıdaki bilgileri Event Collector (AR-002_73) ve Karar Gerekçesi (15_KARAR_GEREKCESI_STANDARDI.md) kayıtlarına işler:

| Kayıt Alanı | Açıklama |
|---|---|
| Provider Adı | Değiştirilen Provider'ın kimliği |
| Son Provider Durumu | Değişim anındaki Provider state değeri |
| Toplam Bekleme Süresi | Provider için harcanan toplam süre |
| Yapılan Poll Sayısı | Gerçekleştirilen durum sorgulama sayısı |
| Provider Değiştirme Gerekçesi | Değişimin anayasal nedeni |
| Verilen Anayasal Karar | HLK Runtime karar kimliği |

---

### Anayasal Sınırlar

HLK hiçbir koşulda:

* tek bir Provider nedeniyle üretim sürecini durduramaz,
* sonsuz bekleme durumuna giremez,
* anayasal karar mekanizmasını devre dışı bırakamaz.

Bu sınırlar sistemdeki tüm harici üretim servis sağlayıcıları için mutlak anayasal güvencedir.

---

### Temel İlke

**Provider yönetimi sabit timeout değil, anayasal karar mekanizması tarafından yürütülen dinamik bir polling mimarisidir. Provider'a özel implementasyonlar bu mimari standardı ihlal edemez.**

---

### Anayasal Dayanak

| Katman | Referans | Dayanak Açıklaması |
|---|---|---|
| **GC** | `GC_PROVIDER_POLL_INTERVAL` | Provider durum sorgulama aralığı (50 saniye) |
| **GC** | `GC_PROVIDER_MAX_POLL_COUNT` | Maksimum durum sorgulama sayısı (5) |
| **AR** | AR-002_21 | Provider Switching — sıradaki adaya geçiş kararı |
| **AR** | AR-002_73 | Production Event Runtime — Provider değişim Event kaydı |
| **AR** | AR-002_75 | Production Service Selection — aday havuzu ve seçim |
| **AR** | AR-002_79 | Production Continuity — TIMEOUT sonrası süreklilik |
| **AR** | AR-002_85 | Video Üretim Başarı İlkesi — Artifact doğrulama zorunluluğu |
| **AR** | AR-002_87 | External Resource Recovery — başarısızlık sonrası kurtarma |

---

### Beklenen Sonuç

* Tüm Provider'lar aynı anayasal polling standardını kullanır.
* Hiçbir Provider sabit timeout ile yönetilmez; karar her zaman HLK Runtime'a aittir.
* Aktif üretim durumları (QUEUED, WAITING, GENERATING) ile başarısız durumlar (FAILED, ERROR, REJECTED, CANCELLED) anayasal olarak ayrıştırılır.
* Başarısız durum tespitinde kalan Poll hakları kullanılmaz; derhal bir sonraki Provider'a geçilir.
* Poll sınırı aşımında Provider TIMEOUT kabul edilir ve alternatif Provider'a geçilir.
* COMPLETED durumu tek başına yeterli değildir; Artifact doğrulaması zorunludur.
* Tüm Provider değişimleri kanıt temelli ve izlenebilir şekilde kaydedilir.
* Hiçbir koşulda tek bir Provider için sonsuz bekleme yapılamaz.
* Provider'a özel implementasyonlar bu mimari standardı ihlal edemez.

---

## AR-002_90

### Production Gate Architecture — Video Üretim Öncesi Zorunlu Workflow Doğrulama Mimarisi

### Kural

HLK hiçbir koşulda Video Production sürecini yalnızca akış sırasına bakarak başlatamaz.

Video Production başlamadan önce HLK aşağıdaki Workflow'ların tamamlanma durumunu anayasal olarak doğrulamak zorundadır:

* **WF-001** Product Link Validation
* **WF-002** Background Research
* **WF-003** Brief Collection
* **WF-004** Brief Approval
* **WF-005** Scenario Generation
* **WF-006** Scenario Approval
* **WF-007** Pricing

HLK bu Workflow'ların tamamının `COMPLETED` durumunda olduğunu doğrulamadan;

* Video Production başlatamaz.
* Provider seçemez.
* Provider çağrısı yapamaz.
* Production Runtime başlatamaz.
* Video Render işlemini başlatamaz.
* Telegram üzerinden "Video Üretimi Başladı" bildirimi gönderemez.
* Telegram üzerinden "Üretim Tamamlandı" bildirimi gönderemez.

---

### Production Gate

Production Gate, HLK'nın Video Production sürecine geçiş izni veren **anayasal doğrulama kapısıdır.**

Production Gate yalnızca aşağıdaki koşulların **tamamı** sağlandığında açılır:

```
WF-001 == COMPLETED
AND
WF-002 == COMPLETED
AND
WF-003 == COMPLETED
AND
WF-004 == COMPLETED
AND
WF-005 == COMPLETED
AND
WF-006 == COMPLETED
AND
WF-007 == COMPLETED
```

Bu koşullardan herhangi biri sağlanmazsa Production Gate **kapalı kalır.** HLK üretimi durdurur ve Recovery sürecine girer.

---

### Recovery Zorunluluğu

Workflow'lardan herhangi biri `COMPLETED` durumunda değilse HLK üretime geçmeyecektir.

Bunun yerine HLK anayasal karar mekanizmasını kullanarak otomatik olarak:

1. **Eksik Workflow'u tespit eder.**
2. **Tamamlanmama nedenini analiz eder.**
3. **Event kayıtlarını inceler.**
4. **Task durumunu inceler.**
5. **Execution durumunu inceler.**
6. **Gerekli Recovery mekanizmasını uygular.**
7. **İlgili Workflow'u yeniden çalıştırmayı dener.**
8. **Workflow durumunu tekrar doğrular.**

Bu döngü başarıyla tamamlanmadan Production Gate açılamaz.

Recovery döngüsü maksimum **3 kez** tekrarlanabilir. 3 başarısız Recovery denemesinden sonra HLK;

* Production Gate'i **kalıcı olarak kapatır.**
* Durumu **FAILED** olarak işaretler.
* Proje Yöneticisine **eskalasyon bildirimi** gönderir.
* İlgili PID'i **arızalı** (faulted) olarak kaydeder.

---

### Single Source of Truth

Workflow `COMPLETED` durumu aşağıdaki bileşenler arasında **tek bir doğrulanmış durumdan** okunacaktır:

* **Workflow Explorer** — Explainable Workflow ağacı
* **Production State** — State Engine kaydı
* **Event System** — Olay Kayıt Merkezi kaydı
* **Telegram Bildirimleri** — Kullanıcıya gönderilen durum mesajları
* **OPS Dashboard** — Yönetici operasyon ekranı

Hiçbir bileşen kendi başına `COMPLETED` varsayımı yapamaz.

`COMPLETED` durumunun tek yetkili kaynağı **Workflow Manifest + Production Package + Decision History** üçlüsünün tutarlı kesişimidir.

---

### Production Gate Yaşam Döngüsü

```
WF-001..WF-007 Durum Kontrolü
  ↓
Tümü COMPLETED?
  ├─ EVET → Production Gate AÇIK → Video Production başlatılır
  └─ HAYIR → Production Gate KAPALI
                ↓
              Eksik Workflow Tespiti
                ↓
              Neden Analizi (Event + Task + Execution)
                ↓
              Recovery Mekanizması
                ↓
              Workflow Yeniden Çalıştırma
                ↓
              Doğrulama
                ├─ COMPLETED → Production Gate AÇIK
                └─ FAILED → Recovery döngüsü (max 3)
                              └─ 3 deneme sonrası → Eskalasyon
```

---

### Yasaklar

Aşağıdaki durumlar Production Gate mimarisi kapsamında **kesinlikle yasaktır:**

* Eksik Workflow'ları görmezden gelerek üretime geçmek
* `COMPLETED` varsayımıyla hareket etmek
* Workflow durumunu Telegram bildirimi veya OPS Dashboard üzerinden tahmin etmek
* Recovery uygulamadan manuel müdahale ile Production Gate'i açmak
* Production Gate kontrolünü atlayarak doğrudan Provider çağrısı yapmak
* Başarısız Workflow'ları atlayarak sonraki aşamaya geçmek

---

### Amaç

Bu mimarinin amacı;

* Video Production sürecinin yalnızca tüm zorunlu Workflow'lar `COMPLETED` olduğunda başlamasını anayasal olarak garanti etmek,
* Eksik veya başarısız Workflow'ların görmezden gelinmesini mimari seviyede engellemek,
* Production Gate mekanizması ile Video Production'a geçişi anayasal denetime bağlamak,
* Eksik Workflow tespitinde otomatik Recovery sürecini zorunlu kılmak,
* Workflow, Event, State, OPS Dashboard ve Telegram'ın aynı yaşam döngüsünü yansıtmasını sağlamak,
* `COMPLETED` durumunun tek bir doğrulanmış kaynaktan okunmasını mimari olarak zorunlu kılmak,
* HLK'nın eksik veya başarısız Workflow'ları görmezden gelmesini anayasal olarak imkansız hale getirmektir.

---

### Beklenen Sonuç

* Workflow tamamlanmadan Production başlamaz.
* Production başlamadan önce HLK eksik Workflow'ları otomatik olarak tamamlamaya çalışır.
* Recovery tamamlanmadan Production Gate açılmaz.
* Telegram yalnızca gerçek Production Event'lerinden sonra bildirim gönderir.
* Workflow, Event, State, OPS Dashboard ve Telegram aynı yaşam döngüsünü yansıtır.
* HLK, eksik veya başarısız Workflow'ları görmezden gelmez; anayasal olarak analiz eder, gerekirse tekrar çalıştırır ve yalnızca tüm zorunlu Workflow'lar doğrulandığında video üretimine izin verir.

---

## AR-002_91

### Başlık

Task Self-Healing Architecture (Task Kendi Kendini İyileştirme Mimarisi)

### Amaç

HLK sisteminde hiçbir Task; eksik bağımlılık, geçici hata, henüz oluşmamış kaynak veya gecikmeli çalışan sistem bileşenleri nedeniyle hemen sonlanamaz.

Recovery Policy başlamadan önce, Task kendi görevini anayasal sınırlar içerisinde kendi kendine tamamlamaya çalışmalıdır.

Bu mimari; AR-002_82 Mission Persistence ile AR-002_83 Recovery Policy arasındaki eksik anayasal katmandır.

### Kapsam

Bu madde; tüm Runtime Task'ları, tüm Workflow Task'ları, tüm Agent Task'ları, tüm Provider Task'ları, tüm Production Task'ları, START_AS_NEW, REPLAY, Retry, Restart ve Recovery süreçleri için zorunludur.

### Constitutional Principle

Task'ın görevi yalnızca `execute()` edilmek değildir. Task'ın görevi; kendisine verilen anayasal görevi SUCCESS durumuna ulaştırmaktır.

İlk başarısızlık, Task'ın sonlanması için yeterli gerekçe değildir.

### Self-Healing Workflow

Bir Task aşağıdaki anayasal sırayı uygulamak zorundadır:

1. **Mevcut kaynak kullanılabiliyorsa kullan.**
2. **Eksik Resource varsa yeniden oluştur.**
3. **Eksik Task Package varsa yeniden üret.**
4. **Eksik Workflow Package varsa yeniden oluştur.**
5. **Eksik Event oluşmasını bekle.** Gerekliyse yeniden üret.
6. **Eksik Digital Asset oluşmasını bekle.** Gerekliyse yeniden oluştur.
7. **Eksik Provider sonucu varsa anayasal polling mekanizmasını uygula.**
8. **Self-Healing başarısız olursa Recovery Policy'ye geç.**
9. **Recovery Policy başarısız olursa HLK Runtime yeniden anayasal karar üretir.**
10. **Tüm anayasal yollar tüketildikten sonra FAILED kararı verilebilir.**

### Controlled Waiting Policy

Task; geçici (Transient) olduğu değerlendirilen durumlarda hemen FAILED olamaz.

Geçici durumlar en az aşağıdakileri kapsar:

* Provider cevap bekleniyor
* Provider polling devam ediyor
* Task Package oluşturuluyor
* Workflow Package oluşturuluyor
* Production Package hazırlanıyor
* Event henüz oluşmadı
* Digital Asset oluşturuluyor
* Artifact doğrulaması tamamlanmadı
* Dosya yazılıyor
* Queue işleniyor

### Waiting Policy Rules

* Bekleme süreleri sabit kod olarak yazılamaz.
* Bekleme süreleri yalnızca Global Configuration üzerinden okunacaktır.
* Her bekleme nedeni Decision History ve Execution Event Collector içerisine kayıt edilmek zorundadır.
* Her yeniden deneme Decision History'ye gerekçesiyle yazılacaktır.

### Yasaklar

Task aşağıdaki nedenlerle sonlanamaz:

* `None`
* `[]`
* boş Task Package
* eksik Resource
* eksik Event
* eksik Artifact
* ilk Exception
* ilk Timeout
* ilk Provider Hatası
* geçici servis hatası
* ilk Queue hatası
* ilk dosya oluşturma hatası

### Constitution Enforcement

Constitution Enforcement Engine; Task'ın Self-Healing uygulanmadan, Recovery uygulanmadan ve anayasal yollar tüketilmeden FAILED olduğunu tespit ederse:

* Constitution Violation oluşturacaktır.
* Violation Event oluşturacaktır.
* Decision History'ye kaydedecektir.
* HLK Runtime yöneticiye rapor verecektir.

### Runtime Requirement

Aşağıdaki süreçler aynı anayasal Self-Healing davranışını kullanacaktır:

* START_AS_NEW
* REPLAY
* Retry
* Recovery
* Restart
* Crash Recovery
* Scheduled Restart

Hiçbiri kendi özel Self-Healing mekanizmasını oluşturamaz. Tek anayasal Self-Healing Architecture kullanılacaktır.

### Tekilleştirme İlkesi

Kod tekrarına izin verilmez:

* Tek Waiting Policy
* Tek Retry Policy
* Tek Recovery Policy
* Tek Self-Healing Policy
* Tek Runtime Decision mekanizması

### Global Configuration

Aşağıdaki GC parametreleri bu mimariyi desteklemek üzere tanımlanmıştır:

| Parametre | Açıklama |
|---|---|
| `GC_TASK_SELF_HEAL_MAX_COUNT` | Self-Healing maksimum deneme sayısı |
| `GC_TASK_SELF_HEAL_DELAY` | Self-Healing adımları arası bekleme (saniye) |
| `GC_PACKAGE_REBUILD_MAX_COUNT` | Package yeniden oluşturma maksimum deneme |
| `GC_PACKAGE_REBUILD_DELAY` | Package rebuild denemeleri arası bekleme (saniye) |
| `GC_RESOURCE_RECOVERY_DELAY` | Resource kurtarma bekleme süresi (saniye) |
| `GC_EVENT_RECOVERY_DELAY` | Event oluşmasını bekleme süresi (saniye) |
| `GC_EVENT_RECOVERY_MAX_COUNT` | Event bekleme maksimum deneme sayısı |
| `GC_FILE_RECOVERY_DELAY` | Dosya oluşmasını bekleme süresi (saniye) |
| `GC_FILE_RECOVERY_MAX_COUNT` | Dosya bekleme maksimum deneme sayısı |
| `GC_ARTIFACT_RECOVERY_DELAY` | Artifact doğrulama bekleme süresi (saniye) |
| `GC_ARTIFACT_RECOVERY_MAX_COUNT` | Artifact bekleme maksimum deneme sayısı |

Bu parametreler mevcut `GC_EXECUTOR_MAX_RETRY`, `GC_EXECUTOR_RETRY_DELAY`, `GC_MAX_RE_EVALUATION_COUNT`, `GC_PROVIDER_POLL_COUNT`, `GC_IMAGE_POLL_INTERVAL`, `GC_VIDEO_POLL_INTERVAL` ile uyumlu çalışır. Hiçbir mevcut GC parametresi değiştirilmez veya devre dışı bırakılmaz.

### Anayasal Dayanak

| Katman | Referans | Açıklama |
|---|---|---|
| **MASTER** | MASTER-001 | ANA YASA üstünlüğü |
| **MASTER** | MASTER-003 | PipelineContext anayasal gerçeği yansıtır |
| **MASTER** | MASTER-004 | Self-Healing karar vermez; HLK Runtime karar verir |
| **MASTER** | MASTER-011 | Runtime aktiflik doğrulaması |
| **MASTER** | MASTER-013 | Self-Healing başarısız → HLK Runtime kararı |
| **AR** | AR-002_22 | Feedback Loop — Self-Healing sonrası yeniden değerlendirme |
| **AR** | AR-002_57 | PID Standardı — Self-Healing kayıtlarında PID zorunlu |
| **AR** | AR-002_60 | CEE — Self-Healing atlanırsa violation |
| **AR** | AR-002_70 | Production Runtime — Self-Healing Gateway |
| **AR** | AR-002_76 | Production Execution — Self-Healing entegrasyonu |
| **AR** | AR-002_79 | Üretim Sürekliliği — Self-Healing → Recovery zinciri |
| **AR** | AR-002_81 | Karar Talep Protokolü — SELF_HEALING karar kategorisi |
| **AR** | AR-002_82 | Mission Persistence — Self-Healing'in üst katmanı |
| **AR** | AR-002_83 | Recovery Policy — Self-Healing başarısız olursa geçiş |
| **AR** | AR-002_84 | Yönetici Yeniden Üretim — START_AS_NEW Self-Healing |
| **AR** | AR-002_86 | Anayasal Yürütme — Self-Healing uygulanmaması ihlal |
| **AR** | AR-002_87 | External Resource Recovery — Provider Self-Healing referansı |
| **AR** | AR-002_90 | Production Gate — Pre-production Self-Healing |

### Beklenen Sonuç

* Hiçbir Task eksik bağımlılık nedeniyle hemen FAILED olmaz.
* Task'lar kendi Package, Resource, Event ve Artifact'lerini onarabilir.
* Self-Healing başarısız olursa Recovery Policy otomatik devreye girer.
* START_AS_NEW ve REPLAY prosedürleri boş task_packages ile karşılaşmaz.
* Tüm bekleme süreleri GC parametrelerinden okunur, hard-coded değer kalmaz.
* Tek Waiting Policy, tek Retry Policy, tek Recovery Policy kullanılır.
* CEE, Self-Healing atlanarak FAILED olan task'ları violation olarak kaydeder.
* Tüm Self-Healing adımları Decision History ve Event Log'a kaydedilir.
