import json, time, platform
from pathlib import Path
import bench
from task3_fewer import NaiveKMeans, YourKMeans
source=Path("task3_fewer.py").read_text(encoding="utf-8")
points,initial=bench.build()
out={"date":"2026-10-24","machine":{"cpu":"AMD Ryzen 7 9800X3D","ram_gib":32},"python":platform.python_version(),"method":"Full, lower only, and separation only; same input, initial centroids and tie rules. Counts include centre separation and movement calls."}
reference=None
for name,kind in [("baseline","baseline"),("full","full"),("lower_only","lower"),("separation_only","separation")]:
 if kind=="baseline": cls=NaiveKMeans
 elif kind=="full": cls=YourKMeans
 else:
  modified=source
  if kind=="lower":
   modified=modified.replace("if self.iterations > 1:", "if False:") 
   modified=modified.replace("threshold = max(lower[i], separation[old])","threshold = lower[i]")
  else:
   modified=modified.replace("threshold = max(lower[i], separation[old])","threshold = separation[old]")
  ns={};exec(compile(modified,name,"exec"),ns);cls=ns["YourKMeans"]
 distance=bench.Distance();algo=cls(bench.K);start=time.perf_counter()
 labels,centres=algo.run(points,initial,distance)
 row={"calls":distance.calls,"seconds":time.perf_counter()-start,"iterations":algo.iterations,"sse":bench.sse(points,labels,centres)}
 if reference is None: reference=(labels,centres)
 row["exact_labels_and_centres"]=(labels,centres)==reference
 assert row["exact_labels_and_centres"]
 out[name]=row
 print(name,row,flush=True)
Path("out/ablation.json").write_text(json.dumps(out,indent=2),encoding="utf-8")


