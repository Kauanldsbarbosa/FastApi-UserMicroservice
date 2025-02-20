import os

from app.config.dev import DevelopmentConfig
from app.config.test import TestConfig


def get_config():
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env == "test":
        return TestConfig()
    return DevelopmentConfig()
