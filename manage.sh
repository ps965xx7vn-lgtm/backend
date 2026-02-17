#!/bin/bash

# ==============================================================================
# Pyland K8s Management Script - Deploy & Cleanup
# ==============================================================================
# Использование: ./manage.sh [deploy|cleanup]
#
# Команды:
#   deploy    - Полный деплой приложения на Kubernetes
#   cleanup   - Очистка всех ресурсов из namespace
# ==============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Загрузка переменных из .env
load_env() {
    if [ -f .env ]; then
        log_info "Загрузка конфигурации из .env..."
        set -a
        source .env
        set +a
    else
        log_warning "Файл .env не найден! Используются значения по умолчанию."
    fi

    # Конфигурация
    KUBECONFIG="${KUBECONFIG:-~/.kube/timeweb-config}"
    K8S_API_SERVER="${K8S_API_SERVER:-}"
    DOCKER_IMAGE="${DOCKER_IMAGE:-ghcr.io/ps965xx7vn-lgtm/backend}"
    DOCKER_TAG="${DOCKER_TAG:-production}"
    NAMESPACE="${NAMESPACE:-pyland}"

    # Раскрываем ~ в пути
    KUBECONFIG="${KUBECONFIG/#\~/$HOME}"
    export KUBECONFIG

    # Обновление kubeconfig если указан K8S_API_SERVER
    if [ -n "$K8S_API_SERVER" ]; then
        log_info "Обновление kubeconfig с новым API сервером: $K8S_API_SERVER"
        if [ -f "$KUBECONFIG" ]; then
            sed -i.bak "s|server: https://[0-9.]*:6443|server: https://$K8S_API_SERVER:6443|g" "$KUBECONFIG"
            log_success "Kubeconfig обновлен"
        else
            log_warning "Файл $KUBECONFIG не найден"
        fi
    fi
}

# ==============================================================================
# CLEANUP: Очистка всех ресурсов
# ==============================================================================
cleanup() {
    echo ""
    echo "======================================================================"
    echo "🗑️  Pyland Kubernetes Cleanup"
    echo "======================================================================"
    echo "  Namespace:  $NAMESPACE"
    echo "  Kubeconfig: $KUBECONFIG"
    echo "======================================================================"
    echo ""

    log_warning "Это удалит ВСЕ ресурсы из namespace $NAMESPACE!"
    read -p "Вы уверены? (введите 'yes' для подтверждения): " -r
    echo

    if [[ ! $REPLY == "yes" ]]; then
        log_error "Очистка отменена"
        exit 1
    fi

    log_info "Начинаем очистку..."
    echo ""

    # Удаление Ingress
    log_info "Удаление Ingress..."
    if kubectl get ingress -n $NAMESPACE --insecure-skip-tls-verify &> /dev/null; then
        kubectl delete ingress --all -n $NAMESPACE --insecure-skip-tls-verify --wait=true
        log_success "Ingress удален"
    else
        log_info "Ingress не найден"
    fi

    # Удаление Certificate
    log_info "Удаление SSL сертификатов..."
    if kubectl get certificate -n $NAMESPACE --insecure-skip-tls-verify &> /dev/null; then
        kubectl delete certificate --all -n $NAMESPACE --insecure-skip-tls-verify --wait=true
        log_success "Сертификаты удалены"
    else
        log_info "Сертификаты не найдены"
    fi

    # Удаление Jobs
    log_info "Удаление Jobs..."
    if kubectl get jobs -n $NAMESPACE --insecure-skip-tls-verify &> /dev/null; then
        kubectl delete jobs --all -n $NAMESPACE --insecure-skip-tls-verify --wait=true
        log_success "Jobs удалены"
    else
        log_info "Jobs не найдены"
    fi

    # Удаление Deployments
    log_info "Удаление Deployments..."
    if kubectl get deployments -n $NAMESPACE --insecure-skip-tls-verify &> /dev/null; then
        kubectl delete deployments --all -n $NAMESPACE --insecure-skip-tls-verify --wait=true
        log_success "Deployments удалены"
    else
        log_info "Deployments не найдены"
    fi

    # Удаление Services
    log_info "Удаление Services..."
    if kubectl get services -n $NAMESPACE --insecure-skip-tls-verify &> /dev/null; then
        kubectl delete services --all -n $NAMESPACE --insecure-skip-tls-verify --wait=true
        log_success "Services удалены"
    else
        log_info "Services не найдены"
    fi

    # Удаление ConfigMaps
    log_info "Удаление ConfigMaps..."
    if kubectl get configmaps -n $NAMESPACE --insecure-skip-tls-verify &> /dev/null; then
        kubectl delete configmaps --all -n $NAMESPACE --insecure-skip-tls-verify --wait=true
        log_success "ConfigMaps удалены"
    else
        log_info "ConfigMaps не найдены"
    fi

    # Удаление Secrets
    log_info "Удаление Secrets..."
    if kubectl get secrets -n $NAMESPACE --insecure-skip-tls-verify &> /dev/null; then
        kubectl delete secrets --all -n $NAMESPACE --insecure-skip-tls-verify --wait=true
        log_success "Secrets удалены"
    else
        log_info "Secrets не найдены"
    fi

    # Удаление PVCs
    log_info "Удаление PersistentVolumeClaims..."
    if kubectl get pvc -n $NAMESPACE --insecure-skip-tls-verify &> /dev/null; then
        kubectl delete pvc --all -n $NAMESPACE --insecure-skip-tls-verify --wait=true
        log_success "PVCs удалены"
    else
        log_info "PVCs не найдены"
    fi

    # Ждем завершения удаления подов
    log_info "Ожидание завершения удаления подов..."
    for i in {1..30}; do
        POD_COUNT=$(kubectl get pods -n $NAMESPACE --insecure-skip-tls-verify --no-headers 2>/dev/null | wc -l)
        if [ "$POD_COUNT" -eq 0 ]; then
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""

    # Финальная проверка
    log_info "Проверка оставшихся ресурсов..."
    kubectl get all -n $NAMESPACE --insecure-skip-tls-verify

    REMAINING=$(kubectl get all -n $NAMESPACE --insecure-skip-tls-verify --no-headers 2>/dev/null | wc -l)
    if [ "$REMAINING" -eq 0 ]; then
        log_success "Все ресурсы удалены из namespace $NAMESPACE"
        echo ""
        read -p "Удалить сам namespace $NAMESPACE? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kubectl delete namespace $NAMESPACE --insecure-skip-tls-verify --wait=true
            log_success "Namespace $NAMESPACE удален"
        else
            log_info "Namespace $NAMESPACE оставлен"
        fi
    else
        log_warning "Остались ресурсы в namespace $NAMESPACE"
    fi

    echo ""
    log_success "Очистка завершена! 🎉"
    echo ""
}

