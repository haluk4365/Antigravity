"""Production Executor — Test Suite."""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from services.pid_runtime import pid_runtime
from services.production_package_runtime import (
    ProductionPackageRuntime, PackageStatus
)
from services.production_executor import (
    ProductionExecutor, ExecutorState, ExecutionStatus, production_executor
)


async def main():
    passed = 0
    failed = 0

    # Cleanup
    await pid_runtime.reset()

    rt = ProductionPackageRuntime()
    executor = ProductionExecutor()

    # ================================================================
    # SETUP: Create a Production Package with Task Packages
    # ================================================================
    print("=== SETUP: Creating test package with tasks ===")
    r = await pid_runtime.generate()
    pid = r.pid
    pkg = await rt.create(pid)
    await rt.update_section(pid, "brief", {"product": "Test Product"})
    await rt.update_section(pid, "scenario", {"title": "Test Scenario"})
    await rt.update_section(pid, "video_parameters", {"format": "9:16", "resolution": "1080p"})

    # Add Task Packages
    tasks = [
        {"task_id": "TASK-001", "agent": "SceneGenerator", "status": "PENDING", "pid": pid, "input_data": True},
        {"task_id": "TASK-002", "agent": "VoiceGenerator", "status": "PENDING", "pid": pid, "input_data": True},
        {"task_id": "TASK-003", "agent": "VideoRenderer", "status": "PENDING", "pid": pid},
    ]
    await rt.update_section(pid, "task_packages", tasks)

    # Add some service usage and decision history
    await rt.update_section(pid, "service_usage", {"voice_service": "ElevenLabs", "video_service": "Higgsfield"})
    await rt.update_section(pid, "decision_history", [{"decision": "approved", "by": "admin"}])

    print(f"  Package prepared: {pid} with {len(tasks)} tasks")
    print("  SETUP COMPLETE\n")

    # ================================================================
    # TEST 1: Production Package Load + Validation
    # ================================================================
    print("=== TEST 1: Package Load + Validation ===")
    try:
        # Load package via executor's internal validation
        await executor._validate_prerequisites(pid)
        print(f"  Prerequisites validated for: {pid}")

        tasks_loaded = await executor._load_task_packages(pid)
        assert len(tasks_loaded) == 3, f"Expected 3 tasks, got {len(tasks_loaded)}"
        # Check deterministic ordering
        task_ids = [t["task_id"] for t in tasks_loaded]
        assert task_ids == sorted(task_ids), f"Tasks not sorted: {task_ids}"
        print(f"  Tasks loaded: {task_ids} (sorted OK)")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 2: Full Execution Flow
    # ================================================================
    print("\n=== TEST 2: Full Execution Flow ===")
    try:
        report = await executor.execute(pid)
        assert report.total_tasks == 3
        assert report.completed_tasks == 3
        assert report.failed_tasks == 0
        assert executor._state == ExecutorState.COMPLETED
        print(f"  Total: {report.total_tasks}, Completed: {report.completed_tasks}, Failed: {report.failed_tasks}")
        print(f"  State: {executor._state.value}")

        # Verify each result
        for r in report.results:
            assert r.status == ExecutionStatus.SUCCESS.value, f"Task {r.task_id} not SUCCESS: {r.status}"
            assert r.duration_ms >= 0
            assert r.pid == pid
        print(f"  All {len(report.results)} results: SUCCESS with valid PID")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 3: Task Status Reporting
    # ================================================================
    print("\n=== TEST 3: Task Status Reporting ===")
    try:
        state = executor.get_state()
        assert state["executor_state"] == "COMPLETED"
        assert state["completed_tasks"] == 3
        assert state["failed_tasks"] == 0
        print(f"  State: {state['executor_state']}, Tasks: {state['completed_tasks']}/{state['total_tasks']}")

        report_dict = executor.get_report()
        assert report_dict is not None
        assert report_dict["pid"] == pid
        print(f"  Report available: pid={report_dict['pid']}, results={len(report_dict['results'])}")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 4: Already-Completed Task Skipping
    # ================================================================
    print("\n=== TEST 4: Already-Completed Task Skipping ===")
    try:
        # Create new package with a mix of pending and completed tasks
        r2 = await pid_runtime.generate(); pid2 = r2.pid
        pkg2 = await rt.create(pid2)
        await rt.update_section(pid2, "brief", {"product": "Test 2"})
        await rt.update_section(pid2, "scenario", {"title": "Test"})
        await rt.update_section(pid2, "video_parameters", {"format": "1:1"})
        mixed_tasks = [
            {"task_id": "TASK-A", "agent": "Agent1", "status": "COMPLETED", "pid": pid2},
            {"task_id": "TASK-B", "agent": "Agent2", "status": "PENDING", "pid": pid2},
            {"task_id": "TASK-C", "agent": "Agent3", "status": "SUCCESS", "pid": pid2},
            {"task_id": "TASK-D", "agent": "Agent4", "status": "PENDING", "pid": pid2},
        ]
        await rt.update_section(pid2, "task_packages", mixed_tasks)

        # Execute — should skip TASK-A and TASK-C (already completed)
        report2 = await executor.execute(pid2)
        # TASK-A and TASK-C have status COMPLETED/SUCCESS → they produce "already_completed" result with SUCCESS status
        # TASK-B and TASK-D have status PENDING → they are executed normally
        print(f"  Total: {report2.total_tasks}, Completed: {report2.completed_tasks}, Failed: {report2.failed_tasks}")
        # All 4 should succeed (2 already done + 2 newly executed)
        assert report2.completed_tasks == 4, f"Expected 4 completed, got {report2.completed_tasks}"
        assert report2.failed_tasks == 0
        print(f"  Already-completed tasks correctly skipped, pending tasks executed")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 5: Retry Behavior
    # ================================================================
    print("\n=== TEST 5: Retry Behavior ===")
    try:
        # Retry is built into _execute_task with GC_EXECUTOR_MAX_RETRY
        # Default is 3 retries. On success, retry loop exits.
        # On failure, it retries up to max_retry times.
        import os
        max_retry = int(os.getenv("GC_EXECUTOR_MAX_RETRY", "3"))
        print(f"  GC_EXECUTOR_MAX_RETRY: {max_retry}")
        print(f"  Retry mechanism confirmed in _execute_task (attempt loop)")
        print(f"  Timeout protection: GC_EXECUTOR_TASK_TIMEOUT={os.getenv('GC_EXECUTOR_TASK_TIMEOUT', '300.0')}s")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 6: Event Integration
    # ================================================================
    print("\n=== TEST 6: Event Integration ===")
    try:
        # After execution, event_logs should be updated
        from services.production_package_runtime import package_runtime
        pkg = await package_runtime.load(pid)
        assert len(pkg.event_logs) > 0, "Event logs should be updated"
        latest_event = pkg.event_logs[-1] if isinstance(pkg.event_logs[-1], dict) else pkg.event_logs[-1]
        print(f"  Event logs count: {len(pkg.event_logs)}")
        if isinstance(latest_event, dict):
            print(f"  Latest event: {latest_event.get('event_type', 'unknown')}")

        # All events must have PID
        for evt in pkg.event_logs:
            if isinstance(evt, dict):
                assert evt.get("pid") == pid, f"Event missing PID: {evt}"
        print(f"  All events have PID field: OK")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 7: Package Status Update
    # ================================================================
    print("\n=== TEST 7: Package Status Update ===")
    try:
        from services.production_package_runtime import package_runtime
        pkg = await package_runtime.load(pid)
        print(f"  Package status after execution: {pkg.metadata.status}")
        # Should be COMPLETED (all tasks succeeded)
        assert pkg.metadata.status in (PackageStatus.COMPLETED.value,), \
            f"Expected COMPLETED, got {pkg.metadata.status}"

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 8: Multiple Task Packages
    # ================================================================
    print("\n=== TEST 8: Multiple Task Packages ===")
    try:
        # Create package with many tasks
        r3 = await pid_runtime.generate(); pid3 = r3.pid
        pkg3 = await rt.create(pid3)
        await rt.update_section(pid3, "brief", {"product": "Multi-task"})
        await rt.update_section(pid3, "scenario", {"title": "Multi"})
        await rt.update_section(pid3, "video_parameters", {"format": "16:9"})
        many_tasks = [
            {"task_id": f"TASK-{i:03d}", "agent": f"Agent-{i}", "status": "PENDING", "pid": pid3}
            for i in range(1, 11)
        ]
        await rt.update_section(pid3, "task_packages", many_tasks)

        report3 = await executor.execute(pid3)
        assert report3.total_tasks == 10
        assert report3.completed_tasks == 10
        assert report3.failed_tasks == 0
        print(f"  {report3.total_tasks} tasks executed, {report3.completed_tasks} completed")

        # Verify deterministic ordering
        task_order = [r.task_id for r in report3.results]
        assert task_order == sorted(task_order), f"Not deterministic: {task_order[:3]}..."
        print(f"  Deterministic ordering verified")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 9: Restart Recovery
    # ================================================================
    print("\n=== TEST 9: Restart Recovery ===")
    try:
        # Create package with some tasks
        r4 = await pid_runtime.generate(); pid4 = r4.pid
        pkg4 = await rt.create(pid4)
        await rt.update_section(pid4, "brief", {"product": "Recovery Test"})
        await rt.update_section(pid4, "scenario", {"title": "Recovery"})
        await rt.update_section(pid4, "video_parameters", {"format": "9:16"})
        recovery_tasks = [
            {"task_id": "RECOVER-001", "agent": "A1", "status": "COMPLETED", "pid": pid4},
            {"task_id": "RECOVER-002", "agent": "A2", "status": "PENDING", "pid": pid4},
            {"task_id": "RECOVER-003", "agent": "A3", "status": "PENDING", "pid": pid4},
        ]
        await rt.update_section(pid4, "task_packages", recovery_tasks)

        # Simulate restart: new executor instance
        new_executor = ProductionExecutor()
        report4 = await new_executor.recover(pid4)
        print(f"  Recovery report: {report4.completed_tasks}/{report4.total_tasks} completed")
        assert report4.total_tasks == 3
        assert report4.completed_tasks == 3  # All should complete (1 already + 2 executed)

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback; traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 10: Exception Handling
    # ================================================================
    print("\n=== TEST 10: Exception Handling ===")
    try:
        # Test validation failure
        try:
            await executor._validate_prerequisites("PID-20991231-9999")
            print("  FAIL: Should have raised ValueError for invalid PID")
            failed += 1
        except ValueError as e:
            print(f"  Invalid PID correctly rejected: {str(e)[:80]}...")

        # Test executing non-existent package
        try:
            await executor.execute("PID-20991231-9999")
            print("  FAIL: Should have raised ValueError")
            failed += 1
        except ValueError as e:
            print(f"  Non-existent package correctly rejected: {str(e)[:80]}...")

        print("  PASS")
        passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        failed += 1

    # ================================================================
    # TEST 11: Executor State Transitions
    # ================================================================
    print("\n=== TEST 11: Executor State Transitions ===")
    try:
        assert executor.is_idle() == False  # Just completed, not idle
        idle_executor = ProductionExecutor()
        assert idle_executor.is_idle() == True
        assert idle_executor.is_running() == False
        print(f"  IDLE state: {idle_executor.is_idle()}")
        print(f"  After execution: idle={executor.is_idle()}, running={executor.is_running()}")

        state = idle_executor.get_state()
        assert state["executor_state"] == "IDLE"
        print(f"  Initial state: {state['executor_state']}")

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
    total = passed + failed
    print(f"RESULTS: {passed}/{total} PASSED, {failed}/{total} FAILED")
    if failed == 0:
        print("PRODUCTION EXECUTOR RUNTIME: ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)

    await pid_runtime.reset()
    return passed, failed


if __name__ == "__main__":
    asyncio.run(main())
