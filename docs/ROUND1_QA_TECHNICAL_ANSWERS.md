# 🧨 Round 1: MediAI Technical Q&A

> **Date**: 2026-01-16  
> **System Version**: MediAI V4  
> **Analysis Based On**: Actual source code review

---

## 1) Rate Limit (slowapi) Configuration

### ❓ Bạn limit endpoint nào? predict limit bao nhiêu/phút? chat bao nhiêu/phút?

**Thực tế trong code:**

| Endpoint | Rate Limit | File |
|----------|------------|------|
| `POST /api/v1/predict/sepsis` | **100/minute** | `api/routers/predictions.py:31` |
| `POST /api/v1/predict/mortality` | **100/minute** | `api/routers/predictions.py:67` |
| `POST /api/v1/chat` | **Không có explicit limit** | `api/routers/chat.py` |
| `POST /api/v1/predict/simple/sepsis` | **Không có explicit limit** | `api/routers/simplified_predictions.py` |
| `POST /api/v1/predict/simple/mortality` | **Không có explicit limit** | `api/routers/simplified_predictions.py` |

**Code evidence:**
```python
# api/routers/predictions.py
limiter = Limiter(key_func=get_remote_address)

@router.post("/predict/sepsis", response_model=SepsisPredictionResponse)
@limiter.limit("100/minute")
async def predict_sepsis(...):
```

### ❓ Vì sao limit theo IP chứ không theo user_id (JWT)?

**Thực tế:** Hiện tại dùng `get_remote_address` (IP-based) thay vì `user_id` vì:

1. **Đơn giản hơn** - Không cần parse JWT trước khi rate limit
2. **Bảo vệ trước authentication** - Rate limit xảy ra trước khi JWT được validate
3. **Trade-off**: Shared IP (NAT, corporate firewall) sẽ bị limit chung → **vấn đề tiềm ẩn**

**Nhược điểm**: Nếu nhiều users ở cùng corporate network, họ share quota.

### ❓ Nếu deploy sau proxy/load balancer (Render) thì get_remote_address có lấy đúng IP thật không?

**Thực tế:** **KHÔNG ĐỦ AN TOÀN!**

- `get_remote_address` lấy từ `request.client.host`
- Khi deploy trên Render.com (behind reverse proxy), `client.host` sẽ là IP của proxy, **không phải IP thật của user**

**Cách fix đúng:**
```python
# Sử dụng X-Forwarded-For header
from slowapi.util import get_remote_address

def get_real_ip(request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)

limiter = Limiter(key_func=get_real_ip)
```

**⚠️ BUG HIỆN TẠI:** Code chưa fix, tất cả requests qua Render sẽ share cùng một rate limit bucket!

---

## 2) Redis Cache: Cache cái gì, key tạo thế nào

### ❓ Bạn cache output predict hay cache SHAP hay cache cả 2?

**Thực tế:** Cache **prediction output** (bao gồm cả `top_features` - là feature importance, **không phải SHAP values thực sự**)

**Code evidence từ `api/services/prediction_service.py`:**
```python
result = {
    "patient_id": request.patient_id,
    "prediction": {
        "risk_score": float(probability),
        "risk_level": risk_level,
        "recommendation": self._get_recommendation(risk_level, "sepsis"),
    },
    "top_features": top_features,  # Feature importance, NOT SHAP
    "metadata": {...}
}

# Cache toàn bộ result
self._save_to_cache(cache_key, result)
```

**⚠️ LƯU Ý:** Comment trong code nói "would use SHAP in production" nhưng thực tế đang dùng `model.feature_importances_` (global importance), **KHÔNG phải SHAP values** (instance-level).

### ❓ Bạn tạo cache key kiểu gì?

**Cache key structure:**
```
prediction:{patient_id}:{SHA256_hash_of_features}
```

**Code từ `api/services/prediction_service.py`:**
```python
def _get_cache_key(self, patient_id: str, features: Dict) -> str:
    features_str = json.dumps(features, sort_keys=True)  # Deterministic
    hash_str = hashlib.sha256(features_str.encode()).hexdigest()
    return f"prediction:{patient_id}:{hash_str}"
```

