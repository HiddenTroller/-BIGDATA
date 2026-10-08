# 과제 1 · MinHash와 LSH 구현

### R1–R4 — 구현 및 검증

`task1_minhash.py`의 미구현 함수에 Jaccard, MinHash signature, LSH 후보 생성 코드를 작성했다.
빈 합집합의 Jaccard는 0이다. 행별 membership을 구성한 후 각 행의 해시를 한 번 계산해 해당 열의 최솟값을 갱신하므로 열마다 행렬 전체를 재탐색하지 않는다.
signature 길이가 h, 문서 수가 c, 행렬의 1인 항목 수가 nnz라면 signature 메모리는 O(c·h), 추가 sparse membership 메모리는 O(nnz)이다.
교재의 signature는 S1=[1,0], S2=[3,2], S3=[0,0], S4=[1,0]으로 모두 재현했다.
LSH는 하나 이상의 band에서 동일한 tuple을 갖는 문서 쌍을 수집하며 i<j와 중복 제거를 보장한다.

### R5 — 남은 signature 행의 처리

signature 길이가 band 수로 나누어떨어지지 않으면 `ValueError`를 발생시킨다.
일부 해시를 버리거나 길이가 다른 band를 만들지 않아 모든 band의 행 수 r을 일정하게 유지하고 후보 확률식을 같은 조건에서 적용한다.

### 관찰

행의 해시 값을 관련 열 모두에 재사용하면 같은 행에 대해 문서마다 해시를 다시 계산할 필요가 없다.
S1–S4는 해시 2개에서 추정값 1.0, 실제 Jaccard 2/3으로 차이가 난다. 해시 수를 늘리면 표본 추정의 분산이 줄지만 계산 시간과 signature 저장 공간이 증가한다.
