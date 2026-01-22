# ✅ Чеклист деплоя на Kubernetes (через 3 недели)

## 🔒 ШАГ 1: Проверка секретов (ОБЯЗАТЕЛЬНО!)

### Откройте `k8s/timeweb-deploy.yaml` и обновите:

```yaml
# Строка 49: Django SECRET_KEY
SECRET_KEY: "ЗАМЕНИТЬ_НА_НОВЫЙ_КЛЮЧ"

# Строка 51: PostgreSQL Password
POSTGRES_PASSWORD: "ЗАМЕНИТЬ_НА_НОВЫЙ_ПАРОЛЬ"

# Строка 53-54: Gmail credentials
EMAIL_HOST_USER: "ваш-email@gmail.com"
EMAIL_HOST_PASSWORD: "gmail-app-password-16-символов"
```

**Генерация SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Gmail App Password:**
1. https://myaccount.google.com/security → Включить 2FA
2. https://myaccount.google.com/apppasswords → Создать
3. Выбрать "Mail" → "Other" → Назвать "Pyland"
4. Скопировать 16-значный пароль

---

## 🔧 ШАГ 2: Проверка конфигурации

### `k8s/timeweb-deploy.yaml` - ConfigMap:

- [ ] `DEBUG: "False"` ✅ (не "True"!)
- [ ] `SITE_URL: "https://pyland.ru"` ✅ (не http!)
- [ ] `ALLOWED_HOSTS` содержит все домены
- [ ] `CSRF_TRUSTED_ORIGINS` содержит https://pyland.ru
- [ ] `DATABASE_URL` содержит тот же пароль что и `POSTGRES_PASSWORD`

### `k8s/ingress.yaml`:

- [ ] Email для Let's Encrypt: `email: limpoposiki@gmail.com` (или ваш)
- [ ] Домены в hosts: `pyland.ru`, `www.pyland.ru`, `api.pyland.ru`

---

## 🐳 ШАГ 3: Docker и Registry

### Проверка доступа:

```bash
# Проверка Docker
docker --version

# Логин в GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Проверка pull
docker pull ghcr.io/ps965xx7vn-lgtm/backend:production
```

---

## ☸️ ШАГ 4: Kubernetes доступ

### Проверка кластера:

```bash
# Установка KUBECONFIG
export KUBECONFIG=~/.kube/timeweb-config

# Проверка подключения
kubectl cluster-info
kubectl get nodes

# Проверка namespace (если уже есть)
kubectl get pods -n pyland
```

### GitHub Registry Secret (только при первом деплое):

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  --docker-email=YOUR_EMAIL \
  -n pyland
```

---

## 🚀 ШАГ 5: ДЕПЛОЙ

### Автоматический (рекомендуется):

```bash
./deploy.sh
```

### Ручной:

```bash
# 1. Build образа
docker build --platform linux/amd64 -t ghcr.io/ps965xx7vn-lgtm/backend:production -f Dockerfile .

# 2. Push образа
docker push ghcr.io/ps965xx7vn-lgtm/backend:production

# 3. Применение манифестов
export KUBECONFIG=~/.kube/timeweb-config
kubectl apply -f k8s/timeweb-deploy.yaml
kubectl apply -f k8s/ingress.yaml

# 4. Перезапуск deployments
kubectl rollout restart deployment/web -n pyland
kubectl rollout restart deployment/celery-worker -n pyland
kubectl rollout restart deployment/celery-beat -n pyland

# 5. Ожидание готовности
kubectl rollout status deployment/web -n pyland --timeout=120s
```

---

## 🔍 ШАГ 6: Проверка статуса

### Поды:

```bash
# Все поды должны быть Running
kubectl get pods -n pyland

# Ожидаем:
# web-XXXXX              1/1  Running
# celery-worker-XXXXX    1/1  Running
# celery-beat-XXXXX      1/1  Running
# postgres-XXXXX         1/1  Running
# redis-XXXXX            1/1  Running
# django-migrations-XXX  0/1  Completed
```

### Логи (проверить на ошибки):

```bash
# Web логи
kubectl logs deployment/web -n pyland --tail=50

# Celery логи
kubectl logs deployment/celery-worker -n pyland --tail=50

# Если есть ошибки - см. TROUBLESHOOTING.md
```

### Ingress и SSL:

```bash
# Ingress должен иметь LoadBalancer IP
kubectl get ingress -n pyland

# SSL сертификат должен создаться (может занять 5-10 минут)
kubectl get certificate -n pyland