**Analysis:**
- ✅ `sort_keys=True` đảm bảo deterministic JSON
- ✅ SHA256 secure hơn MD5
- ❌ **KHÔNG include model version** trong key!
  - Nếu deploy model mới mà không clear cache → trả kết quả cũ

**BUG tiềm ẩn:** Update model version từ v2 → v3 mà không invalidate cache sẽ trả prediction từ model cũ!

### ❓ TTL bao lâu? Tại sao?

**TTL Settings từ `api/core/config.py` và `api/core/redis_cache.py`:**

| Cache Type | TTL | File |
|------------|-----|------|
| Predictions | **3600s (1 hour)** | `config.py:CACHE_TTL_SECONDS` & `redis_cache.py:PREDICTION_TTL` |
| Chat Responses | **1800s (30 min)** | `redis_cache.py:CHAT_RESPONSE_TTL` |
| Embeddings | **86400s (24 hours)** | `redis_cache.py:EMBEDDING_TTL` |

**Lý do 1 hour cho predictions:**
- ICU vitals không thay đổi quá nhanh trong 1 giờ
- Giảm load inference cho repeated queries
- Trade-off: Có thể trả stale data nếu vitals thay đổi nhanh

### ❓ Nếu patient update vitals liên tục, cache có làm trả kết quả "cũ" không?

**Thực tế:** **KHÔNG** - vì cache key bao gồm hash của features!

Nếu vitals thay đổi → hash khác → cache miss → fresh prediction.

**NHƯNG** có edge case:
- Nếu frontend gửi lại **cùng một request** (không update vitals mới) → cache hit → stale result
- Không có mechanism để **invalidate cache** khi patient record được update trong database

**Code evidence - có invalidation function nhưng KHÔNG được gọi tự động:**
```python
# api/core/redis_cache.py
@staticmethod
def invalidate_prediction_cache(prediction_type: str = None) -> int:
    """Invalidate prediction cache."""
    pattern = f"pred:{prediction_type or '*'}:*"
    keys = client.keys(pattern)
    if keys:
        return client.delete(*keys)
    return 0
```

**⚠️ MISSING:** Không có trigger để invalidate cache khi patient vitals được update.

---

## 3) Load Model + Concurrency

### ❓ Model load ở đâu? startup/lifespan hay load khi request đến?

**Thực tế:** Model được load **trong `__init__` của `PredictionService`**, mà `PredictionService` được instantiate **module-level (import time)**.

**Flow:**
1. `api/routers/predictions.py` imports `PredictionService`
2. Line 27: `prediction_service = PredictionService()` - module level
3. `PredictionService.__init__()` calls `self._load_models()`
4. Models loaded from pickle files

**Code evidence:**
```python
# api/routers/predictions.py
prediction_service = PredictionService()  # Line 27

# api/services/prediction_service.py
class PredictionService:
    def __init__(self):
        self.models = {}
        self._init_redis()
        self._load_models()  # Models loaded here!
    
    def _load_models(self):
        with open(sepsis_model_file, "rb") as f:
            self.models["sepsis"] = pickle.load(f)
```

**⚠️ Không dùng FastAPI lifespan event** - models load khi module được import, không phải trong startup.

### ❓ Multi-worker Uvicorn/Gunicorn thì mỗi worker load 1 bản model, RAM có bị nhân lên không?

**Thực tế:** **CÓ!** Mỗi worker load riêng models vào RAM.

- LightGBM models của MediAI: ~2-5MB mỗi model
- 2 models (sepsis + mortality) × N workers = RAM bị nhân
- Với 4 workers: ~20-40MB thêm RAM so với 1 worker

**Giải pháp tiềm năng (chưa implement):**
- Model serving với shared memory
- Dedicated model server (TensorFlow Serving, Triton)
- Redis để cache serialized model (nhưng vẫn deserialize per-worker)

### ❓ SHAP compute có "block event loop" không?

**Thực tế:** MediAI **KHÔNG dùng SHAP thực sự** trong production!

**Code evidence:**
```python
# api/services/prediction_service.py
def _get_top_features(self, features_df, model, model_type: str):
    """Get top contributing features (simplified version)"""
    # In production, use SHAP here
    # For now, return top features by importance
    
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_  # Global importance
        ...
```

