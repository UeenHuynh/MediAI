#!/bin/bash

echo "🔧 Fixing Streamlit Navigation Issues..."
echo ""

# Step 1: Kill any running Streamlit processes
echo "1️⃣ Stopping all Streamlit processes..."
pkill -9 -f streamlit
sleep 2
echo "   ✅ Done"
echo ""

# Step 2: Clear Streamlit cache
echo "2️⃣ Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache 2>/dev/null
rm -rf /root/.streamlit/cache 2>/dev/null
rm -rf /home/*/.streamlit/cache 2>/dev/null
echo "   ✅ Done"
echo ""

# Step 3: Verify file structure
echo "3️⃣ Verifying file structure..."
cd /home/user/MediAI/apps

echo "   Checking pages/ directory:"
ls -la pages/ | grep "\.py$"

echo ""
echo "   Checking for old views/ directory (should NOT exist):"
if [ -d "views" ]; then
    echo "   ⚠️  WARNING: views/ directory still exists! Removing it..."
    rm -rf views/
    echo "   ✅ Removed"
else
    echo "   ✅ No views/ directory (good!)"
fi

echo ""
echo "   Checking for .pages.toml (should NOT exist):"
if [ -f ".pages.toml" ]; then
    echo "   ⚠️  WARNING: .pages.toml still exists! Removing it..."
    rm -f .pages.toml
    echo "   ✅ Removed"
else
    echo "   ✅ No .pages.toml file (good!)"
fi

echo ""

# Step 4: Verify current branch
echo "4️⃣ Verifying git branch..."
git branch --show-current
echo ""

# Step 5: Pull latest changes
echo "5️⃣ Pulling latest changes..."
git pull origin claude/remove-sidebar-navigation-01A7WbNPi3eL6PmNB3GTT7KH
echo "   ✅ Done"
echo ""

# Step 6: Start Streamlit
echo "6️⃣ Starting Streamlit..."
echo ""
echo "   🚀 Running: streamlit run streamlit_app.py --server.port 8501"
echo "   📱 Open: http://localhost:8501"
echo ""
echo "   Expected navigation:"
echo "   ├─ 🏥 MediAI Healthcare ML Platform (home)"
echo "   ├─ 🏠 Dashboard"
echo "   ├─ 🔬 Predict Sepsis"
echo "   ├─ 💔 Predict Mortality"
echo "   ├─ 📊 Model Performance"
echo "   └─ ⚙️ Settings"
echo ""

cd /home/user/MediAI/apps
streamlit run streamlit_app.py --server.port 8501
