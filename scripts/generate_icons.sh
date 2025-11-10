#!/usr/bin/env bash
# Generate all required icon formats from the source icon
# Uses Tauri's built-in icon generation

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Generating application icons..."
echo "================================"
echo ""

cd "$ROOT_DIR/frontend"

# Check if source icon exists
SOURCE_ICON="../frontend/src-tauri/icons/icon.png"
if [ ! -f "$SOURCE_ICON" ]; then
    echo "Error: Source icon not found at $SOURCE_ICON"
    echo "Please provide a 1024x1024 PNG icon at this location"
    exit 1
fi

echo "Source icon: $SOURCE_ICON"
echo "Output directory: src-tauri/icons/"
echo ""

# Generate icons using Tauri CLI
npm run tauri icon "$SOURCE_ICON"

echo ""
echo "✓ Icons generated successfully!"
echo ""
echo "Generated files:"
ls -lh src-tauri/icons/

echo ""
echo "Icons are now ready for bundling."
