import pytest


def test_compute_centroid_basic():
    from faceid.profile import compute_centroid  # to be implemented

    embs = [
        [1.0, 0.0],
        [0.0, 1.0],
    ]
    c = compute_centroid(embs)
    assert c == pytest.approx([0.5, 0.5], rel=1e-9)


def test_compute_profile_stats_outputs_expected_fields():
    from faceid.profile import compute_profile_stats  # to be implemented

    embs = [
        [0.1, 0.2, 0.3, 0.4],
        [0.1, 0.2, 0.3, 0.41],
        [0.1, 0.2, 0.29, 0.4],
    ]
    stats = compute_profile_stats(embs)

    # Required keys for a stable “FaceID v2” contract
    assert "centroid" in stats
    assert "mean_distance" in stats
    assert "std_distance" in stats
    assert "recommended_threshold" in stats

    assert isinstance(stats["centroid"], list)
    assert stats["recommended_threshold"] > 0


def test_compute_profile_stats_rejects_empty():
    from faceid.profile import compute_profile_stats, InvalidEmbeddingError  # to be implemented

    with pytest.raises(InvalidEmbeddingError):
        compute_profile_stats([])
