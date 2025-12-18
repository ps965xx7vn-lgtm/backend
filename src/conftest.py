"""
Корневой conftest.py для всех тестов проекта.

Содержит общие fixtures, доступные во всех тестах.
"""

import pytest
from ninja.testing import TestClient

from pyland.api import api


@pytest.fixture(scope="session")
def api_client():
    """
    Session-level fixture для тестового API клиента.

    Создается один раз для всей тестовой сессии, чтобы избежать
    ошибки "Already registered: pyland_api" от Django Ninja.
    """
    return TestClient(api)
