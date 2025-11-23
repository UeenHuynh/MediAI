# Browser Extension Solution - Hide Streamlit Sidebar Navigation

Since Streamlit blocks CSS/JavaScript injection from within the app, we use a **browser extension** to inject CSS client-side.

## ✅ Recommended: Stylus (Easiest for CSS)

### Step 1: Install Stylus

**For Brave/Chrome:**
1. Go to: https://chrome.google.com/webstore/detail/stylus/clngdbkpkpeebahjckkjfobafhncgmne
2. Click "Add to Brave" / "Add to Chrome"
3. Confirm installation

**For Firefox:**
1. Go to: https://addons.mozilla.org/en-US/firefox/addon/styl-us/
2. Click "Add to Firefox"

### Step 2: Create Custom Style

1. **Open Streamlit app:** http://localhost:8501
2. **Click Stylus icon** in browser toolbar
3. **Click "Write style for: localhost"**
4. **Paste this CSS:**

```css
/* Hide ALL Streamlit default navigation */
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavLink"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNav"] *,
[data-testid="stSidebarNavLink"] *,
[data-testid="stSidebarNavItems"] * {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    opacity: 0 !important;
}

/* Hide specific emotion-cache classes */
div.st-emotion-cache-79elbk,
.st-emotion-cache-79elbk,
div.eczjsme10,
.eczjsme10 {
    display: none !important;
}

/* Hide any navigation in sidebar */
section[data-testid="stSidebar"] nav:not([id="custom-nav"]),
[class*="SidebarNav"],
[class*="sidebar-nav"],
[data-testid*="Nav"]:not([data-testid*="Radio"]) {
    display: none !important;
}
```

5. **Name it:** "MediAI - Hide Navigation"
6. **Save** (Ctrl+S)
7. **Reload** the Streamlit page (F5)

### Step 3: Verify

1. **Check sidebar** - Should only see custom navigation with icons:
   - 🏠 Dashboard
   - 🔬 Predict Sepsis
   - 💔 Predict Mortality
   - 📊 Model Performance
   - ⚙️ Settings

2. **NO default navigation** (auth, dashboard, etc.)

---

## Alternative: Tampermonkey (For JavaScript)

If you prefer JavaScript (more powerful):

### Step 1: Install Tampermonkey

**For Brave/Chrome:**
https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo

### Step 2: Create Userscript

1. Click Tampermonkey icon → **Create a new script**
2. Paste this code:

```javascript
// ==UserScript==
// @name         MediAI - Hide Streamlit Navigation
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Hide default Streamlit sidebar navigation
// @author       You
// @match        http://localhost:8501/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    function removeNav() {
        const selectors = [
            '[data-testid="stSidebarNav"]',
            '[data-testid="stSidebarNavLink"]',
            '[data-testid="stSidebarNavItems"]'
        ];

        let removed = 0;
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                if (el) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    el.remove();
                    removed++;
                    console.log('✅ Removed:', selector);
                }
            });
        });

        return removed;
    }

    // Run immediately
    removeNav();

    // Run on DOM changes
    const observer = new MutationObserver(() => {
        removeNav();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    console.log('🚀 MediAI Navigation Remover Active');
})();
```

3. **Save** (Ctrl+S)
4. **Reload** Streamlit page

---

## 📊 Comparison

| Feature | Stylus | Tampermonkey |
|---------|--------|--------------|
| **Ease of use** | ⭐⭐⭐⭐⭐ Very easy | ⭐⭐⭐ Medium |
| **CSS only** | ✅ Yes | ✅ Yes (via JS) |
| **JavaScript** | ❌ No | ✅ Yes |
| **Performance** | ⚡ Fastest | ⚡ Fast |
| **Debugging** | Easy (DevTools) | Medium (Console) |

**Recommendation:** Use **Stylus** for this use case (CSS-only solution).

---

## 🔧 Troubleshooting

### Stylus not working?

1. **Check if enabled:**
   - Click Stylus icon
   - Make sure your style is **ON** (toggle switch)

2. **Check URL matching:**
   - Style should apply to `localhost` or your domain
   - Edit style → Check "URLs on the domain" or "URLs starting with"

3. **Reload page:**
   - Hard refresh: Ctrl+Shift+R

### Still seeing navigation?

1. **Inspect element** (F12)
2. **Check Computed styles**
3. **See if CSS is applied**
4. **Try more specific selectors:**

```css
/* Nuclear option - hide EVERYTHING in sidebar except radio buttons */
section[data-testid="stSidebar"] > div > div:first-child {
    display: none !important;
}

/* Keep only our custom nav (radio group) */
section[data-testid="stSidebar"] [data-testid*="stRadio"] {
    display: block !important;
}
```

---

## 🎯 Why This Works

**Problem:** Streamlit blocks CSS/JS injection from `st.markdown()` and `components.html()`

**Solution:** Browser extension runs **OUTSIDE** Streamlit's control:
- ✅ Injects CSS directly into page
- ✅ Runs JavaScript in page context
- ✅ Has full DOM access
- ✅ Persists across reloads
- ✅ No Streamlit restrictions

---

## 📦 Export/Import Style

### Export (Share with team):

1. Stylus → Manage
2. Find your style
3. Click "Export" → Save as `.json`

### Import:

1. Stylus → Manage
2. Click "Import" → Select `.json` file

---

## 🚀 Quick Start (Copy-Paste Ready)

**Stylus CSS (Recommended):**
```css
[data-testid="stSidebarNavLink"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
```

**Tampermonkey JS:**
```javascript
setInterval(() => {
    document.querySelectorAll('[data-testid="stSidebarNavLink"]').forEach(el => el.remove());
}, 100);
```

---

## ✅ Success Criteria

After setup, you should see:

**✅ ONLY custom navigation:**
- 🏠 Dashboard
- 🔬 Predict Sepsis
- 💔 Predict Mortality
- 📊 Model Performance
- ⚙️ Settings

**❌ NO default navigation:**
- auth
- dashboard
- model performance
- predict mortality
- predict sepsis
- settings

---

## 📞 Support

If you still have issues:
1. Check DevTools Console for errors
2. Verify CSS selectors match your Streamlit version
3. Try different browser (Chrome, Firefox, Edge)
4. Check if Streamlit version is compatible

---

## 🎓 Learn More

- Stylus Documentation: https://github.com/openstyles/stylus/wiki
- Tampermonkey: https://www.tampermonkey.net/documentation.php
- Streamlit Theming: https://docs.streamlit.io/library/advanced-features/theming

---

**Last Updated:** 2025-01-23
**Tested On:** Streamlit 1.29+, Brave/Chrome, Firefox
