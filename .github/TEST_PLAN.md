# 🧪 План тестирования Git Flow

## ⚠️ ВАЖНО: Branch Protection для приватных репозиториев

**Branch Protection Rules доступны только для:**
- 🌍 Публичных репозиториев (бесплатно)
- 💰 GitHub Pro/Enterprise (приватные репозитории)

### Вариант 1: Сделать репозиторий публичным

```bash
gh repo edit OWNER/REPO --visibility public
```

Затем настройте защиту: **GitHub → Settings → Branches**

### Вариант 2: Альтернативная защита (для приватных repo)

Используйте `.github/workflows/branch-protection.yml` (уже настроено):
- ✅ Блокирует feature → main напрямую
- ✅ Блокирует dev → prod напрямую
- ✅ Требует прохождения всех CI тестов
- ❌ НЕ блокирует direct push (требуется дисциплина команды)

---

## 🔧 Настройка Branch Protection (если репозиторий публичный)

### 1️⃣ Настройка для ветки `main`

```
Branch name pattern: main

✅ Require a pull request before merging
  └─ Require approvals: 1
✅ Require status checks to pass before merging
  └─ Status checks:
     - test
     - security
     - code-quality
✅ Require conversation resolution before merging
✅ Do not allow bypassing the above settings
❌ Allow force pushes (DISABLED)
❌ Allow deletions (DISABLED)
```

### 2️⃣ Настройка для ветки `prod`

```
Branch name pattern: prod

✅ Require a pull request before merging
  └─ Require approvals: 2
✅ Require status checks to pass before merging
  └─ Status checks:
     - test
     - security
     - code-quality
     - validate-prod-pr
✅ Require conversation resolution before merging
✅ Do not allow bypassing the above settings
❌ Allow force pushes (DISABLED)
❌ Allow deletions (DISABLED)
```

### 3️⃣ Настройка для ветки `dev` (опционально)

```
Branch name pattern: dev

✅ Require status checks to pass before merging
  └─ Status checks:
     - test
```

---

## 🧪 Тест-кейсы

### ✅ TEST 1: Блокировка прямого пуша в main

**Ожидаемый результат:** ❌ Push отклонен

```bash
git checkout main
echo "test" > test.txt
git add test.txt
git commit -m "test: direct push to main"
git push origin main
```

**Должно быть:**
```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: error: At least 1 approving review is required by reviewers with write access.
```

---

### ✅ TEST 2: Блокировка прямого пуша в prod

**Ожидаемый результат:** ❌ Push отклонен

```bash
git checkout prod
echo "test" > test.txt
git add test.txt
git commit -m "test: direct push to prod"
git push origin prod
```

**Должно быть:**
```
remote: error: GH006: Protected branch update failed for refs/heads/prod.
remote: error: At least 2 approving reviews are required by reviewers with write access.
```

---

### ✅ TEST 3: Feature → dev (должен работать)

**Ожидаемый результат:** ✅ Успешный workflow

```bash
# Создать feature ветку от dev
git checkout dev
git pull origin dev
git checkout -b feature/test-login

# Сделать изменения
echo "# New Login Feature" > feature-test.md
git add feature-test.md
git commit -m "feat: add new login feature"

# Запушить feature ветку
git push origin feature/test-login
```

**Затем в GitHub:**
1. Создать PR: `feature/test-login` → `dev`
2. ✅ Должен запуститься CI workflow
3. ✅ После прохождения тестов можно мержить (без approval)
4. ✅ После мержа соберётся Docker образ с тегом `dev`

---

### ✅ TEST 4: dev → main (требует approval)

**Ожидаемый результат:** ✅ PR создан, требует 1 approval

```bash
# После мержа feature в dev
# Создать PR в GitHub: dev → main
```

**Проверка:**
1. PR создаётся успешно
2. ⏳ Запускаются workflows:
   - `test` (ci.yml)
   - `security` (ci.yml)
   - `code-quality` (ci.yml)
   - `validate-main-pr` (branch-protection.yml)
3. ⚠️ **Кнопка Merge заблокирована** до получения 1 approval
4. После approval → мерж → Docker образ `latest`

---

### ✅ TEST 5: main → prod (требует 2 approvals)

**Ожидаемый результат:** ✅ PR создан, требует 2 approvals

```bash
# После мержа в main и тестирования на staging
# Создать PR в GitHub: main → prod
```

**Проверка:**
1. PR создаётся успешно
2. ⏳ Запускаются workflows:
   - `test` (ci.yml)
   - `security` (ci.yml)
   - `code-quality` (ci.yml)
   - `validate-prod-pr` (branch-protection.yml)
   - `full-test-suite` (branch-protection.yml)
3. ⚠️ **Кнопка Merge заблокирована** до получения 2 approvals
4. После 2х approvals → мерж → Docker образ `production`

---

### ❌ TEST 6: feature → main напрямую (должен быть заблокирован)

**Ожидаемый результат:** ❌ Workflow провалится

```bash
# Попытаться создать PR: feature/test → main (минуя dev)
```

**Проверка:**
1. PR создаётся технически
2. ❌ Workflow `validate-main-pr` провалится с ошибкой:
   ```
   ❌ Error: Only PRs from 'dev' branch are allowed into 'main'
   Current source: feature/test
   ```
3. ❌ Merge заблокирован

---

### ❌ TEST 7: dev → prod напрямую (должен быть заблокирован)

**Ожидаемый результат:** ❌ Workflow провалится

```bash
# Попытаться создать PR: dev → prod (минуя main)
```

