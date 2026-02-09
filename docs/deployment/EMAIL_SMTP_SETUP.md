# Настройка SMTP для отправки email (Gmail)

## Проблема
Email не отправляется адресатам. Ошибка: `530 Authentication Required`

**Причина:** Отсутствуют учетные данные для SMTP сервера Gmail.

---

## Решение: Настройка Gmail SMTP

### Шаг 1: Создать App Password в Gmail

**ВАЖНО:** Нельзя использовать обычный пароль Gmail. Нужен **App Password**.

1. **Включить 2FA** (если еще не включена):
   - Откройте https://myaccount.google.com/security
   - Найдите "2-Step Verification"
   - Включите двухфакторную аутентификацию

2. **Создать App Password**:
   - Откройте https://myaccount.google.com/apppasswords
   - Выберите приложение: "Mail"
   - Выберите устройство: "Other" (введите "Pyland Production")
   - Нажмите "Generate"
   - **Скопируйте 16-значный пароль** (без пробелов)

### Шаг 2: Добавить credentials в Kubernetes Secret

Откройте файл `k8s/timeweb-deploy.yaml` и найдите секцию Secret:

```yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: django-secret
  namespace: pyland
type: Opaque
stringData:
  SECRET_KEY: "django-prod-$ecure-k3y-7x9z!a2c#d4f%g6h*j8k(m0n)p1q=r3t+u5w-v7y"
  POSTGRES_USER: "pyland_prod_user"
  POSTGRES_PASSWORD: "VXR8K9mN2pL5vT3wQ7jH6fY4nB1xC0eD8sA5kU9rM3g="
  # ВАЖНО: Добавьте ваши Gmail credentials
  EMAIL_HOST_USER: "your-email@gmail.com"           # ← Замените
  EMAIL_HOST_PASSWORD: "your-app-password-here"     # ← Замените на App Password
```

**Замените:**
- `your-email@gmail.com` → Ваш Gmail адрес (например: `pylandschool@gmail.com`)
- `your-app-password-here` → 16-значный App Password из Шага 1

### Шаг 3: Применить изменения

```bash
export KUBECONFIG=~/.kube/timeweb-config

# Применить обновленный Secret
kubectl apply -f k8s/timeweb-deploy.yaml

# Перезапустить web и celery-worker для применения новых credentials
kubectl rollout restart deployment/web deployment/celery-worker -n pyland

# Проверить статус
kubectl get pods -n pyland

# Дождаться пока все поды Running (около 1 минуты)
kubectl wait --for=condition=ready pod -l app=web -n pyland --timeout=120s
```

### Шаг 4: Проверить отправку email

1. **Откройте сайт:** https://pylandschool.com/ru/authentication/signup/

2. **Зарегистрируйте тестовый аккаунт:**
   - Заполните форму регистрации
   - Оставьте галочку "Отправить email с подтверждением регистрации"
   - Нажмите "Создать аккаунт"

3. **Проверьте Celery логи:**
   ```bash
   export KUBECONFIG=~/.kube/timeweb-config
   kubectl logs deployment/celery-worker -n pyland --tail=50 | grep -i "email"
   ```

4. **Успешная отправка выглядит так:**
   ```
   [INFO] Task authentication.tasks.send_verification_email received
   [INFO] Email успешно отправлено пользователю user@example.com, результат: 1
   [INFO] Task succeeded in 1.234s
   ```

5. **Проверьте email адресата** — должно прийти письмо с подтверждением

---

## Альтернативные варианты

### Вариант 1: Использовать другой SMTP (не Gmail)

Если не хотите использовать Gmail, можете использовать:

- **SendGrid** (бесплатно 100 писем/день)
- **Mailgun** (бесплатно 1000 писем/месяц)
- **AWS SES** (0.10$ за 1000 писем)
- **Yandex SMTP** (smtp.yandex.ru:465)

Измените в `k8s/timeweb-deploy.yaml`:

```yaml
data:
  EMAIL_HOST: "smtp.sendgrid.net"  # Или другой провайдер
  EMAIL_PORT: "587"
  EMAIL_USE_TLS: "True"
```

### Вариант 2: Console backend (для тестирования)

Если хотите **временно отключить** отправку email и видеть их только в логах:

```yaml
data:
  EMAIL_BACKEND: "django.core.mail.backends.console.EmailBackend"
```

После этого письма будут выводиться в Celery логи, но не отправляться.

---

## Безопасность

**НЕ коммитьте** реальные credentials в Git!

Текущий `k8s/timeweb-deploy.yaml` в репозитории содержит пустые значения:
```yaml
EMAIL_HOST_USER: ""
EMAIL_HOST_PASSWORD: ""
```

**Для продакшена используйте:**
- Kubernetes Secrets (как сейчас) ✅
- External Secrets Operator
- HashiCorp Vault
- Sealed Secrets

**НЕ используйте:**
- ❌ Хардкод в коде
- ❌ ConfigMap для паролей (не зашифровано)
- ❌ Обычный пароль Gmail (только App Password)

---

## Troubleshooting

### Ошибка: "535 Authentication failed"
**Причина:** Неверный email или пароль.
**Решение:** Проверьте EMAIL_HOST_USER и перегенерируйте App Password.

### Ошибка: "530 Authentication Required"
**Причина:** Отсутствуют credentials.
**Решение:** Добавьте EMAIL_HOST_USER и EMAIL_HOST_PASSWORD в Secret.

### Ошибка: "Username and Password not accepted"
**Причина:** Используется обычный пароль вместо App Password.
**Решение:** Создайте App Password по инструкции выше.

### Email не приходит, но нет ошибок в логах
**Причина:** Попадает в SPAM или блокируется.
**Решение:**
1. Проверьте папку SPAM
2. Добавьте отправителя в контакты
3. Проверьте, что DEFAULT_FROM_EMAIL совпадает с EMAIL_HOST_USER

### "SMTPServerDisconnected"
**Причина:** Неверный порт или TLS настройки.
**Решение:** Gmail использует порт 587 с TLS. Проверьте:
```yaml
EMAIL_PORT: "587"
EMAIL_USE_TLS: "True"
```

---

## Текущая конфигурация

После применения изменений:

```yaml
# ConfigMap - публичные настройки
EMAIL_BACKEND: "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST: "smtp.gmail.com"
EMAIL_PORT: "587"
EMAIL_USE_TLS: "True"
DEFAULT_FROM_EMAIL: "pylandschool@gmail.com"

# Secret - приватные credentials
EMAIL_HOST_USER: "<ваш-gmail>"
EMAIL_HOST_PASSWORD: "<app-password>"
```

**Статус:** ⏳ Ожидает настройки credentials

---

## Следующие шаги

1. ✅ ConfigMap обновлен (EMAIL_BACKEND = smtp)
2. ✅ Переменные окружения добавлены в web/celery-worker
3. ⏳ **Нужно:** Добавить EMAIL_HOST_USER и EMAIL_HOST_PASSWORD в Secret
4. ⏳ **Нужно:** Применить изменения (`kubectl apply`)
5. ⏳ **Нужно:** Перезапустить deployments
6. ⏳ **Нужно:** Протестировать отправку email

**Время настройки:** ~5 минут
