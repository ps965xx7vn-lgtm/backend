#!/bin/bash

# ==============================================================================
# Pyland K8s Deploy Script - Автоматический деплой на Kubernetes
# ==============================================================================
# Использование: ./deploy.sh
#
# Этот скрипт автоматически:
# 1. Собирает Docker образ
# 2. Загружает в GitHub Container Registry
# 3. Деплоит на Kubernetes (Timeweb)
# 4. Проверяет статус
# ==============================================================================

set -e  # Exit on error

# Загрузка переменных из .env
if [ -f .env ]; then
    log_info "Загрузка конфигурации из .env..."
    set -a  # Автоматически экспортировать переменные
    source .env
    set +a
else
    echo "⚠️  Файл .env не найден! Используются значения по умолчанию."
fi

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для красивого вывода
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Конфигурация из .env или значения по умолчанию
KUBECONFIG="${KUBECONFIG:-~/.kube/timeweb-config}"
K8S_API_SERVER="${K8S_API_SERVER:-}"
DOCKER_IMAGE="${DOCKER_IMAGE:-ghcr.io/ps965xx7vn-lgtm/backend}"
DOCKER_TAG="${DOCKER_TAG:-production}"
NAMESPACE="${NAMESPACE:-pyland}"

# Проверка KUBECONFIG
if [ -z "$KUBECONFIG" ]; then
    export KUBECONFIG=~/.kube/timeweb-config
    log_warning "KUBECONFIG не установлен, используем ~/.kube/timeweb-config"
else
    # Раскрываем ~ в пути
    KUBECONFIG="${KUBECONFIG/#\~/$HOME}"
    export KUBECONFIG
fi

# Обновление kubeconfig если указан K8S_API_SERVER
if [ -n "$K8S_API_SERVER" ]; then
    log_info "Обновление kubeconfig с новым API сервером: $K8S_API_SERVER"
    if [ -f "$KUBECONFIG" ]; then
        # Обновляем IP в существующем kubeconfig
        sed -i.bak "s|server: https://[0-9.]*:6443|server: https://$K8S_API_SERVER:6443|g" "$KUBECONFIG"
        log_success "Kubeconfig обновлен"
    else
        log_warning "Файл $KUBECONFIG не найден"
    fi
fi

echo ""
echo "======================================================================"
echo "🚀 Pyland Kubernetes Deployment"
echo "======================================================================"
echo "  K8s API:      ${K8S_API_SERVER:-'из kubeconfig'}"
echo "  Namespace:    $NAMESPACE"
echo "  Docker Image: $DOCKER_IMAGE:$DOCKER_TAG"
echo "  Kubeconfig:   $KUBECONFIG"
echo "======================================================================"
echo ""

# Шаг 1: Git статус
log_info "Проверка Git статуса..."
if [[ -n $(git status -s) ]]; then
    log_warning "Есть незакоммиченные изменения:"
    git status -s
    read -p "Продолжить без коммита? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Деплой отменен"
        exit 1
    fi
else
    log_success "Git репозиторий чистый"
fi

# Шаг 2: Docker build
log_info "Сборка Docker образа (cross-platform amd64)..."
echo "Команда: docker build --platform linux/amd64 -t $DOCKER_IMAGE:$DOCKER_TAG ."
echo ""

if docker build --platform linux/amd64 -t $DOCKER_IMAGE:$DOCKER_TAG -f Dockerfile .; then
    log_success "Docker образ собран"
else
    log_error "Ошибка сборки Docker образа"
    exit 1
fi

# Получаем SHA образа
IMAGE_SHA=$(docker images --no-trunc --quiet $DOCKER_IMAGE:$DOCKER_TAG | cut -c8-19)
log_info "SHA образа: $IMAGE_SHA"

# Шаг 3: Docker push
log_info "Загрузка образа в GitHub Container Registry..."
if docker push $DOCKER_IMAGE:$DOCKER_TAG; then
    log_success "Образ загружен в registry"
else
    log_error "Ошибка загрузки образа"
    exit 1
fi

# Шаг 4: Kubernetes Deploy
log_info "Деплой в Kubernetes..."

# Генерация ConfigMap и Secret из .env
log_info "Генерация ConfigMap и Secret из .env..."
if [ -f "./k8s/scripts/generate-k8s-secrets.sh" ]; then
    ./k8s/scripts/generate-k8s-secrets.sh
else
    log_error "Скрипт generate-k8s-secrets.sh не найден!"
    exit 1
