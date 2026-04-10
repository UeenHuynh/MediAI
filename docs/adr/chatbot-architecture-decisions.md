# Chatbot Architecture Decision Record

Last updated: 2026-04-11

---

## ADR-001: Groq AuthenticationError must fail fast (no retry)

**Status:** Accepted — implemented 2026-04-10

**Context:**
`_generate_with_retry()` in `langchain_medical_bot.py` used tenacity with
`retry_if_exception_type((Exception,))`, which matched every exception including
`groq.AuthenticationError`. A bad API key caused 3 retries with exponential backoff
(min 2 s, max 10 s), adding ~11 s of pure latency to a failure that could never succeed.

**Decision:**
Use `retry_if_not_exception_type(GroqAuthError)` as the tenacity retry predicate.
`groq.AuthenticationError` is imported with an `ImportError` fallback stub so the
decorator works even if the groq package is unavailable.

**Consequences:**
- Auth failures surface immediately (<100 ms).
- Transient errors (network, rate-limit) are still retried up to 3 times.
- **Do not change the retry predicate back to `retry_if_exception_type(Exception)`.**

---

## ADR-002: PubMed must fail open — never propagate HTTP 500

**Status:** Accepted — implemented 2026-04-10

**Context:**
`HybridRAGPipeline._search_pubmed()` called `Entrez.esearch()` with no timeout.
Biopython's internal retry loop (`max_tries=3`, `sleep_between_tries=15 s`) could block
a request thread for 45+ s. A slow NCBI endpoint would cause all chat requests that
triggered PubMed to time out the client.

**Decision:**
1. Set `Entrez.max_tries = 1` around PubMed calls (restore original value in `finally`).
2. Catch `(urllib.error.URLError, OSError)` explicitly before the broad `except Exception`.
3. All PubMed errors return `[]` (empty list) — never raise.

**Consequences:**
- PubMed is permanently best-effort.
- A full hard timeout (e.g. 5 s wall-clock) is not achievable without threads or
  `socket.setdefaulttimeout` — documented as known limitation.
- **Any future PubMed integration must preserve the fail-open contract.**

---

## ADR-003: Live sources (PubMed, Scholar) gated on freshness check

**Status:** Accepted — implemented 2026-04-10

**Context:**
`chat_rag_service.py` originally called `hybrid_rag.retrieve(use_pubmed=True,
use_scholar=True)` on every request. PubMed adds ~1-2 s per call under ideal conditions;
Scholar adds a similar round-trip. Routine queries that can be served from CAG/Qdrant
paid this cost unconditionally.

**Decision:**
Live sources are only enabled when `_query_prefers_live_sources(question)` returns `True`.
This function checks for freshness terms: "latest", "recent", "new", "updated", "current",
"guideline update", "new evidence", "today", "2024", "2025", "2026".

**Consequences:**
- Routine queries: only CAG + Qdrant (~50-200 ms).
- Freshness queries: CAG + Qdrant + PubMed + Scholar.
- **Do not change `use_pubmed=True` unconditionally again.**
- The freshness term list (`_query_prefers_live_sources`) is in both `chat_rag_service.py`
  and `chatbot_v2/retrieval.py` — keep them in sync.

---

## ADR-004: Two deploy paths exist — Docker and native Python

**Status:** Accepted — confirmed 2026-04-11

**Context:**
The repository contains both a `render.yaml` (`env: python`, native build) and an
`api/Dockerfile`. Render hosts two separate services from the same repo.

**Decision / Fact:**

| Service | Build path | Requirements file | Start command |
|---|---|---|---|
| `mediai-api` (native) | `render.yaml` `env: python` | `requirements-prod.txt` (repo root) | `cd api && uvicorn main:app` |
| Docker service (active failure service) | `api/Dockerfile` | `api/requirements-prod.txt` | `uvicorn main:app --host 0.0.0.0 --port 8000` |

Both `requirements-prod.txt` files are byte-for-byte identical.

**Consequences:**
- Dependency changes must be applied to **both** `requirements-prod.txt` and
  `api/requirements-prod.txt` to keep both services working.
- Docker service changes (Dockerfile edits) do **not** affect the native service.
- The Docker build context is `api/` — `COPY requirements-prod.txt .` resolves relative
  to that directory.

---

## ADR-005: Production dependency set is intentionally minimal

**Status:** Accepted — confirmed 2026-04-10

**Context:**
Render free plan has a build time limit and memory constraints. Heavy packages cause
build failure or OOM.

**Removed intentionally:**

| Package | Why removed | Impact |
|---|---|---|
| `sentence-transformers` + torch | ~2 GB, OOM on free tier | Qdrant disabled |
| `qdrant-client` | grpcio C extension, build fails | Vector search disabled |
| `biopython` | Build size; lazy import anyway | PubMed disabled |
| `spacy` + presidio | PII redaction optional | PII redaction disabled |
| `langchain` (main) | Pulls langgraph → ormsgpack Rust fail | Use langchain-core/community/groq only |
| `shap` | Lazy import in prediction_explainer | Explainability disabled |

**Do not add these back without testing the Docker build locally first.**
