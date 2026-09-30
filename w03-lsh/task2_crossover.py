#!/usr/bin/env python3
"""Week 3 · Task 2 — Find the crossover on your own machine.

Textbook §3.4. The timing results depend on your machine; run this script at
several sizes and record where brute force stops being usable.

    python3 task2_crossover.py --sizes 250,500,1000,2000
    python3 task2_crossover.py --sizes 4000,8000 --activity "browser and IDE open"
"""
import argparse, ctypes, json, os, platform, time, tracemalloc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def total_memory_bytes():
    """Return installed physical RAM without requiring a third-party package."""
    if hasattr(os, "sysconf"):
        try:
            return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        except (OSError, ValueError):
            pass

    if platform.system() == "Windows":
        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return status.ullTotalPhys
    return None


def machine(activity):
    return {
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "physical_memory_bytes": total_memory_bytes(),
        "python": platform.python_version(),
        "other_activity": activity,
    }


def timed(fn, *args):
    """Return result, wall time, and peak traced Python allocation."""
    tracemalloc.start()
    try:
        t0 = time.perf_counter()
        result = fn(*args)
        elapsed = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        return result, elapsed, peak
    finally:
        tracemalloc.stop()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", default="250,500,1000,2000",
                   help="comma-separated document counts to try")
    p.add_argument("--threshold", type=float, default=0.6)
    p.add_argument("--activity", default="not recorded",
                   help="other notable apps/work running during this measurement")
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)

    import bench
    from task3_scale import BruteForce
    try:
        from task3_scale import YourFinder
    except Exception:
        YourFinder = None

    rows = []
    for n in [int(x) for x in a.sizes.split(",")]:
        docs = bench.build()[:n]
        sim = bench.Counter()
        _, t_brute, m_brute = timed(BruteForce(a.threshold).find, docs, sim)
        c_brute = sim.calls

        row = {"n": n, "brute_s": t_brute, "brute_calls": c_brute,
               "brute_peak_bytes": m_brute}

        if YourFinder is not None:
            sim2 = bench.Counter()
            try:
                _, t_lsh, m_lsh = timed(YourFinder(a.threshold).find, docs, sim2)
                row.update({"lsh_s": t_lsh, "lsh_calls": sim2.calls,
                            "lsh_peak_bytes": m_lsh})
            except NotImplementedError:
                pass

        rows.append(row)
        line = f"  n={n:>6}  brute {t_brute:>8.2f}s  {c_brute:>12,} cmp"
        if "lsh_s" in row:
            line += f"   |  lsh {row['lsh_s']:>7.2f}s  {row['lsh_calls']:>9,} cmp"
        print(line)

    path = os.path.join(OUT, "crossover.json")
    prior = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"runs": []}
    prior["machine"] = machine(a.activity)
    prior["runs"].extend(rows)
    with open(path, "w", encoding="utf-8") as output:
        json.dump(prior, output, indent=2)
    print(f"\n  -> out/crossover.json  ({len(prior['runs'])} measurement(s))")
    print(f"  RAM: {prior['machine']['physical_memory_bytes']} bytes; "
          f"other activity: {a.activity}")
    print("  Keep raising --sizes until something becomes unpleasant. Record where.")


if __name__ == "__main__":
    main()
