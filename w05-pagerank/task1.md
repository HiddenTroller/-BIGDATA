# Task 1 · PageRank, and the Two Ways It Breaks

**File** — `task1_pagerank.py`
**Theory** — §5.1 PageRank, §5.1.3 dead ends, §5.1.4 spider traps
**Kind** — implementation · runs anywhere

---

## What you are building

A random surfer follows links forever; a page's rank is how often the surfer is
there. As linear algebra that is `r = M r`, and **as written it does not work on
the real web.**

Two structures break it, and one line fixes both. You build the broken version
too, so that you watch each failure rather than take it on trust.

| Structure | What goes wrong |
|---|---|
| **dead end** — a page with no out-links | rank drains out of the graph until everything is 0 |
| **spider trap** — pages that only link to each other | they absorb all the rank |

## Requirements

| # | Requirement |
|---|---|
| R1 | `pagerank(graph, beta, iterations, tol)` returns ranks summing to 1 |
| R2 | Dead ends handled: total rank is conserved |
| R3 | Spider traps handled: nodes outside the trap keep some rank |
| R4 | Stops early when the L1 change drops below `tol` |
| R5 | Sets `pagerank.iterations` to the number actually used — Task 2 reads it |
| R6 | `pagerank_no_teleport` implements the broken version, and really does fail |

R6 is not busywork. The harness checks that your broken version **drains to
near-zero** on the dead-end graph and that the trap **takes over 95%** on the
other. If your "broken" version quietly works, you have hidden the fix somewhere
and you will not understand what it was for.

## Pass condition

```bash
python3 task1_pagerank.py --verify
```

Seven checks, including both failures and both repairs.

```
  ok    without the fix, a dead end drains the graph     total rank 0.0000
  ok    with the fix, rank is conserved                  1.000000
  ok    without the fix, a spider trap takes everything  C+D = 1.0000
```

## What to write in `observation.md`

- Where does a dead end's rank go in the broken version, and where do you send it
  instead? Name the choice you made — there is more than one defensible answer
- The same fix repairs both problems. Say in one sentence why the same thing
  works for two failures that look different
- What does `beta` mean physically? What is the surfer doing with probability
  `1 - beta`?

## Task 1 답안

### 1. 과제의 목적과 구현한 함수

이 과제는 링크 구조로 페이지의 중요도를 계산하는 PageRank를 구현하고, 단순한 링크 이동만으로는 처리할 수 없는 dead end와 spider trap을 직접 비교하는 과제이다.

`pagerank(graph, beta, iterations, tol)`은 정상 버전이며 각 노드의 점수를 `{node: rank}` 형태로 반환한다. `pagerank_no_teleport(graph, iterations)`은 순간이동과 dead end 재분배를 의도적으로 생략한 비교용 버전이다. 고장 버전까지 구현한 이유는 보정의 효과를 말로만 설명하지 않고 실제 점수 변화로 확인하기 위해서이다.

입력 그래프는 `{"A": ["B", "C"], "B": ["C"], "C": []}`처럼 노드를 키로, 나가는 링크 목록을 값으로 갖는 인접 리스트이다. 이 구현은 링크의 목적지가 그래프의 키에 포함되고, 나가는 링크가 목록으로 제공되는 과제 입력을 전제로 한다.

### 2. 점수의 초기화와 링크를 통한 전달

노드 수를 n이라고 하면 모든 노드의 초기 점수를 `1/n`으로 설정한다. 초기 상태에서 어느 페이지가 더 중요한지 모른다고 가정하는 것이며 전체 점수 합은 1이다.

각 반복에서는 이전 점수 `ranks`를 읽어 새 점수 `updated`를 계산한다. 이전 사전을 계산 도중 수정하지 않으므로 모든 노드가 같은 단계의 점수를 기준으로 갱신된다.

노드 u의 나가는 링크가 k개이면 각 링크로 `beta * ranks[u] / k`를 전달한다. 예를 들어 점수가 0.4이고 링크가 2개이며 beta가 0.85이면 각 목적지에 0.17을 전달한다. 한 목적지에 여러 노드가 연결하면 전달받은 점수를 누적한다. 중요한 노드가 연결해 주는 노드에 더 큰 점수가 들어가는 구조이다.

### 3. Dead end: 점수가 사라지는 문제와 선택한 처리

Dead end는 나가는 링크가 없는 노드이다. 고장 버전은 링크가 있는 경우에만 점수를 전달하고 새 점수를 0에서 시작하므로, dead end가 갖고 있던 점수는 다음 단계에서 사라진다. 과제의 DEAD_END 예제에서는 모든 경로가 결국 링크가 없는 C에 도달하므로 전체 점수가 0으로 감소한다. 모든 dead end 포함 그래프가 반드시 전부 0이 되는 것은 아니며, 점수가 남을 수 있는 다른 닫힌 구조의 존재 여부에도 영향을 받는다.

