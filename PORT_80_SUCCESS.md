# ✅ Порты 80 и 443 успешно открыты

**Дата**: 22 декабря 2025
**Статус**: ПОРТ 80 РАБОТАЕТ ✅ | ПОРТ 443 ОТКРЫТ (SSL не настроен) ⚠️

---

## 🎉 Проблема решена!

### Что было сделано

**Timeweb открыл порты 80 и 443** на LoadBalancer IP `188.225.37.90`.

**Проблема была**: В локальном файле `/etc/hosts` была старая запись с IP ноды вместо LoadBalancer IP.

### Исправление

```bash
# Было (старая запись с IP ноды)
194.87.215.91 pyland.ru www.pyland.ru api.pyland.ru

# Стало (правильный LoadBalancer IP)
188.225.37.90 pyland.ru www.pyland.ru api.pyland.ru
```

---

## ✅ Что работает сейчас

### HTTP доступ (порт 80)

```bash
# Главная страница
curl -I http://pyland.ru/
# HTTP/1.1 302 Found → /ru/

# WWW поддомен
curl -I http://www.pyland.ru/
# HTTP/1.1 302 Found → /ru/

# Статика через WhiteNoise
curl -I http://pyland.ru/static/admin/css/base.css
# HTTP/1.1 200 OK
# Content-Type: text/css; charset="utf-8"

# API Health Check
curl http://pyland.ru/api/health/
# {"status": "healthy", "service": "pyland-backend", "version": "1.0.0"}
```

### DNS и сеть

```bash
# DNS резолвится правильно
dig pyland.ru +short
# 188.225.37.90 ✅

# Порт 80 открыт
nc -zv 188.225.37.90 80
# Connection to 188.225.37.90 port 80 [tcp/http] succeeded! ✅

# Порт 443 открыт
nc -zv 188.225.37.90 443
# Connection to 188.225.37.90 port 443 [tcp/https] succeeded! ✅
```

### Kubernetes

```bash
# LoadBalancer Service
NAME                       TYPE           EXTERNAL-IP     PORT(S)
ingress-nginx-controller   LoadBalancer   188.225.37.90   80:30796/TCP,443:31633/TCP

# Ingress
NAME             HOSTS                                            ADDRESS         PORTS
pyland-ingress   pyland.ru,www.pyland.ru,api.pyland.ru,...       188.225.37.90   80

# Все поды работают
NAME                            READY   STATUS      RESTARTS   AGE
web-6f7f9fc5fc-2vzqt            1/1     Running     0          17m
celery-worker-5b57f66fc-q9fmz   1/1     Running     0          17m
celery-beat-7b64f44965-gck82    1/1     Running     0          17m
postgres-64fd9776bd-xjq68       1/1     Running     0          107m
redis-7647f4d7b6-6vcx7          1/1     Running     0          107m
django-migrations-6297s         0/1     Completed   0          152m
```

---

## ⚠️ Требуется настроить SSL

### Текущая проблема

```bash
curl -I https://pyland.ru/
# curl: (60) SSL certificate problem: unable to get local issuer certificate
```

**Причина**: Порт 443 открыт, но SSL сертификата нет.

### Решение: Let's Encrypt + cert-manager

#### Шаг 1: Установить cert-manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

#### Шаг 2: Создать ClusterIssuer для Let's Encrypt

Создайте файл `k8s/letsencrypt-issuer.yaml`:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@pyland.ru  # Замените на ваш email
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

Примените:
```bash
kubectl apply -f k8s/letsencrypt-issuer.yaml
```

#### Шаг 3: Обновить Ingress с TLS

Добавьте в `k8s/timeweb-deploy.yaml` в секцию Ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pyland-ingress
  namespace: pyland
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"  # Добавить
    nginx.ingress.kubernetes.io/ssl-redirect: "true"     # Добавить
spec:
  ingressClassName: nginx
  tls:  # Добавить секцию TLS
  - hosts:
    - pyland.ru
    - www.pyland.ru
    - api.pyland.ru
    secretName: pyland-tls
  rules:
  - host: pyland.ru
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 8000
  # ... остальные правила
```

Примените изменения:
```bash
kubectl apply -f k8s/timeweb-deploy.yaml
```

#### Шаг 4: Проверка сертификата

```bash
# Проверить создание сертификата
kubectl get certificate -n pyland

# Проверить статус
kubectl describe certificate pyland-tls -n pyland

# Проверить секрет
kubectl get secret pyland-tls -n pyland
```

**Ожидается**:
- Certificate: Ready=True
- Secret: создан с ключом и сертификатом

#### Шаг 5: Проверка HTTPS

После выдачи сертификата (обычно 1-2 минуты):

```bash
# Проверить HTTPS
curl -I https://pyland.ru/
# HTTP/2 302 ✅
# location: /ru/

# Проверить сертификат
curl -vI https://pyland.ru/ 2>&1 | grep "subject:"
# subject: CN=pyland.ru ✅
```

---

## 📋 Checklist после настройки SSL

- [ ] `https://pyland.ru/` работает без ошибок
- [ ] `https://www.pyland.ru/` работает без ошибок
- [ ] `https://api.pyland.ru/` работает без ошибок
- [ ] Автоматический редирект с HTTP на HTTPS
- [ ] Сертификат валидный (зелёный замок в браузере)
- [ ] Сертификат автоматически обновляется (cert-manager)

---

## 🔍 Тестирование системы

### 1. Главная страница

```bash
# Открыть в браузере
http://pyland.ru/

# Ожидается:
# - Редирект на /ru/ (или другой язык)
# - Страница входа/регистрации
# - Загрузка статики (CSS, JS)
```

### 2. Регистрация с email

