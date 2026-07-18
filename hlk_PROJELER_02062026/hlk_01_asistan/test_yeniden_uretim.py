"""AR-002_84 Yonetici Yeniden Uretim Proseduru — Test Suite (ASCII-safe).

Test kapsami:
1. find_package — PID ve urun adi ile arama
2. load_full_production_context — anayasal kayitlarin toplanmasi
3. HLK Runtime REPRODUCTION kararlari (RETRY/RESUME/REPLAY/START_AS_NEW/REJECT)
4. prepare_for_reproduction — task/durum/revision_history hazirligi
5. Executor recovery — checkpoint'li yurutme (simulasyon modu)
6. run_reproduction — tam anayasal zincir (sahte pipeline handler'lari ile)
7. Istisna akisi — PID dogrulanamazsa guvenli sonlandirma

Not: Test artiklari (data/production_packages/*.json) test sonunda silinir
(bkz. proje kurali: test paketleri PID artigi birakmamali).
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from services.pid_runtime import pid_runtime
from services.production_package_runtime import package_runtime, PackageStatus
from services.hlk_runtime import hlk_runtime, DecisionRequest, DecisionCategory


class DummyBot:
    """Telegram Bot yerine gecen test nesnesi — mesajlari kaydeder."""

    def __init__(self):
        self.messages = []

    async def send_message(self, chat_id=None, text=None, parse_mode=None, **kw):
        self.messages.append({"chat_id": chat_id, "text": text or ""})

    async def send_video(self, chat_id=None, video=None, caption=None, **kw):
        self.messages.append({"chat_id": chat_id, "text": "[VIDEO]", "video": True})


ADMIN_USER = 999001
ADMIN_CHAT = 999001
USER_CHAT = 555001

_created_pids = []


async def _make_failed_package(product_name: str, brand: str) -> str:
    """FAILED durumda, karma task'li gercekci bir test paketi olusturur."""
    rec = await pid_runtime.generate()
    pid = rec.pid
    _created_pids.append(pid)
    await package_runtime.create(pid)
    await package_runtime.update_section(pid, "brief", {
        "url": "https://ornek.com/urun",
        "product_name": product_name,
        "brand": brand,
        "voice_language": "tr",
        "user_id": 555001,
        "chat_id": USER_CHAT,
    })
    await package_runtime.update_section(pid, "video_parameters", {
        "duration_seconds": 10,
        "voice_language": "tr",
    })
    await package_runtime.update_section(pid, "task_packages", [
        {"task_id": f"TASK-{pid}-001", "agent": "ImageGenerator",
         "status": "COMPLETED", "pid": pid, "completed_at": "2026-07-18T10:00:00"},
        {"task_id": f"TASK-{pid}-002", "agent": "VoiceGenerator",
         "status": "COMPLETED", "pid": pid, "completed_at": "2026-07-18T10:01:00"},
        {"task_id": f"TASK-{pid}-003", "agent": "VideoRenderer",
         "status": "FAILED", "pid": pid,
         "error_detail": "Provider timeout (test senaryosu)"},
        {"task_id": f"TASK-{pid}-004", "agent": "DeliveryAgent",
         "status": "PENDING", "pid": pid},
    ])
    await package_runtime.update_status(pid, PackageStatus.FAILED)
    return pid


