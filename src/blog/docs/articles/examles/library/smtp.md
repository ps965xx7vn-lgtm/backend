# Работа с SMTP в Python
`SMTP (Simple Mail Transfer Protocol)` — это стандарт для отправки электронной почты через интернет. `Python` предоставляет простые инструменты для отправки писем через этот протокол, используя библиотеку `smtplib`.

## 📌 Что вам понадобится:
Аккаунт на почтовом сервисе (например, `Gmail` или `Яндекс.Почта`).
Библиотека `smtplib` — она встроена в `Python`.
Адрес `SMTP-сервера` вашего почтового провайдера.
## 🚀 Шаги для отправки письма через Python:
### 1. Импортируем библиотеку и настраиваем сервер:

```python
import smtplib
from email.mime.text import MIMEText

# Настройки вашего SMTP-сервера (для Gmail)
smtp_server = "smtp.gmail.com"
port = 587
```
### 2. Создаём текст письма:

```python
# Создаем текстовое сообщение
message = MIMEText("Привет! Это тестовое письмо, отправленное через Python.", "plain", "utf-8")
message["Subject"] = "Тестовое письмо"
message["From"] = "your_email@gmail.com"
message["To"] = "recipient_email@example.com"
```
### 3. Подключаемся к серверу и отправляем письмо:

```python
# Вводим данные для авторизации
login = "your_email@gmail.com"
password = "your_password"

# Подключаемся к SMTP-серверу и отправляем письмо
with smtplib.SMTP(smtp_server, port) as server:
    server.starttls()  # Шифруем соединение
    server.login(login, password)  # Входим на сервер
    server.sendmail(login, "recipient_email@example.com", message.as_string())
```
## 🔧 Полезные советы:
Безопасность: Лучше использовать `App Passwords` или `OAuth2`, чем хранить свой основной пароль.
Отладка: Включите отладочный вывод для поиска ошибок:
```python
server.set_debuglevel(1)
```
## 🎯 Задание для вас:
Отправьте тестовое письмо самому себе! Попробуйте изменить тему или добавить `HTML-разметку` в тело письма.

Этот урок — ваш первый шаг к созданию автоматических рассылок или уведомлений для ваших проектов! 🚀
