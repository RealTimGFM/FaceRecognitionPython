import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    DATABASE_URL = os.environ.get("DATABASE_URL")  # optional
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FACEID_STORE_DIR = os.environ.get("FACEID_STORE_DIR")

    TASK_TOKEN = os.environ.get("TASK_TOKEN")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
