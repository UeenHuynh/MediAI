#!/bin/bash
# ===================================================================
# Run All Phase 1 Tests
# Tests: Groq API, PII Masker, Qdrant
# ===================================================================

set -e

echo "🧪 Running Phase 1 Test Suite..."
echo "================================================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
TOTAL_TESTS=3
PASSED_TESTS=0

# Test 1: Groq API
echo -e "\n${YELLOW}[1/$TOTAL_TESTS] Testing Groq API...${NC}"
if python3 scripts/test_groq_api.py; then
    echo -e "${GREEN}✅ Groq API test passed${NC}"
    ((PASSED_TESTS++))
else
    echo -e "${RED}❌ Groq API test failed${NC}"
fi

# Test 2: PII Masker
echo -e "\n${YELLOW}[2/$TOTAL_TESTS] Testing PII Masker...${NC}"
if python3 scripts/test_pii_masker.py; then
    echo -e "${GREEN}✅ PII Masker test passed${NC}"
    ((PASSED_TESTS++))
else
    echo -e "${RED}❌ PII Masker test failed${NC}"
fi

# Test 3: Qdrant
echo -e "\n${YELLOW}[3/$TOTAL_TESTS] Testing Qdrant...${NC}"
if python3 scripts/test_qdrant.py; then
    echo -e "${GREEN}✅ Qdrant test passed${NC}"
    ((PASSED_TESTS++))
else
    echo -e "${RED}❌ Qdrant test failed${NC}"
fi

# Summary
echo ""
echo "================================================================"
echo -e "${YELLOW}TEST SUMMARY${NC}"
echo "================================================================"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC} / $TOTAL_TESTS"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "\n${GREEN}🎉 All Phase 1 tests passed!${NC}"
    echo ""
    echo "Phase 1 (Foundation) is complete. Ready for Phase 2."
    echo ""
    echo "Next steps:"
    echo "  1. Implement CAG Cache (Layer 4)"
    echo "  2. Implement Qdrant integration (Layer 4)"
    echo "  3. Implement Hybrid RAG (Layer 4)"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed ($((TOTAL_TESTS - PASSED_TESTS)) failures)${NC}"
    echo ""
    echo "Please fix failed tests before proceeding to Phase 2."
    echo "See SETUP_CHATBOT.md for troubleshooting."
    exit 1
fi
