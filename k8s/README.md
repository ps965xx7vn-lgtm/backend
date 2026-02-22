# Kubernetes Deployment для Pyland Backend

Полная настройка Kubernetes для Django приложения с PostgreSQL, Redis, Celery.

## 📁 Структура

```
k8s/
├── base/                           # Базовые манифесты
│   ├── namespace.yaml             # Namespace pyland
│   ├── configmap.yaml             # ConfigMap с настройками
│   ├── secret.yaml                # Secrets (переопределяются в overlays)
│   ├── deployment-web.yaml        # Django web deployment
│   ├── deployment-celery-worker.yaml  # Celery worker
│   ├── deployment-celery-beat.yaml    # Celery beat scheduler
│   ├── statefulset-postgres.yaml      # PostgreSQL StatefulSet
│   ├── statefulset-redis.yaml         # Redis StatefulSet
│   ├── service-web.yaml               # Web service
│   ├── service-postgres.yaml          # PostgreSQL service
│   ├── service-redis.yaml             # Redis service
│   ├── job-migrations.yaml            # Django migrations job
│   └── kustomization.yaml
│
└── overlays/                      # Окружения
    ├── dev/                       # Development
    │   ├── kustomization.yaml
    │   ├── configmap-patch.yaml
    │   └── secret-patch.yaml
    ├── staging/                   # Staging
    │   ├── kustomization.yaml
    │   ├── configmap-patch.yaml
    │   └── secret-patch.yaml
    └── prod/                      # Production
        ├── kustomization.yaml
        ├── configmap-patch.yaml
        ├── secret-patch.yaml
        ├── hpa.yaml              # Horizontal Pod Autoscaler
        └── ingress.yaml          # Ingress с TLS
```

---

## 🚀 Быстрый старт

### Предварительные требования

1. **Kubernetes кластер** (minikube, kind, GKE, EKS, AKS)
2. **kubectl** установлен и настроен
3. **kustomize** (встроен в kubectl >= 1.14)
4. **Docker образ** запушен в GHCR: `ghcr.io/ps965xx7vn-lgtm/backend`

### Development (локально)

```bash
# 1. Запустить minikube
minikube start --cpus=4 --memory=8192

# 2. Создать secrets с реальными значениями
# Отредактируй k8s/overlays/dev/secret-patch.yaml

# 3. Deploy в dev окружение
kubectl apply -k k8s/overlays/dev

# 4. Проверить статус
kubectl get pods -n pyland-dev
kubectl logs -n pyland-dev -l app=web

# 5. Запустить миграции
kubectl apply -f k8s/base/job-migrations.yaml

# 6. Создать суперпользователя
kubectl exec -it $(kubectl get pod -n pyland-dev -l app=web -o jsonpath='{.items[0].metadata.name}') \
  -n pyland-dev -- python manage.py createsuperuser

# 7. Пробросить порт
kubectl port-forward -n pyland-dev service/web-service 8000:8000

# 8. Открыть в браузере
http://localhost:8000/api/health/
http://localhost:8000/admin/
```

### Staging

```bash
# 1. Обновить secrets в k8s/overlays/staging/secret-patch.yaml

# 2. Deploy
kubectl apply -k k8s/overlays/staging

# 3. Проверить
kubectl get all -n pyland-staging
```

### Production

```bash
# 1. ОБЯЗАТЕЛЬНО обновить secrets!
# k8s/overlays/prod/secret-patch.yaml
# - Сгенерировать strong passwords
# - Сгенерировать Django SECRET_KEY

# 2. Deploy
kubectl apply -k k8s/overlays/prod

# 3. Проверить
kubectl get all -n pyland

# 4. Проверить ingress
kubectl get ingress -n pyland

# 5. Проверить HPA
kubectl get hpa -n pyland
```

---

## 🔐 Secrets Management

### Генерация секретов

```bash
# PostgreSQL password
openssl rand -base64 32

# Django SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Обновление secrets

1. **Отредактировать** `k8s/overlays/{env}/secret-patch.yaml`
2. **Применить изменения:**
   ```bash
   kubectl apply -k k8s/overlays/prod
   ```
3. **Перезапустить pods:**
   ```bash
   kubectl rollout restart deployment/web -n pyland
   kubectl rollout restart deployment/celery-worker -n pyland
   ```

---

## 📊 Мониторинг

### Логи

```bash
# Web logs
kubectl logs -n pyland -l app=web --tail=100 -f

