# Security & Testing Enhancement Plan

**MediAI Security Hardening and Test Coverage Improvement**

Version: 1.0
Date: 2026-01-08
Status: 📋 Planning

---

## 🎯 Objectives

### Security Goals
- Achieve **A+ Security Rating** on SonarCloud
- Pass **Snyk vulnerability scan** (0 high/critical vulnerabilities)
- Implement **OWASP Top 10** protections
- Achieve **OpenSSF Best Practices Badge** (passing level)

### Testing Goals
- Increase test coverage from **~30%** → **80%+**
- Implement **CI/CD pipeline** with automated testing
- Add **security testing** to CI pipeline
- Achieve **100% API endpoint coverage**

---

## 📊 Current Status Assessment

### ✅ Security - Already Implemented (60%)

| Feature | Status | Details |
|---------|--------|---------|
| Password Hashing | ✅ | bcrypt with salt (rounds=12) |
| JWT Authentication | ✅ | HS256, 30min expiry |
| RBAC | ✅ | Role-based permissions |
| SQL Injection Prevention | ✅ | SQLAlchemy ORM (parameterized queries) |
| Rate Limiting | ✅ | slowapi (100 req/min) |
| CORS Protection | ✅ | Configured origins |
| PII Encryption | ✅ | AES-256 for sensitive data |
| Database SSL | ✅ | Neon PostgreSQL (sslmode=require) |

### ⚠️ Security - Missing (40%)

| Feature | Priority | Effort |
|---------|----------|--------|
| Dependency Scanning | 🔴 High | 1 day |
| SAST Integration | 🔴 High | 1 day |
| Secret Scanning | 🔴 High | 4 hours |
| Security Headers | 🟡 Medium | 4 hours |
| Input Validation | 🟡 Medium | 2 days |
| API Key Rotation | 🟡 Medium | 1 day |
| Audit Logging | 🟢 Low | 2 days |
| Penetration Testing | 🟢 Low | 3 days |

### ✅ Testing - Current Coverage (~30%)

| Category | Coverage | Files |
|----------|----------|-------|
| Unit Tests | ~20% | Few auth tests |
| Integration Tests | ~50% | Some API tests |
| E2E Tests | 0% | None |
| Security Tests | 0% | None |
| Performance Tests | 0% | None |

---

## 🔒 Phase 1: Security Hardening (Week 1)

### Day 1: Dependency Security

**Tasks:**
1. ✅ Add Snyk to GitHub repo
2. ✅ Configure GitHub Dependabot
3. ✅ Add Safety check to CI
4. ✅ Create requirements-security.txt

**Implementation:**

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: Run Safety check
        run: |
          pip install safety
          safety check --file api/requirements.txt --json
```

**Validation:**
- ✅ No high/critical vulnerabilities
- ✅ Dependabot alerts enabled
- ✅ Security badge in README

---

### Day 2: Static Application Security Testing (SAST)

**Tasks:**
1. ✅ Integrate SonarCloud
2. ✅ Configure Bandit (Python SAST)
3. ✅ Add pre-commit hooks
4. ✅ Fix all high-priority issues

**Implementation:**

```yaml
# .github/workflows/sast.yml
name: SAST

on: [push, pull_request]

jobs:
  sonarcloud:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

  bandit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r api/ -f json -o bandit-report.json
          bandit -r api/ -ll  # Show medium/high severity
```

**SonarCloud Configuration:**

```properties
# sonar-project.properties
sonar.projectKey=UeenHuynh_MediAI
sonar.organization=ueenhuynh

sonar.sources=api
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.version=3.11

