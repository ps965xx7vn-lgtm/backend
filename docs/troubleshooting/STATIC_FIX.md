# Решение проблемы со статикой и флагами

## Проблема
На некоторых ПК:
1. **Статика не прогружается** - CSS и JavaScript файлы не загружаются
2. **Флаги показываются как буквы** - вместо эмодзи флагов 🇷🇺 🇬🇧 🇬🇪 показываются только коды стран

## Причины

### 1. Проблема с WhiteNoise и кешированием
- `CompressedManifestStaticFilesStorage` создавал проблемы с кешированием
- Manifest файл мог быть поврежден или устаревший
- Браузеры кешировали старые версии файлов

### 2. Проблема с эмодзи флагов
- НЕ все браузеры и ОС поддерживают эмодзи флагов
- На Windows 10 (старые версии) флаги показываются как буквы
- На некоторых Linux системах нет шрифтов для эмодзи
- iOS Safari может не загружать эмодзи флаги из-за настроек безопасности

## Решения

### ✅ 1. Изменены настройки статики (settings.py)

**Было:**
```python
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

**Стало:**
```python
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",  # Убрали Manifest
    },
}
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_USE_FINDERS = DEBUG
WHITENOISE_MAX_AGE = 0 if DEBUG else 31536000  # Нет кеша в dev режиме

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
```

**Плюсы изменений:**
- ✅ Более простой бэкенд без manifest файла
- ✅ Нет кеширования в dev режиме (DEBUG=True)
- ✅ Использование Django finders в development
- ✅ Лучшая совместимость с разными ОС

### ✅ 2. Заменены эмодзи на CSS флаги

Создан файл `/src/static/css/core/flags.css` с CSS флагами:

**Преимущества CSS флагов:**
- ✅ Работают на ВСЕХ браузерах и ОС
- ✅ Нет зависимости от системных шрифтов
- ✅ Единообразный вид везде
- ✅ Fallback для старых браузеров (показывается текст "RU", "GB", "GE")

**Было в _header.html:**
```html
<span class="flag">
    {% if CURRENT_LANGUAGE == 'ru' %}🇷🇺
    {% elif CURRENT_LANGUAGE == 'ka' %}🇬🇪
    {% else %}🇬🇧{% endif %}
</span>
```

**Стало:**
```html
<span class="flag">
    <span class="flag-icon flag-icon-{{ CURRENT_LANGUAGE|default:'ru' }}">
        {% if CURRENT_LANGUAGE == 'en' %}<span></span>{% endif %}
    </span>
    <span class="flag-text-fallback">
        {% if CURRENT_LANGUAGE == 'ru' %}RU
        {% elif CURRENT_LANGUAGE == 'ka' %}GE
        {% else %}GB{% endif %}
    </span>
</span>
```

### ✅ 3. Добавлен flags.css в base.html

```html
<link rel="stylesheet" href="{% static 'css/core/flags.css' %}">
```

## Как применить изменения

### Для разработчика (локально):

```bash
# 1. Собрать статику с очисткой старых файлов
poetry run python src/manage.py collectstatic --noinput --clear

# 2. Перезапустить сервер
# Ctrl+C чтобы остановить текущий
poetry run python src/manage.py runserver

# 3. Очистить кеш браузера
# В Chrome: Cmd+Shift+Delete (Mac) или Ctrl+Shift+Delete (Windows)
# Или открыть DevTools → Network → поставить галочку "Disable cache"
```

### Для production (Kubernetes):

```bash
# 1. Применить изменения settings.py
git add src/pyland/settings.py
git commit -m "fix: улучшены настройки статики для совместимости"

# 2. Применить CSS флаги
git add src/static/css/core/flags.css src/core/templates/
git commit -m "fix: заменены эмодзи флагов на CSS флаги"

# 3. Пересобрать и задеплоить
docker build -t pyland-backend:latest .
kubectl rollout restart deployment/pyland-web
```

## Проверка работоспособности

### 1. Проверить загрузку статики:

```bash
# Открыть DevTools → Network tab
# Фильтр: CSS, JS
# Все файлы должны иметь статус 200 OK
```

### 2. Проверить флаги:

- Должны быть видны цветные флаги (Россия - бело-сине-красный, и т.д.)
- На старых системах - текст "RU", "GB", "GE"
- НЕ должно быть символов ◻️◻️ или кодов стран

### 3. Тестирование на разных устройствах:

- ✅ Chrome/Safari (Mac) - CSS флаги
- ✅ Firefox (Windows) - CSS флаги
- ✅ Safari (iOS) - CSS флаги
- ✅ Chrome (Android) - CSS флаги
- ✅ Старые браузеры - текст fallback "RU", "GB", "GE"

## FAQ

**Q: Почему на моем ПК работает, а на другом нет?**
A: Разные браузеры и ОС по-разному кешируют статику. Теперь с новыми настройками проблем быть не должно.

**Q: Можно ли вернуть эмодзи флаги?**
A: Не рекомендуется. CSS флаги работают везде и не зависят от системы.

**Q: Что делать если статика все равно не грузится?**
A:
1. Проверить DEBUG=True в локальном .env
2. Запустить `collectstatic --clear`
3. Перезапустить сервер
4. Очистить кеш браузера (жесткое обновление: Cmd+Shift+R)

**Q: Нужно ли обновлять существующие страницы?**
A: Нет, изменения в base.html и _header.html применятся ко всем страницам автоматически.

## Дополнительная оптимизация

Если проблемы сохраняются в production:

1. **Добавить версии к CSS файлам:**
```html
<link rel="stylesheet" href="{% static 'css/core/flags.css' %}?v={{ BUILD_VERSION }}">
```

2. **Настроить Nginx кеширование:**
```nginx
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

3. **Использовать CDN для статики** (опционально)

## Версия исправлений

- **Дата:** 5 марта 2026
- **Версия:** 2.1.0
- **Автор:** GitHub Copilot
- **Файлы изменены:**
  - `src/pyland/settings.py`
  - `src/static/css/core/flags.css` (новый)
  - `src/core/templates/base.html`
  - `src/core/templates/shared/_header.html`
