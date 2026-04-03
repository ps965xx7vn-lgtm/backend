# AI Model Basics — Твоя умная модель! 🧠

## Что такое AI модель?

**AI модель** — это программа, которая учится на данных и делает предсказания.

### Простая аналогия:
```
Студент учится решать задачи:
  Примеры задач → Учёба → Решение новых задач

AI модель учится так же:
  Тренировочные данные → Обучение → Предсказания
```

**AI модель = ученик, который учится на примерах!** 🎓

---

## Компоненты AI модели

### 1. Датасет (Dataset)
**Тренировочные данные** для обучения модели.

```python
dataset = [
    {"input": "Отличный продукт!", "output": "positive"},
    {"input": "Ужасное качество", "output": "negative"},
    {"input": "Нормально, ничего особенного", "output": "neutral"}
]
```

### 2. Обучение (Training)
**Процесс, когда модель учится на данных.**

```python
model = AIModel()
model.train(dataset)  # Модель учится!
```

### 3. Предсказание (Prediction)
**Использование обученной модели.**

```python
prediction = model.predict("Классный товар!")
print(prediction)  # "positive"
```

---

## Ключевые метрики модели

### 1. Accuracy (Точность)
**Процент правильных ответов.**

```python
def calculate_accuracy(correct, total):
    """Точность = правильные / всего."""
    if total == 0:
        return 0
    return (correct / total) * 100

# Пример
correct = 85  # 85 правильных ответов
total = 100   # из 100 попыток
accuracy = calculate_accuracy(correct, total)
print(f"Точность: {accuracy}%")  # Точность: 85.0%
```

### 2. Loss (Ошибка)
**Насколько модель ошибается.**

```python
def calculate_loss(predictions, actuals):
    """Средняя ошибка."""
    if not predictions:
        return 0

    errors = [abs(pred - actual) for pred, actual in zip(predictions, actuals)]
    return sum(errors) / len(errors)

# Пример
predictions = [0.9, 0.7, 0.3, 0.8]  # Предсказания модели
actuals = [1.0, 0.5, 0.0, 1.0]      # Реальные значения
loss = calculate_loss(predictions, actuals)
print(f"Loss: {loss:.2f}")  # Loss: 0.15
```

### 3. Dataset Size (Размер датасета)
**Сколько примеров для обучения.**

```python
datasets = {
    "tiny": 100,        # Маленький
    "small": 1000,      # Малый
    "medium": 10000,    # Средний
    "large": 100000,    # Большой
    "huge": 1000000     # Огромный
}

# Чем больше данных, тем лучше модель!
```

---

## Жизненный цикл модели

### Этап 1: Сбор данных
```python
def collect_dataset(size):
    """Собрать тренировочные данные."""
    dataset = []
    for i in range(size):
        example = {
            "id": i + 1,
            "text": f"Пример текста {i}",
            "label": "positive" if i % 2 == 0 else "negative"
        }
        dataset.append(example)
    return dataset

dataset = collect_dataset(1000)
print(f"Собрано {len(dataset)} примеров")
```

### Этап 2: Обучение
```python
class SimpleAIModel:
    """Простая AI модель."""

    def __init__(self):
        self.dataset_size = 0
        self.accuracy = 0.5  # Начальная точность 50%
        self.loss = 0.5      # Начальная ошибка 50%
        self.is_trained = False

    def train(self, dataset):
        """Обучить модель."""
        self.dataset_size = len(dataset)

        # Точность растёт с данными (но не выше 99%)
        improvement = min(0.49, self.dataset_size / 10000)
        self.accuracy = 0.5 + improvement

        # Ошибка уменьшается
        self.loss = 0.5 - improvement

        self.is_trained = True
        print(f"✅ Модель обучена на {self.dataset_size} примерах")
        print(f"📊 Точность: {self.accuracy:.2%}")
        print(f"📉 Loss: {self.loss:.2f}")

    def predict(self, text):
        """Сделать предсказание."""
        if not self.is_trained:
            return "Модель не обучена!"

        # Простое предсказание (на самом деле сложнее!)
        if len(text) > 20:
            return "positive"
        else:
            return "negative"

# Использование
model = SimpleAIModel()
dataset = collect_dataset(5000)
model.train(dataset)
```

