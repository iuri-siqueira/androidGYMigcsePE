#!/bin/bash

# Build Failure Diagnostic Script for IGCSE GYM Android App
# Run this script after a build failure to get detailed diagnostics

set +e  # Don't exit on errors

echo "========================================="
echo "IGCSE GYM - Build Failure Diagnostics"
echo "========================================="
echo ""
echo "Timestamp: $(date)"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Checking Build Log Location${NC}"
echo "========================================="

BUILD_LOG=$(find .buildozer/android/platform/build-* -name "build.log" 2>/dev/null | head -n 1)

if [ -n "$BUILD_LOG" ]; then
    echo -e "${GREEN}✓${NC} Found build log: $BUILD_LOG"
    echo "  Size: $(du -h "$BUILD_LOG" | cut -f1)"
    echo "  Last modified: $(stat -c %y "$BUILD_LOG" 2>/dev/null | cut -d. -f1 || stat -f %Sm "$BUILD_LOG" 2>/dev/null)"
else
    echo -e "${RED}✗${NC} No build log found"
    echo "  This might indicate a very early failure"
fi

echo ""
echo -e "${BLUE}2. Last 50 Lines of Build Log${NC}"
echo "========================================="

if [ -n "$BUILD_LOG" ]; then
    tail -n 50 "$BUILD_LOG"
else
    echo "No build log available"
fi

echo ""
echo -e "${BLUE}3. Checking for Common Error Patterns${NC}"
echo "========================================="

if [ -n "$BUILD_LOG" ]; then
    echo "Searching for error patterns..."

    # NDK errors
    if grep -i "ndk" "$BUILD_LOG" | grep -i "error\|fail\|not found" > /dev/null; then
        echo -e "${RED}✗ NDK-related errors found:${NC}"
        grep -i "ndk" "$BUILD_LOG" | grep -i "error\|fail\|not found" | tail -n 5
        echo ""
    fi

    # SDK errors
    if grep -i "sdk" "$BUILD_LOG" | grep -i "error\|fail\|not found" > /dev/null; then
        echo -e "${RED}✗ SDK-related errors found:${NC}"
        grep -i "sdk" "$BUILD_LOG" | grep -i "error\|fail\|not found" | tail -n 5
        echo ""
    fi

    # Gradle errors
    if grep -i "gradle" "$BUILD_LOG" | grep -i "error\|fail" > /dev/null; then
        echo -e "${RED}✗ Gradle-related errors found:${NC}"
        grep -i "gradle" "$BUILD_LOG" | grep -i "error\|fail" | tail -n 5
        echo ""
    fi

    # Python errors
    if grep -i "python" "$BUILD_LOG" | grep -i "error\|fail\|exception" > /dev/null; then
        echo -e "${RED}✗ Python-related errors found:${NC}"
        grep -i "python" "$BUILD_LOG" | grep -i "error\|fail\|exception" | tail -n 5
        echo ""
    fi

    # Compilation errors
    if grep -i "compilation failed\|compiler error\|undefined reference" "$BUILD_LOG" > /dev/null; then
        echo -e "${RED}✗ Compilation errors found:${NC}"
        grep -i "compilation failed\|compiler error\|undefined reference" "$BUILD_LOG" | tail -n 5
        echo ""
    fi

    # Memory errors
    if grep -i "out of memory\|cannot allocate\|heap" "$BUILD_LOG" | grep -i "error" > /dev/null; then
        echo -e "${RED}✗ Memory-related errors found:${NC}"
        grep -i "out of memory\|cannot allocate\|heap" "$BUILD_LOG" | grep -i "error" | tail -n 5
        echo ""
    fi

    # Network errors
    if grep -i "download\|fetch\|connection" "$BUILD_LOG" | grep -i "error\|fail\|timeout" > /dev/null; then
        echo -e "${RED}✗ Network-related errors found:${NC}"
        grep -i "download\|fetch\|connection" "$BUILD_LOG" | grep -i "error\|fail\|timeout" | tail -n 5
        echo ""
    fi

    echo -e "${GREEN}✓${NC} Error pattern analysis complete"
else
    echo "No build log available for analysis"
fi

echo ""
echo -e "${BLUE}4. Build Directory Status${NC}"
echo "========================================="

echo "Buildozer directories:"
if [ -d .buildozer ]; then
    echo -e "${GREEN}✓${NC} .buildozer/ exists"
    echo "  Size: $(du -sh .buildozer 2>/dev/null | cut -f1 || echo 'unknown')"
else
    echo -e "${RED}✗${NC} .buildozer/ missing"
fi

if [ -d ~/.buildozer ]; then
    echo -e "${GREEN}✓${NC} ~/.buildozer/ exists"
    echo "  Size: $(du -sh ~/.buildozer 2>/dev/null | cut -f1 || echo 'unknown')"
else
    echo -e "${RED}✗${NC} ~/.buildozer/ missing"
fi

echo ""
echo "Android platform:"
if [ -d .buildozer/android/platform ]; then
    echo -e "${GREEN}✓${NC} Platform directory exists"

    if [ -d .buildozer/android/platform/android-sdk ]; then
        echo -e "  ${GREEN}✓${NC} SDK installed"
    else
        echo -e "  ${RED}✗${NC} SDK missing"
    fi

    if ls .buildozer/android/platform/android-ndk-r* >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} NDK installed: $(ls -d .buildozer/android/platform/android-ndk-r* 2>/dev/null | xargs basename)"
    else
        echo -e "  ${RED}✗${NC} NDK missing"
    fi

    if [ -d .buildozer/android/platform/python-for-android ]; then
        echo -e "  ${GREEN}✓${NC} Python-for-Android installed"
    else
        echo -e "  ${RED}✗${NC} Python-for-Android missing"
    fi
