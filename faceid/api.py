from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets
from typing import Any

from flask import Blueprint, current_app, jsonify, request, session

from .math import InvalidEmbeddingError, _as_float_list
from .store import CorruptProfileError, EnrollmentError, FaceStore, UserNotEnrolledError


def _store() -> FaceStore:
    root = current_app.config.get("FACEID_STORE_DIR", "instance/faceid_store")
    return FaceStore(root)


def create_faceid_blueprint(*, url_prefix: str = "/api/faceid") -> Blueprint:
    bp = Blueprint("faceid", __name__, url_prefix=url_prefix)

    @bp.route("/enroll", methods=["POST"])
    def enroll() -> Any:
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        embeddings = data.get("embeddings")
        if not user_id or embeddings is None:
            return jsonify({"error": "validation_error"}), 400

        try:
            prof = _store().enroll(user_id, embeddings=embeddings, min_samples=3)
        except (EnrollmentError, InvalidEmbeddingError, ValueError):
            return jsonify({"error": "validation_error"}), 400

        thr = (prof.get("stats") or {}).get("recommended_threshold")
        return (
            jsonify(
                {
                    "status": "ok",
                    "user_id": prof.get("user_id"),
                    "samples_added": len(prof.get("samples") or []),
                    "recommended_threshold": thr,
                }
            ),
            201,
        )

    @bp.route("/verify", methods=["POST"])
    def verify() -> Any:
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        embedding = data.get("embedding")
        if not user_id or embedding is None:
            return jsonify({"error": "validation_error"}), 400

        # Validate payload BEFORE revealing if user exists (and matches your unit tests)
        try:
            _as_float_list(embedding)
        except Exception:
            return jsonify({"error": "validation_error"}), 400

        try:
            res = _store().verify(user_id, embedding=embedding)
        except UserNotEnrolledError:
            return jsonify({"error": "user_not_enrolled"}), 404
        except (InvalidEmbeddingError, CorruptProfileError, ValueError):
            return jsonify({"error": "validation_error"}), 400

        return (
            jsonify(
                {
                    "user_id": res.user_id,
                    "match": bool(res.is_match),
                    "distance": float(res.distance),
                    "threshold": float(res.threshold),
                }
            ),
            200,
        )

    @bp.route("/challenge", methods=["GET"])
    def challenge() -> Any:
        # Minimal liveness: client must move face left/right after challenge is issued.
        token = secrets.token_urlsafe(16)
        direction = secrets.choice(["left", "right"])
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=45)).isoformat()
        session["faceid_challenge"] = {
            "token": token,
            "direction": direction,
            "expires_at": expires_at,
        }
        return (
            jsonify({"token": token, "direction": direction, "expires_in_seconds": 45}),
            200,
        )

    @bp.route("/login", methods=["POST"])
    def login() -> Any:
        """
        Client sends:
          { user_id, embedding, challenge_token, challenge_passed: true }
        If ok, we set session["faceid_user"] = user_id.
        Your app.py will then turn that into session["user_id"] (DB primary key) via /faceid/complete.
        """
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        embedding = data.get("embedding")
        token = data.get("challenge_token")
        passed = data.get("challenge_passed")

        if not user_id or embedding is None or not token or passed is not True:
            return jsonify({"error": "validation_error"}), 400

        try:
            _as_float_list(embedding)
        except Exception:
            return jsonify({"error": "validation_error"}), 400

        chall = session.get("faceid_challenge") or {}
        if token != chall.get("token"):
            return jsonify({"error": "liveness_failed"}), 403

        try:
            exp = datetime.fromisoformat(chall.get("expires_at"))
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
        except Exception:
            return jsonify({"error": "liveness_failed"}), 403

        if datetime.now(timezone.utc) > exp:
            return jsonify({"error": "liveness_failed"}), 403

        try:
            res = _store().verify(user_id, embedding=embedding)
        except UserNotEnrolledError:
            return jsonify({"error": "user_not_enrolled"}), 404
        except (InvalidEmbeddingError, CorruptProfileError, ValueError):
            return jsonify({"error": "validation_error"}), 400

        if not res.is_match:
            return (
                jsonify(
                    {
                        "error": "face_mismatch",
                        "distance": float(res.distance),
                        "threshold": float(res.threshold),
                    }
                ),
                401,
            )

        session.pop("faceid_challenge", None)
        session["faceid_user"] = res.user_id
        return jsonify({"status": "ok", "user_id": res.user_id}), 200

    return bp
