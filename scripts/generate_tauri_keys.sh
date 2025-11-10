#!/usr/bin/env bash
# Generate Tauri signing keys for secure updates
# These keys are used to sign updates and verify them on the client side
# This is essential when you move to R2-based auto-updates in the future

set -euo pipefail

echo "Generating Tauri signing keys..."
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "Error: Must be run from the project root directory"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "Error: npm is required but not found"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Generate the keys using Tauri CLI
npm run tauri -- signer generate

echo ""
echo "=== Keys Generated Successfully ==="
echo ""
echo "IMPORTANT: Your signing keys have been generated."
echo ""
echo "The PUBLIC key has been saved to your Tauri config."
echo "The PRIVATE key and password are displayed above."
echo ""
echo "For GitHub Actions, add these secrets:"
echo "  TAURI_SIGNING_PRIVATE_KEY: (the private key string)"
echo "  TAURI_SIGNING_PRIVATE_KEY_PASSWORD: (the password)"
echo ""
echo "Keep your private key and password SECURE and NEVER commit them to git!"
echo ""
echo "These keys will be used for:"
echo "  - Signing application bundles"
echo "  - Verifying updates when you implement auto-updates"
echo "  - Ensuring users only install authentic versions of your app"
echo ""
