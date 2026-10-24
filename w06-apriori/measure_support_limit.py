import json,time,tracemalloc
from collections import Counter
from itertools import combinations
from pathlib import Path
namespace={}
exec(Path("measure_limits_extended.py").read_text(encoding="utf-8").split("# Prove")[0],namespace)
build=namespace["build"]
baskets=build(160000,16000)
out={"date":"2026-10-24","machine":{"cpu":"AMD Ryzen 7 9800X3D","ram_gib":32},"baskets":160000,"items":16000,"seed":246,"time_budget_seconds":30,"peak_budget_bytes":1073741824,"scope":"First/second pass counting only; excludes prebuilt input and final frozenset result materialisation. Checked every 100 baskets; partial counts are not answers.","runs":[]}
for support in [1600,800,400,200,100,50,25,12,6,3,1]:
 counts=Counter();pairs=Counter();tracemalloc.start();start=time.perf_counter()
 for b in baskets:counts.update(b)
 frequent={x for x,c in counts.items() if c>=support}
 reason=None
 for processed,b in enumerate(baskets,1):
  for pair in combinations(sorted(b & frequent),2):pairs[pair]+=1
  if processed%100==0:
   elapsed=time.perf_counter()-start
   if tracemalloc.get_traced_memory()[1]>=out["peak_budget_bytes"]:reason="python_peak_budget";break
   if elapsed>=out["time_budget_seconds"]:reason="algorithm_time_budget";break
 elapsed=time.perf_counter()-start;peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop()
 row={"support":support,"frequent_items":len(frequent),"processed":processed,"pair_counters":len(pairs),"seconds":elapsed,"peak_bytes":peak,"completed":reason is None,"stop_reason":reason or "completed"}
 if reason is None:row["frequent_pairs"]=sum(c>=support for c in pairs.values())
 out["runs"].append(row)
 Path("out/support_limit.json").write_text(json.dumps(out,indent=2),encoding="utf-8");print(row,flush=True)
 del counts,pairs,frequent
 if reason:break
