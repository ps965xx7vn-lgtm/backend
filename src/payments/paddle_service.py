"""
Paddle Service Module - Сервис для работы с Paddle Billing API.

Этот модуль предоставляет методы для интеграции с платежной системой Paddle:
- Создание транзакций
- Создание checkout сессий
- Получение информации о платежах
- Обработка webhook событий
- Работа с продуктами и ценами

Использует официальный Paddle Python SDK (paddle-python-sdk).

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

import json
import logging
import re
import threading
from decimal import Decimal
from enum import Enum
from typing import Any, Final, cast
from uuid import UUID

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from paddle_billing import Client, Environment, Options
from paddle_billing.Entities.Shared import CurrencyCode, Money, TaxCategory, TaxMode
from paddle_billing.Notifications import Secret, Verifier
from paddle_billing.Resources.ClientTokens.Operations import CreateClientToken
from paddle_billing.Resources.Prices.Operations import CreatePrice
from paddle_billing.Resources.Products.Operations import CreateProduct, ListProducts
from paddle_billing.Resources.Transactions.Operations import CreateTransaction
from paddle_billing.Resources.Transactions.Operations.Create import TransactionCreateItem

logger = logging.getLogger(__name__)


# Constants
class PaddleEnvironment(str, Enum):
    """Типы окружений Paddle."""

    SANDBOX = "sandbox"
    PRODUCTION = "production"


class PaddleError(Exception):
    """Базовое исключение для ошибок Paddle сервиса."""

    pass


class CustomerCreationError(PaddleError):
    """Возникает при ошибке создания покупателя."""

    pass


class TransactionCreationError(PaddleError):
    """Возникает при ошибке создания транзакции."""

    pass


class ProductCreationError(PaddleError):
    """Возникает при ошибке создания продукта."""

    pass


# Constants for timeouts and limits
CLIENT_TOKEN_NAME_MAX_LENGTH: Final[int] = 200
CUSTOMER_ID_PATTERN: Final[str] = r"ctm_[a-z0-9]+"
AMOUNT_TO_CENTS_MULTIPLIER: Final[int] = 100
CLIENT_TOKEN_LOG_LENGTH: Final[int] = 20


class PaddleService:
    """
    Сервис для работы с Paddle Billing API через официальный SDK.

    Управляет созданием платежей, работой с продуктами и обработкой событий.
    """

    def __init__(self) -> None:
        """Инициализация клиента Paddle с настройками из .env.

        Raises:
            ImproperlyConfigured: Если отсутствуют необходимые настройки.
        """
        env_str = getattr(settings, "PADDLE_ENVIRONMENT", PaddleEnvironment.SANDBOX)

        try:
            self.environment = PaddleEnvironment(env_str)
        except ValueError:
            raise ImproperlyConfigured(
                f"Invalid PADDLE_ENVIRONMENT: {env_str}. "
                f"Must be one of: {', '.join([e.value for e in PaddleEnvironment])}"
            ) from None

        api_key = self._get_api_key()
        if not api_key:
            raise ImproperlyConfigured("Set PADDLE_SANDBOX_API_KEY or PADDLE_API_KEY in settings.")

        env = (
            Environment.SANDBOX
            if self.environment == PaddleEnvironment.SANDBOX
            else Environment.PRODUCTION
        )
        self.client = Client(api_key, options=Options(environment=env))

        logger.info(
            "Paddle service initialized",
            extra={"environment": self.environment.value, "api_key_length": len(api_key)},
        )

    def _get_api_key(self) -> str:
        """Получить API ключ для текущего окружения.

        Returns:
            API ключ для текущего окружения.
        """
        if self.environment == PaddleEnvironment.SANDBOX:
            return getattr(settings, "PADDLE_SANDBOX_API_KEY", "")
        return getattr(settings, "PADDLE_API_KEY", "")

    def create_transaction(
        self,
        course_id: int | UUID,
        course_name: str,
        amount: Decimal,
        currency: str,
        user_email: str,
        user_id: int,
        success_url: str | None = None,
        cancel_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Создать транзакцию в Paddle.

        Args:
            course_id: ID курса (int или UUID)
            course_name: Название курса
            amount: Сумма платежа
            currency: Валюта (USD, EUR, RUB, GEL и т.д.)
            user_email: Email пользователя
            user_id: ID пользователя
            success_url: URL для успешной оплаты
            cancel_url: URL для отмены

        Returns:
            dict: Данные транзакции с client_token и transaction_id

        Raises:
            TransactionCreationError: При ошибке создания транзакции
            ValueError: При невалидных входных данных
        """
        self._validate_transaction_inputs(
            course_id, course_name, amount, currency, user_email, user_id
        )

        try:
            amount_cents = str(int(amount * AMOUNT_TO_CENTS_MULTIPLIER))

            customer_id = self._get_or_create_customer(user_email, user_id)

            product_id = self._get_or_create_product(course_id, course_name)

            price_id = self._create_price(product_id, amount_cents, currency, course_name)

            logger.info(
                "Creating Paddle transaction",
                extra={
                    "product_id": product_id,
                    "price_id": price_id,
                    "amount": str(amount),
                    "currency": currency,
                    "customer_id": customer_id,
                },
            )

            items = [
                TransactionCreateItem(
                    price_id=price_id,
                    quantity=1,
                )
            ]

            create_operation = CreateTransaction(
                items=items,
                customer_id=customer_id,
                custom_data={
                    "course_id": str(course_id),
                    "user_id": str(user_id),
                    "course_name": course_name,
                },
            )

            transaction = self.client.transactions.create(create_operation)

            logger.info(
                "Paddle transaction created successfully",
                extra={
                    "transaction_id": transaction.id,
                    "user_email": user_email,
                },
            )

            client_token = self._create_client_token(transaction.id, course_name, user_email)

            status = self._extract_status(transaction.status)

            return {
                "transaction_id": transaction.id,
                "status": status,
                "checkout_url": None,
                "client_token": client_token,
                "customer_id": str(transaction.customer_id) if transaction.customer_id else None,
                "amount": str(amount),
                "currency": currency,
                "product_id": product_id,
                "price_id": price_id,
            }

        except (CustomerCreationError, ProductCreationError) as e:
            raise TransactionCreationError(f"Failed to create transaction: {e}") from e
        except Exception as e:
            logger.error(
                "Failed to create Paddle transaction",
                extra={"error": str(e), "user_email": user_email},
                exc_info=True,
            )
            raise TransactionCreationError(f"Transaction creation failed: {e}") from e

    def _validate_transaction_inputs(
        self,
        course_id: int | UUID,
        course_name: str,
        amount: Decimal,
        currency: str,
        user_email: str,
        user_id: int,
    ) -> None:
        """Валидация входных параметров транзакции.

        Raises:
            ValueError: Если любой параметр невалиден.
        """
        if isinstance(course_id, int) and course_id <= 0:
            raise ValueError(f"Invalid course_id: {course_id}")
        elif not isinstance(course_id, (int, UUID)):
            raise ValueError(f"course_id must be int or UUID, got {type(course_id)}")

        if not course_name or not course_name.strip():
            raise ValueError("course_name cannot be empty")

        if amount <= 0:
            raise ValueError(f"Invalid amount: {amount}")

        if not currency or len(currency) != 3:
            raise ValueError(f"Invalid currency code: {currency}")

        if not user_email or "@" not in user_email:
            raise ValueError(f"Invalid email: {user_email}")

        if user_id <= 0:
            raise ValueError(f"Invalid user_id: {user_id}")

    def _extract_status(self, status: Any) -> str:
        """Извлечь строку статуса из enum Paddle SDK.

        Args:
            status: Статус из Paddle транзакции.

        Returns:
            Статус в виде строки.
        """
        if hasattr(status, "value"):
            return str(status.value)
        return str(status)

    def _create_client_token(
        self, transaction_id: str, course_name: str, user_email: str
    ) -> str | None:
        """Создать client token для Paddle.js checkout.

        Args:
            transaction_id: ID транзакции.
            course_name: Название курса для описания.
            user_email: Email пользователя для описания.

        Returns:
            Client token или None при ошибке создания.
        """
        try:
            token_name = f"Checkout for transaction {transaction_id}"
            if len(token_name) > CLIENT_TOKEN_NAME_MAX_LENGTH:
                token_name = token_name[:CLIENT_TOKEN_NAME_MAX_LENGTH]

            client_token_operation = CreateClientToken(
                name=token_name,
                description=f"Client token for {course_name} purchase by {user_email}",
            )
            client_token_response = self.client.client_tokens.create(client_token_operation)
            client_token = client_token_response.token

            logger.info(
                "Client token created for Paddle.js",
                extra={"token_preview": client_token[:CLIENT_TOKEN_LOG_LENGTH]},
            )
            return cast(str, client_token)

        except Exception as e:
            logger.error(
                "Failed to create client token",
                extra={"error": str(e), "transaction_id": transaction_id},
                exc_info=True,
            )
            return None

    def _get_or_create_customer(self, email: str, user_id: int) -> str:
        """
        Получить или создать customer в Paddle.

        Args:
            email: Email пользователя
            user_id: ID пользователя в нашей системе

        Returns:
            str: Customer ID

        Raises:
            CustomerCreationError: При ошибке создания customer.
        """
        try:
            from paddle_billing.Exceptions.ApiErrors.CustomerApiError import CustomerApiError
            from paddle_billing.Resources.Customers.Operations import CreateCustomer

            existing_customer = self._find_existing_customer(email)
            if existing_customer:
                return existing_customer

            customer = self.client.customers.create(
                CreateCustomer(
                    email=email,
                    custom_data={
                        "user_id": str(user_id),
                    },
                )
            )

            logger.info(
                "New Paddle customer created", extra={"customer_id": customer.id, "email": email}
            )
            return cast(str, customer.id)

        except CustomerApiError as e:
            customer_id = self._extract_customer_id_from_error(str(e))
            if customer_id:
                logger.info(
                    "Customer already exists", extra={"customer_id": customer_id, "email": email}
                )
                return customer_id

            logger.error(
                "Failed to create Paddle customer",
                extra={"error": str(e), "email": email},
                exc_info=True,
            )
            raise CustomerCreationError(f"Customer creation failed: {e}") from e

        except Exception as e:
            logger.error(
                "Unexpected error working with Paddle customer",
                extra={"error": str(e), "email": email},
                exc_info=True,
            )
            raise CustomerCreationError(f"Customer operation failed: {e}") from e

    def _find_existing_customer(self, email: str) -> str | None:
        """Найти существующего покупателя по email.

        Args:
            email: Email покупателя.

        Returns:
            Customer ID если найден, иначе None.
        """
        try:
            from paddle_billing.Resources.Customers.Operations import ListCustomers

            customers = self.client.customers.list(ListCustomers(email=email))

            for customer in customers:
                logger.info(
                    "Found existing Paddle customer",
                    extra={"customer_id": customer.id, "email": email},
                )
                return cast(str, customer.id)

        except Exception as e:
            logger.debug("Failed to find customer", extra={"error": str(e), "email": email})

        return None

    def _extract_customer_id_from_error(self, error_msg: str) -> str | None:
        """Извлечь customer ID из сообщения об ошибке Paddle API.

        Args:
            error_msg: Сообщение об ошибке от Paddle API.

        Returns:
            Customer ID если найден в ошибке, иначе None.
        """
        if "conflicts with customer of id" in error_msg:
            match = re.search(CUSTOMER_ID_PATTERN, error_msg)
            if match:
                return match.group(0)
        return None

    def _find_existing_product(self, course_name: str) -> str | None:
        """
        Найти существующий активный продукт по названию курса.

        Args:
            course_name: Название курса для поиска

        Returns:
            Product ID если найден, иначе None
        """
        try:
            products_response = self.client.products.list(
                ListProducts(
                    status=["active"],
                )
            )

            for product in products_response:
                if product.name == course_name:
                    logger.info(
                        "Found existing product by name",
                        extra={"product_id": product.id, "name": course_name},
                    )
                    return cast(str, product.id)

            return None

        except Exception as e:
            logger.warning(
                "Failed to search for existing products",
                extra={"error": str(e), "course_name": course_name},
            )
            return None

    def _get_or_create_product(self, course_id: int | UUID, course_name: str) -> str:
        """
        Получить или создать product в Paddle для курса.

        Сначала ищет существующий активный продукт по названию курса.
        Если не находит - создает новый.

        Args:
            course_id: ID курса (int или UUID)
            course_name: Название курса

        Returns:
            str: Product ID

        Raises:
            ProductCreationError: При ошибке создания product.
        """
        try:
            existing_product = self._find_existing_product(course_name)
            if existing_product:
                logger.info(
                    "Found existing Paddle product",
                    extra={"product_id": existing_product, "course_id": str(course_id)},
                )
                return existing_product

            product = self.client.products.create(
                CreateProduct(
                    name=course_name,
                    tax_category=TaxCategory.Standard,
                    description=f"Курс {course_name}",
                    custom_data={
                        "course_id": str(course_id),
                    },
                )
            )

            logger.info(
                "Paddle product created",
                extra={"product_id": product.id, "course_id": str(course_id)},
            )
            return cast(str, product.id)

        except Exception as e:
            logger.error(
                "Failed to create Paddle product",
                extra={"error": str(e), "course_id": course_id},
                exc_info=True,
            )
            raise ProductCreationError(f"Product creation failed: {e}") from e

    def _create_price(
        self, product_id: str, amount_cents: str, currency: str, description: str
    ) -> str:
        """
        Создать price для продукта.

        Args:
            product_id: ID продукта в Paddle
            amount_cents: Сумма в центах
            currency: Валюта
            description: Описание

        Returns:
            str: Price ID

        Raises:
            ProductCreationError: При ошибке создания price.
        """
        try:
            price = self.client.prices.create(
                CreatePrice(
                    description=f"Price for {description}",
                    product_id=product_id,
                    unit_price=Money(
                        amount=amount_cents,
                        currency_code=CurrencyCode(currency),
                    ),
                    tax_mode=TaxMode.AccountSetting,
                )
            )

            logger.info(
                "Paddle price created",
                extra={
                    "price_id": price.id,
                    "product_id": product_id,
                    "amount_cents": amount_cents,
                    "currency": currency,
                },
            )
            return cast(str, price.id)

        except Exception as e:
            logger.error(
                "Failed to create Paddle price",
                extra={
                    "error": str(e),
                    "product_id": product_id,
                    "currency": currency,
                },
                exc_info=True,
            )
            raise ProductCreationError(f"Price creation failed: {e}") from e

    def get_transaction(self, transaction_id: str) -> dict[str, Any]:
        """
        Получить информацию о транзакции.

        Args:
            transaction_id: ID транзакции в Paddle

        Returns:
            dict: Данные транзакции
        """
        try:
            transaction = self.client.transactions.get(transaction_id)

            total_amount = None
            if hasattr(transaction, "details") and transaction.details:
                if hasattr(transaction.details, "totals") and transaction.details.totals:
                    total_amount = transaction.details.totals.total

            status = (
                str(transaction.status)
                if hasattr(transaction.status, "value")
                else str(transaction.status)
            )

            return {
                "transaction_id": transaction.id,
                "status": status,
                "customer_id": str(transaction.customer_id) if transaction.customer_id else None,
                "amount": total_amount,
                "currency": (
                    str(transaction.currency_code)
                    if hasattr(transaction.currency_code, "value")
                    else str(transaction.currency_code)
                ),
                "created_at": (
                    str(transaction.created_at) if hasattr(transaction, "created_at") else None
                ),
                "updated_at": (
                    str(transaction.updated_at) if hasattr(transaction, "updated_at") else None
                ),
                "custom_data": (
                    transaction.custom_data if hasattr(transaction, "custom_data") else None
                ),
            }

        except Exception as e:
            logger.error(f"Ошибка при получении Paddle транзакции {transaction_id}: {e}")
            raise

    def verify_webhook(self, request_body: bytes, signature: str) -> dict[str, Any] | None:
        """
        Проверить и распарсить webhook от Paddle.

        Args:
            request_body: Тело запроса (raw bytes)
            signature: Paddle-Signature из заголовков

        Returns:
            dict: Данные события или None при ошибке верификации
        """
        try:
            secret_key = settings.PADDLE_WEBHOOK_SECRET

            if not secret_key:
                logger.warning("PADDLE_WEBHOOK_SECRET не установлен")
                if settings.DEBUG:
                    return cast(dict[str, Any], json.loads(request_body.decode("utf-8")))
                return None

            secret = Secret(secret_key)
            verifier = Verifier()

            if not verifier.verify(request_body, secret, signature):
                logger.warning("Paddle webhook signature verification failed")
                return None

            event_data = json.loads(request_body.decode("utf-8"))

            logger.info(f"Получен webhook от Paddle: {event_data.get('event_type')}")

            return cast(dict[str, Any], event_data)

        except Exception as e:
            logger.error(f"Ошибка при верификации Paddle webhook: {e}")
            return None


# Singleton instance with thread-safe initialization
_paddle_service: PaddleService | None = None
_paddle_service_lock = threading.Lock()


def get_paddle_service() -> PaddleService:
    """
    Получить thread-safe singleton instance PaddleService.

    Использует double-checked locking pattern для потокобезопасности.

    Returns:
        PaddleService: Экземпляр сервиса

    Example:
        >>> service = get_paddle_service()
        >>> transaction = service.create_transaction(...)
    """
    global _paddle_service

    if _paddle_service is None:
        with _paddle_service_lock:
            if _paddle_service is None:
                _paddle_service = PaddleService()
                logger.info("PaddleService singleton initialized")

    return _paddle_service


__all__ = [
    "PaddleService",
    "get_paddle_service",
    "PaddleEnvironment",
    "PaddleError",
    "CustomerCreationError",
    "TransactionCreationError",
    "ProductCreationError",
]
