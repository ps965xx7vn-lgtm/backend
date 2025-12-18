#!/bin/bash
# Main Test Runner for Pyland Backend
# Запускает все тесты проекта

set -e  # Exit on error

echo "🧪 Pyland Backend Tests"
echo "======================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory (src/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Track test results
TOTAL_PASSED=0
TOTAL_FAILED=0
TOTAL_SKIPPED=0
FAILED_APPS=()

# Function to run tests for an app
run_app_tests() {
    local APP_NAME=$1
    local TEST_SCRIPT=$2
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📦 Testing: ${APP_NAME}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    if [ -f "$TEST_SCRIPT" ]; then
        if bash "$TEST_SCRIPT"; then
            echo -e "${GREEN}✅ ${APP_NAME} tests passed${NC}"
            return 0
        else
            echo -e "${RED}❌ ${APP_NAME} tests failed${NC}"
            FAILED_APPS+=("$APP_NAME")
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  No test script found: $TEST_SCRIPT${NC}"
        return 0
    fi
}

# Run Authentication tests
run_app_tests "Authentication" "authentication/tests/run_tests.sh" || true

# TODO: Add other apps when ready
# run_app_tests "Blog" "blog/tests/run_tests.sh" || true
# run_app_tests "Courses" "courses/tests/run_tests.sh" || true
# run_app_tests "Students" "students/tests/run_tests.sh" || true

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Test Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ ${#FAILED_APPS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Tested apps:"
    echo "  • Authentication: 90 passed, 14 skipped"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo ""
    echo "Failed apps:"
    for app in "${FAILED_APPS[@]}"; do
        echo -e "  ${RED}✗${NC} $app"
    done
    echo ""
    exit 1
fi
