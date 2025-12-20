#!/bin/bash
set -e

echo "🧪 Git Flow Protection Test Suite"
echo "================================="

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS_COUNT=0
FAIL_COUNT=0

# Функция для тестов
run_test() {
    local test_name=$1
    local expected=$2
    echo -e "\n${BLUE}━━━ $test_name ━━━${NC}"
}

pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASS_COUNT++))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAIL_COUNT++))
}

warn() {
    echo -e "${YELLOW}⚠️  WARNING${NC}: $1"
}

# Сохранить текущую ветку
ORIGINAL_BRANCH=$(git branch --show-current)

# TEST 1: Проверка прямого пуша в main
run_test "TEST 1: Direct push to main (should be blocked)" "blocked"
git checkout main -q 2>/dev/null
git pull origin main -q 2>/dev/null
echo "test-$(date +%s)" > .test-main.txt
git add .test-main.txt
git commit -m "test: direct push to main" -q 2>/dev/null || true

if git push origin main 2>&1 | grep -qE "(protected|GH006|required|approval)"; then
    pass "main branch is protected"
    git reset --hard HEAD~1 -q 2>/dev/null
else
    fail "main branch is NOT protected - anyone can push directly!"
    warn "Please configure Branch Protection Rules in GitHub Settings"
    git reset --hard HEAD~1 -q 2>/dev/null
    git push origin main --force -q 2>/dev/null
fi

# TEST 2: Проверка прямого пуша в prod
run_test "TEST 2: Direct push to prod (should be blocked)" "blocked"
git checkout prod -q 2>/dev/null
git pull origin prod -q 2>/dev/null
echo "test-$(date +%s)" > .test-prod.txt
git add .test-prod.txt
git commit -m "test: direct push to prod" -q 2>/dev/null || true

if git push origin prod 2>&1 | grep -qE "(protected|GH006|required|approval)"; then
    pass "prod branch is protected"
    git reset --hard HEAD~1 -q 2>/dev/null
else
    fail "prod branch is NOT protected - anyone can push directly!"
    warn "Please configure Branch Protection Rules in GitHub Settings"
    git reset --hard HEAD~1 -q 2>/dev/null
    git push origin prod --force -q 2>/dev/null
fi

# TEST 3: Проверка что можно пушить в dev
run_test "TEST 3: Direct push to dev (should work)" "allowed"
git checkout dev -q 2>/dev/null
git pull origin dev -q 2>/dev/null
echo "test-$(date +%s)" > .test-dev.txt
git add .test-dev.txt
git commit -m "test: direct push to dev" -q 2>/dev/null

if git push origin dev -q 2>/dev/null; then
    pass "dev branch allows direct pushes (as configured)"
    git reset --hard HEAD~1 -q 2>/dev/null
    git push origin dev --force -q 2>/dev/null
else
    warn "dev branch push failed - check network or permissions"
fi

# TEST 4: Проверка наличия workflows
run_test "TEST 4: Workflow files exist" "present"
if [ -f ".github/workflows/ci.yml" ] && \
   [ -f ".github/workflows/docker-publish.yml" ] && \
   [ -f ".github/workflows/branch-protection.yml" ]; then
    pass "All required workflow files exist"
else
    fail "Some workflow files are missing"
fi

# TEST 5: Проверка правильности веток
run_test "TEST 5: Required branches exist" "present"
REQUIRED_BRANCHES=("main" "dev" "prod")
MISSING_BRANCHES=()

for branch in "${REQUIRED_BRANCHES[@]}"; do
    if git show-ref --verify --quiet refs/remotes/origin/$branch; then
        pass "Branch '$branch' exists"
    else
        fail "Branch '$branch' is missing"
        MISSING_BRANCHES+=($branch)
    fi
done

# TEST 6: Создание тестовой feature ветки
run_test "TEST 6: Feature branch creation" "allowed"
FEATURE_BRANCH="feature/test-$(date +%s)"
git checkout dev -q 2>/dev/null
git pull origin dev -q 2>/dev/null

if git checkout -b $FEATURE_BRANCH -q 2>/dev/null; then
    echo "# Test Feature" > .test-feature.md
    git add .test-feature.md
    git commit -m "feat: test feature for Git Flow" -q 2>/dev/null

    if git push origin $FEATURE_BRANCH -q 2>/dev/null; then
        pass "Feature branch created and pushed successfully"
        echo -e "${YELLOW}   → Create PR in GitHub: $FEATURE_BRANCH → dev${NC}"
        git checkout dev -q 2>/dev/null
        git branch -D $FEATURE_BRANCH -q 2>/dev/null
        git push origin --delete $FEATURE_BRANCH -q 2>/dev/null
    else
        fail "Failed to push feature branch"
    fi
else
    fail "Failed to create feature branch"
fi

# Вернуться на исходную ветку
git checkout $ORIGINAL_BRANCH -q 2>/dev/null

# Итоговый отчёт
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📊 TEST SUMMARY${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. ✅ Verify workflows run successfully in GitHub Actions"
    echo "2. ✅ Test PR workflow: feature → dev → main → prod"
    echo "3. ✅ Check Docker Hub for published images"
    echo "4. ✅ Configure Branch Protection Rules if not done yet"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo ""
    echo -e "${YELLOW}Action required:${NC}"

    if git push origin main 2>&1 | grep -qvE "(protected|GH006)"; then
        echo "⚠️  Configure Branch Protection for 'main' and 'prod' in:"
        echo "   GitHub → Settings → Branches → Add branch protection rule"
        echo ""
        echo "   See: .github/BRANCH_PROTECTION_SETUP.md for full instructions"
    fi

    exit 1
fi
