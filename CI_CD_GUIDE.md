# CI/CD Pipeline Guide - MediAI Advanced Chatbot

**Branch:** `improve-chatbot`
**CI/CD Platform:** GitHub Actions
**Quality Gate:** SonarQube
**Testing:** Pytest + Coverage

---

## 📋 Table of Contents
1. [Pipeline Overview](#pipeline-overview)
2. [GitHub Actions Setup](#github-actions-setup)
3. [SonarQube Integration](#sonarqube-integration)
4. [Testing Strategy](#testing-strategy)
5. [Security Scanning](#security-scanning)
6. [Deployment Process](#deployment-process)
7. [Quality Standards](#quality-standards)

---

## 🔄 Pipeline Overview

### CI/CD Workflow Stages

```
┌─────────────────────────────────────────────────────────────┐
│                    PUSH TO BRANCH                            │
│           (main, develop, improve-chatbot)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────┐          ┌──────▼───────┐
│  Code Quality │          │   Security   │
│     Check     │          │     Scan     │
│               │          │              │
│ • Black       │          │ • Bandit     │
│ • isort       │          │ • Safety     │
│ • Flake8      │          │              │
│ • Pylint      │          │              │
└───────┬───────┘          └──────┬───────┘
        │                         │
        └────────────┬────────────┘
                     │
            ┌────────▼────────┐
            │   Unit Tests    │
            │  (Python 3.9,   │
            │   3.10, 3.11)   │
            │                 │
            │ • pytest        │
            │ • coverage      │
            └────────┬────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌────────▼────────┐
│   SonarQube     │    │  Integration    │
│     Scan        │    │     Tests       │
│                 │    │                 │
│ • Code Quality  │    │ • DB Tests      │
│ • Coverage      │    │ • API Tests     │
│ • Vulnerabilities│   │ • E2E Tests     │
└────────┬────────┘    └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │   Deploy    │
              │ (main only) │
              │             │
              │ Production  │
              └─────────────┘
```

---

## 🔧 GitHub Actions Setup

### 1. Repository Secrets

Navigate to: **Settings → Secrets and variables → Actions**

Add the following secrets:

```bash
# Required for testing
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
QDRANT_URL=https://xxxxx.cloud.qdrant.io
QDRANT_API_KEY=xxxxxxxxxxxxx

# Required for SonarQube
SONAR_TOKEN=squ_xxxxxxxxxxxxx
SONAR_HOST_URL=https://sonarcloud.io  # or your SonarQube instance

# Optional for deployment
DEPLOY_KEY=xxxxxxxxxxxxx
```

### 2. Workflow Configuration

File: `.github/workflows/ci-cd.yml`

**Triggers:**
- Push to: `main`, `develop`, `improve-chatbot`
- Pull requests to: `main`, `develop`

**Jobs:**
1. **lint**: Code quality checks
2. **security**: Security vulnerability scanning
3. **test**: Unit tests across Python versions
4. **sonarqube**: SonarQube analysis
5. **integration**: Integration tests with PostgreSQL
6. **deploy**: Production deployment (main branch only)

---

## 📊 SonarQube Integration

### Setup SonarCloud (Free for Open Source)

#### Step 1: Create SonarCloud Account
```bash
# Go to: https://sonarcloud.io/
# Sign in with GitHub
# Import your repository
```

#### Step 2: Get Token
```bash
# SonarCloud → My Account → Security
# Generate token
# Add to GitHub Secrets as SONAR_TOKEN
```

#### Step 3: Configuration
File: `sonar-project.properties`

```properties
sonar.projectKey=mediai-advanced-chatbot
sonar.projectName=MediAI Advanced Chatbot
sonar.projectVersion=2.0.0

sonar.sources=api,apps
sonar.tests=tests
sonar.python.version=3.11

sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=junit.xml
```

### Quality Gates

**Minimum Standards:**
- Code Coverage: ≥ 80%
- Duplicated Code: < 3%
- Maintainability Rating: A
- Reliability Rating: A
- Security Rating: A
- Security Hotspots: Reviewed

### SonarQube Metrics Tracked

| Metric | Target | Description |
|--------|--------|-------------|
| Coverage | ≥ 80% | Unit test coverage |
| Duplications | < 3% | Code duplication |
| Bugs | 0 | Reliability issues |
| Vulnerabilities | 0 | Security issues |
| Code Smells | < 50 | Maintainability issues |
| Cognitive Complexity | < 15 | Code complexity |

---

## 🧪 Testing Strategy

### Test Structure

```
tests/
├── __init__.py
├── unit/                    # Fast, isolated tests
│   ├── test_llm_provider.py
│   ├── test_pii_masker.py
│   ├── test_rate_limiter.py
│   └── test_rag_pipeline.py
├── integration/             # Slower, with dependencies
│   ├── test_database.py
│   ├── test_qdrant.py
│   ├── test_groq_api.py
│   └── test_full_pipeline.py
└── e2e/                     # End-to-end tests
    └── test_chatbot_flow.py
```

### Test Markers

```python
@pytest.mark.unit          # Fast unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.slow          # Slow running tests
@pytest.mark.api           # Requires external API
@pytest.mark.database      # Requires database
@pytest.mark.llm           # Requires LLM API
@pytest.mark.rag           # RAG system tests
@pytest.mark.pii           # PII masking tests
@pytest.mark.agent         # Agent orchestrator tests
```

### Running Tests Locally

```bash
# All tests
pytest

# Only unit tests (fast)
pytest -m unit

# Only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# With coverage
pytest --cov=api --cov=apps --cov-report=html

# Specific test file
pytest tests/unit/test_pii_masker.py -v

# Parallel execution (faster)
pytest -n auto
```

### Coverage Requirements

**Minimum Coverage by Module:**
- `api/services/`: ≥ 85%
- `api/core/`: ≥ 80%
- `api/agents/`: ≥ 75%
- Overall: ≥ 80%

---

## 🔒 Security Scanning

### Tools Used

#### 1. Bandit (Python Security Linter)
```bash
# Run locally
bandit -r api/ apps/ -f json -o bandit-report.json

# Check for high severity issues
bandit -r api/ apps/ -ll
```

**Checks:**
- SQL injection vulnerabilities
- Hard-coded secrets
- Unsafe deserialization
- Command injection
- Path traversal

#### 2. Safety (Dependency Vulnerability Scanner)
```bash
# Check for vulnerable dependencies
safety check

# Generate JSON report
safety check --json
```

**Monitors:**
- Known CVEs in dependencies
- Outdated packages with security fixes
- License violations

### Security Best Practices

✅ **Implemented:**
- No secrets in code (use environment variables)
- Input validation and sanitization
- PII masking before LLM processing
- SQL injection prevention (parameterized queries)
- Rate limiting on APIs
- Secure credential storage

---

## 🚀 Deployment Process

### Automatic Deployment (Main Branch)

**Triggered when:**
- Push to `main` branch
- All quality gates pass

**Steps:**
1. ✅ Code quality checks pass
2. ✅ Security scan clean
3. ✅ All tests pass (unit + integration)
4. ✅ SonarQube quality gate pass
5. 🚀 Deploy to production

### Manual Deployment

```bash
# 1. Build application
pip install -r requirements.txt
pip install -r requirements.chatbot.txt
python -m spacy download en_core_web_sm

# 2. Run pre-deployment tests
./scripts/run_phase1_tests.sh

# 3. Deploy
./scripts/deploy.sh  # Your deployment script
```

### Deployment Checklist

- [ ] All tests passing locally
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] API keys valid
- [ ] Monitoring enabled
- [ ] Backup completed
- [ ] Rollback plan ready

---

## ⚙️ Quality Standards

### Code Style

**Enforced by:**
- **Black**: Code formatter
- **isort**: Import sorter
- **Flake8**: Style guide enforcement
- **Pylint**: Static analysis

**Configuration:**
```bash
# Format code
black api/ apps/ scripts/

# Sort imports
isort api/ apps/ scripts/

# Check style
flake8 api/ apps/ scripts/

# Lint code
pylint api/
```

### Code Review Standards

**Required for PR Approval:**
- [ ] All CI checks pass
- [ ] Code coverage ≥ 80%
- [ ] No security vulnerabilities
- [ ] SonarQube quality gate passed
- [ ] Documentation updated
- [ ] Tests added for new features
- [ ] At least 1 reviewer approval

### Git Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

**Example:**
```
feat: Add PII masking service for HIPAA compliance

Implement comprehensive PII detection using:
- Regex patterns for email, phone, SSN
- spaCy NER for name detection
- Session-based token mapping

Resolves #123
```

---

## 📈 Monitoring & Alerts

### GitHub Actions Badges

Add to `README.md`:

```markdown
![CI/CD](https://github.com/your-org/mediai/workflows/CI-CD%20Pipeline/badge.svg)
![Coverage](https://codecov.io/gh/your-org/mediai/branch/main/graph/badge.svg)
![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=mediai&metric=alert_status)
```

### Notifications

**Configured in GitHub:**
- Failed builds → Email notification
- Security alerts → Immediate email
- Deployment success → Slack webhook (optional)

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Tests Failing in CI but Pass Locally
```bash
# Likely cause: Environment variables missing
# Solution: Add secrets in GitHub repo settings
```

#### 2. SonarQube Quality Gate Failing
```bash
# Check coverage
pytest --cov=api --cov=apps --cov-report=term

# Fix code smells
pylint api/ --disable=C,R  # Check only errors
```

#### 3. Security Scan Failing
```bash
# Run locally
bandit -r api/ apps/ -ll

# Fix vulnerabilities, then commit
```

---

## 📚 References

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [SonarCloud](https://sonarcloud.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Bandit Security Linter](https://bandit.readthedocs.io/)
- [Safety](https://github.com/pyupio/safety)

---

**Last Updated:** 2025-12-04
**Maintained By:** Development Team
**Status:** ✅ Active & Monitored
