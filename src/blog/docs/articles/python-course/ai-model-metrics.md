# AI Model Metrics — Измерь успех! 📊

## Зачем нужны метрики?

**Метрики** — это способ измерить, насколько хорошо работает AI модель.

### Простая аналогия:
```
Студент сдаёт экзамен:
  Оценка = метрика успеха

AI модель делает предсказания:
  Accuracy, Precision, Recall = метрики качества
```

**Без метрик не понять, работает ли модель!** 📈

---

## Базовые метрики

### 1. Accuracy (Точность)
**Процент правильных ответов из всех.**

```python
def calculate_accuracy(correct, total):
    """Accuracy = правильные / все."""
    if total == 0:
        return 0
    return (correct / total) * 100

# Пример
correct = 85  # 85 правильных
total = 100   # из 100 всего
accuracy = calculate_accuracy(correct, total)
print(f"Accuracy: {accuracy}%")  # 85%
```

**Когда использовать:**
- ✅ Классы сбалансированы (50/50)
- ❌ Классы несбалансированы (95/5)

---

## Confusion Matrix (Матрица ошибок)

### Основа всех метрик!

```
Реальность
          Positive  Negative
Модель
Positive    TP        FP       (True/False Positive)
Negative    FN        TN       (False/True Negative)
```

- **TP (True Positive)** — правильно нашли положительные
- **TN (True Negative)** — правильно нашли отрицательные
- **FP (False Positive)** — ложная тревога
- **FN (False Negative)** — пропустили положительные

### Пример: детектор спама
```python
def create_confusion_matrix(predictions, actuals):
    """Создать матрицу ошибок."""
    tp = sum(1 for p, a in zip(predictions, actuals)
             if p == 'spam' and a == 'spam')
    tn = sum(1 for p, a in zip(predictions, actuals)
             if p == 'not_spam' and a == 'not_spam')
    fp = sum(1 for p, a in zip(predictions, actuals)
             if p == 'spam' and a == 'not_spam')
    fn = sum(1 for p, a in zip(predictions, actuals)
             if p == 'not_spam' and a == 'spam')

    return {
        "TP": tp,  # Спам определён правильно
        "TN": tn,  # Не спам определён правильно
        "FP": fp,  # Нормальное письмо посчитали спамом
        "FN": fn   # Спам пропустили
    }

# Тест
predictions = ['spam', 'not_spam', 'spam', 'spam', 'not_spam']
actuals = ['spam', 'not_spam', 'not_spam', 'spam', 'not_spam']

matrix = create_confusion_matrix(predictions, actuals)
print(matrix)
# {'TP': 2, 'TN': 2, 'FP': 1, 'FN': 0}
```

---

## Precision (Точность предсказаний)

**Из всех "положительных" предсказаний, сколько правильных?**

```python
def calculate_precision(tp, fp):
    """Precision = TP / (TP + FP)."""
    if tp + fp == 0:
        return 0
    return tp / (tp + fp)

# Пример
tp = 80  # 80 правильно найденных спамов
fp = 20  # 20 нормальных писем назвали спамом

precision = calculate_precision(tp, fp)
print(f"Precision: {precision:.2%}")  # 80%
```

### Когда важна Precision?
- 🚨 **Медицинская диагностика** — нельзя ставить ложный диагноз
- 📧 **Спам-фильтр** — важно не удалить нормальные письма
- ⚖️ **Юридические решения** — ложное обвинение дорого

**Precision отвечает:** Можем ли мы доверять положительным предсказаниям?

---

## Recall (Полнота)

**Из всех реальных "положительных", сколько нашли?**

```python
def calculate_recall(tp, fn):
    """Recall = TP / (TP + FN)."""
    if tp + fn == 0:
        return 0
    return tp / (tp + fn)

# Пример
tp = 80  # 80 спамов найдено
fn = 20  # 20 спамов пропущено

recall = calculate_recall(tp, fn)
print(f"Recall: {recall:.2%}")  # 80%
```

### Когда важна Recall?
- 🔍 **Поиск болезней** — нельзя пропустить заболевание
- 🛡️ **Детекция мошенничества** — важно поймать все случаи
- 🔐 **Безопасность** — лучше лишний раз проверить

**Recall отвечает:** Находим ли мы все положительные случаи?

---

## Precision vs Recall

### Компромисс (Trade-off)
```python
def demonstrate_tradeoff():
    """Показать компромисс Precision/Recall."""

    # Строгая модель (мало FP, но много FN)
    strict_model = {
        "TP": 60, "FP": 5, "FN": 40, "TN": 95,
        "precision": 0.92,  # Высокая!
        "recall": 0.60      # Низкая!
    }

    # Мягкая модель (мало FN, но много FP)
    lenient_model = {
        "TP": 95, "FP": 30, "FN": 5, "TN": 70,
        "precision": 0.76,  # Низкая!
        "recall": 0.95      # Высокая!
    }

    return strict_model, lenient_model

strict, lenient = demonstrate_tradeoff()

print("Строгая модель:")
print(f"  Precision: {strict['precision']:.2%}")
print(f"  Recall: {strict['recall']:.2%}")

print("\nМягкая модель:")
print(f"  Precision: {lenient['precision']:.2%}")
print(f"  Recall: {lenient['recall']:.2%}")
```

