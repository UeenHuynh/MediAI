#!/usr/bin/env python3
"""
Diagnostic script to show exactly what Streamlit navigation will display.
"""
import os
import re
from pathlib import Path

def check_pages():
    """Check all page files and show what will be in navigation."""
    print("🔍 NAVIGATION DIAGNOSTIC REPORT")
    print("=" * 60)
    print()

    # Check main app file
    print("📄 Main App File:")
    if os.path.exists("streamlit_app.py"):
        print("   ✅ streamlit_app.py exists")
        print("   → This will be the HOME page (not shown in nav)")
    else:
        print("   ❌ streamlit_app.py NOT FOUND!")
    print()

    # Check pages directory
    print("📁 Pages Directory:")
    pages_dir = Path("pages")
    if not pages_dir.exists():
        print("   ❌ pages/ directory NOT FOUND!")
        return

    page_files = sorted(pages_dir.glob("*.py"))
    if not page_files:
        print("   ❌ No .py files found in pages/!")
        return

    print(f"   ✅ Found {len(page_files)} page files")
    print()

    # Analyze each page file
    print("📊 NAVIGATION WILL SHOW (in alphabetical order):")
    print("-" * 60)
    for i, page_file in enumerate(page_files, 1):
        filename = page_file.name
        # Remove .py extension for display name
        display_name = filename.replace('.py', '')
        # Replace underscores with spaces
        display_name = display_name.replace('_', ' ')

        # Read file to get title
        with open(page_file, 'r') as f:
            content = f.read()

        # Check for st.set_page_config (should NOT be there)
        if 'st.set_page_config' in content:
            print(f"   ❌ {i}. {filename} - CONTAINS st.set_page_config() (ERROR!)")
            continue

        # Find st.title
        title_match = re.search(r'st\.title\(["\'](.+?)["\']\)', content)
        if title_match:
            title = title_match.group(1)
            print(f"   ✅ {i}. Navigation: '{filename.replace('.py', '')}' → Page Title: '{title}'")
        else:
            print(f"   ⚠️  {i}. Navigation: '{filename.replace('.py', '')}' → No title found")

    print()
    print("=" * 60)
    print()

    # Summary
    print("📋 SUMMARY:")
    print()
    print("Streamlit will automatically create navigation from files in pages/")
    print("Navigation names come from FILENAMES (not from st.title)")
    print()
    print("Expected Navigation Sidebar:")
    for page_file in page_files:
        nav_name = page_file.stem  # filename without extension
        print(f"   • {nav_name}")
    print()

    # Check for issues
    print("🔍 CHECKING FOR ISSUES:")
    issues = []

    # Check for st.set_page_config in pages
    for page_file in page_files:
        with open(page_file, 'r') as f:
            if 'st.set_page_config' in f.read():
                issues.append(f"❌ {page_file.name} contains st.set_page_config()")

    # Check for old views directory
    if os.path.exists("views"):
        issues.append("❌ Old 'views/' directory still exists")

    # Check for .pages.toml
    if os.path.exists(".pages.toml"):
        issues.append("❌ .pages.toml file still exists")

    if issues:
        print()
        for issue in issues:
            print(f"   {issue}")
        print()
        print("⚠️  FIX THESE ISSUES BEFORE RUNNING!")
    else:
        print("   ✅ No issues found!")
        print()
        print("🚀 Ready to run: streamlit run streamlit_app.py")

    print()

if __name__ == "__main__":
    os.chdir("/home/user/MediAI/apps")
    check_pages()
