# Core Templates

HTML шаблоны для основных страниц приложения core.

## 📋 Структура

```
templates/
├── base.html                # Базовый шаблон для всего проекта
├── shared/                  # Общие компоненты (header, footer, etc.)
└── core/                    # Шаблоны core приложения
    ├── home.html           # Главная страница
    ├── contacts.html       # Страница контактов
    ├── about.html          # Страница "О нас"
    └── legal/              # Юридические страницы
        ├── terms_of_service.html
        └── privacy_policy.html
```

## 🏠 base.html

Базовый шаблон, от которого наследуются все страницы проекта.

**Основные блоки:**

```django
{% block title %}{% endblock %}           # Заголовок страницы
{% block extra_meta %}{% endblock %}      # Дополнительные meta-теги
{% block extra_css %}{% endblock %}       # Дополнительные CSS
{% block content %}{% endblock %}         # Основной контент
{% block extra_js %}{% endblock %}        # Дополнительные JS скрипты
```

**Подключаемые стили:**
- `static/css/core/main.css` - базовые стили
- `static/css/core/themes.css` - темная/светлая тема
- `static/css/core/layout.css` - layout grid system
- `static/css/core/components.css` - UI компоненты

**Подключаемые скрипты:**
- `static/js/core/main.js` - базовая функциональность
- `static/js/core/desktop-nav.js` - десктоп навигация
- `static/js/core/mobile-menu.js` - мобильное меню

**Context variables:**
- `footer_data` - из `core.context_processors.footer_data`

---

## 📄 core/home.html

Главная страница платформы Pyland.

**Extends:** `base.html`

**Context variables:**
```python
{
    'popular_courses': QuerySet[Course],  # Популярные курсы (limit 6)
    'stats': {
        'total_students': int,
        'total_courses': int,
        'total_lessons': int,
        'completion_rate': float
    }
}
```

**Используемые блоки:**
- `title` - "Pyland - Онлайн обучение программированию"
- `extra_meta` - Open Graph теги для соцсетей
- `extra_css` - `static/css/core/home.css`
- `content` - основной контент страницы

**Секции:**
1. **Hero Section** - главный баннер с призывом к действию
2. **Popular Courses** - карточки популярных курсов
3. **Statistics** - блок со статистикой платформы
4. **Features** - преимущества платформы
5. **CTA Section** - призыв к регистрации

**Компоненты:**
- `.hero-section` - главный баннер
- `.course-card` - карточка курса
- `.stats-grid` - сетка статистики
- `.features-list` - список возможностей
- `.cta-banner` - призыв к действию

---

## 📧 core/contacts.html

Страница контактов с формой обратной связи.

**Extends:** `base.html`

**Context variables:**
```python
{
    'form': FeedbackForm,           # Форма обратной связи
    'contact_info': {
        'email': str,
        'phone': str,
        'address': str,
        'working_hours': str
    }
}
```

**Используемые блоки:**
- `title` - "Контакты - Pyland"
- `extra_css` - `static/css/core/contact-form.css`
- `content` - форма и контактная информация

**Форма обратной связи:**

```django
<form method="post" class="feedback-form">
    {% csrf_token %}
    {{ form.first_name }}      <!-- Имя -->
    {{ form.phone_number }}    <!-- Телефон -->
    {{ form.email }}           <!-- Email -->
    {{ form.message }}         <!-- Сообщение -->
    {{ form.agree_terms }}     <!-- Согласие с условиями -->
    <button type="submit">Отправить</button>
</form>
```

**Валидация:**
- Client-side: HTML5 валидация + JavaScript
- Server-side: Django forms + Pydantic схемы

**AJAX отправка:**
Форма также может отправляться через API `/api/core/feedback/`

---

## ℹ️ core/about.html

Страница "О нас" с информацией о платформе.

**Extends:** `base.html`

**Context variables:**
```python
{
    'team_members': QuerySet[User],     # Команда (опционально)
    'achievements': List[dict],         # Достижения
}
```

**Используемые блоки:**
- `title` - "О нас - Pyland"
- `content` - информация о платформе

**Секции:**
1. **About Section** - описание платформы
2. **Mission** - миссия и ценности
3. **Team** - команда (если есть)
4. **Achievements** - достижения и награды

---

## ⚖️ core/legal/terms_of_service.html

Условия использования платформы (юридическая страница).

**Extends:** `base.html`

**Context variables:** Нет

**Используемые блоки:**
- `title` - "Условия использования - Pyland"
- `extra_css` - `static/css/core/legal-pages.css`
- `content` - текст условий использования

**Структура:**
1. Общие положения
2. Регистрация и учетная запись
3. Права и обязанности сторон
4. Оплата и возврат средств
5. Интеллектуальная собственность
6. Ограничение ответственности
7. Изменение условий
8. Контактная информация

**CSS стили:**
- `.legal-container` - контейнер с типографикой
- `.legal-section` - отдельная секция
- `.legal-toc` - оглавление (Table of Contents)

---

## 🔒 core/legal/privacy_policy.html

Политика конфиденциальности (юридическая страница).

**Extends:** `base.html`

**Context variables:** Нет