**Нельзя одновременно максимизировать оба!**

---

## F1-Score (Гармоническое среднее)

**Баланс между Precision и Recall.**

```python
def calculate_f1_score(precision, recall):
    """F1 = 2 * (Precision * Recall) / (Precision + Recall)."""
    if precision + recall == 0:
        return 0
    return 2 * (precision * recall) / (precision + recall)

# Пример
precision = 0.80  # 80%
recall = 0.75     # 75%

f1 = calculate_f1_score(precision, recall)
print(f"F1-Score: {f1:.2%}")  # 77.42%
```

### Когда использовать F1?
- ✅ Нужен баланс Precision и Recall
- ✅ Классы несбалансированы
- ✅ Оба типа ошибок (FP и FN) важны

**F1 = 1** — идеально (Precision = Recall = 100%)
**F1 = 0** — модель ничего не находит

---

## Полный пример: оценка модели

```python
class ModelEvaluator:
    """Класс для оценки AI модели."""

    def __init__(self):
        self.tp = 0
        self.tn = 0
        self.fp = 0
        self.fn = 0

    def evaluate(self, predictions, actuals):
        """Оценить предсказания."""
        for pred, actual in zip(predictions, actuals):
            if pred == 1 and actual == 1:
                self.tp += 1
            elif pred == 0 and actual == 0:
                self.tn += 1
            elif pred == 1 and actual == 0:
                self.fp += 1
            else:  # pred == 0 and actual == 1
                self.fn += 1

    def get_accuracy(self):
        """Точность."""
        total = self.tp + self.tn + self.fp + self.fn
        if total == 0:
            return 0
        return (self.tp + self.tn) / total

    def get_precision(self):
        """Precision."""
        if self.tp + self.fp == 0:
            return 0
        return self.tp / (self.tp + self.fp)

    def get_recall(self):
        """Recall."""
        if self.tp + self.fn == 0:
            return 0
        return self.tp / (self.tp + self.fn)

    def get_f1_score(self):
        """F1-Score."""
        precision = self.get_precision()
        recall = self.get_recall()

        if precision + recall == 0:
            return 0
        return 2 * (precision * recall) / (precision + recall)

    def get_report(self):
        """Полный отчёт."""
        return {
            "confusion_matrix": {
                "TP": self.tp,
                "TN": self.tn,
                "FP": self.fp,
                "FN": self.fn
            },
            "metrics": {
                "accuracy": f"{self.get_accuracy():.2%}",
                "precision": f"{self.get_precision():.2%}",
                "recall": f"{self.get_recall():.2%}",
                "f1_score": f"{self.get_f1_score():.2%}"
            }
        }

# Использование
evaluator = ModelEvaluator()

# Тестовые данные
predictions = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1]
actuals = [1, 0, 0, 1, 0, 1, 1, 0, 1, 0]

evaluator.evaluate(predictions, actuals)

# Отчёт
report = evaluator.get_report()
print("📊 Отчёт модели:")
print(f"\nМатрица ошибок:")
for key, value in report["confusion_matrix"].items():
    print(f"  {key}: {value}")

print(f"\nМетрики:")
for key, value in report["metrics"].items():
    print(f"  {key}: {value}")
```

---

## Дополнительные метрики

### Specificity (Специфичность)
**Из всех отрицательных, сколько правильно определили?**

```python
def calculate_specificity(tn, fp):
    """Specificity = TN / (TN + FP)."""
    if tn + fp == 0:
        return 0
    return tn / (tn + fp)

# Пример: не спам определён правильно
tn = 90  # 90 нормальных писем правильно
fp = 10  # 10 нормальных назвали спамом

specificity = calculate_specificity(tn, fp)
print(f"Specificity: {specificity:.2%}")  # 90%
```

### ROC AUC (Площадь под кривой)
```python
def calculate_roc_auc_simple(tpr, fpr):
    """Упрощённая AUC (обычно сложнее)."""
    # True Positive Rate vs False Positive Rate
    auc = (1 - fpr + tpr) / 2
    return auc

tpr = 0.85  # True Positive Rate (Recall)
fpr = 0.10  # False Positive Rate

auc = calculate_roc_auc_simple(tpr, fpr)
print(f"AUC: {auc:.2%}")  # ~87.5%
```

**AUC = 1.0** — идеальная модель
**AUC = 0.5** — случайное угадывание

---

## Выбор метрики для задачи

### Таблица выбора:

