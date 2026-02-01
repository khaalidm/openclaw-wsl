#!/bin/bash

# OpenClaw Agent Startup Script for WSL
# This script brings up the entire agent with one command

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       OpenClaw Agent Startup           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Ollama is running
check_ollama() {
    curl -s http://localhost:11434/api/version >/dev/null 2>&1
}

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}Error: Python3 is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

if ! command_exists ollama; then
    echo -e "${RED}Error: Ollama is not installed${NC}"
    echo "Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites found${NC}"

# Step 2: Setup environment
echo -e "${YELLOW}[2/6] Setting up environment...${NC}"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env from .env.example - Please configure your API keys${NC}"
    fi
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo -e "${GREEN}✓ Environment configured${NC}"

# Step 3: Create virtual environment and install Python dependencies
echo -e "${YELLOW}[3/6] Setting up Python environment...${NC}"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Step 4: Install Node.js dependencies
echo -e "${YELLOW}[4/6] Installing Node.js dependencies...${NC}"

if [ ! -d "node_modules" ]; then
    npm install --silent
fi

echo -e "${GREEN}✓ Node.js dependencies installed${NC}"

# Step 5: Start Ollama if not running
echo -e "${YELLOW}[5/6] Checking Ollama service...${NC}"

if ! check_ollama; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 3
fi

# Ensure the model is pulled
if ! ollama list | grep -q "llama3.2"; then
    echo "Pulling llama3.2 model (this may take a while)..."
    ollama pull llama3.2
fi

echo -e "${GREEN}✓ Ollama is running with llama3.2${NC}"

# Step 6: Start the agent
echo -e "${YELLOW}[6/6] Starting OpenClaw Agent...${NC}"
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     OpenClaw Agent is starting...      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "Models: ${BLUE}Ollama (llama3.2)${NC} + ${BLUE}Gemini${NC}"
echo -e "Channel: ${BLUE}WhatsApp${NC}"
echo ""

# Start the main agent
python3 src/main.py
