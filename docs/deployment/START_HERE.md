# 🚀 START HERE - Быстрый деплой

**Последнее обновление:** 22 января 2026

---

## Что нужно сделать перед деплоем

### ✅ За 1 день до деплоя:

1. **Обновить секреты** в `k8s/timeweb-deploy.yaml`:
   ```yaml
   # Строки 49-54
   SECRET_KEY: "ЗАМЕНИТЬ"
   POSTGRES_PASSWORD: "ЗАМЕНИТЬ"
   EMAIL_HOST_USER: "your-email@gmail.com"
   EMAIL_HOST_PASSWORD: "gmail-app-password"
   ```

2. **Сгенерировать новый SECRET_KEY:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Получить Gmail App Password:**
   - https://myaccount.google.com/security → Включить 2FA
   - https://myaccount.google.com/apppasswords → Создать "Pyland"
   - Скопировать 16-значный пароль

4. **Проверить ConfigMap** в `k8s/timeweb-deploy.yaml`:
   ```yaml
   DEBUG: "False"  # НЕ True!
   SITE_URL: "https://pyland.ru"  # https, не http!
   ```

---

## Деплой (одна команда!)

```bash
./deploy.sh
```

**Или вручную:**

```bash
# 1. Build
docker build --platform linux/amd64 -t ghcr.io/ps965xx7vn-lgtm/backend:production -f Dockerfile .

# 2. Push
docker push ghcr.io/ps965xx7vn-lgtm/backend:production

# 3. Deploy
export KUBECONFIG=~/.kube/timeweb-config
kubectl apply -f k8s/timeweb-deploy.yaml
kubectl apply -f k8s/ingress.yaml

# 4. Restart
kubectl rollout restart deployment/web deployment/celery-worker -n pyland

# 5. Wait
kubectl rollout status deployment/web -n pyland --timeout=120s
```

---

## После деплоя

### Проверить поды:
```bash
kubectl get pods -n pyland

# Ожидаем все Running:
# web, celery-worker, celery-beat, postgres, redis
```

### Проверить доступность:
```bash
# HTTP
curl -I https://pyland.ru/

# API
curl https://pyland.ru/api/health/

# Admin
open https://pyland.ru/admin/
```

### Создать суперюзера:
```bash
kubectl exec -it deployment/web -n pyland -- python manage.py createsuperuser
```

### Проверить email:
1. Зарегистрировать тестовый аккаунт
2. Проверить почту
3. Кликнуть на ссылку подтверждения
4. Убедиться что нет 404

---

## Если что-то не работает

**Поды не запускаются:**
```bash
kubectl describe pod <POD_NAME> -n pyland
kubectl logs <POD_NAME> -n pyland
```

**Email не отправляются:**
```bash
kubectl logs deployment/celery-worker -n pyland | grep -i email
```

**SSL не создается:**
```bash
kubectl get certificate -n pyland
kubectl logs -n cert-manager deployment/cert-manager
```

**Полный troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📚 Полная документация

- **[DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md)** - Подробный чеклист с командами
- **[K8S_DEPLOY_GUIDE.md](K8S_DEPLOY_GUIDE.md)** - Полное руководство
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Решение проблем
- **[EMAIL_SMTP_SETUP.md](EMAIL_SMTP_SETUP.md)** - Настройка email

---

## 🎯 Быстрая шпаргалка

| Что | Команда |
|-----|---------|
| Деплой | `./deploy.sh` |
| Проверка подов | `kubectl get pods -n pyland` |
| Логи web | `kubectl logs -f deployment/web -n pyland` |
| Логи celery | `kubectl logs -f deployment/celery-worker -n pyland` |
| Создать суперюзера | `kubectl exec -it deployment/web -n pyland -- python manage.py createsuperuser` |
| Бэкап БД | `kubectl exec deployment/postgres -n pyland -- pg_dump -U pyland_prod_user pyland_db > backup.sql` |
| Перезапуск | `kubectl rollout restart deployment/web -n pyland` |
| Откат | `kubectl rollout undo deployment/web -n pyland` |

---

**Удачного деплоя! 🚀**
