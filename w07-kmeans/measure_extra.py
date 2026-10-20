"""Record exact pruning validation and point-count sensitivity."""
import contextlib
import io
import json
import random
import time
from pathlib import Path

import bench
from task1_kmeans import BLOBS, kmeans
from task2_curse import sample_distances
from task3_fewer import NaiveKMeans, YourKMeans

OUT = Path(__file__).parent / 'out'


def main():
    OUT.mkdir(exist_ok=True)
    # Compare every count, not just the benchmark's SSE tolerance.
    points, initial = bench.build()
    data = {}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        base = bench.run(NaiveKMeans, 'baseline', points, initial)
        mine = bench.run(YourKMeans, 'yours', points, initial)
    assert base['sse'] == mine['sse']
    data['benchmark'] = {'baseline': base, 'yours': mine,
                         'first_iteration_calls': len(points) * bench.K}
    (OUT / 'bench.txt').write_text(buf.getvalue() + f"\nDistance reduction: {1-mine['calls']/base['calls']:.6%}\nSSE difference: {mine['sse']-base['sse']}\n", encoding='utf-8')
    rng = random.Random(246)
    cases = [([(0.,), (0.,), (1.,), (1.,)], [(0.,), (0.,), (1.,)]),
             ([(-1.,), (0.,), (1.,)], [(-1.,), (1.,)])]
    for _ in range(60):
        n, dim, k = rng.randrange(8, 50), rng.randrange(1, 6), rng.randrange(1, 6)
        pts = [tuple(float(rng.randrange(-4, 5)) for _ in range(dim)) for _ in range(n)]
        cases.append((pts, rng.sample(pts, k)))
    for pts, cents in cases:
        a = NaiveKMeans(len(cents)).run(pts, cents, bench.Distance())
        b = YourKMeans(len(cents)).run(pts, cents, bench.Distance())
        assert a == b, (a, b)
    data['exact_randomized_and_tie_cases'] = len(cases)
    data['initialization'] = {}
    for init in ('random', '++'):
        sses = [kmeans(BLOBS, 3, init=init, seed=seed)[2] for seed in range(40)]
        data['initialization'][init] = {'successes': sum(s < 1 for s in sses),
                                         'mean_sse': sum(sses)/40, 'min_sse': min(sses),
                                         'max_sse': max(sses)}
    # All pairs at fixed d: unlike a fixed 20,000-pair sample, this sees the
    # full extremes and isolates the role of population size.
    data['exhaustive_n_runs'] = []
    for n in (50, 200, 600):
        rng = random.Random(246)
        pts = [tuple(rng.random() for _ in range(50)) for _ in range(n)]
        start = time.perf_counter()
        lo, hi, count = float('inf'), 0., 0
        from task2_curse import euclid
        for i in range(n):
            for j in range(i):
                d = euclid(pts[i], pts[j])
                lo, hi, count = min(lo, d), max(hi, d), count + 1
        data['exhaustive_n_runs'].append({'points': n, 'dim': 50, 'pairs': count,
                                         'min': lo, 'max': hi, 'contrast': (hi-lo)/lo,
                                         'seconds': time.perf_counter()-start})
    (OUT / 'extra.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
    print('Exact pruning, initialization and exhaustive point-count checks passed', flush=True)


if __name__ == '__main__':
    main()