```bash
# Открыть
http://pyland.ru/account/signup

# Заполнить форму:
# - Email: test@example.com
# - Пароль: TestPass123
# - Имя: Test
# - Телефон: +79991234567
# - ✅ Отправить email с подтверждением (чекбокс)

# Ожидается:
# - Успешная регистрация
# - Сообщение: "Пожалуйста, подтвердите ваш email"
# - Email в логах Celery Worker
```

### 3. Проверка email отправки

```bash
# Проверить логи Celery Worker
export KUBECONFIG=~/.kube/timeweb-config
kubectl logs deployment/celery-worker -n pyland --tail=50

# Ожидается:
# Task authentication.tasks.send_verification_email received
# Task authentication.tasks.send_verification_email succeeded in 0.1s
```

### 4. API endpoints

```bash
# Health check
curl http://pyland.ru/api/health/
# {"status": "healthy", ...}

# Ping
curl http://pyland.ru/api/ping
# {"ping": "pong"}

# Docs (Swagger UI)
http://pyland.ru/api/docs
```

### 5. Админка Django

```bash
# Создать суперпользователя (если ещё не создан)
kubectl exec -it deployment/web -n pyland -- python manage.py createsuperuser

# Открыть админку
http://pyland.ru/admin/

# Ожидается:
# - Форма входа
# - Вход работает
# - Стили загружаются (WhiteNoise)
```

---

## 📊 Текущая инфраструктура

### Домены

| Домен | IP | Порт | Статус |
|-------|-------|------|--------|
| pyland.ru | 188.225.37.90 | 80 | ✅ Работает |
| www.pyland.ru | 188.225.37.90 | 80 | ✅ Работает |
| api.pyland.ru | 188.225.37.90 | 80 | ✅ Работает |
| pyland.ru | 188.225.37.90 | 443 | ⚠️ Открыт, SSL не настроен |

### Kubernetes Services

```yaml
LoadBalancer:
  IP: 188.225.37.90
  Ports:
    - 80:30796  (HTTP)
    - 443:31633 (HTTPS)

ClusterIP Services:
  - web-service: 10.111.193.207:8000
  - postgres-service: Headless (None)
  - redis-service: Headless (None)
```

### Deployments

```yaml
web:
  Image: ghcr.io/ps965xx7vn-lgtm/backend:production
  SHA: c117e0d14925
  Replicas: 1
  Features:
    - Django 5.2 + Django Ninja
    - WhiteNoise static files
    - Redis caching
    - show_notifications в регистрации ✅

celery-worker:
  Image: Same as web
  Replicas: 1
  Status: Processing tasks ✅

celery-beat:
  Image: Same as web
  Replicas: 1
  Status: Scheduling tasks ✅

postgres:
  Version: 15
  Storage: PersistentVolumeClaim

redis:
  Version: 7
  Storage: PersistentVolumeClaim
```

---

## 🚀 Что дальше

### Высокий приоритет

1. **✅ Настроить SSL через Let's Encrypt** (инструкции выше)
2. Настроить SMTP для реальной отправки email
   ```bash
   kubectl edit configmap django-config -n pyland
   # Изменить EMAIL_BACKEND на SMTP
   # Добавить EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
   ```

### Средний приоритет

3. Настроить мониторинг (Prometheus + Grafana)
4. Настроить backup для PostgreSQL
5. Увеличить количество реплик для production
   ```yaml
   replicas: 3  # для web
   replicas: 2  # для celery-worker
   ```

### Низкий приоритет

6. Настроить CDN (CloudFlare) для статики
7. Настроить rate limiting на уровне Ingress
8. Добавить health checks в deployments

---

## 📝 Полезные команды

### Мониторинг

```bash
# Все поды
kubectl get pods -n pyland -w

# Логи веб-сервера
kubectl logs -f deployment/web -n pyland

# Логи Celery Worker
kubectl logs -f deployment/celery-worker -n pyland

# Метрики
kubectl top pods -n pyland
```

### Deployment

```bash
# Пересобрать и загрузить новый образ
docker build --platform linux/amd64 -t ghcr.io/ps965xx7vn-lgtm/backend:production .
docker push ghcr.io/ps965xx7vn-lgtm/backend:production

# Перезапустить деплойменты
kubectl rollout restart deployment/web -n pyland
kubectl rollout restart deployment/celery-worker -n pyland
kubectl rollout restart deployment/celery-beat -n pyland

# Проверить статус
kubectl rollout status deployment/web -n pyland
```

### Отладка

```bash
# Shell в контейнере
kubectl exec -it deployment/web -n pyland -- /bin/bash

# Django shell
kubectl exec -it deployment/web -n pyland -- python manage.py shell

# Выполнить management команду
kubectl exec -it deployment/web -n pyland -- python manage.py createsuperuser

# Проверить ConfigMap
kubectl get configmap django-config -n pyland -o yaml

# Проверить Secrets
kubectl get secret django-secret -n pyland -o yaml
```

---

## 🎯 Итог

### ✅ Решено

1. **Порт 80 открыт и работает** - сайт доступен по `http://pyland.ru/`
2. **show_notifications работает** - чекбокс в форме регистрации
3. **Email система работает** - Celery отправляет задачи
4. **Все сервисы запущены** - web, celery, postgres, redis
5. **DNS настроен правильно** - домен резолвится на LoadBalancer IP
6. **Ingress работает** - Nginx маршрутизирует трафик

### 📋 Осталось

1. **Настроить SSL** - Let's Encrypt + cert-manager (15 минут)
2. **SMTP email** - реальная отправка писем (опционально)

---

**Дата**: 22 декабря 2025, 21:40 MSK
**Статус**: ✅ PRODUCTION READY (HTTP)
**Действие**: Настроить SSL для HTTPS
