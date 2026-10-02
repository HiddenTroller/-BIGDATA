| n | distinct | exact seconds | exact MB | FM seconds | FM MB | estimate/truth |
|---:|---:|---:|---:|---:|---:|---:|
| 100,000 | 36,702 | 0.147 | 3.926 | 0.446 | 0.610 | 1.1412 |
| 400,000 | 146,970 | 0.611 | 11.591 | 1.834 | 0.610 | 1.0453 |
| 1,600,000 | 587,625 | 2.573 | 46.648 | 7.390 | 0.610 | 1.0014 |
| 6,400,000 | 2,349,909 | 11.074 | 188.288 | 29.446 | 0.610 | 1.0017 |
| 25,000,000 | 9,179,304 | 43.182 | 744.743 | 117.513 | 0.610 | 1.0257 |

Machine: AMD Ryzen 7 9800X3D 8-Core Processor; 31.11 GiB RAM; Windows 11; Python 3.12.14. Other applications running: Codex/ChatGPT, Discord, Chrome, Windows Explorer.

A2: At 25,000,000 items, exact counting took 43.18 seconds and 744.74 MB. Tens of seconds per interactive query is unpleasant; time was the stopping constraint. The 31.11 GiB machine did NOT run out of RAM. No OOM threshold was measured or claimed. FM took 117.51 seconds: bounded space is not automatically faster.

A4: Across 250x input growth, exact peak grew 189.71x (endpoint exponent 0.950, approximately O(n), with set resizing steps); FM grew 1.0000x (exponent 0.0000, approximately O(1) in n). Exact space is O(distinct); FM space is O(number of hashes * fixed batch size).

A5: Ratios in the table are measured, not corrected using the true count. Accuracy is not guaranteed to improve with n; these particular measurements happen to be close at larger sizes. FM keeps only 64 maxima and a fixed 256-item batch; it never stores the full stream.

Method: seed 246, distinct span floor(0.4*n), one pass per method, perf_counter wall time, tracemalloc peak bytes. NumPy is imported before tracing both methods. Peaks measure traced Python/NumPy allocations and stream-generator state, not total process RSS, all loaded modules, or physical RAM use. A fixed batch improves throughput at a constant ~0.61 MB working-memory cost. These are real local measurements from the user's Windows host.