| Задача | Главная метрика | Почему |
|--------|----------------|--------|
| Спам-фильтр | Precision | Не удалять нормальные письма |
| Детекция болезней | Recall | Не пропустить заболевание |
| Рекомендации товаров | F1-Score | Баланс точности и полноты |
| Распознавание лиц | Accuracy | Классы сбалансированы |
| Детекция мошенничества | Recall | Поймать все случаи |

### Код для выбора метрики:
```python
def recommend_metric(task_type):
    """Рекомендовать метрику для задачи."""
    recommendations = {
        "spam_filter": {
            "primary": "Precision",
            "reason": "Нельзя удалять нормальные письма"
        },
        "disease_detection": {
            "primary": "Recall",
            "reason": "Нельзя пропустить болезнь"
        },
        "fraud_detection": {
            "primary": "Recall",
            "reason": "Поймать все случаи мошенничества"
        },
        "balanced_classification": {
            "primary": "F1-Score",
            "reason": "Баланс Precision и Recall"
        }
    }

    return recommendations.get(task_type, {"primary": "Accuracy", "reason": "По умолчанию"})

# Примеры
print(recommend_metric("spam_filter"))
print(recommend_metric("disease_detection"))
```

---

## Улучшение метрик

### Способы повысить качество:

**1. Больше данных**
```python
def improve_with_data(current_f1, data_increase_percent):
    """Улучшение с добавлением данных."""
    # Упрощённая формула
    improvement = data_increase_percent * 0.001
    new_f1 = min(0.99, current_f1 + improvement)
    return new_f1

f1 = 0.75
new_f1 = improve_with_data(f1, 50)  # +50% данных
print(f"F1: {f1:.2%} → {new_f1:.2%}")
```

**2. Балансировка классов**
```python
def balance_classes(dataset):
    """Уравнять количество классов."""
    positive = [d for d in dataset if d["label"] == 1]
    negative = [d for d in dataset if d["label"] == 0]

    # Использовать меньший класс
    min_size = min(len(positive), len(negative))

    balanced = positive[:min_size] + negative[:min_size]
    return balanced
```

**3. Настройка порога (threshold)**
```python
def adjust_threshold(scores, actuals, target_precision=0.90):
    """Найти порог для целевой precision."""
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    for threshold in thresholds:
        predictions = [1 if score >= threshold else 0 for score in scores]

        tp = sum(1 for p, a in zip(predictions, actuals) if p == 1 and a == 1)
        fp = sum(1 for p, a in zip(predictions, actuals) if p == 1 and a == 0)

        precision = tp / (tp + fp) if tp + fp > 0 else 0

        if precision >= target_precision:
            return threshold

    return 0.5  # По умолчанию

# Пример
scores = [0.9, 0.7, 0.4, 0.8, 0.3]
actuals = [1, 1, 0, 1, 0]
best_threshold = adjust_threshold(scores, actuals, target_precision=0.9)
print(f"Лучший порог: {best_threshold}")
```

---

## Частые ошибки

### ❌ Ошибка 1: Использовать только Accuracy
```python
# ПЛОХО: несбалансированные классы (95% negative, 5% positive)
# Модель говорит "всё negative" → Accuracy = 95%!
# Но Recall = 0% (не нашла ни одного positive)

# ✅ ХОРОШО: смотрим F1-Score
evaluator = ModelEvaluator()
# ... оценка ...
print(f"F1-Score: {evaluator.get_f1_score():.2%}")
```

### ❌ Ошибка 2: Игнорировать контекст
```python
# ПЛОХО: одинаковая метрика для всех задач
all_tasks_use_accuracy()

# ✅ ХОРОШО: метрика зависит от задачи
if task == "medical":
    use_recall()  # Recall важна!
elif task == "spam":
    use_precision()  # Precision важна!
```

### ❌ Ошибка 3: Не тестировать на новых данных
```python
# ПЛОХО: тестируем на тренировочных данных
train_model(train_data)
test_on_same_data(train_data)  # Переобучение!

# ✅ ХОРОШО: отдельный тест
train_model(train_data)
test_on_new_data(test_data)  # Честная оценка
```

---

## Резюме

### Основные метрики:
```python
metrics = {
    "Accuracy": "Всё правильно / всё",
    "Precision": "TP / (TP + FP)",
    "Recall": "TP / (TP + FN)",
    "F1-Score": "2 * P * R / (P + R)"
}
```

### Confusion Matrix:
```
         Predicted
         Pos   Neg
Actual
Pos      TP    FN
Neg      FP    TN
```

### Когда использовать:
- **Accuracy** — классы сбалансированы
- **Precision** — важно избежать FP (ложная тревога)
- **Recall** — важно избежать FN (пропуски)
- **F1-Score** — баланс Precision и Recall

---

## Что дальше?

Теперь ты знаешь метрики AI моделей! 🎉

**Следующие темы:**
- Монетизация — API pricing, подписки
- Инвестиции — раунды финансирования
- Конкуренция — анализ рынка

Создай модель с высоким F1-Score! 📊🚀