**Проверка:**
1. PR создаётся технически
2. ❌ Workflow `validate-prod-pr` провалится с ошибкой:
   ```
   ❌ Error: Only PRs from 'main' branch are allowed into 'prod'
   Current source: dev
   ```
3. ❌ Merge заблокирован

---

### ✅ TEST 8: Docker образы публикуются правильно

**Проверка тегов после мержа:**

| Branch | Push/Merge | Ожидаемые Docker теги |
|--------|------------|----------------------|
| `dev` | feature → dev merge | `dev`, `dev-abc1234` |
| `main` | dev → main merge | `latest`, `main`, `main-abc1234` |
| `prod` | main → prod merge | `production`, `prod-abc1234` |

**Команда для проверки:**
```bash
# Проверить что образы существуют на Docker Hub
docker pull <username>/pyland-backend:dev
docker pull <username>/pyland-backend:latest
docker pull <username>/pyland-backend:production
```

---

### ✅ TEST 9: CI проходит на всех ветках

**После push в любую ветку должны запускаться:**

```yaml
✅ test job:
  - Postgres + Redis services
  - Миграции
  - Pytest с coverage
  - Upload в Codecov

✅ security job:
  - Safety check
  - Bandit scan

✅ code-quality job:
  - Ruff linting
  - Black formatting
  - isort import sorting
  - mypy type checking
```

---

### ✅ TEST 10: Hotfix в production

**Сценарий:** Критический баг в production

```bash
# 1. Создать hotfix ветку от prod
git checkout prod
git pull origin prod
git checkout -b hotfix/critical-security-fix

# 2. Исправить баг
echo "fix" > security-fix.txt
git add security-fix.txt
git commit -m "fix: critical security vulnerability"
git push origin hotfix/critical-security-fix

# 3. Создать PR: hotfix → prod
# ⚠️ Требуется 2 approvals (экстренный процесс)

# 4. После мержа в prod, синхронизировать с main и dev:
git checkout main
git pull origin prod
git push origin main

git checkout dev
git pull origin main
git push origin dev
```

---

## 📊 Чеклист успешного тестирования

После прохождения всех тестов должно быть:

- ✅ Прямой push в main заблокирован
- ✅ Прямой push в prod заблокирован
- ✅ Feature → dev работает без approval
- ✅ dev → main требует 1 approval
- ✅ main → prod требует 2 approvals
- ✅ feature → main блокируется валидацией
- ✅ dev → prod блокируется валидацией
- ✅ Docker образы публикуются с правильными тегами
- ✅ CI проходит на всех ветках
- ✅ Все workflows завершаются успешно

---

## 🚀 Быстрый скрипт для полного теста

Создайте файл `test-git-flow.sh`:

```bash
#!/bin/bash
set -e

echo "🧪 Starting Git Flow Test Suite"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Попытка прямого пуша в main
echo -e "\n${YELLOW}TEST 1: Direct push to main${NC}"
git checkout main
echo "test" > test-main.txt
git add test-main.txt
git commit -m "test: direct push to main" 2>/dev/null || true
if git push origin main 2>&1 | grep -q "protected branch"; then
    echo -e "${GREEN}✅ PASS: main is protected${NC}"
    git reset --hard HEAD~1
else
    echo -e "${RED}❌ FAIL: main is NOT protected${NC}"
    git reset --hard HEAD~1
    git push origin main --force
fi

# Test 2: Попытка прямого пуша в prod
echo -e "\n${YELLOW}TEST 2: Direct push to prod${NC}"
git checkout prod
echo "test" > test-prod.txt
git add test-prod.txt
git commit -m "test: direct push to prod" 2>/dev/null || true
if git push origin prod 2>&1 | grep -q "protected branch"; then
    echo -e "${GREEN}✅ PASS: prod is protected${NC}"
    git reset --hard HEAD~1
else
    echo -e "${RED}❌ FAIL: prod is NOT protected${NC}"
    git reset --hard HEAD~1
    git push origin prod --force
fi

# Test 3: Feature → dev workflow
echo -e "\n${YELLOW}TEST 3: Feature → dev workflow${NC}"
git checkout dev
git pull origin dev
git checkout -b feature/test-$(date +%s)
echo "# Test Feature" > test-feature.md
git add test-feature.md
git commit -m "feat: test feature"
git push origin feature/test-$(date +%s)
echo -e "${GREEN}✅ Feature branch created - create PR manually in GitHub${NC}"

echo -e "\n${GREEN}🎉 Test suite completed!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure Branch Protection Rules in GitHub UI"
echo "2. Create PRs and verify workflows"
echo "3. Check Docker Hub for published images"
```

Запустить:
```bash
chmod +x test-git-flow.sh
./test-git-flow.sh
```

---

## 🔗 Полезные команды

```bash
# Проверить все удаленные ветки
git branch -r

# Проверить защищенные ветки (через GitHub CLI)
gh api repos/:owner/:repo/branches/main/protection

# Проверить статус workflows
gh run list --limit 10

# Проверить Docker образы
docker search <username>/pyland-backend
```

---

## 📞 Troubleshooting

### Проблема: Branch Protection не работает
**Решение:** Убедитесь что настроили правила в Settings → Branches и включили "Include administrators"

### Проблема: CI workflows не запускаются
**Решение:** Проверьте что secrets настроены: DOCKERHUB_USERNAME, DOCKERHUB_TOKEN, CODECOV_TOKEN

### Проблема: Docker образы не публикуются
**Решение:** Проверьте Docker Hub credentials и permissions

### Проблема: Тесты падают на pytest
**Решение:** Проверьте DATABASE_URL и REDIS_URL в CI environment
