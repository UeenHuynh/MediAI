#!/bin/bash

set -e

echo "🔧 FORCE CLEAN & VERIFY NAVIGATION"
echo "=================================="
echo ""

cd /home/user/MediAI/apps

# Step 1: Kill ALL Streamlit processes
echo "1️⃣ Killing ALL Streamlit processes..."
pkill -9 -f streamlit 2>/dev/null || true
pkill -9 -f "python.*streamlit" 2>/dev/null || true
sleep 2
echo "   ✅ Done"
echo ""

# Step 2: Clear ALL caches
echo "2️⃣ Clearing ALL caches..."
rm -rf ~/.streamlit/cache 2>/dev/null || true
rm -rf /root/.streamlit/cache 2>/dev/null || true
rm -rf /home/*/.streamlit/cache 2>/dev/null || true
rm -rf .streamlit/cache 2>/dev/null || true
rm -rf __pycache__ 2>/dev/null || true
rm -rf pages/__pycache__ 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo "   ✅ Done"
echo ""

# Step 3: Pull latest code
echo "3️⃣ Pulling latest code from git..."
cd /home/user/MediAI
git fetch origin claude/remove-sidebar-navigation-01A7WbNPi3eL6PmNB3GTT7KH
git reset --hard origin/claude/remove-sidebar-navigation-01A7WbNPi3eL6PmNB3GTT7KH
echo "   ✅ Done"
echo ""

# Step 4: Verify structure
echo "4️⃣ Verifying file structure..."
cd /home/user/MediAI/apps

echo "   📁 Main file:"
ls -lh streamlit_app.py

echo ""
echo "   📁 Pages directory:"
ls -lh pages/*.py

echo ""
echo "   🔍 Checking for st.set_page_config() in pages (should be NONE):"
if grep -l "st.set_page_config" pages/*.py 2>/dev/null; then
    echo "   ❌ ERROR: Found st.set_page_config() in page files!"
    exit 1
else
    echo "   ✅ No st.set_page_config() in pages (correct!)"
fi

echo ""
echo "   🔍 Checking for old views/ directory (should NOT exist):"
if [ -d "views" ]; then
    echo "   ❌ ERROR: views/ directory still exists!"
    exit 1
else
    echo "   ✅ No views/ directory (correct!)"
fi

echo ""
echo "   🔍 Checking for .pages.toml (should NOT exist):"
if [ -f ".pages.toml" ]; then
    echo "   ❌ ERROR: .pages.toml still exists!"
    exit 1
else
    echo "   ✅ No .pages.toml (correct!)"
fi

echo ""
echo "=================================="
echo "✅ ALL CHECKS PASSED!"
echo ""
echo "📊 Expected navigation (alphabetical, NO emojis in nav):"
echo "   ├─ auth"
echo "   ├─ dashboard"
echo "   ├─ model_performance"
echo "   ├─ predict_mortality"
echo "   ├─ predict_sepsis"
echo "   └─ settings"
echo ""
echo "🎯 Page titles WILL HAVE emojis:"
echo "   - auth → 🔐 Authentication"
echo "   - dashboard → 🏠 Dashboard"
echo "   - model_performance → 📊 Model Performance"
echo "   - predict_mortality → 💔 Predict Mortality Risk"
echo "   - predict_sepsis → 🔬 Predict Sepsis Risk"
echo "   - settings → ⚙️ Settings"
echo ""
echo "🚀 Starting Streamlit..."
echo "   URL: http://localhost:8501"
echo ""

streamlit run streamlit_app.py --server.port 8501 --server.headless true
