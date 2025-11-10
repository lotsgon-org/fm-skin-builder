#!/usr/bin/env bash
# Local build script for FM Skin Builder
# Builds the complete application bundle for the current platform

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[build]${NC} $1"
}

log_error() {
    echo -e "${RED}[build]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[build]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${BLUE}=== $1 ===${NC}"
    echo ""
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

log_section "FM Skin Builder - Local Build"

# Check prerequisites
log_info "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

if ! command -v cargo &> /dev/null; then
    log_error "Rust is not installed. Please install Rust from https://rustup.rs/"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

log_info "All prerequisites found!"

# Step 1: Setup Python environment
log_section "Step 1: Setting up Python environment"

if [ ! -d ".venv" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv .venv
fi

log_info "Python environment ready!"

# Step 2: Build Python backend
log_section "Step 2: Building Python backend"

./scripts/build_backend.sh

# Step 3: Install frontend dependencies
log_section "Step 3: Installing frontend dependencies"

cd frontend
if [ ! -d "node_modules" ]; then
    log_info "Installing frontend dependencies..."
    npm install
else
    log_info "Frontend dependencies already installed"
fi

# Step 4: Build Tauri app
log_section "Step 4: Building Tauri application"

log_info "Building application bundle..."
npm run tauri build

# Step 5: Show results
log_section "Build Complete!"

cd "$ROOT_DIR"

# Determine output location based on platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OUTPUT_DIR="frontend/src-tauri/target/release/bundle"
    log_info "Build artifacts:"
    [ -d "$OUTPUT_DIR/appimage" ] && ls -lh "$OUTPUT_DIR/appimage"/*.AppImage 2>/dev/null || true
    [ -d "$OUTPUT_DIR/deb" ] && ls -lh "$OUTPUT_DIR/deb"/*.deb 2>/dev/null || true
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OUTPUT_DIR="frontend/src-tauri/target/release/bundle"
    log_info "Build artifacts:"
    [ -d "$OUTPUT_DIR/dmg" ] && ls -lh "$OUTPUT_DIR/dmg"/*.dmg 2>/dev/null || true
    [ -d "$OUTPUT_DIR/macos" ] && ls -lh "$OUTPUT_DIR/macos"/*.app 2>/dev/null || true
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    OUTPUT_DIR="frontend/src-tauri/target/release/bundle"
    log_info "Build artifacts:"
    [ -d "$OUTPUT_DIR/nsis" ] && ls -lh "$OUTPUT_DIR/nsis"/*.exe 2>/dev/null || true
    [ -d "$OUTPUT_DIR/msi" ] && ls -lh "$OUTPUT_DIR/msi"/*.msi 2>/dev/null || true
fi

echo ""
log_info "Your application is ready to distribute!"
log_info "Find your build artifacts in: $OUTPUT_DIR"
echo ""

# Show next steps
log_warn "Next steps:"
echo "  1. Test the application before distributing"
echo "  2. For production builds, consider code signing"
echo "  3. Run ./scripts/generate_tauri_keys.sh to set up signing keys for updates"
echo ""
