#!/usr/bin/env python3
"""Week 5 · Task 2 — How long does it take to converge, and on what?

Textbook §5.1, §5.2.

The textbook says PageRank converges. It does not say in how many iterations,
because the answer depends on beta, on the graph, and on what you are willing
to call "converged". Those three knobs are yours to turn, on your machine,
with a graph big enough that you can feel the cost.

    python3 task2_convergence.py --betas 0.5,0.7,0.85,0.95,0.99
    python3 task2_convergence.py --nodes 20000 --betas 0.85,0.95

Your timings are about your hardware. The iteration counts are not - those are
about the mathematics, and everybody should get the same ones.
"""
import argparse, json, os, platform, time, ctypes

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine():
    if platform.system() != "Windows":
        return {"platform": platform.platform(), "processor": platform.processor() or platform.machine(),
                "python": platform.python_version(), "ram_gib": None,
                "background": "Record RAM and concurrent applications manually on this platform"}
    import winreg
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
    cpu = winreg.QueryValueEx(key, "ProcessorNameString")[0]
    winreg.CloseKey(key)
    total = ctypes.c_ulonglong()
    if not ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(total)):
        raise OSError("Cannot read installed RAM")
    return {"cpu": cpu.strip(), "ram_gib": total.value / 1024**2,
            "background": "Codex/ChatGPT, Microsoft Edge, Explorer, Windows TiWorker observed; background load is not controlled",
            "platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "python": platform.python_version()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--betas", default="0.5,0.7,0.85,0.95,0.99")
    p.add_argument("--nodes", type=int, default=None,
                   help="graph size; default is the harness graph")
    p.add_argument("--tol", type=float, default=1e-10)
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)

    import bench
    if a.nodes:
        bench.NODES = a.nodes
    graph = bench.build()

    from task1_pagerank import pagerank

    rows = []
    for beta in [float(x) for x in a.betas.split(",")]:
        t0 = time.perf_counter()
        ranks = pagerank(graph, beta=beta, iterations=10000, tol=a.tol)
        elapsed = time.perf_counter() - t0
        iters = getattr(pagerank, "iterations", None)
        top = sorted(ranks.items(), key=lambda kv: -kv[1])[:10]
        rows.append({"beta": beta, "nodes": len(graph), "tol": a.tol,
                     "iterations": iters, "seconds": elapsed,
                     "top10": [k for k, _ in top], "iteration_limit": 10000,
                     "hit_iteration_limit": iters == 10000})
        print(f"  beta {beta:<5}  {str(iters):>4} iterations  {elapsed:>7.3f}s   "
              f"top: {', '.join(k for k, _ in top[:3])}")

    path = os.path.join(OUT, "convergence.json")
    prior = json.load(open(path)) if os.path.exists(path) else {"runs": []}
    prior["machine"] = machine()
    prior["runs"].extend(rows)
    json.dump(prior, open(path, "w"), indent=2)
    print(f"\n  -> out/convergence.json  ({len(prior['runs'])} run(s))")


if __name__ == "__main__":
    main()

