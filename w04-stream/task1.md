# Task 1 · Answer Questions About a Stream You Cannot Store

**File** — `task1_sketches.py`
**Theory** — §4.3 sampling, §4.4 Bloom filters, §4.5 counting distinct elements
**Kind** — implementation · runs anywhere, no data needed

---

## What you are building

Three structures, each trading an exact answer for a bounded amount of space.
The job is not to get them working. It is to know **exactly what you traded**.

| | Question | Method |
|---|---|---|
| `BloomFilter` | have I seen this before? | §4.4 |
| `flajolet_martin` | how many *distinct* things went past? | §4.5 |
| `reservoir_sample` | give me k of them, uniformly | §4.3 |

## Requirements

| # | Requirement |
|---|---|
| R1 | The Bloom filter **never** has a false negative. Not rarely — never |
| R2 | `expected_fp_rate(n)` returns the §4.4.2 prediction, computed not measured |
| R3 | The measured false-positive rate matches that prediction |
| R4 | `flajolet_martin` lands within **a factor of two** of the true distinct count |
| R5 | `reservoir_sample` is uniform: every item has probability k/n, and you hold only k |
| R6 | One pass. None of these may store the stream |

R1 and R3 together are the real test. R1 is structural — if you ever have a false
negative, you built something else. R3 says your understanding of *why* it works
is good enough to predict its error rate before measuring it.

## About R4 and the factor of two

That tolerance is not generous, it is honest. Flajolet-Martin really is that
crude, and HyperLogLog exists because of it.

How you combine many hashes matters a great deal:

- averaging `2^R` directly is dominated by whichever hash got lucky — the values
  are exponential, so one outlier swamps everything
- the median is robust but can only ever be a power of two
- §4.5.3 suggests grouping and combining twice

Try more than one and look at what happens. Landing inside a factor of two
*reliably* is the requirement; getting closer is not expected.

## Pass condition

```bash
python3 task1_sketches.py --verify
```

Four checks: no false negatives, predicted rate matches measured, distinct
estimate within 2×, reservoir uniform across 4,000 trials.

## What to write in `observation.md`

- Why can a Bloom filter never have a false negative? One sentence, structural
- Your predicted and measured false-positive rates. If they differ, say why
- Which combining rule you used for Flajolet-Martin, and what the others gave you
- Reservoir sampling holds k items but has to be correct for a stream whose
  length it never learns. Where in your code does that actually happen?

---

## 과제 답안

### R1–R3 — Bloom 필터 구현과 오탐률

`task1_sketches.py`의 미구현 함수를 구현했다. Bloom 필터는 m개의 비트를 bytearray에 압축해서 저장하고, seed와 입력으로부터 결정되는 k개의 해시 위치를 사용한다. 삽입은 해당 비트를 1로 설정하며 조회는 같은 위치가 모두 1인지 확인한다. 비트를 지우지 않으므로 삽입한 원소에는 false negative가 발생하지 않는다.

삽입한 서로 다른 원소 수를 n이라 할 때 이론적 오탐률은 다음과 같다.

```text
p ≈ (1 − exp(−kn/m))^k
```

`expected_fp_rate(n)`는 측정 결과 대신 이 식을 계산한다. m=8,192, k=5, n=800에서 예측 오탐률은 0.860%, 미삽입 원소 20,000개에 대한 측정 오탐률은 0.840%였다. 유한한 표본과 해시 충돌의 변동으로 두 값에 작은 차이가 발생하며 검증 기준을 만족했다.

### R4 — Flajolet–Martin과 추정값 결합

각 입력을 64비트 값으로 해시하고, seed로 생성한 64개의 salt와 혼합해 각 해시의 trailing zero 최댓값 R을 유지한다. 처리 속도를 위해 NumPy로 최대 256개씩 처리하지만 배치 크기는 고정되어 전체 스트림을 저장하지 않는다.

64개 R을 8개 그룹으로 나누어 그룹별 R의 평균을 구하고, 그 평균들의 중앙값을 지수로 사용한다. 이는 그룹 내에서는 2^R의 기하평균, 그룹 간에는 중앙값을 사용하는 방식이다. 마지막으로 고정된 근사 보정 계수 1.26으로 나눈다. 이 계수는 입력별 실제 정답에 맞춰 조정하지 않으며, 추정 정확도를 보장하는 상수로 해석하지 않는다.

| 결합 방식 | 추정값 | 실제 distinct 수 대비 |
|---|---:|---:|
| 2^R의 산술평균 | 79,328 | 약 3.98배 |
| 2^R의 중앙값 | 16,384 | 약 0.82배 |
| 구현한 그룹 결합 및 보정 | 약 14,808 | 약 0.742배 |
| 실제 distinct 수 | 19,953 | 1.00배 |

산술평균은 지수적으로 큰 이상값에 영향을 받아 과대 추정했다. 구현한 방법은 검증 데이터에서 실제 값의 0.5–2배 범위를 만족했다. 추가로 distinct 수 100, 1,000, 10,000 및 seed 0, 1, 246의 9개 조합에서도 약 0.740–1.253배였다. 이는 실험 결과이며 모든 스트림에서 같은 오차를 보장하는 것은 아니다.

### R5–R6 — Reservoir sampling의 균등성과 공간

처음 k개를 저장하고, 이후 0부터 시작하는 위치 i의 원소에 대해 `j = rng.randrange(i + 1)`를 뽑는다. j<k이면 sample[j]를 새 원소로 교체한다. 따라서 새 원소는 k/(i+1)의 확률로 들어오고, 기존 표본의 각 원소는 i/(i+1)의 확률로 남는다. 이를 반복하면 길이 n의 스트림에서 각 위치의 최종 포함 확률은 k/n이다. n을 미리 알 필요가 없고, n<k이면 전체 n개를 반환한다.

4,000회 검증에서 각 위치의 기대 선택 횟수는 1,000회였고 최대·최소 횟수 차이는 기대값의 8.9%로 허용 기준 15% 미만이었다. Bloom 필터는 O(m) 비트, FM은 고정 배치 크기 B=256에 대해 O(B·h) 작업 공간(h는 해시 수), reservoir는 O(k)개의 원소를 사용한다. 세 구현 모두 입력을 한 번 순회하며 전체 스트림을 저장하지 않는다.

### 실행 및 결과

```bash
python3 task1_sketches.py --verify
```

네 검증 모두 통과했다. 기존 verify 검증 로직은 수정하지 않았다. 상세 기록은 [out/tests.txt](out/tests.txt), 서술 답안은 [out/observation.md](out/observation.md)에 있다.
