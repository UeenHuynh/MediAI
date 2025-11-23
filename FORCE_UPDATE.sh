#!/bin/bash

echo "🚨 FORCE UPDATE TO LATEST CODE"
echo "======================================"
echo ""

cd /home/user/MediAI

# Show current state
echo "📊 Current state:"
echo "   Branch: $(git branch --show-current)"
echo "   Commit: $(git log --oneline -1)"
echo ""

# Kill ALL Streamlit processes EVERYWHERE
echo "1️⃣ Killing ALL Streamlit processes..."
pkill -9 -f streamlit 2>/dev/null || true
pkill -9 -f "python.*streamlit" 2>/dev/null || true
sleep 3
echo "   ✅ Done"
echo ""

# Clear ALL caches
echo "2️⃣ Clearing ALL caches..."
rm -rf ~/.streamlit 2>/dev/null || true
rm -rf /root/.streamlit 2>/dev/null || true
rm -rf /home/*/.streamlit 2>/dev/null || true
rm -rf apps/.streamlit/cache 2>/dev/null || true
rm -rf apps/__pycache__ 2>/dev/null || true
rm -rf apps/pages/__pycache__ 2>/dev/null || true
find apps/ -name "*.pyc" -delete 2>/dev/null || true
find apps/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo "   ✅ Done"
echo ""

# Pull latest code
echo "3️⃣ Pulling LATEST code..."
git fetch origin claude/remove-sidebar-navigation-01A7WbNPi3eL6PmNB3GTT7KH
git reset --hard origin/claude/remove-sidebar-navigation-01A7WbNPi3eL6PmNB3GTT7KH
echo "   ✅ Done"
echo ""

# Show new state
echo "📊 New state:"
echo "   Commit: $(git log --oneline -1)"
echo ""

# Verify files
echo "4️⃣ Verifying files..."
cd apps

echo "   Main file exists:"
ls -lh streamlit_app.py

echo ""
echo "   Checking for OLD navigation code (radio, sidebar):"
if grep -q "st.radio.*Dashboard\|st.sidebar.*radio\|nav_options" streamlit_app.py; then
    echo "   ❌ ERROR: OLD NAVIGATION CODE FOUND!"
    grep -n "st.radio\|st.sidebar\|nav_options" streamlit_app.py | head -10
    exit 1
else
    echo "   ✅ No old navigation code!"
fi

echo ""
echo "   Pages:"
ls -1 pages/*.py

echo ""
echo "======================================"
echo "✅ CODE IS LATEST VERSION"
echo ""
echo "🚀 TO START STREAMLIT:"
echo "   cd /home/user/MediAI/apps"
echo "   streamlit run streamlit_app.py --server.port 8501"
echo ""
echo "⚠️  CRITICAL: Open browser in INCOGNITO or HARD REFRESH (Ctrl+Shift+R)"
echo "   Browser cache can show old navigation!"
echo ""
