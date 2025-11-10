#!/usr/bin/env bash
# Check if all prerequisites for building are installed

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1: $(command -v $1)"
        if [ -n "${2:-}" ]; then
            VERSION=$($1 $2 2>&1 | head -1)
            echo -e "  Version: $VERSION"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} $1: not found"
        return 1
    fi
}

echo "Checking build prerequisites..."
echo "==============================="
echo ""

ERRORS=0

echo "Core Tools:"
check_command "node" "--version" || ((ERRORS++))
check_command "npm" "--version" || ((ERRORS++))
check_command "cargo" "--version" || ((ERRORS++))
check_command "rustc" "--version" || ((ERRORS++))
check_command "python3" "--version" || ((ERRORS++))

echo ""
echo "Optional Tools:"
check_command "git" "--version" || echo -e "${YELLOW}⚠${NC} git: not found (optional)"

echo ""
echo "Python Environment:"
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists at .venv/"
    if [ -f ".venv/bin/python3" ] || [ -f ".venv/Scripts/python.exe" ]; then
        echo -e "${GREEN}✓${NC} Python interpreter found in venv"
    else
        echo -e "${RED}✗${NC} Python interpreter not found in venv"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⚠${NC} Virtual environment not found (will be created on first build)"
fi

echo ""
echo "Frontend Dependencies:"
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Frontend node_modules exists"
else
    echo -e "${YELLOW}⚠${NC} Frontend dependencies not installed (run 'cd frontend && npm install')"
fi

echo ""
echo "Platform-Specific:"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux detected - checking for required system libraries..."
    check_command "pkg-config" "--version" || echo -e "${YELLOW}⚠${NC} pkg-config not found"

    if pkg-config --exists gtk+-3.0 2>/dev/null; then
        echo -e "${GREEN}✓${NC} GTK+3 development libraries found"
    else
        echo -e "${RED}✗${NC} GTK+3 development libraries not found"
        echo "  Install with: sudo apt-get install libwebkit2gtk-4.1-dev"
        ((ERRORS++))
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS detected"
    if xcode-select -p &> /dev/null; then
        echo -e "${GREEN}✓${NC} Xcode Command Line Tools installed"
    else
        echo -e "${RED}✗${NC} Xcode Command Line Tools not found"
        echo "  Install with: xcode-select --install"
        ((ERRORS++))
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    echo "Windows detected"
    echo -e "${GREEN}✓${NC} Windows environment"
fi

echo ""
echo "==============================="

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All critical prerequisites are installed!${NC}"
    echo ""
    echo "You're ready to build. Run:"
    echo "  ./scripts/build_local.sh"
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS critical issue(s)${NC}"
    echo ""
    echo "Please install missing prerequisites and try again."
    echo "See docs/BUILD.md for detailed installation instructions."
    exit 1
fi