**Nếu sau này thêm SHAP:**
- SHAP TreeExplainer trên LightGBM: ~100-500ms per sample
- **CÓ block event loop** nếu chạy sync
- Cần wrap trong `asyncio.to_thread()` hoặc dùng ProcessPoolExecutor

```python
# Cách fix đúng khi thêm SHAP
import asyncio
def compute_shap_sync(model, data):
    explainer = shap.TreeExplainer(model)
    return explainer.shap_values(data)

async def compute_shap_async(model, data):
    return await asyncio.to_thread(compute_shap_sync, model, data)
```

---

## 4) Preprocessing & Missing Data

### ❓ Input schema sepsis gồm những feature nào?

**Full schema từ `api/models/schemas.py` - SepsisFeatures class:**

| Category | Features | Count |
|----------|----------|-------|
| Demographics | age, gender, bmi | 3 |
| Vitals | heart_rate, sbp, dbp, temperature, respiratory_rate | 5 |
| Labs | wbc, lactate, creatinine, platelets, bilirubin, sodium, potassium, glucose, hemoglobin, bicarbonate, pao2, paco2, ph, anion_gap, albumin, troponin, bnp, inr, ast, alt | 20 |
| SOFA Scores | respiratory_sofa, cardiovascular_sofa, hepatic_sofa, coagulation_sofa, renal_sofa, neurological_sofa | 6 |
| Temporal Trends | lactate_trend_12h, hr_trend_6h, wbc_trend_12h, sbp_trend_6h, temperature_trend_6h, rr_trend_6h | 6 |
| Time Features | hour_of_admission, icu_los_so_far | 2 |
| **TOTAL** | | **42 features** |

### ❓ Missing value strategy?

**Thực tế:** MediAI dùng **Smart Feature Imputation** với medical correlations!

**Code từ `api/services/feature_imputation.py`:**

```python
class FeatureImputer:
    @staticmethod
    def impute_sepsis_features(vital_signs: Dict) -> Dict:
        # Calculate risk indicators
        tachycardia_score = min(max(hr - 80, 0) / 50, 1.0)
        hypotension_score = min(max(120 - sbp, 0) / 40, 1.0)
        fever_score = min(max(temp - 37.0, 0) / 3.0, 1.0)
        ...
        
        # Continuous risk score (0-5)
        risk_score = tachycardia_score + hypotension_score + fever_score + ...
        risk_pct = risk_score / 5.0
        
        # Impute labs based on clinical correlation
        if wbc is None:
            wbc = 7.5 + (risk_pct * 17.5)  # Normal → elevated with risk
        
        if lactate is None:
            lactate = 1.2 + (lactate_risk * 3.8)  # Normal → elevated
        
        # CUBIC curve for albumin to avoid model threshold at ~3.1
        albumin = 3.5 - ((risk_pct**3) * 1.5)
```

**Strategy Summary:**
- **NOT** median imputation
- **NOT** forward fill / LOCF
- **Phyisiologically-derived imputation** - tính toán labs từ vitals dựa trên medical correlation
- Dùng **continuous risk scoring** thay vì discrete thresholds

### ❓ Nếu input thiếu quá nhiều feature thì bạn reject hay vẫn predict?

**Thực tế:** MediAI **KHÔNG reject** - luôn predict!

**Simplified endpoint (`api/routers/simplified_predictions.py`) chỉ yêu cầu:**
- age, heart_rate, temperature, respiratory_rate, systolic_bp, diastolic_bp, spo2

**Các labs là OPTIONAL:**
- wbc, lactate, creatinine (có thể None)

**Workflow:**
1. Frontend gửi 7 vitals cơ bản
2. `FeatureImputer.impute_sepsis_features()` sinh 42 features
3. Model predict với full 42 features

**⚠️ Concern:** Nếu imputation sai nhiều, model vẫn cho prediction với confidence cao!

### ❓ Làm sao tránh model bị "đoán bừa" mà nhìn vẫn có vẻ tự tin?

**Thực tế:** MediAI **KHÔNG có explicit mechanism** để flag low-confidence predictions!

**What's missing:**
1. ❌ Không track số features bị imputed
2. ❌ Không giảm confidence khi nhiều features imputed
3. ❌ Không warning user về data quality

