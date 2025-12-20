#!/bin/bash

echo "🔒 Setting up Branch Protection Rules via GitHub API"
echo "====================================================="

# Проверка наличия GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found"
    echo "Install: brew install gh"
    echo ""
    echo "Alternative: Configure manually in GitHub UI"
    echo "See: .github/BRANCH_PROTECTION_SETUP.md"
    exit 1
fi

# Проверка авторизации
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

# Получить информацию о репозитории
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "📦 Repository: $REPO"
echo ""

# Функция для настройки защиты ветки
protect_branch() {
    local branch=$1
    local required_approvals=$2
    local required_checks=$3

    echo "🔒 Protecting branch: $branch (approvals: $required_approvals)"

    # Базовая защита через API
    gh api \
        --method PUT \
        -H "Accept: application/vnd.github+json" \
        "/repos/$REPO/branches/$branch/protection" \
        -f required_status_checks[strict]=true \
        -f required_status_checks[contexts][]="$required_checks" \
        -f enforce_admins=true \
        -f required_pull_request_reviews[dismiss_stale_reviews]=true \
        -f required_pull_request_reviews[require_code_owner_reviews]=false \
        -f required_pull_request_reviews[required_approving_review_count]=$required_approvals \
        -f required_pull_request_reviews[require_last_push_approval]=false \
        -f restrictions=null \
        -f required_linear_history=true \
        -f allow_force_pushes=false \
        -f allow_deletions=false \
        -f required_conversation_resolution=true \
        -f lock_branch=false \
        -f allow_fork_syncing=true \
        && echo "✅ $branch protected" || echo "❌ Failed to protect $branch"

    echo ""
}

# Настроить защиту для main
echo "━━━ Configuring main branch ━━━"
protect_branch "main" "1" "test,security,code-quality"

# Настроить защиту для prod
echo "━━━ Configuring prod branch ━━━"
protect_branch "prod" "2" "test,security,code-quality,validate-prod-pr,full-test-suite"

# Настроить защиту для dev (опционально, только тесты)
echo "━━━ Configuring dev branch ━━━"
gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    "/repos/$REPO/branches/dev/protection" \
    -f required_status_checks[strict]=true \
    -f required_status_checks[contexts][]=test \
    -f enforce_admins=false \
    -f required_pull_request_reviews=null \
    -f restrictions=null \
    -f required_linear_history=false \
    -f allow_force_pushes=true \
    -f allow_deletions=false \
    && echo "✅ dev protected (lightweight)" || echo "❌ Failed to protect dev"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Branch Protection configured!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Verify in GitHub:"
echo "https://github.com/$REPO/settings/branches"
echo ""
echo "Test with:"
echo "./test-git-flow.sh"