정상 버전에서는 dead end들의 점수 합 `dangling_mass`를 구하고, 이를 모든 노드에 균등하게 재분배하는 방식을 선택했다. 링크를 따라가기로 했지만 이동할 링크가 없는 경우 전체 노드 중 하나를 임의로 선택한다고 해석한다. 각 노드가 받는 재분배 점수는 `beta * dangling_mass / n`이다. 이 처리로 기존 점수가 그래프 밖으로 유출되지 않는다.

### 4. Spider trap: 점수 독점과 순간이동

Spider trap은 내부 노드끼리만 연결되어 외부로 나갈 링크가 없는 집단이다. 과제의 SPIDER_TRAP 예제에서는 A→B→C로 들어간 뒤 C와 D 사이를 오가게 된다. 고장 버전에는 탈출 경로가 없으므로 반복 후 C와 D의 점수 합이 1이 된다.

정상 버전은 링크 이동 외에 균등 순간이동을 추가한다. 확률 `1-beta`로 전체 노드 중 하나를 선택하므로 trap 안에서도 바깥으로 이동할 가능성이 생긴다. 기본 beta=0.85의 검증에서 A의 점수는 약 0.0375, B는 약 0.0694로 남았고 C와 D가 전체 점수를 독점하지 않았다.

Dead end에서는 균등 재분배가 점수 보존을 담당하고, spider trap에서는 순간이동이 탈출 경로를 제공한다. 두 처리는 모두 전체 노드에 같은 값을 배분하는 형태이지만 코드에서는 서로 다른 항으로 계산한다.

### 5. Beta와 정상 버전의 갱신식

Beta는 사용자가 링크를 따라 이동할 확률이고, `1-beta`는 전체 페이지 중 하나를 균등 선택하여 순간이동할 확률이다. 기본값 0.85는 링크 이동 85%, 순간이동 15%라는 모델 가정을 뜻한다.

각 노드 v의 점수는 다음 식으로 갱신한다.

`r_new[v] = (1-beta)/n + beta*dangling_mass/n + beta*sum(r[u]/out_degree[u])`

마지막 합은 v로 연결되는 노드 u에 대해 계산한다.

| 항 | 의미 |
|---|---|
| `(1-beta)/n` | 모든 노드가 받는 균등 순간이동 점수 |
| `beta*dangling_mass/n` | dead end 점수의 균등 재분배 |
| `beta*sum(r[u]/out_degree[u])` | 링크를 통해 들어오는 점수 |

이전 전체 점수 합이 1이면 링크 이동과 dead end 재분배에서 합계 beta를 전달하고, 순간이동에서 합계 1-beta를 추가한다. 따라서 새 점수 합도 부동소수점 반올림 오차 범위에서 1이다. 별도로 합을 1로 맞추는 정규화로 오류를 숨기지 않고 전달 규칙 자체로 점수를 보존한다.

### 6. 수렴 조건과 반복 횟수

각 반복 후 모든 노드의 변화량을 합산한다.

`delta = sum(abs(updated[node] - ranks[node]) for node in graph)`

이는 연속된 두 점수 벡터의 L1 차이이다. `delta < tol`이면 점수가 충분히 안정되었다고 보고 조기 종료한다. 실제 수행한 횟수는 `pagerank.iterations`에 기록하여 Task 2에서 읽을 수 있도록 했다.

최대 반복 횟수에 도달하면 마지막 점수를 반환한다. 이 경우 반환되었다는 사실만으로 수렴했다고 판단할 수 없으며, tol은 연속 단계의 변화 기준이지 최종 정답과의 오차를 직접 나타내는 값은 아니다.

### 7. 검증 결과

`python task1_pagerank.py --verify`의 7개 검사를 모두 통과했다.

| 검사 | 확인한 결과 |
|---|---|
| 전체 점수 합 | 정상 버전에서 1 유지 |
| 노드 누락 | 입력의 모든 노드를 반환 |
| SIMPLE 예제 순위 | C가 A와 B보다 높은 점수 |
| DEAD_END 고장 버전 | 전체 점수 합 0 |
| DEAD_END 정상 버전 | 전체 점수 합 1 |
| SPIDER_TRAP 고장 버전 | C+D의 점수 합 1 |
| SPIDER_TRAP 정상 버전 | A와 B에도 점수 유지 |

조기 종료와 실제 반복 횟수 기록도 추가 확인했다. 상세 관찰은 `out/observation.md`의 Task 1에 정리했다.
