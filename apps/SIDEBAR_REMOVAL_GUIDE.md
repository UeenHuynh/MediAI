# Complete Guide: Removing Default Streamlit Sidebar Navigation

This document explains **ALL the techniques** used to completely remove Streamlit's default sidebar navigation and show ONLY our custom navigation menu.

## 🎯 Goal

**REMOVE:** Default Streamlit sidebar navigation (auth, dashboard, model performance, predict mortality, predict sepsis, settings)

**KEEP:** Custom navigation menu with icons (🏠 Dashboard, 🔬 Predict Sepsis, 💔 Predict Mortality, 📊 Model Performance, ⚙️ Settings)

## 🔧 Complete Solution (Multi-Layered Approach)

We use **5 different techniques** working together to ensure the default navigation is completely hidden:

### 1. Directory Structure ✅

**WHY:** Streamlit automatically creates sidebar navigation when it detects a `pages/` directory.

**SOLUTION:** Use `views/` instead of `pages/`

```
apps/
├── streamlit_app.py    # Main single-page app
└── views/              # NOT "pages/" - prevents auto-detection
    ├── dashboard.py
    ├── predict_sepsis.py
    └── ...
```

**CRITICAL:** Never create a `pages/` directory with Python files!

### 2. Configuration Files ✅

**File: `.streamlit/config.toml`**

```toml
[client]
showSidebarNavigation = false

[ui]
hideSidebarNav = true
```

**File: `.pages.toml`** (root of apps directory)

```toml
# Empty file - explicitly tells Streamlit: NO PAGES
```

### 3. CSS Hiding ✅

**File: `streamlit_app.py`**

Aggressive CSS with `!important` flags:

```css
[data-testid="stSidebarNav"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}

[data-testid="stSidebarNav"] ul {
    display: none !important;
}

[data-testid="stSidebarNav"] li {
    display: none !important;
}

section[data-testid="stSidebarNav"] {
    display: none !important;
}
```

### 4. JavaScript Removal ✅

**File: `streamlit_app.py`**

Forcefully removes elements using JavaScript:

```javascript
// Run on page load
window.addEventListener('load', function() {
    const selectors = [
        '[data-testid="stSidebarNav"]',
        'section[data-testid="stSidebarNav"]',
        'div[data-testid="stSidebarNav"]'
    ];

    selectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            if (el) {
                el.remove();  // Completely remove from DOM
            }
        });
    });
});

// Also run periodically (every 100ms) to catch re-renders
setInterval(function() {
    const navElements = document.querySelectorAll('[data-testid="stSidebarNav"]');
    navElements.forEach(el => {
        if (el) el.remove();
    });
}, 100);
```

### 5. Single-Page App Architecture ✅

**WHY:** Multi-page apps automatically generate navigation.

**SOLUTION:** Build as single-page app with manual view loading:

```python
# streamlit_app.py
if st.session_state.current_page == "🏠 Dashboard":
    from views import dashboard
    dashboard.show()
elif st.session_state.current_page == "🔬 Predict Sepsis":
    from views import predict_sepsis
    predict_sepsis.show()
# ... etc
```

## 🧪 How to Test

### Step 1: Clear Everything
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/cache/

