from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .math import InvalidEmbeddingError, _as_float_list
from .profile import compute_profile_stats


class EnrollmentError(ValueError):
    pass


class UserNotEnrolledError(FileNotFoundError):
    pass


class CorruptProfileError(ValueError):
    pass


@dataclass(frozen=True)
class VerifyResult:
    user_id: str
    is_match: bool
    distance: float
    threshold: float


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _require_safe_user_id(user_id: str) -> str:
    if not isinstance(user_id, str):
        raise ValueError("user_id must be a string")
    user_id = user_id.strip()
    if not user_id:
        raise ValueError("user_id required")

    if "/" in user_id or "\\" in user_id or ".." in user_id:
        raise ValueError("Invalid user_id")

    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", user_id):
        raise ValueError("Invalid user_id format")

    return user_id


def _euclidean(a: List[float], b: List[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


class FaceStore:
    def __init__(self, root_dir: Path | str):
        self.root_dir = Path(root_dir)

    def _user_dir(self, user_id: str) -> Path:
        uid = _require_safe_user_id(user_id)
        return self.root_dir / uid

    def _profile_path(self, user_id: str) -> Path:
        return self._user_dir(user_id) / "profile.json"

    def exists(self, user_id: str) -> bool:
        try:
            p = self._profile_path(user_id)
        except ValueError:
            return False
        return p.exists()

    def enroll(
        self,
        user_id: str,
        embeddings: List[Iterable[float]],
        *,
        min_samples: int = 3,
        base_threshold: float = 0.35,
        now: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        uid = _require_safe_user_id(user_id)

        if embeddings is None:
            raise EnrollmentError("embeddings required")
        if len(embeddings) < int(min_samples):
            raise EnrollmentError(f"Need at least {min_samples} samples")

        vecs = [_as_float_list(v) for v in embeddings]
        stats = compute_profile_stats(vecs, base_threshold=base_threshold)

        profile = {
            "user_id": uid,
            "created_at": (now or _utc_now()).astimezone(timezone.utc).isoformat(),
            "samples": vecs,
            "stats": stats,
        }

        user_dir = self._user_dir(uid)
        user_dir.mkdir(parents=True, exist_ok=True)

        tmp = user_dir / "profile.json.tmp"
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(profile, f)
        tmp.replace(self._profile_path(uid))

        return profile

    def load_profile(self, user_id: str) -> Dict[str, Any]:
        uid = _require_safe_user_id(user_id)
        path = self._profile_path(uid)
        if not path.exists():
            raise UserNotEnrolledError(uid)

        try:
            raw = path.read_text(encoding="utf-8")
            profile = json.loads(raw)
        except UserNotEnrolledError:
            raise
        except Exception as e:
            raise CorruptProfileError("profile.json is corrupt") from e

        if not isinstance(profile, dict):
            raise CorruptProfileError("Invalid profile format")

        return profile

    def verify(
        self, user_id: str, embedding: Iterable[float], *, base_threshold: float = 0.35
    ) -> VerifyResult:
        uid = _require_safe_user_id(user_id)
        prof = self.load_profile(uid)

        vec = _as_float_list(embedding)
        stats = prof.get("stats") or {}
        centroid = stats.get("centroid")

        if not isinstance(centroid, list):
            samples = prof.get("samples") or []
            if not samples:
                raise CorruptProfileError("Missing centroid and samples")
            centroid = compute_profile_stats(samples, base_threshold=base_threshold)[
                "centroid"
            ]

        if len(vec) != len(centroid):
            raise InvalidEmbeddingError("Embedding length mismatch")

        distance = _euclidean(vec, centroid)

        recommended = stats.get("recommended_threshold")
        try:
            recommended_f = float(recommended)
        except Exception:
            recommended_f = float(base_threshold)

        threshold = max(float(base_threshold), recommended_f)
        return VerifyResult(
            user_id=uid,
            is_match=(distance <= threshold),
            distance=distance,
            threshold=threshold,
        )

    def prune_older_than(
        self, *, hours: int = 24, now: Optional[datetime] = None
    ) -> int:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        now_dt = (now or _utc_now()).astimezone(timezone.utc)
        cutoff = now_dt - timedelta(hours=int(hours))
        deleted = 0

        for child in self.root_dir.iterdir():
            if not child.is_dir():
                continue

            profile_path = child / "profile.json"
            if not profile_path.exists():
                continue

            try:
                prof = self.load_profile(child.name)
                created_at = prof.get("created_at")
                created_dt = datetime.fromisoformat(created_at)
                if created_dt.tzinfo is None:
                    created_dt = created_dt.replace(tzinfo=timezone.utc)
            except Exception:
                self._delete_dir(child)
                deleted += 1
                continue

            if created_dt <= cutoff:
                self._delete_dir(child)
                deleted += 1

        return deleted

    def delete(self, user_id: str) -> None:
        uid = _require_safe_user_id(user_id)
        d = self._user_dir(uid)
        if d.exists():
            self._delete_dir(d)

    @staticmethod
    def _delete_dir(path: Path) -> None:
        for p in sorted(path.rglob("*"), reverse=True):
            try:
                if p.is_file() or p.is_symlink():
                    p.unlink(missing_ok=True)
                else:
                    p.rmdir()
            except Exception:
                pass
        try:
            path.rmdir()
        except Exception:
            pass
