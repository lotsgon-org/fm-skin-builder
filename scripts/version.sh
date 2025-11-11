#!/bin/bash
# Helper script to show version information
#
# Usage:
#   ./scripts/version.sh           # Show current and next versions
#   ./scripts/version.sh --next    # Show only next version
#   ./scripts/version.sh --beta    # Show next beta version

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_full_info() {
    echo -e "${BLUE}Version Information${NC}"
    echo "==================="
    echo ""

    # Current version
    CURRENT=$(python3 scripts/get_next_version.py --current 2>/dev/null || echo "0.1.0")
    echo -e "${GREEN}Current version:${NC} v$CURRENT"

    # Latest tag
    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")
    echo -e "${GREEN}Latest tag:${NC} $LATEST_TAG"
    echo ""

    # Commits since last tag
    if [ "$LATEST_TAG" != "none" ]; then
        COMMIT_COUNT=$(git rev-list $LATEST_TAG..HEAD --count)
        echo -e "${BLUE}Commits since last tag:${NC} $COMMIT_COUNT"

        if [ $COMMIT_COUNT -gt 0 ]; then
            echo ""
            echo "Recent commits:"
            git log $LATEST_TAG..HEAD --pretty=format:"  %C(yellow)%h%Creset %s" --no-merges | head -5
            echo ""
        fi
    else
        COMMIT_COUNT=$(git rev-list HEAD --count)
        echo -e "${BLUE}Total commits:${NC} $COMMIT_COUNT"
        echo ""
        echo "Recent commits:"
        git log --pretty=format:"  %C(yellow)%h%Creset %s" --no-merges | head -5
        echo ""
    fi

    echo ""
    echo -e "${BLUE}Next versions:${NC}"

    # Next release version
    NEXT=$(python3 scripts/get_next_version.py)
    echo -e "${GREEN}  Next release:${NC} v$NEXT"

    # Next beta version
    NEXT_BETA=$(python3 scripts/get_next_version.py --beta)
    echo -e "${GREEN}  Next beta:${NC} $NEXT_BETA"

    echo ""
    echo -e "${YELLOW}Tip:${NC} Use conventional commits to control version bumps:"
    echo "  feat: ...        → minor bump (0.1.0 → 0.2.0)"
    echo "  fix: ...         → patch bump (0.1.0 → 0.1.1)"
    echo "  feat!: ...       → minor bump for 0.x (0.1.0 → 0.2.0)"
    echo "  BREAKING CHANGE  → minor bump for 0.x (0.1.0 → 0.2.0)"
}

# Parse arguments
if [ "$1" = "--next" ]; then
    python3 scripts/get_next_version.py
elif [ "$1" = "--beta" ]; then
    python3 scripts/get_next_version.py --beta
elif [ "$1" = "--current" ]; then
    python3 scripts/get_next_version.py --current
else
    show_full_info
fi
