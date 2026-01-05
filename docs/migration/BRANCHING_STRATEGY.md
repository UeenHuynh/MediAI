# Branching Strategy: V2 Migration + Self-Hosted Deployment

**Model:** Trunk-Based Development with Release Branches
**Deployment Target:** Self-hosted VPS (4GB RAM, 4 cores recommended)
**CI/CD:** GitHub Actions
**Version Control:** Git + GitHub

---

## 📐 BRANCHING MODEL

```
main (production - deployed to VPS)
│
├── develop (integration branch - staging environment)
│   │
│   ├── feature/phase0-foundation
│   │   ├── feat/ci-cd-pipeline
│   │   ├── feat/pre-commit-hooks
│   │   ├── feat/baseline-metrics
│   │   └── feat/deployment-scripts
│   │
│   ├── feature/phase1-api-contracts
│   │   ├── feat/openapi-spec
│   │   ├── feat/mock-server
│   │   └── feat/contract-tests
│   │
│   ├── feature/phase2-frontend
│   │   ├── feat/nextjs-setup
│   │   ├── feat/glassmorphism-ui
│   │   ├── feat/msw-mocks
│   │   └── feat/storybook
│   │
│   ├── feature/phase3-backend
│   │   ├── feat/fastapi-refactor
│   │   ├── feat/api-validation
│   │   └── feat/auth-improvements
│   │
│   ├── feature/learning-features (optional)
│   │   ├── feat/kafka-streaming
│   │   ├── feat/timescaledb
│   │   ├── feat/duckdb-analytics
│   │   └── feat/advanced-caching
│   │
│   └── feature/deployment
│       ├── feat/nginx-config
│       ├── feat/ssl-certificates
│       ├── feat/monitoring-stack
│       └── feat/backup-automation
│
├── release/v2.0.0 (release candidate)
│   └── (cherry-picked fixes from develop)
│
└── hotfix/* (emergency fixes to production)
    └── hotfix/security-patch-xxx
```

---

## 🏷️ BRANCH NAMING CONVENTION

### Primary Branches

| Branch | Purpose | Lifespan | Deployed To | Protected |
|--------|---------|----------|-------------|-----------|
| `main` | Production-ready code | Permanent | VPS Production | ✅ Yes |
| `develop` | Integration branch | Permanent | Local/Staging | ✅ Yes |
| `release/v*` | Release candidates | Until merged | VPS Staging | ✅ Yes |

### Supporting Branches

| Type | Pattern | Example | Lifespan | Merged Into |
|------|---------|---------|----------|-------------|
| Feature | `feature/phase{N}-{name}` | `feature/phase1-api-contracts` | Until complete | `develop` |
| Sub-feature | `feat/{short-name}` | `feat/nextjs-setup` | <2 days | parent `feature/*` |
| Hotfix | `hotfix/{issue}` | `hotfix/memory-leak` | <1 day | `main` + `develop` |
| Bugfix | `fix/{issue}` | `fix/cache-invalidation` | <1 day | `develop` |
| Chore | `chore/{task}` | `chore/update-deps` | <1 day | `develop` |
| Docs | `docs/{topic}` | `docs/api-reference` | <1 day | `develop` |

---

## 🔒 BRANCH PROTECTION RULES

### For `main` Branch

```yaml
Protection Rules:
  - Require pull request before merging: ✅
  - Require approvals: 1 (minimum)
  - Dismiss stale reviews when new commits pushed: ✅
  - Require review from Code Owners: ✅
  - Require status checks to pass: ✅
    - CI/CD pipeline (build, test, lint)
    - Contract tests (Pact)
    - Security scan (Trivy)
    - Performance tests (Locust)
  - Require branches to be up to date: ✅
  - Require signed commits: ⚠️ Optional (recommended)
  - Include administrators: ✅
  - Restrict who can push: ✅ (only CI/CD + admins)
  - Allow force pushes: ❌ Never
  - Allow deletions: ❌ Never
```