# Celery worker logs
kubectl logs -n pyland -l app=celery-worker --tail=100 -f

# Celery beat logs
kubectl logs -n pyland -l app=celery-beat --tail=100 -f

# PostgreSQL logs
kubectl logs -n pyland -l app=postgres --tail=100 -f

# Все логи
kubectl logs -n pyland --all-containers --tail=100 -f
```

### Статус

```bash
# Все ресурсы
kubectl get all -n pyland

# Pods
kubectl get pods -n pyland -o wide

# Services
kubectl get svc -n pyland

# Ingress
kubectl get ingress -n pyland

# HPA (production)
kubectl get hpa -n pyland

# PVC (persistent volumes)
kubectl get pvc -n pyland
```

### Health checks

```bash
# Health endpoint
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://web-service.pyland:8000/api/health/

# Readiness endpoint
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://web-service.pyland:8000/api/readiness/

# Ping endpoint
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://web-service.pyland:8000/api/ping
```

---

## 🔧 Управление

### Scaling

```bash
# Manual scaling
kubectl scale deployment/web -n pyland --replicas=5

# Check HPA status
kubectl get hpa -n pyland -w
```

### Rolling updates

```bash
# Update image
kubectl set image deployment/web \
  web=ghcr.io/ps965xx7vn-lgtm/backend:v1.2.0 \
  -n pyland

# Check rollout status
kubectl rollout status deployment/web -n pyland

# Rollout history
kubectl rollout history deployment/web -n pyland

# Rollback
kubectl rollout undo deployment/web -n pyland
```

### Migrations

```bash
# Create migration job
kubectl create job --from=cronjob/django-migrations manual-migration-1 -n pyland

# Check job status
kubectl get jobs -n pyland

# Check job logs
kubectl logs job/manual-migration-1 -n pyland
```

### Создание суперпользователя

После первого деплоя необходимо создать суперпользователя для доступа к Django Admin.

#### Интерактивный способ (через промпт)

```bash
# Получить имя web-пода
kubectl get pods -n pyland -l app=web

# Открыть shell в pod и запустить createsuperuser
kubectl exec -it <web-pod-name> -n pyland -- python manage.py createsuperuser
```

Команда запросит:
- **Email** — адрес электронной почты (является логином)
- **Password** — пароль (минимум 8 символов)
- **Password (again)** — подтверждение пароля

#### Неинтерактивный способ (через переменные окружения)

```bash
# Создать суперпользователя без промптов
kubectl exec -it <web-pod-name> -n pyland -- \
  bash -c "DJANGO_SUPERUSER_EMAIL=admin@example.com \
           DJANGO_SUPERUSER_PASSWORD=strongpassword123 \
           python manage.py createsuperuser --noinput"
```

#### Через одноразовый Job (рекомендуется для CI/CD)

```bash
# Создать Job для инициализации суперпользователя
kubectl run create-superuser \
  --image=ghcr.io/ps965xx7vn-lgtm/backend:latest \
  --restart=Never \
  --env="DJANGO_SUPERUSER_EMAIL=admin@example.com" \
  --env="DJANGO_SUPERUSER_PASSWORD=strongpassword123" \
  -n pyland \
  -- python manage.py createsuperuser --noinput

# Проверить результат
kubectl logs create-superuser -n pyland

# Удалить Pod после выполнения
kubectl delete pod create-superuser -n pyland
```

> **⚠️ Важно:** Не используйте простые пароли в production. Сгенерируйте надёжный пароль:
> ```bash
> openssl rand -base64 16
> ```

#### Проверка и доступ к Admin

```bash
# Пробросить порт до web-service
kubectl port-forward -n pyland service/web-service 8000:8000

# Открыть Django Admin
http://localhost:8000/admin/
```

#### Сброс пароля суперпользователя

```bash
kubectl exec -it <web-pod-name> -n pyland -- \
  python manage.py changepassword admin@example.com
```

### Database access

```bash
# Port forward PostgreSQL
kubectl port-forward -n pyland service/postgres-service 5432:5432

