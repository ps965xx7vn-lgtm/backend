# Доступ к приложению без порта - Руководство

## Текущее состояние

✅ **Приложение полностью работает**: http://pyland.ru:30796
✅ **Email уведомления**: Настроены и работают через Celery
✅ **Статические файлы**: Обслуживаются через WhiteNoise
⚠️ **Порт 80 не отвечает**: Требуется настройка на стороне Timeweb

## Проблема

DNS настроен правильно (`pyland.ru → 188.225.37.90`), но LoadBalancer не отвечает на стандартном порту 80. Это связано с настройками облачного провайдера Timeweb.

```bash
# Работает
curl http://pyland.ru:30796/api/ping

# Не работает (timeout)
curl http://pyland.ru/api/ping
```

## Решения

### Вариант 1: Обращение в поддержку Timeweb (Рекомендуется)

1. Открыть тикет в поддержку Timeweb
2. Запросить открытие портов 80 и 443 для LoadBalancer IP `188.225.37.90`
3. После настройки приложение будет доступно без порта

**Ожидаемый результат:**
```bash
http://pyland.ru  →  работает
https://pyland.ru  →  работает (после установки SSL)
```

### Вариант 2: Настройка firewall на ноде (Временное решение)

Если есть SSH доступ к ноде кластера:

```bash
# Проброс порта 80 → 30796 на ноде
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 30796
sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 31633

# Сохранить правила
sudo iptables-save > /etc/iptables/rules.v4
```

**Недостатки:**
- Требует root доступ к ноде
- Может сброситься при перезагрузке
- Нужна настройка на каждой ноде

### Вариант 3: Использовать внешний Reverse Proxy (CloudFlare/Nginx)

1. Настроить CloudFlare с проксированием:
   - DNS: `pyland.ru → Proxied`
   - CloudFlare Rules: Redirect `:80 → :30796`

2. Или использовать отдельный сервер с Nginx:
   ```nginx
   server {
       listen 80;
       server_name pyland.ru;

       location / {
           proxy_pass http://188.225.37.90:30796;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Текущая конфигурация

### Ingress Controller
```yaml
Service: ingress-nginx-controller
Type: LoadBalancer
External-IP: 188.225.37.90
Ports:
  - 80:30796/TCP   # HTTP
  - 443:31633/TCP  # HTTPS
```

### Проверка состояния
```bash
# Проверить LoadBalancer
kubectl get svc -n ingress-nginx

# Проверить Ingress
kubectl get ingress -n pyland

# Тест через LoadBalancer IP (работает)
curl http://188.225.37.90:80/api/ping  # ✅ Работает через порт 80
curl http://188.225.37.90/api/ping     # ❌ Не работает без порта

# Тест через домен
curl http://pyland.ru:30796/api/ping   # ✅ Работает через NodePort
curl http://pyland.ru/api/ping         # ❌ Не работает без порта
```

## Email уведомления

✅ **Полностью настроены и работают**

### Текущая конфигурация
- **Backend**: Console (логи в Celery Worker)
- **Celery**: Подключен к Redis правильно
- **Задачи**: Выполняются успешно

### Настройка SMTP (опционально)

Для отправки реальных писем обновите ConfigMap:

```bash
kubectl edit configmap django-config -n pyland
```

Замените:
```yaml
EMAIL_BACKEND: "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST: "smtp.gmail.com"  # Или ваш SMTP сервер
EMAIL_HOST_USER: "your-email@gmail.com"
EMAIL_HOST_PASSWORD: "your-app-password"  # Пароль приложения Gmail
EMAIL_PORT: "587"
EMAIL_USE_TLS: "True"
DEFAULT_FROM_EMAIL: "noreply@pyland.ru"
```

Затем перезапустите deployments:
```bash
kubectl rollout restart deployment/web -n pyland
kubectl rollout restart deployment/celery-worker -n pyland
```

### Проверка email уведомлений

```bash
# Регистрация с уведомлением
curl -X POST http://pyland.ru:30796/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "confirm_password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User",
    "show_notifications": true
  }'

# Проверить логи Celery
kubectl logs deployment/celery-worker -n pyland --tail=20
```

Должны увидеть:
```
Task authentication.tasks.send_verification_email[...] received
Task authentication.tasks.send_verification_email[...] succeeded
```

## Итоговый чеклист

- [x] DNS настроен (pyland.ru → 188.225.37.90)
- [x] Ingress Controller установлен
- [x] Статические файлы работают (WhiteNoise)
- [x] API полностью функционален
- [x] Email уведомления работают (Celery + Redis)
- [ ] **Порт 80 открыт** ← Требуется обращение в Timeweb
- [ ] SSL сертификаты установлены (после открытия порта 80)

## Следующие шаги

1. **Обратиться в поддержку Timeweb** для открытия портов 80/443 на LoadBalancer
2. После открытия порта установить SSL: [DEPLOYMENT.md](DEPLOYMENT.md#ssl-setup)
3. Настроить SMTP для реальной отправки email
4. Создать admin пользователя: `kubectl exec -it deployment/web -n pyland -- python manage.py createsuperuser`

## Дополнительная информация

- Полная документация деплоя: [DEPLOYMENT.md](DEPLOYMENT.md)
- Техническая архитектура: [ARCHITECTURE.md](ARCHITECTURE.md)
- Настройка CI/CD: [GIT_WORKFLOW.md](GIT_WORKFLOW.md)