### Этап 3: Тестирование
```python
def test_model(model, test_data):
    """Проверить модель на тестовых данных."""
    correct = 0
    total = len(test_data)

    for example in test_data:
        prediction = model.predict(example["text"])
        if prediction == example["label"]:
            correct += 1

    accuracy = (correct / total) * 100
    print(f"Тестовая точность: {accuracy:.1f}%")
    return accuracy

# Тестовые данные
test_data = collect_dataset(100)
test_accuracy = test_model(model, test_data)
```

### Этап 4: Улучшение
```python
def improve_model(model, additional_data):
    """Дообучить модель на новых данных."""
    all_data = model.dataset_size + len(additional_data)
    improvement_dataset = collect_dataset(all_data)
    model.train(improvement_dataset)
    return model

# Дообучение
model = improve_model(model, collect_dataset(2000))
```

---

## Типы AI моделей

### 1. Classification (Классификация)
**Определить категорию.**

```python
model_classification = {
    "task": "Классификация",
    "examples": [
        "Спам или не спам?",
        "Позитивный или негативный отзыв?",
        "Кошка или собака на фото?"
    ],
    "output": "Категория (метка)"
}
```

### 2. Regression (Регрессия)
**Предсказать число.**

```python
model_regression = {
    "task": "Регрессия",
    "examples": [
        "Цена квартиры",
        "Продажи в следующем месяце",
        "Температура завтра"
    ],
    "output": "Число (значение)"
}
```

### 3. Generation (Генерация)
**Создать что-то новое.**

```python
model_generation = {
    "task": "Генерация",
    "examples": [
        "Сгенерировать текст",
        "Создать изображение",
        "Написать код"
    ],
    "output": "Новый контент"
}
```

---

## Метрики качества модели

### Confusion Matrix (Матрица ошибок)
```python
def confusion_matrix(predictions, actuals):
    """Подсчёт TP, TN, FP, FN."""
    tp = sum(1 for p, a in zip(predictions, actuals) if p == 1 and a == 1)
    tn = sum(1 for p, a in zip(predictions, actuals) if p == 0 and a == 0)
    fp = sum(1 for p, a in zip(predictions, actuals) if p == 1 and a == 0)
    fn = sum(1 for p, a in zip(predictions, actuals) if p == 0 and a == 1)

    return {
        "true_positive": tp,   # Правильно нашли
        "true_negative": tn,   # Правильно отклонили
        "false_positive": fp,  # Ложная тревога
        "false_negative": fn   # Пропустили
    }

# Пример
predictions = [1, 0, 1, 1, 0, 1, 0, 0]
actuals = [1, 0, 0, 1, 0, 1, 1, 0]

matrix = confusion_matrix(predictions, actuals)
print(matrix)
# {'true_positive': 3, 'true_negative': 3, 'false_positive': 1, 'false_negative': 1}
```

### Overfitting vs Underfitting
```python
class ModelFit:
    """Проверка переобучения."""

    @staticmethod
    def check_fit(train_accuracy, test_accuracy):
        """Определить тип fit."""
        if train_accuracy < 0.7 and test_accuracy < 0.7:
            return "❌ Underfitting — модель слабая"
        elif train_accuracy > 0.9 and test_accuracy < 0.7:
            return "⚠️ Overfitting — модель запомнила данные"
        else:
            return "✅ Good Fit — модель работает хорошо"

# Примеры
print(ModelFit.check_fit(0.95, 0.60))  # Overfitting
print(ModelFit.check_fit(0.65, 0.63))  # Underfitting
print(ModelFit.check_fit(0.88, 0.85))  # Good Fit
```

---

## Практический пример: модель для стартапа

