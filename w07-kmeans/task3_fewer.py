#!/usr/bin/env python3
"""Week 7 · Task 3 — The same clustering, with far fewer distances.

Textbook §7.3, and §7.1.3 for why distance is the expensive part.

`NaiveKMeans` does what the definition says: every iteration, compare every
point with every centroid. That is n x k distance computations per pass, and on
a real dataset the distance computation is almost the entire cost.

Most of that work is wasted. After the first couple of iterations, most points
do not change cluster, and most centroids barely move. The triangle inequality
lets you prove a point cannot have changed cluster **without measuring it**.

    python3 bench.py
    python3 bench.py --yours

Correctness first: your final SSE must match the baseline's. Fewer distances
with a worse clustering is not an improvement, it is a different algorithm.
"""


class NaiveKMeans:
    """Every point against every centroid, every iteration."""

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            for i, p in enumerate(points):
                best, bi = None, 0
                for j, c in enumerate(centroids):
                    d = distance(p, c)
                    if best is None or d < best - 1e-12:
                        best, bi = d, j
                if labels[i] != bi:
                    labels[i] = bi
                    changed = True
            centroids = _means(points, labels, self.k, centroids)
            if not changed:
                break
        return labels, centroids


def _means(points, labels, k, previous):
    out = []
    for j in range(k):
        group = [p for p, l in zip(points, labels) if l == j]
        if group:
            out.append(tuple(sum(v) / len(group) for v in zip(*group)))
        else:
            out.append(previous[j])
    return out


class YourKMeans:
    """Your k-means.

        __init__(k, max_iter=50)
        run(points, initial_centroids, distance) -> (labels, centroids)

    Same starting centroids, same `distance` function - which is counted. That
    counter is your score.

    The idea, from §7.3 and the triangle inequality:

        if a point is much closer to its current centroid than that centroid
        moved, and than any other centroid could have come, then it cannot have
        changed cluster, and you do not have to measure anything

    Keeping enough bookkeeping to make that test cheap, without keeping so much
    that the bookkeeping costs more than the distances, is the task.

    You may call `distance` on two centroids, and those calls are counted too -
    which is the correct accounting, since that is real work. There are k of
    them and n points, and k is much smaller than n. That asymmetry is the
    whole opening.
    """

    def __init__(self, k, max_iter=50):
        if k < 1 or max_iter < 1:
            raise ValueError("k and max_iter must be positive")
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        import math
        if len(initial_centroids) != self.k:
            raise ValueError("need k initial centroids")
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        upper = [math.inf] * len(points)
        lower = [0.0] * len(points)
        self.bound_skips = 0
        self.first_iteration_calls = 0
        for self.iterations in range(1, self.max_iter + 1):
            separation = [math.inf] * self.k
            if self.iterations > 1:
                for a in range(self.k):
                    for b in range(a + 1, self.k):
                        half = distance(centroids[a], centroids[b]) / 2
                        separation[a] = min(separation[a], half)
                        separation[b] = min(separation[b], half)
            changed = False
            for i, point in enumerate(points):
                old = labels[i]
                if old is not None:
                    threshold = max(lower[i], separation[old])
                    # Strict margin preserves the baseline's 1e-12 tie rule.
                    if upper[i] + 1e-10 < threshold:
                        self.bound_skips += 1
                        continue
                    upper[i] = distance(point, centroids[old])
                    if upper[i] + 1e-10 < threshold:
                        self.bound_skips += 1
                        continue
                ds = [distance(point, centre) for centre in centroids]
                best, label = ds[0], 0
                for j in range(1, self.k):
                    if ds[j] < best - 1e-12:
                        best, label = ds[j], j
                lower[i] = min((d for j, d in enumerate(ds) if j != label), default=math.inf)
                upper[i] = best
                labels[i] = label
                changed |= label != old
            if self.iterations == 1:
                self.first_iteration_calls = len(points) * self.k
            new_centroids = _means(points, labels, self.k, centroids)
            if not changed:
                centroids = new_centroids
                break
            movement = [distance(a, b) for a, b in zip(centroids, new_centroids)]
            largest = max(movement)
            for i, label in enumerate(labels):
                upper[i] += movement[label]
                lower[i] = max(0.0, lower[i] - largest)
            centroids = new_centroids
        return labels, centroids
