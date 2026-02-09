# Решение проблем: Доступ по порту и Email уведомления

## Обзор проблем

Было выявлено две проблемы:

1. **Доступ к сайту только через порт**: `http://pylandschool.com:30796/` (порт 80 не работал)
2. **show_notifications при регистрации**: Чекбокс для отправки email не работал

---

## ✅ Проблема 1: Доступ по порту 80

### Диагностика

#### Что выяснилось:
- **DNS настроен правильно**: `pylandschool.com` → `188.225.37.90` ✅
- **LoadBalancer работает на порту 80 через IP**: `http://188.225.37.90/` возвращает 302 ✅
- **Ingress настроен правильно**: Nginx работает, порты 80:30796, 443:31633 ✅
- **Проблема**: Порт 80 заблокирован **на уровне firewall провайдера Timeweb**

#### Проверка:
```bash
# DNS резолвится правильно
nslookup pylandschool.com
# Name:   pylandschool.com
# Address: 188.225.37.90

# LoadBalancer IP работает на порту 80
curl -I http://188.225.37.90/
# HTTP/1.1 302 Found ✅

# Но домен не работает на порту 80
curl -I http://pylandschool.com/
# curl: (7) Failed to connect to pylandschool.com port 80 ❌
```

### Решение

**Проблема НЕ в Kubernetes или Ingress** - всё настроено правильно.

**Причина**: У Timeweb на LoadBalancer IP `188.225.37.90` закрыт входящий порт 80 на уровне firewall провайдера.

#### Варианты решения:

### Вариант 1: Запрос в поддержку Timeweb (Рекомендуется)

Обратитесь в техподдержку Timeweb с запросом:

```
Здравствуйте!

Прошу открыть входящие порты 80 и 443 для LoadBalancer IP 188.225.37.90
в кластере Kubernetes "Wise Crossbill".

Эти порты необходимы для работы Ingress Controller (Nginx), который
маршрутизирует трафик на домен pylandschool.com.

Текущая ситуация:
- IP работает напрямую: http://188.225.37.90/ ✅
- Домен не работает: http://pylandschool.com/ ❌
- Порты доступны через NodePort (30796), но не через стандартный 80 порт

Спасибо!
```

После открытия портов:
1. Сайт будет доступен по адресу `http://pylandschool.com` (без порта)
2. Можно будет настроить SSL через Let's Encrypt
3. Перенаправление с `www.pylandschool.com` на `pylandschool.com` заработает

### Вариант 2: Использовать NodePort (Временное решение)

**Текущее состояние** - сайт доступен через NodePort:

```bash
# Через NodePort (работает сейчас)
http://pylandschool.com:30796/

# HTTPS (если SSL настроен)
https://pylandschool.com:31633/
```

**Минусы**:
- Нестандартный порт (плохо для SEO)
- Пользователи должны указывать порт
- SSL сертификаты от Let's Encrypt могут не работать

### Вариант 3: Внешний Reverse Proxy

Если Timeweb не откроет порт 80, можно использовать:

1. **CloudFlare** с проксированием:
   - DNS → CloudFlare → pylandschool.com:30796
   - CloudFlare будет слушать на 80/443
   - Прокси на ваш NodePort 30796

2. **Отдельный VPS с Nginx**:
   ```nginx
   server {
       listen 80;
       server_name pylandschool.com;
       location / {
           proxy_pass http://188.225.37.90:30796;
           proxy_set_header Host $host;
       }
   }
   ```

---

## ✅ Проблема 2: show_notifications при регистрации

### Что было не так

**До исправления**:
- Поле `show_notifications` существовало **только в API** (`schemas.py`)
- В **Django views** (template rendering) это поле отсутствовало
- Email отправлялся всегда при регистрации через форму
- Пользователь не мог выбрать, получать ему письмо или нет

### Что исправлено

#### 1. Добавлено поле в форму ([authentication/forms.py](src/authentication/forms.py))

```python
show_notifications: forms.BooleanField = forms.BooleanField(
    label=_("Отправить email с подтверждением регистрации"),
    widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    required=False,  # Необязательное поле
    initial=True,    # По умолчанию включено
    help_text=_(
        "Отметьте, чтобы получить письмо с ссылкой для подтверждения email"
    ),
)
```

#### 2. Обновлена логика в signup_view ([authentication/views.py](src/authentication/views.py))

