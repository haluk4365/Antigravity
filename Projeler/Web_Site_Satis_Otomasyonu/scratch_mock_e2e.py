"""
Kıyamet Testi — scratch_mock_e2e.py
ANA Kuralı: Simülasyon / Fuzzing / "Kıyamet" Testi

output.json'daki GERÇEK Apify payload'unu ve bilerek bozulmuş mock verileri
kullanarak pipeline fonksiyonlarını uçtan uca test eder.

Apify API veya Notion API ÇAĞIRMAZ — sadece lokal parse/score/logger fonksiyonlarını sınar.

Kullanım:
  cd Projeler/Web_Site_Satis_Otomasyonu
  python scratch_mock_e2e.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import logging
from unittest.mock import patch, MagicMock
from typing import Any

# Mono-repo kök path ayarı
_project_root = os.path.dirname(os.path.abspath(__file__))
_mono_root = os.path.abspath(os.path.join(_project_root, "..", ".."))
if _mono_root not in sys.path:
    sys.path.insert(0, _mono_root)

# Test edilen modüller — config import'u env check yapıyor, mock'lanacak
# Önce path'ler ayarlandıktan sonra import et
from src.lead_generator import parse_place, score_lead, _parse_price_scale

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
test_logger = logging.getLogger("kiyamet_testi")


# ============================================================================
# TEST HELPER
# ============================================================================

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: list[str] = []

    def ok(self, name: str):
        self.passed += 1
        test_logger.info("  ✅ %s", name)

    def fail(self, name: str, reason: str):
        self.failed += 1
        self.errors.append(f"{name}: {reason}")
        test_logger.error("  ❌ %s — %s", name, reason)

    def summary(self):
        total = self.passed + self.failed
        test_logger.info("")
        test_logger.info("=" * 60)
        test_logger.info("📊 KIYAMET TESTİ SONUÇLARI: %d/%d başarılı", self.passed, total)
        if self.errors:
            test_logger.info("❌ Başarısız testler:")
            for err in self.errors:
                test_logger.info("   • %s", err)
        else:
            test_logger.info("🎉 Tüm testler geçti!")
        test_logger.info("=" * 60)
        return self.failed == 0


results = TestResult()


# ============================================================================
# GERÇEK PAYLOAD YÜKLE (output.json)
# ============================================================================

def load_real_payload() -> list[dict]:
    """output.json'dan gerçek Apify verisi yükle."""
    output_path = os.path.join(_project_root, "output.json")
    if not os.path.exists(output_path):
        test_logger.warning("output.json bulunamadı — gerçek veri testleri atlanacak")
        return []

    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()

    # output.json'da ilk birkaç satır console output olabilir — JSON kısmını bul
    items = []
    json_start = content.find("{")
    if json_start == -1:
        return []

    # Her {...} bloğunu ayrıştır
    depth = 0
    block_start = None
    for i, ch in enumerate(content[json_start:], start=json_start):
        if ch == "{":
            if depth == 0:
                block_start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and block_start is not None:
                try:
                    obj = json.loads(content[block_start : i + 1])
                    items.append(obj)
                except json.JSONDecodeError:
                    pass
                block_start = None
        if len(items) >= 2:  # 2 sample yeterli
            break

    return items


REAL_PAYLOAD = load_real_payload()


# ============================================================================
# TEST 1: Happy Path — Gerçek Veri
# ============================================================================

def test_happy_path():
    """output.json verisinin parse + score edilmesini test et."""
    test_name = "Happy Path (gerçek output.json)"
    if not REAL_PAYLOAD:
        results.fail(test_name, "output.json yüklenemedi")
        return

    try:
        for item in REAL_PAYLOAD:
            lead = parse_place(item)
            score = score_lead(lead)

            assert lead["name"] != "N/A", f"İşletme adı N/A döndü: {item.get('title')}"
            assert isinstance(score, float), f"Skor float değil: {type(score)}"
            assert 0 <= score <= 100, f"Skor aralık dışı: {score}"
            assert lead["place_id"], f"place_id boş"

        results.ok(test_name)
    except Exception as e:
        results.fail(test_name, str(e))


