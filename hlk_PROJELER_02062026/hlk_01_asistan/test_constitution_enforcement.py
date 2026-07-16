"""Constitution Enforcement Engine — Test Suite."""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from services.constitution_enforcement import (
    ConstitutionEnforcementEngine, EnforcementVerdict,
    DecisionJustification, ViolationSeverity, constitution_enforcement
)


def test_pre_check():
    """TEST 1: PRE-CHECK CTP creation."""
    cee = ConstitutionEnforcementEngine()
    ctp = cee.pre_check(
        "Test task: verify CTP creation",
        ["test.py", "services/test.py"],
        master_rules=["MASTER-001", "MASTER-003", "MASTER-004"],
        arch_rules=["AR-002_57", "AR-002_70"],
        flow_steps=["FD-008_1"],
    )
    assert ctp.ctp_id.startswith("CEE-CTP-"), f"Invalid CTP ID: {ctp.ctp_id}"
    assert len(ctp.master_rules) == 3
    assert len(ctp.arch_rules) == 2
    assert len(ctp.immutable_fields) == 5
    print(f"  CTP: {ctp.ctp_id}, MASTER:{len(ctp.master_rules)}, AR:{len(ctp.arch_rules)}")
    print("  PASS")


def test_post_check_pass():
    """TEST 2: POST-CHECK PASS verdict."""
    cee = ConstitutionEnforcementEngine()
    cee.pre_check("Test PASS", ["test.py"])
    report = cee.post_check(True, True, True, True, True, True)
    assert report.verdict == EnforcementVerdict.PASS
    assert report.all_passed
    assert report.deficiency_count == 0
    assert report.justification
    assert report.justification["DecisionName"] == "CEE Enforcement PASS"
    print(f"  Verdict: {report.verdict.value}, All passed: {report.all_passed}")
    print("  PASS")


def test_post_check_fail():
    """TEST 3: POST-CHECK FAIL verdict + justification."""
    cee = ConstitutionEnforcementEngine()
    cee.pre_check("Test FAIL", ["test.py"])
    report = cee.post_check(
        code_anayasa_ok=False, flow_ok=True, state_ok=False,
        operational_ok=True, architecture_ok=True, runtime_ok=True,
        deficiencies=[
            {"type": "MISSING_CHECK", "description": "Kod-Anayasa uyumsuz", "ana_yasa_ref": "MASTER-003"},
        ],
    )
    assert report.verdict == EnforcementVerdict.FAIL
    assert not report.all_passed
    assert report.deficiency_count == 1
    assert report.justification
    assert "FAIL" in report.justification["DecisionName"]
    assert len(report.justification["Justifications"]) >= 1
    print(f"  Verdict: {report.verdict.value}, Deficiencies: {report.deficiency_count}")
    print(f"  Justification: {report.justification['DecisionName']}")
    print("  PASS")


def test_six_dimension_audit():
    """TEST 4: 6-dimension audit granularity."""
    cee = ConstitutionEnforcementEngine()
    cee.pre_check("6-dim test", ["test.py"])

    # All pass
    r = cee.post_check(True, True, True, True, True, True)
    assert r.verdict == EnforcementVerdict.PASS

    # Each dimension individually fails
    checks = [
        (False,True,True,True,True,True, "code_anayasa"),
        (True,False,True,True,True,True, "flow"),
        (True,True,False,True,True,True, "state"),
        (True,True,True,False,True,True, "operational"),
        (True,True,True,True,False,True, "architecture"),
        (True,True,True,True,True,False, "runtime"),
    ]
    for c1,c2,c3,c4,c5,c6,name in checks:
        r = cee.post_check(c1,c2,c3,c4,c5,c6)
        assert r.verdict == EnforcementVerdict.FAIL, f"{name} should FAIL"
    print(f"  All 6 dimensions individually verified")
    print("  PASS")


def test_violation_detection():
    """TEST 5: Violation detection."""
    cee = ConstitutionEnforcementEngine()

    # CRITICAL: constitution not ready
    has, defs, viols = cee.detect_violations({"constitution_ready": False})
    assert has
    assert any(v["severity"] == "KRITIK" for v in viols)
    print(f"  KRITIK violation detected: {viols[0]['type']}")

    # Clean context
    has, defs, viols = cee.detect_violations({"constitution_ready": True})
    assert not has
    print(f"  Clean context: no violations")

    # Hardcoded values
    has, defs, viols = cee.detect_violations({
        "constitution_ready": True,
        "hardcoded_values": ["SAHNE1_SURE=15"],
    })
    assert has
    assert any(v["type"] == "HARDCODED_VALUE" for v in viols)
    print(f"  Hardcoded value detected: {viols[0]['type']}")

    print("  PASS")


def test_decision_justification():
    """TEST 6: Decision Justification (15_KARAR_GEREKCESI_STANDARDI.md)."""
    # PASS justification
    j_pass = DecisionJustification(
        decision_name="CEE Enforcement PASS",
        decision_description="All checks passed.",
        justifications=["Code compliant", "Flow compliant"],
        confidence_level="HIGH",
        decision_outcomes=["Production can proceed"],
    )
    d = j_pass.to_dict()
    assert d["DecisionID"].startswith("DEC-")
    assert d["DecisionMaker"] == "CEE"
    assert d["ConfidenceLevel"] == "HIGH"
    assert len(d["Justifications"]) == 2
    print(f"  PASS justification: {d['DecisionID']}")

    # FAIL justification
    j_fail = DecisionJustification(
        decision_name="CEE Enforcement FAIL",
        decision_description="Checks failed.",
        justifications=["Code-Anayasa mismatch"],
        confidence_level="HIGH",
        decision_outcomes=["Executor retry required"],
        pid="PID-20260713-0001",
    )
    d2 = j_fail.to_dict()
    assert d2["PID"] == "PID-20260713-0001"
    assert d2["DecisionOutcomes"][0] == "Executor retry required"
    print(f"  FAIL justification: PID={d2['PID']}")

    print("  PASS")


