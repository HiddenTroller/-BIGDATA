# Task 3 · Same Memory, Fewer Mistakes

**Files** — `task3_budget.py` · harness `bench.py` (**do not edit the harness**)
**Theory** — §4.4.2
**Kind** — improvement · runs anywhere

---

## What you are given

`NaiveFilter` is a membership filter in a fixed number of bits. It works, and it
makes far more mistakes than it needs to with the memory it was handed.

You get **exactly the same bits**. Make fewer mistakes.

```bash
python3 bench.py
python3 bench.py --yours
```

```
  80,000 bits  ·  8,000 items inserted  ·  200,000 queried
```

Ten bits per item, and the harness tells you the item count before you start —
so there is no excuse for guessing.

**Where the baseline lands:**

```
  baseline   false positives  19,023  ( 9.511%)   false negatives     0   bits 80,000
```

One in ten queries comes back wrong.

## Requirements

| # | Requirement |
|---|---|
| R1 | `YourFilter(n_bits, seed)` with `add`, `__contains__`, `memory_bits()` |
| R2 | `bench.py` unmodified |
| R3 | `memory_bits()` ≤ the budget, and it must count **all** of your memory |
| R4 | **Zero false negatives** |
| R5 | Lower false-positive rate than the baseline |
| R6 | In `observation.md`: the theoretical minimum rate for 10 bits per item, and whether you reached it |

R4 is not negotiable. The entire value of this structure is that "no" means no.
A filter that scores better by occasionally forgetting something has not improved
anything, it has broken the contract.

R3 exists because counting only some of your memory is not an optimisation.

## Grading

| | Requirement |
|---|---|
| pass | R1–R5, more than 5% better |
| good | ≥ **50%** better |
| **strong** | false-positive rate ≤ **0.9%** |

The "strong" bar is set where it is for a reason: with m/n = 10 there is a
**floor**, and it is around 0.82%. You are being asked to reach the optimum, not
to beat it. §4.4.2 will tell you which parameter to set and what to set it to —
there is one derivative between you and the answer.

## The harder question, which is worth more than the grade

The harness tells you n before you start. **A real stream does not.**

You do not have to implement anything for this, but `observation.md` asks: what
would you do when you cannot know how many items are coming? Name what goes
wrong if you guess too low, and what you waste if you guess too high.

## What to write in `observation.md`

- Which parameter you changed and the value you chose, with the derivation
- R6: the floor for 10 bits per item, and how close you got
- What you would do if n were unknown

---

## 과제 답안

### R1·R2·R4 — 구현과 누락 방지

`task3_budget.py`의 YourFilter를 구현하고, 원본 NaiveFilter와 bench.py는 유지했다. 필터는 bytearray의 각 비트를 개별 위치로 사용하고, 7개의 해시 위치를 설정·조회한다. add()와 __contains__()가 동일한 해시 위치를 사용하고 비트를 지우지 않으므로 삽입한 원소는 누락되지 않는다.

NaiveFilter의 코드에서는 위치 하나를 bytearray의 한 바이트로 저장한다. 따라서 원본 memory_bits()가 보고하는 80,000비트는 실제 Python 객체의 물리 할당량과 다르다. 

### R3 — 메모리 예산

`__slots__`로 인스턴스 사전을 제거하고, 필터가 보유하는 객체를 필터 인스턴스·bytearray·seed 정수 세 개로 제한했다. 생성할 때 객체 헤더 비용을 먼저 제외해 배열 크기를 정하고, memory_bits()는 세 객체의 sys.getsizeof() 합계에 8을 곱한다.

이번 Windows/Python 실행 환경에서 보유 상태 전체는 80,000비트였고, 이 중 실제 비트 배열은 78,936비트였다. 이는 필터가 지속적으로 보유하는 메모리의 계산이며 공용 클래스·실행 코드와 일시적인 해시 계산 버퍼는 포함하지 않는다. 실행 중 peak 메모리 전체가 10KB 안이라는 의미는 아니다. 객체 헤더 크기가 다른 Python 환경에서는 비트 배열 길이와 측정 오탐률도 달라질 수 있다.

### R5·R6 — 최적 해시 수와 이론적 오탐률

Bloom 필터의 오탐률 근사는 다음과 같다.

```text
p(k) = (1 − exp(−kn/m))^k
a = n/m
d(log p)/dk = log(1 − exp(−ak)) + ak·exp(−ak)/(1 − exp(−ak))
```

이를 0으로 놓으면 최적점에서 exp(−ak)=1/2이고, k=(m/n)·ln 2이다. m/n=10일 때 k≈6.931이므로 정수 해시 개수는 7로 선택했다. 구현의 K=7은 이번 과제의 10비트/원소 조건에 맞춘 값이며 임의의 삽입 개수에 항상 최적인 값은 아니다.

연속 최적값의 이론적 오탐률은 다음과 같다.

```text
p_min = exp(−(m/n)·(ln 2)^2)
      = exp(−10·(ln 2)^2)
      ≈ 0.8193%
```

이는 해당 Bloom 필터 모형의 최적값으로, 모든 근사 membership 자료구조의 보편적인 하한이라는 의미는 아니다. 구현은 메타데이터를 제외한 m=78,936비트를 사용하므로 실제 m/n=9.867이며 k=7에 대한 예측값은 약 0.8740%이다.

### 성능 측정과 판정

삽입 원소 8,000개와 미삽입 조회 200,000개로, 수정하지 않은 bench.py를 실행했다.

| 필터 | false positive 수 | 오탐률 | false negative 수 | 보고된 메모리 |
|---|---:|---:|---:|---:|
| NaiveFilter | 19,023 | 9.511% | 0 | 80,000비트 |
| YourFilter | 1,770 | 0.885% | 0 | 80,000비트 |

기준 대비 오탐률 감소는 1−1,770/19,023≈90%이다. 측정 오탐률은 0.9% 이하이므로 strong 기준을 만족했다. 이상적인 0.8193%보다 약 0.0657%p 높으며, 실제 배열 크기에 따른 예측 0.8740%에 가까웠다. 차이는 메타데이터에 사용한 공간과 유한한 조회 표본의 변동으로 설명할 수 있다.

### 입력 개수 n을 알 수 없을 때

n을 너무 작게 예상하면 필터의 비트가 빠르게 포화되어 오탐률이 올라간다. n을 너무 크게 예상하면 필요한 것보다 많은 공간과 해시 계산을 사용한다.

비트 점유율을 관찰하고 필요할 때 새로운 Bloom 필터 층을 추가하는 scalable Bloom filter를 사용할 수 있다. 여러 층을 조회하면 전체 오탐률이 증가하므로 층별 오탐률 예산의 합을 목표 이하로 배분해야 한다. 원본 데이터의 재생이 가능하면 더 큰 필터로 재구성하는 방법도 있다. 엄격하게 고정된 메모리로 무한한 distinct 입력을 받으면서 일정한 오탐률을 영구히 유지할 수는 없다.

### 실행 및 검증

```bash
python3 bench.py --yours
python3 test_tasks.py --task 3
```

메모리 예산 검사, 누락 0건, 기준 대비 개선, 0.9% 기준을 만족했다. 전체 자동 검사 결과는 8개 통과·실패 0개이다.
