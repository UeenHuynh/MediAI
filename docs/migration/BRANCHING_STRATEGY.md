# Branching Strategy: V2 Migration

## Model: Trunk-Based Development

```
main (production - V1 Streamlit)
│
├── feature/v2-migration (long-lived integration branch)
│   │
│   ├── feature/phase1-api-stabilization
│   │   ├── feat/auth-refresh-token
│   │   ├── feat/doctor-api
│   │   └── feat/alembic-migrations
│   │
│   ├── feature/phase2-frontend
│   │   ├── feat/nextjs-setup
│   │   ├── feat/glassmorphism-components
│   │   └── feat/pages-implementation
│   │
│   ├── feature/phase3-data-engineering
│   │   └── ...
│   │
│   └── feature/phase5-security
│       └── ...
│
└── hotfix/* (urgent V1 fixes)
```

## Branch Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/phase{N}-{name}` | `feature/phase1-api-stabilization` |
| Sub-feature | `feat/{short-name}` | `feat/doctor-api` |
| Hotfix | `hotfix/{issue}` | `hotfix/login-bug` |

## Merge Rules

### Into `feature/v2-migration`:
- PR required
- 1 approval minimum
- All tests pass
- No merge conflicts

### Into `main`:
- Only when phase is complete
- Feature flag enabled
- Smoke tests pass on staging
- Rollback plan documented

## Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Examples:
```
feat(auth): add refresh token endpoint
fix(api): correct CORS headers for Vercel
docs(migration): update Phase 0 checklist
```

## Protection Rules

| Branch | Direct Push | Force Push | Delete |
|--------|-------------|------------|--------|
| `main` | ❌ No | ❌ No | ❌ No |
| `feature/v2-migration` | ❌ No | ❌ No | ❌ No |
| `feature/*` | ✅ Yes | ⚠️ With care | ✅ After merge |
