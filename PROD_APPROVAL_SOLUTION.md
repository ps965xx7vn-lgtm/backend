# Решение проблемы Prod Approval для Solo-Dev

## Текущая проблема

```
❌ enforce_admins: true → блокирует даже admin bypass
❌ required_approving_review_count: 1 → нужен approval
❌ GitHub не позволяет self-approve свои PR
```

**Результат:** PR блокируется, merge невозможен даже с admin правами

---

## ✅ Решение 1: Admin Bypass (РЕКОМЕНДУЕТСЯ)

### Суть:
- Отключить `enforce_admins` → admin может bypass protection
- Оставить `required_approving_review_count: 1` → защита от случайных merge
- Workflow: PR → Checks → Admin merge (без approval)

### Настройки:
```bash
# 1. Отключить enforce_admins (разрешить admin bypass)
gh api -X DELETE repos/:owner/:repo/branches/prod/protection/enforce_admins

# 2. Проверить что остальное на месте
gh api repos/:owner/:repo/branches/prod/protection --jq '{
  enforce_admins: .enforce_admins.enabled,
  required_reviews: .required_pull_request_reviews.required_approving_review_count,
  required_checks: [.required_status_checks.checks[].context]
}'
```

### Workflow для merge в prod:
```bash
# Шаг 1: Создать PR (main → prod)
gh pr create --base prod --head main --title "release: v1.0" --body "Production release"

# Шаг 2: Дождаться всех checks
gh pr checks --watch

# Шаг 3: Merge с admin правами (bypass approval requirement)
gh pr merge --admin --squash

# Или через Web UI: Merge → Squash and merge (admin bypass badge появится)
```

### Плюсы:
- ✅ Solo-dev friendly (можешь merge сам)
- ✅ Защита осталась (требуется сознательный admin merge)
- ✅ Required checks работают (test, security, code-quality)
- ✅ Audit trail сохраняется (видно что был admin bypass)

### Минусы:
- ⚠️ Меньше строгости (admin может bypass все)
- ⚠️ Нет второй пары глаз (но для solo-dev это норма)

---

## ✅ Решение 2: Убрать Approval Requirement

### Суть:
- Убрать требование approval вообще
- Полагаться только на required checks
- Самый простой подход для solo-dev

### Настройки:
```bash
# Вариант A: Убрать approval requirement полностью
gh api -X DELETE repos/:owner/:repo/branches/prod/protection/required_pull_request_reviews

# Вариант B: Оставить настройки, но с 0 approvals
gh api -X PATCH repos/:owner/:repo/branches/prod/protection/required_pull_request_reviews \
  -F required_approving_review_count=0 \
  -F dismiss_stale_reviews=false
```

### Workflow для merge в prod:
```bash
# Шаг 1: Создать PR
gh pr create --base prod --head main --title "release: v1.0"

# Шаг 2: Дождаться checks
gh pr checks --watch

# Шаг 3: Обычный merge (no admin needed)
gh pr merge --squash
```

### Плюсы:
- ✅ Максимально просто
- ✅ Не нужен admin bypass
- ✅ Required checks все равно работают
- ✅ Быстрый deployment

### Минусы:
- ❌ Меньше защиты (любой с write access может merge)
- ❌ Нет "паузы для раздумий"
- ❌ Меньше формальности для prod

---

## ✅ Решение 3: Второй Аккаунт (НЕ РЕКОМЕНДУЕТСЯ)

### Суть:
- Создать технический аккаунт (bot/secondary)
- Использовать его для approvals
- Сложно и избыточно для solo-dev

### Настройки:
```bash
# 1. Создать GitHub аккаунт (bot)
# 2. Добавить в collaborators с write access
gh api repos/:owner/:repo/collaborators/bot-account -X PUT

# 3. Настроить GH CLI для bot аккаунта
gh auth login --with-token < bot-token.txt
```

### Workflow:
```bash
# Terminal 1 (основной аккаунт)
gh pr create --base prod --head main

# Terminal 2 (bot аккаунт)
gh pr review 6 --approve

# Terminal 1 (основной)
gh pr merge --squash
```

### Плюсы:
- ✅ Максимальная строгость
- ✅ Формально корректный workflow

### Минусы:
- ❌ Сложность и overhead
- ❌ Нужно два аккаунта
- ❌ Избыточно для solo-dev

---

## 🎯 Итоговая рекомендация

### Для solo-dev проекта:

**Вариант 1** (если хочешь сохранить формальность):
```bash
# Production settings
enforce_admins: false
required_approving_review_count: 1
require_last_push_approval: false
required_checks: [test, security, code-quality]

# Merge workflow
gh pr merge --admin --squash
```

**Вариант 2** (если нужна скорость и простота):
```bash
# Production settings
enforce_admins: true (optional)
required_approving_review_count: 0  ← убрать approval
required_checks: [test, security, code-quality]

# Merge workflow
gh pr merge --squash
```

---

## 🚀 Применить рекомендованное решение

### Вариант 1 (Admin Bypass):
```bash
# Применить настройки
gh api -X DELETE repos/:owner/:repo/branches/prod/protection/enforce_admins

# Проверить
gh api repos/:owner/:repo/branches/prod/protection --jq '.enforce_admins.enabled'
# Должно быть: false

# Теперь можно merge
gh pr merge 6 --admin --squash
```

### Вариант 2 (No Approval):
```bash
# Применить настройки
gh api -X PATCH repos/:owner/:repo/branches/prod/protection/required_pull_request_reviews \
  -F required_approving_review_count=0

# Или удалить requirement полностью
gh api -X DELETE repos/:owner/:repo/branches/prod/protection/required_pull_request_reviews

# Теперь можно merge без approval
gh pr merge 6 --squash
```

---

## 📋 Финальная конфигурация (рекомендация)

### Для dev:
```yaml
Protection:
  - Require PR: no
  - Required checks: [test]
  - Approvals: 0
```

### Для main:
```yaml
Protection:
  - Require PR: yes
  - Required checks: [test, security, code-quality]
  - Approvals: 0
  - enforce_admins: false
```

### Для prod:
```yaml
Protection:
  - Require PR: yes
  - Required checks: [test, security, code-quality]
  - Approvals: 0  ← ИЛИ используй admin bypass
  - enforce_admins: false  ← для admin bypass
  - require_last_push_approval: false
```

---

## ✅ Выводы

**Для solo-dev лучше:**
1. Убрать approval requirement (простота)
2. Полагаться на required checks (защита)
3. Использовать PR workflow (visibility + audit)

**Checks защищают от:**
- ❌ Broken tests
- ❌ Security vulnerabilities
- ❌ Code quality issues

**Approval защищает от:**
- ❌ Human errors (опечатки в config)
- ❌ Недостаточной проверки
- ⚠️ Но для solo-dev это твоя ответственность

**Рекомендация:** Вариант 2 (убрать approval, полагаться на checks)
