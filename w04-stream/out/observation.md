# Week 4 observations

## Task 1
Bloom insertion only sets bits, and lookup checks the same deterministic positions: without deletion, every inserted item remains present. Predicted FP 0.860%, measured 0.840%; finite query sampling accounts for the small difference.
FM combines mean log2 maxima within eight groups, then takes the median and divides by a fixed 1.26 calibration (approximate, not fitted per input). On the verification stream: raw arithmetic mean 79,328 (3.98x), raw median 16,384 (0.82x), grouped estimate 14,808 (0.742x), truth 19,953; exponential outliers spoil the raw mean. This is a maximum-trailing-zero estimator, not HyperLogLog.
Reservoir Algorithm R uses j=randrange(i+1) and replaces only when j<k. A new item enters with probability k/(i+1); each retained prior item survives with probability i/(i+1). Induction gives every position k/n without knowing n and using at most k stored items.

## Task 2
At 25,000,000 items exact counting took 43.18s and 744.74 MB; time made interactive repetition unpleasant, while RAM remained sufficient. This is a practical stopping point, not a measured OOM boundary.
Measured endpoint growth exponents: exact 0.950 (approximately linear), FM 0.0000 (constant in stream length). See limits.md for all sizes, environment, memory scope, and accuracy ratios.
A factor of two is acceptable for rough capacity planning or order-of-magnitude visitor counts; it is unacceptable for billing, precise daily-active-user reporting, or detecting a 5% change.

## Task 3
For p(k)=(1-exp(-kn/m))^k, differentiating log p gives optimum exp(-kn/m)=1/2, hence k=(m/n)ln 2=6.931 and integer k=7. The continuous Bloom optimum at ten bits/item is exp(-10*(ln 2)^2)=0.8193%; this is the Bloom-family optimum, not a universal lower bound for all approximate membership structures.
Observed FP is 1,770/200,000=0.885%, versus baseline 9.511%: 90.7% fewer mistakes, zero false negatives, strong grade. All owned persistent object headers, packed bytes, and seed occupy 80,000 bits; 78,936 bits hold membership data. Metadata reduces effective m/n to 9.867, giving a k=7 prediction of about 0.8740%. Shared executable code and temporary hash workspace are outside persistent filter state; peak execution memory is not claimed to fit 10 KB. bench.py is unchanged.
If n is unknown, monitor occupancy and use a scalable Bloom filter with additional layers and a summable error budget, or rebuild from a replayable source. Guessing n too low saturates bits and raises false positives; guessing too high wastes memory and hash work. With a hard fixed budget and an unbounded stream, a constant FP target cannot be maintained indefinitely without dropping history.