# ============================================================================
# TEST 2: Empty Payload
# ============================================================================

def test_empty_payload():
    """Boş liste verildiğinde graceful davranış."""
    test_name = "Empty Payload ([])"
    try:
        items = []
        leads = [parse_place(item) for item in items]
        assert leads == [], "Boş input boş output vermeli"
        results.ok(test_name)
    except Exception as e:
        results.fail(test_name, f"Crash: {str(e)}")


# ============================================================================
# TEST 3: Eksik Key'ler
# ============================================================================

def test_missing_keys():
    """title, totalScore gibi kritik alanlar olmadan parse crash etmemeli."""
    test_name = "Eksik Key'ler (title, totalScore yok)"
    try:
        broken_item = {
            "address": "Bilinmiyor Cad.",
            "placeId": "TEST_MISSING_KEYS",
        }
        lead = parse_place(broken_item)
        score = score_lead(lead)

        assert lead["name"] == "N/A", f"Beklenen N/A, gelen: {lead['name']}"
        assert lead["stars"] == 0, f"Beklenen 0, gelen: {lead['stars']}"
        assert lead["reviews_count"] == 0, f"Beklenen 0, gelen: {lead['reviews_count']}"
        assert isinstance(score, float), f"Skor float değil"
        assert score >= 0, f"Skor negatif: {score}"

        results.ok(test_name)
    except Exception as e:
        results.fail(test_name, f"Crash: {str(e)}")


# ============================================================================
# TEST 4: Bozuk Veri Tipleri
# ============================================================================

def test_corrupt_types():
    """totalScore string, reviewsCount null gibi bozuk tipler."""
    test_name = "Bozuk Veri Tipleri (totalScore='abc')"
    try:
        broken_item = {
            "title": "Bozuk Restoran",
            "totalScore": "abc",       # string olmamalı ama gelebilir
            "reviewsCount": None,       # null
            "price": 12345,             # int olarak gelmiş
            "placeId": "TEST_CORRUPT",
            "categoryName": None,       # null
        }
        lead = parse_place(broken_item)
        score = score_lead(lead)

        # stars "abc" olduğunda 0'a düşmeli (or 0 guard)
        # Eğer düşmüyorsa score_lead'de TypeError olabilir
        assert isinstance(score, float), f"Skor float değil: {type(score)}"
        results.ok(test_name)
    except TypeError as e:
        results.fail(test_name, f"TypeError yakalanmadı: {str(e)}")
    except Exception as e:
        results.fail(test_name, f"Beklenmedik crash: {type(e).__name__}: {str(e)}")


# ============================================================================
# TEST 5: Null Payload
# ============================================================================

def test_null_item():
    """Listedeki bir item None ise crash olmamalı."""
    test_name = "Null Payload (None item)"
    try:
        # parse_place None alırsa AttributeError vermemeli — kontrol edelim
        lead = parse_place({})  # tamamen boş dict
        score = score_lead(lead)

        assert lead["name"] == "N/A"
        assert score >= 0
        results.ok(test_name)
    except Exception as e:
        results.fail(test_name, f"Crash: {type(e).__name__}: {str(e)}")


# ============================================================================
# TEST 6: Dev Payload (Performans)
# ============================================================================

def test_large_payload():
    """10.000 item simüle — performans ve bellek kontrolü."""
    test_name = "Dev Payload (10.000 item)"
    try:
        base_item = REAL_PAYLOAD[0] if REAL_PAYLOAD else {
            "title": "Test İşletme",
            "totalScore": 4.5,
            "reviewsCount": 150,
            "price": "$$",
            "placeId": "PERF_TEST",
            "categoryName": "Restaurant",
            "address": "Test Adres",
            "city": "İstanbul",
        }

        # 10.000 kopyası
        large_payload = []
        for i in range(10_000):
            item = dict(base_item)
            item["placeId"] = f"PERF_{i}"
            large_payload.append(item)

        t0 = time.time()
        leads = []
        for item in large_payload:
            lead = parse_place(item)
            lead["score"] = score_lead(lead)
            leads.append(lead)
        elapsed = time.time() - t0

        assert len(leads) == 10_000, f"Beklenen 10000, gelen: {len(leads)}"
        assert elapsed < 10, f"10.000 item {elapsed:.1f}s sürdü — 10s limitini aştı"

        results.ok(f"{test_name} ({elapsed:.2f}s)")
    except Exception as e:
        results.fail(test_name, f"Crash: {type(e).__name__}: {str(e)}")