```python
class TextClassifier:
    """AI модель для классификации текстов."""

    def __init__(self, name):
        self.name = name
        self.accuracy = 0.5
        self.loss = 0.5
        self.dataset_size = 0
        self.predictions_made = 0

    def train(self, dataset):
        """Обучить на датасете."""
        self.dataset_size = len(dataset)

        # Качество улучшается с размером датасета
        if self.dataset_size < 1000:
            self.accuracy = 0.65
            self.loss = 0.35
        elif self.dataset_size < 5000:
            self.accuracy = 0.80
            self.loss = 0.20
        elif self.dataset_size < 10000:
            self.accuracy = 0.90
            self.loss = 0.10
        else:
            self.accuracy = 0.95
            self.loss = 0.05

        print(f"🎓 {self.name} обучена!")
        print(f"📊 Датасет: {self.dataset_size} примеров")
        print(f"✅ Точность: {self.accuracy:.2%}")
        print(f"📉 Loss: {self.loss:.2f}")

    def predict(self, text):
        """Классифицировать текст."""
        self.predictions_made += 1

        # Упрощённая логика
        positive_words = ["отлично", "хорошо", "супер", "класс", "круто"]
        negative_words = ["плохо", "ужасно", "отвратительно", "провал"]

        text_lower = text.lower()

        if any(word in text_lower for word in positive_words):
            return "positive"
        elif any(word in text_lower for word in negative_words):
            return "negative"
        else:
            return "neutral"

    def get_stats(self):
        """Статистика модели."""
        return {
            "model": self.name,
            "accuracy": f"{self.accuracy:.2%}",
            "dataset_size": self.dataset_size,
            "predictions": self.predictions_made
        }

# Создать и обучить модель
model = TextClassifier("SentimentAI v1.0")
dataset = collect_dataset(7500)
model.train(dataset)

# Использовать модель
reviews = [
    "Отлично работает!",
    "Ужасный продукт",
    "Нормально, ничего особенного"
]

for review in reviews:
    sentiment = model.predict(review)
    print(f"'{review}' → {sentiment}")

# Статистика
print("\n📊 Статистика модели:")
print(model.get_stats())
```

---

## Улучшение модели

### Способы повысить качество:

**1. Добавить данных**
```python
def add_more_data(model, additional_size):
    """Дообучить на новых данных."""
    new_data = collect_dataset(additional_size)
    total_data = model.dataset_size + len(new_data)
    all_data = collect_dataset(total_data)
    model.train(all_data)
    return model
```

**2. Улучшить качество данных**
```python
def clean_dataset(dataset):
    """Очистить датасет от плохих примеров."""
    # Убрать дубликаты
    unique = {d["text"]: d for d in dataset}.values()

    # Убрать короткие примеры
    quality = [d for d in unique if len(d["text"]) > 10]

    return list(quality)
```

**3. Настроить параметры**
```python
model_config = {
    "learning_rate": 0.001,      # Скорость обучения
    "batch_size": 32,            # Размер батча
    "epochs": 10,                # Количество эпох
    "dropout": 0.2               # Регуляризация
}
```

---

## Частые ошибки

### ❌ Ошибка 1: Мало данных
```python
# ПЛОХО
tiny_dataset = collect_dataset(50)  # Слишком мало!
model.train(tiny_dataset)  # Точность будет низкой

# ✅ ХОРОШО
good_dataset = collect_dataset(5000)  # Достаточно
model.train(good_dataset)
```

### ❌ Ошибка 2: Не тестируем модель
```python
# ПЛОХО
model.train(dataset)
# Используем сразу, не проверив!

# ✅ ХОРОШО
model.train(dataset)
test_accuracy = test_model(model, test_data)
if test_accuracy > 80:
    deploy_model(model)
```

### ❌ Ошибка 3: Переобучение
```python
# ПЛОХО: обучаем слишком долго
model.train(dataset, epochs=1000)  # Overfitting!

# ✅ ХОРОШО: контролируем
model.train(dataset, epochs=10)
if train_acc - test_acc > 0.15:
    print("⚠️ Overfitting detected!")
```

---

## Резюме

### AI модель — это:
- 🧠 **Программа**, которая учится
- 📚 **Датасет** — тренировочные данные
- 🎓 **Обучение** — процесс learning
- 📊 **Метрики** — accuracy, loss
- 🔮 **Предсказания** — использование

### Ключевые метрики:
```python
model_metrics = {
    "accuracy": 0.88,       # Точность 88%
    "loss": 0.12,           # Ошибка 12%
    "dataset_size": 10000,  # 10К примеров
    "predictions": 5000     # 5К предсказаний
}
```

### Жизненный цикл:
```
Сбор данных → Обучение → Тестирование → Улучшение → Деплой
```

---

## Что дальше?

Теперь ты знаешь основы AI моделей! 🎉

**Следующие темы:**
- Метрики моделей — precision, recall, F1-score
- Типы моделей — классификация, регрессия, генерация
- Обучение моделей — оптимизация, регуляризация

Создай свою AI модель и покори рынок! 🤖💡
