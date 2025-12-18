# Готовность к продакшену и план k8s автоматизации

**Дата анализа:** 18 декабря 2025 г.

## 📊 Текущее состояние CI/CD

### ✅ Что уже работает

#### 1. **GitHub Actions Workflows (4 workflow)**

- **ci.yml** - основной CI pipeline
  - ✅ PostgreSQL 15 + Redis 7 в services
  - ✅ Python 3.13 + Poetry
  - ✅ Кэширование virtualenv
  - ✅ Миграции + create_roles
  - ✅ Компиляция переводов (gettext)
  - ✅ Тесты: 134 passed, 9 skipped
  - ✅ Coverage upload в Codecov
  - ✅ Security checks (Safety, Bandit)
  - ✅ Code quality (Black, isort, Ruff)

- **docs.yml** - документация
  - ✅ Markdown linting
  - ✅ Link checking
  - ✅ Генерация индекса документации

- **pr-checks.yml** - проверки PR
- **dependency-updates.yml** - обновление зависимостей

#### 2. **Pre-commit hooks**

```bash
✅ Ruff (linting + formatting)
✅ Black (code formatting)
✅ isort (import sorting)
✅ Trailing whitespace
✅ YAML/JSON validation
✅ Large files detection
✅ Merge conflicts detection
✅ Private key detection
✅ Django-upgrade
✅ Bandit (security)
```

#### 3. **Настройки для продакшена**

```python
# settings.py - production-ready конфигурация
✅ SECRET_KEY через env
✅ DEBUG через env (по умолчанию False)
✅ ALLOWED_HOSTS через env
✅ DATABASE_URL через env (dj-database-url)
✅ REDIS_URL через env с fallback на dummy cache
✅ CSRF_TRUSTED_ORIGINS через env
✅ Loguru + Django logging настроены
✅ i18n: ru/en/ka переводы
```

---

## ⚠️ Что отсутствует для продакшена

### 🔴 **Критично (без этого не запустить)**

#### 1. **Containerization**
```bash
❌ Dockerfile отсутствует
❌ docker-compose.yml отсутствует
❌ .dockerignore отсутствует
❌ Нет multi-stage build
```

#### 2. **K8s Manifests**
```bash
❌ deployment.yaml
❌ service.yaml
❌ ingress.yaml
❌ configmap.yaml
❌ secrets.yaml
❌ statefulset.yaml (для PostgreSQL/Redis)
❌ persistent-volume-claim.yaml
❌ hpa.yaml (autoscaling)
```

#### 3. **Environment Variables Management**
```bash
❌ .env.example для продакшена
❌ Secrets management (не используем k8s secrets пока)
❌ DATABASE_URL не задан по умолчанию
❌ Нет health check endpoints
```

#### 4. **Static Files & Media**
```bash
⚠️ STATIC_ROOT не настроен для k8s PVC
⚠️ MEDIA_ROOT не настроен для объектного хранилища
⚠️ WhiteNoise или CDN не настроены
⚠️ collectstatic не запускается в CI
```

#### 5. **Database Migrations**
```bash
⚠️ Нет механизма автомиграций в k8s (Job)
⚠️ Нет проверки совместимости миграций
⚠️ Backup/restore стратегия отсутствует
```

#### 6. **Observability**
```bash
❌ Health check endpoint (/health, /readiness, /liveness)
❌ Prometheus metrics (/metrics)
❌ Sentry не настроен (есть в зависимостях, но не сконфигурирован)
❌ ELK/Grafana Loki для логов
❌ APM (Application Performance Monitoring)
```

### 🟡 **Важно (лучше иметь перед продом)**

#### 7. **CI/CD Enhancements**
```bash
⚠️ Нет Docker image build & push в GitHub Container Registry (GHCR)
⚠️ Нет автоматического деплоя в staging/production
⚠️ Нет rollback механизма
⚠️ Нет smoke tests после деплоя
```

#### 8. **Security**
```bash
⚠️ Нет Pod Security Standards (PSS)
⚠️ Нет Network Policies в k8s
⚠️ Нет RBAC для приложения
⚠️ SSL/TLS certificates management (cert-manager?)
⚠️ Secrets rotation отсутствует
```

#### 9. **Performance**
```bash
⚠️ Gunicorn/uWSGI не настроен (production WSGI server)
⚠️ Celery worker не в отдельном Deployment
⚠️ Redis для sessions vs cache (разделение)
⚠️ Database connection pooling (pgbouncer?)
⚠️ Resource limits не определены
```

#### 10. **Backup & Disaster Recovery**
```bash
❌ PostgreSQL backup стратегия
❌ Redis persistence (RDB/AOF)
❌ Media files backup
❌ Disaster recovery plan
```

---

## 🚀 План автоматизации для k8s

### Фаза 1: Containerization (1-2 дня)

