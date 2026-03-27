"""
Payments Application Configuration

Django app config for payment processing module.
"""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """
    Configuration for Payments application.

    Features:
        - Paddle Billing integration for course purchases
        - Multi-currency support (USD, EUR, RUB, GEL)
        - Dynamic exchange rates with auto-updates (hourly)
        - Automatic student enrollment on payment completion
        - Webhook handling for payment status updates

    Environment Variables Required:
        - PADDLE_SANDBOX_API_KEY: Sandbox API key for testing
        - PADDLE_API_KEY: Production API key
        - PADDLE_ENVIRONMENT: 'sandbox' or 'production'
        - PADDLE_WEBHOOK_SECRET: Secret for webhook verification
        - EXCHANGE_RATE_API_KEY: (Optional) API key for currency rates

    Related Apps:
        - authentication: User model
        - courses: Course model
        - students: Student enrollments
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"
    verbose_name = "Payment Processing"

    def ready(self) -> None:
        """
        Initialize payment app when Django starts.

        Currently no signals or startup hooks needed.
        Paddle service is initialized lazily on first use.
        """
        pass
