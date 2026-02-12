# Kubernetes Scripts

## generate-k8s-secrets.sh

Автоматически генерирует Kubernetes ConfigMap и Secret из `.env` файла.

### Использование

```bash
# Из корня проекта
./k8s/scripts/generate-k8s-secrets.sh

# Или с указанием .env файла
./k8s/scripts/generate-k8s-secrets.sh .env.production
```

### Что делает

1. Читает переменные из `.env` файла
2. Разделяет их на:
   - **ConfigMap** (несекретные): DEBUG, ALLOWED_HOSTS, EMAIL_HOST и т.д.
   - **Secret** (секретные): SECRET_KEY, пароли, API ключи
3. Генерирует YAML файлы в `k8s/generated/`:
   - `configmap.yaml` - ConfigMap для Django
   - `secret.yaml` - Secret для чувствительных данных

### Важно

- ⚠️ **Не коммитьте** файлы из `k8s/generated/` в git!
- `k8s/generated/` добавлена в `.gitignore`
- Скрипт вызывается автоматически при `./deploy.sh`

### Переменные

#### ConfigMap (несекретные)
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`
- `DEFAULT_FROM_EMAIL`
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- `SOCIAL_AUTH_JSONFIELD_ENABLED`

#### Secret (секретные)
- `SECRET_KEY` - Django secret key
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - БД
- `DB_URL` - Database URL
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` - SMTP
- `SOCIAL_AUTH_GITHUB_KEY`, `SOCIAL_AUTH_GITHUB_SECRET` - GitHub OAuth
- `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`, `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` - Google OAuth
- `ROLLBAR_TOKEN`, `ROLLBAR_ENVIRONMENT` - Мониторинг

### Применение вручную

```bash
# Сгенерировать
./k8s/scripts/generate-k8s-secrets.sh

# Применить
kubectl apply -f k8s/generated/configmap.yaml
kubectl apply -f k8s/generated/secret.yaml
```

### Обновление секретов в продакшене

```bash
# 1. Обновите .env файл
nano .env

# 2. Сгенерируйте новые манифесты
./k8s/scripts/generate-k8s-secrets.sh

# 3. Примените изменения
kubectl apply -f k8s/generated/configmap.yaml
kubectl apply -f k8s/generated/secret.yaml

# 4. Перезапустите поды для загрузки новых значений
kubectl rollout restart deployment/web -n pyland
kubectl rollout restart deployment/celery-worker -n pyland
kubectl rollout restart deployment/celery-beat -n pyland
```

## Структура

```
k8s/
├── scripts/
│   ├── generate-k8s-secrets.sh  # Генератор ConfigMap/Secret
│   └── README.md                # Эта документация
├── generated/                   # Игнорируется git
│   ├── configmap.yaml          # Сгенерированный ConfigMap
│   └── secret.yaml             # Сгенерированный Secret
├── base/                        # Базовые манифесты (не используются с timeweb)
├── overlays/                    # Оверлеи для разных окружений
├── timeweb-deploy.yaml          # All-in-one деплой для Timeweb
└── ingress.yaml                 # Ingress с SSL
```
