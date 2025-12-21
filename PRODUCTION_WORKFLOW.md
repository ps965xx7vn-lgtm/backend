# Production Workflow Guide

## Структура веток и правила

### 🔧 `dev` - Development Branch
**Назначение:** Активная разработка, быстрые итерации

**Правила:**
- ✅ Прямые коммиты разрешены
- ✅ Быстрый цикл разработки
- ⚠️ Required checks: `test` (обязательно)

**Workflow:**
```bash
git checkout dev
git add .
git commit -m "feat: новая функция"
git push origin dev
```

---

### 🚀 `main` - Staging/Pre-Production
**Назначение:** Стабильная версия для тестирования перед prod

**Правила:**
- ❌ Прямые коммиты **ЗАПРЕЩЕНЫ**
- ✅ Только через Pull Request
- ✅ Approval **НЕ требуется** (solo-dev friendly)
- ✅ Required checks: `test`, `security`, `code-quality`

**Workflow:**
```bash
# 1. Создать feature ветку или использовать dev
git checkout -b feature/my-feature
# или
git checkout dev

# 2. Сделать изменения и закоммитить
git add .
git commit -m "feat: описание"
git push origin dev  # или feature/my-feature

# 3. Создать PR в main
gh pr create --base main --head dev --title "feat: ..." --body "..."

# 4. Дождаться CI (2-3 минуты)
gh pr checks <номер>

# 5. Смержить самостоятельно (без approval)
gh pr merge <номер> --squash --delete-branch
```

---

### 🏭 `prod` - Production Branch
**Назначение:** Production-ready код, максимальная стабильность

**Правила:**
- ❌ Прямые коммиты **СТРОГО ЗАПРЕЩЕНЫ**
- ✅ Только через Pull Request
- ✅ **ОБЯЗАТЕЛЬНЫЙ Approval** (минимум 1 reviewer)
- ✅ `require_last_push_approval: true` - нужен approval после последнего пуша
- ✅ `enforce_admins: true` - даже admin не может обойти правила
- ✅ Required checks: `test`, `security`, `code-quality`, `Docker Build and Push`
- ✅ `required_conversation_resolution: true` - все комментарии должны быть разрешены

**Workflow:**
```bash
# 1. Убедиться что main стабилен и протестирован
git checkout main
git pull origin main

# 2. Создать PR main → prod
gh pr create --base prod --head main \
  --title "release: версия X.Y.Z" \
  --body "## Release Notes

- Новые фичи
- Исправления
- Breaking changes

**Тестирование:** [ссылка на тест-план]
**Changelog:** [ссылка]"

# 3. Дождаться CI + Docker build (10-12 минут)
gh pr checks <номер>

# 4. ⚠️ НУЖЕН APPROVAL от другого разработчика
# Для solo-dev временно:
# - Попросить кого-то проаппрувить
# - Или создать второй GitHub аккаунт для code review
# - Или временно отключить enforce_admins (НЕ рекомендуется)

# 5. После approval - мерж
gh pr merge <номер> --merge  # НЕ squash для prod!
```

---

## Сравнение защиты веток

| Правило | dev | main | prod |
|---------|-----|------|------|
| Прямые коммиты | ✅ Разрешены | ❌ Запрещены | ❌ Запрещены |
| Pull Request | ⚪ Опционально | ✅ Обязателен | ✅ Обязателен |
| Required Approval | ⚪ Нет | ⚪ 0 (solo-dev) | ✅ **1+ reviewer** |
| enforce_admins | ❌ false | ❌ false | ✅ **true** |
| require_last_push_approval | ❌ - | ❌ false | ✅ **true** |
| Required Checks | test | test, security, code-quality | test, security, code-quality, **Docker** |
| Conversation Resolution | ❌ - | ❌ false | ✅ **true** |

---

## Hotfix Workflow (срочные фиксы в prod)

```bash
# 1. Создать hotfix ветку от prod
git checkout prod
git pull origin prod
git checkout -b hotfix/critical-bug

# 2. Исправить баг
git add .
git commit -m "hotfix: критический баг X"
git push origin hotfix/critical-bug

# 3. Создать PR hotfix → prod (приоритет!)
gh pr create --base prod --head hotfix/critical-bug \
  --title "🔥 HOTFIX: критический баг X" \
  --label "hotfix,priority:high"

# 4. ⚠️ СРОЧНО попросить approval у reviewer
# После approval - мерж

# 5. Backport в main и dev
git checkout main
git cherry-pick <hotfix-commit-sha>
git push origin main

git checkout dev
git cherry-pick <hotfix-commit-sha>
git push origin dev
```

