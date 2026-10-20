"""Additional reproducible PCY memory and SON measurements (standard library)."""
import contextlib
import ctypes
import importlib.util
import io
import json
import os
import platform
import sys
import time
import tracemalloc
from pathlib import Path

import bench
from task1_apriori import BASKETS, association_rules, frequent_singletons
from task3_pcy import PlainApriori, YourAlgorithm
from task4_son import chunked, son_pass_one, son_pass_two

OUT = Path(__file__).parent / 'out'


def machine_details():
    details = {'platform': platform.platform(), 'python': platform.python_version(),
               'processor': os.environ.get('PROCESSOR_IDENTIFIER', platform.processor()),
               'background': 'Codex and its sandbox shell; other host applications are not visible from the sandbox.'}
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            details['cpu_name'] = winreg.QueryValueEx(key, 'ProcessorNameString')[0]
    except OSError:
        details['cpu_name'] = 'unavailable from sandbox'
    class Status(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
            (name, ctypes.c_ulonglong) for name in
            ('total_phys', 'available_phys', 'total_page', 'available_page',
             'total_virtual', 'available_virtual', 'extended_virtual')]
    try:
        status = Status()
        status.length = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            details['ram_bytes'] = status.total_phys
            details['available_ram_bytes'] = status.available_phys
    except (AttributeError, OSError):
        details['ram_bytes'] = None
    return details


def measured(cls, baskets, support=50, **kwargs):
    algo = cls(support, **kwargs)
    tracemalloc.start()
    start = time.perf_counter()
    answer = algo.run(baskets)
    elapsed = time.perf_counter() - start
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return {'seconds': elapsed, 'peak_bytes': peak, 'pair_counters': algo.peak_counters,
            'answer_count': len(answer)}, answer


def main():
    OUT.mkdir(exist_ok=True)
    data = {'machine': machine_details(), 'memory_runs': [], 'bucket_runs': [], 'son_runs': []}
    baskets = bench.build()
    for size in (200, 1000, 5000, 20000):
        base, truth = measured(PlainApriori, baskets[:size])
        mine, found = measured(YourAlgorithm, baskets[:size])
        assert found == truth
        data['memory_runs'].append({'baskets': size, 'baseline': base, 'pcy': mine})
        print('memory', size, base['peak_bytes'], mine['peak_bytes'], flush=True)
    truth = PlainApriori(50).run(baskets)
    for buckets in (1009, 100003, 1000003):
        stats, found = measured(YourAlgorithm, baskets, buckets=buckets)
        assert found == truth
        data['bucket_runs'].append({'buckets': buckets, **stats})
    for chunks in (3, 8, 16):
        start = time.perf_counter()
        candidates = son_pass_one(chunked(baskets, chunks), 50, len(baskets))
        found = son_pass_two(baskets, candidates, 50)
        assert found == truth
        data['son_runs'].append({'chunks': chunks, 'candidates': len(candidates),
                                 'pairs': len(found), 'missing': 0, 'extra': 0,
                                 'seconds': time.perf_counter() - start})
    data['spark_available'] = bool(importlib.util.find_spec('pyspark'))
    data['rules'] = association_rules(BASKETS, 3, 0)
    data['benchmark_frequent_items'] = len(frequent_singletons(baskets, 50))
    (OUT / 'extra.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        base = bench.run(PlainApriori, 'baseline', baskets)
        mine = bench.run(YourAlgorithm, 'yours', baskets, base['pairs'])
    assert mine['pairs'] == base['pairs']
    (OUT / 'bench.txt').write_text(buf.getvalue() + f"\nPeak counter reduction: {1-mine['peak']/base['peak']:.6%}\n", encoding='utf-8')
    print('Additional measurements complete', flush=True)


if __name__ == '__main__':
    main()
