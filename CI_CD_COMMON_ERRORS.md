# 🐛 CI/CD Common Errors & Prevention Guide

**Purpose:** Document all CI/CD errors encountered and how to prevent them
**Last Updated:** 2025-12-04

---

## ❌ Error 1: Flake8 - Undefined Variable in Lambda

### Error Message:
```
scripts/initialize_rag_system.py:88:48: F821 undefined name 'e'
            'get_stats': lambda: {'error': str(e)}
                                               ^
1     F821 undefined name 'e'
Error: Process completed with exit code 1.
```

### Root Cause:
Lambda function trying to access variable `e` from outer scope (exception handler), but lambda captures variables by reference, not value. When lambda executes later, `e` is out of scope.

### Problem Code:
```python
except Exception as e:
    rag = type('obj', (object,), {
        'get_stats': lambda: {'error': str(e)}  # ❌ e not in lambda scope
    })()
```

### Fixed Code:
```python
except Exception as e:
    error_msg = str(e)  # ✅ Capture value before lambda
    rag = type('obj', (object,), {
        'get_stats': lambda: {'error': error_msg}  # ✅ Use captured value
    })()
```

### Prevention Rules:
1. **Never reference exception variables directly in lambdas**
2. **Always capture values before lambda definition:**
   ```python
   # ❌ BAD
   lambda: str(exception_var)
   
   # ✅ GOOD
   error = str(exception_var)
   lambda: error
   ```
3. **Run flake8 locally before commit:**
   ```bash
   flake8 api/ apps/ scripts/ --select=E9,F63,F7,F82
   ```

### Pre-commit Check:
```bash
# Add to pre-commit hook
flake8 --select=E9,F63,F7,F82 $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
```

---

## ❌ Error 2: Deprecated GitHub Actions (upload-artifact v3)

### Error Message:
```
Error: This request has been automatically failed because it uses a 
deprecated version of `actions/upload-artifact: v3`. 
Learn more: https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/
```

### Root Cause:
GitHub deprecated v3 of upload-artifact and download-artifact actions. Must use v4 or higher.

### Problem Code:
```yaml
- name: Upload Test Results
  uses: actions/upload-artifact@v3  # ❌ Deprecated
  with:
    name: test-results
    path: junit.xml
```

### Fixed Code:
```yaml
- name: Upload Test Results
  uses: actions/upload-artifact@v4  # ✅ Current version
  with:
    name: test-results
    path: junit.xml
```

### All Affected Actions:
```yaml
# Update ALL of these:
actions/upload-artifact@v3   → @v4
actions/download-artifact@v3 → @v4
actions/checkout@v3          → @v4 (recommended)
actions/setup-python@v4      → @v5 (when available)
```

### Prevention Rules:
1. **Always use latest stable versions of GitHub Actions**
2. **Check for deprecation notices in Actions tab**
3. **Use Dependabot to auto-update actions:**

Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Search & Replace Command:
```bash
# Find all v3 actions
grep -r "actions/.*@v3" .github/workflows/

# Replace with sed
sed -i 's/@v3/@v4/g' .github/workflows/*.yml
```

---

## 🔍 Prevention Checklist (Before Every Commit)

### 1. Run Linters Locally:
```bash
# Flake8 (critical errors only)
flake8 api/ apps/ scripts/ --select=E9,F63,F7,F82

# Flake8 (all style issues)
flake8 api/ apps/ scripts/ --max-line-length=127

# Black (code formatter)
black --check api/ apps/ scripts/

# isort (import sorter)
isort --check-only api/ apps/ scripts/
```

### 2. Run Tests Locally:
```bash
# Unit tests
pytest tests/unit/ -v

# With coverage
pytest tests/unit/ --cov=api --cov=apps

# All tests
pytest tests/ -v
```

### 3. Check GitHub Actions YAML:
```bash
# Validate YAML syntax
yamllint .github/workflows/*.yml

# Check for deprecated actions
grep -E "actions/.*@v[123]" .github/workflows/*.yml
```

### 4. Check for Secrets:
```bash
# Check for API keys
git grep -E 'sk-|gsk_|AIza|ghp_' -- '*.py' '*.yml' '*.md'

# Should only show examples/templates
```

