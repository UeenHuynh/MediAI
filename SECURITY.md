# Security Best Practices

## API Keys & Secrets Management

### ✅ DO:
- **Use `.env` files for secrets** - Store all API keys in `.env` or `.env.chatbot`
- **Keep `.env` files local only** - These files are already in `.gitignore`
- **Use `.env.example` templates** - Share safe templates without real keys
- **Rotate compromised keys immediately** - If accidentally committed, revoke and regenerate
- **Use environment variables** - Access via `os.getenv("KEY_NAME")`

### ❌ DON'T:
- **Never commit `.env` files** - They contain real API keys
- **Never hardcode secrets in code** - Always use environment variables
- **Never share API keys publicly** - Keep them confidential
- **Never commit sensitive data** - Use `.gitignore` to prevent accidents

## Protected Files

The following files are automatically ignored by git:

```
.env
.env.chatbot
.env.local
.env.*.local
*.key
credentials.json
secrets.json
```

## Setup Instructions

1. **Copy template to create your config:**
   ```bash
   cp .env.chatbot.example .env.chatbot
   ```

2. **Add your API keys:**
   Edit `.env.chatbot` and replace placeholder values with real keys

3. **Verify .gitignore protection:**
   ```bash
   git status
   # Should NOT show .env.chatbot or .env
   ```

## What to Do If You Accidentally Commit Secrets

1. **Immediately revoke the exposed keys** on the provider's website
2. **Generate new API keys**
3. **Remove from git history:**
   ```bash
   git rm --cached .env.chatbot
   git commit -m "security: Remove secrets from tracking"
   ```
4. **Update your local `.env.chatbot` with new keys**

## API Key Providers

- **Groq**: https://console.groq.com/ (Free: 30 req/min)
- **NCBI/PubMed**: https://www.ncbi.nlm.nih.gov/account/
- **Qdrant**: https://cloud.qdrant.io/ (Free: 1GB)
- **HuggingFace**: https://huggingface.co/settings/tokens

## Questions?

If you have security concerns, please open an issue or contact the maintainers privately.
