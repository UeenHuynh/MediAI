# Chatbot Debug Runbook

Last updated: 2026-04-11

---

## 0. Prerequisites

```bash
BASE="https://mediai-7owz.onrender.com"   # Docker service (active)
TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=demo&password=demo123' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
```

Check service is up before any test:
```bash
curl -s "$BASE/health" | python3 -m json.tool
# Expected: {"status":"healthy",...}
```

---

## 1. Standard smoke test (generic query)

```bash
curl -s -X POST "$BASE/api/v1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"sepsis management","session_id":"smoke-1","include_sources":true}' \
  | python3 -m json.tool
```

**Pass criteria:**
- HTTP 200
- `answer` is non-empty, clinically relevant
- `processing_time_ms` < 8000
- `citations` list present (may be empty if CAGCache not populated)

**Fail signals:**
- `answer` starts with "I apologize" → LLM failed silently; check `error` field in server logs
- `processing_time_ms` > 11000 → tenacity retrying; likely auth/quota issue
- HTTP 500 → unhandled exception; check `/health` component status

---

## 2. Freshness-query test (live sources gate)

```bash
curl -s -X POST "$BASE/api/v1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"latest sepsis guidelines 2026","session_id":"smoke-fresh","include_sources":true}' \
  | python3 -m json.tool
```

**Pass criteria:**
- HTTP 200
- `processing_time_ms` may be higher (Scholar round-trip ~1-3 s)
- If Scholar is reachable, at least one citation should have `"source_type":"live_api"`

**Fail signals:**
- `citations[*].tier` all null → CAGCache empty AND Scholar unreachable; query path degraded to pure LLM
- `processing_time_ms` > 20000 → PubMed blocking despite timeout fix; check if biopython somehow reinstalled

---

## 3. Auth-failure test (fail-fast check)

```bash
time curl -s -X POST "$BASE/api/v1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer INVALID_TOKEN" \
  -d '{"message":"sepsis"}'
```

**Pass criteria:**
- HTTP 401, `{"detail":"Could not validate credentials"}`
- Wall-clock time < 1 s

**Fail signals:**
- HTTP 200 with apology text and latency > 10 s → GroqAuthError still being retried (regression of H2 fix)

---

## 4. Live-source failure / fail-open test

```bash
curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$BASE/api/v1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"GIBBERISH_QUERY_THAT_MATCHES_NOTHING_XYZ_123"}'
```

**Pass criteria:**
- HTTP 200 (never 500)
- `answer` is a generic disclaimer or "unable to find specific information"
- No timeout > 35 s

**Fail signals:**
- HTTP 500 → retrieval exception propagated; check `hybrid_rag.py` and `chatbot_v2/retrieval.py`

---

## 5. Trace / observability check

After any of the above tests, verify server logs contain:
```
RETRIEVAL_TRACE used_cag=... used_qdrant=... used_pubmed=... used_scholar=... docs=... wants_live=... legacy_path=...
LLM_TRACE provider=... model=... fallback_used=... error=...
```

If these lines are missing: the trace changes in `chatbot_v2/retrieval.py` and
`chatbot_v2/chatbot.py` were not deployed. Re-check the active deploy commit.

---

## 6. Deploy verification steps

1. Push commit to `main`.
2. Render triggers auto-deploy on the **Docker service** (the one with `api/Dockerfile`).
   The **native Python service** (`render.yaml`, `env: python`) is a separate service — it
   also auto-deploys but uses different config.
3. Watch Render build log for:
   - `COPY requirements-prod.txt .` — confirms correct Dockerfile is running
   - `Successfully installed ...` — no conflict errors
   - `Uvicorn running on ...` — server started
4. Hit `/health` — wait for `"status":"healthy"` before running smoke tests.
5. Run smoke test 1 and check server logs for `RETRIEVAL_TRACE` and `LLM_TRACE` lines.

---

## 7. Known permanent limitations (as of 2026-04-11)

| Limitation | Root cause | Fix path |
|---|---|---|
| PubMed always disabled | `biopython` not in `requirements-prod.txt` | Add biopython; test build size |
| Qdrant always disabled | `qdrant-client` not in `requirements-prod.txt` | Requires Qdrant instance + embeddings |
| `tier=null` on all citations | CAGCache not populated with matching docs | Populate CAGCache with clinical knowledge base |
| `model_name` not in HTTP response | `ChatResponse` schema does not include it | Extend `ChatResponse` if needed |
