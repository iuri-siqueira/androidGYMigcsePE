#!/bin/bash

# Build Environment Verification Script for IGCSE GYM Android App
# This script verifies that all prerequisites are met before building

set -e

echo "========================================="
echo "IGCSE GYM - Build Environment Verification"
echo "========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

check_command() {
    local cmd=$1
    local required=$2

    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $cmd is installed"
        ((PASS++))
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} $cmd is NOT installed (REQUIRED)"
            ((FAIL++))
            return 1
        else
            echo -e "${YELLOW}⚠${NC} $cmd is NOT installed (optional)"
            ((WARN++))
            return 0
        fi
    fi
}

check_version() {
    local name=$1
    local version_cmd=$2

    echo -n "  Version: "
    eval "$version_cmd" || echo "unknown"
}

echo "1. Checking Required Commands..."
echo "=================================="

check_command "python3" "true" && check_version "Python" "python3 --version"
check_command "pip3" "true" && check_version "pip" "pip3 --version"
check_command "java" "true" && check_version "Java" "java -version 2>&1 | head -n 1"
check_command "javac" "true" && check_version "Javac" "javac -version 2>&1"
check_command "git" "true" && check_version "Git" "git --version"
check_command "unzip" "true"
check_command "zip" "true"
check_command "buildozer" "true" && check_version "Buildozer" "buildozer --version 2>&1 | head -n 1"

echo ""
echo "2. Checking Optional Tools..."
echo "=============================="

check_command "ccache" "false"
check_command "cmake" "false"
check_command "ninja" "false"

echo ""
echo "3. Checking Python Packages..."
echo "==============================="

check_python_package() {
    local package=$1
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $package is installed"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $package is NOT installed"
        ((FAIL++))
    fi
}

check_python_package "buildozer"
check_python_package "cython"
check_python_package "kivy"

echo ""
echo "4. Checking Environment Variables..."
echo "====================================="

check_env() {
    local var=$1
    local required=$2

    if [ -n "${!var}" ]; then
        echo -e "${GREEN}✓${NC} $var is set: ${!var}"
        ((PASS++))
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} $var is NOT set (REQUIRED)"
            ((FAIL++))
        else
            echo -e "${YELLOW}⚠${NC} $var is NOT set (optional)"
            ((WARN++))
        fi
    fi
}

check_env "JAVA_HOME" "true"
check_env "PATH" "true"
check_env "BUILDOZER_WARN_ON_ROOT" "false"

echo ""
echo "5. Checking File Structure..."
echo "=============================="

check_file() {
    local file=$1
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $file is MISSING"
        ((FAIL++))
    fi
}

check_dir() {
    local dir=$1
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir exists"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠${NC} $dir does not exist (will be created)"
        ((WARN++))
    fi
}

check_file "buildozer.spec"
check_file "main_android.py"
check_file "requirements.txt"
check_dir "assets"
check_file "assets/icon.png"
check_file "assets/presplash.png"

echo ""
echo "6. Checking Disk Space..."
echo "=========================="

available_space=$(df -h . | tail -1 | awk '{print $4}')
echo "  Available space: $available_space"

# Convert to GB for comparison (rough check)
space_gb=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$space_gb" -lt 10 ]; then
    echo -e "${YELLOW}⚠${NC} Low disk space (< 10GB). Android builds require significant space."
    ((WARN++))
else
    echo -e "${GREEN}✓${NC} Sufficient disk space available"
    ((PASS++))
fi

echo ""
echo "========================================="
echo "VERIFICATION SUMMARY"
echo "========================================="
echo -e "${GREEN}Passed:${NC} $PASS"
echo -e "${YELLOW}Warnings:${NC} $WARN"
echo -e "${RED}Failed:${NC} $FAIL"
echo ""

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}FAIL:${NC} Build environment is NOT ready"
    echo "Please fix the failed checks above before building."
    exit 1
elif [ $WARN -gt 0 ]; then
    echo -e "${YELLOW}WARNING:${NC} Build environment has warnings"
    echo "Build may proceed but some features may not work optimally."
    exit 0
else
    echo -e "${GREEN}SUCCESS:${NC} Build environment is ready!"
    echo "You can proceed with: buildozer android debug"
    exit 0
fi
