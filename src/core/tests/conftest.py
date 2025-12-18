"""
Pytest fixtures для тестов core.

Содержит общие fixtures для всех тестов модуля.
"""

import pytest
from ninja.testing import TestClient

from core.api import router as core_router


@pytest.fixture(scope="session")
def api_client():
    """
    Клиент для тестирования API core endpoints.

    Использует отдельный TestClient(core_router) для изоляции core tests.
    """
    return TestClient(core_router)
