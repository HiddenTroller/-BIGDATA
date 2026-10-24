"""Independent brute-force checks, including uneven SON chunks and collisions."""
import random
from collections import Counter
from itertools import combinations
from task1_apriori import frequent_pairs, association_rules, BASKETS
from task3_pcy import YourAlgorithm
from task4_son import son_pass_one, son_pass_two


def main():
    rng = random.Random(246)
    for trial in range(100):
        baskets = [set(rng.sample(range(9), rng.randrange(10)))
                   for _ in range(rng.randrange(1, 35))]
        support = rng.randrange(1, len(baskets) + 2)
        counts = Counter(frozenset(p) for basket in baskets
                         for p in combinations(sorted(basket), 2))
        truth = {pair: count for pair, count in counts.items() if count >= support}
        assert frequent_pairs(baskets, support) == truth
        # A tiny bucket table deliberately forces hash collisions.
        algo = YourAlgorithm(support, buckets=3)
        assert algo.run(baskets) == truth
        assert algo.run(baskets) == truth  # reused object resets its counters
        chunks = [baskets[:1], baskets[1:4], baskets[4:]]
        candidates = son_pass_one(chunks, support, len(baskets))
        assert set(truth) <= candidates
        assert son_pass_two(baskets, candidates, support) == truth
    assert frequent_pairs([], 1) == {}
    assert son_pass_one([], 1, 0) == set()
    rules = {(a, b): (c, lift) for a, b, c, lift in association_rules(BASKETS, 2, 0)}
    assert rules['cola', 'milk'][0] == 1
    assert rules['milk', 'cola'][0] == 0.4
    print('100 independent brute-force cases passed: exact counts, collisions, reuse, uneven SON chunks.')
    print('Empty input and asymmetric confidence checks passed.')


if __name__ == '__main__':
    main()
