#!/bin/bash
# ===================================================================
# MediAI Advanced Chatbot - Dependency Installation Script
# ===================================================================

set -e  # Exit on error

echo "🚀 Installing MediAI Advanced Chatbot Dependencies..."
echo "================================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python version: $python_version${NC}"

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
python3 -m pip install --upgrade pip
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install main chatbot dependencies
echo -e "\n${YELLOW}Installing chatbot dependencies...${NC}"
pip install -r requirements.chatbot.txt
echo -e "${GREEN}✓ Chatbot dependencies installed${NC}"

# Download spaCy model
echo -e "\n${YELLOW}Downloading spaCy English model...${NC}"
python3 -m spacy download en_core_web_sm
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ spaCy model downloaded${NC}"
else
    echo -e "${RED}✗ Failed to download spaCy model${NC}"
    echo -e "${YELLOW}  You can download it later with: python -m spacy download en_core_web_sm${NC}"
fi

# Verify installations
echo -e "\n${YELLOW}Verifying installations...${NC}"

# Check Groq
python3 -c "import groq; print('✓ groq')" 2>/dev/null || echo -e "${RED}✗ groq${NC}"

# Check LangGraph
python3 -c "import langgraph; print('✓ langgraph')" 2>/dev/null || echo -e "${RED}✗ langgraph${NC}"

# Check Qdrant
python3 -c "import qdrant_client; print('✓ qdrant-client')" 2>/dev/null || echo -e "${RED}✗ qdrant-client${NC}"

# Check spaCy
python3 -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✓ spacy + en_core_web_sm')" 2>/dev/null || echo -e "${RED}✗ spacy${NC}"

# Check transformers
python3 -c "import transformers; print('✓ transformers')" 2>/dev/null || echo -e "${RED}✗ transformers${NC}"

# Check PyMuPDF
python3 -c "import fitz; print('✓ PyMuPDF (fitz)')" 2>/dev/null || echo -e "${RED}✗ PyMuPDF${NC}"

echo -e "\n${GREEN}================================================================${NC}"
echo -e "${GREEN}✅ Installation complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Fill in API keys in .env file"
echo -e "2. Run: ${GREEN}python scripts/init_chatbot_database.py${NC}"
echo -e "3. Run: ${GREEN}python scripts/init_qdrant_store.py${NC}"
echo -e "4. Run: ${GREEN}python scripts/test_chatbot_integration.py${NC}"
echo -e "\n${YELLOW}See SETUP_CHATBOT.md for detailed instructions.${NC}"
