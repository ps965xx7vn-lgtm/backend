# Как просто работать с HTTP-запросами в Python: библиотека Requests
Работать с интернетом на `Python`? Легко! Для этого есть удобная библиотека `Requests`, которая позволяет отправлять запросы на веб-сайты и получать ответы. Она делает работу с `HTTP-запросами` простой и понятной, даже если вы только начинаете программировать.

Давайте разберемся на примерах, как пользоваться этой библиотекой!

## Что такое HTTP-запросы?
Когда вы открываете веб-страницу, ваш браузер отправляет запрос на сервер, и тот возвращает ответ (например, `HTML-код`). В `Python` мы можем сделать то же самое с помощью библиотеки `Requests`.

## Как отправить GET-запрос?
Допустим, вы хотите получить данные с веб-сайта. Для этого используется метод `requests.get()`.

```python
import requests

url = 'https://jsonplaceholder.typicode.com/posts'  # Фейковый API для тестов
response = requests.get(url)

# Проверяем, успешно ли прошёл запрос
response.raise_for_status()

print(response.text)  # Выводим текст ответа
```

Этот код отправляет запрос и получает данные (например, список постов). Если всё прошло хорошо, ответ можно вывести или обработать.

## Как отправить POST-запрос?
`POST-запрос` используется, когда вы хотите отправить данные на сервер. Например, чтобы создать новый пост или добавить пользователя.

```python
import requests

url = 'https://jsonplaceholder.typicode.com/posts'
data = {
    'title': 'Новый пост',
    'body': 'Содержимое поста',
    'userId': 1
}

response = requests.post(url, json=data)
response.raise_for_status()

print(response.json())  # Получаем ответ в формате JSON
```
Этот запрос отправляет данные на сервер и возвращает ответ с созданным ресурсом.

## Как передать параметры в URL?
Иногда данные передаются прямо через `URL`. Например, чтобы получить посты конкретного пользователя.

```python
import requests

url = 'https://jsonplaceholder.typicode.com/posts'
params = {'userId': 1}  # Параметр запроса

response = requests.get(url, params=params)
response.raise_for_status()

print(response.json())  # Получаем посты пользователя с ID = 1
```
Здесь мы добавили параметр `userId`, чтобы сервер вернул только посты этого пользователя.

## Как добавить заголовки к запросу?
Иногда нужно передать серверу дополнительную информацию, например, указать, какой у вас клиент (браузер) или передать токен доступа.

```python
import requests

url = 'https://jsonplaceholder.typicode.com/posts'
headers = {'User-Agent': 'my-app'}

response = requests.get(url, headers=headers)
response.raise_for_status()
```

## Как обрабатывать разные типы данных?
Ответы от сервера могут быть разными: текст, `JSON` или даже изображения. В `Requests` есть удобные методы для обработки всех этих форматов:

- `response.text` — текст (например, `HTML` или текстовый файл).
- `response.json()` — `JSON-данные`.
- `response.content` — бинарные данные (например, картинки).

```python
import requests

url = 'https://jsonplaceholder.typicode.com/posts/1'
response = requests.get(url)
response.raise_for_status()

data = response.json()  # Преобразуем ответ в словарь
print(data)
```