---

## 📋 Common Error Patterns

### Pattern 1: Variable Scope in Closures
```python
# ❌ BAD - Variable out of scope
try:
    x = risky_operation()
except Exception as e:
    handler = lambda: f"Error: {e}"  # e may be out of scope

# ✅ GOOD - Capture value
try:
    x = risky_operation()
except Exception as e:
    error_msg = str(e)
    handler = lambda: f"Error: {error_msg}"
```

### Pattern 2: Undefined Variables in F-strings
```python
# ❌ BAD - Variable may not exist
result = f"Value: {undefined_var}"

# ✅ GOOD - Check existence
result = f"Value: {undefined_var if 'undefined_var' in locals() else 'N/A'}"
```

### Pattern 3: Import Errors
```python
# ❌ BAD - Circular import or missing module
from api.services import llm_provider
from api.services.llm_provider import rate_limiter  # circular!

# ✅ GOOD - Import at module level, avoid circular
from api.services import llm_provider
# Use: llm_provider.RateLimiter
```

---

## 🛠️ Automated Prevention

### Pre-commit Hook Script

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Pre-commit checks for Python code

echo "🔍 Running pre-commit checks..."

# Check 1: Flake8 critical errors
echo "→ Checking for critical Python errors..."
if ! flake8 api/ apps/ scripts/ --select=E9,F63,F7,F82 --count; then
    echo "❌ Critical Python errors found! Fix before committing."
    exit 1
fi

# Check 2: Check for secrets
echo "→ Checking for secrets..."
if git diff --cached --name-only | xargs grep -E 'sk-[a-zA-Z0-9]{32,}|AIza[a-zA-Z0-9_-]{35}|gsk_[a-zA-Z0-9]{52}' 2>/dev/null; then
    echo "❌ Potential API key found! Remove before committing."
    exit 1
fi

# Check 3: Check for deprecated actions
echo "→ Checking GitHub Actions..."
if git diff --cached --name-only | grep -q "\.github/workflows" ; then
    if git diff --cached | grep -E "actions/.*@v[123]" ; then
        echo "⚠️  WARNING: Using deprecated GitHub Actions versions"
        echo "   Consider updating to v4 or higher"
    fi
fi

# Check 4: Validate YAML if changed
if git diff --cached --name-only | grep -q "\.yml$\|\.yaml$" ; then
    echo "→ Validating YAML syntax..."
    for file in $(git diff --cached --name-only | grep "\.yml$\|\.yaml$"); do
        if ! python -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            echo "❌ Invalid YAML syntax in $file"
            exit 1
        fi
    done
fi

echo "✅ All pre-commit checks passed!"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 📊 CI/CD Best Practices Summary

### DO:
- ✅ Run linters locally before commit
- ✅ Use latest stable action versions
- ✅ Capture exception values before using in closures
- ✅ Test YAML syntax before pushing
- ✅ Use pre-commit hooks for validation
- ✅ Keep dependencies up to date
- ✅ Document all errors encountered

### DON'T:
- ❌ Reference exception variables in lambdas
- ❌ Use deprecated GitHub Actions versions
- ❌ Skip local testing before commit
- ❌ Ignore flake8 warnings
- ❌ Commit without running linters
- ❌ Use hardcoded values in CI (use env vars)
- ❌ Forget to update documentation

---

## 🔗 References

- **Flake8 Error Codes:** https://flake8.pycqa.org/en/latest/user/error-codes.html
- **GitHub Actions Changelog:** https://github.blog/changelog/
- **Python Lambda Gotchas:** https://docs.python-guide.org/writing/gotchas/#late-binding-closures
- **GitHub Actions Deprecations:** https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/

---

## 📝 Error Log

Track all CI/CD errors here:

| Date | Error | Fix | Commit |
|------|-------|-----|--------|
| 2025-12-04 | F821 undefined name 'e' in lambda | Captured exception value before lambda | Next commit |
| 2025-12-04 | Deprecated upload-artifact@v3 | Updated to @v4 | Next commit |

---

**Maintained by:** Development Team
**Review Frequency:** After every CI/CD error
**Next Review:** When new errors occur
