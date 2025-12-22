# 🚀 Автоматический деплой на Kubernetes

## Быстрый старт

```bash
./deploy.sh
```

Один скрипт для полного деплоя: build → push → deploy → verify

---

## Что деплоится

- ✅ Django Web (Gunicorn)
- ✅ Celery Worker + Beat
- ✅ PostgreSQL 15
- ✅ Redis 7
- ✅ Nginx Ingress + Let's Encrypt SSL
- ✅ Health checks

**Домены**: pyland.ru, www.pyland.ru, api.pyland.ru
**SSL**: Автоматический (limpoposiki@gmail.com)

---

## Требования

1. **Docker**: `docker --version` (24.0+)
2. **kubectl**: Доступ к Timeweb кластеру
3. **KUBECONFIG**: `~/.kube/timeweb-config`

---

## Процесс деплоя

Скрипт автоматически:

1. Проверяет Git статус
2. Собирает Docker образ (amd64)
3. Загружает в ghcr.io
4. Применяет K8s манифесты
5. Перезапускает deployments
6. Проверяет статус подов
7. Тестирует HTTP/HTTPS

**Время**: 2-3 минуты

---

## После деплоя

### Проверка статуса

```bash
# Все поды
kubectl get pods -n pyland

# SSL сертификат
kubectl get certificate -n pyland

# Логи
kubectl logs -f deployment/web -n pyland
```

### Тестирование

```bash
# HTTP (редирект на HTTPS)
curl -I http://pyland.ru/

# HTTPS
curl -I https://pyland.ru/

# API
curl https://pyland.ru/api/health/
```

---

## Полезные команды

```bash
# Shell в контейнере
kubectl exec -it deployment/web -n pyland -- /bin/bash

# Django shell
kubectl exec -it deployment/web -n pyland -- python manage.py shell

# Создать суперюзера
kubectl exec -it deployment/web -n pyland -- python manage.py createsuperuser

# Масштабирование
kubectl scale deployment/web --replicas=3 -n pyland

# Откат версии
kubectl rollout undo deployment/web -n pyland
```

---

## Отладка

### Логи

```bash
kubectl logs -f deployment/web -n pyland
kubectl logs -f deployment/celery-worker -n pyland
```

### SSL проблемы

```bash
kubectl describe certificate pyland-tls -n pyland
kubectl get challenges -n pyland
```

### Пересоздание подов

```bash
kubectl delete pod -l app=web -n pyland
```

---

Подробная документация: см. комментарии в `deploy.sh`
