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

- **Dead end:** 고장 버전에서는 나가는 링크가 없는 노드의 점수를 다음 반복에 전달하지 않으므로 전체 점수 합이 감소하여 0이 된다. 정상 버전에서는 해당 점수 합을 모든 노드에 균등 재분배한다.
- **두 문제의 해결:** 이동할 곳이 없을 때의 균등 재분배는 점수 유출을 막고, 매 단계의 균등 순간이동은 spider trap 밖으로도 이동할 확률을 제공한다.
- **beta:** 링크를 따라 이동할 확률이다. 확률 `1 - beta`로 전체 노드 중 하나를 균등 선택하여 순간이동한다.
- **수렴과 반복 횟수:** 새 점수와 이전 점수의 L1 차이(절댓값 차이의 합)가 `tol`보다 작으면 종료하며, 수행한 횟수는 `pagerank.iterations`에 기록한다. 최대 반복 횟수에 도달하면 마지막 점수를 반환한다.

정상 버전의 갱신식은 각 노드 v에 대해 다음과 같다.

`r_new[v] = (1 - beta)/n + beta * dangling_mass/n + beta * sum(r[u]/out_degree[u])`

마지막 합은 v로 연결되는 노드 u에 대해 계산한다. 각 항은 각각 균등 순간이동, dead-end 점수 재분배, 링크를 통한 유입을 뜻한다.
