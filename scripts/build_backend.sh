#!/usr/bin/env bash
set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[build-backend]${NC} $1"
}

log_error() {
    echo -e "${RED}[build-backend]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[build-backend]${NC} $1"
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$ROOT_DIR/frontend/src-tauri/resources/backend"
ENTRY_POINT="$ROOT_DIR/fm_skin_builder/__main__.py"
BINARY_NAME="fm_skin_builder"

# Determine platform-specific binary extension
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    BINARY_NAME="${BINARY_NAME}.exe"
    VENV_PY="$ROOT_DIR/.venv/Scripts/python.exe"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    VENV_PY="$ROOT_DIR/.venv/bin/python3"
else
    VENV_PY="$ROOT_DIR/.venv/bin/python3"
fi

log_info "Building backend for $(uname -s)..."
log_info "Binary name: $BINARY_NAME"

# Check for Python
if [[ ! -x "$VENV_PY" ]]; then
    log_error "Virtual environment missing at: $VENV_PY"
    log_error "Run scripts/setup_python_env.sh first."
    exit 1
fi

# Verify Python version
PY_VERSION=$("$VENV_PY" --version 2>&1 | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
log_info "Using Python $PY_VERSION"

pushd "$ROOT_DIR" >/dev/null

# Install dependencies
log_info "Installing dependencies..."
"$VENV_PY" -m pip install --upgrade pip -q
"$VENV_PY" -m pip install -r requirements.txt pyinstaller -q

# Clean previous builds
log_info "Cleaning previous builds..."
rm -rf build dist "$BINARY_NAME.spec" "fm_skin_builder.spec"

# Build with PyInstaller
log_info "Building standalone executable with PyInstaller..."
"$VENV_PY" -m PyInstaller \
    --onefile \
    --name "fm_skin_builder" \
    --hidden-import=PIL._tkinter_finder \
    --collect-all UnityPy \
    --collect-all cairosvg \
    --collect-all svg.path \
    --additional-hooks-dir="$ROOT_DIR/hooks" \
    --runtime-hook="$ROOT_DIR/hooks/rthook_cairocffi.py" \
    "$ENTRY_POINT"

# Verify build
if [[ ! -f "dist/fm_skin_builder" && ! -f "dist/fm_skin_builder.exe" ]]; then
    log_error "Build failed: Binary not found in dist/"
    exit 1
fi

# Prepare output directory
mkdir -p "$DIST_DIR"

# Copy binary
log_info "Copying binary to resources..."
if [[ -f "dist/fm_skin_builder.exe" ]]; then
    cp "dist/fm_skin_builder.exe" "$DIST_DIR/"
    FINAL_BINARY="$DIST_DIR/fm_skin_builder.exe"
else
    cp "dist/fm_skin_builder" "$DIST_DIR/"
    FINAL_BINARY="$DIST_DIR/fm_skin_builder"
    chmod +x "$FINAL_BINARY"
fi

# Verify final binary
if [[ ! -f "$FINAL_BINARY" ]]; then
    log_error "Failed to copy binary to $FINAL_BINARY"
    exit 1
fi

popd >/dev/null

# Get binary size
BINARY_SIZE=$(du -h "$FINAL_BINARY" | cut -f1)
log_info "Backend binary built successfully!"
log_info "Location: $FINAL_BINARY"
log_info "Size: $BINARY_SIZE"

# Test the binary
log_info "Testing binary..."
if "$FINAL_BINARY" --help > /dev/null 2>&1; then
    log_info "Binary test passed!"
else
    log_warn "Binary test failed, but this might be expected in some environments"
fi
