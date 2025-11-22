import streamlit as st

st.set_page_config(page_title="Test Clean App", layout="wide")

st.title("🧪 Test Clean - No Multi-Page")
st.write("If you see ONLY this page and NO sidebar navigation, the fix works!")
st.write("Current files in apps/:")

import os
files = os.listdir('.')
for f in sorted(files):
    st.write(f"- {f}")