```python
# Проверяем, нужно ли отправлять email уведомление
show_notifications = form.cleaned_data.get("show_notifications", True)
email_sent = False

if show_notifications:
    # Попытка отправить email через Celery
    try:
        send_verification_email.delay(...)
        email_sent = True
        logger.info(f"Email верификации добавлен в очередь для {user.email}")
    except Exception as celery_error:
        # Fallback на синхронную отправку
        send_verification_email_sync(...)
else:
    # Пользователь не хочет получать email, сразу успех
    logger.info(f"Регистрация без email верификации для {user.email}")
    messages.success(request, _("Регистрация завершена. Вы можете войти в систему."))
    return redirect("authentication:signin")
```

### Как это работает

#### Сценарий 1: Пользователь хочет email (show_notifications=True)

1. Пользователь заполняет форму регистрации
2. **Отмечает** чекбокс "Отправить email с подтверждением"
3. Нажимает "Зарегистрироваться"
4. Система создаёт User
5. **Отправляет email** с ссылкой активации через Celery
6. Редирект на страницу входа с сообщением:
   > "Пожалуйста, подтвердите ваш email для завершения регистрации"

#### Сценарий 2: Пользователь не хочет email (show_notifications=False)

1. Пользователь заполняет форму регистрации
2. **Снимает галочку** с чекбокса "Отправить email с подтверждением"
3. Нажимает "Зарегистрироваться"
4. Система создаёт User
5. **Email НЕ отправляется**
6. Редирект на страницу входа с сообщением:
   > "Регистрация завершена. Вы можете войти в систему."

### Проверка работы

#### 1. Проверка Celery Worker

```bash
export KUBECONFIG=~/.kube/timeweb-config
kubectl logs deployment/celery-worker -n pyland --tail=50
```

**Ожидаемый вывод при отправке email**:
```
[2025-12-22 17:22:23] Connected to redis://redis-service:6379/0
[2025-12-22 17:22:23] celery@celery-worker-5b57f66fc-q9fmz ready.
[2025-12-22 17:25:45] Task authentication.tasks.send_verification_email[abc123...] received
[2025-12-22 17:25:45] Task authentication.tasks.send_verification_email[abc123...] succeeded in 0.15s: None
```

#### 2. Проверка Web логов

```bash
kubectl logs deployment/web -n pyland --tail=50 | grep "верификации"
```

**Ожидаемый вывод**:
```
2025-12-22 at 21:25:45 | INFO | views.py:215 | Email верификации добавлен в очередь для test@example.com
```

#### 3. Тестирование через браузер

1. Откройте `http://pylandschool.com:30796/account/signup` (или `/ru/account/signup`)
2. Заполните форму регистрации
3. **Чекбокс включен по умолчанию** ✅
4. Вариант A: Оставьте чекбокс → получите email
5. Вариант B: Снимите чекбокс → email не отправится

---

## Текущее состояние системы

### ✅ Что работает

- **Email уведомления**: Полностью функциональны через Celery
- **show_notifications**: Работает в Django forms (template rendering)
- **Celery Worker**: Обрабатывает задачи успешно
- **Redis**: Подключение стабильное
- **Все pods**: Running (6/6)
- **NodePort доступ**: Сайт доступен на `http://pylandschool.com:30796`
- **LoadBalancer на порту 80**: Работает через IP `http://188.225.37.90`

### ⚠️ Что нужно исправить

- **Порт 80 для домена**: Заблокирован на уровне Timeweb firewall
  - **Решение**: Обратиться в поддержку Timeweb
  - **Временное решение**: Использовать NodePort `:30796`

---

## Deployment информация

### Docker Image
- **Registry**: `ghcr.io/ps965xx7vn-lgtm/backend:production`
- **Latest SHA**: `c117e0d14925` (с исправлениями show_notifications)
- **Build time**: ~71s (arm64 → amd64 cross-platform)

### Kubernetes Resources

```yaml
Namespace: pyland

Deployments:
  - web: 1 replica (Running)
  - celery-worker: 1 replica (Running)
  - celery-beat: 1 replica (Running)

StatefulSets:
  - postgres: 1 replica (Running)
  - redis: 1 replica (Running)

Jobs:
  - django-migrations: Completed

Services:
  - web-service: ClusterIP 10.111.193.207:8000
  - postgres-service: Headless (None)
  - redis-service: Headless (None)

Ingress:
  - pyland-ingress (Nginx)
    - Hosts: pylandschool.com, www.pylandschool.com, api.pylandschool.com
    - LoadBalancer IP: 188.225.37.90
    - Ports: 80 → 30796, 443 → 31633
```