# Clear browser cache
# Ctrl+Shift+Delete (Chrome/Firefox)
```

### Step 2: Run the App
```bash
cd /home/user/MediAI/apps
streamlit run streamlit_app.py --server.port 8501
```

### Step 3: Verify
1. **Open browser:** http://localhost:8501
2. **Hard refresh:** Ctrl+Shift+R (or Cmd+Shift+R on Mac)
3. **Check sidebar:** Should ONLY see custom navigation menu with icons
4. **Inspect browser:** F12 → Elements → Search for `stSidebarNav` (should be 0 results or hidden)

## ❌ Common Mistakes That Break It

### Mistake 1: Using `pages/` Directory
```
❌ apps/pages/dashboard.py     # Streamlit auto-detects
✅ apps/views/dashboard.py     # Safe from auto-detection
```

### Mistake 2: Not Hard Refreshing Browser
- Browser caches old Streamlit navigation
- **Solution:** Always hard refresh (Ctrl+Shift+R)

### Mistake 3: Missing Configuration
- Make sure `.streamlit/config.toml` exists
- Make sure `.pages.toml` exists
- **Solution:** Check both files are present

### Mistake 4: Wrong `initial_sidebar_state`
```python
❌ initial_sidebar_state="collapsed"  # Hides sidebar completely
✅ initial_sidebar_state="expanded"   # Shows sidebar with our nav
```

## 🔍 Debugging Steps

If you STILL see default navigation:

### 1. Check Directory Structure
```bash
ls -la apps/
# Should NOT see "pages/" directory
# Should see "views/" directory
```

### 2. Check Browser DevTools
```
F12 → Console
Type: document.querySelectorAll('[data-testid="stSidebarNav"]')
Result should be: NodeList(0) [] or elements with display:none
```

### 3. Check Streamlit Version
```bash
streamlit --version
# Should be >= 1.29.0 for best compatibility
```

### 4. Check Files Are Loaded
```
F12 → Network → Reload page
Check: streamlit_app.py loads
Check: CSS is injected
Check: JavaScript runs (no errors in Console)
```

### 5. Nuclear Option - Complete Reset
```bash
# Stop Streamlit
pkill -f streamlit

# Clear all caches
rm -rf ~/.streamlit/
rm -rf .streamlit/cache/

# Clear browser cache completely
# Restart browser

# Run again
streamlit run streamlit_app.py --server.port 8501
```

## 📊 Verification Checklist

Before declaring success, verify:

- [ ] No `pages/` directory exists
- [ ] `.streamlit/config.toml` has navigation disabled
- [ ] `.pages.toml` exists (can be empty)
- [ ] CSS in `streamlit_app.py` has `!important` flags
- [ ] JavaScript removal code is present
- [ ] Browser hard refreshed (Ctrl+Shift+R)
- [ ] DevTools shows no `stSidebarNav` elements (or hidden)
- [ ] Sidebar shows ONLY custom navigation with icons
- [ ] No text-only navigation items visible

## 🎓 Why This Is Necessary

Streamlit's multi-page app feature is **very aggressive** about showing navigation:

1. **Auto-detection:** Automatically creates nav from `pages/` directory
2. **CSS Override:** Regular CSS can be overridden by Streamlit's own styles
3. **Dynamic Rendering:** Streamlit re-renders components, re-creating hidden elements
4. **Configuration Defaults:** Default settings favor showing navigation

Therefore, we need **multiple layers of defense**:
- Directory naming (prevent detection)
- Configuration (disable features)
- CSS (hide visually)
- JavaScript (remove from DOM)
- Architecture (single-page app)

## ✅ Success Criteria

When working correctly, you should see:

**Sidebar:**
- ✅ "Navigation" header
- ✅ 🏠 Dashboard (radio button)
- ✅ 🔬 Predict Sepsis (radio button)
- ✅ 💔 Predict Mortality (radio button)
- ✅ 📊 Model Performance (radio button)
- ✅ ⚙️ Settings (radio button)
- ✅ Version and Status info

**NOT in Sidebar:**
- ❌ auth
- ❌ dashboard (text only)
- ❌ model performance (text only)
- ❌ predict mortality (text only)
- ❌ predict sepsis (text only)
- ❌ settings (text only)

## 📞 Still Having Issues?

If default navigation still appears:

1. **Screenshot the sidebar** - Compare with success criteria above
2. **Check browser console** - Look for JavaScript errors
3. **Inspect element** - Right-click sidebar → Inspect → Check for `stSidebarNav`
4. **Verify files** - Make sure all files match this guide
5. **Try different browser** - Test in Chrome, Firefox, or Edge

The solution in this repo uses **all 5 techniques** simultaneously. This is the most aggressive approach possible to hide Streamlit's default navigation.
