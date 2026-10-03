# Task 2 · Find the Size Where Exact Stops Being Possible

**File** — `task2_limits.py`
**Theory** — §4.1 the stream model, §4.5
**Kind** — **measurement. The number is about your machine, and nobody else's.**

---

## Why this task exists

"The exact answer does not fit" is easy to agree with and hard to feel. This task
makes you watch it happen: hold every distinct item in a `set`, raise the stream
size, and find where your own laptop stops coping.

You cannot look this number up and an agent cannot produce it for you. It depends
on your RAM, your Python, and what else you have open.

## What to do

```bash
python3 task2_limits.py --sizes 100000,400000,1600000
python3 task2_limits.py --sizes 6400000
python3 task2_limits.py --sizes 25000000        # if you dare
```

Each run records, for both the exact `set` and your Flajolet-Martin from Task 1:
wall time, peak memory, and the estimate's ratio to the truth.

| # | Requirement |
|---|---|
| A1 | At least **four** stream sizes, spanning a 16× range or more |
| A2 | Go until the exact version is genuinely unpleasant. **Record that size and what ran out — time or memory** |
| A3 | Tabulate memory against n for both methods → `out/limits.md` |
| A4 | The exact set's memory grows with n. Flajolet-Martin's does not. Confirm that from **your own numbers**, and give both growth rates |
| A5 | Report FM's accuracy ratio at each size. Does it get better or worse as n grows? |
| A6 | State your machine: CPU, RAM, what else was running |

A4 is the whole lesson in one measurement. One line goes up and the other is
flat, and you should be able to say roughly *how* flat — FM's memory is set by
the number of hashes, not by the data.

A5 is the honest counterweight: you did not get the flat line for free.

## The estimate is bad, and that is a result

FM lands within a factor of two, not within a few percent. If your ratios wander
between 0.6× and 1.7×, that is the method behaving normally. Report what you got
rather than the number you wanted, and say in `observation.md` whether a factor
of two is good enough for the question "how many distinct users visited today".

## Pass condition

`out/limits.json` has four or more sizes with your machine recorded, and
`out/limits.md` answers A2–A6.

```bash
python3 test_tasks.py --task 2
```

## If your machine is small

That is a finding. A laptop that cannot get past 2 million items tells you
something precise about constant factors. "I stopped at X because Y" with the
evidence is a complete answer.

## What to write in `observation.md`

- The size where exact became unbearable, and whether time or memory gave out first
- The two growth rates from A4
- Is a factor of two good enough for "how many distinct users visited today"?
  Give a case where it is and a case where it is not

---

## 과제 답안

### A1·A3 — 스트림 크기별 측정 결과

2026-10-02에 사용자 Windows PC에서 직접 실행한 결과다. seed=246, distinct 값의 범위는 floor(0.4·n)이며 정확한 set과 Task 1의 FM에 같은 스트림을 각각 한 번씩 공급했다. 5개 크기를 측정했고 최대/최소 입력 비율은 250배로, 4개 이상·16배 이상 조건을 만족했다. 아래 MB는 1,000,000바이트 기준이다.

| 스트림 길이 n | 실제 distinct 수 | set 시간(s) | set peak(MB) | FM 시간(s) | FM peak(MB) | FM 추정/실제 |
|---:|---:|---:|---:|---:|---:|---:|
| 100,000 | 36,702 | 0.147 | 3.926 | 0.446 | 0.610 | 1.1412 |
| 400,000 | 146,970 | 0.611 | 11.591 | 1.834 | 0.610 | 1.0453 |
| 1,600,000 | 587,625 | 2.573 | 46.648 | 7.390 | 0.610 | 1.0014 |
| 6,400,000 | 2,349,909 | 11.074 | 188.288 | 29.446 | 0.610 | 1.0017 |
| 25,000,000 | 9,179,304 | 43.182 | 744.743 | 117.513 | 0.610 | 1.0257 |

원시 측정값은 [out/limits.json](out/limits.json), 표와 분석은 [out/limits.md](out/limits.md)에 있다.

### A2 — 중단 지점과 제약

