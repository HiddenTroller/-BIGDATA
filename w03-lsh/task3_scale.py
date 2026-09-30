#!/usr/bin/env python3
"""Week 3 · Task 3 — LSH candidate generation with exact verification.

Uses 200 deterministic minhash functions split into 50 bands of 4 rows.
The S-curve transition estimate is (1 / 50) ** (1 / 4) ≈ 0.376, favoring
recall above the task's 0.6 similarity threshold.
"""
import random

_HASHES = 200
_BANDS = 50
_PRIME = (1 << 61) - 1
_SEED = 202603


class BruteForce:
    """Correct reference implementation used by the harness."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        out = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))
        return out


class YourFinder:
    """Minhash documents, bucket bands, and exactly check candidate pairs."""

    def __init__(self, threshold):
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold

    def find(self, docs, similarity):
        docs = list(docs)
        if len(docs) < 2:
            return set()

        # Stable IDs make results independent of Python's randomized hash seed.
        universe = set().union(*docs)
        ordered = sorted(universe,
                         key=lambda value: (type(value).__module__,
                                            type(value).__qualname__, repr(value)))
        item_id = {item: index for index, item in enumerate(ordered)}

        rng = random.Random(_SEED)
        coefficients = [(rng.randrange(1, _PRIME), rng.randrange(_PRIME))
                        for _ in range(_HASHES)]
        signatures = [[_PRIME] * _HASHES for _ in docs]
        for doc_index, doc in enumerate(docs):
            for item in doc:
                item_number = item_id[item]
                for hash_index, (a, b) in enumerate(coefficients):
                    value = (a * item_number + b) % _PRIME
                    if value < signatures[doc_index][hash_index]:
                        signatures[doc_index][hash_index] = value

        rows_per_band = _HASHES // _BANDS
        candidates = set()
        for band in range(_BANDS):
            start = band * rows_per_band
            end = start + rows_per_band
            buckets = {}
            for doc_index, signature in enumerate(signatures):
                key = tuple(signature[start:end])
                buckets.setdefault(key, []).append(doc_index)
            for members in buckets.values():
                for offset, i in enumerate(members):
                    for j in members[offset + 1:]:
                        candidates.add((i, j))

        return {(i, j) for i, j in candidates
                if similarity(docs[i], docs[j]) >= self.threshold}
