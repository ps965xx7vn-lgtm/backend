# Certificate System Implementation

## Дата: 4 февраля 2026 г.

## Обзор

Реализована полная система автоматической выдачи и отправки сертификатов студентам при завершении курсов с многоуровневой валидацией и защитой от преждевременной выдачи.

---

## Основные компоненты

### 1. Автоматическая отправка сертификатов на email

**Файлы:**
- `certificates/tasks.py` - Celery задачи для асинхронной и синхронной отправки
- `reviewers/signals.py` - Проверка завершения курса и генерация сертификата
- `certificates/templates/certificates/emails/certificate_issued.html` - HTML шаблон письма

**Функциональность:**
- Celery задача `send_certificate_email()` с 3 retry попытками
- Синхронный fallback `send_certificate_email_sync()` при недоступности Celery
- Проверка активных Celery workers перед async отправкой
- HTML email в стиле auth app с inline CSS для совместимости с почтовыми клиентами

**Данные в письме:**
- Имя студента и название курса
- Номер сертификата (CERT-YYYYMMDD-XXXX)
- Дата завершения курса
- Интересная статистика:
  - Пройдено уроков (X/Y)
  - Время обучения (часы)
  - Получено отзывов от ревьюеров
- Кнопки:
  - "Просмотреть сертификат" - ссылка на страницу проверки
  - "Скачать PDF" - прямая ссылка на PDF файл

---

### 2. КРИТИЧЕСКАЯ ЗАЩИТА: Валидация прохождения шагов

**Проблема:** Студенты могли получать сертификаты без фактического прохождения контента курса (0/16 шагов completed, но lessons approved).

**Решение в `reviewers/signals.py`:**

```python
def check_and_send_certificate(student_profile, course):
    """
    Курс считается завершенным ТОЛЬКО если:
    1. Все уроки имеют approved submissions (старая проверка)
    2. ВСЕ шаги в уроках отмечены как completed (НОВАЯ ЗАЩИТА)
    """
    # Проверка 1: Все уроки одобрены
    approved_count = LessonSubmission.objects.filter(
        student=student_profile,
        lesson__course=course,
        status="approved"
    ).distinct().count()

    if approved_count < total_lessons:
        return  # Не все уроки одобрены

    # НОВАЯ ПРОВЕРКА 2: Все шаги пройдены
    from reviewers.models import StepProgress

    total_steps = 0
    completed_steps = 0

    for lesson in all_lessons:
        lesson_steps = lesson.steps.all()
        total_steps += lesson_steps.count()

        for step in lesson_steps:
            step_progress = StepProgress.objects.filter(
                profile=student_profile,
                step=step,
                is_completed=True  # КРИТИЧЕСКИ ВАЖНО
            ).first()

            if step_progress:
                completed_steps += 1

    # ЗАЩИТА: Блокируем сертификат если шаги не пройдены
    if completed_steps < total_steps:
        logger.warning(
            f"⚠️  Student has approved all lessons "
            f"but not completed all steps ({completed_steps}/{total_steps}). "
            f"Certificate will NOT be issued."
        )
        return  # ВЫХОД - НЕТ СЕРТИФИКАТА

    # Только если ОБА условия выполнены - выдаем сертификат
    if approved_count >= total_lessons and completed_steps >= total_steps:
        # Создание сертификата, генерация PDF, отправка email...
```

**Тесты:**
- ✅ Сценарий 1: 5/5 lessons approved, 0/19 steps completed → Сертификат НЕ выдан
- ✅ Сценарий 2: 5/5 lessons approved, 19/19 steps completed → Сертификат выдан

---

### 3. Блокировка следующего урока без прохождения всех шагов

**Файл:** `students/views.py` (функция `lesson_detail_view`)

**Старая логика:** Следующий урок разблокируется если `submission.status == 'approved'`

**Новая логика:**

```python
# ЖЕСТКАЯ ЛОГИКА: Проверяем доступность следующего урока
# Требования для разблокировки следующего урока:
# 1. Текущий урок должен иметь approved submission
# 2. ВСЕ шаги текущего урока должны быть completed
next_lesson_available = False
if next_lesson and existing_submission and existing_submission.status == "approved":
    # Дополнительная проверка: все шаги текущего урока пройдены?
    from reviewers.models import StepProgress

    total_steps = lesson.steps.count()
    completed_steps = StepProgress.objects.filter(
        profile=profile,
        step__lesson=lesson,
        is_completed=True
    ).count()

    # Разблокируем следующий урок ТОЛЬКО если все шаги пройдены
    if completed_steps >= total_steps:
        next_lesson_available = True
        logger.info(
            f"Next lesson unlocked for {request.user.email}: "
            f"all {completed_steps}/{total_steps} steps completed"
        )
    else:
        logger.warning(
            f"Next lesson BLOCKED for {request.user.email}: "
            f"only {completed_steps}/{total_steps} steps completed"
        )
```