### For `develop` Branch

```yaml
Protection Rules:
  - Require pull request: ✅
  - Require approvals: 1
  - Require status checks: ✅
    - Build success
    - Unit tests passing
    - Lint checks
  - Allow force pushes: ❌
  - Allow deletions: ❌
```

### For `feature/*` Branches

```yaml
Protection Rules:
  - None (developers can force push for rebasing)
  - Delete after merge: ✅ Automatic
```

---

## 💬 COMMIT MESSAGE FORMAT

**Convention:** [Conventional Commits](https://www.conventionalcommits.org/)

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(api): add refresh token endpoint` |
| `fix` | Bug fix | `fix(cache): correct Redis TTL calculation` |
| `docs` | Documentation | `docs(migration): update Phase 0 checklist` |
| `style` | Code style (formatting) | `style(api): format with black` |
| `refactor` | Code refactoring | `refactor(db): optimize patient query` |
| `perf` | Performance improvement | `perf(api): add database connection pooling` |
| `test` | Add/update tests | `test(prediction): add sepsis model tests` |
| `chore` | Maintenance tasks | `chore(deps): update langchain to v1.1` |
| `ci` | CI/CD changes | `ci(github): add deployment workflow` |
| `build` | Build system | `build(docker): optimize API image size` |
| `revert` | Revert previous commit | `revert: feat(api): add refresh token` |

### Scopes

Common scopes for this project:
- `api` - FastAPI backend
- `frontend` - Next.js UI
- `db` - Database related
- `cache` - Redis caching
- `kafka` - Streaming features
- `deployment` - VPS deployment
- `monitoring` - Prometheus/Grafana
- `docs` - Documentation
- `tests` - Testing infrastructure

### Examples

```bash
# Good commits
feat(api): implement JWT refresh token rotation
fix(cache): prevent race condition in feature store
perf(db): add index on patient_id for faster lookups
docs(deployment): add VPS setup guide
ci(github): add automated deployment to VPS
refactor(api): extract prediction logic to service layer

# Bad commits (avoid)
update stuff
fix bug
WIP
asdfasdf
```

---

## 🔄 WORKFLOW: FEATURE DEVELOPMENT

### 1. Create Feature Branch

```bash
# Update develop
git checkout develop
git pull origin develop

# Create feature branch from develop
git checkout -b feature/phase2-frontend

# Create sub-feature branch
git checkout -b feat/nextjs-setup
```

### 2. Development Cycle

```bash
# Make changes
# ...

# Stage changes
git add .

# Commit (will run pre-commit hooks)
git commit -m "feat(frontend): initialize Next.js 14 with App Router"

# Push to remote
git push origin feat/nextjs-setup
```

### 3. Create Pull Request

**Template:** `.github/pull_request_template.md`

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passing
- [ ] E2E tests passing (if applicable)
- [ ] Manual testing completed

## Deployment Checklist
- [ ] Database migrations added (if needed)
- [ ] Environment variables documented
- [ ] Feature flags configured (if needed)
- [ ] Rollback plan documented

## Screenshots (if UI changes)
[Add screenshots here]

## Related Issues
Closes #123
```

### 4. Code Review & Merge

```bash
# After PR approval
# Merge sub-feature into parent feature
git checkout feature/phase2-frontend
git merge feat/nextjs-setup --no-ff
git push origin feature/phase2-frontend

# Delete sub-feature branch
git branch -d feat/nextjs-setup
git push origin --delete feat/nextjs-setup
```

### 5. Merge to Develop

```bash
# When phase complete
git checkout develop
git merge feature/phase2-frontend --no-ff
git push origin develop

# Tag milestone
git tag -a v2.0.0-alpha.2 -m "Phase 2 frontend complete"
git push origin v2.0.0-alpha.2
```

---

## 🚀 WORKFLOW: DEPLOYMENT TO VPS

### Development → Staging → Production

```
┌─────────────┐
│   develop   │ ← Feature branches merge here
└──────┬──────┘
       │ (automated: push to staging)
       ↓
┌─────────────┐
│   Staging   │ ← VPS staging environment (subdomain)
│ VPS Server  │    staging.mediai.yourdomain.com
└──────┬──────┘
       │ (manual: create release branch)
       ↓
┌─────────────┐
│ release/v*  │ ← Release candidate (testing)
└──────┬──────┘
       │ (manual: approve release)
       ↓
┌─────────────┐
│     main    │ ← Production code
└──────┬──────┘
       │ (automated: deploy to production)
       ↓
┌─────────────┐
│ Production  │ ← VPS production environment
│ VPS Server  │    mediai.yourdomain.com
└─────────────┘
```

### Deployment Commands

**1. Deploy to Staging (Automatic on push to `develop`)**

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging
on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to VPS Staging
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/mediai-staging
            git pull origin develop
            docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build
```

**2. Create Release (Manual)**

```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v2.0.0

# Bump version
npm version 2.0.0  # or manually edit version files

# Push release branch
git push origin release/v2.0.0

# Create release PR to main
gh pr create --base main --head release/v2.0.0 \
  --title "Release v2.0.0" \
  --body "$(cat docs/release_notes/v2.0.0.md)"
```

**3. Deploy to Production (Automatic on merge to `main`)**

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Create deployment tag
        run: |
          git tag -a v${{ github.run_number }} -m "Deployment ${{ github.run_number }}"
          git push origin v${{ github.run_number }}

      - name: Deploy to VPS Production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST_PROD }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY_PROD }}
          script: |
            cd /opt/mediai-production
            git pull origin main
            docker-compose down
            docker-compose up -d --build --remove-orphans
            docker-compose exec -T api alembic upgrade head
```

---

## 🔧 WORKFLOW: HOTFIX (Emergency Production Fix)

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/memory-leak-fix

# 2. Fix the issue
# ... make changes ...

# 3. Commit with clear message
git commit -m "fix(api): resolve memory leak in prediction endpoint"

# 4. Create PR to main (expedited review)
gh pr create --base main --head hotfix/memory-leak-fix \
  --title "HOTFIX: Memory leak in prediction endpoint" \
  --label "hotfix,priority:critical"

# 5. After approval and merge to main
# Also merge back to develop
git checkout develop
git merge hotfix/memory-leak-fix
git push origin develop

# 6. Delete hotfix branch
git branch -d hotfix/memory-leak-fix
git push origin --delete hotfix/memory-leak-fix
```

---

## 📊 BRANCH LIFECYCLE

### Feature Branch

```bash
# Lifespan: Until feature complete (typically 1-7 days)

# Start
git checkout -b feature/phase1-api-contracts

# Development
git commit -m "feat: ..."
git push origin feature/phase1-api-contracts

# Complete
# Merge to develop via PR
# Delete after merge
```

### Release Branch

```bash
# Lifespan: Until released (1-3 days for testing)

# Start
git checkout -b release/v2.0.0

# Bug fixes only
git commit -m "fix: ..."

# Complete
# Merge to main (production)
# Merge back to develop
# Tag with version number
git tag -a v2.0.0 -m "Release v2.0.0"

# Delete after merge
```

---

## 🌳 GIT HOOKS & AUTOMATION

### Pre-commit Hooks (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=5000']

  - repo: https://github.com/psf/black
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
        args: ['--max-line-length=100']

  - repo: local
    hooks:
      - id: commitlint
        name: commitlint
        entry: commitlint --edit
        language: system
        stages: [commit-msg]
```

### Commit Message Linting

**Install:**
```bash
npm install -g @commitlint/cli @commitlint/config-conventional
```

**Config:** `commitlint.config.js`
```javascript
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat', 'fix', 'docs', 'style', 'refactor',
      'perf', 'test', 'chore', 'ci', 'build', 'revert'
    ]],
    'scope-enum': [2, 'always', [
      'api', 'frontend', 'db', 'cache', 'kafka',
      'deployment', 'monitoring', 'docs', 'tests'
    ]],
    'subject-case': [2, 'always', 'lower-case'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'header-max-length': [2, 'always', 72]
  }
};
```

---

## 📋 CODE OWNERS

**File:** `.github/CODEOWNERS`

```
# Global owners
* @yourusername

# API backend
/api/** @backend-team

# Frontend
/frontend/** @frontend-team

# Infrastructure
/docker-compose*.yml @devops-team
/nginx/** @devops-team
/.github/workflows/** @devops-team

# Documentation
/docs/** @documentation-team

# Database migrations
/alembic/** @database-team @backend-team

# Deployment scripts
/scripts/deploy*.sh @devops-team
```

---

## 🎯 MERGE STRATEGIES

### Feature → Develop

```bash
# Use merge commit (preserve history)
git merge feature/phase1-api --no-ff -m "Merge feature/phase1-api into develop"
```

### Release → Main

```bash
# Use merge commit with GPG signing (if configured)
git merge release/v2.0.0 --no-ff --gpg-sign -m "Release v2.0.0"
```

### Develop → Main (Not recommended)

```bash
# Only via release branches
# develop should NEVER merge directly to main
```

---

## 📌 TAGGING STRATEGY

### Version Tags

```bash
# Semantic Versioning: vMAJOR.MINOR.PATCH

# Alpha releases (develop)
git tag -a v2.0.0-alpha.1 -m "Phase 0 complete"
git tag -a v2.0.0-alpha.2 -m "Phase 1 complete"

# Beta releases (feature complete, testing)
git tag -a v2.0.0-beta.1 -m "Feature complete, begin testing"

# Release candidates
git tag -a v2.0.0-rc.1 -m "Release candidate 1"

# Production releases
git tag -a v2.0.0 -m "Release v2.0.0 - Full production deployment"

# Push tags
git push origin --tags
```

### Deployment Tags

```bash
# Automated deployment tags (created by CI/CD)
deploy-staging-$(date +%Y%m%d-%H%M%S)
deploy-production-$(date +%Y%m%d-%H%M%S)
```

---

## 🚨 ROLLBACK PROCEDURES

### Rollback Production Deployment

```bash
# Option 1: Revert to previous tag
ssh user@vps-production
cd /opt/mediai-production
git checkout tags/v2.0.0  # Previous stable version
docker-compose down
docker-compose up -d --build

# Option 2: Revert commit on main
git revert HEAD
git push origin main
# CI/CD will automatically deploy
```

### Rollback Database Migration

```bash
# SSH to VPS
ssh user@vps-production

# Downgrade migration
docker-compose exec api alembic downgrade -1

# Check status
docker-compose exec api alembic current
```

---

## ✅ CHECKLIST: BRANCH WORKFLOW SETUP

### Phase 0 Tasks

- [ ] Enable branch protection on `main`
- [ ] Enable branch protection on `develop`
- [ ] Install pre-commit hooks locally
- [ ] Setup commitlint
- [ ] Create `.github/CODEOWNERS`
- [ ] Create PR template (`.github/pull_request_template.md`)
- [ ] Configure GitHub Actions (CI/CD workflows)
- [ ] Test deployment to VPS staging
- [ ] Document rollback procedures
- [ ] Setup SSH keys for VPS deployment

---

## 📚 REFERENCES

- [Trunk-Based Development](https://trunkbaseddevelopment.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Git Flow vs Trunk-Based](https://www.atlassian.com/git/tutorials/comparing-workflows)

---

**Document Version:** 2.0
**Last Updated:** 2024-12-16
**Next Review:** After Phase 0 completion
**Status:** ✅ Ready for implementation

**Action Required:** Complete Phase 0 checklist items above
