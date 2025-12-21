from datetime import datetime, timedelta, timezone
import pytest


def _vec(n, base=0.0, step=0.01):
    return [base + i * step for i in range(n)]


def test_enroll_then_verify_match(store_dir):
    from faceid.store import FaceStore  # to be implemented

    store = FaceStore(store_dir)
    user_id = "tim"

    # Multi-sample enrollment (improves robustness)
    store.enroll(user_id, embeddings=[_vec(8, 0.10), _vec(8, 0.11), _vec(8, 0.09)], min_samples=3)

    res = store.verify(user_id, embedding=_vec(8, 0.105), base_threshold=0.35)
    assert res.is_match is True
    assert res.distance <= res.threshold


def test_enroll_then_verify_non_match(store_dir):
    from faceid.store import FaceStore  # to be implemented

    store = FaceStore(store_dir)
    user_id = "tim"

    store.enroll(user_id, embeddings=[_vec(8, 0.10), _vec(8, 0.11), _vec(8, 0.09)], min_samples=3)

    res = store.verify(user_id, embedding=_vec(8, 9.0), base_threshold=0.35)
    assert res.is_match is False
    assert res.distance > res.threshold


def test_enroll_requires_min_samples(store_dir):
    from faceid.store import FaceStore, EnrollmentError  # to be implemented

    store = FaceStore(store_dir)
    with pytest.raises(EnrollmentError):
        store.enroll("u1", embeddings=[_vec(8, 0.1), _vec(8, 0.2)], min_samples=3)


def test_verify_unknown_user_raises(store_dir):
    from faceid.store import FaceStore, UserNotEnrolledError  # to be implemented

    store = FaceStore(store_dir)
    with pytest.raises(UserNotEnrolledError):
        store.verify("missing", embedding=_vec(8, 0.1))


def test_rejects_path_traversal_user_id(store_dir):
    from faceid.store import FaceStore  # to be implemented

    store = FaceStore(store_dir)
    with pytest.raises(ValueError):
        store.enroll("../etc/passwd", embeddings=[_vec(8, 0.1), _vec(8, 0.1), _vec(8, 0.1)], min_samples=3)


def test_prune_older_than_deletes_old_profiles(store_dir):
    from faceid.store import FaceStore  # to be implemented

    store = FaceStore(store_dir)
    now = datetime(2025, 1, 1, tzinfo=timezone.utc)

    store.enroll("old", embeddings=[_vec(8, 0.1), _vec(8, 0.1), _vec(8, 0.1)], min_samples=3, now=now - timedelta(hours=30))
    store.enroll("new", embeddings=[_vec(8, 0.2), _vec(8, 0.2), _vec(8, 0.2)], min_samples=3, now=now - timedelta(hours=1))

    deleted = store.prune_older_than(hours=24, now=now)
    assert deleted == 1
    assert store.exists("old") is False
    assert store.exists("new") is True


def test_corrupt_profile_file_raises(store_dir):
    from faceid.store import FaceStore, CorruptProfileError  # to be implemented

    store = FaceStore(store_dir)
    user_id = "corrupt"

    # create corrupt profile file directly
    user_path = store._user_dir(user_id)  # allowed for test; implementation should exist
    user_path.mkdir(parents=True, exist_ok=True)
    (user_path / "profile.json").write_text("{ not valid json }", encoding="utf-8")

    with pytest.raises(CorruptProfileError):
        store.load_profile(user_id)
