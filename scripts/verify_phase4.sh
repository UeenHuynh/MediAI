#!/bin/bash
# Phase 4 Integration Verification Script
# Tests critical integration points between Frontend and Backend

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="http://localhost:8000/api/v1"
FRONTEND_URL="http://localhost:3000"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Phase 4 Integration Verification${NC}"
echo -e "${BLUE}============================================${NC}\n"

PASSED=0
FAILED=0

check() {
    local name="$1"
    local result="$2"

    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $name"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} $name"
        FAILED=$((FAILED + 1))
    fi
}

# 1. Backend Health
echo -e "\n${YELLOW}[1/10]${NC} Backend API Health..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    check "Backend API is healthy" "PASS"
else
    check "Backend API is healthy" "FAIL"
fi

# 2. Frontend Server
echo -e "\n${YELLOW}[2/10]${NC} Frontend Server..."
if curl -s $FRONTEND_URL | grep -q "<!DOCTYPE html>"; then
    check "Frontend server is running" "PASS"
else
    check "Frontend server is running" "FAIL"
fi

# 3. CORS Configuration
echo -e "\n${YELLOW}[3/10]${NC} CORS Configuration..."
CORS_TEST=$(curl -s -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: POST" -X OPTIONS $API_URL/auth/login -i)
if echo "$CORS_TEST" | grep -q "Access-Control-Allow-Origin"; then
    check "CORS headers present" "PASS"
else
    check "CORS headers present" "FAIL"
fi

# 4. JWT Authentication Flow
echo -e "\n${YELLOW}[4/10]${NC} JWT Authentication Flow..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=demo&password=demo123")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
REFRESH=$(echo "$LOGIN_RESPONSE" | grep -o '"refresh_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ] && [ -n "$REFRESH" ]; then
    check "JWT tokens generated" "PASS"
else
    check "JWT tokens generated" "FAIL"
fi

# 5. Token Authorization
echo -e "\n${YELLOW}[5/10]${NC} Token Authorization..."
USER_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/auth/me")
if echo "$USER_RESPONSE" | grep -q "username"; then
    check "Bearer token authentication works" "PASS"
else
    check "Bearer token authentication works" "FAIL"
fi

# 6. Token Refresh Flow
echo -e "\n${YELLOW}[6/10]${NC} Token Refresh Flow..."
REFRESH_RESPONSE=$(curl -s -X POST "$API_URL/auth/refresh" \
    -H "Content-Type: application/json" \
    -d "{\"token\":\"$REFRESH\"}")

NEW_TOKEN=$(echo "$REFRESH_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
if [ -n "$NEW_TOKEN" ]; then
    check "Token refresh mechanism works" "PASS"
else
    check "Token refresh mechanism works" "FAIL"
fi

# 7. Protected Endpoint Access
echo -e "\n${YELLOW}[7/10]${NC} Protected Endpoint Access..."
DOCTORS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/doctors?limit=1")
if echo "$DOCTORS_RESPONSE" | grep -q "doctors"; then
    check "Protected endpoints accessible with JWT" "PASS"
else
    check "Protected endpoints accessible with JWT" "FAIL"
fi

# 8. Unauthorized Access Blocked
echo -e "\n${YELLOW}[8/10]${NC} Unauthorized Access Protection..."
UNAUTH_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$API_URL/doctors")
if [ "$UNAUTH_RESPONSE" = "401" ] || [ "$UNAUTH_RESPONSE" = "403" ]; then
    check "Unauthorized requests blocked" "PASS"
else
    check "Unauthorized requests blocked" "FAIL"
fi

# 9. Error Handling
echo -e "\n${YELLOW}[9/10]${NC} Error Handling..."
ERROR_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=invalid&password=wrong" -w "%{http_code}" -o /dev/null)
if [ "$ERROR_RESPONSE" = "401" ]; then
    check "Error responses properly formatted" "PASS"
else
    check "Error responses properly formatted" "FAIL"
fi

# 10. Rate Limiting
echo -e "\n${YELLOW}[10/10]${NC} Rate Limiting Headers..."
RATE_RESPONSE=$(curl -s -i -H "Authorization: Bearer $TOKEN" "$API_URL/doctors" | head -20)
if echo "$RATE_RESPONSE" | grep -q "X-Process-Time"; then
    check "Performance headers present" "PASS"
else
    check "Performance headers present" "FAIL"
fi

# Summary
echo -e "\n${BLUE}============================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

PASS_RATE=$((PASSED * 100 / (PASSED + FAILED)))
echo -e "Pass Rate: ${PASS_RATE}%"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ Phase 4 Integration: EXCELLENT${NC}"
    exit 0
elif [ $PASS_RATE -ge 80 ]; then
    echo -e "\n${YELLOW}⚠ Phase 4 Integration: GOOD (minor issues)${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Phase 4 Integration: NEEDS WORK${NC}"
    exit 1
fi
