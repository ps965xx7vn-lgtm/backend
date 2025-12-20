# Branch Protection Setup Guide

## 🔒 Настройка защиты веток в GitHub

После пуша этих изменений, настройте Branch Protection Rules в GitHub:

### 1. Защита ветки `main`

**Settings → Branches → Add branch protection rule**

**Branch name pattern:** `main`

✅ **Require a pull request before merging**
  - Require approvals: **1**
  - Dismiss stale pull request approvals when new commits are pushed
  - Require review from Code Owners

✅ **Require status checks to pass before merging**
  - Require branches to be up to date before merging
  - Status checks required:
    - `test` (from ci.yml)
    - `security` (from ci.yml)
    - `code-quality` (from ci.yml)
    - `validate-main-pr` (from branch-protection.yml)
    - `full-test-suite` (from branch-protection.yml)

✅ **Require conversation resolution before merging**

✅ **Require linear history**

✅ **Include administrators** (применяется ко всем)

❌ **Allow force pushes** (запретить)

❌ **Allow deletions** (запретить)

---

### 2. Защита ветки `prod`

**Branch name pattern:** `prod`

✅ **Require a pull request before merging**
  - Require approvals: **2** (строже чем main)
  - Dismiss stale pull request approvals when new commits are pushed
  - Require review from Code Owners
  - Restrict who can dismiss pull request reviews (только admins)

✅ **Require status checks to pass before merging**
  - Require branches to be up to date before merging
  - Status checks required:
    - `test` (from ci.yml)
    - `security` (from ci.yml)
    - `code-quality` (from ci.yml)
    - `validate-prod-pr` (from branch-protection.yml)
    - `full-test-suite` (from branch-protection.yml)
    - `build-and-push` (from docker-publish.yml)

✅ **Require deployments to succeed before merging**

✅ **Require conversation resolution before merging**

✅ **Require linear history**

✅ **Require signed commits** (для production)

✅ **Include administrators**

❌ **Allow force pushes** (строго запретить)

❌ **Allow deletions** (строго запретить)

✅ **Restrict pushes that create matching branches** (только через PR)

---

### 3. Настройка ветки `dev`

**Branch name pattern:** `dev`

✅ **Require a pull request before merging** (опционально)
  - Require approvals: **0** (может быть без апрува для быстрой разработки)

✅ **Require status checks to pass before merging**
  - Status checks required:
    - `test` (from ci.yml)

✅ **Require conversation resolution before merging**

❌ **Allow force pushes** (можно разрешить для dev)

---

## 🔄 Git Flow процесс

### Создание новой фичи:

```bash
# Переключиться на dev и обновить
git checkout dev
git pull origin dev

# Создать feature ветку
git checkout -b feature/new-login-page

# Разработка...
git add .
git commit -m "feat: add new login page"
git push origin feature/new-login-page

# Создать PR в GitHub: feature/new-login-page → dev
```

### Релиз в staging (main):

```bash
# После мержа нескольких фич в dev
# Создать PR в GitHub: dev → main
# ⚠️ Требуется 1 approval
# ✅ Автоматически запустятся все тесты
# ✅ После мержа соберётся Docker образ с тегом 'latest'
```

### Деплой в production (prod):

```bash
# После тестирования на staging (main)
# Создать PR в GitHub: main → prod
# ⚠️ Требуется 2 approvals
# ✅ Полный набор тестов + security scan
# ✅ После мержа соберётся Docker образ с тегом 'production'
```

---

## 🐳 Docker Image Tags

| Branch | Docker Tags | Использование |
|--------|-------------|--------------|
| `dev` | `dev`, `dev-abc1234` | Development окружение |
| `main` | `latest`, `main`, `main-abc1234` | Staging окружение |
| `prod` | `production`, `prod-abc1234` | Production окружение |
| Tag `v1.2.3` | `1.2.3`, `1.2`, `1` | Release версии |

---

## 🚨 Защита от ошибок

### 1. Нельзя напрямую пушить в main/prod:
```bash
# ❌ Это не сработает:
git push origin main

# Error: remote: error: GH006: Protected branch update failed.
```

### 2. Нельзя мержить feature → main напрямую:
```bash
# ❌ PR feature/login → main будет отклонён
# ✅ Только dev → main разрешён
```

### 3. Нельзя мержить без тестов:
```bash
# ❌ Если CI тесты не прошли, мерж заблокирован
# ✅ Нужно исправить и ре-коммитить
```

---

## 📊 Рекомендуемая структура команды

| Роль | Права |
|------|-------|
| **Developers** | Push в dev, создание feature веток, approve PR в dev |
| **Tech Leads** | Approve PR dev → main (staging release) |
| **DevOps / CTO** | Approve PR main → prod (production deploy), 2 approvals обязательно |

---

## 🛠️ Быстрые команды

### Обновить все ветки:
```bash
git fetch --all
git checkout dev && git pull origin dev
git checkout main && git pull origin main
git checkout prod && git pull origin prod
```

### Hotfix в production:
```bash
# 1. Создать hotfix от prod
git checkout prod
git checkout -b hotfix/critical-bug

# 2. Исправить баг
git commit -m "fix: critical security issue"

# 3. Создать PR hotfix → prod (требуется 2 approvals)
# 4. После мержа в prod, также мержнуть обратно в main и dev
git checkout main
git merge hotfix/critical-bug
git push origin main

git checkout dev
git merge hotfix/critical-bug
git push origin dev
```

---

## 📝 CODEOWNERS файл (опционально)

Создайте `.github/CODEOWNERS`:

```
# Default reviewers для всех PR
* @your-username @tech-lead-username

# Критичные файлы требуют review от DevOps
Dockerfile @devops-username
.github/workflows/* @devops-username
docker-compose*.yml @devops-username

# Security файлы требуют review от security team
**/authentication/* @security-team
**/payments/* @security-team
```

---

## ✅ Проверка настройки

После настройки проверьте:

1. ✅ Создайте тестовую feature ветку и PR в dev
2. ✅ Попробуйте напрямую пушнуть в main (должно быть запрещено)
3. ✅ Создайте PR dev → main (должен требовать 1 approval)
4. ✅ Создайте PR main → prod (должен требовать 2 approvals)
5. ✅ Проверьте что Docker образы публикуются с правильными тегами

---

## 🔗 Полезные ссылки

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [CODEOWNERS Syntax](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