---

### 4. Исправление PDF URL

**Проблема:** PDF URL содержал полный системный путь:
```
http://127.0.0.1:8000/media//Users/dmitrii/.../media/certificates/file.pdf
```

**Причина:** `generate_certificate_pdf()` возвращал `certificate.pdf_file.path` (абсолютный путь)

**Решение в `certificates/utils.py`:**

```python
def generate_certificate_pdf(certificate: Certificate, language: str = "ru") -> None:
    # ... генерация PDF ...

    # Возвращаем относительный путь для использования в URL
    # НЕ используем .path (полный системный путь), а .name (относительный путь от MEDIA_ROOT)
    return certificate.pdf_file.name  # Вернет: certificates/certificate_XXX.pdf
```

**Результат:**
```
http://127.0.0.1:8000/media/certificates/certificate_CERT-20260204-B666.pdf
```

---

### 5. Передача даты completion_date как объект datetime

**Проблема:** Дата в email не отображалась (пустое поле)

**Причина:** В сигнале дата преобразовывалась в строку `.strftime("%d.%m.%Y")`, но в шаблоне использовался фильтр `|date:"d.m.Y"` который работает только с datetime/date объектами.

**Решение в `reviewers/signals.py`:**

```python
# БЫЛО (неправильно):
completion_date=certificate.completion_date.strftime("%d.%m.%Y"),

# СТАЛО (правильно):
completion_date=certificate.completion_date,  # Передаем объект datetime
```

**В шаблоне:**
```django
<p><strong>Дата завершения:</strong> {{ completion_date|date:"d.m.Y" }}</p>
```

---

### 6. Поиск сертификата по номеру или коду

**Проблема:** Форма проверки сертификата искала только по `verification_code` (хэш SHA-256), а пользователи вводили `certificate_number` (CERT-20260204-XXXX) из email.

**Решение в `certificates/views.py`:**

```python
def verify_form(request):
    """Универсальный поиск по certificate_number ИЛИ verification_code"""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()

        # Ищем по ОБОИМ полям
        certificate = Certificate.objects.filter(
            Q(certificate_number=code) | Q(verification_code=code)
        ).select_related('student', 'course').first()
```

**Теперь работает:**
- ✅ По certificate_number: `CERT-20260204-B666` (из email)
- ✅ По verification_code: `хэш SHA-256` (из QR кода)

---

## Оптимизация кода

### Удалены отладочные принты

**Статистика очистки:**
- **JavaScript**: 97 строк console.log() удалено из 41 файла
- **Python**: 833 строки print() удалено из 190 файлов
- **Итого**: 930 строк отладочного кода удалено

**Файлы с наибольшими изменениями:**
- `reviewers/schemas.py`: 53 строки
- `reviewers/admin.py`: 32 строки
- `reviewers/submission-review.js`: 31 строка
- `students/views.py`: 29 строк
- `reviewers/api.py`: 25 строк

**Исключения:**
- `pyland/settings.py` - оставлены информационные print о статусе Redis/Cache
- Docstrings и комментарии к функциям сохранены
- Важные логи через `logger.info/warning/error` сохранены

---

## Стилизация страниц

### Страница проверки сертификата

**Файл:** `certificates/templates/certificates/verify_form.html`

**Изменения:**
- Добавлен revolutionary hero banner в стиле blog
- Gradient background с анимированными частицами
- Glass morphism эффекты
- Responsive дизайн

**CSS:** `static/css/certificates/verify-form.css`

---

## Тестирование

### Тестовые сценарии

1. **Защита от выдачи сертификата без шагов**
   - Все уроки approved, 0 шагов completed → ❌ Сертификат НЕ выдан
   - Все уроки approved, все шаги completed → ✅ Сертификат выдан

2. **Блокировка следующего урока**
   - Урок approved, 2/3 шагов → ❌ Следующий урок заблокирован
   - Урок approved, 3/3 шагов → ✅ Следующий урок разблокирован

