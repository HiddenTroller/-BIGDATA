#!/usr/bin/env python3
"""Week 3 · Task 3 — Find the same pairs without comparing everything.

Textbook §3.4.

`BruteForce` compares every pair. On 3,000 documents that is 4.5 million
comparisons and it is completely correct. On 3 million documents it is 4.5
trillion and it is completely useless.

Beat it. Find the same near-duplicate pairs while making far fewer comparisons.

    python3 bench.py
    python3 bench.py --yours

The harness counts every call you make to `similarity()`. That is your score.
It also checks **recall** - which of the truly similar pairs you found. Skipping
comparisons is easy; skipping comparisons without losing the pairs is the task.
"""
import random
from itertools import combinations

from task1_minhash import lsh_candidates, minhash_signatures


class BruteForce:
    """Correct, and quadratic."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        """docs is [set_of_shingles, ...]. Return {(i, j), ...} with i < j."""
        out = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))
        return out


class YourFinder:
    """Your near-duplicate finder.

        __init__(threshold)
        find(docs, similarity) -> {(i, j), ...}

    `similarity(a, b)` is the only way to compare two documents, and every call
    is counted. Everything else - signatures, banding, bucketing - is free, in
    the sense that the harness does not charge you for it. That is deliberate:
    it is also roughly true at scale, where the comparison is the expensive
    part and the hashing is linear.

    Two knobs decide everything:

        the number of hashes in a signature
        how many bands you split it into

    §3.4.2 gives you the relationship between those and the probability that a
    pair at similarity s becomes a candidate. It is an S-curve, and where its
    step sits is something you choose. Choose it on purpose and be able to say
    why in observation.md - a threshold of 0.8 does not mean bands should be
    anything in particular until you have done the arithmetic.

    You may reuse your Task 1 code.
    """

    def __init__(self, threshold):
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold
        self.num_hashes = 120
        self.bands = 30
        rng = random.Random(246)
        prime = 2_147_483_647
        self.hashes = [
            (lambda row, a=a, b=b: (a * row + b) % prime)
            for a, b in ((rng.randrange(1, prime), rng.randrange(prime))
                         for _ in range(self.num_hashes))
        ]

    def find(self, docs, similarity):
        if self.threshold == 0:
            # Every Jaccard value (including empty unions) is >= zero.
            return {(i, j) for i, j in combinations(range(len(docs)), 2)
                    if similarity(docs[i], docs[j]) >= self.threshold}
        if len(docs) < 2:
            return set()
        # Coordinate compression supports arbitrary hashable shingles without
        # relying on Python's process-randomized string hashes.
        row_ids, columns, document_ids = {}, [], []
        for index, doc in enumerate(docs):
            if not doc:
                continue  # Empty sets have Jaccard zero and cannot qualify.
            rows = set()
            for shingle in doc:
                if shingle not in row_ids:
                    row_ids[shingle] = len(row_ids)
                rows.add(row_ids[shingle])
            columns.append(rows)
            document_ids.append(index)
        if len(columns) < 2:
            return set()
        signatures = minhash_signatures(columns, self.hashes, len(row_ids))
        candidates = lsh_candidates(signatures, self.bands)
        found = set()
        for left, right in sorted(candidates):
            i, j = document_ids[left], document_ids[right]
            if similarity(docs[i], docs[j]) >= self.threshold:
                found.add((i, j))
        return found
