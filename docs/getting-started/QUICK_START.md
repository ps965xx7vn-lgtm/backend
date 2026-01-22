# 🚀 Быстрый старт - Pyland Backend

## Branch Structure

```
dev (разработка) → main (staging) → prod (production)
     ↓ прямой push      ↓ PR (0 approvals)   ↓ PR (1+ approval REQUIRED)
```

## Быстрый workflow

### 1️⃣ Разработка фичи

```bash
# В dev можно коммитить напрямую
git checkout dev
git add .
git commit -m "feat: новая фича"
git push origin dev
```

### 2️⃣ Deploy в staging (main)

```bash
# Создать PR dev → main
gh pr create --base main --head dev \
  --title "feat: новая фича" \
  --body "Описание изменений"

# Подождать CI (2-3 мин)
gh pr checks <номер>

# Мержить САМОСТОЯТЕЛЬНО (без approval)
gh pr merge <номер> --squash --delete-branch
```

### 3️⃣ Release в production

```bash
# Создать PR main → prod
gh pr create --base prod --head main \
  --title "release: версия X.Y.Z" \
  --body "Release notes..."

# ⚠️ НУЖЕН APPROVAL от другого разработчика
# Попросить кого-то заапрувить PR
# После approval:
gh pr merge <номер> --squash
```

---

## Solo-dev обходной путь для prod

### Вариант A: Второй GitHub аккаунт (рекомендуется)

1. Создай второй GitHub аккаунт для code review
2. Добавь в репозиторий:
   ```bash
   gh api repos/ps965xx7vn-lgtm/backend/collaborators/USERNAME --method PUT
   ```
3. Заапрувь PR с второго аккаунта

### Вариант B: Временное отключение (только для hotfix!)

```bash
# 1. Отключить enforce_admins
gh api --method DELETE repos/ps965xx7vn-lgtm/backend/branches/prod/protection/enforce_admins

# 2. Мерж с admin override
gh pr merge <номер> --squash --admin

# 3. ⚠️ СРАЗУ ВОССТАНОВИТЬ!
gh api --method POST repos/ps965xx7vn-lgtm/backend/branches/prod/protection/enforce_admins
```

---

## CI/CD Required Checks

✅ **test** - pytest (все тесты)
✅ **security** - bandit, safety
✅ **code-quality** - ruff, black, isort

**Для prod дополнительно:**
✅ **Docker Build and Push** - сборка и публикация образа

---

## Полезные команды

```bash
# Проверить статус PR
gh pr checks <номер>

# Посмотреть открытые PR
gh pr list

# Посмотреть защиту веток
gh api repos/ps965xx7vn-lgtm/backend/branches/prod/protection | jq

# Перезапустить failed workflow
gh run rerun <run-id>
```

---

## 📚 Детальная документация

- **PRODUCTION_WORKFLOW.md** - полный гайд по production workflow
- **GIT_WORKFLOW.md** - Git Flow стратегия
- **CONTRIBUTING.md** - contribution guidelines

---

## Текущий статус

- ✅ **dev** - свободная разработка
- ✅ **main** - solo-dev friendly (0 approvals)
- ✅ **prod** - ТРЕБУЕТ approval (готов для team)

**PR #6 (main → prod) ожидает approval для тестирования prod workflow**
