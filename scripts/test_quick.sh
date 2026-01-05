#!/bin/bash
# Quick API test - essential endpoints only

set -e
set -o pipefail

BASE_URL="http://localhost:8000"
API_URL="$BASE_URL/api/v1"

echo "🧪 MediAI Quick API Test"
echo "========================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

test_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    local auth="$5"

    echo -n "Testing: $name ... "

    if [ -n "$data" ]; then
        if [ -n "$auth" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $auth" \
                -d "$data")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
                -H "Content-Type: application/json" \
                -d "$data")
        fi
    else
        if [ -n "$auth" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
                -H "Authorization: Bearer $auth")
        else
            response=$(curl -s -w "\n%{http_code}" "$url")
        fi
    fi

    http_code=$(echo "$response" | tail -n1)

    if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
        echo -e "${GREEN}✓ PASS${NC} ($http_code)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} ($http_code)"
        FAILED=$((FAILED + 1))
    fi
}

# 1. Health Check (no auth)
test_endpoint "Health Check" "GET" "$BASE_URL/health"

# 2. Login
echo -n "Testing: Login ... "
login_response=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=demo&password=demo123")

TOKEN=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓ PASS${NC} (token received)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC} (no token)"
    FAILED=$((FAILED + 1))
    exit 1
fi

# 3. Get Current User
test_endpoint "Get Current User" "GET" "$API_URL/auth/me" "" "$TOKEN"

# 4. List Doctors
test_endpoint "List Doctors" "GET" "$API_URL/doctors?limit=5" "" "$TOKEN"

# 5. Get Doctor by ID
test_endpoint "Get Doctor #1" "GET" "$API_URL/doctors/1" "" "$TOKEN"

# 6. Chat - Ask Question
CHAT_DATA='{"message":"What is sepsis?","include_sources":true}'
test_endpoint "Chat: Ask Question" "POST" "$API_URL/chat" "$CHAT_DATA" "$TOKEN"

# 7. List Chat Sessions
test_endpoint "Chat: List Sessions" "GET" "$API_URL/chat/sessions" "" "$TOKEN"

# Summary
echo ""
echo "========================"
echo "Test Summary:"
echo "  Passed: $PASSED"
echo "  Failed: $FAILED"
echo "========================"

if [ $FAILED -gt 0 ]; then
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
