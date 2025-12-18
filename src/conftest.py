"""
Корневой conftest.py для всех тестов проекта.

Содержит общие fixtures, доступные во всех тестах.
"""

import pytest
from ninja.testing import TestClient


@pytest.fixture(scope="session")
def api_client():
    """
    Session-level fixture для тестового API клиента.

    Создается один раз для всей тестовой сессии, чтобы избежать
    ошибки "Already registered: pyland_api" от Django Ninja.
    """
    from pyland.api import api

    return TestClient(api)
