import os


class BaseConfig:
    def __init__(self):
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        self.PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Api Startkit")
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
        self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./src/local.db")
