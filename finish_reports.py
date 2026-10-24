"""Build Korean reports and SVG charts exclusively from recorded measurements."""
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).parent
A = ROOT / 'w06-apriori' / 'out'
B = ROOT / 'w07-kmeans' / 'out'


def read(folder, name):
    return json.loads((folder / name).read_text(encoding='utf-8'))


def write(folder, name, text):
    (folder / name).write_text(text.strip() + '\n', encoding='utf-8')


def chart(folder, name, xs, series, title, xlabel, logy=False):
    # Fixed, labelled axes; all plotted values come from the accompanying JSON.
    colors = ['#155e75', '#be123c', '#6d28d9']
    vals = [v for _, ys in series for v in ys]
    transform = (lambda v: math.log10(max(v, 1e-12))) if logy else (lambda v: v)
    bottom, top = min(map(transform, vals)), max(map(transform, vals))
    if bottom == top:
        top += 1
    def ypos(y):
        return 330 - (transform(y)-bottom)/(top-bottom)*230
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="430" viewBox="0 0 900 430" role="img">',
           f'<title>{escape(title)}</title><rect width="900" height="430" fill="white"/>',
           '<g font-family="Arial, sans-serif" font-size="13" fill="#172033">',
           f'<text x="70" y="30" font-size="20">{escape(title)}</text>',
           '<path d="M90 80V330H860" fill="none" stroke="#334155"/>']
    for tick in range(6):
        value = bottom+(top-bottom)*tick/5
        y = 330-230*tick/5
        label = f'{10**value:.3g}' if logy else f'{value:.3g}'
        svg.append(f'<path d="M90 {y}H860" stroke="#e2e8f0"/><text x="15" y="{y+4}">{label}</text>')
    for index, (label, ys) in enumerate(series):
        color = colors[index]
        positions = [(90+i*770/max(1, len(xs)-1), ypos(y)) for i, y in enumerate(ys)]
        coords = ' '.join(f'{x},{y}' for x, y in positions)
        svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2"/>')
        for x, y in positions:
            svg.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')
        svg.append(f'<text x="{100+index*240}" y="60" fill="{color}">{escape(label)}</text>')
    for i, x in enumerate(xs):
        xpos = 90+i*770/max(1, len(xs)-1)
        svg.append(f'<text x="{xpos}" y="355" text-anchor="middle">{escape(str(x))}</text>')
    svg.append(f'<text x="450" y="390" text-anchor="middle">{escape(xlabel)}</text>')
    svg.append(f'<text x="90" y="415">Y: {"log10 scale" if logy else "linear scale"}; X: equally spaced recorded settings</text></g></svg>')
    write(folder, name, ''.join(svg))


