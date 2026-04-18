import os
from pathlib import Path


def _load_local_env() -> None:
    """
    Load a local .env file into os.environ without overriding real env vars.

    Render and other hosts should keep using their dashboard/runtime env vars.
    This is only a lightweight local fallback for development.
    """
    env_path = Path(__file__).resolve().with_name(".env")
    if not env_path.is_file():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key[7:].strip()

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]

        os.environ.setdefault(key, value)


_load_local_env()


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    DATABASE_URL = os.environ.get("NEON_DATABASE_URL") or os.environ.get("DATABASE_URL")  # optional
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FACEID_STORE_DIR = os.environ.get("FACEID_STORE_DIR")

    TASK_TOKEN = os.environ.get("TASK_TOKEN")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