2,500만 개에서 정확한 set 계산은 43.18초, peak 메모리는 744.74MB였다. 반복적인 대화형 조회마다 수십 초를 기다리는 실용적인 시간 부담을 중단 이유로 기록했다. RAM이 부족하거나 프로그램이 실패한 것은 아니며, 물리적인 메모리 한계나 OOM 발생 지점을 측정한 결과로 주장하지 않는다. 이 PC에서 메모리 부족이 발생하는 최대 입력 크기는 이번 실험으로 알 수 없다.

FM은 같은 입력에서 117.51초가 걸렸다. 메모리를 일정하게 유지하는 것과 계산 속도가 빠른 것은 별개의 조건이며, 이 구현에서는 여러 해시의 연산 비용 때문에 set보다 느렸다.

### A4 — 메모리 증가율

입력은 250배 증가했고 정확한 set의 peak 메모리는 약 189.71배 증가했다. 두 끝점으로 구한 증가 지수는 다음과 같다.

```text
α = log(M_last / M_first) / log(n_last / n_first)
set: α ≈ 0.950
FM:  α ≈ 0.0000
```

set은 서로 다른 원소를 모두 보관하므로 O(distinct) 공간이 필요하고, 이번처럼 distinct 수가 n에 비례하면 대략 O(n)이다. set의 재할당과 고정 비용 때문에 측정치가 완전히 직선은 아니다.

FM은 64개 최댓값과 고정 크기 배치만 보관하므로 n에 대한 공간은 O(1)이다. 실제 peak도 모든 크기에서 약 0.61MB였다. 해시 수 h와 배치 크기 B를 변경하면 작업 공간 O(B·h)가 달라지므로 모든 설정에서 같은 메모리를 쓰는 것은 아니다.

### A5 — 정확도와 활용 가능성

추정/실제 비율은 1.1412, 1.0453, 1.0014, 1.0017, 1.0257이었다. 이번 입력에서는 큰 크기의 비율이 1에 가까웠지만, 증가에 따라 항상 정확해지는 것은 아니며 마지막 크기에서는 오차가 다시 커졌다. FM의 정확도는 해시 결과와 결합 방식의 변동에 영향을 받는다.

하루 방문자의 대략적인 규모나 자원 수요를 파악하는 데에는 2배 범위 추정이 유용할 수 있다. 사용자 수를 기준으로 한 과금, 정확한 DAU 보고, 5% 수준 변화 감지에는 충분하지 않다.

### A6 — 측정 환경과 측정 범위

- CPU: AMD Ryzen 7 9800X3D 8-Core Processor
- RAM: 33,408,483,328바이트, 약 31.11GiB의 보고된 총 물리 메모리
- OS/Python: Windows 11, Python 3.12.14
- 당시 실행 중인 앱: Codex/ChatGPT, Discord, Chrome, Windows Explorer

CPU와 RAM을 기록하기 위해 원본 machine()에 Windows 조회를 추가했다. 앱 목록은 당시 프로세스를 확인한 뒤 직접 기록한 값이며 자동 감지 기능은 아니다. FM 측정 전에 빈 스트림 호출로 NumPy를 미리 import해 일회성 모듈 로딩 비용을 제외했다. 원본 스트림 생성과 exact_distinct() 계산은 유지했다.

시간은 perf_counter, 메모리는 tracemalloc의 peak이다. 추적되는 Python/NumPy 할당 및 스트림 생성기의 작업 공간을 포함하지만, 프로세스 전체 RSS나 물리 RAM 사용량과 같지는 않다. Codespaces나 Colab에서 재실행하면 해당 서버의 측정값이므로 이 PC 결과와 구분해야 한다.

### 실행 및 검증

```bash
python3 task2_limits.py --sizes 100000,400000,1600000,6400000
python3 task2_limits.py --sizes 25000000
python3 test_tasks.py --task 2
```

Task 2 자동 검증의 크기 수, 범위, 환경 기록, limits.md 존재 확인은 모두 통과했다. A2–A6의 해석은 이 답안과 limits.md에 서술했다.
