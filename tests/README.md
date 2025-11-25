# Testing Suite

Comprehensive testing for MediAI platform.

## Test Structure

```
tests/
├── __init__.py                # Test package init
├── conftest.py                # Pytest fixtures and configuration
├── test_model_service.py      # Unit tests for ML model service
├── test_encryption.py         # Unit tests for encryption utilities
├── test_api.py                # API endpoint tests
└── test_integration.py        # End-to-end integration tests
```

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_model_service.py -v
```

### Run with coverage
```bash
pytest tests/ --cov=apps --cov=api --cov-report=html
```

### Run specific test class
```bash
pytest tests/test_model_service.py::TestModelService -v
```

### Run specific test method
```bash
pytest tests/test_model_service.py::TestModelService::test_model_loading -v
```

## Test Categories

### Unit Tests

**test_model_service.py** (11 tests)
- Model loading and initialization
- Feature count verification
- Sepsis prediction (low/high risk)
- Mortality prediction
- Feature preparation
- Risk level thresholds

**test_encryption.py** (8 tests)
- Encryption/decryption
- Patient data encryption
- Hash generation
- Special characters handling

### API Tests

**test_api.py** (4 tests)
- Root endpoint
- Health check
- Models info
- Input validation

### Integration Tests

**test_integration.py** (9 tests)
- End-to-end prediction workflow
- Multiple predictions consistency
- API validation
- Model service singleton

## Test Coverage

Target: **70%+ coverage**

Current coverage by module:
- `apps/services/model_service.py`: 20% (core prediction logic)
- `apps/utils/encryption.py`: Testing complete
- `api/`: Testing in progress

## CI/CD Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Pre-commit hooks (optional)

See `.github/workflows/ci.yml` for CI configuration.

## Writing New Tests

### Test Naming Convention
- File: `test_*.py`
- Class: `Test*`
- Method: `test_*`

### Example Test

```python
import pytest

class TestMyFeature:
    """Test my feature"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.feature = MyFeature()

    def test_basic_functionality(self):
        """Test basic functionality"""
        result = self.feature.do_something()
        assert result == expected
```

### Using Fixtures

Fixtures are defined in `conftest.py`:
- `sample_sepsis_features`: Standard sepsis patient features
- `sample_mortality_features`: Standard mortality patient features
- `low_risk_sepsis_features`: Low risk patient
- `high_risk_sepsis_features`: High risk patient

## Test Results

Last test run:
```
============================= test session starts ==============================
collected 11 items

test_model_service.py::TestModelService::test_model_loading PASSED       [  9%]
test_model_service.py::TestModelService::test_sepsis_feature_count PASSED [ 18%]
test_model_service.py::TestModelService::test_mortality_feature_count PASSED
test_model_service.py::TestModelService::test_sepsis_prediction_low_risk PASSED
test_model_service.py::TestModelService::test_sepsis_prediction_high_risk PASSED
test_model_service.py::TestModelService::test_mortality_prediction PASSED
test_model_service.py::TestModelService::test_sepsis_prediction_with_missing_optional_fields PASSED
test_model_service.py::TestModelService::test_mortality_prediction_vasopressor_boolean PASSED
test_model_service.py::TestModelService::test_risk_level_thresholds_sepsis PASSED
test_model_service.py::TestModelService::test_feature_preparation_sepsis PASSED
test_model_service.py::TestModelService::test_feature_preparation_mortality PASSED

============================== 11 passed in 0.98s ===============================
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`, ensure you're running from project root:
```bash
cd /path/to/MediAI
pytest tests/
```

### Model Files Missing

Tests require model files in `models/` directory:
- `sepsis_lightgbm_v1.pkl`
- `sepsis_feature_names.pkl`
- `mortality_lightgbm_v1.pkl`
- `mortality_feature_names.pkl`

### Dependency Issues

Install test dependencies:
```bash
pip install pytest pytest-cov
pip install -r requirements.txt
pip install -r api/requirements.txt
pip install -r apps/requirements.txt
```

## Future Test Additions

- [ ] API integration tests with mock database
- [ ] Streamlit UI tests with selenium
- [ ] Load testing for API endpoints
- [ ] Model drift detection tests
- [ ] Security penetration tests
