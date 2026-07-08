# 02 — General Rules

Genel kurallar.

---

## GK-001_1

HLK'nın analiz sürecini başlatabilmesi için kullanıcının ilk zorunlu girdisi, analiz edilebilir ve erişilebilir bir ürün linkidir. Ürün adı, ürün açıklaması veya tek başına görsel analiz sürecini başlatmak için yeterli kabul edilmez.

---

## GK-001_2

HLK, kullanıcının gönderdiği ürün linki doğrulanmadan hiçbir araştırma, analiz, görev dağıtımı veya alt süreç başlatmaz. Link doğrulaması, tüm sonraki işlemler için zorunlu başlangıç koşuludur.

---

## GK-001_3

HLK, ürün linki doğrulanamadığında araştırma sürecini devam ettirmeye çalışmaz. Kullanıcıyı standart sistem mesajı ile bilgilendirir ve yalnızca geçerli yeni bir ürün linki bekleme durumuna geçer. Bu aşamada başka hiçbir analiz başlatılmaz.

---

## GK-001_4

HLK, geçersiz ürün linki durumunda kullanıcıya sınırsız deneme hakkı tanımaz. Her başarısız doğrulamadan sonra sistem kalan deneme hakkını günceller ve kullanıcıyı bu bilgi ile bilgilendirir. Maksimum deneme hakkı sistem konfigürasyonunda tanımlanır.

---

## GK-001_5

HLK, kullanıcıya gönderilecek sistem mesajlarını önceden tanımlanmış sabit metinler olarak değil, sistem tarafından belirlenmiş iletişim kurallarına uygun şekilde dinamik olarak üretir. Üretilen mesaj; doğru, kısa, anlaşılır, mevcut durumu yansıtan ve kullanıcıyı bir sonraki adıma yönlendiren nitelikte olmalıdır.

---

## GK-001_6

HLK, kullanıcı tarafından gönderilen her yeni ürün linkini önceki başarısız denemelerden bağımsız ve önyargısız olarak yeniden değerlendirir. Önceki başarısız doğrulamalar yeni linkin analizini etkilemez; yalnızca sistem tarafından takip edilen deneme sayacı korunur.

---

## GK-001_7

HLK, kullanıcıdan gelen ürün linkini yalnızca doğrulanacak bir adres olarak değil, sonraki tüm araştırma ve analiz süreçlerinin temel veri kaynağı olarak kabul eder. Bu nedenle link doğrulama aşaması, reklam üretim sürecinin ayrılmaz bir parçasıdır ve atlanamaz.

---

## GK-001_8

HLK, ürün linki başarıyla doğrulandığında bu aşamayı tamamlanmış kabul eder ve bir sonraki iş akışına geçer.

---

## GK-001_9

HLK, bir ürün linkini yalnızca erişilebilir olduğu için doğrulanmış kabul etmez.

Link doğrulama sürecinde HLK, kendi karar mekanizmasını kullanarak linkin;

* analiz edilebilir olup olmadığını,
* gerçek bir ürün sayfasına ait olup olmadığını,
* reklam üretim sürecinde kullanılabilecek yeterli ürün bilgisi içerip içermediğini,
* teknik olarak işlenebilir durumda olup olmadığını

değerlendirir.

HLK yalnızca reklam üretim sürecini başlatabilecek yeterli ve güvenilir ürün bilgisinin elde edilebildiğini tespit ettiğinde link doğrulama aşamasını başarılı kabul eder.

---

## GK-001_10

HLK, bir ürün linkinin doğrulama sonucunu sezgisel olarak belirlemez.

Link doğrulama sürecinde HLK, kendi karar mekanizmasını kullanarak en az aşağıdaki doğrulama kriterlerini değerlendirir:

* Link erişilebilir durumda mı?
* Sayfa teknik olarak açılabiliyor mu?
* Sayfa gerçek bir ürün sayfası mı?
* Ürün adı tespit edilebiliyor mu?
* Ürün hakkında açıklama, özellik veya anlamlı ürün bilgisi bulunuyor mu?
* Ürüne ait en az bir görsel veya görsel referans mevcut mu?
* Ürünü tanımlamaya yetecek asgari ürün bilgileri elde edilebiliyor mu?
* Sayfa hata, yönlendirme döngüsü veya erişim engeli içermiyor mu?

HLK, bu kriterlerin sonucunu kendi karar mekanizması ile değerlendirir.

HLK yalnızca ürünü güvenilir şekilde tanımlayabilecek yeterli bilginin elde edildiğini tespit ettiğinde link doğrulama aşamasını başarılı kabul eder.

Aksi durumda link doğrulama başarısız kabul edilir ve sonraki iş akışlarına geçilmez.

---

## GK-001_11

HLK, link doğrulama sürecinde oluşturulan güven puanını karar gerekçelerinden biri olarak değerlendirir.

Link doğrulama görevinde elde edilen nihai güven puanı 30 veya üzerinde ise bu durum link doğrulama lehine bir gerekçe olarak kabul edilir.

Nihai güven puanının 30'un altında olması durumunda bu durum link doğrulama aleyhine bir gerekçe olarak kabul edilir.

Minimum güven eşiğinin aşılması tek başına link doğrulama kararı oluşturmaz.

HLK, nihai kararı diğer doğrulama gerekçeleri ile birlikte değerlendirerek verir.

Bu nedenle güven puanı, karar mekanizmasının kullandığı gerekçelerden yalnızca biridir ve tek başına yeterli değildir.

---

## GK-001_12

HLK projesi içerisinde oluşturulan tüm dokümantasyon, kayıt dosyaları, manifest dosyaları ve registry dosyalarında kullanıcıya veya geliştiriciye gösterilen alan adları öncelikli olarak Türkçe kullanılmalıdır.

Uluslararası standartlar, API uyumluluğu, programlama dili gereksinimleri veya teknik zorunluluk nedeniyle İngilizce isim kullanılması gereken durumlarda, ilgili alanın Türkçe karşılığı da aynı kayıt içerisinde belirtilmelidir.

Kod içerisinde kullanılan teknik isimler, değişken adları, sınıf adları, fonksiyon adları ve API alanları bu kuralın kapsamı dışındadır.

Bu kuralın amacı; HLK dokümantasyonunun okunabilirliğini artırmak, proje bütünlüğünü korumak ve teknik gereksinimlerle kullanıcı dostu dokümantasyonu birlikte sürdürebilmektir.
