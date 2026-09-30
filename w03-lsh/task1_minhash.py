#!/usr/bin/env python3
"""Week 3 · Task 1 — Minhash and LSH, built from the matrix up.

Textbook §3.2 - §3.4.

    python3 task1_minhash.py --verify
"""
import argparse

# §3.3.5. Rows are elements 0..4, columns are the sets S1..S4.
BOOK = [[1, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 0, 1, 0]]
# The two hash functions the textbook uses on the row numbers.
BOOK_HASHES = [lambda r: (r + 1) % 5, lambda r: (3 * r + 1) % 5]


def jaccard(a, b):
    """Return |a ∩ b| / |a ∪ b|; the similarity of two empty sets is 0."""
    union_size = len(a | b)
    return len(a & b) / union_size if union_size else 0.0


def minhash_signatures(columns, hashes, n_rows):
    """Build one signature per column while making one outer pass over rows.

    `columns` contains one set of row IDs per document. An empty column gets
    None in every signature slot because no row belongs to that set.
    """
    if n_rows < 0:
        raise ValueError("n_rows must be non-negative")

    signatures = [[None] * len(hashes) for _ in columns]
    for column in columns:
        if any(row < 0 or row >= n_rows for row in column):
            raise ValueError("column contains a row outside 0..n_rows-1")

    # Each matrix row is visited once; its 1s update all corresponding columns.
    for row in range(n_rows):
        for column_index, column in enumerate(columns):
            if row in column:
                signature = signatures[column_index]
                for hash_index, hash_fn in enumerate(hashes):
                    value = hash_fn(row)
                    previous = signature[hash_index]
                    if previous is None or value < previous:
                        signature[hash_index] = value
    return signatures


def lsh_candidates(signatures, bands):
    """Return (i, j) pairs sharing at least one LSH band.

    Remainder rows are distributed one each to the earliest bands, so every
    signature position is used even when its length is not divisible by bands.
    """
    if not signatures:
        return set()
    if bands <= 0:
        raise ValueError("bands must be a positive integer")

    width = len(signatures[0])
    if any(len(signature) != width for signature in signatures):
        raise ValueError("all signatures must have the same length")
    if width == 0:
        return set()
    if bands > width:
        raise ValueError("bands cannot exceed the signature length")

    base, extra = divmod(width, bands)
    candidates = set()
    start = 0
    for band in range(bands):
        band_width = base + (1 if band < extra else 0)
        buckets = {}
        end = start + band_width
        for column_index, signature in enumerate(signatures):
            key = tuple(signature[start:end])
            buckets.setdefault(key, []).append(column_index)
        for members in buckets.values():
            for left_pos in range(len(members)):
                for right_pos in range(left_pos + 1, len(members)):
                    i, j = members[left_pos], members[right_pos]
                    candidates.add((i, j) if i < j else (j, i))
        start = end
    return candidates


# ------------------------------------------------------------------- harness
def columns_from_matrix(matrix):
    n_rows, n_cols = len(matrix), len(matrix[0])
    return [{r for r in range(n_rows) if matrix[r][c]} for c in range(n_cols)]


def verify():
    fails = 0

    def check(label, got, want):
        nonlocal fails
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<44} {got}"
              + ("" if ok else f"\n{'':>54}want {want}"))
        fails += not ok

    cols = columns_from_matrix(BOOK)
    check("jaccard(S1, S4)", round(jaccard(cols[0], cols[3]), 4), round(2 / 3, 4))
    check("jaccard(S1, S2)", jaccard(cols[0], cols[1]), 0.0)
    check("jaccard on empty sets", jaccard(set(), set()), 0)

    sig = minhash_signatures(cols, BOOK_HASHES, len(BOOK))
    check("signature of S1", sig[0], [1, 0])
    check("signature of S2", sig[1], [3, 2])
    check("signature of S3", sig[2], [0, 0])
    check("signature of S4", sig[3], [1, 0])

    cands = lsh_candidates([[1, 0], [3, 2], [0, 0], [1, 0]], bands=2)
    check("S1 and S4 are candidates", (0, 3) in cands, True)
    check("S1 and S2 are not", (0, 1) in cands, False)
    check("uneven bands include remainder rows",
          lsh_candidates([[1, 2, 3, 4, 5], [0, 0, 0, 4, 5]], bands=2) == {(0, 1)}, True)

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    if not fails:
        print("  Note that S1 and S4 agree in both signature positions, which "
              "estimates\n  their similarity as 1.0 when it is actually 2/3. "
              "Two hashes is not many.")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