# ==============================================================================
# DEPLOY: Полный деплой приложения
# ==============================================================================
deploy() {
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
    if [ -z "$SKIP_GIT_CHECK" ]; then
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
    else
        log_warning "Проверка Git пропущена (SKIP_GIT_CHECK=1)"
    fi

    # Шаг 2 и 3: Docker build & push
    if [ -z "$SKIP_DOCKER_BUILD" ]; then
        log_info "Сборка Docker образа (cross-platform amd64)..."
        echo "Команда: docker build --platform linux/amd64 -t $DOCKER_IMAGE:$DOCKER_TAG ."
        echo ""

        if docker build --platform linux/amd64 -t $DOCKER_IMAGE:$DOCKER_TAG -f Dockerfile .; then
            log_success "Docker образ собран"
        else
            log_error "Ошибка сборки Docker образа"
            exit 1
        fi

        IMAGE_SHA=$(docker images --no-trunc --quiet $DOCKER_IMAGE:$DOCKER_TAG | cut -c8-19)
        log_info "SHA образа: $IMAGE_SHA"

        log_info "Загрузка образа в GitHub Container Registry..."
        if docker push $DOCKER_IMAGE:$DOCKER_TAG; then
            log_success "Образ загружен в registry"
        else
            log_error "Ошибка загрузки образа"
            exit 1
        fi
    else
        log_warning "Сборка и загрузка Docker образа пропущена (SKIP_DOCKER_BUILD=1)"
        log_info "Используется существующий образ: $DOCKER_IMAGE:$DOCKER_TAG"
    fi

    # Шаг 4: Kubernetes Deploy
    log_info "Деплой в Kubernetes..."

    # Создание namespace
    log_info "Создание namespace..."
    kubectl create namespace $NAMESPACE --insecure-skip-tls-verify --dry-run=client -o yaml | kubectl apply -f - --insecure-skip-tls-verify

    # Установка Ingress Controller и Cert-Manager
    log_info "Проверка и установка Ingress Controller и Cert-Manager..."
    if [ -f "./k8s/scripts/setup-ingress.sh" ]; then
        chmod +x ./k8s/scripts/setup-ingress.sh
        ./k8s/scripts/setup-ingress.sh
    else
        log_warning "Скрипт setup-ingress.sh не найден. Пропускаем установку Ingress..."
    fi

    # Генерация ConfigMap и Secret
    log_info "Генерация ConfigMap и Secret из .env..."
    if [ -f "./k8s/scripts/generate-k8s-secrets.sh" ]; then
        ./k8s/scripts/generate-k8s-secrets.sh
    else
        log_error "Скрипт generate-k8s-secrets.sh не найден!"
        exit 1
    fi

    # Применяем все манифесты
    log_info "Применение ConfigMap и Secret..."
    kubectl apply -f k8s/generated/configmap.yaml --insecure-skip-tls-verify --validate=false
    kubectl apply -f k8s/generated/secret.yaml --insecure-skip-tls-verify --validate=false

    log_info "Применение основных манифестов..."
    kubectl apply -f k8s/timeweb-deploy.yaml --insecure-skip-tls-verify --validate=false

    log_info "Применение Let's Encrypt ClusterIssuer..."
    kubectl apply -f k8s/letsencrypt-issuer.yaml --insecure-skip-tls-verify --validate=false

    log_info "Применение Ingress с SSL..."
    kubectl apply -f k8s/ingress.yaml --insecure-skip-tls-verify --validate=false

    # Перезапускаем deployments
    log_info "Перезапуск deployments..."
    kubectl rollout restart deployment/web -n $NAMESPACE --insecure-skip-tls-verify
    kubectl rollout restart deployment/celery-worker -n $NAMESPACE --insecure-skip-tls-verify
    kubectl rollout restart deployment/celery-beat -n $NAMESPACE --insecure-skip-tls-verify
    log_success "Deployments перезапущены"

    # Шаг 5: Ожидание готовности
    log_info "Ожидание готовности подов (30 секунд)..."
    sleep 30

    # Проверка статуса
    log_info "Проверка статуса подов..."
    kubectl get pods -n $NAMESPACE --insecure-skip-tls-verify

    echo ""
    log_info "Проверка статуса deployments..."
    kubectl rollout status deployment/web -n $NAMESPACE --timeout=60s --insecure-skip-tls-verify
    kubectl rollout status deployment/celery-worker -n $NAMESPACE --timeout=60s --insecure-skip-tls-verify
    kubectl rollout status deployment/celery-beat -n $NAMESPACE --timeout=60s --insecure-skip-tls-verify

    # Шаг 6: Проверка сервисов
    echo ""
    log_info "Статус сервисов:"
    kubectl get svc -n $NAMESPACE --insecure-skip-tls-verify

    # Шаг 7: Проверка Ingress
    echo ""
    log_info "Статус Ingress:"
    kubectl get ingress -n $NAMESPACE --insecure-skip-tls-verify

    # Шаг 8: Проверка SSL сертификата
    echo ""
    log_info "Статус SSL сертификата:"
    kubectl get certificate -n $NAMESPACE --insecure-skip-tls-verify 2>/dev/null || log_warning "Сертификат ещё создаётся..."

    # Финальная информация
    echo ""
    echo "======================================================================"
    log_success "Деплой завершён!"
    echo "======================================================================"
    echo ""
    echo "📊 Информация о деплое:"
    echo "  Docker образ:  $DOCKER_IMAGE:$DOCKER_TAG"
    echo "  Namespace:     $NAMESPACE"
    echo ""
    echo "🌐 URL для доступа:"
    echo "  HTTP:  http://pylandschool.com/"
    echo "  HTTPS: https://pylandschool.com/"
    echo "  API:   https://pylandschool.com/api/docs"
    echo ""
    echo "📝 Полезные команды:"
    echo "  Логи web:          kubectl logs -f deployment/web -n $NAMESPACE --insecure-skip-tls-verify"
    echo "  Логи celery:       kubectl logs -f deployment/celery-worker -n $NAMESPACE --insecure-skip-tls-verify"
    echo "  Список подов:      kubectl get pods -n $NAMESPACE --insecure-skip-tls-verify"
    echo "  Статус SSL:        kubectl get certificate -n $NAMESPACE --insecure-skip-tls-verify"
    echo "  Описание Ingress:  kubectl describe ingress pyland-ingress -n $NAMESPACE --insecure-skip-tls-verify"
    echo ""

    # Проверка SSL сертификата
    CERT_READY=$(kubectl get certificate pyland-tls -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' --insecure-skip-tls-verify 2>/dev/null)
    if [ "$CERT_READY" == "True" ]; then
        log_success "SSL сертификат готов и валиден!"
    else
        log_warning "SSL сертификат ещё создаётся (обычно 1-2 минуты)"
        echo "  Проверить статус: kubectl describe certificate pyland-tls -n $NAMESPACE --insecure-skip-tls-verify"
    fi

    echo ""
    log_success "Готово! 🎉"
    echo ""
}

# ==============================================================================
# MAIN: Выбор действия
# ==============================================================================
show_menu() {
    echo ""
    echo "======================================================================"
    echo -e "${CYAN}🚀 Pyland Kubernetes Management${NC}"
    echo "======================================================================"
    echo ""
    echo "Выберите действие:"
    echo ""
    echo "  1) Deploy   - Развернуть приложение на Kubernetes"
    echo "  2) Cleanup  - Очистить все ресурсы из namespace"
    echo "  3) Exit     - Выход"
    echo ""
    echo "======================================================================"
    echo ""
}

# Загружаем конфигурацию
load_env

# Если команда передана как аргумент
if [ $# -gt 0 ]; then
    case "$1" in
        deploy)
            deploy
            ;;
        cleanup)
            cleanup
            ;;
        *)
            echo "Использование: $0 [deploy|cleanup]"
            exit 1
            ;;
    esac
else
    # Интерактивное меню
    while true; do
        show_menu
        read -p "Ваш выбор [1-3]: " choice
        echo ""

        case $choice in
            1)
                deploy
                break
                ;;
            2)
                cleanup
                break
                ;;
            3)
                log_info "Выход..."
                exit 0
                ;;
            *)
                log_error "Неверный выбор. Попробуйте снова."
                sleep 2
                ;;
        esac
    done
fi
