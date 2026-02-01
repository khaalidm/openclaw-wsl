#!/bin/bash

# OpenClaw Windows WSL Installation Script
# Run this script in WSL to set up the complete environment

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   OpenClaw WSL Installation Script         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Update system
echo -e "${YELLOW}[1/5] Updating system packages...${NC}"
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# Install Node.js (if not present)
echo -e "${YELLOW}[2/5] Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi
echo -e "${GREEN}✓ Node.js $(node --version)${NC}"

# Install Python (if not present)
echo -e "${YELLOW}[3/5] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    sudo apt-get install -y python3 python3-pip python3-venv
fi
echo -e "${GREEN}✓ Python $(python3 --version)${NC}"

# Install Ollama
echo -e "${YELLOW}[4/5] Checking Ollama...${NC}"
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi
echo -e "${GREEN}✓ Ollama installed${NC}"

# Install Chromium for WhatsApp Web
echo -e "${YELLOW}[5/5] Installing browser dependencies for WhatsApp...${NC}"
sudo apt-get install -y chromium-browser || sudo apt-get install -y chromium

# Make scripts executable
echo -e "${YELLOW}[6/6] Making scripts executable...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

chmod +x "$SCRIPT_DIR/install-wsl.sh"
chmod +x "$PROJECT_DIR/start.sh"
echo -e "${GREEN}✓ Scripts are now executable${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Installation Complete!                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and add your Gemini API key"
echo "  2. Run ./start.sh to start the agent"
echo ""
