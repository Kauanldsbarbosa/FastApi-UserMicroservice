import os

from .base_config import BaseConfig


class TestConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.DATABASE_URL = (
            f'sqlite:///{os.path.join(os.getcwd(), "test_db.sqlite")}'
        )
        self.AUTH_TOKEN_EXPIRES = os.getenv(
            'AUTH_TOKEN_EXPIRES',
            '30'
            )
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'test_secret_key')
        self.ALGORITHM = os.getenv('ALGORITHM', 'HS256')
