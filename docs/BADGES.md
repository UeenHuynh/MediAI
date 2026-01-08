# MediAI Badges Reference

This document tracks all badges used in README.md and their status.

**Last Updated:** 2026-01-08

---

## 🎯 Current Badges (README.md)

### Core Technology Stack
```markdown
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

### Deployment & Status
```markdown
[![Deployment](https://img.shields.io/badge/deployment-live-success.svg)](https://mediai-frontend-five.vercel.app)
[![Backend Status](https://img.shields.io/badge/backend-healthy-success.svg)](https://mediai-7owz.onrender.com/health)
```

### Security Badges
```markdown
[![Security Score](https://img.shields.io/badge/security%20score-60%25→100%25-orange.svg)](docs/SECURITY_AND_TESTING_PLAN.md)
[![Known Vulnerabilities](https://img.shields.io/badge/vulnerabilities-scanning-yellow.svg)](https://github.com/UeenHuynh/MediAI/security)
[![OWASP](https://img.shields.io/badge/OWASP-Top%2010-blue.svg)](https://owasp.org/www-project-top-ten/)
[![HIPAA](https://img.shields.io/badge/HIPAA-compliant-green.svg)](docs/SECURITY_AND_TESTING_PLAN.md)
```

### Code Quality & Testing
```markdown
[![Code Coverage](https://img.shields.io/badge/coverage-30%25→80%25-orange.svg)](docs/SECURITY_AND_TESTING_PLAN.md)
[![Tests](https://img.shields.io/badge/tests-planning-yellow.svg)](docs/SECURITY_AND_TESTING_PLAN.md)
[![Code Quality](https://img.shields.io/badge/quality-B→A+-orange.svg)](docs/SECURITY_AND_TESTING_PLAN.md)
```

---

## 🔄 Badge Evolution Plan (Phase 10)

### Week 1: Security Hardening

**After Day 2 (SonarCloud Integration):**
```markdown
<!-- Replace static badge with dynamic SonarCloud badge -->
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=UeenHuynh_MediAI&metric=alert_status)](https://sonarcloud.io/dashboard?id=UeenHuynh_MediAI)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=UeenHuynh_MediAI&metric=security_rating)](https://sonarcloud.io/dashboard?id=UeenHuynh_MediAI)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=UeenHuynh_MediAI&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=UeenHuynh_MediAI)
```

**After Day 1 (Snyk Integration):**
```markdown
[![Known Vulnerabilities](https://snyk.io/test/github/UeenHuynh/MediAI/badge.svg)](https://snyk.io/test/github/UeenHuynh/MediAI)
```

### Week 2: Testing Enhancement

**After Day 6 (Coverage Integration):**
```markdown
[![codecov](https://codecov.io/gh/UeenHuynh/MediAI/branch/main/graph/badge.svg)](https://codecov.io/gh/UeenHuynh/MediAI)
```

**Or with Coveralls:**
```markdown
[![Coverage Status](https://coveralls.io/repos/github/UeenHuynh/MediAI/badge.svg?branch=main)](https://coveralls.io/github/UeenHuynh/MediAI?branch=main)
```

### Week 3: CI/CD Integration

**After Day 11 (GitHub Actions):**
```markdown
[![CI](https://github.com/UeenHuynh/MediAI/workflows/CI/badge.svg)](https://github.com/UeenHuynh/MediAI/actions)
[![Security Scan](https://github.com/UeenHuynh/MediAI/workflows/Security%20Scan/badge.svg)](https://github.com/UeenHuynh/MediAI/actions)
[![Tests](https://github.com/UeenHuynh/MediAI/workflows/Tests/badge.svg)](https://github.com/UeenHuynh/MediAI/actions)
```

---

## 🎯 Target Badge Suite (After Phase 10)

### Final README.md Badges

```markdown
# MediAI - ICU Risk Prediction Platform V4

<!-- Core Stack -->
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- Deployment -->
[![Deployment](https://img.shields.io/badge/deployment-live-success.svg)](https://mediai-frontend-five.vercel.app)
[![Backend Status](https://img.shields.io/badge/backend-healthy-success.svg)](https://mediai-7owz.onrender.com/health)

<!-- CI/CD -->
[![CI](https://github.com/UeenHuynh/MediAI/workflows/CI/badge.svg)](https://github.com/UeenHuynh/MediAI/actions)
[![Security Scan](https://github.com/UeenHuynh/MediAI/workflows/Security%20Scan/badge.svg)](https://github.com/UeenHuynh/MediAI/actions)

<!-- Security -->
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=UeenHuynh_MediAI&metric=alert_status)](https://sonarcloud.io/dashboard?id=UeenHuynh_MediAI)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=UeenHuynh_MediAI&metric=security_rating)](https://sonarcloud.io/dashboard?id=UeenHuynh_MediAI)
[![Known Vulnerabilities](https://snyk.io/test/github/UeenHuynh/MediAI/badge.svg)](https://snyk.io/test/github/UeenHuynh/MediAI)
[![OWASP](https://img.shields.io/badge/OWASP-Top%2010%20✓-success.svg)](docs/SECURITY_AND_TESTING_PLAN.md)
[![HIPAA](https://img.shields.io/badge/HIPAA-compliant-green.svg)](docs/SECURITY_AND_TESTING_PLAN.md)

<!-- Code Quality & Testing -->
[![codecov](https://codecov.io/gh/UeenHuynh/MediAI/branch/main/graph/badge.svg)](https://codecov.io/gh/UeenHuynh/MediAI)
[![Code Quality](https://sonarcloud.io/api/project_badges/measure?project=UeenHuynh_MediAI&metric=code_smells)](https://sonarcloud.io/dashboard?id=UeenHuynh_MediAI)
[![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=UeenHuynh_MediAI&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=UeenHuynh_MediAI)
```

---

## 📊 Badge Status Tracking

| Badge Type | Status | Current Value | Target Value | ETA |
|------------|--------|---------------|--------------|-----|
| **Security Rating** | 🟡 Planning | 60% (B) | 100% (A+) | Week 1 |
| **Vulnerabilities** | 🟡 Unknown | Unknown | 0 High/Critical | Week 1 |
| **Code Coverage** | 🟡 Low | 30% | 80%+ | Week 2 |
| **Quality Gate** | ⚫ None | N/A | PASSED | Week 1 |
| **CI/CD** | ⚫ None | Manual | Automated | Week 3 |
| **Tests** | 🟡 Partial | ~30 tests | 280+ tests | Week 2-3 |
| **OWASP** | 🟡 Partial | Partial | Full Coverage | Week 1 |

**Legend:**
- ✅ Green: Target achieved
- 🟡 Yellow: In progress or needs improvement
- ⚫ None: Not yet implemented

---

## 🔧 How to Update Badges

### 1. SonarCloud Setup
```bash
# Sign up at https://sonarcloud.io
# Connect GitHub repo
# Get project key: UeenHuynh_MediAI
# Add SONAR_TOKEN to GitHub Secrets
```

### 2. Snyk Setup
```bash
# Sign up at https://snyk.io
# Connect GitHub repo
# Badge auto-generated at:
# https://snyk.io/test/github/UeenHuynh/MediAI
```

### 3. Codecov Setup
```bash
# Sign up at https://codecov.io
# Connect GitHub repo
# Add CODECOV_TOKEN to GitHub Secrets
# Badge URL: https://codecov.io/gh/UeenHuynh/MediAI
```

### 4. GitHub Actions Badges
```bash
# Automatically generated after workflow creation
# Format: https://github.com/{user}/{repo}/workflows/{workflow}/badge.svg
# Example: https://github.com/UeenHuynh/MediAI/workflows/CI/badge.svg
```

---

## 📝 Badge Color Scheme

### Security Badges
- 🔴 Red (`critical`): <40% security score, high vulnerabilities
- 🟡 Orange/Yellow (`orange`, `yellow`): 40-79% security score, medium vulnerabilities
- 🟢 Green (`success`): 80%+ security score, 0 high vulnerabilities

### Testing Badges
- 🔴 Red: <50% coverage
- 🟡 Yellow: 50-79% coverage
- 🟢 Green: 80%+ coverage

### CI/CD Badges
- 🟢 Green: Passing
- 🔴 Red: Failing
- ⚪ Gray: N/A or in progress

---

## 🎨 Custom Badge Generator

Use [shields.io](https://shields.io/) for custom badges:

```
https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>.svg
```

**Examples:**
```markdown
![Security](https://img.shields.io/badge/security-A+-success.svg)
![Coverage](https://img.shields.io/badge/coverage-85%25-success.svg)
![Tests](https://img.shields.io/badge/tests-280%20passed-success.svg)
```

---

**Document Version:** 1.0
**Last Updated:** 2026-01-08
**Next Review:** After Phase 10 completion (Jan 28, 2026)
