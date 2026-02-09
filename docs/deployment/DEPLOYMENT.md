# Pyland Production Deployment - Timeweb Kubernetes

## ✅ Статус деплоймента

Приложение успешно задеплоено на Timeweb Kubernetes кластер.

### Работающие сервисы:
- ✅ Django Web (1/1 Running) - порт 8000 с WhiteNoise для статики
- ✅ Celery Worker (1/1 Running) - асинхронные задачи
- ✅ Celery Beat (1/1 Running) - периодические задачи с django-celery-beat
- ✅ PostgreSQL (1/1 Running) - база данных с hostPath volume
- ✅ Redis (1/1 Running) - кеш и брокер с hostPath volume
- ✅ Nginx Ingress Controller (Running) - маршрутизация трафика
- ✅ Static Files - обслуживаются через WhiteNoise middleware

## 🌐 Доступ к приложению

### Текущие адреса:
- **LoadBalancer IP**: `188.225.37.90`
- **NodePort HTTP**: `194.87.215.91:30796`
- **NodePort HTTPS**: `194.87.215.91:31633`

### API Endpoints (работают):
```bash
# Health check
curl http://194.87.215.91:30796/api/health/

# Readiness check
curl http://194.87.215.91:30796/api/readiness/

# Ping
curl http://194.87.215.91:30796/api/ping

# API Documentation
curl http://194.87.215.91:30796/api/docs

# Static Files (проверка)
curl -I http://194.87.215.91:30796/static/admin/css/base.css

# Admin Page
open http://194.87.215.91:30796/admin/
```

## 📋 Настройка DNS

Для работы через доменное имя **pylandschool.com** добавьте A-записи в DNS:

### В панели управления доменом (например, Timeweb, Cloudflare):

| Тип | Имя | Значение | TTL |
|-----|-----|----------|-----|
| A | @ | 188.225.37.90 | 300 |
| A | www | 188.225.37.90 | 300 |
| A | api | 188.225.37.90 | 300 |

### Проверка DNS (после настройки):
```bash
# Проверка A-записей
dig pylandschool.com +short
dig www.pylandschool.com +short
dig api.pylandschool.com +short

# Должны вернуть: 188.225.37.90
```

### Временное тестирование (добавить в /etc/hosts):
```bash
# macOS/Linux
sudo sh -c 'echo "188.225.37.90 pylandschool.com www.pylandschool.com api.pylandschool.com" >> /etc/hosts'

# Windows (в C:\Windows\System32\drivers\etc\hosts)
188.225.37.90 pylandschool.com www.pylandschool.com api.pylandschool.com
```

## 🔧 Управление деплойментом

### Подключение к кластеру:
```bash
export KUBECONFIG=~/.kube/timeweb-config
kubectl cluster-info
```

### Просмотр статуса:
```bash
# Все поды
kubectl get pods -n pyland

# Логи web сервиса
kubectl logs -f deployment/web -n pyland

# Логи celery worker
kubectl logs -f deployment/celery-worker -n pyland

# Статус ingress
kubectl get ingress -n pyland
```

### Перезапуск сервисов:
```bash
# Перезапуск web
kubectl rollout restart deployment/web -n pyland

# Перезапуск всех deployment
kubectl rollout restart deployment -n pyland

# Применение изменений
kubectl apply -f k8s/timeweb-deploy.yaml
```

### Масштабирование:
```bash
# Увеличить количество web подов
kubectl scale deployment/web --replicas=2 -n pyland

# Статус масштабирования
kubectl rollout status deployment/web -n pyland
```

## 🔐 SSL/TLS (рекомендуется)

### Установка cert-manager:
```bash
# Установить cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Проверить установку
kubectl get pods -n cert-manager
```

### Создать ClusterIssuer для Let's Encrypt:
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: pylandschool@gmail.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

### Обновить Ingress для SSL:
Добавить аннотацию в `k8s/ingress.yaml`:
```yaml
metadata:
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - pylandschool.com
    - www.pylandschool.com
    - api.pylandschool.com
    secretName: pyland-tls-cert
```

## 📊 Мониторинг

### Проверка здоровья:
```bash
# Health check
curl http://pylandschool.com:30796/api/health/

# Readiness check
curl http://pylandschool.com:30796/api/readiness/

# Проверка БД и Redis
kubectl exec -it deployment/web -n pyland -- python manage.py check --database default
```

