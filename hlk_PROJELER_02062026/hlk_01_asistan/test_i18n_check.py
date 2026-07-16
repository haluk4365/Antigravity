"""HLK i18n Kapsamli Test"""
from config.i18n import t, _SECTIONS

LANGS = ['tr', 'en', 'de', 'fr', 'es', 'ar', 'ru', 'kr']

def test_all():
    results = {"ok": 0, "fail": 0}

    # Test 1: Kategoriler
    print("=== TEST 1: Kategori kontrolu ===")
    expected = ['s03','s04','s05','s06','s07','s08','s09','s10','s11','s12','s13',
                'common','pricing','payment','admin_payment','material','platform','final']
    for k in expected:
        ok = k in _SECTIONS
        tag = "OK" if ok else "MISSING"
        print(f"  [{tag}] {k}")
        if ok: results["ok"] += 1
        else: results["fail"] += 1

    # Test 2: Tum diller
    print("\n=== TEST 2: Dil eksik kontrolu ===")
    missing = []
    total_keys = 0
    for cat_name, cat_dict in _SECTIONS.items():
        for key, translations in cat_dict.items():
            if not isinstance(translations, dict):
                continue
            total_keys += 1
            for lang in LANGS:
                if lang not in translations:
                    missing.append(f"{cat_name}.{key} -> {lang}")
    if missing:
        for m in missing:
            print(f"  MISSING: {m}")
            results["fail"] += 1
    else:
        print(f"  Tum {total_keys} anahtar x 8 dil = eksiksiz!")
        results["ok"] += 1

    # Test 3: Kritik anahtarlar
    print("\n=== TEST 3: Kritik metinler ===")
    critical = [
        'final.payment_received', 'final.production_started',
        'final.duration_info', 'final.auto_delivery',
        'final.timeout_warning', 'final.timeout_closed',
        'final.payment_approved_toast', 'final.new_session_start',
        'final.payment_cancelled',
        'pricing.title', 'payment.card_title',
        'payment.pay_done_btn', 'payment.pay_cancel_btn',
        'admin_payment.title', 'admin_payment.approve_btn', 'admin_payment.ret_btn',
        's03.title', 's04.title', 's05.title',
        's06.title', 's07.title', 's08.title',
        's09.title', 's10.title', 's11.title',
        's12.title', 's13.scenario_ready',
    ]
    for key in critical:
        val = t(key, 'en')
        if val == key:
            print(f"  MISSING: {key}")
            results["fail"] += 1
        else:
            results["ok"] += 1
    print(f"  {len(critical)} anahtar kontrol edildi")

    # Test 4: Her dilde ornek (ASCII-safe)
    print("\n=== TEST 4: Tum diller ornek ===")
    for lang in LANGS:
        val = t('final.payment_received', lang)
        ok = val != 'final.payment_received'
        print(f"  {lang}: {'OK' if ok else 'MISSING'} | len={len(val)}")

    # Test 5: get_lang
    print("\n=== TEST 5: get_lang ===")
    from config.i18n import get_lang
    assert get_lang({"language": "en"}) == "en"
    assert get_lang({"language": "de"}) == "de"
    assert get_lang({}) == "tr"
    assert get_lang({"language": "xx"}) == "tr"
    print("  get_lang: OK")

    print(f"\n=== SONUC: {results['ok']} OK, {results['fail']} FAIL ===")
    return results["fail"] == 0

if __name__ == "__main__":
    ok = test_all()
    exit(0 if ok else 1)
