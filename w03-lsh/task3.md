# Task 3 · Find the Same Pairs, Comparing Far Less

**Files** — `task3_scale.py` · harness `bench.py` (**do not edit the harness**)
**Theory** — §3.4
**Kind** — improvement · synthetic data, runs anywhere

---

## What you are given

`BruteForce` compares every pair. On the harness's 2,120 documents that is
2.2 million comparisons, and it is completely correct. On 3 million documents
it is 4.5 trillion, and it is completely useless.

```bash
python3 bench.py            # baseline, about 6 seconds
python3 bench.py --yours
```

The documents are synthetic with a fixed seed and **120 near-duplicate pairs
planted in them**, so the ground truth is known and everyone's numbers compare.

**Where the baseline lands:**

```
  baseline     comparisons  2,246,140   recall 100.0%   precision 100.0%     5.62s
```

## How you are scored

The harness counts every call to `similarity()`. That is your score. Signatures,
banding and bucketing are **not** charged — which is deliberate, and roughly true
at scale, where comparison is the expensive part and hashing is linear.

It also measures **recall**: how many of the truly similar pairs you found.
Skipping comparisons is trivial. Skipping comparisons without losing pairs is
the task.

## Requirements

| # | Requirement |
|---|---|
| R1 | `YourFinder(threshold)` with `find(docs, similarity)` returning `{(i, j), ...}` |
| R2 | `bench.py` unmodified |
| R3 | **Recall at least 90%.** Below that nothing else counts |
| R4 | Fewer comparisons than the baseline |
| R5 | In `observation.md`: your choice of hash count and band count, **with the arithmetic from §3.4.2 that justifies it** |

## Grading

| | Requirement |
|---|---|
| pass | R1–R4, more than 50% avoided |
| good | ≥ **95%** avoided |
| **strong** | ≥ **99%** avoided **and** recall ≥ 95% |

All three are reachable — a reasonable banding gets above 99.9% with full recall.
The failure mode is not being too slow, it is choosing bands badly and quietly
losing half the pairs. The harness will tell you; `recall` is the first number
to read.

## R5 · the arithmetic, not the guess

For a signature of `n` hashes split into `b` bands of `r = n/b` rows, a pair at
similarity `s` becomes a candidate with probability

```
    1 - (1 - s^r)^b
```

That is an S-curve, and its step sits near `(1/b)^(1/r)`. The threshold here is
**0.6**. Pick `n` and `b` so the step lands where you want it, then say in
`observation.md` what step you were aiming for and why — above the threshold, or
below it, and what each choice costs you.

Answering "I tried 120 hashes and 30 bands and it worked" is a pass. Answering
with the step you computed is the point of the task.

## What to write in `observation.md`

- Your `n` and `b`, the step they put the S-curve at, and why there
- What happened to recall when you moved the step the wrong way — try it
- The harness does not charge you for hashing. At what scale would that stop
  being a fair simplification?

---

## 과제 답안

### R1–R4 — 구현과 평가 결과

원래 `YourFinder(threshold)`와 `find(docs, similarity)` 선언을 유지하고 미구현 부분에만 코드를 채웠다.
MinHash와 banding으로 후보를 얻은 후 전달받은 `similarity()`로 최종 판정한다. 결과는 i<j인 쌍의 set이며 각 후보는 한 번만 비교한다.

원본 `bench.py`를 그대로 실행한 결과:

| 항목 | BruteForce | YourFinder |
|---|---:|---:|
| 문서 수 | 2,120 | 2,120 |
| 실제 유사 쌍 수 | 121 | 121 |
| similarity 호출 수 | 2,246,140 | 125 |
| Recall | 100% | 100% |
| Precision | 100% | 100% |
| 실행 시간 | 6.34초 | 0.48초 |

비교 감소율은 1−125/2,246,140=99.9944%다. Recall≥95%, 비교 감소≥99%인 `strong` 조건을 만족한다.
120개의 복제 문서가 심어졌지만 실제 유사 쌍은 121개였다. 같은 원본에서 파생된 복제 문서끼리도 유사할 수 있으므로 ground truth의 실제 쌍 수를 기준으로 평가했다.
전체 실행 출력은 요구된 `out/bench.txt`에 기록했다.

### R5 — 해시와 band 선택의 계산

n_hash=120, b=30, r=120/30=4로 선택했다.

```text
step ≈ (1/b)^(1/r) = (1/30)^(1/4) = 0.4273
P(candidate | s=0.6) = 1−(1−0.6^4)^30 = 0.984456 ≈ 98.45%
```

step을 판정 threshold 0.6보다 낮게 잡아 유사 쌍의 누락을 줄였다. 낮은 step은 후보 수와 비교 비용을 늘리는 대가를 치르지만 이번 데이터에서는 비교 125회로 충분했다.
후보 확률은 독립적인 이상적 MinHash를 가정한 값이다. 사용한 선형 해시는 실용적 근사이므로 실제 recall도 확인했다.

### step을 잘못 옮긴 실험과 관찰

같은 120개 해시에서 band 수만 10으로 바꾸면 r=12, step=(1/10)^(1/12)=0.8254가 된다.
이때 s=0.6의 후보 확률은 1−(1−0.6^12)^10=2.1556%다. 동일 데이터 실험에서 121쌍 중 36쌍만 찾아 recall이 29.75%로 떨어졌다.
이 실험은 `finder = YourFinder(0.6)` 이후 `finder.bands = 10`으로 band 설정만 바꿔 재현할 수 있다.

평가 점수에서 해시 비용을 제외하더라도 작은 데이터에서는 해시 준비 비용이 전수 비교보다 클 수 있다.
문서·어휘·signature 또는 bucket이 커지면 해시 계산·메모리·후보 생성 비용도 중요해지므로 실제 실행 시간과 메모리를 함께 봐야 한다.
과제별 2–3줄 관찰 기록은 `out/observation.md`에 작성했다.