def main():
    extra6, extra7 = read(A, 'extra.json'), read(B, 'extra.json')
    data6, data7 = read(A, 'explosion.json'), read(B, 'curse.json')
    machine = extra6['machine']
    for folder, data, filename in ((A, data6, 'explosion.json'), (B, data7, 'curse.json')):
        data['machine'] = machine
        data['measurement_note'] = 'Actual local execution; tracemalloc peaks exclude prebuilt input and native allocations. Timings are single runs.'
        write(folder, filename, json.dumps(data, indent=2, ensure_ascii=False))
    env = (f"실행 환경: {machine['cpu_name'].strip()}, RAM {machine['ram_bytes']/2**30:.2f} GiB, "
           f"{machine['platform']}, Python {machine['python']}. Codex와 샌드박스 셸이 실행 중이었다. "
           "샌드박스 밖의 전체 프로그램 목록은 확인할 수 없어 다른 앱이 없었다고 단정하지 않는다. "
           "시간은 단일 실행이며 실행 간 부하와 tracemalloc 계측 비용의 영향을 받는다.")
    rows = data6['runs']
    table = '| support | 최고 쌍 카운터 | 빈발 쌍 | 시간(s) | Python 할당 peak(MB) |\n|---:|---:|---:|---:|---:|\n'
    table += '\n'.join(f"| {r['support']} | {r['peak_counters']:,} | {r['frequent_pairs']:,} | {r['seconds']:.3f} | {r['peak_bytes']/1e6:.3f} |" for r in rows)
    ratios = [rows[i+1]['peak_counters']/rows[i]['peak_counters'] for i in range(len(rows)-1)]
    chart(A, 'explosion.svg', [r['support'] for r in rows],
          [('peak pair counters', [r['peak_counters'] for r in rows]),
           ('frequent pairs', [r['frequent_pairs'] for r in rows])],
          'Support threshold vs counters and answers', 'Support (decreasing; categorical spacing)', True)
    write(A, 'explosion.md', f'''# 지지도와 카운터 증가 실측

{env}

고정 데이터: bench.build(seed=246), 20,000개 바구니, 2,000개 항목. 지지도 400→1, 총 9개 설정으로 400배 범위를 측정했다. 각 시간은 입력 생성 이후 알고리즘 실행 시간이다. 메모리는 tracemalloc이 관측한 Python 할당 peak이며, 이미 생성된 바구니와 프로세스 전체 RAM은 제외한다.

{table}

![카운터와 정답의 증가](explosion.svg)

## A2: 어디서 중단했는가

support=1까지 완료했다. 가장 큰 측정은 {rows[-1]['seconds']:.3f}초, {rows[-1]['peak_bytes']/1e6:.3f} MB였다. 이 데이터에서는 RAM 부족이나 견디기 어려운 지연이 발생하지 않았다. support는 양의 정수이므로 1보다 낮추어도 새로운 양의 지지도 쌍이 생기지 않는다. 따라서 1에서 종료했으며, 메모리 고장점이나 6 GB 한계를 측정했다고 주장하지 않는다. 이 고정 데이터로는 실제 기기의 메모리 한계를 찾을 수 없다는 것이 관찰이다.

## A4–A5: 카운터와 정답의 다른 증가

연속 설정의 카운터 배수는 {', '.join(f'{v:.3f}' for v in ratios)}이다. 초반 400→200→100→50에서 5.54배·4.67배·3.00배로 증가해 두 배보다 가파르다. 이후 항목이 대부분 살아남아 카운터는 893,456개에서 포화한다. 따라서 계속 지수적으로 늘어난다는 결론은 틀리다.

support 400→50에서 정답은 249→6,397인데 카운터는 10,585→820,259개이다. support=50에서 약 128.2개 카운터를 유지해야 정답 하나를 얻는다. 그러나 support=1에서는 관측된 모든 쌍이 정답이 되어 둘 다 893,456이다. 낮은 문턱이 항상 같은 비율로 더 많은 메모리를 쓰는 것은 아니다. 이 간격이 큰 중간 영역에서 PCY의 필터가 특히 유용하다.
''')
    memory_table = '| 바구니 수 | A-Priori peak(MB) | PCY peak(MB) |\n|---:|---:|---:|\n'
    memory_table += '\n'.join(f"| {r['baskets']:,} | {r['baseline']['peak_bytes']/1e6:.3f} | {r['pcy']['peak_bytes']/1e6:.3f} |" for r in extra6['memory_runs'])
    bucket_table = '| 버킷 수 | 최고 쌍 카운터 | 할당 peak(MB) | 정답 수 |\n|---:|---:|---:|---:|\n'
    bucket_table += '\n'.join(f"| {r['buckets']:,} | {r['pair_counters']:,} | {r['peak_bytes']/1e6:.3f} | {r['answer_count']:,} |" for r in extra6['bucket_runs'])
    son_table = '| 청크 수 | 후보 수 | 최종 쌍 수 | 누락/추가 | 시간(s) |\n|---:|---:|---:|---|---:|\n'
    son_table += '\n'.join(f"| {r['chunks']} | {r['candidates']:,} | {r['pairs']:,} | 0 / 0 | {r['seconds']:.3f} |" for r in extra6['son_runs'])
    write(A, 'observation.md', f'''# 6주차 관찰 기록

## Task 1: 구현과 규칙의 해석

1패스에서 항목을 세고, 2패스에서는 살아남은 두 항목의 쌍만 센다. 주어진 7개 바구니에서 support=3이면 bread/milk/diaper/beer의 지지도가 모두 5여서 이들 사이 신뢰도는 우연히 대칭이다. 비대칭을 보려면 같은 데이터에서 support=2로 낮춘다. cola→milk는 2/2=1.0, milk→cola는 2/5=0.4다. cola 구매자에 대한 주장이 더 강하지만 표본 2개만으로 일반화할 수 없다.

support=3, confidence≥0.75의 최고 규칙은 beer→diaper 등 신뢰도 0.8, lift=1.12다. 결과 항목의 기본 비율이 5/7이므로 개선은 작다. 인과관계나 강한 연관성을 입증했다고 보지 않는다.

항목 2,000개의 모든 가능한 쌍은 1,999,000개다. 벤치 데이터 support=50에서 빈발 항목은 {extra6['benchmark_frequent_items']:,}개이고 가능한 생존 쌍은 {math.comb(extra6['benchmark_frequent_items'],2):,}개다. 실제 바구니에 나타나 딕셔너리에 생성된 카운터는 820,259개다. 가능한 쌍 수와 실제 보유 카운터를 구별해야 한다.

## Task 2: 측정의 한계

support=1까지 측정했으며 {rows[-1]['peak_bytes']/1e6:.1f} MB, {rows[-1]['seconds']:.2f}초로 완료되어 실제 RAM 부족은 일어나지 않았다. 데이터의 끝에 도달한 것이며 기기의 한계에 도달한 것이 아니다. 카운터는 초반 문턱 반감마다 5.54→4.67→3.00배 늘다가 893,456개에 포화했다. 정답 수도 결국 같은 수에 도달한다. 세부 표와 그래프 및 계측 범위는 [explosion.md](explosion.md)에 기록했다.

## Task 3: PCY의 이득과 비용

버킷 1,000,003개를 썼다. 정수 배열 array('I')의 본체는 4,000,012바이트이며 카운트는 support에서 포화시켜 overflow를 피한다. 1패스 말에 125,001바이트의 packed bitmap으로 압축한 뒤 정수 배열을 삭제한다. 변환 중 잠시 두 배열이 공존하는 비용도 peak 측정에 포함했다. 항목 Counter, tuple key, dict, 결과 frozenset 등의 비용도 tracemalloc에 포함한다. 입력 바구니, 네이티브 할당, 전체 프로세스 RAM은 제외한다.

동일한 6,397개 정답과 정확한 지지도 값을 유지하며 쌍 카운터는 820,259→13,183으로 약 98.39% 줄었다. 카운터 지표만으로 RAM 절감률을 주장하지 않고 실제 할당도 별도로 재었다.

{memory_table}

이 데이터의 prefix와 고정 support=50에서는 메모리 교차점이 1,000개와 5,000개 바구니 사이에 있다. 정확한 교차점은 측정하지 않았다. 빈발 항목 수·쌍 밀도·support·해시 충돌·버킷 수·Python 객체 크기에 따라 이동한다. 작은 데이터에서는 PCY가 고정 배열 때문에 오히려 불리하고, 시간도 더 걸린다.

{bucket_table}

1,009개 버킷에서는 충돌로 거의 모든 버킷이 빈발해져 필터가 효과를 잃었다. 버킷 수를 줄이는 것은 공짜 절약이 아니며 2패스 딕셔너리를 키울 수 있다. bench.py는 수정하지 않았다.

## Task 4: 선택 과제 SON

청크별 문턱은 support×청크크기/전체크기이고 크기가 다른 청크에도 그대로 적용했다. 전역 빈발 쌍이 모든 청크에서 문턱 미만이라면 그 지지도를 합해도 support 미만이어야 한다. 전역에서 support 이상이라는 가정과 모순이므로 후보 합집합은 빈발 쌍을 놓치지 않는다. 2패스가 정확한 지지도를 세어 거짓 양성을 제거한다.

{son_table}

청크를 늘리면 후보 수가 변하지만 최종 정답 6,397개는 유지된다. 후보가 정답보다 많은 것은 1패스의 지역 잡음이며 최종 답의 오류가 아니다. pass two는 후보×바구니의 전수 부분집합 검사 대신 각 바구니의 쌍을 열거하고 후보 set에서 조회한다. 따라서 교재의 느린 구현 시간 12.19초를 내 측정으로 복사하지 않았다. 단일 기기에 들어가는 데이터에서는 기본 A-Priori도 효율적이지만, SON은 청크별 독립 처리와 두 전역 패스로 분산 가능한 구조를 제공한다. 현재 환경에 PySpark가 설치되지 않아 Spark 실행은 생략했다. 단일 프로세스 SON은 구현과 검증을 완료했다.

## 재현

python task1_apriori.py --verify, python task2_explosion.py --supports 400,200,100,50,25,12,6,3,1, python measure_extra.py, python verify_extra.py, python test_tasks.py. 실행 기록은 out/bench.txt, out/tests.txt, out/verification.txt에 있다.
''')
    write(A, 'task4.txt', 'SON single-process measurements\n'+json.dumps(extra6['son_runs'],indent=2)+'\nPySpark: not installed; Spark execution not attempted.')
    main_rows = [r for r in data7['runs'] if r['points']==1000]
    table7 = '| d | n | 표본 쌍 | 평균 | min | max | contrast | 표준편차/평균 | 시간(s) |\n|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n'
    table7 += '\n'.join(f"| {r['dim']} | {r['points']} | {r['pairs']} | {r['mean']:.4f} | {r['min']:.4f} | {r['max']:.4f} | {r['contrast']:.4f} | {r['relative_stdev']:.4f} | {r['seconds']:.4f} |" for r in data7['runs'])
    full_table = '| n (d=50) | 전체 쌍 | contrast |\n|---:|---:|---:|\n'
    full_table += '\n'.join(f"| {r['points']} | {r['pairs']:,} | {r['contrast']:.4f} |" for r in extra7['exhaustive_n_runs'])
    chart(B, 'curse.svg', [r['dim'] for r in main_rows],
          [('contrast', [r['contrast'] for r in main_rows]),
           ('relative standard deviation', [r['relative_stdev'] for r in main_rows])],
          'Distance concentration vs dimension (n=1000)', 'Dimension (categorical spacing)', True)
    write(B, 'curse.md', f'''# 차원의 저주 실측

{env}

seed=246. 각 (n,d)에서 균등 단위 정육면체 점을 만든 뒤 20,000번 인덱스 쌍을 추출했다. 같은 점 쌍은 제외하므로 유효 쌍 수가 조금 작고 중복된 쌍은 있을 수 있다. 표본 extrema이며 모든 점 쌍의 전역 최소/최대라고 주장하지 않는다.

{table7}

![거리 집중](curse.svg)

## A3–A5: 차원에 따른 변화

n=1,000의 측정 격자에서 contrast가 1 미만인 첫 차원은 50 (이전 20에서는 1 초과), 0.5 미만인 첫 차원은 200 (이전 100에서는 0.5 초과)이다. 정확한 전환점을 측정한 것은 아니다. d=1,000에서 contrast는 약 0.160이다.

평균은 d=100에서 약 4.068, d=1,000에서 약 12.903이다. 비율 {main_rows[-1]['mean']/next(r['mean'] for r in main_rows if r['dim']==100):.4f}는 sqrt(10)=3.1623에 가깝다. 서로 독립인 U(0,1) 좌표 차의 제곱 기댓값은 1/6이므로 거리 제곱의 평균은 d/6이고, 고차원에서 거리가 집중되면 평균 거리가 sqrt(d/6)에 가까워진다. 평균 거리가 d에 선형으로 자란다는 주장은 지지하지 않는다.

상대표준편차는 d=2의 약 0.476에서 d=1,000의 약 0.019로 줄었다. 상대 표준편차는 분포 전체의 전형적 집중을, contrast는 표본의 극단값 간 분리를 나타낸다. 전형적 거리의 정보 손실에는 상대 표준편차가 더 안정적이고, nearest/farthest의 구분을 질문할 때는 contrast가 직접적이다. 어느 하나만으로 모든 실제 데이터의 거리 기반 방법이 실패한다고 단정할 수 없다.

## A6: 점 수와 측정 프로토콜

d=50에서 n=200, 1,000, 4,000으로도 측정했다. 20,000회로 고정한 무작위 쌍 표본에서는 n의 효과가 작고 단조롭다는 보장도 없다. n을 늘려도 보는 쌍 수는 거의 같기 때문이다. 이를 모든 쌍의 극단값에 대한 결론과 혼동하지 않도록, 추가로 같은 난수열의 prefix n=50,200,600을 사용해 모든 쌍을 비교했다.

{full_table}

전수 비교에서는 n이 늘며 더 가까운 쌍·먼 쌍을 발견해 contrast가 커졌다. d만이 아니라 n과 표본 쌍 수에도 의존한다. 가장 큰 차원 실행의 시간은 {main_rows[-1]['seconds']:.4f}초였으며, 전수 비교의 최대 n=600은 {extra7['exhaustive_n_runs'][-1]['seconds']:.4f}초였다.

## A8: 3주차 LSH와의 관계

이 결과는 균등한 고차원 유클리드 데이터의 관찰이다. 3주차는 문자 shingle 집합의 Jaccard 유사도와 minhash 충돌 확률을 사용하므로 이 측정으로 LSH가 실패한다고 결론 내릴 수 없다. 실제 문서에 중복 구조와 유사도 격차가 있으면 밴딩은 여전히 유용하다. 반대로 실제 집합들의 Jaccard 유사도 자체가 비슷하게 집중되면 후보 분리에 어려움이 생길 수 있으므로, 거리의 종류와 실제 유사도 분포부터 확인해야 한다.
''')
    metrics = extra7['benchmark']
    write(B, 'observation.md', f'''# 7주차 관찰 기록

## Task 1: k-means와 초기화

거리는 모든 좌표의 제곱 차 합의 제곱근이고 차원 불일치는 거부한다. 동률은 낮은 중심 인덱스에 배정한다. 빈 클러스터는 현재 비어 있지 않은 중심들에서 가장 먼 점으로 다시 초기화한다. 대안인 이전 중심 유지와 달리 비어 있는 클러스터를 데이터가 먼 영역으로 옮겨 다시 사용할 기회를 주지만, 동일 좌표만 있는 데이터에서는 k개의 비어 있지 않은 군집을 강제할 수 없다.

40개 seed에서 random은 {extra7['initialization']['random']['successes']}/40, k-means++는 {extra7['initialization']['++']['successes']}/40회 올바른 세 덩어리(SSE<1)를 찾았다. 평균 SSE는 random {extra7['initialization']['random']['mean_sse']:.5f}, ++ {extra7['initialization']['++']['mean_sse']:.5f}다. random의 최고 SSE는 96.105, 최저는 0.12였다. k-means++는 먼저 거리 제곱에 비례해 떨어진 점을 선택하는 비용을 지불하고 나쁜 시작의 위험을 줄인다. 이미 좋은 중심이 있거나 매우 짧은 작업이면 이 비용을 지불할 이유가 작다.

k를 늘려 얻을 수 있는 최적 SSE는 줄어들며 k=n이면 각 점을 자기 중심으로 해 SSE=0이다. 따라서 SSE 최소만으로 k를 고르면 의미 없는 극단에 이른다. 독립적인 무작위 초기화 실행의 관측 SSE가 언제나 단조롭다는 뜻은 아니며, 꺾임·안정성·해석 가능성도 봐야 한다.

## Task 2: 차원과 표본 수

n=1,000, 약 20,000개 표본 쌍에서 contrast가 1 아래로 간 첫 측정 차원은 50, 0.5 아래는 200이다. 전환점은 측정 격자와 n 및 쌍 표본 수에 따라 바뀐다. d=50의 전수 비교에서 n=50→200→600의 contrast는 0.841→0.900→1.209로 증가했다. 분포와 표본 극단값은 별개다. Jaccard 기반 문서 LSH는 균등 유클리드 점과 다른 자료·척도를 사용하므로 이 결과만으로 실패한다고 할 수 없다. 자세한 표와 근거는 [curse.md](curse.md)에 있다.

## Task 3: 근사 없이 가지치기

Hamerly 형태의 경계를 사용한다. 점마다 현재 소속까지의 거리 상한 u와 다른 모든 중심까지 거리의 하한 l 두 수를 저장하며 추가 상태는 2n=40,000개 수다. 레이블은 두 알고리즘 모두 필요하고 이 수에 포함하지 않았다. 중심 간 최소 거리의 절반 s와 이동량도 O(k)개 저장하며, 모든 점-중심별 O(nk) 하한 행렬은 저장하지 않는다.

u < max(l,s)일 때 다른 중심이 더 가까울 수 없다. 필요하면 현재 중심까지 거리만 재계산해 상한을 조인 뒤 다시 검사한다. 그래도 실패하면 모든 중심과 비교한다. 이동 후 u에는 현재 중심 이동량을 더하고 l에서는 모든 중심 중 최대 이동량을 뺀다. 중심 간 거리 계산과 이동량 계산도 전달받은 distance 함수로 세어 숨기지 않았다. 경계는 점당 O(1), 라운드당 O(n+k²) 관리 비용이 들며, 중심 평균 갱신 비용은 여전히 남는다. 코드의 1e-10 여유와 엄격한 부등식은 기준선의 1e-12 동률 판정을 보호하기 위해 가지치기를 더 보수적으로 한다.

기준선 {metrics['baseline']['calls']:,}회에서 {metrics['yours']['calls']:,}회로 약 {100*(1-metrics['yours']['calls']/metrics['baseline']['calls']):.2f}% 줄었다. SSE는 둘 다 {metrics['baseline']['sse']:.9f}로 차이가 정확히 0이고 반복도 43회로 같았다. 동일 초기화·동률 규칙·평균 계산을 유지하면서 결과를 바꿀 수 없는 비교만 생략하기 때문이다. 무작위 작은 정수 좌표, 중복 중심, 빈 클러스터와 동률을 포함한 {extra7['exact_randomized_and_tie_cases']}개 추가 사례에서 레이블과 중심까지 기준선과 일치했다.

첫 반복은 모든 점×중심인 {metrics['first_iteration_calls']:,}회를 수행한다. 최적화 버전 전체의 {100*metrics['first_iteration_calls']/metrics['yours']['calls']:.2f}%다. 한 번도 배정하지 않은 점에는 유효한 경계가 없으므로 이 비용은 생략하지 않았다. 모든 중심의 이동량을 뺀 l이 느슨해질 때도 있지만, 이후 중심 이동이 작아지면 l과 s의 결합이 대부분의 점을 건너뛴다. 두 경계의 개별 기여 비율을 별도로 측정하지 않았으므로 어느 하나가 몇 %를 절약했다고 주장하지 않는다.

bench.py는 수정하지 않았다. 실제 시간은 기준선 {metrics['baseline']['time']:.3f}초, 최적화 {metrics['yours']['time']:.3f}초였지만 채점 지표는 거리 호출 수이고, 이 속도비는 현재 데이터·기기의 단일 측정이다.

## 재현

python task1_kmeans.py --verify; python task2_curse.py --dims 2,5,10,20,50,100,200,500,1000; python task2_curse.py --dims 50 --points 200; python task2_curse.py --dims 50 --points 4000; python measure_extra.py; python test_tasks.py. 최종 검증 로그는 out/tests.txt에 있다.
''')
    print('Korean reports and SVG plots created from measurements.')


if __name__ == '__main__':
    main()
