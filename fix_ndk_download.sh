#!/bin/bash
# Fix NDK Download Issues
# The environment blocks dl.google.com, so we need alternative solutions

set -e

NDK_VERSION="r28c"
NDK_DIR="/root/.buildozer/android/platform/android-ndk-${NDK_VERSION}"
NDK_ZIP="/root/.buildozer/android/platform/android-ndk-${NDK_VERSION}-linux.zip"

echo "=== Android NDK Download Fix ==="
echo "NDK Version: ${NDK_VERSION}"
echo "Target Directory: ${NDK_DIR}"
echo ""

# Remove corrupted files
echo "Cleaning up corrupted NDK files..."
rm -rf "${NDK_DIR}" 2>/dev/null || true
rm -f "${NDK_ZIP}" 2>/dev/null || true

# Try alternative download sources
echo "Attempting to download NDK from alternative sources..."

# Method 1: Try direct download with retry
echo "Method 1: Attempting direct download (may fail due to network restrictions)..."
if wget --tries=3 --timeout=30 "https://dl.google.com/android/repository/android-ndk-${NDK_VERSION}-linux.zip" -O "${NDK_ZIP}" 2>&1 | tee /tmp/ndk_download.log; then
    echo "✓ Download successful!"
else
    echo "✗ Direct download failed (expected due to 403 Forbidden)"
    rm -f "${NDK_ZIP}" 2>/dev/null || true
fi

# Method 2: Check if we got a valid zip
if [ -f "${NDK_ZIP}" ] && [ -s "${NDK_ZIP}" ]; then
    echo "Verifying downloaded file..."
    if file "${NDK_ZIP}" | grep -q "Zip archive"; then
        echo "✓ Valid ZIP file detected"
        echo "Extracting NDK..."
        cd "$(dirname "${NDK_ZIP}")"
        unzip -q "${NDK_ZIP}"

        # Verify extraction
        if [ -d "${NDK_DIR}/toolchains/llvm/prebuilt/linux-x86_64/bin" ]; then
            echo "✓ NDK extracted successfully!"
            ls -lh "${NDK_DIR}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang" || echo "Warning: clang not found"
            exit 0
        else
            echo "✗ NDK extraction incomplete"
        fi
    else
        echo "✗ Downloaded file is not a valid ZIP"
        rm -f "${NDK_ZIP}"
    fi
fi

# Method 3: Documentation for manual intervention
echo ""
echo "=== MANUAL INTERVENTION REQUIRED ==="
echo ""
echo "The Android NDK cannot be downloaded automatically due to network restrictions."
echo "This environment blocks access to: dl.google.com"
echo ""
echo "SOLUTION 1: Use GitHub Actions for building (RECOMMENDED)"
echo "  - GitHub Actions has unrestricted internet access"
echo "  - See .github/workflows/ for CI/CD setup"
echo ""
echo "SOLUTION 2: Download NDK from an unrestricted machine"
echo "  1. On a machine with internet access, download:"
echo "     https://dl.google.com/android/repository/android-ndk-${NDK_VERSION}-linux.zip"
echo "  2. Upload to this server"
echo "  3. Place at: ${NDK_ZIP}"
echo "  4. Run: unzip -q \"${NDK_ZIP}\" -d \"$(dirname "${NDK_DIR}")\""
echo ""
echo "SOLUTION 3: Request network whitelist from system administrator"
echo "  Domains to whitelist:"
echo "    - dl.google.com"
echo "    - github.com/libsdl-org (if not already done)"
echo ""
echo "Expected NDK size: ~1.2GB (zip), ~3.5GB (extracted)"
echo "Current status: NDK not available"
echo ""

exit 1
