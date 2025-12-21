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
VISIBILITY=$(gh repo view --json visibility -q .visibility)
echo "📦 Repository: $REPO"
echo "🔍 Visibility: $VISIBILITY"
echo ""

# Проверка типа репозитория
if [ "$VISIBILITY" = "PRIVATE" ]; then
    echo "⚠️  WARNING: Branch Protection requires GitHub Pro for private repos"
    echo ""
    echo "You have 2 options:"
    echo ""
    echo "1️⃣  Make repository PUBLIC (recommended for open-source):"
    echo "   gh repo edit $REPO --visibility public"
    echo ""
    echo "2️⃣  Use alternative protection (GitHub Actions + CODEOWNERS):"
    echo "   Already configured in .github/workflows/branch-protection.yml"
    echo ""
    read -p "Make repository public now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📢 Making repository public..."
        gh repo edit $REPO --visibility public
        echo "✅ Repository is now public"
        echo ""
    else
        echo "ℹ️  Using alternative protection via GitHub Actions"
        echo "   Your workflows will block invalid PRs automatically"
        echo ""
        echo "✅ Setup complete (alternative mode)"
        exit 0
    fi
fi

# Функция для настройки защиты ветки
protect_branch() {
    local branch=$1
    local required_approvals=$2
    shift 2
    local required_checks=("$@")

    echo "🔒 Protecting branch: $branch (approvals: $required_approvals)"

    # Формируем JSON для contexts
    local contexts_json="["
    for check in "${required_checks[@]}"; do
        contexts_json+="\"$check\","
    done
    contexts_json="${contexts_json%,}]"  # Удаляем последнюю запятую

    # Базовая защита через API с правильными типами данных
    gh api \
        --method PUT \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "/repos/$REPO/branches/$branch/protection" \
        --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": $contexts_json
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": $required_approvals,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
EOF

    if [ $? -eq 0 ]; then
        echo "✅ $branch protected"
    else
        echo "❌ Failed to protect $branch"
    fi
# Настроить защиту для main
echo "━━━ Configuring main branch ━━━"
protect_branch "main" 1 "test" "security" "code-quality"

# Настроить защиту для prod
echo "━━━ Configuring prod branch ━━━"
protect_branch "prod" 2 "test" "security" "code-quality" "validate-prod-pr" "full-test-suite"

# Настроить защиту для dev (опционально, только тесты)
echo "━━━ Configuring dev branch ━━━"
gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "/repos/$REPO/branches/dev/protection" \
    --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["test"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": true,
  "allow_deletions": false
}
EOF

if [ $? -eq 0 ]; then
    echo "✅ dev protected (lightweight)"
else
    echo "❌ Failed to protect dev"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Branch Protection configured!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Verify in GitHub:"
echo "https://github.com/$REPO/settings/branches"
echo ""
echo "Test with:"
echo "./test-git-flow.sh"
