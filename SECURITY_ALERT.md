# 🚨 SECURITY ALERT - API Keys Exposed

**Date:** 2025-12-04
**Severity:** HIGH
**Status:** MITIGATED (keys removed from repo)

---

## ⚠️ Exposed Credentials

The following API keys were accidentally committed to the public repository in file `RAG_SYSTEM_COMPLETE.md`:

### 1. Google API Key (Gemini)
```
AIzaSyCq_xPmvDyvJ98Y4Q63XBVEazm6fVyDX5k
```

**Service:** Google Cloud / Gemini API
**Exposure Duration:** Unknown (check git history)
**Risk:** High - Can be used to make API calls on your account

### 2. DeepSeek API Key
```
sk-bdb799d9bd6845ec8004c68bfc2f06dc
```

**Service:** DeepSeek Platform
**Exposure Duration:** Unknown (check git history)
**Risk:** High - Can consume your API credits

---

## ✅ Immediate Actions Taken

1. ✅ Removed `RAG_SYSTEM_COMPLETE.md` from git repository
2. ✅ Pushed changes to remote (commit: 209b723)
3. ✅ Created this security alert

---

## 🔥 URGENT: Actions YOU Must Take NOW

### Step 1: Revoke Google API Key (Gemini)

```bash
# Go to Google Cloud Console
https://console.cloud.google.com/apis/credentials

# Steps:
1. Find the API key: AIzaSyCq_xPmvDyvJ98Y4Q63XBVEazm6fVyDX5k
2. Click "Delete" or "Restrict"
3. Create a NEW API key
4. Update your local .env file with new key
5. DO NOT commit the new key
```

### Step 2: Revoke DeepSeek API Key

```bash
# Go to DeepSeek Platform
https://platform.deepseek.com/api_keys

# Steps:
1. Find the key: sk-bdb799d9bd6845ec8004c68bfc2f06dc
2. Click "Delete" or "Revoke"
3. Create a NEW API key
4. Update your local .env file with new key
5. DO NOT commit the new key
```

### Step 3: Check for Unauthorized Usage

```bash
# Google Cloud Console
https://console.cloud.google.com/apis/dashboard
# Check for unusual API calls in the last few days

# DeepSeek Platform
https://platform.deepseek.com/usage
# Check for unexpected usage
```

### Step 4: Update Local Environment

```bash
# Edit .env file (NEVER commit this file)
nano .env

# Replace old keys with new keys:
GOOGLE_API_KEY=your_new_google_key_here
DEEPSEEK_API_KEY=your_new_deepseek_key_here
```

### Step 5: Verify .gitignore

```bash
# Ensure .env is in .gitignore
grep "^\.env$" .gitignore || echo ".env" >> .gitignore

# Verify .env is NOT tracked
git ls-files | grep "^\.env$" && echo "WARNING: .env is tracked!" || echo "OK: .env not tracked"
```

---

## 🛡️ Prevention for Future

### 1. Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Check for potential secrets before commit

echo "🔍 Checking for secrets..."

# Check for common API key patterns
if git diff --cached --name-only | xargs grep -E 'sk-[a-zA-Z0-9]{32,}|AIza[a-zA-Z0-9_-]{35}|gsk_[a-zA-Z0-9]{52}' 2>/dev/null; then
    echo "❌ ERROR: Potential API key found in staged files!"
    echo "Please remove API keys before committing."
    exit 1
fi

echo "✅ No secrets detected"
exit 0
```

```bash
chmod +x .git/hooks/pre-commit
```

### 2. Use git-secrets

```bash
# Install git-secrets
brew install git-secrets  # macOS
# or
sudo apt-get install git-secrets  # Linux

# Initialize
git secrets --install
git secrets --register-aws

# Add custom patterns
git secrets --add 'AIza[0-9A-Za-z_-]{35}'
git secrets --add 'sk-[a-zA-Z0-9]{32,}'
git secrets --add 'gsk_[a-zA-Z0-9]{52}'
```

### 3. GitHub Secret Scanning

Enable on your repository:
1. Go to: Settings → Code security and analysis
2. Enable "Secret scanning"
3. Enable "Push protection"

### 4. Environment Variable Management

**NEVER:**
- ❌ Commit .env files
- ❌ Put API keys in code
- ❌ Share API keys in docs (use placeholders)
- ❌ Post API keys in issues/PRs

**ALWAYS:**
- ✅ Use .env files (gitignored)
- ✅ Use placeholders in examples (`your_key_here`, `xxxxx`)
- ✅ Use environment variables
- ✅ Rotate keys regularly

---

## 📊 Impact Assessment

### Potential Risks

1. **Unauthorized API Usage**
   - Someone could have used your keys
   - Check billing for unexpected charges

2. **Data Access**
   - Depending on API permissions, data could be accessed
   - Review API key restrictions in console

3. **Quota Exhaustion**
   - Keys could be used to exhaust your free tier
   - Monitor usage quotas

### Recommended Actions

- [ ] Check Google Cloud billing: https://console.cloud.google.com/billing
- [ ] Check DeepSeek usage: https://platform.deepseek.com/usage
- [ ] Review recent API calls in logs
- [ ] Set up billing alerts
- [ ] Enable API restrictions (IP, referrer, etc.)

---

## 📝 Git History Cleanup (Optional but Recommended)

**WARNING:** This rewrites git history and requires force push!

```bash
# Use BFG Repo-Cleaner to remove keys from history
# Download: https://rtyley.github.io/bfg-repo-cleaner/

# 1. Create backup
git clone https://github.com/UeenHuynh/MediAI.git MediAI-backup

# 2. Clone fresh copy
git clone https://github.com/UeenHuynh/MediAI.git MediAI-clean
cd MediAI-clean

# 3. Run BFG to remove keys
bfg --replace-text secrets.txt  # Create secrets.txt with keys to remove

# 4. Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push (CAUTION!)
git push --force --all origin
git push --force --tags origin
```

**Note:** Coordinate with team before force pushing!

---

## ✅ Verification Checklist

After completing all steps:

- [ ] Old Google API key revoked
- [ ] Old DeepSeek API key revoked
- [ ] New keys generated
- [ ] New keys added to .env (local only)
- [ ] .env is in .gitignore
- [ ] .env is NOT tracked by git
- [ ] Checked for unauthorized usage
- [ ] Set up billing alerts
- [ ] Installed pre-commit hook
- [ ] Enabled GitHub secret scanning
- [ ] Informed team members (if applicable)

---

## 📞 Support

If you need help or suspect malicious usage:

- **Google Cloud Support:** https://cloud.google.com/support
- **DeepSeek Support:** https://platform.deepseek.com/support
- **GitHub Security:** https://github.com/security

---

**Created:** 2025-12-04
**Priority:** URGENT
**Action Required:** YES - Revoke keys immediately
**File Removed:** RAG_SYSTEM_COMPLETE.md (commit 209b723)