fi

# Применяем все манифесты
log_info "Применение ConfigMap и Secret..."
kubectl apply -f k8s/generated/configmap.yaml --validate=false
kubectl apply -f k8s/generated/secret.yaml --validate=false

log_info "Применение основных манифестов..."
kubectl apply -f k8s/timeweb-deploy.yaml --validate=false

log_info "Применение Ingress с SSL..."
kubectl apply -f k8s/ingress.yaml --validate=false

# Перезапускаем deployments для загрузки нового образа
log_info "Перезапуск deployments..."
kubectl rollout restart deployment/web -n $NAMESPACE
kubectl rollout restart deployment/celery-worker -n $NAMESPACE
kubectl rollout restart deployment/celery-beat -n $NAMESPACE

log_success "Deployments перезапущены"

# Шаг 5: Ожидание готовности
log_info "Ожидание готовности подов (30 секунд)..."
sleep 30

# Проверка статуса
log_info "Проверка статуса подов..."
kubectl get pods -n $NAMESPACE

echo ""
log_info "Проверка статуса deployments..."
kubectl rollout status deployment/web -n $NAMESPACE --timeout=60s
kubectl rollout status deployment/celery-worker -n $NAMESPACE --timeout=60s
kubectl rollout status deployment/celery-beat -n $NAMESPACE --timeout=60s

# Шаг 6: Проверка сервисов
echo ""
log_info "Статус сервисов:"
kubectl get svc -n $NAMESPACE

# Шаг 7: Проверка Ingress
echo ""
log_info "Статус Ingress:"
kubectl get ingress -n $NAMESPACE

# Шаг 8: Проверка SSL сертификата
echo ""
log_info "Статус SSL сертификата:"
kubectl get certificate -n $NAMESPACE 2>/dev/null || log_warning "Сертификат ещё создаётся..."

# Шаг 9: Health checks
echo ""
log_info "Проверка доступности сервиса..."

# Получаем LoadBalancer IP
LB_IP=$(kubectl get ingress pyland-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)

if [ -n "$LB_IP" ]; then
    log_info "LoadBalancer IP: $LB_IP"

    # Тест HTTP
    log_info "Проверка HTTP..."
    if curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://$LB_IP/api/ping | grep -q "200"; then
        log_success "HTTP работает"
    else
        log_warning "HTTP не отвечает (возможно, редирект на HTTPS)"
    fi

    # Тест HTTPS
    log_info "Проверка HTTPS..."
    if curl -s -k -o /dev/null -w "%{http_code}" --max-time 10 https://$LB_IP/api/ping | grep -q "200"; then
        log_success "HTTPS работает"
    else
        log_warning "HTTPS не отвечает (сертификат может ещё создаваться)"
    fi
else
    log_warning "LoadBalancer IP не найден"
fi

# Финальная информация
echo ""
echo "======================================================================"
log_success "Деплой завершён!"
echo "======================================================================"
echo ""
echo "📊 Информация о деплое:"
echo "  Docker образ:  $DOCKER_IMAGE:$DOCKER_TAG"
echo "  Image SHA:     $IMAGE_SHA"
echo "  Namespace:     $NAMESPACE"
echo "  LoadBalancer:  ${LB_IP:-'Ожидание...'}"
echo ""
echo "🌐 URL для доступа:"
echo "  HTTP:  http://pylandschool.com/"
echo "  HTTPS: https://pylandschool.com/"
echo "  API:   https://pylandschool.com/api/docs"
echo ""
echo "📝 Полезные команды:"
echo "  Логи web:          kubectl logs -f deployment/web -n $NAMESPACE"
echo "  Логи celery:       kubectl logs -f deployment/celery-worker -n $NAMESPACE"
echo "  Список подов:      kubectl get pods -n $NAMESPACE"
echo "  Статус SSL:        kubectl get certificate -n $NAMESPACE"
echo "  Описание Ingress:  kubectl describe ingress pyland-ingress -n $NAMESPACE"
echo ""

# Проверка SSL сертификата
CERT_READY=$(kubectl get certificate pyland-tls -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
if [ "$CERT_READY" == "True" ]; then
    log_success "SSL сертификат готов и валиден!"
else
    log_warning "SSL сертификат ещё создаётся (обычно 1-2 минуты)"
    echo "  Проверить статус: kubectl describe certificate pyland-tls -n $NAMESPACE"
fi

echo ""
log_success "Готово! 🎉"
echo ""
