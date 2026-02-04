"""
QR Code Generator with Logo/Icon inside

Генерирует QR-коды с логотипом в центре для сертификатов.
"""

import io
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_qr_with_logo(url: str, logo_path: str = None, size: int = 300) -> io.BytesIO:
    """
    Генерировать QR-код с логотипом в центре.

    Args:
        url: URL для кодирования в QR
        logo_path: Путь к файлу логотипа (PNG/JPG)
        size: Размер QR-кода в пикселях

    Returns:
        BytesIO: Изображение QR-кода в памяти
    """
    try:
        import qrcode
        from PIL import Image

        # Создать QR-код с высокой коррекцией ошибок (необходимо для логотипа)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% восстановление
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Создать изображение
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # Если есть логотип, добавить его в центр
        if logo_path and Path(logo_path).exists():
            try:
                logo = Image.open(logo_path)

                # Рассчитать размер логотипа (20% от QR-кода)
                qr_width, qr_height = qr_img.size
                logo_size = int(qr_width * 0.25)

                # Изменить размер логотипа
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

                # Создать белый фон для логотипа
                logo_bg_size = int(logo_size * 1.1)
                logo_bg = Image.new("RGB", (logo_bg_size, logo_bg_size), "white")

                # Вставить логотип на белый фон
                logo_pos = ((logo_bg_size - logo_size) // 2, (logo_bg_size - logo_size) // 2)
                if logo.mode == "RGBA":
                    logo_bg.paste(logo, logo_pos, logo)
                else:
                    logo_bg.paste(logo, logo_pos)

                # Вставить логотип в центр QR-кода
                logo_position = ((qr_width - logo_bg_size) // 2, (qr_height - logo_bg_size) // 2)
                qr_img.paste(logo_bg, logo_position)

                logger.info(f"Added logo to QR code from: {logo_path}")

            except Exception as e:
                logger.warning(f"Failed to add logo to QR code: {e}. Using plain QR.")

        # Изменить размер до нужного
        qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)

        # Сохранить в BytesIO
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    except ImportError as e:
        logger.error("qrcode and/or Pillow not installed. Install: poetry add qrcode pillow")
        raise ImportError(
            "qrcode и Pillow требуются для генерации QR. Установите: poetry add qrcode pillow"
        ) from e
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        raise