# Connect with psql
psql -h localhost -U pyland_user -d pyland_db

# Shell into postgres pod
kubectl exec -it -n pyland postgres-0 -- psql -U pyland_user -d pyland_db
```

### Redis access

```bash
# Port forward Redis
kubectl port-forward -n pyland service/redis-service 6379:6379

# Connect with redis-cli
redis-cli -h localhost -p 6379

# Shell into redis pod
kubectl exec -it -n pyland redis-0 -- redis-cli
```

---

## 🛠 Troubleshooting

### Pod не запускается

```bash
# Describe pod
kubectl describe pod <pod-name> -n pyland

# Events
kubectl get events -n pyland --sort-by='.lastTimestamp'

# Logs
kubectl logs <pod-name> -n pyland --previous
```

### ImagePullBackOff

```bash
# Check imagePullSecrets
kubectl get secrets -n pyland

# Create GHCR secret (if needed)
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=ps965xx7vn-lgtm \
  --docker-password=<PAT_TOKEN> \
  -n pyland

# Patch deployment
kubectl patch deployment web -n pyland \
  -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"ghcr-secret"}]}}}}'
```

### Health checks failing

```bash
# Check liveness
kubectl exec -it <pod-name> -n pyland -- \
  curl localhost:8000/api/health/

# Check readiness
kubectl exec -it <pod-name> -n pyland -- \
  curl localhost:8000/api/readiness/
```

### Database connection errors

```bash
# Test connection from web pod
kubectl exec -it <web-pod> -n pyland -- \
  python manage.py dbshell

# Check postgres service
kubectl get svc postgres-service -n pyland
kubectl get endpoints postgres-service -n pyland
```

---

## 🔄 CI/CD Integration

### GitHub Actions Deployment

```yaml
# .github/workflows/k8s-deploy.yml
name: K8s Deploy

on:
  push:
    branches: [main, prod]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3

      - name: Deploy to staging (main branch)
        if: github.ref == 'refs/heads/main'
        run: |
          kubectl apply -k k8s/overlays/staging

      - name: Deploy to prod (prod branch)
        if: github.ref == 'refs/heads/prod'
        run: |
          kubectl apply -k k8s/overlays/prod
```

---

## 📈 Production Optimization

### Resource Limits

Текущие настройки в base манифестах:

```yaml
# Web
requests:
  memory: "256Mi"
  cpu: "250m"
limits:
  memory: "512Mi"
  cpu: "500m"

# Celery Worker
requests:
  memory: "256Mi"
  cpu: "250m"
limits:
  memory: "512Mi"
  cpu: "500m"

# PostgreSQL
requests:
  memory: "256Mi"
  cpu: "250m"
limits:
  memory: "1Gi"
  cpu: "1000m"
```

### HPA Settings (Production)

```yaml
# Web HPA
minReplicas: 3
maxReplicas: 10
CPU target: 70%
Memory target: 80%

# Celery Worker HPA
minReplicas: 3
maxReplicas: 8
CPU target: 75%
```

---

## 🔒 Security Checklist

- [ ] Обновить все secrets (не использовать дефолтные значения)
- [ ] Включить Network Policies
- [ ] Настроить RBAC
- [ ] Включить Pod Security Policies
- [ ] Настроить TLS для ingress
- [ ] Включить encryption at rest для volumes
- [ ] Настроить image scanning (Trivy, Snyk)
- [ ] Ограничить egress traffic
- [ ] Включить audit logging

---

## 📚 Дополнительно

### Useful Commands Cheatsheet

```bash
# Get everything
kubectl get all -n pyland

# Delete everything
kubectl delete -k k8s/overlays/dev

# Restart all deployments
kubectl rollout restart deployment -n pyland

# Watch pods
kubectl get pods -n pyland -w

# Execute command in pod
kubectl exec -it <pod> -n pyland -- bash

# Copy files
kubectl cp <pod>:/app/file.txt ./file.txt -n pyland
```

### Links

- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Kustomize Docs](https://kustomize.io/)
- [Django Deployment](https://docs.djangoproject.com/en/5.0/howto/deployment/)
- [Project GitHub](https://github.com/ps965xx7vn-lgtm/backend)

---

**Готово! 🎉** Kubernetes манифесты созданы и готовы к использованию.