---

## CI/CD Checks

### Required для всех веток:
- ✅ **test** - pytest (все тесты должны пройти)
- ✅ **security** - bandit, safety, trivy
- ✅ **code-quality** - ruff, black, isort, mypy

### Дополнительно для prod:
- ✅ **Docker Build and Push** - успешная сборка и публикация образа

### Non-blocking (не блокируют merge):
- ⚠️ **Lint Markdown** - проверка markdown файлов (continue-on-error)
- ℹ️ **Check Links** - проверка ссылок в документации

---

## Быстрые команды

```bash
# Проверить статус веток
gh api repos/ps965xx7vn-lgtm/backend/branches | jq -r '.[].name'

# Проверить protection settings
gh api repos/ps965xx7vn-lgtm/backend/branches/prod/protection | jq '{approvals, enforce_admins, checks}'

# Посмотреть открытые PR
gh pr list --state open

# Проверить checks для PR
gh pr checks <номер>

# Просмотр логов failed check
gh run view <run-id> --log-failed

# Список последних workflow runs
gh run list --limit 10
```

---

## Solo-Dev Временные решения для Prod Approval

### Вариант 1: Второй GitHub аккаунт (рекомендуется)
```bash
# 1. Создать второй GitHub аккаунт (например, для code review)
# 2. Добавить в репозиторий с Write доступом
gh api repos/ps965xx7vn-lgtm/backend/collaborators/SECOND_USERNAME --method PUT

# 3. Заапрувить PR с второго аккаунта
# (открыть в браузере под вторым аккаунтом)
```

### Вариант 2: GitHub CLI с разными токенами
```bash
# Создать review от имени другого пользователя (если есть доступ)
GH_TOKEN=<token-второго-аккаунта> gh pr review <номер> --approve
```

### Вариант 3: Временно отключить enforce_admins (⚠️ НЕ рекомендуется)
```bash
# Только в крайнем случае для hotfix!
gh api --method DELETE repos/ps965xx7vn-lgtm/backend/branches/prod/protection/enforce_admins

# Мерж с --admin флагом
gh pr merge <номер> --merge --admin

# ⚠️ ОБЯЗАТЕЛЬНО восстановить!
gh api --method POST repos/ps965xx7vn-lgtm/backend/branches/prod/protection/enforce_admins
```

---

## Best Practices

1. **Всегда тестируй в dev** перед PR в main
2. **main → prod** только после полного тестирования
3. **Используй semantic commit messages**: `feat:`, `fix:`, `docs:`, `refactor:`
4. **Добавляй описание в PR** - что изменилось, зачем, как тестировалось
5. **Проверяй Docker build** перед prod deployment
6. **Делай small PRs** - легче ревьюить и мержить
7. **Храни CHANGELOG.md** - документируй изменения для prod

---

## Troubleshooting

### PR не мержится без approval
**Проблема:** "At least 1 approving review is required"
**Решение:** Это prod ветка - нужен реальный approval. См. "Solo-Dev Временные решения" выше.

### Admin не может обойти правила
**Проблема:** "enforce_admins is enabled"
**Решение:** Это правильно для prod! Используй временное отключение только для hotfix.

### Checks не проходят
**Проблема:** CI падает
**Решение:**
```bash
# Посмотреть детали
gh run view <run-id> --log-failed

# Перезапустить failed check
gh run rerun <run-id>
```

---

## Переход к team-разработке

Когда появится второй разработчик:

1. ✅ Prod protection уже настроен правильно
2. ✅ Добавить CODEOWNERS файл:
```bash
cat > .github/CODEOWNERS << 'EOF'
* @username1 @username2
/src/authentication/ @username1
/src/core/ @username2
EOF
```

3. ✅ Включить `require_code_owner_reviews: true` для prod:
```bash
# Обновить prod protection
gh api --method PATCH repos/ps965xx7vn-lgtm/backend/branches/prod/protection/required_pull_request_reviews \
  -f require_code_owner_reviews=true
```

4. ✅ Настроить main тоже с approval:
```bash
# Установить required_approving_review_count: 1 для main
```

---

**Итог:** Prod ветка уже готова для командной работы! Просто пригласи reviewers. 🚀