# Если READY = True - отлично
# Если READY = False - подождите или проверьте логи cert-manager
```

---

## 🌐 ШАГ 7: Проверка доступности

### HTTP/HTTPS тесты:

```bash
# Получить LoadBalancer IP
LB_IP=$(kubectl get ingress pyland-ingress -n pyland -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "LoadBalancer IP: $LB_IP"

# Тест HTTP (должен редиректить на HTTPS)
curl -I http://$LB_IP/api/ping

# Тест HTTPS
curl -k -I https://$LB_IP/api/health/

# С доменом (после настройки DNS)
curl -I https://pyland.ru/
curl -I https://pyland.ru/api/health/
curl https://pyland.ru/api/docs  # Swagger UI
```

### Проверка в браузере:

- [ ] https://pyland.ru/ - главная страница
- [ ] https://pyland.ru/admin/ - админ-панель
- [ ] https://pyland.ru/api/docs - API документация
- [ ] https://pyland.ru/ru/authentication/signup/ - регистрация

---

## 👤 ШАГ 8: Создание суперпользователя

```bash
kubectl exec -it deployment/web -n pyland -- python manage.py createsuperuser

# Ввести:
# Email: admin@pyland.ru
# Password: (надежный пароль)
```

**Вход в админку:**
- URL: https://pyland.ru/admin/
- Email: admin@pyland.ru
- Password: (ваш пароль)

---

## 📧 ШАГ 9: Проверка Email

### Тест регистрации:

1. Откройте https://pyland.ru/ru/authentication/signup/
2. Зарегистрируйте тестовый аккаунт
3. Проверьте почту - должно прийти письмо с подтверждением
4. Ссылка должна быть вида: `https://pyland.ru/ru/authentication/verify-email-confirm/...`
5. Кликните на ссылку - должна открыться страница подтверждения (не 404!)

### Если письма не приходят:

```bash
# Проверьте Celery логи
kubectl logs deployment/celery-worker -n pyland | grep -i email

# Проверьте Secret
kubectl get secret django-secret -n pyland -o jsonpath='{.data.EMAIL_HOST_USER}' | base64 -d
kubectl get secret django-secret -n pyland -o jsonpath='{.data.EMAIL_HOST_PASSWORD}' | base64 -d

# См. EMAIL_SMTP_SETUP.md для деталей
```

---

## 📊 ШАГ 10: Мониторинг (первые 30 минут)

```bash
# Следить за логами
kubectl logs -f deployment/web -n pyland

# Проверить ошибки
kubectl logs deployment/web -n pyland | grep -i error

# Проверить статус подов каждые 5 минут
watch kubectl get pods -n pyland
```

---

## 💾 ШАГ 11: Резервное копирование

```bash
# Бэкап базы данных
kubectl exec deployment/postgres -n pyland -- \
  pg_dump -U pyland_prod_user pyland_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Сохранить в безопасное место
```

---

## 🚨 Частые проблемы

| Проблема | Решение |
|----------|---------|
| `ImagePullBackOff` | Проверьте `ghcr-secret`: `kubectl get secret ghcr-secret -n pyland` |
| `CrashLoopBackOff` | Проверьте логи: `kubectl logs <POD> -n pyland` |
| Pod в состоянии `Pending` | Недостаточно ресурсов на ноде или PVC не создан |
| 404 на email ссылках | Проверьте что деплоили последний код с reverse() |
| Emails не отправляются | Проверьте Gmail credentials и App Password |
| SSL сертификат не создается | Проверьте DNS A-записи и логи cert-manager |
| База данных недоступна | Проверьте `kubectl logs deployment/postgres -n pyland` |

**Подробнее:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📚 Дополнительные документы

- **Полное руководство:** [K8S_DEPLOY_GUIDE.md](K8S_DEPLOY_GUIDE.md)
- **Архитектура:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Email Setup:** [EMAIL_SMTP_SETUP.md](EMAIL_SMTP_SETUP.md)
- **Git Workflow:** [GIT_WORKFLOW.md](GIT_WORKFLOW.md)

---

## ✅ Финальный чеклист

Перед тем как завершить деплой, убедитесь:

- [ ] Все поды в статусе `Running` или `Completed`
- [ ] LoadBalancer IP доступен
- [ ] HTTP редиректит на HTTPS
- [ ] HTTPS открывается в браузере
- [ ] SSL сертификат валиден (зеленый замок)
- [ ] API docs доступны
- [ ] Админ-панель доступна
- [ ] Суперпользователь создан
- [ ] Тестовая регистрация работает
- [ ] Email с подтверждением приходит
- [ ] Ссылка в письме работает (не 404)
- [ ] Логи не содержат критичных ошибок
- [ ] Создан бэкап базы данных

**Если все ✅ - деплой успешен! 🎉**

---

## 🆘 Экстренная помощь

Если что-то пошло не так:

```bash
# Полный откат
kubectl delete namespace pyland

# Пересоздание с нуля
kubectl apply -f k8s/timeweb-deploy.yaml
kubectl apply -f k8s/ingress.yaml
```

**Важно:** Перед удалением namespace сделайте бэкап базы данных!

---

**Последнее обновление:** 23 декабря 2025
**Версия:** 1.0.0
