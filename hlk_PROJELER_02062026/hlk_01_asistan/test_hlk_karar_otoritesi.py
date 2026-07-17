# -*- coding: utf-8 -*-
"""MASTER-013 / AR-002_81 — HLK Runtime Karar Otoritesi Runtime Testi.

Bu test; karar üretiminin yalnızca HLK Runtime'da gerçekleştiğini,
production_pipeline.py'nin karar üretmediğini ve Karar Talep Protokolü'nün
(durdur → talep et → karar → devam et) çalıştığını doğrular.

Doğrulanan anayasal kurallar:
- MASTER-013: HLK Karar Otoritesi ve Üretim Yürütücüsü Rol Ayrımı
- AR-002_81: Karar Talep Protokolü + karar kategorileri
- OR-004_12: Karar talebi operasyon kuralı
- AR-002_81 Sayısal Değer Yasağı (GC parametreleri)
"""

import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from services.hlk_runtime import (
    DecisionCategory,
    DecisionRequest,
    RuntimeDecision,
    hlk_runtime,
)


PASS = "PASS"
FAIL = "FAIL"
results = []


def check(name: str, cond: bool, detail: str = "") -> None:
    verdict = PASS if cond else FAIL
    results.append((name, verdict, detail))
    print(f"  [{verdict}] {name}" + (f" — {detail}" if detail else ""))


