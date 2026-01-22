# 🚀 Полное руководство по деплою на Kubernetes

## Оглавление

1. [Предварительные требования](#предварительные-требования)
2. [Подготовка к деплою](#подготовка-к-деплою)
3. [Автоматический деплой](#автоматический-деплой)
4. [Ручной деплой](#ручной-деплой)
5. [Настройка секретов](#настройка-секретов)
6. [Проверка статуса](#проверка-статуса)
7. [Устранение проблем](#устранение-проблем)

---

## Предварительные требования

### 1. Установленные инструменты

```bash
# Docker (24.0+)
docker --version

# kubectl (1.28+)
kubectl version --client

# Git
git --version
```

### 2. Доступ к кластеру

```bash
# Настройка KUBECONFIG
export KUBECONFIG=~/.kube/timeweb-config

# Проверка подключения
kubectl cluster-info
kubectl get nodes
```

### 3. Docker Registry доступ

```bash
# GitHub Container Registry (GHCR)
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Проверка
docker pull ghcr.io/ps965xx7vn-lgtm/backend:production
```

---

## Подготовка к деплою

### Шаг 1: Обновление секретов

**Обязательно обновите перед деплоем!**

Откройте `k8s/timeweb-deploy.yaml` и замените:

```yaml
# Secret (строки 45-54)
stringData:
  SECRET_KEY: "django-prod-$ecure-k3y-7x9z!a2c#d4f%g6h*j8k(m0n)p1q=r3t+u5w-v7y"  # ⚠️ ЗАМЕНИТЬ
  POSTGRES_USER: "pyland_prod_user"
  POSTGRES_PASSWORD: "VXR8K9mN2pL5vT3wQ7jH6fY4nB1xC0eD8sA5kU9rM3g="  # ⚠️ ЗАМЕНИТЬ
  EMAIL_HOST_USER: "your-email@gmail.com"  # ⚠️ ЗАМЕНИТЬ
  EMAIL_HOST_PASSWORD: "your-app-password-here"  # ⚠️ ЗАМЕНИТЬ
```

**Как сгенерировать SECRET_KEY:**

```bash
# Вариант 1: Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Вариант 2: OpenSSL
openssl rand -base64 50
```

**Как получить Gmail App Password:**

1. Включите 2FA в Gmail: https://myaccount.google.com/security
2. Создайте App Password: https://myaccount.google.com/apppasswords
3. Выберите "Mail" → "Other (Custom name)" → "Pyland"
4. Скопируйте 16-значный пароль (вида: `abcd efgh ijkl mnop`)

### Шаг 2: Обновление ConfigMap

Проверьте настройки в `k8s/timeweb-deploy.yaml`:

```yaml
# ConfigMap (строки 14-40)
data:
  DEBUG: "False"  # ⚠️ В проде должно быть False
  ALLOWED_HOSTS: "pyland.ru,www.pyland.ru,api.pyland.ru,188.225.37.90"
  CSRF_TRUSTED_ORIGINS: "https://pyland.ru,https://www.pyland.ru,https://api.pyland.ru"
  DATABASE_URL: "postgresql://pyland_prod_user:PASSWORD@postgres-service:5432/pyland_db"  # Используйте тот же пароль
  SITE_URL: "https://pyland.ru"  # ⚠️ В проде должно быть https://
```

### Шаг 3: Обновление Ingress SSL

Откройте `k8s/ingress.yaml` и проверьте email для Let's Encrypt:

```yaml
# Строка 15
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    email: limpoposiki@gmail.com  # ⚠️ Ваш реальный email
```

### Шаг 4: GitHub Registry Secret

**Создайте секрет только при первом деплое:**

```bash
# GitHub Personal Access Token с правами read:packages
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  --docker-email=YOUR_EMAIL \
  -n pyland
```

---

## Автоматический деплой

### Вариант 1: Полный деплой (рекомендуется)

```bash
# Запустить скрипт
./deploy.sh
```

**Что делает скрипт:**

1. ✅ Проверяет Git статус
2. ✅ Собирает Docker образ (linux/amd64)
3. ✅ Загружает в ghcr.io
4. ✅ Применяет K8s манифесты
5. ✅ Перезапускает deployments
6. ✅ Проверяет статус подов
7. ✅ Тестирует HTTP/HTTPS endpoints

**Время деплоя:** 2-3 минуты

**Вывод при успешном деплое:**

```
====================================================================
✅ Деплой завершён!
====================================================================

📊 Информация о деплое:
  Docker образ:  ghcr.io/ps965xx7vn-lgtm/backend:production
  Image SHA:     5a86caf2a2a1
  Namespace:     pyland
  LoadBalancer:  188.225.37.90

🌐 URL для доступа:
  HTTP:  http://pyland.ru/
  HTTPS: https://pyland.ru/
  API:   https://pyland.ru/api/docs
```

---

## Ручной деплой

### Шаг 1: Build и Push образа

```bash
# Сборка для amd64 (важно для Timeweb)
docker build --platform linux/amd64 \
  -t ghcr.io/ps965xx7vn-lgtm/backend:production \
  -f Dockerfile .

# Загрузка в registry
docker push ghcr.io/ps965xx7vn-lgtm/backend:production
```

### Шаг 2: Применение манифестов

```bash
# Установка KUBECONFIG
export KUBECONFIG=~/.kube/timeweb-config

# Применение всех ресурсов
kubectl apply -f k8s/timeweb-deploy.yaml
kubectl apply -f k8s/ingress.yaml

# Проверка
kubectl get all -n pyland
```

### Шаг 3: Перезапуск deployments

```bash
# Перезапуск для подтягивания нового образа
kubectl rollout restart deployment/web -n pyland
kubectl rollout restart deployment/celery-worker -n pyland
kubectl rollout restart deployment/celery-beat -n pyland

# Ожидание готовности
kubectl rollout status deployment/web -n pyland --timeout=120s
kubectl rollout status deployment/celery-worker -n pyland --timeout=120s
kubectl rollout status deployment/celery-beat -n pyland --timeout=120s
```

---

## Настройка секретов

### Способ 1: Обновление через kubectl

```bash
# Обновление Django SECRET_KEY
kubectl create secret generic django-secret \
  --from-literal=SECRET_KEY="YOUR_NEW_SECRET_KEY" \
  --from-literal=POSTGRES_USER="pyland_prod_user" \
  --from-literal=POSTGRES_PASSWORD="YOUR_NEW_PASSWORD" \
  --from-literal=EMAIL_HOST_USER="your-email@gmail.com" \
  --from-literal=EMAIL_HOST_PASSWORD="your-app-password" \
  -n pyland \
  --dry-run=client -o yaml | kubectl apply -f -

# Перезапуск для применения
kubectl rollout restart deployment/web -n pyland
```

### Способ 2: Редактирование в кластере

```bash
# Редактирование секрета
kubectl edit secret django-secret -n pyland

# Кодирование значений в base64
echo -n "your-secret-value" | base64
```

### Способ 3: Через файл

```bash
# Создание локального секрета
cat <<EOF > django-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: django-secret
  namespace: pyland
type: Opaque
stringData:
  SECRET_KEY: "your-new-secret-key"
  POSTGRES_USER: "pyland_prod_user"
  POSTGRES_PASSWORD: "your-new-password"
  EMAIL_HOST_USER: "your-email@gmail.com"
  EMAIL_HOST_PASSWORD: "your-app-password"
EOF

# Применение
kubectl apply -f django-secret.yaml

# Удаление локального файла (безопасность!)
shred -u django-secret.yaml  # Linux
rm -P django-secret.yaml     # macOS
```

---

## Проверка статуса

### Поды и deployments

```bash
# Все ресурсы в namespace
kubectl get all -n pyland

# Статус подов
kubectl get pods -n pyland

# Подробная информация
kubectl describe pod <POD_NAME> -n pyland
```

### Логи

```bash
# Web логи (последние 100 строк)
kubectl logs -f deployment/web -n pyland --tail=100

# Celery worker логи
kubectl logs -f deployment/celery-worker -n pyland --tail=100

# Celery beat логи
kubectl logs -f deployment/celery-beat -n pyland --tail=100

# Postgres логи
kubectl logs deployment/postgres -n pyland --tail=50

# Redis логи
kubectl logs deployment/redis -n pyland --tail=50
```

### Ingress и SSL

```bash
# Статус Ingress
kubectl get ingress -n pyland

# Подробная информация
kubectl describe ingress pyland-ingress -n pyland

# SSL сертификат
kubectl get certificate -n pyland
kubectl describe certificate pyland-tls -n pyland

# Логи cert-manager
kubectl logs -n cert-manager deployment/cert-manager
```

### Health checks

```bash
# LoadBalancer IP
LB_IP=$(kubectl get ingress pyland-ingress -n pyland -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "LoadBalancer IP: $LB_IP"

# HTTP ping
curl -I http://$LB_IP/api/ping

# HTTPS health
curl -k -I https://$LB_IP/api/health/

# С доменом (после настройки DNS)
curl -I https://pyland.ru/api/health/
```

---

## Устранение проблем

### Под не запускается

```bash
# Проверка событий
kubectl get events -n pyland --sort-by='.lastTimestamp'

# Описание пода
kubectl describe pod <POD_NAME> -n pyland

# Логи предыдущего контейнера (если был рестарт)
kubectl logs <POD_NAME> -n pyland --previous

# Частые проблемы:
# - ImagePullBackOff: проверьте ghcr-secret
# - CrashLoopBackOff: проверьте логи и SECRET_KEY
# - Pending: недостаточно ресурсов на ноде
```

### База данных недоступна

```bash
# Проверка PostgreSQL пода
kubectl get pod -l app=postgres -n pyland

# Подключение к PostgreSQL
kubectl exec -it deployment/postgres -n pyland -- \
  psql -U pyland_prod_user -d pyland_db

# SQL команды:
# \dt - список таблиц
# \l - список баз данных
# SELECT * FROM auth_user LIMIT 5;
```

### Redis недоступен

```bash
# Проверка Redis пода
kubectl get pod -l app=redis -n pyland

# Подключение к Redis
kubectl exec -it deployment/redis -n pyland -- redis-cli

# Redis команды:
# PING - проверка связи
# INFO - информация о сервере
# DBSIZE - количество ключей
# KEYS * - список всех ключей
```

### Celery не обрабатывает задачи

```bash
# Проверка worker логов
kubectl logs deployment/celery-worker -n pyland --tail=100

# Проверка beat логов (для периодических задач)
kubectl logs deployment/celery-beat -n pyland --tail=100

# Подключение к Django shell
kubectl exec -it deployment/web -n pyland -- python manage.py shell

# Тест Celery задачи:
from authentication.tasks import send_verification_email
result = send_verification_email.delay(1, 'http://test.com', 'Test', 'template.html')
result.ready()
```

### SSL сертификат не создается

```bash
# Проверка cert-manager
kubectl get pods -n cert-manager

# Проверка CertificateRequest
kubectl get certificaterequest -n pyland
kubectl describe certificaterequest <NAME> -n pyland

# Проверка Challenge
kubectl get challenge -n pyland
kubectl describe challenge <NAME> -n pyland

# Частые проблемы:
# - DNS не настроен: проверьте A-записи
# - Email неверный: обновите в ingress.yaml
# - Rate limit Let's Encrypt: подождите 1 час
```

### Статические файлы не загружаются

```bash
# Проверка collectstatic
kubectl exec deployment/web -n pyland -- ls -la /app/staticfiles/

# Проверка WhiteNoise в логах
kubectl logs deployment/web -n pyland | grep -i whitenoise

# Тест загрузки
curl -I https://pyland.ru/static/admin/css/base.css
```

### Email не отправляются

```bash
# Проверка Celery worker логов
kubectl logs deployment/celery-worker -n pyland | grep -i email

# Проверка секрета
kubectl get secret django-secret -n pyland -o jsonpath='{.data.EMAIL_HOST_USER}' | base64 -d
kubectl get secret django-secret -n pyland -o jsonpath='{.data.EMAIL_HOST_PASSWORD}' | base64 -d

# Тест SMTP из пода
kubectl exec -it deployment/web -n pyland -- python manage.py shell

# В Django shell:
from django.core.mail import send_mail
send_mail('Test', 'Body', 'from@gmail.com', ['to@example.com'])
```

---

## Полезные команды

### Масштабирование

```bash
# Увеличение реплик web
kubectl scale deployment/web --replicas=3 -n pyland

# Уменьшение реплик
kubectl scale deployment/web --replicas=1 -n pyland

# Автоматическое масштабирование
kubectl autoscale deployment/web --min=1 --max=5 --cpu-percent=80 -n pyland
```

### Обновление образа

```bash
# Обновление тега образа
kubectl set image deployment/web web=ghcr.io/ps965xx7vn-lgtm/backend:v1.2.0 -n pyland

# Откат к предыдущей версии
kubectl rollout undo deployment/web -n pyland

# История деплоев
kubectl rollout history deployment/web -n pyland
```

### Резервное копирование

```bash
# Бэкап базы данных
kubectl exec deployment/postgres -n pyland -- \
  pg_dump -U pyland_prod_user pyland_db > backup_$(date +%Y%m%d).sql

# Восстановление из бэкапа
kubectl exec -i deployment/postgres -n pyland -- \
  psql -U pyland_prod_user -d pyland_db < backup_20250101.sql
```

### Очистка

```bash
# Удаление всех ресурсов
kubectl delete namespace pyland

# Удаление конкретных ресурсов
kubectl delete deployment web -n pyland
kubectl delete service web-service -n pyland

# Удаление завершенных Job
kubectl delete job django-migrations -n pyland
```

---

## Чеклист перед деплоем через 3 недели

### За день до деплоя:

- [ ] Обновил `SECRET_KEY` в `k8s/timeweb-deploy.yaml`
- [ ] Обновил `POSTGRES_PASSWORD` в `k8s/timeweb-deploy.yaml`
- [ ] Добавил реальные Gmail credentials в Secret
- [ ] Проверил `DEBUG=False` в ConfigMap
- [ ] Проверил `SITE_URL=https://pyland.ru` в ConfigMap
- [ ] Проверил email для Let's Encrypt в `k8s/ingress.yaml`
- [ ] Закоммитил все изменения (кроме секретов!)

### В день деплоя:

- [ ] Проверил доступ к кластеру: `kubectl get nodes`
- [ ] Проверил Docker Registry доступ: `docker pull ghcr.io/ps965xx7vn-lgtm/backend:production`
- [ ] Запустил `./deploy.sh`
- [ ] Проверил статус подов: `kubectl get pods -n pyland`
- [ ] Проверил HTTP: `curl -I http://pyland.ru/`
- [ ] Проверил HTTPS: `curl -I https://pyland.ru/`
- [ ] Проверил API: `curl https://pyland.ru/api/health/`
- [ ] Проверил SSL: `kubectl get certificate -n pyland`
- [ ] Создал суперюзера: `kubectl exec -it deployment/web -n pyland -- python manage.py createsuperuser`
- [ ] Зашел в админку: https://pyland.ru/admin/
- [ ] Проверил отправку email (регистрация тестового пользователя)

### После деплоя:

- [ ] Мониторинг логов первые 30 минут: `kubectl logs -f deployment/web -n pyland`
- [ ] Проверил все критичные эндпоинты
- [ ] Настроил мониторинг (если требуется)
- [ ] Создал бэкап базы данных
- [ ] Документировал возникшие проблемы

---

## Контакты и поддержка

- **Документация проекта:** [README.md](README.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Email Setup:** [EMAIL_SMTP_SETUP.md](EMAIL_SMTP_SETUP.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)

**Удачного деплоя! 🚀**
