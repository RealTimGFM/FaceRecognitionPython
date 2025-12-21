from __future__ import annotations

import math
from typing import Iterable, List


class InvalidEmbeddingError(ValueError):
    """Raised when an embedding vector is missing/invalid (shape, type, NaN/Inf, etc.)."""


def _as_float_list(vec: Iterable[float]) -> List[float]:
    try:
        out = [float(x) for x in vec]
    except Exception as e:
        raise InvalidEmbeddingError("Embedding must be an iterable of numbers") from e

    if not out:
        raise InvalidEmbeddingError("Embedding must not be empty")

    for x in out:
        if math.isnan(x) or math.isinf(x):
            raise InvalidEmbeddingError("Embedding contains NaN/Inf")
    return out


def normalize(vec: Iterable[float]) -> List[float]:
    v = _as_float_list(vec)
    norm = math.sqrt(sum(x * x for x in v))
    if norm == 0.0:
        raise InvalidEmbeddingError("Cannot normalize zero vector")
    return [x / norm for x in v]


def cosine_distance(a: Iterable[float], b: Iterable[float]) -> float:
    va = normalize(a)
    vb = normalize(b)
    if len(va) != len(vb):
        raise InvalidEmbeddingError("Embedding length mismatch")

    dot = sum(x * y for x, y in zip(va, vb))
    dot = max(-1.0, min(1.0, dot))  # clamp for numeric stability

    # distance in [0, 2]
    return 1.0 - dot
