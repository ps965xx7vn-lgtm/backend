# Support Application

Приложение технической поддержки платформы Pyland School.

## Описание

Support отвечает за систему обработки обращений пользователей через тикеты.

## Модели

### Ticket
Основная модель тикета поддержки:
- **user** - пользователь, создавший тикет
- **subject** - тема обращения
- **message** - текст сообщения
- **status** - статус обработки
- **priority** - приоритет
- **assigned_to** - назначенный сотрудник support
- **created_at** - дата создания
- **updated_at** - дата обновления
- **closed_at** - дата закрытия

### Статусы
- **open** - Открыт, ожидает обработки
- **in_progress** - В работе
- **closed** - Закрыт, решен

### Приоритеты
- **low** - Низкий (общие вопросы)
- **medium** - Средний (по умолчанию)
- **high** - Высокий (технические проблемы)

### Планируемые модели

#### TicketMessage
Сообщения в тикете (переписка):
- **ticket** - тикет
- **author** - автор сообщения (user или support)
- **message** - текст сообщения
- **is_internal** - внутренняя заметка (не видна пользователю)
- **created_at** - дата создания

#### TicketAttachment
Прикрепленные файлы:
- **ticket** - тикет
- **file** - файл (скриншоты, логи)
- **uploaded_by** - кто загрузил
- **uploaded_at** - дата загрузки

#### TicketCategory
Категории тикетов:
- **name** - название категории
- **description** - описание
- **icon** - иконка
- **auto_assign_to** - автоназначение на роль/пользователя

## API Endpoints (планируется)

### Для пользователей
```
GET    /api/support/tickets/              - Мои тикеты
POST   /api/support/tickets/              - Создать тикет
GET    /api/support/tickets/{id}          - Детали тикета
POST   /api/support/tickets/{id}/messages - Добавить сообщение
POST   /api/support/tickets/{id}/close    - Закрыть тикет
```

### Для support команды
```
GET    /api/support/tickets/all           - Все тикеты
PATCH  /api/support/tickets/{id}/assign   - Назначить на себя
PATCH  /api/support/tickets/{id}/status   - Изменить статус
PATCH  /api/support/tickets/{id}/priority - Изменить приоритет
POST   /api/support/tickets/{id}/internal - Внутренняя заметка
```

### Статистика
```
GET    /api/support/stats                 - Статистика поддержки
```

## Views (планируется)

### Для пользователей
- `ticket_create` - создание тикета
- `ticket_list` - список своих тикетов
- `ticket_detail` - детали тикета с историей

### Для support
- `support_dashboard` - dashboard с активными тикетами
- `ticket_manage` - управление тикетом
- `support_stats` - статистика команды

## Workflow

### 1. Создание тикета
```
Пользователь → Форма → Ticket.create(status='open')
              → Email уведомление support команде
```

### 2. Назначение
```
Auto: Ticket → TicketCategory → auto_assign_to
Manual: Support admin → Assign to team member
```

### 3. Обработка
```
Support → Read ticket → Respond → Update status
       → Add internal notes → Escalate if needed
```

### 4. Закрытие
```
Support → Resolve issue → Status = 'closed'
       → Email пользователю → Request feedback
```

## Приоритеты обработки

### Low (24-48 часов)
- Общие вопросы
- Предложения по улучшению
- Некритичные баги

### Medium (8-12 часов)
- Вопросы по функционалу
- Технические проблемы
- Ошибки в контенте

### High (1-4 часа)
- Критичные баги
- Недоступность сервиса
- Проблемы с оплатой
- Потеря данных

## Автоматизация

### Auto-reply
При создании тикета:
```python
send_auto_reply(ticket):
    """
    Спасибо за обращение!
    Ваш тикет #{ticket.id} принят.
    Приоритет: {ticket.priority}
    Мы ответим в течение {sla_time}
    """
```

### Auto-assign
По категориям или ключевым словам:
```python
if 'payment' in ticket.subject.lower():
    ticket.assigned_to = get_payment_specialist()
elif 'bug' in ticket.subject.lower():
    ticket.assigned_to = get_tech_support()
```

### SLA мониторинг
```python
def check_sla_violations():
    """Проверка нарушений SLA"""
    overdue_tickets = Ticket.objects.filter(
        status='open',
        created_at__lt=timezone.now() - sla_time
    )
    notify_managers(overdue_tickets)
```

## Уведомления

### Для пользователя
- Тикет создан
- Получен ответ
- Статус изменен
- Тикет закрыт

### Для support
- Новый тикет
- Новое сообщение
- Эскалация
- SLA violation

## Admin панель

Функционал:
- Список всех тикетов
- Фильтры: статус, приоритет, категория, назначенный
- Поиск по тексту, автору, ID
- Массовые действия: назначить, закрыть, изменить приоритет
- Статистика: среднее время ответа, закрытия
- Экспорт в CSV

## Интеграция

### Email
Входящие письма → создание тикетов:
```python
# Парсинг email
ticket = Ticket.objects.create(
    user=find_or_create_user(from_email),
    subject=email.subject,
    message=email.body
)
```

### Slack/Discord
Уведомления команде:
```python
notify_slack(f"Новый тикет #{ticket.id}: {ticket.subject}")
```

### Знания base (FAQ)
Автоматические предложения:
```python
similar_faq = find_similar_articles(ticket.subject)
suggest_to_user(similar_faq)
```

## Метрики

### KPI
- First Response Time (FRT)
- Average Resolution Time (ART)
- Customer Satisfaction Score (CSAT)
- Ticket Volume
- Reopened Tickets %

### Dashboard
```
Активные тикеты: 12
Сегодня создано: 8
Сегодня закрыто: 5
Средний FRT: 2.5 часа
Средний ART: 8 часов
```

## Шаблоны ответов

### Быстрые ответы
```python
TEMPLATES = {
    'password_reset': "Инструкция по сбросу пароля...",
    'course_access': "Как получить доступ к курсу...",
    'certificate_issue': "Проблемы с сертификатом...",
}
```

### Макросы
- Приветствие
- Запрос дополнительной информации
- Эскалация
- Закрытие с решением
- Закрытие без решения

## Связанные приложения

- **authentication** - данные пользователя
- **notifications** - уведомления по тикетам
- **courses** - вопросы по курсам
- **payments** - проблемы с оплатой

## Тестирование

```bash
pytest support/tests/ -v
```

## Авторы

Pyland Team, 2025
