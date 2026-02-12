#!/bin/bash

# ==============================================================================
# Генерация Kubernetes ConfigMap и Secret из .env файла
# ==============================================================================
# Использование: ./generate-k8s-secrets.sh [env-file]
# По умолчанию использует .env в корне проекта
# Вывод: k8s/generated/configmap.yaml и k8s/generated/secret.yaml
# ==============================================================================

set -e

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Путь к .env файлу
ENV_FILE="${1:-.env}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_PATH="$PROJECT_ROOT/$ENV_FILE"

# Директория для сгенерированных файлов
OUTPUT_DIR="$PROJECT_ROOT/k8s/generated"
mkdir -p "$OUTPUT_DIR"

CONFIGMAP_FILE="$OUTPUT_DIR/configmap.yaml"
SECRET_FILE="$OUTPUT_DIR/secret.yaml"

# Проверка существования .env
if [ ! -f "$ENV_PATH" ]; then
    echo "❌ Файл $ENV_PATH не найден!"
    echo "Использование: $0 [путь-к-.env]"
    exit 1
fi

log_info "Генерация Kubernetes манифестов из $ENV_FILE..."

# Переменные для ConfigMap (несекретные)
CONFIGMAP_VARS=(
    "DEBUG"
    "ALLOWED_HOSTS"
    "CSRF_TRUSTED_ORIGINS"
    "EMAIL_BACKEND"
    "EMAIL_HOST"
    "EMAIL_PORT"
    "EMAIL_USE_TLS"
    "DEFAULT_FROM_EMAIL"
    "CELERY_BROKER_URL"
    "CELERY_RESULT_BACKEND"
    "SOCIAL_AUTH_JSONFIELD_ENABLED"
)

# Переменные для Secret (секретные)
SECRET_VARS=(
    "SECRET_KEY"
    "POSTGRES_DB"
    "POSTGRES_USER"
    "POSTGRES_PASSWORD"
    "DB_URL"
    "EMAIL_HOST_USER"
    "EMAIL_HOST_PASSWORD"
    "SOCIAL_AUTH_GITHUB_KEY"
    "SOCIAL_AUTH_GITHUB_SECRET"
    "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"
    "SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI"
    "ROLLBAR_TOKEN"
    "ROLLBAR_ENVIRONMENT"
)

# Функция для чтения значения из .env
get_env_value() {
    local key=$1
    local value=$(grep "^${key}=" "$ENV_PATH" | cut -d'=' -f2- | sed "s/^['\"]//;s/['\"]$//")
    echo "$value"
}

# Генерация ConfigMap
log_info "Создание ConfigMap..."
cat > "$CONFIGMAP_FILE" << 'EOF'
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: django-config
  namespace: pyland
data:
  K8S_DEPLOYMENT: "True"
EOF

for var in "${CONFIGMAP_VARS[@]}"; do
    value=$(get_env_value "$var")
    if [ -n "$value" ]; then
        echo "  $var: \"$value\"" >> "$CONFIGMAP_FILE"
    fi
done

# Добавляем специфичные для k8s переменные
cat >> "$CONFIGMAP_FILE" << 'EOF'
  # Kubernetes-specific overrides
  DATABASE_URL: "postgresql://pyland_user:pyland_password@postgres-service:5432/pyland_db"
  REDIS_URL: "redis://redis-service:6379/0"
  SITE_URL: "https://pylandschool.com"
EOF

log_success "ConfigMap создан: $CONFIGMAP_FILE"

# Генерация Secret
log_info "Создание Secret..."
cat > "$SECRET_FILE" << 'EOF'
---
apiVersion: v1
kind: Secret
metadata:
  name: django-secret
  namespace: pyland
type: Opaque
stringData:
EOF

for var in "${SECRET_VARS[@]}"; do
    value=$(get_env_value "$var")
    if [ -n "$value" ]; then
        echo "  $var: \"$value\"" >> "$SECRET_FILE"
    fi
done

log_success "Secret создан: $SECRET_FILE"

echo ""
log_success "Манифесты сгенерированы!"
echo "  ConfigMap: $CONFIGMAP_FILE"
echo "  Secret:    $SECRET_FILE"
echo ""
log_warning "⚠️  Не коммитьте файлы из k8s/generated/ в git!"
log_info "Применить: kubectl apply -f $CONFIGMAP_FILE -f $SECRET_FILE"
echo ""
