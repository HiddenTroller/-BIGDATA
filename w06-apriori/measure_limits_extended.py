import json, time, tracemalloc, random, platform
from pathlib import Path
from itertools import combinations
from collections import Counter
import bench
TIME_LIMIT=30.0
MEMORY_LIMIT=1024*1024*1024
def build(n,items):
 rng=random.Random(246)
 weights=[1/(i+1)**0.8 for i in range(items)]
 cumulative=[];total=0
 for w in weights: total+=w;cumulative.append(total)
 planted=[(rng.randrange(300),rng.randrange(300)) for _ in range(25)]
 planted=[(a,b) for a,b in planted if a!=b]
 baskets=[]
 for _ in range(n):
  k=max(2,int(rng.gauss(20,4)))
  basket=set(rng.choices(range(items),cum_weights=cumulative,k=k))
  if rng.random()<0.08:basket.update(rng.choice(planted))
  baskets.append(basket)
 return baskets
# Prove the faster generator preserves the original fixed input.
assert build(20000,2000)==bench.build()
results={"date":"2026-10-24","python":platform.python_version(),"machine":{"cpu":"AMD Ryzen 7 9800X3D","ram_gib":32},"limits":{"algorithm_seconds":TIME_LIMIT,"python_peak_bytes":MEMORY_LIMIT},"measurement":"Input excluded from tracemalloc; first and second passes included. Limits checked each 100 baskets. A stopped run has partial counters, not final frequent-pair answers. No physical OOM is attempted.","runs":[]}
for n,items,support in [(20000,2000,1),(40000,4000,1),(80000,8000,1),(160000,16000,1)]:
 g=time.perf_counter();baskets=build(n,items);generation=time.perf_counter()-g
 counts=Counter();pairs=Counter();processed=0;reason=None
 tracemalloc.start();start=time.perf_counter()
 for basket in baskets: counts.update(basket)
 frequent={x for x,c in counts.items() if c>=support}
 for processed,basket in enumerate(baskets,1):
  for pair in combinations(sorted(basket & frequent),2):pairs[pair]+=1
  if processed%100==0:
   current,peak=tracemalloc.get_traced_memory()
   elapsed=time.perf_counter()-start
   if peak>=MEMORY_LIMIT: reason="python_peak_budget";break
   if elapsed>=TIME_LIMIT: reason="algorithm_time_budget";break
 elapsed=time.perf_counter()-start;current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
 row={"baskets":n,"items":items,"support":support,"generation_seconds":generation,"algorithm_seconds":elapsed,"second_pass_processed":processed,"pair_counters":len(pairs),"peak_bytes":peak,"completed":reason is None,"stop_reason":reason or "completed"}
 if reason is None:row["frequent_pairs"]=sum(c>=support for c in pairs.values())
 results["runs"].append(row);print(row,flush=True)
 Path("out/limits_extended.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
 del baskets,counts,pairs,frequent
 if reason:break


