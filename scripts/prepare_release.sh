#!/usr/bin/env bash
# Prepare a new release
# This script helps with versioning and tagging

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_usage() {
    echo "Usage: $0 <version>"
    echo ""
    echo "Examples:"
    echo "  $0 0.2.0    # Create version 0.2.0"
    echo "  $0 1.0.0    # Create version 1.0.0"
    echo ""
    echo "This script will:"
    echo "  1. Update version in package.json"
    echo "  2. Update version in tauri.conf.json"
    echo "  3. Update version in pyproject.toml"
    echo "  4. Create a git commit"
    echo "  5. Create a git tag"
    echo ""
    echo "After running this script, push the tag to trigger a release build:"
    echo "  git push origin v<version>"
    exit 1
}

if [ $# -ne 1 ]; then
    show_usage
fi

VERSION="$1"

# Validate version format (simple check)
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in format X.Y.Z (e.g., 1.2.3)"
    exit 1
fi

echo -e "${BLUE}Preparing release v${VERSION}${NC}"
echo ""

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update package.json
echo "Updating package.json..."
if [ -f "package.json" ]; then
    sed -i.bak "s/\"version\": \".*\"/\"version\": \"${VERSION}\"/" package.json
    rm package.json.bak
fi

# Update frontend package.json
echo "Updating frontend/package.json..."
if [ -f "frontend/package.json" ]; then
    sed -i.bak "s/\"version\": \".*\"/\"version\": \"${VERSION}\"/" frontend/package.json
    rm frontend/package.json.bak
fi

# Update tauri.conf.json
echo "Updating tauri.conf.json..."
if [ -f "frontend/src-tauri/tauri.conf.json" ]; then
    sed -i.bak "s/\"version\": \".*\"/\"version\": \"${VERSION}\"/" frontend/src-tauri/tauri.conf.json
    rm frontend/src-tauri/tauri.conf.json.bak
fi

# Update pyproject.toml
echo "Updating pyproject.toml..."
if [ -f "pyproject.toml" ]; then
    sed -i.bak "s/version = \".*\"/version = \"${VERSION}\"/" pyproject.toml
    rm pyproject.toml.bak
fi

# Update fm_skin_builder/version.py if it exists
echo "Updating version.py..."
if [ -f "fm_skin_builder/version.py" ]; then
    echo "__version__ = \"${VERSION}\"" > fm_skin_builder/version.py
fi

echo ""
echo -e "${GREEN}✓ Version files updated${NC}"
echo ""

# Show what changed
echo "Changed files:"
git diff --stat

echo ""
read -p "Create commit and tag? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted. You can commit manually."
    exit 0
fi

# Commit changes
git add package.json frontend/package.json frontend/src-tauri/tauri.conf.json pyproject.toml
[ -f "fm_skin_builder/version.py" ] && git add fm_skin_builder/version.py

git commit -m "chore: bump version to ${VERSION}"

# Create tag
git tag -a "v${VERSION}" -m "Release v${VERSION}"

echo ""
echo -e "${GREEN}✓ Release v${VERSION} prepared!${NC}"
echo ""
echo "Next steps:"
echo "  1. Push the changes: git push origin $(git branch --show-current)"
echo "  2. Push the tag:     git push origin v${VERSION}"
echo ""
echo "Pushing the tag will trigger the GitHub Actions build workflow."
echo "Artifacts will be available in the Actions tab after the build completes."
