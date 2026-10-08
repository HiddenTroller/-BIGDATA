# Task 2 · How Long Does It Take to Converge, and on What?

**File** — `task2_convergence.py`
**Theory** — §5.1, §5.2
**Kind** — **measurement. Timings are about your machine; iteration counts are not.**

---

## Why this task exists

The textbook says PageRank converges. It does not say in how many iterations,
because that depends on `beta`, on the graph, and on what you call "converged".

This task turns those three knobs and writes down what happens.

## What to do

```bash
python3 task2_convergence.py --betas 0.5,0.7,0.85,0.95,0.99
python3 task2_convergence.py --nodes 20000 --betas 0.85,0.95
python3 task2_convergence.py --tol 1e-6 --betas 0.85
```

| # | Requirement |
|---|---|
| A1 | At least **five** values of beta, spanning 0.5 to 0.99 |
| A2 | Tabulate iterations against beta → `out/convergence.md` |
| A3 | Describe the shape. What happens as beta approaches 1, and **why** |
| A4 | At least two graph sizes, at least 5× apart. Does the **iteration count** change with size? Does the **time**? Those are different questions |
| A5 | Two tolerances at least 1e-4 apart. How many extra iterations does each extra digit cost? |
| A6 | Does the **top-10 ranking** change as beta changes? At which beta does it first change? |
| A7 | Your machine: CPU, RAM, what else was running |

A4 is the one worth thinking about before you run it. Predict the answer for
both halves first, then check. One of them will surprise you.

A6 is the practically important one. If the ranking is stable across beta, then
beta is a tuning detail. If it is not, then somebody chose 0.85 and that choice
is in every result.

## Pass condition

`out/convergence.json` has five or more betas with your machine recorded, and
`out/convergence.md` answers A3–A6.

```bash
python3 test_tasks.py --task 2
```

## What to write in `observation.md`

- What happens to the iteration count as beta → 1, and the reason
- A4: which of iteration count and wall time grew with graph size, and why they differ
- A6: whether the top 10 moved, and what that means for trusting a published ranking

## 과제 수행 결과

### 1. 측정의 목적

PageRank가 수렴한다는 사실과 실제로 몇 번 반복해야 하는지는 다른 문제이다. 이 실험은 beta, 그래프 크기, 허용 오차를 바꾸어 반복 횟수와 실행 시간을 각각 비교하고, beta 선택이 최종 상위 10개 순서에도 영향을 주는지 확인한다.

`task2_convergence.py`는 Task 1의 `pagerank`를 호출하고 `pagerank.iterations`에서 실제 반복 횟수를 읽는다. 시간은 `time.perf_counter()`로 함수 실행 전후의 차이를 측정하며 그래프 생성 시간은 포함하지 않는다. 상위 10개는 점수 내림차순으로 정렬하여 기록한다.

### 2. A1·A2: 실험 조건과 결과 파일

| 조건 | 사용한 값 |
|---|---|
| 고정 seed | 246 |
| beta | 0.5, 0.7, 0.85, 0.95, 0.99 |
| 노드 수 | 1,200 및 20,000 |
| tol | 1e-3, 1e-4, 1e-6, 1e-8, 1e-10 |
| 최대 반복 횟수 | 실행당 10,000회 |
| 실험 수 | 5×2×5 = 50회 |

기존 측정 코드의 반복 한도를 500회에서 10,000회로 늘리고, 결과에 한도 도달 여부를 기록하도록 했다. 이번 50회는 모두 한도 이전에 수렴했다. 고정 seed는 같은 조건의 그래프를 재현하기 위한 설정이며, 크기가 다르면 생성되는 그래프도 달라진다.

원시 측정값과 환경은 `out/convergence.json`, 전체 측정 표와 분석은 `out/convergence.md`에 저장했다. JSON에는 기존 실행에 이어 결과가 추가되므로 재측정 시에는 이전 실험과 새 실험을 구분해야 한다.

### 3. A3: beta가 1에 가까워질 때

노드 1,200개, tol=1e-10에서 beta를 0.5→0.7→0.85→0.95→0.99로 늘렸을 때 반복 횟수는 14→17→20→23→24회였다.

