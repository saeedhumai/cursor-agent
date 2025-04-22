#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Cursor Agent Development Installation ===${NC}"

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: Not running in a virtual environment. It's recommended to use one.${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting installation."
        exit 1
    fi
fi

echo -e "${GREEN}Cleaning up previous builds...${NC}"
rm -rf build/ dist/ *.egg-info/ cursor_agent.egg-info/ cursor_agent_tools.egg-info/

echo -e "${GREEN}Installing package in development mode...${NC}"
pip install -e . # -e is for editable mode

echo -e "${GREEN}Verifying installation...${NC}"

# Check if agent package is installed
echo -en "Checking agent package... "
if python -c 'import agent; print(agent.__file__)' > /dev/null 2>&1; then
    AGENT_PATH=$(python -c 'import agent; print(agent.__file__)')
    echo -e "${GREEN}OK${NC} at $AGENT_PATH"
else
    echo -e "${RED}FAILED${NC}"
    echo "The agent package could not be imported."
fi

# Check if cursor_agent package is installed
echo -en "Checking cursor_agent package... "
if python -c 'import cursor_agent; print(cursor_agent.__file__)' > /dev/null 2>&1; then
    CURSOR_AGENT_PATH=$(python -c 'import cursor_agent; print(cursor_agent.__file__)')
    echo -e "${GREEN}OK${NC} at $CURSOR_AGENT_PATH"
else
    echo -e "${RED}FAILED${NC}"
    echo "The cursor_agent package could not be imported."
fi

# Check if cursor_agent_tools package is installed
echo -en "Checking cursor_agent_tools package... "
if python -c 'import cursor_agent_tools; print(cursor_agent_tools.__file__)' > /dev/null 2>&1; then
    TOOLS_PATH=$(python -c 'import cursor_agent_tools; print(cursor_agent_tools.__file__)')
    echo -e "${GREEN}OK${NC} at $TOOLS_PATH"
else
    echo -e "${RED}FAILED${NC}"
    echo "The cursor_agent_tools package could not be imported."
fi

# Verify import functionality
echo -en "Verifying import structure... "
if python -c 'from cursor_agent import ClaudeAgent, OpenAIAgent, create_agent; from cursor_agent_tools import ClaudeAgent, OpenAIAgent, create_agent; from agent import ClaudeAgent, OpenAIAgent, create_agent' > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "The import structure could not be verified."
fi

# Make the script executable
chmod +x dev_install.sh

echo -e "${GREEN}Installation process completed.${NC}" 