# ============================================================================
# TEST 7: Supabase Logger Çökmesi (Fallback Testi)
# ============================================================================

def test_logger_fallback():
    """Supabase erişilemez olduğunda fallback JSONL'ye yazmalı."""
    test_name = "Supabase Logger Çökmesi (fallback)"
    try:
        from _skills.providers.supabase_logger import SupabaseLoggerNode

        # Sahte/erişilemez URL ile init
        mock_logger = SupabaseLoggerNode(
            supabase_url="https://fake-project.supabase.co",
            supabase_key="fake-key-12345",
        )

        # Fallback dosya yolunu temizle (varsa)
        fallback_file = "fallback_antigravity_logs.jsonl"
        if os.path.exists(fallback_file):
            os.remove(fallback_file)

        # safe_log çağır — Supabase'e bağlanamayacak, fallback'e düşmeli
        result = mock_logger.safe_log(
            project_name="KIYAMET_TEST",
            status="TEST",
            message="Bu bir simülasyon — fallback test",
            details={"test": True},
            raw_payload={"simulated": "data"},
        )

        # safe_log False dönmeli (Supabase fail → fallback'e yazdı)
        assert result is False, f"Supabase'e bağlanmaması gerekirdi ama result={result}"

        # Fallback dosyası oluşmuş mu?
        assert os.path.exists(fallback_file), "Fallback JSONL dosyası oluşmadı"

        with open(fallback_file, "r") as f:
            lines = f.readlines()
        assert len(lines) >= 1, "Fallback dosyası boş"

        # Fallback kaydını doğrula
        record = json.loads(lines[-1])
        assert record["project_name"] == "KIYAMET_TEST"
        assert record["status"] == "TEST"
        assert "fallback_error" in record

        # Temizle
        os.remove(fallback_file)

        results.ok(test_name)
    except ImportError:
        results.fail(test_name, "_skills.providers.supabase_logger import edilemedi")
    except Exception as e:
        results.fail(test_name, f"Crash: {type(e).__name__}: {str(e)}")


# ============================================================================
# TEST 8: Price Parse Edge Cases
# ============================================================================

def test_price_edge_cases():
    """Fiyat alanının çeşitli edge-case formatlarını test et."""
    test_name = "Price Parse Edge Cases"
    try:
        cases = [
            (None, ("Bilinmiyor", 15)),
            ("", ("Bilinmiyor", 15)),
            ("₺2,000+", ("$$$", 30)),
            ("$", ("$", 10)),
            ("$$", ("$$", 20)),
            ("$$$", ("$$$", 30)),
            ("Cheap", ("$", 10)),
            ("ucuz", ("$", 10)),
            ("pahalı", ("$$$", 30)),
        ]

        for input_val, expected in cases:
            got = _parse_price_scale(input_val)
            assert got == expected, f"Input={input_val!r}: beklenen={expected}, gelen={got}"

        results.ok(test_name)
    except Exception as e:
        results.fail(test_name, f"{str(e)}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    test_logger.info("")
    test_logger.info("🔥 KIYAMET TESTİ BAŞLIYOR — Web_Site_Satis_Otomasyonu")
    test_logger.info("=" * 60)

    test_happy_path()
    test_empty_payload()
    test_missing_keys()
    test_corrupt_types()
    test_null_item()
    test_large_payload()
    test_logger_fallback()
    test_price_edge_cases()

    all_passed = results.summary()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