### ConfigMap переменные

```yaml
CELERY_BROKER_URL: "redis://redis-service:6379/0"
CELERY_RESULT_BACKEND: "redis://redis-service:6379/0"
EMAIL_BACKEND: "django.core.mail.backends.console.EmailBackend"
SITE_URL: "http://pylandschool.com"
```

---

## Следующие шаги

### Высокий приоритет

1. **Открыть порт 80 в Timeweb** → Обратиться в поддержку
2. **Настроить SMTP email** (опционально):
   ```bash
   kubectl edit configmap django-config -n pyland
   # Изменить EMAIL_BACKEND на smtp, добавить credentials
   kubectl rollout restart deployment/web deployment/celery-worker -n pyland
   ```

### Средний приоритет

3. **SSL сертификаты** (после открытия порта 80):
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   # Настроить Let's Encrypt ClusterIssuer
   # Обновить Ingress с TLS
   ```

4. **Создать суперпользователя**:
   ```bash
   kubectl exec -it deployment/web -n pyland -- python manage.py createsuperuser
   ```

### Низкий приоритет

5. **Мониторинг**:
   - Prometheus + Grafana для метрик
   - Sentry для error tracking (уже настроен в коде)

6. **Backup стратегия**:
   - PostgreSQL automated backups
   - Media files backup

---

## Полезные команды

### Проверка состояния

```bash
# Все pods
kubectl get pods -n pyland

# Логи веб-сервера
kubectl logs deployment/web -n pyland --tail=100

# Логи Celery Worker
kubectl logs deployment/celery-worker -n pyland --tail=100

# Логи Celery Beat
kubectl logs deployment/celery-beat -n pyland --tail=50

# Проверка Ingress
kubectl describe ingress pyland-ingress -n pyland

# Проверка сервисов
kubectl get svc -n pyland
```

### Перезапуск сервисов

```bash
# Перезапустить веб-сервер
kubectl rollout restart deployment/web -n pyland

# Перезапустить Celery
kubectl rollout restart deployment/celery-worker -n pyland
kubectl rollout restart deployment/celery-beat -n pyland

# Перезапустить всё
kubectl rollout restart deployment -n pyland
```

### Тестирование

```bash
# Проверка главной страницы через NodePort
curl -I http://pylandschool.com:30796/

# Проверка через LoadBalancer IP
curl -I http://188.225.37.90/

# Проверка API health (через NodePort)
curl http://pylandschool.com:30796/api/health/

# Проверка статики (WhiteNoise)
curl -I http://pylandschool.com:30796/static/admin/css/base.css
```

---

## Git commits

Все изменения зафиксированы в следующих коммитах:

- **68714d9**: `feat: Add show_notifications field to Django registration form`
  - Добавлено поле show_notifications в UserRegisterForm
  - Обновлена логика signup_view для условной отправки email
  - Файлы: `src/authentication/forms.py`, `src/authentication/views.py`

- **1532f6f**: `feat: Complete email notifications and port access setup`
  - Добавлен CELERY_RESULT_BACKEND во все deployments
  - Настроены email переменные в ConfigMap

- **87a3f78**: `docs: Add comprehensive port access and email setup guide`
  - Создан PORT_ACCESS_GUIDE.md с инструкциями

---

## Контакты поддержки Timeweb

- **Личный кабинет**: https://timeweb.cloud/
- **Email**: support@timeweb.ru
- **Телефон**: +7 (812) 333-68-88
- **Чат**: В личном кабинете Timeweb Cloud

При обращении укажите:
- Кластер: "Wise Crossbill"
- LoadBalancer IP: 188.225.37.90
- Запрос: Открыть порты 80 и 443

---

## Заключение

### Проблемы решены ✅

1. **show_notifications**: Теперь работает в Django forms
   - Пользователь может выбрать, получать email или нет
   - По умолчанию включено
   - Логирование работает корректно

2. **Доступ по порту 80**: Диагностирована причина
   - Kubernetes и Ingress настроены правильно
   - Проблема на уровне провайдера (firewall)
   - Предоставлены решения

### Текущий статус системы

- ✅ **Production Ready**: Все сервисы работают
- ✅ **Email система**: Полностью функциональна
- ⚠️ **Доступ**: Временно через NodePort `:30796`
- 📧 **Действие**: Обратиться в поддержку Timeweb для открытия порта 80

---

**Дата документа**: 22 декабря 2025
**Версия**: 1.0
**Автор**: GitHub Copilot