### Логи:
```bash
# Все логи namespace
kubectl logs -n pyland --all-containers=true --tail=100

# Логи определенного пода
kubectl logs -f <pod-name> -n pyland

# Логи с фильтром
kubectl logs -f deployment/web -n pyland | grep ERROR
```

### Метрики ресурсов:
```bash
# CPU и память нод
kubectl top nodes

# CPU и память подов
kubectl top pods -n pyland

# Детальная информация о поде
kubectl describe pod <pod-name> -n pyland
```

## 🗄️ Бэкапы данных

### PostgreSQL:
```bash
# Создать бэкап
kubectl exec -it deployment/postgres -n pyland -- pg_dump -U pyland_prod_user pyland_db > backup.sql

# Восстановить бэкап
kubectl exec -i deployment/postgres -n pyland -- psql -U pyland_prod_user pyland_db < backup.sql
```

### Данные на хосте:
```bash
# PostgreSQL data
/data/postgres

# Redis data
/data/redis
```

## 🚀 Обновление приложения

### 1. Обновление кода:
```bash
# Собрать новый образ
docker build --platform linux/amd64 -t ghcr.io/ps965xx7vn-lgtm/backend:production .

# Загрузить на GHCR
docker push ghcr.io/ps965xx7vn-lgtm/backend:production
```

### 2. Применить миграции:
```bash
# Удалить старую job и создать новую
kubectl delete job django-migrations -n pyland
kubectl apply -f k8s/timeweb-deploy.yaml

# Проверить статус миграций
kubectl logs job/django-migrations -n pyland
```

### 3. Перезапустить deployment:
```bash
kubectl rollout restart deployment/web deployment/celery-worker deployment/celery-beat -n pyland
```

## ⚙️ Конфигурация

### Секреты в production:
```yaml
POSTGRES_USER: pyland_prod_user
POSTGRES_PASSWORD: VXR8K9mN2pL5vT3wQ7jH6fY4nB1xC0eD8sA5kU9rM3g=
SECRET_KEY: django-prod-$ecure-k3y-7x9z!a2c#d4f%g6h*j8k(m0n)p1q=r3t+u5w-v7y
DATABASE_URL: postgresql://pyland_prod_user:***@postgres-service:5432/pyland_db
```

### ConfigMap переменные:
```yaml
DEBUG: "False"
ALLOWED_HOSTS: "*"
DATABASE_URL: postgresql://pyland_prod_user:***@postgres-service:5432/pyland_db
REDIS_URL: redis://redis-service:6379/0
CELERY_BROKER_URL: redis://redis-service:6379/0
```

## 🐛 Troubleshooting

### Pod не запускается:
```bash
# Проверить события
kubectl describe pod <pod-name> -n pyland

# Проверить логи
kubectl logs <pod-name> -n pyland --previous
```

### 503 Service Unavailable:
```bash
# Проверить endpoints
kubectl get endpoints web-service -n pyland

# Проверить readiness probe
kubectl describe pod <web-pod> -n pyland | grep Readiness
```

### База данных недоступна:
```bash
# Проверить статус PostgreSQL
kubectl get pods -n pyland -l app=postgres

# Проверить логи PostgreSQL
kubectl logs -f deployment/postgres -n pyland

# Тест подключения
kubectl exec -it deployment/web -n pyland -- python manage.py check --database default
```

### Redis недоступен:
```bash
# Проверить статус Redis
kubectl get pods -n pyland -l app=redis

# Проверить подключение
kubectl exec -it deployment/web -n pyland -- python -c "import redis; r=redis.from_url('redis://redis-service:6379/0'); print(r.ping())"
```

## 📝 Полезные команды

```bash
# Выполнить команду в поде
kubectl exec -it <pod-name> -n pyland -- sh

# Просмотр ресурсов
kubectl get all -n pyland

# Просмотр events
kubectl get events -n pyland --sort-by='.lastTimestamp'

# Копирование файлов
kubectl cp <pod-name>:/app/logs/django.log ./django.log -n pyland

# Port-forward для локального доступа
kubectl port-forward svc/web-service 8000:8000 -n pyland
```

## 📞 Контакты и поддержка

- **GitHub**: [ps965xx7vn-lgtm/backend](https://github.com/ps965xx7vn-lgtm/backend)
- **Docker Registry**: ghcr.io/ps965xx7vn-lgtm/backend

---

**Последнее обновление**: 22 декабря 2025
**Версия**: 1.0.0
**Статус**: ✅ Production Ready