**Используемые блоки:**
- `title` - "Политика конфиденциальности - Pyland"
- `extra_css` - `static/css/core/legal-pages.css`
- `content` - текст политики

**Структура:**
1. Общие положения
2. Какие данные мы собираем
3. Как мы используем данные
4. Cookies и технологии отслеживания
5. Передача данных третьим лицам
6. Безопасность данных
7. Ваши права
8. Изменение политики
9. Контактная информация

**GDPR compliance:**
- Информация о сборе данных
- Права пользователей (доступ, удаление, исправление)
- Контактные данные DPO (Data Protection Officer)

---

## 🔧 Использование в views

### Рендеринг шаблона:

```python
from django.shortcuts import render

def home(request):
    context = {
        'popular_courses': Course.objects.annotate(
            student_count=Count('enrollments')
        ).order_by('-student_count')[:6],
        'stats': {
            'total_students': Student.objects.filter(roles__name='student').count(),
            'total_courses': Course.objects.count(),
            'total_lessons': Lesson.objects.count(),
            'completion_rate': 78.5
        }
    }
    return render(request, 'core/home.html', context)
```

### Передача формы:

```python
from .forms import FeedbackForm

def contacts(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Обработка формы
            pass
    else:
        form = FeedbackForm()
    
    return render(request, 'core/contacts.html', {'form': form})
```

---

## 🎨 CSS классы

### Общие классы (используются во всех шаблонах):

```css
.container              /* Основной контейнер (max-width: 1200px) */
.section                /* Секция контента */
.btn                    /* Кнопка */
.btn-primary           /* Главная кнопка */
.btn-secondary         /* Вторичная кнопка */
.card                   /* Карточка */
.form-control          /* Поле формы */
.alert                  /* Уведомление */
.grid                   /* Grid layout */
```

### Специфичные классы home.html:

```css
.hero-section          /* Главный баннер */
.course-card           /* Карточка курса */
.stats-grid            /* Сетка статистики */
.stat-item             /* Элемент статистики */
.features-list         /* Список возможностей */
.cta-banner            /* Призыв к действию */
```

### Специфичные классы contacts.html:

```css
.feedback-form         /* Форма обратной связи */
.contact-info          /* Блок контактной информации */
.contact-item          /* Элемент контакта */
.form-group            /* Группа полей формы */
.error-message         /* Сообщение об ошибке */
```

### Специфичные классы legal pages:

```css
.legal-container       /* Контейнер юридической страницы */
.legal-section         /* Секция документа */
.legal-toc             /* Оглавление */
.legal-highlight       /* Выделенный текст */
```

---

## 🔍 SEO и мета-теги

### Open Graph теги (home.html):

```django
{% block extra_meta %}
<meta property="og:title" content="Pyland - Онлайн школа программирования">
<meta property="og:description" content="Изучайте программирование онлайн">
<meta property="og:image" content="{% static 'images/og-image.jpg' %}">
<meta property="og:url" content="{{ request.build_absolute_uri }}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
{% endblock %}
```

### Canonical URLs:

```django
<link rel="canonical" href="{{ request.build_absolute_uri }}">
```

---

## 📱 Адаптивность

Все шаблоны адаптивны и работают на устройствах:
- 📱 Mobile (320px - 767px)
- 📱 Tablet (768px - 1023px)
- 💻 Desktop (1024px+)

**Breakpoints:**
```css
/* Mobile First подход */
@media (min-width: 768px) { /* Tablet */ }
@media (min-width: 1024px) { /* Desktop */ }
@media (min-width: 1440px) { /* Large Desktop */ }
```

---

## 🌐 Интернационализация

Для подготовки к переводам используйте:

```django
{% load i18n %}

<h1>{% trans "Welcome to Pyland" %}</h1>
<p>{% blocktrans %}Learn programming online{% endblocktrans %}</p>
```

---

## ♿ Доступность (A11y)

Все шаблоны следуют WCAG 2.1 Level AA:

- ✅ Semantic HTML (`<header>`, `<main>`, `<nav>`, `<footer>`)
- ✅ ARIA labels для интерактивных элементов
- ✅ Keyboard navigation
- ✅ Правильная структура заголовков (h1 → h2 → h3)
- ✅ Alt текст для изображений
- ✅ Контраст цветов (минимум 4.5:1)
- ✅ Focus indicators

**Пример:**

```django
<button 
    aria-label="Отправить форму обратной связи"
    aria-describedby="form-help-text">
    Отправить
</button>
<span id="form-help-text" class="sr-only">
    Форма будет отправлена на обработку
</span>
```

---

## 🧪 Тестирование шаблонов

```python
from django.test import TestCase

class TemplateTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
    
    def test_contacts_form_displays(self):
        response = self.client.get('/contacts/')
        self.assertContains(response, '<form')
        self.assertContains(response, 'feedback-form')
```

---

## 📚 Связанная документация

- [CSS Architecture](../../static/css/core/README.md) - Архитектура стилей
- [JavaScript Documentation](../../static/js/core/README.md) - JS скрипты
- [Template Tags](../templatetags/README.md) - Custom template tags
- [Forms](../forms.py) - Django формы
- [Views](../views.py) - Представления