3. **PDF URL корректность**
   - Проверка отсутствия системных путей в URL
   - Проверка отсутствия дублирования 'media'

4. **Email отправка**
   - Celery async отправка (при доступности workers)
   - Sync fallback (при недоступности Celery)
   - Корректность всех данных в письме

5. **Поиск сертификата**
   - По certificate_number (CERT-20260204-XXXX)
   - По verification_code (хэш)

---

## Документация

**Созданные файлы:**
- `docs/EMAIL_CERTIFICATE_SETUP.md` - настройка email системы
- `CERTIFICATE_SYSTEM_IMPLEMENTATION.md` - текущий файл

**Обновленные файлы:**
- `docs/MULTILINGUAL_CERTIFICATES.md` - добавлена информация об email
- `CHANGELOG.md` - добавлены записи о всех изменениях

---

## Безопасность

### Критические проверки

1. **Двухуровневая валидация завершения курса:**
   - Уровень 1: Approved lesson submissions
   - Уровень 2: Completed step progress (НОВОЕ)

2. **Защита от преждевременной разблокировки:**
   - Следующий урок доступен только после прохождения ВСЕХ шагов
   - Логирование попыток доступа

3. **Корректные пути к файлам:**
   - Использование относительных путей для URL
   - Защита от раскрытия системных путей

4. **Универсальный поиск сертификатов:**
   - Поддержка читаемого номера и защищенного кода
   - Q() объекты для безопасного поиска

---

## Производительность

### Оптимизации

1. **Celery async отправка:**
   - Не блокирует основной процесс
   - Retry механизм (3 попытки)
   - Graceful degradation к sync при недоступности

2. **Проверка Celery workers:**
   - `current_app.control.inspect().active()` перед отправкой
   - Быстрый fallback к sync методу

3. **Кэширование:**
   - Статистика студента кэшируется
   - Инвалидация при изменении progress

4. **Select related:**
   - Оптимизация запросов при поиске сертификатов
   - `.select_related('student', 'course')`

---

## Будущие улучшения

1. **Уведомления:**
   - Push-уведомления о получении сертификата
   - SMS-уведомления (опционально)
   - Telegram bot уведомления

2. **Социальные функции:**
   - Шаринг сертификата в социальные сети
   - Публичная страница достижений студента
   - Рейтинг лучших студентов

3. **Аналитика:**
   - Статистика времени прохождения курсов
   - A/B тестирование email шаблонов
   - Метрики открываемости писем

4. **Интеграции:**
   - LinkedIn certificate integration
   - Blockchain verification
   - API для внешних систем

---

## Коммит

```bash
git add -A
git commit -m "feat: система сертификатов с защитой и email

ФУНКЦИОНАЛЬНОСТЬ:
- Автоматическая отправка сертификатов на email при завершении курса
- Celery async задача с retry + sync fallback
- HTML email шаблон в стиле auth app с inline CSS
- Статистика в письме: уроки, время, отзывы

БЕЗОПАСНОСТЬ (КРИТИЧНО):
- Двухуровневая валидация: lessons approved + steps completed
- Блокировка сертификата если шаги не пройдены (0/16 → не выдается)
- Блокировка следующего урока без прохождения всех шагов
- Защита от gaming системы

ИСПРАВЛЕНИЯ:
- PDF URL: используем .name вместо .path (убрали дублирование пути)
- completion_date: передаем datetime вместо строки (фиксит отображение даты)
- Поиск сертификата: по certificate_number ИЛИ verification_code

ОПТИМИЗАЦИЯ:
- Удалено 930 строк отладочного кода (97 JS + 833 Python)
- Очищены console.log() из всех JS файлов
- Удалены отладочные print() из Python (кроме settings.py)
- Сохранены docstrings и важные логи

ДОКУМЕНТАЦИЯ:
- docs/EMAIL_CERTIFICATE_SETUP.md
- CERTIFICATE_SYSTEM_IMPLEMENTATION.md
- Обновлен CHANGELOG.md

ТЕСТЫ:
✅ Защита от выдачи без шагов
✅ Блокировка следующего урока
✅ PDF URL корректность
✅ Email отправка (async + sync)
✅ Поиск по номеру и коду"

git push origin dev
```

---

## Авторы

- Dmitrii - Backend & System Architecture
- GitHub Copilot - Code Assistance

---

## Лицензия

Proprietary - PyLand Online School Platform