**Potential fix:**
```python
def predict_with_confidence(request, imputed_count):
    base_prediction = model.predict(...)
    
    # Penalize confidence based on imputation
    imputation_penalty = imputed_count / total_features
    adjusted_confidence = base_confidence * (1 - imputation_penalty * 0.5)
    
    if imputed_count > 20:
        warnings.append("⚠️ High imputation - prediction may be less reliable")
```

---

## 5) RAG + Qdrant Pipeline

### ❓ Bạn chunk docs theo size bao nhiêu? overlap bao nhiêu?

**Thực tế: KHÔNG có explicit chunking configuration!**

Từ `api/core/qdrant_store.py`:
- Documents được add với `content` field
- Không thấy chunking logic trong `add_documents()`
- Chunking phải được handle ở ingestion scripts (ngoài main codebase)

**Embedding truncation từ `api/services/langchain_medical_bot.py`:**
```python
def _check_token_budget(self, context: str) -> str:
    estimated_tokens = len(context) / 4  # ~4 chars per token
    if estimated_tokens > self.max_tokens:
        char_limit = int(self.max_tokens * 4 * 0.8)
        truncated = context[:char_limit]
        return truncated
```

**Max token limit:** 12,000 tokens (default)

### ❓ Embedding model nào? dimension bao nhiêu? cosine hay dot?

**Từ `api/core/qdrant_store.py`:**

| Config | Value |
|--------|-------|
| Embedding Model | `all-MiniLM-L6-v2` (sentence-transformers) |
| Dimension | **384** |
| Distance Metric | **Cosine** |
| Score Threshold | 0.5 (default) |

**Code evidence:**
```python
# api/core/qdrant_store.py
self.client.create_collection(
    collection_name=self.collection_name,
    vectors_config=VectorParams(
        size=384,  # Sentence transformer dimension
        distance=Distance.COSINE,
    ),
)
```

### ❓ Top-k retrieve bao nhiêu? có rerank không?

**Từ `api/services/hybrid_rag.py`:**

| Tier | Source | Top-k | Rerank |
|------|--------|-------|--------|
| 1 | CAG Cache | 3 | No |
| 2 | Qdrant | 5 | No |
| 3 | PubMed | 5 | No |
| 4 | Semantic Scholar | 3 | No |

**Ranking strategy (NO ML reranker):**
```python
def _rank_results(self, results, query):
    tier_priority = {"cag": 4, "qdrant": 3, "pubmed": 2, "scholar": 1}
    sorted_results = sorted(
        results,
        key=lambda x: (tier_priority.get(x.get("tier", ""), 0), x.get("score", 0)),
        reverse=True,
    )
```

**⚠️ NO semantic reranker** (như Cohere Rerank, BGE Reranker)

### ❓ Bạn trả citations về frontend kiểu gì?

**JSON format từ `api/routers/chat.py`:**
```json
{
  "answer": "Sepsis is...",
  "citations": [
    {
      "number": 1,
      "source": "PubMed",
      "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
      "pmid": "12345678"
    },
    {
      "number": 2,
      "source": "CAG Guidelines",
      "url": null,
      "pmid": null
    }
  ],
  "disclaimer": "⚠️ This information is for educational purposes only...",
  "session_id": "uuid-here",
  "redacted_query": null,
  "processing_time_ms": 1234
}
```

### ❓ Nếu không retrieve được paper tốt, bạn làm gì để LLM không bịa?

**Implemented safeguards:**

1. **Structured prompt** yêu cầu LLM chỉ dùng retrieved context:
   ```python
   "Answer using retrieved context only. Cite sources as [1], [2], etc."
   ```

2. **Emergency detection** trong system prompt:
   ```python
   """If emergency signs detected (chest pain, difficulty breathing,
   severe bleeding, altered consciousness), start with:
   "🚨 EMERGENCY - Call 911 immediately." """
   ```

3. **Mandatory disclaimer:**
   ```python
   "⚠️ This is informational only. Consult healthcare provider."
   ```

4. **Safety rules:**
   ```python
   """- Never provide specific medication dosages
   - Never diagnose conditions definitively
   - Always recommend professional consultation"""
   ```

**WHAT'S MISSING:**
- ❌ No "I don't know" trigger when retrieval fails
- ❌ No confidence score for retrieved documents
- ❌ No explicit "no relevant documents found" response

