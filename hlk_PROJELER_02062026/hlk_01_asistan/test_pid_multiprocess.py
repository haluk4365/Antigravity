"""PID Runtime Multi-Process Test — cross-worker duplicate prevention."""
import asyncio
import multiprocessing
import sys
from pathlib import Path

# Ensure project root in path
sys.path.insert(0, str(Path(__file__).resolve().parent))


def worker_process(worker_id: int, rounds: int, result_queue: multiprocessing.Queue):
    """Multi-process worker — each runs in its own Python process."""
    from services.pid_runtime import PIDRuntime

    async def work():
        rt = PIDRuntime()
        pids = []
        for i in range(rounds):
            r = await rt.generate()
            pids.append((r.pid, r.sequence))
        return pids

    pids = asyncio.run(work())
    result_queue.put((worker_id, pids))


def hscale_worker(worker_id: int, rounds: int, result_queue: multiprocessing.Queue):
    """Horizontal scaling worker — simulates workers joining at different times."""
    import asyncio
    from services.pid_runtime import PIDRuntime

    async def work():
        rt = PIDRuntime()
        pids = []
        for i in range(rounds):
            r = await rt.generate()
            pids.append((r.pid, r.sequence))
            await asyncio.sleep(0.001)
        return pids

    pids = asyncio.run(work())
    result_queue.put((worker_id, pids))


def main():
    from services.pid_runtime import _PID_STATE_FILE, _PID_LOCK_PATH
    from services.pid_runtime import pid_runtime

    # Cleanup
    async def cleanup():
        await pid_runtime.reset()

    asyncio.run(cleanup())

    passed = 0
    failed = 0

    # ================================================================
    # TEST 1: Multi Process — 4 workers x 5 rounds
    # ================================================================
    print("=== TEST 1: Multi Process (4 workers x 5 rounds) ===")
    try:
        n_workers = 4
        rounds_per_worker = 5
        result_queue = multiprocessing.Queue()
        processes = []
        for w in range(n_workers):
            p = multiprocessing.Process(
                target=worker_process, args=(w, rounds_per_worker, result_queue)
            )
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        all_pids = []
        while True:
            try:
                wid, pids = result_queue.get_nowait()
                all_pids.extend([p[0] for p in pids])
                seqs = [p[1] for p in pids]
                print(f"  Worker {wid}: PIDs={[p[0] for p in pids]} seqs={seqs}")
            except Exception:
                break

        total = n_workers * rounds_per_worker
        unique = len(set(all_pids))
        if unique == total:
            print(f"  PASS: {total} PIDs, {unique} unique — NO DUPLICATES")
            passed += 1
        else:
            print(f"  FAIL: {total} PIDs, {unique} unique — {total - unique} DUPLICATES!")
            failed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        failed += 1

    # ================================================================
    # TEST 2: Horizontal Scaling — 2 batches of 3 workers
    # ================================================================
    print("\n=== TEST 2: Horizontal Scaling (2 batches) ===")
    try:
        asyncio.run(cleanup())

        # First batch
        q1 = multiprocessing.Queue()
        procs1 = []
        for w in range(3):
            p = multiprocessing.Process(target=hscale_worker, args=(w, 3, q1))
            procs1.append(p)
            p.start()
        for p in procs1:
            p.join()

        batch1_pids = []
        while True:
            try:
                wid, pids = q1.get_nowait()
                batch1_pids.extend([p[0] for p in pids])
                print(f"  Batch1 Worker {wid}: {[p[0] for p in pids]}")
            except Exception:
                break

        # Second batch
        q2 = multiprocessing.Queue()
        procs2 = []
        for w in range(3, 6):
            p = multiprocessing.Process(target=hscale_worker, args=(w, 3, q2))
            procs2.append(p)
            p.start()
        for p in procs2:
            p.join()

        batch2_pids = []
        while True:
            try:
                wid, pids = q2.get_nowait()
                batch2_pids.extend([p[0] for p in pids])
                print(f"  Batch2 Worker {wid}: {[p[0] for p in pids]}")
            except Exception:
                break

        all_pids = batch1_pids + batch2_pids
        total = 18  # 6 workers x 3 rounds
        unique = len(set(all_pids))
        if unique == total:
            print(f"  PASS: {total} PIDs across 2 batches, {unique} unique")
            passed += 1
        else:
            print(f"  FAIL: {total} PIDs, {unique} unique — DUPLICATES across batches!")
            failed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        failed += 1

    # ================================================================
    # SUMMARY
    # ================================================================
    print()
    print("=" * 60)
    print(f"MULTI-PROCESS RESULTS: {passed} PASSED, {failed} FAILED")
    if failed == 0:
        print("CROSS-WORKER PID UNIQUENESS: VERIFIED")
    print("=" * 60)
    return passed, failed


if __name__ == "__main__":
    main()
