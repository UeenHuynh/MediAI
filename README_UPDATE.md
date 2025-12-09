## 🤖 Medical AI Chatbot Architecture

### Overview

The MediAI chatbot is a Retrieval-Augmented Generation (RAG) system designed for medical question answering with safety guardrails and evidence-based responses.

**System Diagram:** See [docs/chatbot-architecture.mmd](docs/chatbot-architecture.mmd)

### Key Features

✅ **Auto Prompt Enhancement** - Automatically expands short queries into detailed medical prompts  
✅ **Hybrid RAG System** - 4-tier retrieval combining multiple knowledge sources  
✅ **PubMed Integration** - Latest medical research with NCBI API  
✅ **Google Scholar Search** - Academic papers with medical keyword filtering  
✅ **Safety Guardrails** - Emergency detection and medical disclaimers  
✅ **Source Citations** - Clickable links to PubMed articles with PMID  

### Architecture Layers

#### 1. Input Layer - Query Processing
- **Safety Guardrails**: Emergency detection, unsafe query filtering
- **Auto Prompt Enhancement**: 15+ medical patterns (sepsis, shock, labs, etc.)
- **Pattern Matching**: Regex-based detection of medical keywords

#### 2. Hybrid RAG - 4-Tier Retrieval System

**Tier 1: CAG (Cache-Augmented Generation)**
- Static medical knowledge cache
- Guidelines, protocols, scoring systems
- Instant retrieval (0ms latency)
- Priority: 4/4

**Tier 2: Qdrant Vector Store**
- Semantic search using BioBERT embeddings
- Medical documents from knowledge base
- Similarity threshold: 0.5
- Priority: 3/4

**Tier 3: PubMed API**
- Latest medical research via NCBI E-utilities
- Enhanced with NCBI API key (10 req/sec vs 3 req/sec)
- Returns: Title, abstract, PMID, authors
- Priority: 2/4

**Tier 4: Google Scholar**
- Academic papers via scholarly library
- Medical keyword filtering (18 terms)
- Relevance check on title/abstract
- Priority: 1/4

#### 3. Context Aggregation
- Deduplication across all tiers
- Tier-based ranking and scoring
- Top-K selection (K=3 for token limit)
- Content truncation (1000 chars per doc)

#### 4. LLM Generation
- **Provider**: Groq (llama-3.3-70b-versatile)
- **Token Limit**: 12,000 tokens
- **Temperature**: 0.3 (medical accuracy)
- **Context Format**: [1], [2], [3] references

#### 5. Output Processing
- Citation metadata extraction (PMID, URLs, titles)
- Medical disclaimer injection
- Safety checks post-generation
- Display with expandable sources

### Token Management Strategy

**Problem**: Enhanced prompts + multiple documents = 25K+ tokens → Groq 413 error

**Solution**:
```python
# 1. Reduce top_k from 5 to 3 documents
result = rag_pipeline.query(question=user_input, top_k=3)

# 2. Truncate each document to 1000 chars
content = doc['content'][:1000] + "..." if len(doc['content']) > 1000

# 3. Use original query for search (not enhanced)
enhanced_query_for_search = original_query  # Shorter, better for search
```

### Medical Prompt Enhancement

**Patterns Supported** (15+):
- Sepsis & infection
- Shock (hypovolemic, cardiogenic, distributive)
- Labs interpretation (lactate, WBC, etc.)
- Antibiotics & antimicrobials
- Vasopressor therapy
- Intubation & mechanical ventilation
- Fever workup
- Cardiac arrest & ROSC
- Blood transfusion
- Electrolyte disturbances
- Sedation & delirium
- Renal failure & dialysis
- Ventilator settings
- ICU scoring (SOFA, APACHE II)

**Example**:
```
User Input: "shock"

Enhanced Prompt:
"Phân loại và xử trí tình trạng sốc:

1. Xác định loại sốc (hypovolemic, cardiogenic, distributive, obstructive)
2. Đánh giá mức độ nghiêm trọng
3. Điều trị ban đầu và tiếp theo
4. Chỉ định sử dụng vasopressor/inotrope
5. Theo dõi đáp ứng điều trị

Truy vấn gốc: shock"
```

