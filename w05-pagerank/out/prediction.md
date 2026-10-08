# Task 2 측정 전 예상

아래 영어 문장은 실험을 실행하기 전에 기록한 예상의 원문이다. 이번 문서 보완에서는 원문을 보존하고 한국어 해설을 추가했다.

> Before measurement: larger graphs should cost more time per iteration; iteration count depends mainly on beta and graph mixing, not directly on node count. Stricter tolerance should require more iterations.

## 예상의 의미

- **그래프 크기와 시간:** 노드와 링크가 많아지면 한 번 반복할 때 방문할 항목이 늘어나므로 실행 시간이 증가할 것으로 예상했다.
- **그래프 크기와 반복 횟수:** 수렴에 필요한 반복 횟수는 노드 수 자체보다 beta와 점수가 그래프 전체로 퍼지는 구조에 더 큰 영향을 받을 것으로 예상했다. 노드 수가 늘어나는 비율과 반복 횟수 증가 비율이 같을 것이라고 가정하지 않았다.
- **허용 오차:** 더 작은 변화까지 기다리도록 tol을 줄이면 추가 반복이 필요할 것으로 예상했다.

## 측정 후 확인

이 부분은 측정 이후의 해석이다. 노드 수를 약 16.67배 늘렸을 때 beta=0.85, tol=1e-10의 반복 횟수는 20→21회, 시간은 약 19.85배로 증가했다. 허용 오차를 엄격하게 만들수록 반복 횟수도 증가하여 예상과 부합했다.

크기에 따라 생성 그래프 구조도 바뀌므로 크기 효과만을 완전히 분리한 실험은 아니다. 상세 값과 분석은 `convergence.md`에서 확인할 수 있다.
