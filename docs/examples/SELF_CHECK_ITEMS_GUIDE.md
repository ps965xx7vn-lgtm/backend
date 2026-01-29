# Инструкция по использованию чекбоксов самопроверки

## Что изменилось

1. **Добавлено поле `self_check_items` в Step модель**
   - Тип: `JSONField` (список строк)
   - Содержит массив строк для отображения чекбоксов
   - Nullable: может быть пустым или null

2. **Обновлена API схема `StepOut`**
   - Добавлено поле `self_check_items: list[str] | None`
   - API теперь возвращает массив чекбоксов для каждого шага

3. **Удалено поле `repair_description` из курсов**
   - Это админ-поле для платформы, не для студентов
   - Не должно показываться в интерфейсе прохождения курса

## Структура данных API

### GET /api/courses/steps/{id}

```json
{
  "id": "uuid",
  "name": "Название шага",
  "step_number": 1,
  "description": "Описание шага...",
  "actions": "Инструкции что делать...",
  "self_check": "Текстовая проверка (старый формат)",
  "self_check_items": [
    "Первый пункт для проверки",
    "Второй пункт для проверки",
    "Третий пункт для проверки"
  ],
  "submission_field": "github_repo_url"
}
```

## Логика работы на фронтенде

### 1. Отображение чекбоксов

```tsx
// Пример React компонента
interface Step {
  id: string;
  name: string;
  self_check_items?: string[];
  // ... другие поля
}

function StepSelfCheck({ step }: { step: Step }) {
  const [checkedItems, setCheckedItems] = useState<boolean[]>(
    step.self_check_items?.map(() => false) || []
  );

  if (!step.self_check_items || step.self_check_items.length === 0) {
    return null; // Нет чекбоксов для этого шага
  }

  const allChecked = checkedItems.every(item => item);

  const handleCheck = (index: number) => {
    const newChecked = [...checkedItems];
    newChecked[index] = !newChecked[index];
    setCheckedItems(newChecked);
  };

  return (
    <div className="self-check-section">
      <h3>Самопроверка</h3>
      {step.self_check_items.map((item, index) => (
        <label key={index}>
          <input
            type="checkbox"
            checked={checkedItems[index]}
            onChange={() => handleCheck(index)}
          />
          {item}
        </label>
      ))}

      {allChecked && (
        <button onClick={handleNextStep}>
          Следующий шаг →
        </button>
      )}
    </div>
  );
}
```

### 2. Кнопка "Следующий шаг"

**Правила отображения:**
- Кнопка появляется ТОЛЬКО когда все чекбоксы отмечены
- При клике на кнопку:
  1. Отметить текущий шаг как пройденный (API запрос)
  2. Перейти к следующему шагу
  3. Обновить прогресс урока

```tsx
const handleNextStep = async () => {
  try {
    // 1. Отметить шаг как пройденный
    await fetch(`/api/courses/steps/${step.id}/complete`, {
      method: 'POST',
    });

    // 2. Перейти к следующему шагу
    navigate(`/courses/steps/${nextStepId}`);
  } catch (error) {
    console.error('Error completing step:', error);
  }
};
```

### 3. Сохранение состояния чекбоксов

**Важно:** Чекбоксы должны сохраняться в localStorage или backend:

```tsx
// Сохранение в localStorage
useEffect(() => {
  const key = `step-${step.id}-checkboxes`;
  localStorage.setItem(key, JSON.stringify(checkedItems));
}, [checkedItems, step.id]);

// Загрузка при монтировании
useEffect(() => {
  const key = `step-${step.id}-checkboxes`;
  const saved = localStorage.getItem(key);
  if (saved) {
    setCheckedItems(JSON.parse(saved));
  }
}, [step.id]);
```

## Примеры из курса Git

### Шаг 2: Установка Git
```json
"self_check_items": [
  "Зайди на github.com/твой-username - видишь свою страницу",
  "Есть фото и имя",
  "Email подтверждён (зелёная галочка в настройках)"
]
```

### Шаг 18: Публикация сайта
```json
"self_check_items": [
  "Контакты добавлены локально",
  "Коммит создан и отправлен",
  "На сайте появились контакты",
  "Сайт работает на GitHub Pages"
]
```

### Шаг 19: Финальная проверка
```json
"self_check_items": [
  "Мой сайт работает по ссылке username.github.io/my-portfolio",
  "На GitHub видны все 6 коммитов",
  "Репозиторий публичный (Public)",
  "Я скопировал ссылку на репозиторий",
  "Готов отправить на проверку"
]
```

## UI/UX рекомендации

1. **Визуальное отличие:**
   - Невыполненные чекбоксы: серый цвет
   - Выполненные: зелёная галочка
   - Все выполнены: показать кнопку с анимацией

2. **Прогресс:**
   - Показывать счётчик: "3 из 5 выполнено"
   - Прогресс-бар заполнения чекбоксов

3. **Кнопка "Следующий шаг":**
   - Большая, заметная
   - Зелёный цвет
   - Анимация появления когда все галочки стоят

4. **Валидация:**
   - Если пользователь пытается перейти дальше без галочек - предупреждение
   - "Проверьте все пункты перед переходом к следующему шагу"

## Backend endpoint для завершения шага

**TODO:** Нужно добавить API endpoint:

```python
# courses/api.py
@router.post("/steps/{step_id}/complete")
def complete_step(request, step_id: UUID):
    """Отметить шаг как пройденный."""
    # Логика сохранения прогресса пользователя
    pass
```

## Совместимость со старыми курсами

- Если `self_check_items` пустой или null → показываем старое текстовое поле `self_check`
- Новые курсы используют только `self_check_items`
- Поле `repair_description` не показывается студентам (только админам)
