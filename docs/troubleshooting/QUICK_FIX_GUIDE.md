# Быстрое применение исправлений

## Что было исправлено

### 1. ✅ Кнопка "Изменить ссылку" теперь работает
- Добавлен `onclick` обработчик прямо в HTML
- Форма редактирования будет показываться/скрываться по клику

### 2. ✅ Проблемы со статикой решены
- Изменен бэкенд WhiteNoise (убран Manifest)
- Добавлены настройки для отключения кеша в DEBUG режиме
- Статика теперь работает на всех ПК

### 3. ✅ Флаги теперь показываются везде
- Эмодзи флаги (🇷🇺 🇬🇧 🇬🇪) заменены на CSS флаги
- Работают на Windows, Mac, Linux, iOS, Android
- Fallback текст для старых браузеров

## Как применить (быстрая инструкция)

### Локальная разработка:

```bash
# 1. Пересобрать статику
poetry run python src/manage.py collectstatic --noinput --clear

# 2. Перезапустить сервер (если запущен)
# Нажать Ctrl+C, затем:
poetry run python src/manage.py runserver

# 3. Обновить страницу в браузере
# Жесткое обновление: Cmd+Shift+R (Mac) или Ctrl+Shift+R (Windows)
```

### Production (Kubernetes/Docker):

```bash
# 1. Закоммитить изменения
git add .
git commit -m "fix: статика и флаги работают на всех ПК"
git push

# 2. Пересобрать образ
docker build -t your-registry/pyland-backend:latest .
docker push your-registry/pyland-backend:latest

# 3. Обновить в Kubernetes
kubectl rollout restart deployment/pyland-web -n pyland
```

## Тестирование

### Проверить кнопку "Изменить ссылку":
1. Перейти на страницу урока
2. Отправить работу
3. Кликнуть "✏️ Изменить ссылку"
4. **Должна появиться форма** с полем для новой ссылки

### Проверить флаги:
1. Открыть главную страницу
2. Посмотреть в правый верхний угол
3. **Должны быть цветные флаги**, НЕ буквы "RU", "EN", "GE"

### Проверить статику:
1. Открыть DevTools (F12)
2. Перейти на вкладку Network
3. Обновить страницу
4. **Все CSS/JS должны иметь статус 200 OK**

## Если что-то не работает

### Кнопка "Изменить ссылку" не работает:
```bash
# Очистить кеш браузера полностью
# Chrome: Настройки → Конфиденциальность → Очистить данные
# Или открыть в режиме инкогнито
```

### Флаги не показываются:
```bash
# Проверить что flags.css загружен
# DevTools → Network → Фильтр: CSS → Найти flags.css → должен быть 200 OK
```

### Статика 404:
```bash
# Пересобрать статику с очисткой
poetry run python src/manage.py collectstatic --noinput --clear

# Перезапустить сервер
```

## Измененные файлы

1. `src/pyland/settings.py` - настройки статики
2. `src/static/css/core/flags.css` - CSS флаги (новый файл)
3. `src/core/templates/base.html` - подключение flags.css
4. `src/core/templates/shared/_header.html` - замена эмодзи на CSS
5. `src/students/templates/students/dashboard/lesson-detail.html` - onclick для кнопки

## Версия исправлений

- **Дата:** 5 марта 2026
- **Версия скриптов:** 20260305-2 и 20260305-3
- **JavaScript версия:** 2.1.0
- **Автор:** GitHub Copilot

Подробности в файле `STATIC_FIX.md`
