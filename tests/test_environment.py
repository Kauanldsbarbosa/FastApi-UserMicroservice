import asyncio
import pytest
from app.config.settings import get_config


def test_environment():
    assert get_config().DATABASE_URL.startswith('sqlite')
