#!/bin/bash
# Diagnostic script to verify Streamlit app setup

echo "========================================="
echo "MediAI Streamlit Setup Diagnostic"
echo "========================================="
echo ""

echo "1. Checking directory structure..."
if [ -d "/home/user/MediAI/apps/pages" ]; then
    echo "   ❌ ERROR: pages/ directory exists (should NOT exist)"
    ls -la /home/user/MediAI/apps/pages
else
    echo "   ✅ GOOD: No pages/ directory"
fi

if [ -d "/home/user/MediAI/apps/views" ]; then
    echo "   ✅ GOOD: views/ directory exists"
    echo "   Files in views/:"
    ls -1 /home/user/MediAI/apps/views/*.py | wc -l
    echo "   files found"
else
    echo "   ❌ ERROR: views/ directory missing"
fi

echo ""
echo "2. Checking configuration files..."

if [ -f "/home/user/MediAI/apps/.streamlit/config.toml" ]; then
    echo "   ✅ GOOD: .streamlit/config.toml exists"
    echo "   Checking for showSidebarNavigation setting..."
    if grep -q "showSidebarNavigation.*false" /home/user/MediAI/apps/.streamlit/config.toml; then
        echo "   ✅ GOOD: showSidebarNavigation = false"
    else
        echo "   ⚠️  WARNING: showSidebarNavigation not set to false"
    fi
else
    echo "   ❌ ERROR: .streamlit/config.toml missing"
fi

if [ -f "/home/user/MediAI/apps/.pages.toml" ]; then
    echo "   ✅ GOOD: .pages.toml exists"
else
    echo "   ⚠️  WARNING: .pages.toml missing"
fi

echo ""
echo "3. Checking streamlit_app.py..."

if [ -f "/home/user/MediAI/apps/streamlit_app.py" ]; then
    echo "   ✅ GOOD: streamlit_app.py exists"

    if grep -q "stSidebarNav" /home/user/MediAI/apps/streamlit_app.py; then
        echo "   ✅ GOOD: Contains CSS to hide stSidebarNav"
    else
        echo "   ❌ ERROR: Missing CSS to hide stSidebarNav"
    fi

    if grep -q "from views import" /home/user/MediAI/apps/streamlit_app.py; then
        echo "   ✅ GOOD: Imports from views/ (not pages/)"
    else
        echo "   ⚠️  WARNING: May not be importing from views/"
    fi

    if grep -q "setInterval" /home/user/MediAI/apps/streamlit_app.py; then
        echo "   ✅ GOOD: Contains JavaScript removal code"
    else
        echo "   ⚠️  WARNING: Missing JavaScript removal code"
    fi
else
    echo "   ❌ ERROR: streamlit_app.py missing"
fi

echo ""
echo "4. Checking Python files..."
PAGES_COUNT=$(find /home/user/MediAI/apps -path "*/pages/*.py" 2>/dev/null | wc -l)
VIEWS_COUNT=$(find /home/user/MediAI/apps -path "*/views/*.py" 2>/dev/null | wc -l)

echo "   Python files in pages/: $PAGES_COUNT (should be 0)"
echo "   Python files in views/: $VIEWS_COUNT (should be 6)"

if [ $PAGES_COUNT -eq 0 ]; then
    echo "   ✅ GOOD: No files in pages/"
else
    echo "   ❌ ERROR: Found files in pages/"
fi

if [ $VIEWS_COUNT -ge 5 ]; then
    echo "   ✅ GOOD: Views exist"
else
    echo "   ⚠️  WARNING: Expected at least 5 view files"
fi

echo ""
echo "========================================="
echo "SUMMARY"
echo "========================================="

# Count issues
ERRORS=0
WARNINGS=0

[ -d "/home/user/MediAI/apps/pages" ] && ERRORS=$((ERRORS+1))
[ ! -d "/home/user/MediAI/apps/views" ] && ERRORS=$((ERRORS+1))
[ ! -f "/home/user/MediAI/apps/.streamlit/config.toml" ] && ERRORS=$((ERRORS+1))
[ ! -f "/home/user/MediAI/apps/streamlit_app.py" ] && ERRORS=$((ERRORS+1))
[ $PAGES_COUNT -gt 0 ] && ERRORS=$((ERRORS+1))

echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [ $ERRORS -eq 0 ]; then
    echo ""
    echo "✅ Setup looks CORRECT!"
    echo ""
    echo "Next steps:"
    echo "1. Kill any running Streamlit processes:"
    echo "   pkill -f streamlit"
    echo ""
    echo "2. Clear Streamlit cache:"
    echo "   rm -rf ~/.streamlit/cache/"
    echo ""
    echo "3. Run the app:"
    echo "   cd /home/user/MediAI/apps"
    echo "   streamlit run streamlit_app.py --server.port 8501"
    echo ""
    echo "4. Open browser: http://localhost:8501"
    echo "5. Hard refresh: Ctrl+Shift+R"
else
    echo ""
    echo "❌ Found $ERRORS issue(s) - please fix before running"
fi

echo "========================================="
