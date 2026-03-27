"""
Pytest Configuration and Fixtures для payments.

Содержит общие fixtures для всех тестов payments app.
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.fixture
def user(db):
    """
    Обычный пользователь для тестов.

    Returns:
        User: Пользователь со student ролью
    """
    from authentication.models import Role

    role, _ = Role.objects.get_or_create(name="student", defaults={"description": "Student role"})

    user = User.objects.create_user(
        email="student@example.com",
        first_name="Test",
        last_name="Student",
        password="TestPass123!",
        role=role,
    )
    return user


@pytest.fixture
def staff_user(db):
    """
    Staff пользователь для админки.

    Returns:
        User: Staff пользователь
    """
    from authentication.models import Role

    role, _ = Role.objects.get_or_create(name="manager", defaults={"description": "Manager role"})

    user = User.objects.create_user(
        email="manager@example.com",
        first_name="Test",
        last_name="Manager",
        password="TestPass123!",
        is_staff=True,
        role=role,
    )
    return user


@pytest.fixture
def course(db):
    """
    Тестовый курс с ценой.

    Returns:
        Course: Курс с базовыми параметрами
    """
    from django.utils.text import slugify

    from courses.models import Course

    return Course.objects.create(
        name="Test Course",
        slug=slugify("Test Course"),
        description="Test course description",
        price=Decimal("99.00"),
        status="active",
    )


@pytest.fixture
def client_logged_in(user):
    """
    Django test client с залогиненным пользователем.

    Returns:
        Client: Аутентифицированный клиент
    """
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def mock_paddle_client():
    """
    Mock Paddle API клиента.

    Returns:
        MagicMock: Мок объект Paddle Client
    """
    mock_client = MagicMock()

    # Mock transaction response
    mock_transaction = Mock()
    mock_transaction.id = "txn_test123"
    mock_transaction.status = "ready"
    mock_transaction.checkout = Mock()
    mock_transaction.checkout.url = "https://paddle.com/checkout/test"

    mock_client.transactions.create.return_value = mock_transaction

    # Mock customer response
    mock_customer = Mock()
    mock_customer.id = "ctm_test123"
    mock_customer.email = "test@example.com"

    mock_client.customers.create.return_value = mock_customer
    mock_client.customers.list.return_value = Mock(data=[])

    # Mock product response
    mock_product = Mock()
    mock_product.id = "pro_test123"
    mock_product.name = "Test Product"

    mock_client.products.create.return_value = mock_product
    mock_client.products.list.return_value = Mock(data=[])

    # Mock price response
    mock_price = Mock()
    mock_price.id = "pri_test123"
    mock_price.unit_price = Mock(amount="9900", currency_code="USD")

    mock_client.prices.create.return_value = mock_price

    return mock_client


@pytest.fixture
def mock_currency_api_response():
    """
    Mock ответ от exchangerate-api.com.

    Returns:
        dict: Мок данных курсов валют
    """
    return {
        "result": "success",
        "base_code": "USD",
        "conversion_rates": {
            "USD": 1.0,
            "EUR": 0.85,
            "RUB": 75.0,
            "GEL": 2.65,
        },
    }


@pytest.fixture
def mock_requests_get(mock_currency_api_response):
    """
    Mock requests.get для API курсов валют.

    Yields:
        MagicMock: Патченный requests.get
    """
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_currency_api_response
        mock_get.return_value = mock_response
        yield mock_get
