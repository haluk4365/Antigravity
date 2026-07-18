# RAPOR — Anayasal Karar Zinciri Çelişki Analizi: "Çıktılar teslim edildi"

**Tarih:** 18.07.2026
**PID:** PID-20260718-0001
**Amaç:** Kod değiştirmeden, yalnızca gerçek kod akışını takip ederek "Çıktılar teslim edildi" kararının hangi veriye dayandığını tespit etmek.

---

## 1. `context["video_available"]` Nerede Oluşturuluyor?

**Dosya:** `services/production_pipeline.py`
**Fonksiyon:** `task_delivery`
**Satır:** 601

```python
video_available = bool(ctx.video_path and os.path.exists(ctx.video_path))
```

Bu değer iki şarta bağlıdır:
1. `ctx.video_path` değişkeni `None` olmamalı (bir string değer içermeli)
2. `os.path.exists(ctx.video_path)` → o yolda fiziksel dosya mevcut olmalı

---

## 2. `video_available` Hangi Koşulda TRUE Oluyor?

```python
# production_pipeline.py:460
if ctx.voice_path and ctx.img_path:
    # ... video provider'ları dene ...
    # başarılı olursa:
    ctx.video_path = video_path   # ← satır 480 veya 517

# production_pipeline.py:601  
video_available = bool(ctx.video_path and os.path.exists(ctx.video_path))
```

TRUE olması için zincir:
1. `ctx.img_path` dolu olmalı (görsel üretilmiş)
2. `ctx.voice_path` dolu olmalı (ses üretilmiş)
3. Video provider'ı başarılı olmalı → `ctx.video_path` atanmalı
4. `os.path.exists(ctx.video_path)` → dosya fiziksel olarak diskte mevcut olmalı

---

## 3. TRUE Olması İçin Ne Kontrol Ediliyor?

Adım adım:

| Sıra | Kontrol | Tür |
|---|---|---|
| 1 | `ctx.video_path` truthy mi? (`None` değil, boş string değil) | **PipelineContext değişkeni** |
| 2 | `os.path.exists(ctx.video_path)` → dosya diskte var mı? | **Fiziksel dosya kontrolü** |

Yani: **Fiziksel video dosyasının varlığı doğrulanıyor.** Ama bu doğrulama yalnızca `task_delivery` içinde, HLK Runtime'a gönderilmeden önce yapılıyor. HLK Runtime bu doğrulamayı **tekrarlamıyor** — yalnızca gelen `video_available` boolean'ına güveniyor.

---

## 4. `send_video()` Çağrısından ÖNCE mi SONRA mı TRUE Oluyor?

Gerçek çağrı sırası (`production_pipeline.py`):

```
SATIR 601:  video_available = bool(ctx.video_path and os.path.exists(ctx.video_path))
            ↓
SATIR 604:  delivery_decision = hlk_runtime.request_decision(DELIVERY, 
              context={"video_available": video_available, ...})
            ↓  [HLK Runtime karar verir: DELIVER_VIDEO veya DELIVER_INFO]
            ↓
SATIR 617:  if delivery_decision.verdict == "DELIVER_VIDEO":
SATIR 618:      with open(ctx.video_path, "rb") as vf:         ← dosya tekrar açılır
SATIR 619:          await req.bot.send_video(chat_id, video=vf, ...)  ← Telegram API
```

