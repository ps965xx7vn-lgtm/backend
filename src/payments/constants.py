"""
Payments Constants Module - Константы для платежной интеграции.

Содержит константы для CSP политик, Paddle доменов и других настроек.

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

from typing import Final

PADDLE_SCRIPT_SRC: Final[tuple[str, ...]] = (
    "https://cdn.paddle.com",
    "https://sandbox-cdn.paddle.com",
)

PADDLE_STYLE_SRC: Final[tuple[str, ...]] = (
    "https://cdn.paddle.com",
    "https://sandbox-cdn.paddle.com",
)

PADDLE_CONNECT_SRC: Final[tuple[str, ...]] = (
    "https://api.paddle.com",
    "https://sandbox-api.paddle.com",
    "https://cdn.paddle.com",
    "https://sandbox-cdn.paddle.com",
    "https://checkout.paddle.com",
    "https://sandbox-checkout.paddle.com",
    "https://buy.paddle.com",
    "https://sandbox-buy.paddle.com",
)

PADDLE_FRAME_SRC: Final[tuple[str, ...]] = (
    "https://checkout.paddle.com",
    "https://sandbox-checkout.paddle.com",
    "https://cdn.paddle.com",
    "https://sandbox-cdn.paddle.com",
    "https://buy.paddle.com",
    "https://sandbox-buy.paddle.com",
)


def build_paddle_csp_directive(directive: str, base_sources: str = "'self'") -> str:
    """
    Построить CSP директиву с Paddle доменами.

    Args:
        directive: Тип директивы (script-src, style-src, etc.)
        base_sources: Базовые источники (по умолчанию 'self')

    Returns:
        Строка CSP директивы с всеми необходимыми источниками.

    Example:
        >>> build_paddle_csp_directive('script-src', "'self' 'unsafe-inline'")
        "script-src 'self' 'unsafe-inline' https://cdn.paddle.com ..."
    """
    sources_map = {
        "script-src": PADDLE_SCRIPT_SRC,
        "style-src": PADDLE_STYLE_SRC,
        "connect-src": PADDLE_CONNECT_SRC,
        "frame-src": PADDLE_FRAME_SRC,
    }

    directive_type = directive.split()[0]
    sources = sources_map.get(directive_type, ())

    return f"{directive} {base_sources} {' '.join(sources)}"


def get_full_paddle_csp(
    img_src: str = "'self' data: https:",
    font_src: str = "'self' data:",
    frame_ancestors: str = "'none'",
) -> str:
    """
    Получить полную CSP политику с поддержкой Paddle.

    Args:
        img_src: Источники изображений.
        font_src: Источники шрифтов.
        frame_ancestors: Политика вложения в iframe.

    Returns:
        Полная CSP политика строка.
    """
    style_directive = build_paddle_csp_directive("style-src", "'self' 'unsafe-inline'")
    script_directive = build_paddle_csp_directive("script-src", "'self' 'unsafe-inline'")
    connect_directive = build_paddle_csp_directive("connect-src", "'self'")
    frame_directive = build_paddle_csp_directive("frame-src", "")

    return (
        f"default-src 'self'; "
        f"img-src {img_src}; "
        f"{style_directive}; "
        f"{script_directive}; "
        f"font-src {font_src}; "
        f"{connect_directive}; "
        f"{frame_directive}; "
        f"frame-ancestors {frame_ancestors};"
    )


__all__ = [
    "PADDLE_SCRIPT_SRC",
    "PADDLE_STYLE_SRC",
    "PADDLE_CONNECT_SRC",
    "PADDLE_FRAME_SRC",
    "build_paddle_csp_directive",
    "get_full_paddle_csp",
]
