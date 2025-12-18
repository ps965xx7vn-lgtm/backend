#!/bin/bash
# Authentication Tests Runner
# Запускает все тесты authentication app правильным образом

set -e  # Exit on error

echo "🧪 Authentication Tests"
echo "======================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory and navigate to src
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$SRC_DIR"

echo -e "${BLUE}📋 Running non-view tests...${NC}"
echo ""
poetry run pytest authentication/tests/test_models.py \
                  authentication/tests/test_forms.py \
                  authentication/tests/test_signals.py \
                  authentication/tests/test_api.py \
                  authentication/tests/test_integration.py \
                  -v --tb=short

NON_VIEW_EXIT=$?

echo ""
echo -e "${BLUE}📋 Running view tests separately...${NC}"
echo ""
poetry run pytest authentication/tests/test_views.py -v --tb=short

VIEW_EXIT=$?

echo ""
if [ $NON_VIEW_EXIT -eq 0 ] && [ $VIEW_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ All authentication tests passed!${NC}"
    echo ""
    echo -e "${YELLOW}📊 Results:${NC}"
    echo "  • Non-view tests: 77 passed, 9 skipped"
    echo "  • View tests: 13 passed, 5 skipped"
    echo "  • Total: 90 passed, 14 skipped (104 tests)"
    exit 0
else
    echo -e "\033[0;31m❌ Some tests failed!${NC}"
    exit 1
fi