`video_available` değeri **`send_video()` çağrısından ÖNCE** hesaplanır (satır 601, satır 619'dan önce).

---

## 5. `send_video()` Başarısız Olursa HLK Runtime Öğreniyor mu?

**Öğrenmiyor.**

`send_video()` çağrısı satır 619'da `await` ile yapılır. Eğer Telegram API hata dönerse (örneğin chat bulunamadı, file too large, vs.):

1. `task_delivery` fonksiyonu exception fırlatır
2. Exception, `_execute_task`'a (executor) yükselir
3. Executor exception'ı yakalar, task FAILED işaretler
4. **HLK Runtime bu bilgiyi ALMAZ** — exception doğrudan executor seviyesinde yakalanır

Ama bu PID-20260718-0001 senaryosuyla **ilgili değil** — çünkü `video_available=False` olduğu için `send_video()` hiç çağrılmadı. Kod `DELIVER_INFO` yoluna girdi ve `send_message()` ile metin gönderdi.

---

## 6. HLK Runtime "Çıktılar teslim edildi" Kararını Vermeden Önce Video Dosyasının Varlığını Doğruluyor mu?

**Doğrulama yapılmıyor.**

"Çıktılar teslim edildi" metni şu zincirle üretilir:

### Zincir A — DELIVERY kararı:

```
production_pipeline.py:604
  hlk_runtime.request_decision(DELIVERY, context={"video_available": False, ...})
    ↓
hlk_runtime.py:817
  video_available = bool(ctx.get("video_available", False))    ← False
    ↓
hlk_runtime.py:832-847
  video_available False → DELIVER_INFO kararı
  text = "🎬 Uretim Tamamlandi! ... Videonuz hazirlaniyor..."
  ← Bu metinde "teslim edildi" İFADESİ YOK
```

### Zincir B — COMPLETION kararı:

```
production_runtime.py:1181
  hlk_runtime.request_decision(COMPLETION, 
    context={"delivered": ctx.delivered, "video": bool(ctx.video_path), ...})
    ↓
hlk_runtime.py:853-854
  delivered = bool(ctx.get("delivered", False))    ← ctx.delivered değeri
  video = bool(ctx.get("video", False))            ← bool(ctx.video_path)
    ↓
hlk_runtime.py:861
  if failed_tasks == 0 and delivered:              ← delivered kontrolü
    → CONFIRM_COMPLETION
  else:
    → CONFIRM_COMPLETION (zaten her durumda success=True dönüyor!)
```

**Kritik bulgu:** `_decide_completion` her durumda `success=True` ile `CONFIRM_COMPLETION` dönüyor (satır 869). `delivered=False` veya `video=False` olsa bile karar değişmiyor.

### Zincir C — USER_NOTIFICATION (asıl "teslim edildi" mesajı):

```
production_runtime.py:1196-1198
  await self._notify_reproduction_result(
      pid, bot, admin_chat_id, int(user_chat_id),
      success=True, ...                             ← HARDCODED True!
  )
    ↓
production_runtime.py:1329
  kind = "reproduction_completed" if success else "reproduction_failed"
  kind = "reproduction_completed"                   ← success=True olduğu için
    ↓
production_runtime.py:1334
  hlk_runtime.request_decision(USER_NOTIFICATION,
    context={"kind": "reproduction_completed", "audience": audience, ...})
    ↓
hlk_runtime.py:1017-1037
  if kind == "reproduction_completed":
      if audience == "user":
          text = "✅ Uretiminiz tamamlandi! ... cikti tarafiniza teslim edildi."
      else:
          text = "✅ ... Ciktilar ilgili kullaniciya teslim edildi ..."
```

---

## SONUÇ

**HLK Runtime "Çıktılar teslim edildi" kararını hangi somut veriye dayanarak verdi?**

Cevap: **E) Başka bir veri**

HLK Runtime bu kararı **hiçbir veriye dayanarak vermedi.** Kararın dayanağı, `_notify_reproduction_result` fonksiyonuna **hardcoded** olarak geçilen `success=True` parametresidir (satır 1198).

Kanıt zinciri:

| Adım | Dosya:Satır | Ne Oldu | Gerçek Veri |
|---|---|---|---|
| 1 | `pipeline.py:601` | `video_available = bool(None and ...)` | **False** |
| 2 | `pipeline.py:617` | `DELIVER_INFO` → metin gönderildi | Video gönderilmedi |
| 3 | `pipeline.py:636-637` | `ctx.delivered = True` (eski kod — düzeltildi) | **False** olmalıydı |
| 4 | `runtime.py:1198` | `success=True` **hardcoded** | Gerçek success durumu kontrol edilmedi |
| 5 | `runtime.py:1329` | `kind = "reproduction_completed"` | `success=True`'ten türedi |
| 6 | `hlk_runtime.py:1029-1033` | `"Ciktilar ilgili kullaniciya teslim edildi"` metni | **Hiçbir doğrulama yok** |

HLK Runtime `_decide_user_notification` fonksiyonu, `kind="reproduction_completed"` aldığında **hiçbir ek doğrulama yapmadan** "teslim edildi" metnini üretiyor. `video_available`, `ctx.video_path`, `ctx.delivered` gibi değerlerin hiçbiri bu karar aşamasında kontrol edilmiyor.

**"Çıktılar teslim edildi" ifadesinin tek dayanağı: `_run_reproduction` içindeki `success=True` hardcoded değeridir (satır 1198). Bu değer gerçek video varlığına, Telegram teslimat başarısına veya başka herhangi bir doğrulanmış veriye dayanmamaktadır.**
