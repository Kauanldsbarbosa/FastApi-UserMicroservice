from .base_config import BaseConfig
import os


class DevelopmentConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://apistartkit_user:supersecurepassword@db:5432/apistartkit_db"
        )