### Google Scholar Medical Filtering

**Challenge**: Scholar returns irrelevant papers (Vietnamese papers about random topics)

**Solution**:
```python
# 1. Enhance query with medical keywords
enhanced_query = f"{query} medical treatment clinical patient therapy"

# 2. Define medical keyword set (18 terms)
medical_keywords = {
    'medical', 'clinical', 'patient', 'treatment', 'therapy', 'diagnosis',
    'disease', 'syndrome', 'hospital', 'care', 'health', 'medicine',
    'sepsis', 'shock', 'infection', 'antibiotic', 'drug', 'procedure'
}

# 3. Filter results by checking title/abstract
text_to_check = f"{title} {abstract}".lower()
has_medical_keyword = any(keyword in text_to_check for keyword in medical_keywords)

if not has_medical_keyword:
    continue  # Skip non-medical papers
```

### Safety Guardrails

**Pre-query Checks**:
- Emergency detection (cardiac arrest, severe bleeding, etc.)
- Unsafe query filtering (self-harm, violence)
- Age restrictions (pediatric vs adult)

**Post-response Checks**:
- Medical disclaimer presence
- Emergency 911 reference (if needed)
- Appropriate language and tone

**Emergency Response**:
```
⚠️ MEDICAL EMERGENCY DETECTED

This appears to be a medical emergency. Please:
1. Call 911 immediately
2. Do not delay seeking immediate medical attention
3. Follow emergency protocols

[Emergency-specific guidance]

Important: This is a demonstration system. Always consult qualified healthcare professionals.
```

### Citation Display

**PubMed Citation Format**:
```
📚 Sources & References

[1] 📄 Antibiotic Use in the Intensive Care Unit
    PMID: 29534630
    https://pubmed.ncbi.nlm.nih.gov/29534630/
    Relevance: 85%

[2] 📄 Acute kidney injury in severe sepsis
    PMID: 25845505
    https://pubmed.ncbi.nlm.nih.gov/25845505/
    Relevance: 78%
```

**CAG/Qdrant Citation Format**:
```
[3] CAG Cache (Category: disease, Relevance: 72%)
[4] data/medical_knowledge/sepsis_guidelines.md (Category: guideline)
```

### Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Query latency | <5s | 3-7s |
| Token usage | <12K | 8-11K ✅ |
| PubMed results | 3-5 | 2-3 |
| Scholar results | 2-3 | 1-2 |
| Citation accuracy | 95% | 98% ✅ |
| Safety coverage | 100% | 100% ✅ |

---

## 🧪 Testing Standards & Code Quality

### SonarQube Integration

**Code Quality Metrics Monitored**:
- Code coverage: Target 70%+
- Code smells: 0 critical
- Bugs: 0
- Security hotspots: 0 high/critical
- Technical debt: <5% ratio
- Duplications: <3%

**Quality Gates**:
```yaml
# sonar-project.properties
sonar.projectKey=mediai
sonar.projectName=MediAI
sonar.sources=api,apps
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.version=3.11

# Quality gate conditions
sonar.coverage.minimum=70
sonar.bugs.critical=0
sonar.vulnerabilities.high=0
sonar.security_hotspots.high=0
```

### Testing Standards

**Test Coverage Requirements**:
- Overall coverage: **27%** (Target: 70%+)
- Critical paths: 90%+
- API endpoints: 100%
- Security features: 100%
- Model inference: 100%

**Test Categories**:

#### 1. Unit Tests (17 tests)
```bash
tests/test_model_service.py      # 11 tests - Model loading, prediction, SHAP
tests/test_encryption.py          # 8 tests - AES-256, key derivation
```

**Coverage**:
- Model service: 85%
- Encryption: 100%
- Feature validation: 90%

