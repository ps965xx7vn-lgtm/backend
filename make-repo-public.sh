#!/bin/bash

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "════════════════════════════════════════"
echo "🔓 Сделать репозиторий публичным"
echo "════════════════════════════════════════"
echo ""

# Проверка GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI не установлен"
    echo "Установите: brew install gh"
    exit 1
fi

# Авторизация
if ! gh auth status &> /dev/null; then
    echo "❌ Не авторизованы в GitHub CLI"
    echo "Выполните: gh auth login"
    exit 1
fi

# Получить информацию о репозитории
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
VISIBILITY=$(gh repo view --json visibility -q .visibility)

echo -e "${BLUE}📦 Репозиторий:${NC} $REPO"
echo -e "${BLUE}🔒 Текущий статус:${NC} $VISIBILITY"
echo ""

if [ "$VISIBILITY" = "PUBLIC" ]; then
    echo -e "${GREEN}✅ Репозиторий уже публичный!${NC}"
    echo ""
    echo "Теперь можно настроить Branch Protection:"
    echo "  ./setup-branch-protection.sh"
    exit 0
fi

echo -e "${YELLOW}⚠️  Внимание!${NC}"
echo ""
echo "Сделав репозиторий публичным:"
echo "  ✅ Бесплатная Branch Protection"
echo "  ✅ Бесплатные GitHub Actions (3000 мин/мес → безлимит)"
echo "  ✅ Видимость в GitHub Search"
echo "  ✅ Возможность получать contributions от community"
echo ""
echo "  ⚠️  Весь код будет доступен публично"
echo "  ⚠️  История коммитов будет видна всем"
echo "  ⚠️  Secrets останутся защищенными (не будут видны)"
echo ""
read -p "Продолжить? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "❌ Отменено"
    echo ""
    echo "Альтернатива: используйте GitHub Actions для защиты"
    echo "  Уже настроено в .github/workflows/branch-protection.yml"
    exit 1
fi

echo ""
echo "🔄 Изменяю видимость репозитория..."
gh repo edit $REPO --visibility public

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Репозиторий теперь ПУБЛИЧНЫЙ!${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""
    echo "Следующие шаги:"
    echo ""
    echo "1️⃣  Настроить Branch Protection:"
    echo "   ./setup-branch-protection.sh"
    echo ""
    echo "2️⃣  Проверить что все работает:"
    echo "   ./test-git-flow.sh"
    echo ""
    echo "3️⃣  Открыть настройки в браузере:"
    echo "   https://github.com/$REPO/settings/branches"
    echo ""
else
    echo ""
    echo "❌ Ошибка при изменении видимости"
    echo "Попробуйте вручную: https://github.com/$REPO/settings"
    exit 1
fi
