#!/bin/bash
# Script to restart Streamlit on port 8501

echo "Stopping old process on port 8501..."
sudo kill -9 $(lsof -ti:8501) 2>/dev/null

echo "Waiting 2 seconds..."
sleep 2

echo "Starting Streamlit on port 8501..."
cd /home/neeyuhuynh/Desktop/MediAI/apps
streamlit run streamlit_app.py --server.port 8501

echo "Done! App is now running on http://localhost:8501"