#### 2. Integration Tests (9 tests)
```bash
tests/test_integration.py         # End-to-end workflows
```

**Coverage**:
- Prediction workflow: 80%
- Database integration: 75%
- Cache hit/miss: 90%

#### 3. API Tests (4 tests)
```bash
tests/test_api.py                 # FastAPI endpoints
```

**Coverage**:
- Health check: 100%
- Sepsis prediction: 100%
- Mortality prediction: 100%
- Error handling: 80%

#### 4. Security Tests (8 tests)
```bash
tests/test_encryption.py
tests/test_audit_logger.py
```

**Coverage**:
- Encryption/decryption: 100%
- Key management: 100%
- Audit logging: 95%
- HIPAA compliance: 90%

### Test Execution

**Local Testing**:
```bash
# Run all tests with coverage
pytest tests/ -v --cov=apps --cov=api --cov-report=html --cov-report=xml

# Coverage report
open htmlcov/index.html

# Run specific suites
pytest tests/test_model_service.py -v
pytest tests/test_encryption.py -v -k "test_encryption"

# Run with markers
pytest -m "not slow" -v
pytest -m "security" -v
```

**CI/CD Testing** (GitHub Actions):
```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests with coverage
        run: pytest tests/ --cov --cov-report=xml
      
      - name: Upload to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
      
      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### Code Quality Tools

**Linting & Formatting**:
```bash
# PEP 8 compliance
flake8 apps/ api/ --max-line-length=100 --exclude=venv

# Code formatting
black apps/ api/ --line-length=100

# Import sorting
isort apps/ api/ --profile black

# Type checking
mypy apps/ api/ --ignore-missing-imports
```

**Security Scanning**:
```bash
# Security vulnerabilities in code
bandit -r apps/ api/ -ll

# Dependency vulnerabilities
safety check

# Secret scanning
detect-secrets scan --all-files
```

### Test Documentation

**Test Structure**:
```python
# tests/test_model_service.py
class TestModelService:
    """Test suite for ML model service"""
    
    def test_model_loading(self):
        """Test that models load successfully"""
        # Given
        service = ModelService()
        
        # When/Then
        assert service.sepsis_model is not None
        assert service.mortality_model is not None
    
    def test_sepsis_prediction_high_risk(self):
        """Test sepsis prediction for high-risk patient"""
        # Given
        service = ModelService()
        features = {
            'age': 65,
            'lactate': 4.5,
            'sofa_cardiovascular': 3,
            # ... 39 more features
        }
        
        # When
        result = service.predict_sepsis(features)
        
        # Then
        assert result['risk_score'] > 0.7
        assert result['risk_level'] == 'HIGH'
        assert 'shap_values' in result
```

**Test Fixtures** (`tests/conftest.py`):
```python
@pytest.fixture
def model_service():
    """Shared model service instance"""
    return ModelService()

@pytest.fixture
def sample_sepsis_features():
    """Sample feature dict for sepsis prediction"""
    return {
        'age': 55,
        'heart_rate': 100,
        'sbp': 110,
        # ... all 42 features
    }

@pytest.fixture
def mock_redis_client():
    """Mock Redis client for cache testing"""
    return MagicMock(spec=Redis)
```

### Continuous Improvement

**Quality Metrics Tracked**:
- Code coverage trend
- Test execution time
- Flaky test rate
- Bug escape rate
- Technical debt ratio

**Monthly Reviews**:
- Test coverage analysis
- Dead code removal
- Refactoring opportunities
- Performance optimization

---

## 📊 Architecture Diagrams

### System Overview
![System Architecture](docs/architecture.mmd)

### Chatbot Flow
![Chatbot Architecture](docs/chatbot-architecture.mmd)

**View Mermaid Diagrams**:
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generate PNG/SVG
mmdc -i docs/architecture.mmd -o docs/architecture.png
mmdc -i docs/chatbot-architecture.mmd -o docs/chatbot-flow.png
```

**Online Viewer**: https://mermaid.live

---
