#!/bin/bash
# Local CI/CD Pipeline Check Script
# Run this script before pushing code to catch issues

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to print headers
print_header() {
    echo -e "\n${BOLD}====================================================================${NC}"
    echo -e "${BOLD} $1 ${NC}"
    echo -e "${BOLD}====================================================================${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error messages and exit if needed
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to handle errors
handle_error() {
    print_error "$1"
    echo -e "\n${BOLD}${RED}CI/CD CHECKS FAILED! ❌${NC}"
    echo -e "${RED}Fix the issues above before pushing your code.${NC}"
    exit 1
}

# Print title
echo -e "${BOLD}RUNNING LOCAL CI/CD PIPELINE CHECKS${NC}"

# Step 1: Install dependencies
print_header "STEP: Installing Dependencies"

echo -e "${CYAN}Running: python -m pip install --upgrade pip${NC}"
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    handle_error "Failed to upgrade pip"
fi

echo -e "${CYAN}Running: pip install -e \".[dev]\"${NC}"
pip install -e ".[dev]"
if [ $? -ne 0 ]; then
    handle_error "Failed to install package dependencies"
fi

echo -e "${CYAN}Running: pip install pytest pytest-cov flake8 mypy types-requests${NC}"
pip install pytest pytest-cov flake8 mypy types-requests
if [ $? -ne 0 ]; then
    handle_error "Failed to install test dependencies"
fi

print_success "Dependencies installed successfully"

# Step 2: Run linting checks
print_header "STEP: Running Linting Checks"

echo -e "${CYAN}Running: flake8 agent tests --config=.flake8${NC}"
flake8 agent tests --config=.flake8
flake8_status=$?

echo -e "${CYAN}Running: mypy agent tests --config-file=.mypy.ini${NC}"
mypy agent tests --config-file=.mypy.ini
mypy_status=$?

if [ $flake8_status -ne 0 ] || [ $mypy_status -ne 0 ]; then
    handle_error "Linting checks failed"
fi

print_success "Linting checks passed"

# Step 3: Run tests with coverage
print_header "STEP: Running Tests with Coverage"

# Create test directories first
echo -e "${CYAN}Creating test directories...${NC}"
python -m tests.create_test_dirs

# Run tests with coverage
echo -e "${CYAN}Running: python -m pytest tests/ -v --ignore=tests/requires_api/ -k \"not test_openai_with_proxy\" --cov=agent --cov-report=term-missing${NC}"
python -m pytest tests/ -v --ignore=tests/requires_api/ -k "not test_openai_with_proxy" --cov=agent --cov-report=term-missing
test_status=$?

if [ $test_status -eq 0 ]; then
    print_success "Tests passed successfully"
else
    handle_error "Tests failed"
fi

# Final success message
echo -e "\n${BOLD}${GREEN}ALL CI/CD CHECKS PASSED! ✅${NC}"
echo -e "${GREEN}Your code is ready to be pushed.${NC}"

exit 0 