#!/usr/bin/env python3
"""Week 3 · Task 2 — Find the crossover on your own machine.

Textbook §3.4.

Everybody knows brute force is quadratic and LSH is not. That is not the
interesting question. The interesting question is **where, on the machine in
front of you, does it start to matter** - and that answer is yours alone. It
depends on your CPU, your memory, and how big your shingle sets are.

This script gives you the timing loop. The two methods are yours: import them
from Task 1 and Task 3.

    python3 task2_crossover.py --sizes 500,1000,2000,4000
    python3 task2_crossover.py --sizes 8000,16000          # keep going

Write down where it hurts. That is the deliverable.
"""
import argparse, ctypes, datetime, json, os, platform, random, time, tracemalloc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine(background="not recorded"):
    info = {
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "python": platform.python_version(),
        "logical_processors": os.cpu_count(),
        "background": background,
    }
    if os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
                info["processor"] = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        except OSError:
            pass

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
                (name, ctypes.c_ulonglong) for name in
                ("total_phys", "avail_phys", "total_page", "avail_page",
                 "total_virtual", "avail_virtual", "avail_extended")]

        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            info["ram_bytes"] = status.total_phys
            info["available_ram_bytes"] = status.avail_phys
    else:
        try:
            info["ram_bytes"] = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        except (ValueError, OSError, AttributeError):
            pass
    return info


def timed(fn, *args):
    """Wall time and peak memory of one call."""
    owns_trace = not tracemalloc.is_tracing()
    if owns_trace:
        tracemalloc.start()
    tracemalloc.reset_peak()
    try:
        t0 = time.perf_counter()
        result = fn(*args)
        elapsed = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        return result, elapsed, peak
    finally:
        if owns_trace:
            tracemalloc.stop()


def build_documents(n, seed=246):
    """Generate exactly n documents; bench.build() is capped at 2,120.

    Same 60-shingle/5,000-vocabulary distribution, with about 6% near copies.
    The seed and generation rule are identical for both measured methods.
    """
    import bench
    rng = random.Random(seed)
    docs = []
    for _ in range(n):
        if docs and rng.random() < 0.06:
            clone = set(docs[rng.randrange(len(docs))])
            for _ in range(rng.randint(4, 14)):
                clone.discard(rng.choice(tuple(clone)))
                clone.add(rng.randrange(bench.VOCAB))
            docs.append(clone)
        else:
            docs.append(set(rng.sample(range(bench.VOCAB), bench.SHINGLES)))
    return docs


def measure(finder_class, n, threshold):
    import bench
    # Trace BEFORE data generation so each method's peak includes its input.
    # Wall time measures find() only, matching the original timing contract.
    tracemalloc.start()
    try:
        docs = build_documents(n)
        sim = bench.Counter()
        found, elapsed, peak = timed(finder_class(threshold).find, docs, sim)
        return {"s": elapsed, "calls": sim.calls, "peak_bytes": peak,
                "found": len(found), "actual_n": len(docs)}
    finally:
        tracemalloc.stop()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", default="250,500,1000,2000",
                   help="comma-separated document counts to try")
    p.add_argument("--threshold", type=float, default=0.6)
    p.add_argument("--background", default="not recorded",
                   help="applications running during this measurement")
    a = p.parse_args()
    sizes = [int(x) for x in a.sizes.split(",")]
    if any(n <= 0 for n in sizes):
        p.error("sizes must be positive integers")
    if not 0 <= a.threshold <= 1:
        p.error("threshold must be between 0 and 1")
    os.makedirs(OUT, exist_ok=True)

    from task3_scale import BruteForce, YourFinder
    path = os.path.join(OUT, "crossover.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as stream:
            prior = json.load(stream)
    else:
        prior = {"runs": []}
    current_machine = machine(a.background)
    prior["machine"] = current_machine
    prior["memory_metric"] = "tracemalloc peak Python allocations including input; not process RSS"
    for n in sizes:
        print(f"  measuring n={n:,} (both methods; memory tracing enabled)", flush=True)
        brute = measure(BruteForce, n, a.threshold)
        lsh = measure(YourFinder, n, a.threshold)
        t_brute, c_brute = brute["s"], brute["calls"]
        row = {"n": n, "actual_n": brute["actual_n"],
               "threshold": a.threshold, "seed": 246,
               "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "machine": current_machine, "unpleasant": t_brute >= 60 or lsh["s"] >= 60}
        for label, result in (("brute", brute), ("lsh", lsh)):
            for key in ("s", "calls", "peak_bytes", "found"):
                row[f"{label}_{key}"] = result[key]
        prior["runs"].append(row)
        # Save each completed size, so an interrupted larger run loses no data.
        temporary = path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as stream:
            json.dump(prior, stream, indent=2)
        os.replace(temporary, path)
        line = f"  n={n:>6}  brute {t_brute:>8.2f}s  {c_brute:>12,} cmp"
        line += f"   |  lsh {row['lsh_s']:>7.2f}s  {row['lsh_calls']:>9,} cmp"
        print(line, flush=True)
    print(f"\n  -> out/crossover.json  ({len(prior['runs'])} measurement(s))")
    print("  Keep raising --sizes until something becomes unpleasant. Record where.")


if __name__ == "__main__":
    main()
