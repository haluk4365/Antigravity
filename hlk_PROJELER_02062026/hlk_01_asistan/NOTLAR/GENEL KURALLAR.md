# HLK AI REKLAM ASISTANI — GENEL KURALLAR

## PROJE BİLGİLERİ
- Proje adı: HLK AI Reklam Asistanı
- Ana dosya: main.py
- Venv: C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk_PROJELER_02062026\HLK-AI-Reklam-Asistani\venv\
- Test botu: @hlk01_test_bot
- Canlı bot: @hlk_reklam_asistani01_bot
- Railway proje: skillful-achievement
- GitHub: haluk4365/HLK-AI-Reklam-Asistani
- Proje klasörü: C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk_PROJELER_02062026\HLK-AI-Reklam-Asistani

## KOMUT PROTOKOLÜ

### "testi başlat" geldiğinde:
⚠️ KRİTİK: Python'ı SADECE bat dosyası başlatır. Claude Code doğrudan python başlatmaz.
   testi_baslat.bat kendi içinde: cd, taskkill, TEST_MODE=true, venv aktifleştirme, python başlatma — hepsini yapar.
1. Çalışan tüm python proseslerini durdur
2. Bat dosyasını çalıştır:
   ⚠️ KRİTİK: Klasör adındaki parantez `(DOLUNAY)` yüzünden parantezli tam yolla
   `Start-Process` GÜVENİLMEZ (cmd yolu "Antigravity"de keser, bat hiç çalışmaz, python başlamaz).
   Bunun yerine 8.3 KISA YOL ile başlat (parantezsiz, kanıtlanmış çalışıyor):
   Start-Process -FilePath "cmd.exe" -ArgumentList "/c","C:\Users\msist\OneDrive\Desktop\ANTIGR~1\HLK_PR~1\HLK-AI~1\TESTI_~1.BAT"
   (Not: kullanıcı bat'a çift tıklayınca da sorunsuz çalışır — sorun yalnızca programatik Start-Process'tedir.)
3. 5 saniye bekle, bot_err.log son satırlarını kontrol et
4. "Application started" görünüyorsa ekrana yaz:

======================
TEST KONUMU BAŞLATILDI
Testten çıkmak için "TESTİ BİTİR" komutu veriniz
======================

### "testi bitir" geldiğinde:
1. HLK python prosesini durdur
2. Ekrana yaz:

======================
TEST DURDURULDU
Railway (canlı) devreye girdi
Canlıya geçmek için "CANLIYA GEÇ" komutu veriniz
======================

### "canlıya geç" geldiğinde:
1. git add .
2. git commit -m "deploy: [otomatik tarih]"
3. git push origin main
4. Ekrana yaz:

======================
CANLIYA GEÇİLİYOR...
GitHub push tamamlandı
Railway otomatik deploy başladı
Railway loglarını kontrol edin
======================

## GENEL TEST MOD KURAL_0 — KALICI
**Açıklama:** "testi başlat" komutu verildiğinde TEST_MODE ve BOT_MODE ortam değişkenleri sistem ya da oturum değişkeni olmadan otomatik oluşturulur. Bilgisayar her yeniden başlatıldığında bu değişkenler kayboluyordu; çözüm olarak testi_baslat.bat dosyasının içine `set TEST_MODE=true` ve `set BOT_MODE=test` komutları eklendi. Böylece bat her çalıştığında bu değişkenler o an, o bat penceresine özgü olarak tanımlanır. Claude Code python'ı doğrudan başlatmaz — sadece bat dosyasını tetikler; bat kendi içinde cd, taskkill, env set, venv aktivasyonu ve python başlatma işlemlerini sırasıyla yürütür.
- Sistem değişkenine, oturum değişkenine, Claude Code'un $env: atamasına BAĞIMLI DEĞİLDİR
- Claude Code python'ı doğrudan başlatmaz — sadece testi_baslat.bat'ı açar
- Bat her şeyi kendi içinde taşır: cd → taskkill → set env → venv → python

## GENEL_KURAL_1 — Oturum Zaman Aşımı (Tüm Oturum Boyunca Geçerli)

### Tanım
Sıra kullanıcıya geçtiği her anda (yazma beklentisi, buton beklentisi, şık seçimi, link gönderme vb.) bu kural otomatik olarak devreye girer.

### Akış
- Sıra kullanıcıya geçince 5 dakika sayacı başlar
- Kullanıcının gerçekleştirdiği her **geçerli etkileşim** (mesaj yazması, herhangi bir buton seçmesi, fotoğraf yüklemesi, video yüklemesi, katalog veya başka bir materyal yüklemesi, sistem tarafından kabul edilen herhangi bir kullanıcı girdisi) kullanıcının aktif olduğunu gösterir
- Bu durumda çalışmakta olan bekleme zamanlayıcısı iptal edilir ve kullanıcı sırası yeniden başlamış kabul edilerek bekleme zamanlayıcısı sıfırdan yeniden başlatılır
- Bu işlem, oturum boyunca kullanıcı tarafına sıra geçtiği sürece her geçerli kullanıcı etkileşiminde tekrar edilir
- **Temel ilke: Kullanıcının her geçerli etkileşimi, bekleme zamanlayıcısını sıfırlar ve kullanıcı sırası için zaman sayımı yeniden başlatılır.**
- 5 dakika dolup herhangi bir geçerli etkileşim gelmezse kullanıcıya şu mesaj gönderilir:
  "HLK asistanı ile açık bir Telegram oturumunuz kaldı, 2 dakika içinde bu oturum kapatılacaktır."
- 2 dakika daha beklenir
- Bu süre içinde geçerli bir etkileşim gelirse zamanlayıcı sıfırlanır, oturum devam eder
- Gelmezse kullanıcıya şu mesaj gönderilir:
  "HLK ile açık olan Telegram oturumunuz kapatılmıştır."
- Oturum sonlanır

## GENEL_KURAL_2 — Genel Kural Silme Koruması (Tüm Oturum Boyunca Geçerli)

### Tanım
Bu projede tanımlı tüm Genel Kurallar korumalıdır. Hiçbir Genel Kural onaysız silinemez.

### Akış
- Claude Code herhangi bir "GENEL_KURAL_n" satırını veya bloğunu silmeden önce duraklar
- Kullanıcıya şunu sorar: "Emin misin? **GENEL_KURAL_n** silinecek."
- Kullanıcı "evet" / "onayla" / "sil" ile onaylamadan işlem yapılmaz
- Onay gelmezse kural korunur, hiçbir değişiklik uygulanmaz

### Kural deposu
Bu projedeki tüm Genel Kurallar yalnızca şu dosyada saklanır:
`C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk_PROJELER_02062026\HLK-AI-Reklam-Asistani\ANA KURALLAR\GENEL KURALLAR.md`
Başka bir dosyaya taşınamaz, parçalanamaz, yorum satırına alınamaz.

## KRİTİK NOTLAR
- venv her zaman C:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)\hlk_PROJELER_02062026\HLK-AI-Reklam-Asistani\venv\ altındadır
- .env dosyası projede mevcut
- Her sabah ilk açılışta bu dosyayı oku, özet ver, komut bekle
- Komutlar Türkçe gelecek, Türkçe yanıt ver