def main() -> int:
    print("=" * 60)
    print("MASTER-013 / AR-002_81 KARAR OTORİTESİ RUNTIME TESTİ")
    print("=" * 60)

    # ── 1. PROVIDER_RESULT: kabul kararı ─────────────────────────────
    d = hlk_runtime.request_decision(DecisionRequest(
        pid="PID-TEST-0001",
        category=DecisionCategory.PROVIDER_RESULT.value,
        requester="test.provider_accept",
        context={"category": "image", "provider": "fal.ai",
                 "artifact": "/tmp/img.png", "error": "",
                 "remaining_candidates": 1},
    ))
    check("PROVIDER_RESULT kabul kararı HLK Runtime'da üretildi",
          isinstance(d, RuntimeDecision) and d.verdict == "ACCEPT",
          f"verdict={d.verdict}")
    check("Karar gerekçesi 15_KARAR standardında (DecisionMaker=HLK_RUNTIME)",
          d.rationale.get("DecisionMaker") == "HLK_RUNTIME")

    # ── 2. PROVIDER_RESULT: red + sıradaki provider kararı ──────────
    d = hlk_runtime.request_decision(DecisionRequest(
        pid="PID-TEST-0001",
        category=DecisionCategory.PROVIDER_RESULT.value,
        requester="test.provider_reject",
        context={"category": "image", "provider": "fal.ai",
                 "artifact": "", "error": "HTTP 500",
                 "remaining_candidates": 1},
    ))
    check("PROVIDER_RESULT red kararı → NEXT_PROVIDER HLK Runtime'da",
          d.verdict == "REJECT" and d.params.get("action") == "NEXT_PROVIDER")

    # ── 3. PROVIDER_RESULT: aday kalmadı → REPORT_FAILURE ────────────
    d = hlk_runtime.request_decision(DecisionRequest(
        pid="PID-TEST-0001",
        category=DecisionCategory.PROVIDER_RESULT.value,
        requester="test.provider_exhausted",
        context={"category": "video", "provider": "hedra",
                 "artifact": "", "error": "timeout",
                 "remaining_candidates": 0},
    ))
    check("Aday kalmadığında REPORT_FAILURE kararı HLK Runtime'da",
          d.verdict == "REJECT" and d.params.get("action") == "REPORT_FAILURE")

    # ── 4. CREATIVE_CONTENT: seslendirme metni kararı (AR-002_77) ────
    d = hlk_runtime.request_decision(DecisionRequest(
        pid="PID-TEST-0001",
        category=DecisionCategory.CREATIVE_CONTENT.value,
        requester="test.voice_script",
        context={"kind": "voice_script", "brand": "TestMarka",
                 "product_name": "TestUrun", "voice_lang": "tr"},
    ))
    check("Seslendirme metni HLK Runtime kararı ile üretildi",
          d.verdict == "PROVIDE" and "TestMarka" in d.params.get("voice_text", ""))

    # ── 5. DELIVERY: teslim + kullanıcı mesajı kararı ────────────────
    d = hlk_runtime.request_decision(DecisionRequest(
        pid="PID-TEST-0001",
        category=DecisionCategory.DELIVERY.value,
        requester="test.delivery_info",
        context={"video_available": False, "brand": "TestMarka",
                 "product_name": "TestUrun", "duration": 15,
                 "voice_lang": "tr"},
    ))
    check("Teslim şekli kararı (DELIVER_INFO) HLK Runtime'da",
          d.verdict == "DELIVER_INFO" and bool(d.params.get("text")))
    d2 = hlk_runtime.request_decision(DecisionRequest(
        pid="PID-TEST-0001",
        category=DecisionCategory.DELIVERY.value,
        requester="test.delivery_video",
        context={"video_available": True, "brand": "TestMarka",
                 "product_name": "TestUrun", "duration": 15,
                 "voice_lang": "tr"},
    ))
    check("Teslim şekli kararı (DELIVER_VIDEO) HLK Runtime'da",
          d2.verdict == "DELIVER_VIDEO" and bool(d2.params.get("caption")))

    # ── 6. USER_NOTIFICATION: başarısızlık bildirimi kararı ──────────
    d = hlk_runtime.request_decision(DecisionRequest(
        pid="PID-TEST-0001",
        category=DecisionCategory.USER_NOTIFICATION.value,
        requester="test.failure_notify",
        context={"kind": "production_failure", "pid": "PID-TEST-0001"},
    ))
    check("Kullanıcı süreç mesajı içeriği HLK Runtime kararı ile",
          d.verdict == "NOTIFY" and "PID-TEST-0001" in d.params.get("text", ""))

    # ── 7. COMPLETION: tamamlanma kararı (AR-002_80) ─────────────────
    d = hlk_runtime.request_decision(DecisionRequest(
        pid="PID-TEST-0001",
        category=DecisionCategory.COMPLETION.value,
        requester="test.completion",
        context={"delivered": True, "video": True, "failed_tasks": 0},
    ))
    check("COMPLETION kararı HLK Runtime'da",
          d.verdict == "CONFIRM_COMPLETION" and d.params.get("success") is True)

    # ── 8. AMBIGUITY: tereddüt kuralı (MASTER-013) ───────────────────
    d = hlk_runtime.request_decision(DecisionRequest(
        pid="PID-TEST-0001",
        category=DecisionCategory.AMBIGUITY.value,
        requester="test.ambiguity",
        context={"reason": "unsupported_provider", "provider": "bilinmeyen.ai"},
    ))
    check("Tereddüt (bilinmeyen provider) kararı HLK Runtime'da (SKIP)",
          d.verdict == "SKIP" and d.params.get("action") == "SKIP")

    # ── 9. Karar kayıtları izlenebilir (PID ile) ─────────────────────
    decisions = hlk_runtime.get_decisions("PID-TEST-0001")
    check("Tüm kararlar PID ile ilişkilendirilerek kaydedildi",
          len(decisions) >= 9, f"kayıt sayısı={len(decisions)}")

    # ── 10. production_pipeline karar üretmiyor (statik doğrulama) ───
    import inspect
    from services import production_pipeline as pp
    src = inspect.getsource(pp)
    check("production_pipeline retry sınırı hesaplamıyor (karar devri)",
          "GC_MAX_RE_EVALUATION_COUNT" not in src)
    check("production_pipeline eskalasyon kararı vermiyor (karar devri)",
          "escalation_engine" not in src)
    check("production_pipeline kullanıcı süreç mesajı üretmiyor",
          "Uretim Tamamlandi" not in src)
    check("production_pipeline seslendirme metnini kendisi üretmiyor",
          "urununu simdi kesfedin" not in src)
    check("production_pipeline karar talebini HLK Runtime'a iletiyor",
          "hlk_runtime.request_decision" in src)

    # ── 11. Sayısal Değer Yasağı (AR-002_81) ─────────────────────────
    hardcoded_ok = (
        "range(8)" not in src
        and "timeout=30)" not in src
        and "timeout=10)" not in src
        and "asyncio.sleep(3)" not in src
        and "asyncio.sleep(5)" not in src
    )
    check("production_pipeline hardcoded sayısal değer içermiyor",
          hardcoded_ok)
    gc_ok = all(k in src for k in (
        "GC_PROVIDER_HTTP_TIMEOUT", "GC_PROVIDER_STATUS_TIMEOUT",
        "GC_PROVIDER_POLL_COUNT", "GC_IMAGE_POLL_INTERVAL",
        "GC_VIDEO_POLL_INTERVAL",
    ))
    check("production_pipeline tüm sayısal değerleri GC'den okuyor", gc_ok)

    from services import production_executor as pe
    pe_src = inspect.getsource(pe)
    check("production_executor retry beklemesi GC parametresinden",
          "GC_EXECUTOR_RETRY_DELAY" in pe_src
          and "asyncio.sleep(0.5)" not in pe_src)

    # ── Sonuç ────────────────────────────────────────────────────────
    failed = [r for r in results if r[1] == FAIL]
    print("-" * 60)
    print(f"TOPLAM: {len(results)} | PASS: {len(results) - len(failed)} | "
          f"FAIL: {len(failed)}")
    if failed:
        print("SONUÇ: FAIL")
        return 1
    print("SONUÇ: PASS — Karar otoritesi münhasıran HLK Runtime'da")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
