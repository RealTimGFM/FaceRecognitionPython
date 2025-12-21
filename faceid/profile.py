from __future__ import annotations

import math
from typing import Dict, Iterable, List

from .math import InvalidEmbeddingError, _as_float_list


def compute_centroid(embeddings: List[Iterable[float]]) -> List[float]:
    if not embeddings:
        raise InvalidEmbeddingError("No embeddings provided")

    vecs = [_as_float_list(v) for v in embeddings]
    dim = len(vecs[0])
    if any(len(v) != dim for v in vecs):
        raise InvalidEmbeddingError("Embedding length mismatch")

    centroid = [0.0] * dim
    for v in vecs:
        for i, x in enumerate(v):
            centroid[i] += x
    return [x / len(vecs) for x in centroid]


def _euclidean(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def compute_profile_stats(embeddings: List[Iterable[float]], base_threshold: float = 0.35) -> Dict[str, object]:
    if not embeddings:
        raise InvalidEmbeddingError("No embeddings provided")

    vecs = [_as_float_list(v) for v in embeddings]
    dim = len(vecs[0])
    if any(len(v) != dim for v in vecs):
        raise InvalidEmbeddingError("Embedding length mismatch")

    centroid = compute_centroid(vecs)
    dists = [_euclidean(v, centroid) for v in vecs]

    mean = sum(dists) / len(dists)
    if len(dists) == 1:
        std = 0.0
    else:
        var = sum((d - mean) ** 2 for d in dists) / (len(dists) - 1)
        std = math.sqrt(var)

    # Adaptive threshold:
    # - floor at base_threshold (avoid being too strict)
    # - allow variability (reduce false negatives)
    # - clamp to avoid runaway (reduce false positives)
    adaptive = mean + 3.0 * std
    thr = max(float(base_threshold), float(adaptive))
    thr = min(thr, float(base_threshold) * 5.0)

    return {
        "centroid": centroid,
        "mean_distance": mean,
        "std_distance": std,
        "recommended_threshold": thr,
    }