else
    echo -e "${RED}✗${NC} Platform directory missing"
fi

echo ""
echo -e "${BLUE}5. System Resources${NC}"
echo "========================================="

echo "Disk space:"
df -h . | tail -1 | awk '{print "  Available: " $4 " (" $5 " used)"}'

echo ""
echo "Memory:"
free -h 2>/dev/null | grep "Mem:" | awk '{print "  Total: " $2 ", Available: " $7}' || echo "  Unable to check (Linux only)"

echo ""
echo -e "${BLUE}6. Environment Variables${NC}"
echo "========================================="

echo "Build-related variables:"
echo "  BUILDOZER_WARN_ON_ROOT: ${BUILDOZER_WARN_ON_ROOT:-not set}"
echo "  ANDROIDSDK: ${ANDROIDSDK:-not set}"
echo "  ANDROIDNDK: ${ANDROIDNDK:-not set}"
echo "  ANDROIDAPI: ${ANDROIDAPI:-not set}"
echo "  JAVA_HOME: ${JAVA_HOME:-not set}"
echo "  PATH (first 100 chars): ${PATH:0:100}..."

echo ""
echo -e "${BLUE}7. Tool Versions${NC}"
echo "========================================="

echo "Python: $(python3 --version 2>&1 || echo 'not found')"
echo "Buildozer: $(buildozer --version 2>&1 | head -n 1 || echo 'not found')"
echo "Java: $(java -version 2>&1 | head -n 1 || echo 'not found')"
echo "Git: $(git --version 2>&1 || echo 'not found')"

echo ""
echo -e "${BLUE}8. Recent Build Artifacts${NC}"
echo "========================================="

if [ -d bin ]; then
    echo "APK files in bin/:"
    ls -lh bin/*.apk 2>/dev/null || echo "  No APK files found"
else
    echo "bin/ directory does not exist"
fi

echo ""
echo -e "${BLUE}9. Buildozer Spec Configuration${NC}"
echo "========================================="

if [ -f buildozer.spec ]; then
    echo "Key configuration values:"
    echo "  Python version: $(grep "requirements.*python3" buildozer.spec | cut -d= -f2 | cut -d, -f1)"
    echo "  Kivy version: $(grep "requirements.*kivy" buildozer.spec | cut -d= -f2 | grep -o 'kivy[^,]*')"
    echo "  P4A release: $(grep "^p4a.release" buildozer.spec | cut -d= -f2 || echo 'not set')"
    echo "  P4A branch: $(grep "^p4a.branch" buildozer.spec | cut -d= -f2 || echo 'not set')"
    echo "  NDK: $(grep "^android.ndk" buildozer.spec | cut -d= -f2 | tr -d ' ' || echo 'not set')"
    echo "  API: $(grep "^android.api" buildozer.spec | cut -d= -f2 | tr -d ' ')"
    echo "  Architectures: $(grep "^android.archs" buildozer.spec | cut -d= -f2 | tr -d ' ')"
else
    echo -e "${RED}✗${NC} buildozer.spec not found!"
fi

echo ""
echo -e "${BLUE}10. Recommended Actions${NC}"
echo "========================================="

# Analyze and provide recommendations
RECOMMENDATIONS=()

if [ ! -f "$BUILD_LOG" ]; then
    RECOMMENDATIONS+=("Run: buildozer -v android debug (for verbose output)")
fi

if [ ! -d .buildozer/android/platform/android-sdk ]; then
    RECOMMENDATIONS+=("SDK is missing - buildozer will download it on next run")
fi

if ! ls .buildozer/android/platform/android-ndk-r* >/dev/null 2>&1; then
    RECOMMENDATIONS+=("NDK is missing - buildozer will download it on next run")
fi

if [ -n "$BUILD_LOG" ] && grep -i "out of memory" "$BUILD_LOG" >/dev/null; then
    RECOMMENDATIONS+=("Out of memory detected - close other applications or increase swap")
fi

if [ -n "$BUILD_LOG" ] && grep -i "network\|download.*fail\|connection.*timeout" "$BUILD_LOG" >/dev/null; then
    RECOMMENDATIONS+=("Network errors detected - check internet connection and retry")
fi

if grep -q "^p4a.branch" buildozer.spec 2>/dev/null; then
    RECOMMENDATIONS+=("WARNING: Using p4a.branch instead of p4a.release - switch to stable release")
fi

AVAILABLE_SPACE_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE_GB" -lt 10 ]; then
    RECOMMENDATIONS+=("Low disk space (${AVAILABLE_SPACE_GB}GB) - free up at least 10GB")
fi

if [ ${#RECOMMENDATIONS[@]} -eq 0 ]; then
    echo -e "${GREEN}No immediate issues detected.${NC}"
    echo ""
    echo "General troubleshooting steps:"
    echo "1. Clean build: buildozer android clean"
    echo "2. Remove caches: rm -rf ~/.buildozer .buildozer"
    echo "3. Verify environment: ./verify_build_environment.sh"
    echo "4. Check BUILD_GUIDE.md for detailed troubleshooting"
else
    for i in "${!RECOMMENDATIONS[@]}"; do
        echo -e "${YELLOW}$((i+1)).${NC} ${RECOMMENDATIONS[$i]}"
    done
fi

echo ""
echo "========================================="
echo "Diagnostic Complete"
echo "========================================="
echo ""
echo "For more help, see:"
echo "  - BUILD_GUIDE.md (troubleshooting section)"
echo "  - https://buildozer.readthedocs.io/"
echo "  - .buildozer/android/platform/build-*/build.log (full log)"
echo ""