**Приоритет: КРИТИЧНЫЙ**

- [ ] Создать `Dockerfile` с multi-stage build
  - Builder stage: установка зависимостей
  - Final stage: минимальный production образ
  - Gunicorn как WSGI сервер
  - Collectstatic встроен в build

- [ ] Создать `docker-compose.yml` для локальной разработки
  - Django app
  - PostgreSQL 15
  - Redis 7
  - Celery worker
  - Celery beat

- [ ] Создать `.dockerignore`

- [ ] Протестировать локально:
  ```bash
  docker-compose up --build
  docker-compose exec web python manage.py migrate
  docker-compose exec web python manage.py create_roles
  ```

### Фаза 2: Health Checks & Observability (1 день)

**Приоритет: КРИТИЧНЫЙ**

- [ ] Добавить health check endpoints в Django
  ```python
  /health/ - базовая проверка
  /readiness/ - проверка БД + Redis
  /liveness/ - проверка что процесс жив
  ```

- [ ] Настроить Sentry
  - dsn в env
  - интеграция с Django
  - traces + errors

- [ ] Добавить Prometheus metrics (опционально)
  - `django-prometheus` package
  - `/metrics` endpoint

### Фаза 3: K8s Base Manifests (2-3 дня)

**Приоритет: ВЫСОКИЙ**

#### 3.1 ConfigMap & Secrets
```yaml
# configmap.yaml - несекретные конфиги
# secrets.yaml - SECRET_KEY, DATABASE_URL, REDIS_URL
```

#### 3.2 Deployments
```yaml
# deployment-web.yaml - Django app (Gunicorn)
# deployment-celery-worker.yaml - Celery workers
# deployment-celery-beat.yaml - Celery beat scheduler
```

#### 3.3 Services
```yaml
# service-web.yaml - ClusterIP для веб-приложения
# service-redis.yaml - ClusterIP для Redis
# service-postgres.yaml - ClusterIP для PostgreSQL
```

#### 3.4 StatefulSets (опционально, если БД внутри k8s)
```yaml
# statefulset-postgres.yaml - PostgreSQL
# statefulset-redis.yaml - Redis
```

**Рекомендация:** Использовать managed PostgreSQL (AWS RDS, Google Cloud SQL, Azure Database) вместо внутри k8s.

#### 3.5 Persistent Volumes
```yaml
# pvc-media.yaml - для media files
# pvc-static.yaml - для static files (если нужно)
```

#### 3.6 Ingress
```yaml
# ingress.yaml - NGINX Ingress Controller
# SSL/TLS с cert-manager (Let's Encrypt)
```

### Фаза 4: CI/CD для k8s (2 дня)

**Приоритет: ВЫСОКИЙ**

- [ ] Расширить `.github/workflows/ci.yml`:

  ```yaml
  # После успешных тестов:
  - name: Build Docker image
    run: docker build -t ghcr.io/${{ github.repository }}:${{ github.sha }} .

  - name: Push to GHCR
    run: docker push ghcr.io/${{ github.repository }}:${{ github.sha }}

  - name: Deploy to staging
    run: |
      kubectl set image deployment/pyland-web \
        web=ghcr.io/${{ github.repository }}:${{ github.sha }}
  ```

- [ ] Создать отдельный workflow `deploy.yml` для production
  - Ручной trigger (workflow_dispatch)
  - Проверка тегов (только vX.Y.Z)
  - Rollback механизм

- [ ] Smoke tests после деплоя:
  ```bash
  curl https://staging.pyland.com/health/
  ```

### Фаза 5: Database Migrations в k8s (1 день)

**Приоритет: СРЕДНИЙ**

- [ ] Создать `Job` для миграций:
  ```yaml
  # job-migrate.yaml
  # Запускается перед каждым деплоем
  # migrate + create_roles + compilemessages
  ```

- [ ] Использовать Helm hooks или ArgoCD PreSync hooks

### Фаза 6: Observability & Monitoring (2-3 дня)

**Приоритет: СРЕДНИЙ**

- [ ] Prometheus + Grafana
  - Метрики приложения
  - Dashboards для Django

- [ ] ELK или Grafana Loki
  - Централизованные логи
  - Loguru → JSON format → Loki

- [ ] Alerting
  - PagerDuty / Opsgenie
  - Critical alerts: DB down, Redis down, 5xx errors > threshold

### Фаза 7: Autoscaling & Performance (1-2 дня)

**Приоритет: НИЗКИЙ (можно позже)**

- [ ] Horizontal Pod Autoscaler (HPA)
  ```yaml
  # hpa.yaml
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  ```

- [ ] Vertical Pod Autoscaler (VPA) - опционально

- [ ] PgBouncer для connection pooling

- [ ] Redis Cluster (если нужна HA)

