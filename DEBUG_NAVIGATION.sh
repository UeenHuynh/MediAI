#!/bin/bash

echo "🔍 COMPREHENSIVE NAVIGATION DEBUG"
echo "=========================================="
echo ""

# Part 1: Find ALL Streamlit processes
echo "1️⃣ Searching for ALL Streamlit processes..."
echo ""
ps aux | grep -i streamlit | grep -v grep > /tmp/streamlit_processes.txt

if [ -s /tmp/streamlit_processes.txt ]; then
    echo "   ⚠️  FOUND RUNNING STREAMLIT PROCESSES:"
    cat /tmp/streamlit_processes.txt
    echo ""
    echo "   These processes may be running OLD CODE!"
    echo "   You MUST kill them first."
    echo ""
else
    echo "   ✅ No Streamlit processes running"
    echo ""
fi

# Part 2: Check for any Python files with navigation code
echo "2️⃣ Searching for navigation code in system..."
echo ""
find /home/user -name "*.py" -type f 2>/dev/null | xargs grep -l "st.sidebar.*radio\|Navigation.*Dashboard" 2>/dev/null | head -10 > /tmp/nav_files.txt

if [ -s /tmp/nav_files.txt ]; then
    echo "   ⚠️  FOUND FILES WITH NAVIGATION CODE:"
    cat /tmp/nav_files.txt
    echo ""
    echo "   One of these files may be running!"
else
    echo "   ✅ No navigation code found in system"
    echo ""
fi

# Part 3: Verify THIS repository code
echo "3️⃣ Verifying CODE IN THIS REPOSITORY..."
echo ""
cd /home/user/MediAI/apps

echo "   Repository location: /home/user/MediAI"
echo "   Current branch: $(git branch --show-current)"
echo "   Latest commit: $(git log --oneline -1)"
echo ""

echo "   Files in pages/:"
ls -1 pages/*.py 2>/dev/null || echo "   ERROR: No pages directory!"
echo ""

echo "   Checking streamlit_app.py for navigation code:"
if grep -q "st.sidebar\|st.radio.*Dashboard\|nav_options" streamlit_app.py 2>/dev/null; then
    echo "   ❌ ERROR: NAVIGATION CODE FOUND IN streamlit_app.py!"
    echo ""
    echo "   Problematic lines:"
    grep -n "st.sidebar\|st.radio\|nav_options" streamlit_app.py | head -20
    echo ""
else
    echo "   ✅ No navigation code in streamlit_app.py (correct!)"
fi
echo ""

echo "   Checking pages/ for navigation code:"
found_nav=false
for f in pages/*.py; do
    if grep -q "st.sidebar\|🏠 Dashboard.*radio\|Navigation" "$f" 2>/dev/null; then
        echo "   ❌ FOUND in $f:"
        grep -n "st.sidebar\|🏠 Dashboard\|Navigation" "$f" | head -5
        found_nav=true
    fi
done

if [ "$found_nav" = false ]; then
    echo "   ✅ No navigation code in pages/ (correct!)"
fi
echo ""

# Part 4: Create code fingerprint
echo "4️⃣ CODE FINGERPRINT (to verify you're running correct version):"
echo ""
echo "   MD5 of streamlit_app.py:"
md5sum streamlit_app.py 2>/dev/null | cut -d' ' -f1
echo ""
echo "   First 5 lines of streamlit_app.py:"
head -5 streamlit_app.py
echo ""

# Part 5: Instructions
echo "=========================================="
echo ""
echo "📋 DIAGNOSIS:"
echo ""

if [ -s /tmp/streamlit_processes.txt ]; then
    echo "❌ PROBLEM FOUND: Streamlit is RUNNING"
    echo ""
    echo "   You have Streamlit processes running that may be using OLD CODE."
    echo "   You MUST kill them first:"
    echo ""
    echo "   pkill -9 -f streamlit"
    echo ""
elif [ -s /tmp/nav_files.txt ]; then
    echo "❌ PROBLEM FOUND: Navigation code exists in system"
    echo ""
    echo "   Found navigation code in files outside this repository."
    echo "   Make sure you're running from: /home/user/MediAI/apps"
    echo ""
else
    echo "✅ NO ISSUES FOUND IN REPOSITORY CODE"
    echo ""
    echo "   The code in this repository is CORRECT."
    echo "   If you're still seeing duplicate navigation:"
    echo ""
    echo "   1. Make sure you're running from THIS directory:"
    echo "      cd /home/user/MediAI/apps"
    echo "      streamlit run streamlit_app.py"
    echo ""
    echo "   2. Clear browser cache or use Incognito mode"
    echo ""
    echo "   3. Verify you're seeing THIS version by checking:"
    echo "      - Home page should say: 'MediAI Healthcare ML Platform'"
    echo "      - Should show 'Welcome to MediAI' section"
    echo "      - Should NOT have navigation with radio buttons"
    echo ""
fi

echo "=========================================="
echo ""

# Cleanup
rm -f /tmp/streamlit_processes.txt /tmp/nav_files.txt
