#!/bin/bash

# ==============================================================================
# Setup Ingress Controller and Cert-Manager for Kubernetes
# ==============================================================================
# Использование: ./setup-ingress.sh
# Устанавливает nginx-ingress и cert-manager если их нет в кластере
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

# Проверка наличия kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl не найден!"
    exit 1
fi

log_info "Проверка Ingress Controller и Cert-Manager..."
echo ""

# ==============================================================================
# Проверка и установка Nginx Ingress Controller
# ==============================================================================
log_info "Проверка Nginx Ingress Controller..."

if kubectl get namespace ingress-nginx --insecure-skip-tls-verify &> /dev/null; then
    INGRESS_PODS=$(kubectl get pods -n ingress-nginx --insecure-skip-tls-verify -l app.kubernetes.io/name=ingress-nginx --no-headers 2>/dev/null | wc -l)

    if [ "$INGRESS_PODS" -gt 0 ]; then
        log_success "Nginx Ingress Controller уже установлен"
    else
        log_warning "Namespace ingress-nginx существует, но нет подов. Переустанавливаем..."
        kubectl delete namespace ingress-nginx --insecure-skip-tls-verify --wait=true 2>/dev/null || true
        sleep 5
    fi
fi

if ! kubectl get namespace ingress-nginx --insecure-skip-tls-verify &> /dev/null || [ "$INGRESS_PODS" -eq 0 ]; then
    log_info "Установка Nginx Ingress Controller..."

    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml \
        --insecure-skip-tls-verify --validate=false

    log_success "Nginx Ingress Controller установлен"

    # Ждем готовности
    log_info "Ожидание запуска Ingress Controller (до 60 секунд)..."
    for i in {1..12}; do
        READY_PODS=$(kubectl get pods -n ingress-nginx --insecure-skip-tls-verify -l app.kubernetes.io/component=controller --no-headers 2>/dev/null | grep "Running" | wc -l)
        if [ "$READY_PODS" -gt 0 ]; then
            log_success "Ingress Controller запущен"
            break
        fi
        echo -n "."
        sleep 5
    done
    echo ""

    # Включаем hostNetwork для работы на портах 80/443
    log_info "Настройка hostNetwork для Ingress Controller..."
    kubectl patch deployment ingress-nginx-controller -n ingress-nginx \
        --insecure-skip-tls-verify \
        --type='json' \
        -p='[{"op": "add", "path": "/spec/template/spec/hostNetwork", "value": true}]'

    log_info "Ожидание перезапуска контроллера..."
    sleep 10

    log_success "Ingress Controller настроен с hostNetwork"
fi

# ==============================================================================
# Проверка и установка Cert-Manager
# ==============================================================================
log_info "Проверка Cert-Manager..."

if kubectl get namespace cert-manager --insecure-skip-tls-verify &> /dev/null; then
    CERT_MANAGER_PODS=$(kubectl get pods -n cert-manager --insecure-skip-tls-verify -l app.kubernetes.io/instance=cert-manager --no-headers 2>/dev/null | wc -l)

    if [ "$CERT_MANAGER_PODS" -gt 0 ]; then
        log_success "Cert-Manager уже установлен"
    else
        log_warning "Namespace cert-manager существует, но нет подов. Переустанавливаем..."
        kubectl delete namespace cert-manager --insecure-skip-tls-verify --wait=true 2>/dev/null || true
        sleep 5
    fi
fi

if ! kubectl get namespace cert-manager --insecure-skip-tls-verify &> /dev/null || [ "$CERT_MANAGER_PODS" -eq 0 ]; then
    log_info "Установка Cert-Manager..."

    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml \
        --insecure-skip-tls-verify --validate=false

    log_success "Cert-Manager установлен"

    # Ждем готовности
    log_info "Ожидание запуска Cert-Manager (до 60 секунд)..."
    for i in {1..12}; do
        READY_PODS=$(kubectl get pods -n cert-manager --insecure-skip-tls-verify --no-headers 2>/dev/null | grep "Running" | wc -l)
        if [ "$READY_PODS" -ge 3 ]; then
            log_success "Cert-Manager запущен"
            break
        fi
        echo -n "."
        sleep 5
    done
    echo ""
fi

# ==============================================================================
# Проверка и создание ClusterIssuer для Let's Encrypt
# ==============================================================================
log_info "Проверка Let's Encrypt ClusterIssuer..."

if kubectl get clusterissuer letsencrypt-prod --insecure-skip-tls-verify &> /dev/null; then
    log_success "ClusterIssuer letsencrypt-prod уже существует"
else
    log_info "Создание ClusterIssuer letsencrypt-prod..."

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    LETSENCRYPT_FILE="$SCRIPT_DIR/../letsencrypt-issuer.yaml"

    if [ -f "$LETSENCRYPT_FILE" ]; then
        kubectl apply -f "$LETSENCRYPT_FILE" --insecure-skip-tls-verify --validate=false
        log_success "ClusterIssuer создан"
    else
        log_warning "Файл letsencrypt-issuer.yaml не найден в k8s/"
    fi
fi

# ==============================================================================
# Финальная проверка
# ==============================================================================
echo ""
log_info "Финальная проверка компонентов..."

echo ""
echo "Ingress-Nginx:"
kubectl get pods -n ingress-nginx --insecure-skip-tls-verify

echo ""
echo "Cert-Manager:"
kubectl get pods -n cert-manager --insecure-skip-tls-verify

echo ""
echo "ClusterIssuers:"
kubectl get clusterissuer --insecure-skip-tls-verify

echo ""
log_success "Установка Ingress и Cert-Manager завершена!"
echo ""
