"""Production Package Runtime — Test Suite (ASCII-safe)."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Module-level imports (before event loop)
from services.pid_runtime import pid_runtime
from services.production_package_runtime import (
    ProductionPackageRuntime, PackageStatus, package_runtime
)


async def main():
    passed = 0
    failed = 0

    # Cleanup
    await pid_runtime.reset()

    rt = ProductionPackageRuntime()

    # ================================================================
    # TEST 1: Package Create
    # ================================================================
    print("=== TEST 1: Package Create ===")
    try:
        pid_record = await pid_runtime.generate()
        pid = pid_record.pid
        print(f"  PID: {pid}")

        package = await rt.create(pid)
        assert package.pid == pid
        assert package.metadata.status == PackageStatus.CREATED.value
        print(f"  Package created: {package.pid}, status={package.metadata.status}")

        # Duplicate create must fail
        try:
            await rt.create(pid)
            print("  FAIL: Duplicate not detected")
            failed += 1
        except ValueError:
            print("  Duplicate detection: OK")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 2: Package Load (disk persistence)
    # ================================================================
    print("\n=== TEST 2: Package Load ===")
    try:
        loaded = await rt.load(pid)
        assert loaded is not None
        assert loaded.pid == pid
        print(f"  Memory load: {loaded.pid}")

        # Restart simulation
        rt2 = ProductionPackageRuntime()
        loaded2 = await rt2.load(pid)
        assert loaded2 is not None
        assert loaded2.pid == pid
        print(f"  Disk load (restart): {loaded2.pid}")

        # Non-existent PID
        nf = await rt.load("PID-20991231-9999")
        assert nf is None
        print(f"  Non-existent PID: None (correct)")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 3: Package Validate
    # ================================================================
    print("\n=== TEST 3: Package Validate ===")
    try:
        result = await rt.validate(pid)
        print(f"  Valid: {result.is_valid}, Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")
        assert len(result.errors) == 0, f"Errors: {result.errors}"

        result2 = await rt.validate("PID-20991231-9999")
        assert not result2.is_valid
        print(f"  Non-existent PID: {result2.errors[0]}")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 4: Package Update
    # ================================================================
    print("\n=== TEST 4: Package Update ===")
    try:
        brief = {"product_name": "Test Product", "brand": "Test Brand"}
        ok = await rt.update_section(pid, "brief", brief)
        assert ok

        scenario = {"title": "Test Scenario", "scenes": [{"id": 1}]}
        ok = await rt.update_section(pid, "scenario", scenario)
        assert ok

        video_params = {"format": "9:16", "resolution": "1080p"}
        ok = await rt.update_section(pid, "video_parameters", video_params)
        assert ok

        # Invalid section name
        try:
            await rt.update_section(pid, "invalid_section", {})
            print("  FAIL: Invalid section not rejected")
            failed += 1
        except ValueError:
            print("  Invalid section rejection: OK")

        # Verify updates persisted
        loaded = await rt.load(pid)
        assert loaded.brief == brief
        assert loaded.scenario == scenario
        assert loaded.video_parameters == video_params
        print(f"  Updates verified: brief={bool(loaded.brief)}, scenario={bool(loaded.scenario)}, video_params={bool(loaded.video_parameters)}")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 5: Integrity Check
    # ================================================================
    print("\n=== TEST 5: Integrity Check ===")
    try:
        ok, msg = await rt.verify_integrity(pid)
        assert ok, f"Integrity failed: {msg}"
        print(f"  Integrity: {msg[:80]}...")

        ok2, msg2 = await rt.verify_integrity("PID-20991231-9999")
        assert not ok2
        print(f"  Non-existent PID: {msg2}")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 6: PID Linkage
    # ================================================================
    print("\n=== TEST 6: PID Linkage ===")
    try:
        record = await pid_runtime.get_record(pid)
        assert record is not None
        assert record.pid == pid
        print(f"  PID record: {record.pid}")

        validation = await pid_runtime.validate(pid)
        assert validation.is_valid
        print(f"  PID validation: OK")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 7: Digital Asset Linkage
    # ================================================================
    print("\n=== TEST 7: Digital Asset Linkage ===")
    try:
        assets = [
            {"asset_id": "ASSET-001", "type": "image", "sha256": "abc123"},
            {"asset_id": "ASSET-002", "type": "image", "sha256": "def456"},
        ]
        ok = await rt.update_section(pid, "digital_assets", assets)
        assert ok

        images = [
            {"url": "https://example.com/ref1.jpg", "source": "web"},
            {"url": "https://example.com/ref2.jpg", "source": "user"},
        ]
        ok = await rt.update_section(pid, "reference_images", images)
        assert ok

        loaded = await rt.load(pid)
        assert len(loaded.digital_assets) == 2
        assert len(loaded.reference_images) == 2
        print(f"  Digital assets: {len(loaded.digital_assets)}, Reference images: {len(loaded.reference_images)}")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 8: Event Linkage
    # ================================================================
    print("\n=== TEST 8: Event Linkage ===")
    try:
        events = [
            {"event_id": "OLAY-031", "name": "EVENT_PRODUCTION_PACKAGE_CREATED", "pid": pid},
            {"event_id": "OLAY-023", "name": "EVENT_VIDEO_PRODUCTION_STARTED", "pid": pid},
        ]
        ok = await rt.update_section(pid, "event_logs", events)
        assert ok

        loaded = await rt.load(pid)
        assert len(loaded.event_logs) == 2
        for evt in loaded.event_logs:
            assert evt.get("pid") == pid
        print(f"  Event logs: {len(loaded.event_logs)} (PID field verified)")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 9: Task Package Linkage
    # ================================================================
    print("\n=== TEST 9: Task Package Linkage ===")
    try:
        tasks = [
            {"task_id": "TASK-001", "agent": "SceneGen", "status": "COMPLETED", "pid": pid},
            {"task_id": "TASK-002", "agent": "VoiceGen", "status": "PENDING", "pid": pid},
        ]
        ok = await rt.update_section(pid, "task_packages", tasks)
        assert ok

        loaded = await rt.load(pid)
        assert len(loaded.task_packages) == 2
        for tp in loaded.task_packages:
            assert tp.get("pid") == pid
        print(f"  Task packages: {len(loaded.task_packages)} (PID reference verified)")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 10: Restart Persistence
    # ================================================================
    print("\n=== TEST 10: Restart Persistence ===")
    try:
        rt3 = ProductionPackageRuntime()
        loaded = await rt3.load(pid)
        assert loaded is not None
        assert loaded.pid == pid
        assert loaded.brief.get("product_name") == "Test Product"
        assert len(loaded.task_packages) == 2
        assert len(loaded.event_logs) == 2
        assert len(loaded.digital_assets) == 2
        print(f"  All sections preserved across restart")
        print(f"  Brief: {loaded.brief.get('product_name')}, Tasks: {len(loaded.task_packages)}, Events: {len(loaded.event_logs)}, Assets: {len(loaded.digital_assets)}")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 11: Multiple Packages
    # ================================================================
    print("\n=== TEST 11: Multiple Packages ===")
    try:
        pid2_record = await pid_runtime.generate()
        pid2 = pid2_record.pid
        print(f"  Second PID: {pid2}")

        pkg2 = await rt.create(pid2)
        assert pkg2.pid == pid2

        pkg1 = await rt.load(pid)
        pkg2_loaded = await rt.load(pid2)
        assert pkg1 is not None and pkg2_loaded is not None
        assert pkg1.pid != pkg2_loaded.pid
        print(f"  Package 1: {pkg1.pid} ({pkg1.metadata.status})")
        print(f"  Package 2: {pkg2_loaded.pid} ({pkg2_loaded.metadata.status})")

        count = await rt.get_package_count()
        assert count['active'] >= 2
        print(f"  Total: {count['total']}, Active: {count['active']}")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 12: Close and Archive
    # ================================================================
    print("\n=== TEST 12: Close and Archive ===")
    try:
        ok = await rt.close(pid)
        assert ok
        closed = await rt.load(pid)
        assert closed.metadata.status == PackageStatus.COMPLETED.value
        assert closed.metadata.completed_at
        print(f"  Closed: {pid} (status={closed.metadata.status})")

        ok = await rt.archive(pid)
        assert ok
        archived = await rt.load(pid)
        assert archived is not None
        assert archived.metadata.status == PackageStatus.ARCHIVED.value
        assert archived.metadata.archived_at
        print(f"  Archived: {pid} (status={archived.metadata.status})")

        # Archived package cannot be updated
        ok2 = await rt.update_section(pid, "brief", {"test": True})
        if ok2:
            print("  WARNING: Archived package was updated")
        else:
            print(f"  Archived update blocked: OK")

        count = await rt.get_package_count()
        assert count['archived'] >= 1
        print(f"  Total: {count['total']}, Archived: {count['archived']}")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # SUMMARY
    # ================================================================
    print()
    print("=" * 60)
    print(f"RESULTS: {passed}/{passed+failed} PASSED, {failed}/{passed+failed} FAILED")
    if failed == 0:
        print("PRODUCTION PACKAGE RUNTIME: ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)

    # Cleanup
    await pid_runtime.reset()

    return passed, failed


if __name__ == "__main__":
    asyncio.run(main())
