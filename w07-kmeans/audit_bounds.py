import json, time, platform
from pathlib import Path
import bench
from task3_fewer import NaiveKMeans, YourKMeans
src=Path("task3_fewer.py").read_text(encoding="utf-8")
src=src.replace("self.bound_skips = 0", 'self.bound_skips = 0\n        self.stats = {"before": {"lower_only":0,"separation_only":0,"both":0}, "after": {"lower_only":0,"separation_only":0,"both":0}}')
src=src.replace("self.bound_skips += 1\n                        continue",'''self.bound_skips += 1
                        phase = "before" if not tightened else "after"
                        lo = upper[i] + 1e-10 < lower[i]
                        sep = upper[i] + 1e-10 < separation[old]
                        key = "both" if lo and sep else "lower_only" if lo else "separation_only"
                        self.stats[phase][key] += 1
                        continue''')
src=src.replace("threshold = max(lower[i], separation[old])","tightened = False\n                    threshold = max(lower[i], separation[old])")
src=src.replace("upper[i] = distance(point, centroids[old])","upper[i] = distance(point, centroids[old])\n                    tightened = True")
ns={}
exec(compile(src,"instrumented_task3_fewer.py","exec"),ns)
points,initial=bench.build()
result={"date":"2026-10-24","python":platform.python_version(),"cpu":"AMD Ryzen 7 9800X3D"}
outputs=[]
for name,cls in [("baseline",NaiveKMeans),("original",YourKMeans),("instrumented",ns["YourKMeans"])]:
 d=bench.Distance(); algo=cls(bench.K); start=time.perf_counter()
 labels,centres=algo.run(points,initial,d)
 row={"calls":d.calls,"seconds":time.perf_counter()-start,"iterations":algo.iterations,"sse":bench.sse(points,labels,centres)}
 if hasattr(algo,"stats"): row["skip_stats"]=algo.stats
 result[name]=row
 outputs.append((labels,centres))
 print(name,row,flush=True)
assert outputs[0]==outputs[1]==outputs[2]
assert result["original"]["calls"]==result["instrumented"]["calls"]
result["exact_labels_and_centres"]=True
Path("bound_audit.json").write_text(json.dumps(result,indent=2),encoding="utf-8")


