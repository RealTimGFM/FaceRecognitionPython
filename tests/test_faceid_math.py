import math
import pytest


def test_normalize_unit_length():
    from faceid.math import normalize  # to be implemented

    v = [3.0, 4.0]
    out = normalize(v)
    norm = math.sqrt(sum(x * x for x in out))
    assert norm == pytest.approx(1.0, rel=1e-9)


def test_normalize_rejects_zero_vector():
    from faceid.math import normalize, InvalidEmbeddingError  # to be implemented

    with pytest.raises(InvalidEmbeddingError):
        normalize([0.0, 0.0, 0.0])


def test_cosine_distance_identical_is_zero():
    from faceid.math import cosine_distance  # to be implemented

    a = [0.1, 0.2, 0.3, 0.4]
    assert cosine_distance(a, a) == pytest.approx(0.0, abs=1e-9)


def test_cosine_distance_opposites_is_two():
    from faceid.math import cosine_distance  # to be implemented

    a = [1.0, 0.0]
    b = [-1.0, 0.0]
    assert cosine_distance(a, b) == pytest.approx(2.0, abs=1e-9)


def test_cosine_distance_rejects_shape_mismatch():
    from faceid.math import cosine_distance, InvalidEmbeddingError  # to be implemented

    with pytest.raises(InvalidEmbeddingError):
        cosine_distance([0.1, 0.2], [0.1])


def test_rejects_nan_inf_values():
    from faceid.math import normalize, InvalidEmbeddingError  # to be implemented

    with pytest.raises(InvalidEmbeddingError):
        normalize([1.0, float("nan")])

    with pytest.raises(InvalidEmbeddingError):
        normalize([1.0, float("inf")])
