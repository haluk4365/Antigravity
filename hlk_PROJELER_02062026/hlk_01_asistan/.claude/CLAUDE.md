# HLK_01 PROJESİ BAŞLANGIÇ TALİMATI

HLK_01 projesine her giriş yaptığında veya yeni bir oturum başlattığında, hiçbir geliştirme, analiz, öneri, yorum veya kod üretimine başlamadan önce aşağıdaki adımları eksiksiz uygula.


## 0. REFERANS FORM SENKRONİZASYONU (Ön Koşul)

HLK projesinde **her "TEST BAŞLAT" komutu çalıştırılmadan önce** aşağıdaki işlemler zorunlu olarak uygulanacaktır.

1. **FORMLAR klasörünü tara.** `HLK_01_asistan/FORMLAR/` dizini içerisinde bulunan tüm `REFERANS_*.png` dosyalarını tespit et.

2. **Aynı isimde klasörü kontrol et.** Her Referans Form `.png` dosyası için **aynı `FORMLAR/` klasörü içerisinde** aynı isimde bir klasörün bulunup bulunmadığını kontrol et. (Örnek: `REFERANS_SENARYO_ONAY_FORMU.png` → `REFERANS_SENARYO_ONAY_FORMU/`)

3. **Eksik klasörü oluştur.** Aynı isimde klasör bulunmuyorsa, **aynı `FORMLAR/` klasörü içerisinde** otomatik olarak oluştur.

4. **Klasör içeriğini hazırla.** Oluşturulan klasörün içerisine aşağıdaki dosyalar yerleştirilir:
   - İlgili Referans `.png` dosyası (kaynak konumundan kopyalanır.)
   - `template.html`
   - `sample-data.json`
   - `render.js`

5. **Referans `.png` dosyasını esas al.** Referans `.png` dosyası, ilgili Referans Form klasörünün değiştirilemez tek görsel otoritesidir. `template.html`, `sample-data.json` ve `render.js` dosyaları bu Referans `.png` dosyası esas alınarak oluşturulur ve gerektiğinde güncellenir. Hiçbir durumda `template.html`, `sample-data.json` veya `render.js` dosyaları Referans `.png` dosyasının yerine geçemez veya onu değiştiremez.

6. **Mevcut klasörü koru.** Aynı isimde klasör mevcutsa, klasörün içeriği kontrol edilir. `template.html`, `sample-data.json` veya `render.js` dosyalarından biri eksikse **yalnızca eksik olan dosya** oluşturulur.

7. **Mevcut dosyalara dokunma.** Mevcut klasörler ve mevcut dosyalar **hiçbir durumda silinmez, yeniden oluşturulmaz veya üzerine yazılmaz.**

8. **Tamamlanmayı doğrula.** Tüm Referans Formlar kontrol edilip eksikler tamamlandıktan sonra normal "Testi Başlat" akışı devam eder.

Bu doğrulama ve senkronizasyon işlemi, HLK'nın her "TEST BAŞLAT" görevinden önce zorunlu olarak uygulanacaktır. Bu işlem tamamlanmadan HLK hiçbir geliştirme veya test sürecine başlamayacaktır.

---

## 1. MASTER-001 Analiz Zorunluluğu

Öncelikle MASTER-001 içerisinde tanımlanan **Analiz Zorunluluğu** kuralını uygula.

Aşağıdaki anayasal dosyaları karar hiyerarşisindeki sıraya göre oku ve öğren.

1. 00_HLK_MASTER_RULE_BOOK.md
2. 01_Global_Configuration.md
3. 02_General_Rules.md
4. 03_Architecture_Rules.md
5. 07_HLK_STATE_ENGINE.md
6. 08_HLK_FLOW_DIAGRAM.md
7. İlgili diğer .md dosyaları

Bu analiz tamamlanmadan hiçbir geliştirme yapılmayacaktır.

---

## 2. Flow Diagram Referansı

Analiz tamamlandıktan sonra, geliştirilecek veya incelenecek davranışın ait olduğu sahneyi (SAHNE-1 ... SAHNE-n) tespit et.