---

## 6) Security "nói là HIPAA/GDPR" - Implementation thực tế

### ❓ PII redaction bạn làm bằng rule-based regex hay model NER?

**Thực tế: CẢ HAI!**

**Từ `api/services/pii_redaction_service.py`:**

1. **Microsoft Presidio** (includes ML models):
   - `AnalyzerEngine` - NER-based entity detection
   - Supports 15+ entity types

2. **Custom Regex Patterns** (medical-specific):
   ```python
   MEDICAL_PATTERNS = {
       "PATIENT_ID": Pattern(
           name="patient_id_pattern",
           regex=r"(?i)\b(PATIENT|PT|PAT)[-_][0-9]{5,10}\b",
           score=0.85,
       ),
       "MRN": Pattern(
           name="mrn_pattern",
           regex=r"(?i)\b(?:MRN|MR)[-:][0-9]{6,12}\b",
           score=0.9,
       ),
   }
   
   SSN_PATTERN = Pattern(
       regex=r"\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b",
       score=0.85,
   )
   ```

**Supported entities:**
- PERSON, EMAIL, PHONE, SSN, MEDICAL_LICENSE
- CREDIT_CARD, IBAN, PASSPORT, DRIVER_LICENSE
- DATE_TIME, LOCATION, IP_ADDRESS
- PATIENT_ID, MRN (custom medical)

### ❓ Audit log bạn log những gì? log ở đâu? có tránh log raw PII không?

**Audit logging implementation:**

1. **What's logged:**
   - Entity types detected (NOT the actual PII content)
   - Count of entities
   - Processing time

2. **Log destination:** Standard Python logging (stdout)

**Code evidence từ `api/services/pii_redaction_service.py`:**
```python
if self.enable_audit_log and results:
    entity_types = {r.entity_type for r in results}
    logger.info(
        f"PII detected: {len(results)} instances, types={entity_types}"
    )
    
# Later:
if self.enable_audit_log:
    logger.info(
        f"PII redaction completed: "
        f"{result.pii_count} entities, "
        f"{result.processing_time_ms:.2f}ms"
    )
```

**✅ DOES NOT log raw PII values**

**⚠️ MISSING for full HIPAA compliance:**
- ❌ Logs không được gửi đến centralized audit system
- ❌ Không có log retention policy (7 year requirement)
- ❌ Không log user_id who accessed PHI
- ❌ Không có tamper-evident logging

### ❓ JWT lưu ở đâu frontend? localStorage hay httpOnly cookie? vì sao?

**Thực tế: localStorage!**

**Từ `frontend/src/stores/auth-store.ts`:**
```typescript
const response = await apiClient.post("/auth/login", formData, {...});
const { access_token, refresh_token } = response.data;

localStorage.setItem("access_token", access_token);  // HERE!
localStorage.setItem("refresh_token", refresh_token);
```

**Security implications:**

| Storage | XSS Vulnerable | CSRF Vulnerable |
|---------|----------------|-----------------|
| localStorage | ✅ YES | ❌ No |
| httpOnly cookie | ❌ No | ✅ YES (without SameSite) |

**Current risk:**
- JavaScript có thể access localStorage
- XSS attack có thể steal JWT tokens
- Cần sanitize all user inputs để prevent XSS

**Better approach (not implemented):**
```typescript
// Server should set httpOnly cookie:
// Set-Cookie: access_token=xxx; HttpOnly; Secure; SameSite=Strict

// Frontend chỉ cần:
fetch("/api/protected", { credentials: "include" })
```

---

## 🎯 Summary: Gaps & Recommendations

| Area | Current State | Priority Fix |
|------|---------------|--------------|
| Rate Limiting | IP-based, broken behind proxy | Use X-Forwarded-For |
| Cache | No model version in key | Add version to cache key |
| SHAP | Not implemented (uses global importance) | Add TreeExplainer with async |
| Confidence | No imputation penalty | Add confidence adjustment |
| Reranking | Score-based only | Add Cohere/BGE reranker |
| Hallucination | Prompt-based guard only | Add "no documents" fallback |
| Audit | Basic logging only | Add centralized audit system |
| JWT Storage | localStorage (XSS risk) | Switch to httpOnly cookie |