def test_escalation():
    """TEST 7: CEE-005 Escalation after max retries."""
    cee = ConstitutionEnforcementEngine()
    ctp = cee.pre_check("Escalation test", ["test.py"])

    # 3 failures = escalation
    for i in range(3):
        report = cee.post_check(
            code_anayasa_ok=False, flow_ok=True, state_ok=True,
            operational_ok=True, architecture_ok=True, runtime_ok=True,
        )
        assert report.verdict == EnforcementVerdict.FAIL

    assert cee.needs_escalation()
    assert cee.get_attempt_count() == 3
    print(f"  After {cee.MAX_ENFORCEMENT_RETRIES} FAILs: needs_escalation={cee.needs_escalation()}")
    print("  PASS")


def test_scan_diff_evaluation():
    """TEST 8: Scan/Diff Engine result evaluation."""
    cee = ConstitutionEnforcementEngine()

    # Scan result - clean
    cee.pre_check("Scan test", ["test.py"])
    scan_r = cee.evaluate_scan_result({
        "all_pass": True, "deficiencies": [],
        "passed": 10, "total_checks": 10,
    })
    assert scan_r.verdict == EnforcementVerdict.PASS

    # Scan result - failed
    scan_r2 = cee.evaluate_scan_result({
        "all_pass": False,
        "deficiencies": [{"type": "VIOLATION", "description": "Test failure", "ana_yasa_ref": "AR-002_57"}],
    })
    assert scan_r2.verdict == EnforcementVerdict.FAIL
    print(f"  Scan PASS: {scan_r.verdict.value}, Scan FAIL: {scan_r2.verdict.value}")

    # Diff result
    cee.pre_check("Diff test", ["test.py"])
    diff_r = cee.evaluate_diff_result({"has_violations": False, "violations": []})
    assert diff_r.verdict == EnforcementVerdict.PASS
    print(f"  Diff PASS: {diff_r.verdict.value}")

    print("  PASS")


def test_history():
    """TEST 9: Enforcement history tracking."""
    cee = ConstitutionEnforcementEngine()
    cee.pre_check("History test", ["test.py"])
    cee.post_check(True, True, True, True, True, True)
    cee.post_check(False, True, True, True, True, True)

    history = cee.get_history()
    assert len(history) == 2
    assert history[0].verdict == EnforcementVerdict.PASS
    assert history[1].verdict == EnforcementVerdict.FAIL
    print(f"  History: {len(history)} entries (PASS + FAIL)")
    print("  PASS")


def test_reset():
    """TEST 10: CEE reset."""
    cee = ConstitutionEnforcementEngine()
    cee.pre_check("Reset test", ["test.py"])
    assert cee.get_active_ctp() is not None

    cee.reset()
    assert cee.get_active_ctp() is None
    print(f"  After reset: active_ctp={cee.get_active_ctp()}")
    print("  PASS")


def test_concurrent_enforcement():
    """TEST 11: Multiple enforcement cycles."""
    cee = ConstitutionEnforcementEngine()

    for i in range(5):
        cee.pre_check(f"Cycle {i}", [f"test_{i}.py"])
        report = cee.post_check(
            code_anayasa_ok=(i != 3),  # cycle 3 fails
            flow_ok=True, state_ok=True,
            operational_ok=True, architecture_ok=True, runtime_ok=True,
        )
        expected = EnforcementVerdict.FAIL if i == 3 else EnforcementVerdict.PASS
        assert report.verdict == expected, f"Cycle {i}: expected {expected}, got {report.verdict}"

    history = cee.get_history()
    assert len(history) == 5
    passes = sum(1 for h in history if h.verdict == EnforcementVerdict.PASS)
    fails = sum(1 for h in history if h.verdict == EnforcementVerdict.FAIL)
    print(f"  5 cycles: {passes} PASS, {fails} FAIL")
    print("  PASS")


def main():
    passed = 0; failed = 0
    tests = [
        ("PRE-CHECK CTP Creation", test_pre_check),
        ("POST-CHECK PASS", test_post_check_pass),
        ("POST-CHECK FAIL + Justification", test_post_check_fail),
        ("6-Dimension Audit", test_six_dimension_audit),
        ("Violation Detection", test_violation_detection),
        ("Decision Justification (15_KARAR)", test_decision_justification),
        ("CEE-005 Escalation", test_escalation),
        ("Scan/Diff Evaluation", test_scan_diff_evaluation),
        ("History Tracking", test_history),
        ("CEE Reset", test_reset),
        ("Concurrent Enforcement", test_concurrent_enforcement),
    ]

    for name, test_fn in tests:
        print(f"\n=== {name} ===")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            import traceback; traceback.print_exc()
            failed += 1

    print()
    print("=" * 60)
    print(f"RESULTS: {passed}/{passed+failed} PASSED, {failed}/{passed+failed} FAILED")
    if failed == 0:
        print("CONSTITUTION ENFORCEMENT ENGINE: ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