# Exclusions
sonar.exclusions=**/migrations/**,**/tests/**,**/__pycache__/**
```

**Validation:**
- ✅ SonarCloud Quality Gate: PASSED
- ✅ Security Rating: A
- ✅ 0 vulnerabilities

---

### Day 3: Secret Scanning & Security Headers

**Tasks:**
1. ✅ Add GitGuardian/TruffleHog
2. ✅ Implement security headers middleware
3. ✅ Audit environment variables
4. ✅ Add .env.example with safe defaults

**Security Headers:**

```python
# api/core/security_headers.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # OWASP recommended headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response
```

**Secret Scanning:**

```yaml
# .github/workflows/secret-scan.yml
name: Secret Scan

on: [push, pull_request]

jobs:
  trufflehog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: TruffleHog OSS
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

**Validation:**
- ✅ No secrets in git history
- ✅ All security headers present
- ✅ A+ rating on securityheaders.com

---

### Day 4: Input Validation & API Security

**Tasks:**
1. ✅ Add comprehensive Pydantic validation
2. ✅ Implement request sanitization
3. ✅ Add API request size limits
4. ✅ Enhance rate limiting per endpoint

**Enhanced Validation:**

```python
# api/models/schemas.py - Enhanced validation
from pydantic import BaseModel, Field, validator, constr
from typing import Optional
import re

class PatientCreateRequest(BaseModel):
    # Strict validation
    first_name: constr(min_length=1, max_length=100, strip_whitespace=True)
    last_name: constr(min_length=1, max_length=100, strip_whitespace=True)
    date_of_birth: date

    # Email validation
    email: Optional[EmailStr] = None

    # Phone validation
    phone: Optional[constr(regex=r'^\+?[1-9]\d{1,14}$')] = None

    # SSN validation (encrypted)
    ssn: Optional[constr(regex=r'^\d{3}-\d{2}-\d{4}$')] = None

    @validator('date_of_birth')
    def validate_dob(cls, v):
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        if v < date(1900, 1, 1):
            raise ValueError('Date of birth too far in the past')
        return v

    @validator('ssn')
    def validate_ssn(cls, v):
        # Prevent test SSNs (000-xx-xxxx, etc.)
        if v and v.startswith('000'):
            raise ValueError('Invalid SSN')
        return v

class Config:
    # Prevent extra fields
    extra = 'forbid'
```

**Request Size Limits:**

```python
# api/main.py
from fastapi import Request, HTTPException

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    # Limit request body to 10MB
    MAX_REQUEST_SIZE = 10 * 1024 * 1024

    content_length = request.headers.get('content-length')
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        raise HTTPException(status_code=413, detail="Request too large")

    return await call_next(request)
```

**Validation:**
- ✅ All endpoints have strict validation
- ✅ Malformed requests rejected (400)
- ✅ Request size limits enforced

---

## 🧪 Phase 2: Test Coverage Enhancement (Week 2)

### Day 5-6: Unit Tests (Target: 80% coverage)

**Test Structure:**

```
tests/
├── unit/
│   ├── test_auth.py           # Authentication logic
│   ├── test_rbac.py            # Role-based access control
│   ├── test_encryption.py      # PII encryption
│   ├── test_prediction.py      # ML prediction service
│   ├── test_chat_service.py    # Chat session management
│   └── test_validators.py      # Input validation
├── integration/
│   ├── test_api_auth.py        # Auth endpoints
│   ├── test_api_patients.py    # Patient API
│   ├── test_api_predictions.py # Prediction API
│   └── test_api_chat.py        # Chat API
├── e2e/
│   ├── test_user_flow.py       # Complete user workflows
│   └── test_chat_flow.py       # Chat conversation flow
└── security/
    ├── test_sql_injection.py   # SQL injection tests
    ├── test_xss.py              # XSS prevention tests
    └── test_auth_bypass.py     # Auth bypass tests
```

**Unit Test Example:**

```python
# tests/unit/test_encryption.py
import pytest
from core.encryption import encrypt_pii, decrypt_pii

class TestPIIEncryption:
    """Test PII encryption/decryption"""

    def test_encrypt_decrypt_ssn(self):
        """Test SSN encryption round-trip"""
        original = "123-45-6789"
        encrypted = encrypt_pii(original)
        decrypted = decrypt_pii(encrypted)

        assert encrypted != original, "Encrypted value should differ"
        assert decrypted == original, "Decryption should restore original"

    def test_encryption_is_deterministic(self):
        """Test same input produces same output"""
        ssn = "123-45-6789"
        encrypted1 = encrypt_pii(ssn)
        encrypted2 = encrypt_pii(ssn)

        # Should be deterministic for database queries
        assert encrypted1 == encrypted2

    def test_different_inputs_produce_different_outputs(self):
        """Test different inputs produce different encrypted values"""
        ssn1 = "123-45-6789"
        ssn2 = "987-65-4321"

        encrypted1 = encrypt_pii(ssn1)
        encrypted2 = encrypt_pii(ssn2)

        assert encrypted1 != encrypted2

    def test_empty_string_handling(self):
        """Test empty string encryption"""
        with pytest.raises(ValueError):
            encrypt_pii("")

    def test_none_handling(self):
        """Test None value handling"""
        assert encrypt_pii(None) is None
```

**Coverage Configuration:**

```ini
# .coveragerc
[run]
source = api
omit =
    */tests/*
    */migrations/*
    */__pycache__/*
    */venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:

