import os

from .base_config import BaseConfig


class TestConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.DATABASE_URL = (
            f'sqlite:///{os.path.join(os.getcwd(), "test_db.sqlite")}'
        )
