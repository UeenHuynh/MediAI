# MediAI — Claude Code Rules

## Source of truth files

| File | Purpose |
|---|---|
| `render.yaml` | Native Python service config (env vars, build/start commands) |
| `requirements-prod.txt` | Root — used by native Render service |
| `api/requirements-prod.txt` | Used by Docker service (`api/Dockerfile`) — must stay in sync with root |
| `api/Dockerfile` | Docker build — active failing/fixed service on Render |
| `docs/debug/chatbot-incident.md` | Living incident log — append every debug result here |
| `docs/runbooks/chatbot-debug.md` | Smoke tests and deploy verification steps |
| `docs/adr/chatbot-architecture-decisions.md` | Hard architecture rules with rationale |

## Standard commands

```bash
# Health check
curl -s https://mediai-7owz.onrender.com/health | python3 -m json.tool

# Get token
TOKEN=$(curl -s -X POST https://mediai-7owz.onrender.com/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=demo&password=demo123' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

# Smoke test
curl -s -X POST https://mediai-7owz.onrender.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"sepsis management","session_id":"smoke-1"}' | python3 -m json.tool
```

## Hard rules

1. **Groq AuthenticationError must not be retried.** Tenacity uses `retry_if_not_exception_type(GroqAuthError)`. Do not revert this.
2. **PubMed must fail open.** Any PubMed exception → return `[]`. Never propagate.
3. **Live sources (PubMed, Scholar) are gated on `_query_prefers_live_sources()`.** Do not enable them unconditionally.
4. **Both `requirements-prod.txt` files must stay in sync.** Edit both or edit neither.
5. **The Docker build context is `api/`.** `COPY` paths in `api/Dockerfile` are relative to `api/`.

## Areas not to touch casually

- `api/routers/chat.py` — only edit when services-layer diagnosis is confirmed wrong
- `api/services/langchain_medical_bot.py` — tenacity retry decorator is intentional
- `api/services/hybrid_rag.py` — PubMed timeout fix (`max_tries=1`) must stay
- `api/services/chat_rag_service.py` — `wants_live` gate must stay
- Either `requirements-prod.txt` file — no heavy packages without testing Docker build locally