Beta가 커지면 순간이동 확률이 줄어 링크를 통한 이전 분포의 영향이 더 오래 남는다. PageRank 갱신은 beta<1에서 L1 차이를 줄이는 수축 성질을 가지며, beta가 클수록 보장되는 수축이 약해진다. 따라서 대체로 더 많은 반복이 필요하다. 실제 수렴 속도에는 그래프 구조도 영향을 주므로 beta만으로 정확한 반복 횟수를 결정할 수는 없다.

### 4. A4: 크기와 시간은 같은 방식으로 증가하는가

노드 수는 약 16.67배 늘렸다. tol=1e-10에서 크기 변경 전후의 반복 횟수는 beta별로 14→14, 17→18, 20→21, 23→24, 24→25회였다. 노드 수에 비례하는 증가는 없었다.

반면 beta=0.85의 함수 실행 시간은 0.009652초에서 0.191569초로 약 19.85배 증가했다. 수렴에 필요한 반복 수가 비슷해도, 한 번 반복할 때 순회할 노드와 링크 수가 커지기 때문이다.

측정 전에는 반복 횟수가 크기에 직접 비례하지 않고 시간은 늘어날 것으로 예상했고 결과는 이 예상과 부합했다. 다만 그래프 생성기가 크기에 따라 구조를 바꾸고 dead end 수를 12개로 유지하므로, 크기 이외의 구조적 효과도 함께 포함된 비교이다.

### 5. A5: 허용 오차와 추가 반복 비용

1e-3과 1e-10은 절대 차이가 1e-4 이상이므로 과제 조건을 만족한다. 정확도 자릿수별 비용은 beta=0.85에서 1e-4→1e-6→1e-8→1e-10을 비교했다.

| 노드 수 | tol 순서별 반복 횟수 | 두 자리 추가 시 증가량 | 한 자리당 평균 증가량 |
|---:|---|---|---|
| 1,200 | 9, 12, 16, 20 | 3, 4, 4회 | 1.5, 2.0, 2.0회 |
| 20,000 | 9, 12, 17, 21 | 3, 5, 4회 | 1.5, 2.5, 2.0회 |

허용 오차를 더 엄격하게 하면 추가 반복이 필요했다. 오차가 대략 기하급수적으로 줄어드는 구간에서는 자릿수 증가에 따른 반복 비용이 비교적 비슷하다. 이 수치는 연속된 점수 벡터의 변화 기준을 엄격하게 만든 비용이며, 최종 정답의 소수 자릿수를 직접 보증하는 값은 아니다.

### 6. A6: 상위 10개 순위 변화

tol=1e-10에서 두 그래프 모두 측정한 beta 중 0.7에서 처음 상위 10개 순서가 달라졌다. beta=0.5에서는 p00000이 p00004보다 앞섰고, beta=0.7에서는 둘의 순서가 바뀌었다. 이 실험에서 상위 10개에 포함되는 노드 집합은 같았고 순서가 달라졌다.

0.5와 0.7 사이의 값을 추가로 측정하지 않았으므로 정확한 순위 교차 지점이 0.7이라고 단정할 수는 없다. 확인한 것은 측정 지점 중 최초 변화가 0.7이라는 사실이다.

이 결과는 beta 선택이 단순히 계산 시간만 바꾸는 것이 아니라 순위 해석에도 영향을 줄 수 있음을 보여 준다. 순위를 발표할 때 beta, 수렴 기준과 사용한 그래프를 함께 밝혀야 결과를 비교할 수 있다.

### 7. A7: 환경과 측정 한계

측정 환경은 AMD Ryzen 5 7500F 6-Core Processor, RAM 32.0 GiB, Python 3.12.14, Windows 11이었다. ChatGPT/Codex, Edge, Explorer, Windows TiWorker가 실행 중인 것으로 관찰됐으며 작업 부하는 통제하지 않았다.

각 조건의 시간은 1회 측정이므로 운영체제 스케줄링이나 백그라운드 작업에 따른 변동이 있을 수 있다. 반복 횟수는 주로 그래프·알고리즘·설정에 좌우되고, 시간은 하드웨어와 실행 환경에도 좌우된다. CPU와 RAM은 Windows 환경에서 자동 기록하며 다른 플랫폼에서는 RAM과 동시 실행 프로그램 정보를 수동으로 보완해야 한다.

`python test_tasks.py --task 2`에서 실험 조건과 필수 결과 파일에 대한 검사를 통과했다.
