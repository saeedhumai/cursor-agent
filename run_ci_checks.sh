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

# Define Python versions to test
PYTHON_VERSIONS=("3.10.4")

# Configuration options
CONTINUE_ON_MISSING=true  # Continue if a Python version is missing
STRICT_MODE=${STRICT_MODE:-false}  # Can be overridden with STRICT_MODE=true ./run_ci_checks.sh

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
echo -e "${BOLD}Testing across Python versions: ${PYTHON_VERSIONS[*]}${NC}"

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    print_error "pyenv is not installed. Please install pyenv first."
    echo -e "${YELLOW}Visit https://github.com/pyenv/pyenv for installation instructions.${NC}"
    exit 1
fi

# Initialize pyenv
print_header "Initializing pyenv"
eval "$(pyenv init -)"
eval "$(pyenv init --path 2>/dev/null || echo 'No --path support')"

# Get available Python versions
AVAILABLE_VERSIONS=$(pyenv versions --bare | grep -E "^($(IFS="|"; echo "${PYTHON_VERSIONS[*]}"))")

if [ -z "$AVAILABLE_VERSIONS" ]; then
    print_error "None of the required Python versions (${PYTHON_VERSIONS[*]}) are installed."
    echo -e "${YELLOW}Please install at least one of these versions using pyenv:${NC}"
    for version in "${PYTHON_VERSIONS[@]}"; do
        echo -e "  ${CYAN}pyenv install $version${NC}"
    done
    exit 1
fi

# Function to run checks for a specific Python version
run_checks_for_version() {
    local version=$1
    print_header "Running checks with Python $version"
    
    # Switch to the requested Python version
    echo -e "${CYAN}Switching to Python $version...${NC}"
    if ! pyenv shell $version 2>/dev/null; then
        print_error "Failed to switch to Python $version (not installed)"
        echo -e "${YELLOW}To install this version, run: pyenv install $version${NC}"
        return 1
    fi
    
    # Display current Python version
    python --version
    
    # Step 1: Install dependencies
    print_header "STEP: Installing Dependencies"

    echo -e "${CYAN}Running: python -m pip install --upgrade pip${NC}"
    python -m pip install --upgrade pip
    if [ $? -ne 0 ]; then
        print_error "Failed to upgrade pip"
        return 1
    fi

    echo -e "${CYAN}Running: pip install -e \".[dev]\"${NC}"
    pip install -e ".[dev]"
    if [ $? -ne 0 ]; then
        print_error "Failed to install package dependencies"
        return 1
    fi

    echo -e "${CYAN}Running: pip install pytest pytest-cov flake8 mypy types-requests beautifulsoup4 types-beautifulsoup4${NC}"
    pip install pytest pytest-cov flake8 mypy types-requests beautifulsoup4 types-beautifulsoup4
    if [ $? -ne 0 ]; then
        print_error "Failed to install test dependencies"
        return 1
    fi

    print_success "Dependencies installed successfully"

    # Step 2: Run linting checks
    print_header "STEP: Running Linting Checks"

    echo -e "${CYAN}Running: flake8 cursor_agent_tools tests --config=.flake8${NC}"
    flake8 cursor_agent_tools tests --config=.flake8
    flake8_status=$?

    echo -e "${CYAN}Running: mypy cursor_agent_tools tests --config-file=.mypy.ini${NC}"
    mypy cursor_agent_tools tests --config-file=.mypy.ini
    mypy_status=$?

    if [ $flake8_status -ne 0 ] || [ $mypy_status -ne 0 ]; then
        print_error "Linting checks failed"
        return 1
    fi

    print_success "Linting checks passed"

    # Step 3: Run tests with coverage
    print_header "STEP: Running Tests with Coverage"

    # Create test directories first
    echo -e "${CYAN}Creating test directories...${NC}"
    python -m tests.create_test_dirs

    # Run tests with coverage
    echo -e "${CYAN}Running: python -m pytest tests/ -v --ignore=tests/requires_api/ -k \"not test_openai_with_proxy and not test_chat_with_user_info and not test_file_tools and not test_image\" --cov=cursor_agent_tools --cov-report=term-missing${NC}"
    python -m pytest tests/ -v --ignore=tests/requires_api/ -k "not test_openai_with_proxy and not test_chat_with_user_info and not test_file_tools and not test_image" --cov=cursor_agent_tools --cov-report=term-missing
    test_status=$?

    if [ $test_status -eq 0 ]; then
        print_success "Tests passed successfully"
        return 0
    else
        print_error "Tests failed"
        return 1
    fi
}

# Track overall success
SUCCESS=true
CHECKED_VERSIONS=0

# Run checks for each Python version
for version in "${PYTHON_VERSIONS[@]}"; do
    # Check if this Python version is available
    if echo "$AVAILABLE_VERSIONS" | grep -q "^$version"; then
        if run_checks_for_version $version; then
            print_success "Checks passed for Python $version"
            CHECKED_VERSIONS=$((CHECKED_VERSIONS + 1))
        else
            print_error "Checks failed for Python $version"
            SUCCESS=false
            if [ "$STRICT_MODE" = true ]; then
                print_error "Exiting due to failed checks (STRICT_MODE is enabled)"
                exit 1
            fi
        fi
    else
        echo -e "\n${YELLOW}⚠️ Python $version is not installed via pyenv.${NC}"
        echo -e "${YELLOW}To install: pyenv install $version${NC}"
        
        if [ "$CONTINUE_ON_MISSING" != true ] || [ "$STRICT_MODE" = true ]; then
            print_error "Cannot continue without Python $version (CONTINUE_ON_MISSING=$CONTINUE_ON_MISSING, STRICT_MODE=$STRICT_MODE)"
            exit 1
        fi
    fi
done

print_header "SUMMARY"
if [ "$SUCCESS" = true ] && [ $CHECKED_VERSIONS -gt 0 ]; then
    echo -e "${BOLD}${GREEN}ALL CI/CD CHECKS PASSED! ✅${NC}"
    echo -e "${GREEN}Successfully checked $CHECKED_VERSIONS Python version(s)${NC}"
    echo -e "${GREEN}Your code is ready to be pushed.${NC}"
    exit 0
else
    if [ $CHECKED_VERSIONS -eq 0 ]; then
        print_error "No Python versions were checked!"
    else
        print_error "Checks failed on one or more Python versions."
    fi
    exit 1
fi 