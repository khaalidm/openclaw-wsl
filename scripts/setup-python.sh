#!/bin/bash

# OpenClaw Python Environment Setup Script
# Sets up Python virtual environment and installs dependencies

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON_MIN_VERSION="3.10"

cd "$PROJECT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   OpenClaw Python Environment Setup        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}[1/4] Checking Python version...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed${NC}"
    echo "Install Python 3.10+ before running this script"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}Error: Python $PYTHON_MIN_VERSION+ is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

# Create virtual environment
echo -e "${YELLOW}[2/4] Creating virtual environment...${NC}"

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
    read -p "Recreate it? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
        echo -e "${GREEN}✓ Virtual environment recreated${NC}"
    else
        echo -e "${GREEN}✓ Using existing virtual environment${NC}"
    fi
else
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓ Virtual environment created at $VENV_DIR${NC}"
fi

# Activate and upgrade pip
echo -e "${YELLOW}[3/4] Upgrading pip...${NC}"

source "$VENV_DIR/bin/activate"
pip install --upgrade pip --quiet

echo -e "${GREEN}✓ pip upgraded to $(pip --version | cut -d' ' -f2)${NC}"

# Install dependencies
echo -e "${YELLOW}[4/4] Installing dependencies...${NC}"

if [ -f "$PROJECT_DIR/pyproject.toml" ]; then
    pip install -e ".[dev]" --quiet
    echo -e "${GREEN}✓ Installed from pyproject.toml (with dev dependencies)${NC}"
elif [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓ Installed from requirements.txt${NC}"
else
    echo -e "${RED}Error: No pyproject.toml or requirements.txt found${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Python Environment Ready!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo "To activate the virtual environment:"
echo -e "  ${BLUE}source venv/bin/activate${NC}"
echo ""
echo "To run the agent:"
echo -e "  ${BLUE}python src/main.py${NC}"
echo ""
echo "Or use the start script:"
echo -e "  ${BLUE}./start.sh${NC}"
echo ""