[html]
directory = htmlcov
```

**CI Integration:**

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: mediai_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r api/requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/mediai_test
          ENABLE_DATABASE: true
        run: |
          pytest tests/ \
            --cov=api \
            --cov-report=xml \
            --cov-report=html \
            --cov-report=term \
            --cov-fail-under=80

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

**Validation:**
- ✅ 80%+ code coverage
- ✅ All critical paths tested
- ✅ Coverage badge in README

---

### Day 7: Integration & E2E Tests

**Integration Test Example:**

```python
# tests/integration/test_api_chat.py
import pytest
from fastapi.testclient import TestClient
from main import app

class TestChatAPI:
    """Test chat API endpoints"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def auth_token(self, client):
        """Get auth token for tests"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "demo", "password": "demo123"}
        )
        return response.json()["access_token"]

    def test_send_message_success(self, client, auth_token):
        """Test successful message send"""
        response = client.post(
            "/api/v1/chat",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"message": "What is sepsis?", "include_sources": true}
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "session_id" in data
        assert len(data["answer"]) > 0

    def test_send_message_unauthorized(self, client):
        """Test message send without auth"""
        response = client.post(
            "/api/v1/chat",
            json={"message": "What is sepsis?"}
        )

        assert response.status_code == 401

    def test_conversation_history(self, client, auth_token):
        """Test full conversation flow"""
        # Send first message
        response1 = client.post(
            "/api/v1/chat",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"message": "What is sepsis?"}
        )
        session_id = response1.json()["session_id"]

        # Send follow-up message
        response2 = client.post(
            "/api/v1/chat",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"message": "What are the symptoms?", "session_id": session_id}
        )

        # Get conversation history
        response3 = client.get(
            f"/api/v1/chat/history/{session_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response3.status_code == 200
        history = response3.json()
        assert len(history["messages"]) == 4  # 2 user + 2 assistant
```

**E2E Test Example:**

```python
# tests/e2e/test_user_flow.py
import pytest
from playwright.sync_api import Page, expect

class TestCompleteUserFlow:
    """End-to-end user flow tests"""

    def test_complete_prediction_workflow(self, page: Page):
        """Test complete prediction workflow from login to result"""

        # 1. Login
        page.goto("https://mediai-frontend.vercel.app")
        page.fill('[name="username"]', 'demo')
        page.fill('[name="password"]', 'demo123')
        page.click('button[type="submit"]')

        # 2. Navigate to predictions
        expect(page).to_have_url("/dashboard")
        page.click('text=Predictions')

        # 3. Create new prediction
        page.click('text=New Prediction')
        page.fill('[name="patient_id"]', 'P001')
        page.fill('[name="heart_rate"]', '110')
        page.fill('[name="blood_pressure_systolic"]', '85')
        page.click('button:has-text("Calculate Risk")')

        # 4. Verify result
        expect(page.locator('.prediction-result')).to_be_visible()
        expect(page.locator('.risk-score')).to_contain_text('%')
```

**Validation:**
- ✅ All API endpoints tested
- ✅ E2E workflows covered
- ✅ CI passes all tests

---

## 🛡️ Phase 3: Security Testing (Week 3)

### Security Test Suite

```python
# tests/security/test_sql_injection.py
import pytest
from fastapi.testclient import TestClient

class TestSQLInjection:
    """Test SQL injection prevention"""

    def test_sql_injection_in_patient_search(self, client, auth_token):
        """Test SQL injection in search endpoint"""
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE patients; --",
            "1' UNION SELECT * FROM users--",
        ]

        for payload in payloads:
            response = client.get(
                f"/api/v1/patients?search={payload}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )

            # Should return 400 or 422, not 500 or data leak
            assert response.status_code in [400, 422]

# tests/security/test_xss.py
class TestXSSPrevention:
    """Test XSS prevention"""

    def test_xss_in_chat_message(self, client, auth_token):
        """Test XSS script injection in chat"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
        ]

        for payload in xss_payloads:
            response = client.post(
                "/api/v1/chat",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"message": payload}
            )

            # Should sanitize or reject
            assert response.status_code in [200, 400]
            if response.status_code == 200:
                data = response.json()
                # Ensure script tags are escaped
                assert "<script>" not in data["answer"]

# tests/security/test_auth_bypass.py
class TestAuthBypass:
    """Test authentication bypass attempts"""

    def test_jwt_signature_bypass(self, client):
        """Test JWT signature verification"""
        fake_token = "eyJhbGciOiJub25lIn0.eyJzdWIiOiJhZG1pbiJ9."

        response = client.get(
            "/api/v1/patients",
            headers={"Authorization": f"Bearer {fake_token}"}
        )

        assert response.status_code == 401

    def test_expired_token(self, client):
        """Test expired token rejection"""
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZW1vIiwiZXhwIjoxfQ.xxx"

        response = client.get(
            "/api/v1/patients",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
```

---

## 📈 Success Metrics

### Security Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| SonarCloud Quality Gate | N/A | PASSED | 🎯 |
| Security Rating | N/A | A | 🎯 |
| Vulnerabilities | Unknown | 0 High/Critical | 🎯 |
| Code Smells | Unknown | <50 | 🎯 |
| Technical Debt | Unknown | <1 day | 🎯 |
| Snyk Score | N/A | 90+ | 🎯 |
| OWASP Top 10 | Partial | Full Coverage | 🎯 |

### Testing Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Code Coverage | ~30% | 80%+ | 🎯 |
| Unit Tests | ~20 | 200+ | 🎯 |
| Integration Tests | ~10 | 50+ | 🎯 |
| E2E Tests | 0 | 10+ | 🎯 |
| Security Tests | 0 | 20+ | 🎯 |
| API Coverage | ~50% | 100% | 🎯 |

---

## 🚀 Implementation Timeline

```mermaid
gantt
    title Security & Testing Enhancement
    dateFormat  YYYY-MM-DD

    section Week 1: Security
    Dependency Scanning       :2026-01-08, 1d
    SAST Integration         :2026-01-09, 1d
    Secret Scanning          :2026-01-10, 1d
    Input Validation         :2026-01-11, 2d

    section Week 2: Testing
    Unit Tests              :2026-01-13, 2d
    Integration Tests       :2026-01-15, 1d
    E2E Tests              :2026-01-16, 1d

    section Week 3: Security Testing
    Security Test Suite     :2026-01-17, 2d
    Penetration Testing     :2026-01-19, 1d
    Documentation          :2026-01-20, 1d
```

**Total Effort:** ~15 days (3 weeks)
**Team:** 1 developer
**Risk:** Low (incremental changes, comprehensive testing)

---

## ✅ Validation Checklist

### Before Deployment

- [ ] All tests passing (unit, integration, e2e)
- [ ] Coverage ≥ 80%
- [ ] SonarCloud Quality Gate: PASSED
- [ ] Snyk scan: 0 high/critical vulnerabilities
- [ ] Bandit scan: 0 high severity issues
- [ ] Secret scan: PASSED
- [ ] Security headers: A+ rating
- [ ] All OWASP Top 10 mitigated
- [ ] Documentation updated
- [ ] Badges added to README

### Post-Deployment

- [ ] Monitor error rates (should be <0.1%)
- [ ] Monitor response times (should be <500ms p95)
- [ ] Check security dashboard weekly
- [ ] Review Snyk alerts daily
- [ ] Update dependencies monthly

---

## 📚 References

- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [OpenSSF Best Practices](https://bestpractices.coreinfrastructure.org/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-08
**Next Review:** 2026-02-08