### Фаза 8: Security Hardening (2-3 дня)

**Приоритет: ВЫСОКИЙ**

- [ ] Pod Security Standards (PSS)
  ```yaml
  # Restricted profile
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    readOnlyRootFilesystem: true
  ```

- [ ] Network Policies
  - Только web → postgres
  - Только web/celery → redis
  - Deny all по умолчанию

- [ ] RBAC для приложения

- [ ] Secrets management
  - External Secrets Operator + AWS Secrets Manager
  - или Hashicorp Vault

- [ ] SSL/TLS
  - cert-manager для Let's Encrypt
  - Автоматическое обновление сертификатов

### Фаза 9: Backup & DR (1-2 дня)

**Приоритет: СРЕДНИЙ**

- [ ] PostgreSQL backups
  - Velero для k8s
  - pg_dump через CronJob
  - AWS RDS automatic backups

- [ ] Redis persistence
  - AOF включен
  - Снэпшоты в S3

- [ ] Media files backup
  - rsync в S3 через CronJob
  - или использовать S3 как primary storage (django-storages)

---

## 📋 Рекомендуемый порядок выполнения

### Неделя 1: Базовая инфраструктура
1. ✅ **День 1-2:** Dockerfile + docker-compose
2. ✅ **День 3:** Health checks + Sentry
3. ✅ **День 4-5:** ConfigMap, Secrets, Deployments, Services

### Неделя 2: CI/CD + Security
4. ✅ **День 1-2:** GitHub Actions для build & push образов
5. ✅ **День 3:** Migration Jobs
6. ✅ **День 4-5:** Security hardening (PSS, Network Policies)

### Неделя 3: Observability + Production
7. ✅ **День 1-2:** Prometheus/Grafana + Loki
8. ✅ **День 3:** Ingress + SSL/TLS
9. ✅ **День 4:** Smoke tests + Rollback
10. ✅ **День 5:** Backup стратегия

### Неделя 4: Оптимизация (опционально)
11. ⚪ HPA
12. ⚪ PgBouncer
13. ⚪ CDN для статики
14. ⚪ Load testing

---

## 🛠️ Технологический стек для k8s

### Обязательные компоненты
- **Container Registry:** GitHub Container Registry (GHCR)
- **K8s Cluster:** AWS EKS / GKE / Azure AKS / Minikube (для начала)
- **Ingress Controller:** NGINX Ingress
- **Certificate Manager:** cert-manager
- **Database:** Managed PostgreSQL (AWS RDS, Cloud SQL)
- **Cache:** Managed Redis (ElastiCache, Memorystore)

### Рекомендуемые инструменты
- **GitOps:** ArgoCD или Flux CD
- **Secrets:** External Secrets Operator + AWS Secrets Manager
- **Monitoring:** Prometheus + Grafana
- **Logging:** Grafana Loki или ELK Stack
- **Tracing:** Sentry (уже в зависимостях)
- **Backup:** Velero

---

## 📊 Оценка готовности

| Компонент | Статус | % Готовности |
|-----------|--------|--------------|
| CI/CD базовый | ✅ Готово | 100% |
| Тесты | ✅ Работают | 95% (7 файлов игнорируются) |
| Pre-commit | ✅ Настроен | 100% |
| Containerization | ❌ Отсутствует | 0% |
| K8s Manifests | ❌ Отсутствует | 0% |
| Health Checks | ❌ Нет | 0% |
| Observability | ⚠️ Частично | 20% (Sentry есть, не настроен) |
| Security | ⚠️ Базовая | 40% (bandit, но нет PSS) |
| Static/Media | ⚠️ Не готово | 30% (работает локально) |
| Secrets Management | ❌ Нет | 0% |

**Общая готовность к продакшену: ~25%**

---

## 🎯 Следующие шаги

### Прямо сейчас (следующие 30 минут):
1. Создать базовый `Dockerfile`
2. Создать `docker-compose.yml`
3. Создать `.dockerignore`

### Сегодня/завтра:
4. Добавить health check endpoints
5. Протестировать Docker локально
6. Настроить Sentry

### На этой неделе:
7. Создать базовые k8s manifests (ConfigMap, Deployment, Service)
8. Настроить GHCR в GitHub Actions
9. Первый деплой в Minikube/Kind локально

---

## 📚 Ссылки для изучения

- [Django + Kubernetes Best Practices](https://learnk8s.io/django-kubernetes)
- [12-Factor App](https://12factor.net/)
- [Django Production Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Helm Charts for Django](https://github.com/helm/charts/tree/master/stable/postgresql)
- [ArgoCD Getting Started](https://argo-cd.readthedocs.io/en/stable/getting_started/)

---

**Вывод:** CI отлично настроен, но для продакшена нужно добавить Dockerfile, k8s manifests, health checks и observability. Начнём с контейнеризации?
