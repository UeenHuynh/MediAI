# Contributing to MediAI

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+ (for frontend)
- Docker & Docker Compose
- Git

### Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/mediai.git
cd mediai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r api/requirements.txt
pip install pre-commit pytest pytest-cov

# Setup pre-commit hooks
pre-commit install

# Start dev environment
docker-compose -f docker-compose.dev.yml up -d

# Run tests
pytest --cov=api --cov=apps
```

## Code Style

### Python
- **Formatter**: Black (line length 88)
- **Linter**: Flake8
- **Import Sorting**: isort (black profile)
- **Type Checking**: mypy

### Commit Convention
We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Add/update tests
- `chore`: Maintenance

**Examples:**
```
feat(auth): add refresh token endpoint
fix(predict): handle null values in patient data
docs(readme): update setup instructions
test(api): add integration tests for auth
```

## Pull Request Process

1. **Create feature branch** from `develop`
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature
   ```

2. **Make changes** following code style

3. **Run pre-commit checks**
   ```bash
   pre-commit run --all-files
   ```

4. **Run tests**
   ```bash
   pytest --cov=api --cov=apps --cov-fail-under=80
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature
   ```

6. **PR Requirements:**
   - [ ] All CI checks pass
   - [ ] Test coverage ≥ 80%
   - [ ] At least 1 review approval
   - [ ] No merge conflicts

## Testing

### Unit Tests
```bash
pytest tests/unit/ -v
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### Coverage Report
```bash
pytest --cov=api --cov-report=html
open htmlcov/index.html
```

## Security

- Never commit secrets or credentials
- Use environment variables for sensitive data
- Run `bandit -r api/` before committing
- Report vulnerabilities to security@mediai.com
