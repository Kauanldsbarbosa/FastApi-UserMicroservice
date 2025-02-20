from .base_config import BaseConfig
import os


class TestConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.DATABASE_URL = "sqlite:///./test.db"

