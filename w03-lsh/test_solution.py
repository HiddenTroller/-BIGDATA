"""Additional checks for edge cases and the measurement-size regression."""
import unittest

from task1_minhash import jaccard, lsh_candidates, minhash_signatures
from task2_crossover import build_documents
from task3_scale import BruteForce, YourFinder


class SolutionTests(unittest.TestCase):
    def test_jaccard_empty_and_disjoint(self):
        self.assertEqual(jaccard(set(), set()), 0.0)
        self.assertEqual(jaccard({1}, {2}), 0.0)
        self.assertEqual(jaccard({1, 2}, {2, 3}), 1 / 3)

    def test_hash_each_populated_row_once(self):
        visited = []

        def identity(row):
            visited.append(row)
            return row

        signatures = minhash_signatures([{0, 2}, {2}, set()], [identity], 4)
        self.assertEqual(visited, [0, 2])
        self.assertEqual(signatures, [[0], [2], [float("inf")]])

    def test_invalid_row_rejected(self):
        for row in (-1, 3):
            with self.assertRaises(ValueError):
                minhash_signatures([{row}], [lambda r: r], 3)

    def test_band_collisions_and_pair_deduplication(self):
        self.assertEqual(lsh_candidates([[1, 2], [1, 2], [3, 2]], 2),
                         {(0, 1), (0, 2), (1, 2)})
        self.assertEqual(lsh_candidates([], 1), set())

    def test_remainders_and_inconsistent_lengths_rejected(self):
        for signatures, bands in (([[1, 2, 3]], 2), ([[1], [1, 2]], 1),
                                  ([[1]], 0), ([[]], 1)):
            with self.assertRaises(ValueError):
                lsh_candidates(signatures, bands)

    def test_finder_exact_duplicates_empty_and_zero_threshold(self):
        docs = [set(), {"alpha", "beta"}, {"alpha", "beta"}, {"other"}, set()]
        for threshold in (0, 0.6, 1):
            expected = BruteForce(threshold).find(docs, jaccard)
            self.assertEqual(YourFinder(threshold).find(docs, jaccard), expected)
        self.assertEqual(YourFinder(0.6).find([], jaccard), set())

    def test_large_measurement_really_contains_requested_size(self):
        docs = build_documents(2200)
        self.assertEqual(len(docs), 2200)
        self.assertEqual(docs[:32], build_documents(32))
        self.assertEqual(build_documents(32), build_documents(32))


if __name__ == "__main__":
    unittest.main()