async def main():
    passed = 0
    failed = 0

    # Temiz baslangic (proje kurali: PID artigi birakma)
    await pid_runtime.reset()

    # ================================================================
    # TEST 1: find_package — PID ve urun adi ile arama
    # ================================================================
    print("=== TEST 1: find_package (PID + urun adi) ===")
    try:
        pid1 = await _make_failed_package("Akilli Saat X", "TeknoMarka")

        by_pid = await package_runtime.find_package(pid1)
        assert by_pid is not None and by_pid.pid == pid1
        print(f"  PID ile bulundu: {by_pid.pid}")

        by_name = await package_runtime.find_package("Akilli Saat")
        assert by_name is not None and by_name.pid == pid1
        print(f"  Urun adi ile bulundu: {by_name.pid}")

        by_brand = await package_runtime.find_package("TeknoMarka")
        assert by_brand is not None and by_brand.pid == pid1
        print(f"  Marka ile bulundu: {by_brand.pid}")

        not_found = await package_runtime.find_package("OlmayanUrun12345")
        assert not_found is None
        print("  Olmayan urun: None (dogru)")
        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 2: load_full_production_context — anayasal kayitlar
    # ================================================================
    print("\n=== TEST 2: load_full_production_context ===")
    try:
        ctx = await package_runtime.load_full_production_context(pid1)
        assert ctx["pid"] == pid1
        assert ctx["package_status"] == "FAILED"
        assert ctx["total_tasks"] == 4
        assert ctx["completed_tasks"] == 2
        assert ctx["failed_tasks"] == 1
        assert ctx["pending_tasks"] == 1
        assert ctx["failed_step"] == f"TASK-{pid1}-003"
        assert ctx["last_successful_step"] == f"TASK-{pid1}-002"
        assert "Provider timeout" in ctx["last_error"]
        for key in ("workflow", "state_engine_records", "event_logs",
                    "digital_asset_archive", "digital_asset_catalog",
                    "scene_registry", "decision_history", "revision_history"):
            assert key in ctx, f"eksik anahtar: {key}"
        print(f"  Basarisiz adim: {ctx['failed_step']}")
        print(f"  Son basarili adim: {ctx['last_successful_step']}")
        print("  Tum anayasal kayit anahtarlari mevcut")
        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 3: HLK Runtime REPRODUCTION kararlari (MASTER-013)
    # ================================================================
    print("\n=== TEST 3: REPRODUCTION kararlari ===")
    try:
        def _decide(status, failed_t=0, active=True):
            return hlk_runtime.request_decision(DecisionRequest(
                pid=pid1,
                category=DecisionCategory.REPRODUCTION.value,
                requester="test_yeniden_uretim",
                context={
                    "package_status": status, "failed_tasks": failed_t,
                    "completed_tasks": 2, "total_tasks": 4,
                    "last_error": "x", "failed_step": "y",
                    "hlk_runtime_active": active,
                },
            ))

        assert _decide("FAILED", 1).verdict == "RETRY"
        assert _decide("PRODUCING").verdict == "RESUME"
        assert _decide("READY").verdict == "RESUME"
        assert _decide("COMPLETED").verdict == "REPLAY"
        assert _decide("CREATED").verdict == "START_AS_NEW"
        assert _decide("ARCHIVED").verdict == "REJECT"
        assert _decide("FAILED", 1, active=False).verdict == "REJECT"
        d = _decide("FAILED", 1)
        assert d.rationale.get("DecisionMaker") == "HLK_RUNTIME"
        assert d.rationale.get("Justifications")
        print("  RETRY/RESUME/REPLAY/START_AS_NEW/REJECT kararlari dogru")
        print("  Karar gerekcesi standardi (15) uyumlu: DecisionMaker=HLK_RUNTIME")
        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 4: prepare_for_reproduction — RETRY hazirligi
    # ================================================================
    print("\n=== TEST 4: prepare_for_reproduction (RETRY) ===")
    try:
        ok = await package_runtime.prepare_for_reproduction(pid1, "RETRY")
        assert ok is True
        pkg = await package_runtime.load(pid1)
        assert pkg.metadata.status == PackageStatus.PRODUCING.value
        assert pkg.metadata.production_type == "reproduction"
        statuses = {t["task_id"]: t["status"] for t in pkg.task_packages}
        assert statuses[f"TASK-{pid1}-001"] == "COMPLETED"  # korunur
        assert statuses[f"TASK-{pid1}-002"] == "COMPLETED"  # korunur
        assert statuses[f"TASK-{pid1}-003"] == "PENDING"    # sifirlanir
        assert statuses[f"TASK-{pid1}-004"] == "PENDING"
        assert pkg.revision_history, "revision_history bos olmamali"
        last_rev = pkg.revision_history[-1]
        assert last_rev["type"] == "reproduction"
        assert last_rev["procedure"] == "RETRY"
        assert last_rev["previous_status"] == "FAILED"
        print("  Durum: FAILED -> PRODUCING, tur: reproduction")
        print("  Tamamlanan task'lar korundu, basarisiz task PENDING oldu")
        print(f"  Surum gecmisi kaydi: {last_rev['type']}/{last_rev['procedure']}")
        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 5: Executor recovery — checkpoint'li yurutme (simulasyon)
    # ================================================================
    print("\n=== TEST 5: Executor recovery (checkpoint) ===")
    try:
        from services.production_executor import production_executor
        await production_executor.reset()
        production_executor._handlers = {}  # simulasyon modu (gercek provider yok)
        report = await production_executor.recover(pid1)
        assert report.pid == pid1
        assert report.failed_tasks == 0, f"basarisiz task: {report.errors}"
        # 2 checkpoint'li + 2 yeni yurutulen = 4 tamamlanmis
        assert report.completed_tasks == 4, f"beklenen 4, gelen {report.completed_tasks}"
        pkg = await package_runtime.load(pid1)
        assert pkg.metadata.status == PackageStatus.COMPLETED.value
        print(f"  Recovery raporu: {report.completed_tasks}/{report.total_tasks} tamam")
        print("  Tamamlanmis task'lar atlandi, kalanlar yurutuldu")
        print("  Paket durumu: COMPLETED")
        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 6: run_reproduction — tam anayasal zincir (Adim 1-21)
    # ================================================================
    print("\n=== TEST 6: run_reproduction (tam zincir) ===")
    try:
        import services.production_pipeline as pp
        from services.production_runtime import production_runtime
        from services.production_executor import production_executor

        pid2 = await _make_failed_package("Kahve Makinesi Z", "EvMarka")

        # Sahte pipeline handler'lari (gercek provider cagrisi yok)
        async def _fake_task(task, pid):
            return {"result": "ok"}

        async def _fake_delivery(task, pid):
            c = pp.get_context(pid)
            if c is not None:
                c.delivered = True
                if c.request is not None and c.request.bot is not None:
                    await c.request.bot.send_message(
                        chat_id=c.request.chat_id, text="[TESLIM]")
            return {"delivered": True}

        _orig_agents = dict(pp.PIPELINE_AGENTS)
        pp.PIPELINE_AGENTS = {
            "ImageGenerator": _fake_task,
            "VoiceGenerator": _fake_task,
            "VideoRenderer": _fake_task,
            "DeliveryAgent": _fake_delivery,
        }
        try:
            await production_executor.reset()
            hlk_runtime.boot(ADMIN_USER)  # Constitutional Boot Chain
            bot = DummyBot()
            result = await production_runtime.run_reproduction(
                pid2, bot, ADMIN_CHAT, ADMIN_USER
            )
        finally:
            pp.PIPELINE_AGENTS = _orig_agents

        assert result.success is True, f"hata: {result.error}"
        assert result.pid == pid2

        # Bildirimler: yonetici (baslangic + tamamlanma) + kullanici (teslim + tamamlanma)
        admin_msgs = [m for m in bot.messages if m["chat_id"] == ADMIN_CHAT]
        user_msgs = [m for m in bot.messages if m["chat_id"] == USER_CHAT]
        assert any("baslatildi" in m["text"] for m in admin_msgs), "yonetici baslangic bildirimi yok"
        assert any("tamamlandi" in m["text"] for m in admin_msgs), "yonetici tamamlanma bildirimi yok"
        assert any("tamamlandi" in m["text"].lower() or "[TESLIM]" in m["text"]
                   for m in user_msgs), "kullanici bildirimi yok"
        print(f"  Sonuc: success={result.success}, durum={result.state}")
        print(f"  Yonetici bildirimi: {len(admin_msgs)} adet")
        print(f"  Kullanici bildirimi: {len(user_msgs)} adet")

        # Kayit dogrulamalari (Adim 19-20)
        pkg2 = await package_runtime.load(pid2)
        assert pkg2.metadata.status == PackageStatus.COMPLETED.value
        assert pkg2.metadata.production_type == "reproduction"
        event_types = [e.get("event_type") for e in pkg2.event_logs
                       if isinstance(e, dict)]
        assert "EVENT_REPRODUCTION_REQUESTED" in event_types, "OLAY-107 kaydi yok"
        assert "EVENT_REPRODUCTION_STARTED" in event_types, "OLAY-108 kaydi yok"
        cats = [d.get("category") for d in pkg2.decision_history
                if isinstance(d, dict)]
        assert "REPRODUCTION" in cats, "REPRODUCTION karari Decision History'de yok"
        assert pkg2.revision_history and \
            pkg2.revision_history[-1]["type"] == "reproduction"
        print("  OLAY-107 + OLAY-108 paket event_logs'da kayitli")
        print("  REPRODUCTION karari Decision History'de kayitli")
        print("  Surum gecmisi korundu")
        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 7: Istisna akisi — PID dogrulanamazsa guvenli sonlandirma
    # ================================================================
    print("\n=== TEST 7: Istisna akisi (gecersiz PID) ===")
    try:
        from services.production_runtime import production_runtime
        bot = DummyBot()
        result = await production_runtime.run_reproduction(
            "PID-20991231-9999", bot, ADMIN_CHAT, ADMIN_USER
        )
        assert result.success is False
        assert result.error, "hata gerekcesi bos olmamali"
        admin_msgs = [m for m in bot.messages if m["chat_id"] == ADMIN_CHAT]
        assert any("baslatilamadi" in m["text"] for m in admin_msgs), \
            "yonetici istisna bildirimi yok"
        assert any("guvenli" in m["text"].lower() for m in admin_msgs), \
            "guvenli sonlandirma ifadesi yok"
        print(f"  Sonuc: success=False, gerekce: {result.error[:60]}")
        print("  Yonetici anayasal gerekceyle bilgilendirildi")
        print("  Hicbir uretim baslatilmadi (guvenli sonlandirma)")
        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ================================================================
    # Temizlik — test artiklari silinir (proje kurali)
    # ================================================================
    print("\n=== Temizlik ===")
    removed = 0
    for pid in _created_pids:
        for p in (Path("data/production_packages") / f"{pid}.json",
                  Path("data/production_packages/archive") / f"{pid}.json"):
            if p.exists():
                p.unlink()
                removed += 1
    await pid_runtime.reset()
    print(f"  {removed} test paketi silindi, PID registry sifirlandi")

    print("\n" + "=" * 50)
    print(f"SONUC: {passed} PASS / {failed} FAIL")
    print("=" * 50)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