08_HLK_FLOW_DIAGRAM.md içerisinde yalnızca bu sahneye ait kullanıcı akışını yeniden oku.

Bu sahneye ait;

* ekran sırası,
* ekran temizleme işlemleri,
* konuşma balonları,
* daktilo efektleri,
* butonlar,
* kullanıcı etkileşimleri,
* state geçişleri,
* sahne geçişleri

geliştirme boyunca birincil referans olarak kullanılacaktır.

Flow Diagram ile çalışan kod arasında herhangi bir farklılık tespit edilirse, Flow Diagram esas alınacak ve kod buna göre değerlendirilecektir.

---

## 3. Geliştirme İlkesi

Hiçbir geliştirme;

* varsayıma,
* önceki oturum bilgilerine,
* ezbere,
* kişisel yoruma

dayandırılmayacaktır.

Tüm analizler ve geliştirmeler yalnızca güncel proje kaynakları esas alınarak yapılacaktır.

---

## 4. Zorunlu Bildirim

Yukarıdaki analiz tamamlandıktan sonra aşağıdaki ifadeyi yaz.

**✅ Tüm KAYNAKLAR okundu ve öğrenildi.**

Bu bildirim verilmeden geliştirme sürecine başlanmayacaktır.

---

# ÇALIŞMA DİSİPLİNİ

HLK projesi, anayasal mimari ile yönetilen bir sistemdir.

Hiçbir geliştirme, analiz, öneri, yorum, refaktör veya kod değişikliği doğrudan kod seviyesinden başlatılamaz.

Her geliştirme aşağıdaki anayasal çalışma disiplinini eksiksiz uygulamak zorundadır.

---

## 1. İlgili STATE'i Tespit Et

Öncelikle geliştirme yapılacak veya analiz edilecek ilgili STATE belirlenir.

Tüm sonraki işlemler bu STATE üzerinden yürütülür.

---

## 2. STATE'e Bağlı Anayasal Referansları Oku

İlgili STATE'e bağlı tüm anayasal referanslar eksiksiz okunur ve öğrenilir.

Bunlar arasında;

* HLK MASTER RULE BOOK
* Global Configuration
* General Rules
* Architecture Rules
* Operational Rules
* Quality Rules
* Module Rules
* State Engine
* Workflow
* Workflow Feature Map
* Flow Diagram
* Referans Formlar
* ilgili diğer anayasal kaynaklar

bulunabilir.

HLK, hangi referansların ilgili STATE için gerekli olduğunu kendisi tespit etmek zorundadır.

---

## 3. Anayasal Tutarlılığı Doğrula

HLK, ilgili STATE'e ait tüm anayasal referanslar arasında çelişki olup olmadığını kontrol eder.

Çelişki tespit edilirse;

* kod değiştirilmez,
* anayasal uyumluluk raporu hazırlanır,
* Proje Yöneticisine bildirilir.

---

## 4. Kod Analizine Başla

Yalnızca ilgili STATE'e ait anayasal analiz tamamlandıktan sonra;

* kod analizi,
* kod geliştirme,
* refaktör,
* hata düzeltme,
* test

başlatılabilir.

---

## 5. Geliştirme Sonrası Doğrulama

Kod tamamlandıktan sonra;

ilgili STATE'e bağlı tüm anayasal referanslarla yeniden karşılaştırılır.

Anayasal uyumsuzluk tespit edilirse geliştirme tamamlanmış kabul edilmez.

---

## Temel İlke

HLK içerisinde;

STATE

↓

Anayasal Referanslar

↓

Kod

↓

Runtime

↓

Telegram

geliştirme sırası zorunludur.

Bu sıra hiçbir geliştirme görevinde değiştirilemez veya atlanamaz.

Kod hiçbir zaman geliştirme sürecinin başlangıç noktası değildir.

Kod, anayasal analiz tamamlandıktan sonra geliştirilen son katmandır.

---

## Zorunlu Bildirim

Anayasal analiz tamamlandıktan sonra aşağıdaki bildirim verilmelidir.

**✅ Tüm KAYNAKLAR okundu ve öğrenildi.**

Bu bildirim verilmeden geliştirme sürecine başlanmayacaktır.
