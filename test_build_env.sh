#!/bin/bash
# Comprehensive Build Environment Test Script
# Tests all dependencies and configurations needed for Android build

set -e

echo "=========================================="
echo "Build Environment Validation Script"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

check_command() {
    local cmd=$1
    local name=$2
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $name found: $(command -v $cmd)"
        if [ "$3" = "version" ]; then
            $cmd --version 2>&1 | head -n 1 | sed 's/^/  /'
        fi
        return 0
    else
        echo -e "${RED}✗${NC} $name not found"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

check_python_package() {
    local package=$1
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python package '$package' installed"
        python3 -c "import $package; print('  Version:', getattr($package, '__version__', 'unknown'))" 2>/dev/null || true
        return 0
    else
        echo -e "${RED}✗${NC} Python package '$package' not installed"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

check_file() {
    local file=$1
    local name=$2
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $name found: $file"
        return 0
    else
        echo -e "${RED}✗${NC} $name not found: $file"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

check_dir() {
    local dir=$1
    local name=$2
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $name found: $dir"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $name not found: $dir"
        WARNINGS=$((WARNINGS + 1))
        return 1
    fi
}

echo "1. Checking System Commands"
echo "----------------------------"
check_command "python3" "Python3" version
check_command "pip3" "pip3" version
check_command "java" "Java" version
check_command "git" "Git" version
check_command "gcc" "GCC" version
check_command "g++" "G++" version
check_command "make" "Make" version
check_command "autoconf" "Autoconf" version
check_command "automake" "Automake" version
check_command "libtoolize" "Libtool" version
check_command "pkg-config" "pkg-config" version
check_command "ccache" "ccache" version
check_command "patchelf" "patchelf" version
check_command "unzip" "unzip"
check_command "zip" "zip"
echo ""

echo "2. Checking Python Environment"
echo "-------------------------------"
python3 --version
echo "Python executable: $(which python3)"
echo "Pip version: $(pip3 --version)"
echo ""

echo "3. Checking Required Python Packages"
echo "-------------------------------------"
check_python_package "buildozer"
check_python_package "Cython"
check_python_package "pythonforandroid"
check_python_package "kivy"
check_python_package "sh"
check_python_package "colorama"
check_python_package "xlsxwriter"
echo ""

echo "4. Checking Buildozer Installation"
echo "-----------------------------------"
if check_command "buildozer" "Buildozer"; then
    buildozer --version 2>&1 | sed 's/^/  /'
fi
echo ""

echo "5. Checking p4a (python-for-android)"
echo "-------------------------------------"
if check_command "p4a" "p4a"; then
    p4a --version 2>&1 | sed 's/^/  /'
fi
echo ""

echo "6. Checking Java Environment"
echo "-----------------------------"
if [ -n "$JAVA_HOME" ]; then
    echo -e "${GREEN}✓${NC} JAVA_HOME set: $JAVA_HOME"
    if [ -d "$JAVA_HOME" ]; then
        echo -e "${GREEN}✓${NC} JAVA_HOME directory exists"
    else
        echo -e "${RED}✗${NC} JAVA_HOME directory does not exist"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠${NC} JAVA_HOME not set"
    WARNINGS=$((WARNINGS + 1))
fi
java -version 2>&1 | sed 's/^/  /'
echo ""

echo "7. Checking Android Environment"
echo "--------------------------------"
if [ -n "$ANDROID_HOME" ]; then
    echo -e "${GREEN}✓${NC} ANDROID_HOME set: $ANDROID_HOME"
    check_dir "$ANDROID_HOME" "Android SDK directory"
else
    echo -e "${YELLOW}⚠${NC} ANDROID_HOME not set (will be set by buildozer)"
    WARNINGS=$((WARNINGS + 1))
fi

if [ -n "$ANDROID_NDK_HOME" ]; then
    echo -e "${GREEN}✓${NC} ANDROID_NDK_HOME set: $ANDROID_NDK_HOME"
    check_dir "$ANDROID_NDK_HOME" "Android NDK directory"
else
    echo -e "${YELLOW}⚠${NC} ANDROID_NDK_HOME not set (will be set by buildozer)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

echo "8. Checking Project Files"
echo "--------------------------"
check_file "buildozer.spec" "buildozer.spec"
check_file "main_android.py" "main_android.py"
check_dir "assets" "Assets directory"
echo ""

echo "9. Validating buildozer.spec"
echo "-----------------------------"
if [ -f "buildozer.spec" ]; then
    echo "Requirements:"
    grep "^requirements" buildozer.spec | sed 's/^/  /'
    echo "Android API:"
    grep "^android.api" buildozer.spec | sed 's/^/  /'
    echo "Android NDK:"
    grep "^android.ndk" buildozer.spec | sed 's/^/  /'
    echo "P4A branch:"
    grep "^p4a.branch" buildozer.spec | sed 's/^/  /'
    echo "Architectures:"
    grep "^android.archs" buildozer.spec | sed 's/^/  /'
fi
echo ""

echo "10. Checking System Libraries"
echo "------------------------------"
check_lib() {
    local lib=$1
    if ldconfig -p | grep -q "$lib"; then
        echo -e "${GREEN}✓${NC} $lib found"
    else
        echo -e "${YELLOW}⚠${NC} $lib not found"
        WARNINGS=$((WARNINGS + 1))
    fi
}

check_lib "libffi"
check_lib "libssl"
check_lib "libz"
check_lib "libncurses"
check_lib "libsqlite3"
echo ""

echo "11. Checking Autotools Configuration"
echo "-------------------------------------"
echo "Autoconf version:"
autoconf --version | head -n 1 | sed 's/^/  /'
echo "Automake version:"
automake --version | head -n 1 | sed 's/^/  /'
echo "Libtool version:"
libtoolize --version | head -n 1 | sed 's/^/  /'

if [ -n "$ACLOCAL_PATH" ]; then
    echo -e "${GREEN}✓${NC} ACLOCAL_PATH set: $ACLOCAL_PATH"
else
    echo -e "${YELLOW}⚠${NC} ACLOCAL_PATH not set"
fi

echo "Checking for libtool m4 macros:"
if [ -d "/usr/share/aclocal" ]; then
    if ls /usr/share/aclocal/libtool*.m4 &>/dev/null; then
        echo -e "${GREEN}✓${NC} Libtool m4 macros found:"
        ls /usr/share/aclocal/libtool*.m4 | sed 's/^/  /'
    else
        echo -e "${RED}✗${NC} Libtool m4 macros not found"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}✗${NC} /usr/share/aclocal directory not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "12. Testing Python Syntax"
echo "-------------------------"
if [ -f "main_android.py" ]; then
    if python3 -m py_compile main_android.py 2>/dev/null; then
        echo -e "${GREEN}✓${NC} main_android.py syntax is valid"
    else
        echo -e "${RED}✗${NC} main_android.py has syntax errors"
        python3 -m py_compile main_android.py 2>&1 | sed 's/^/  /'
        ERRORS=$((ERRORS + 1))
    fi
fi
echo ""

echo "13. Checking Disk Space"
echo "-----------------------"
df -h . | tail -n 1 | awk '{print "Available space: " $4}'
AVAILABLE=$(df . | tail -n 1 | awk '{print $4}')
if [ "$AVAILABLE" -gt 10485760 ]; then  # 10GB in KB
    echo -e "${GREEN}✓${NC} Sufficient disk space (>10GB)"
else
    echo -e "${YELLOW}⚠${NC} Low disk space (<10GB), build may fail"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

echo "14. Checking Memory"
echo "-------------------"
if command -v free &> /dev/null; then
    free -h | grep "Mem:" | sed 's/^/  /'
    AVAILABLE_MEM=$(free -m | grep "Mem:" | awk '{print $7}')
    if [ "$AVAILABLE_MEM" -gt 2048 ]; then
        echo -e "${GREEN}✓${NC} Sufficient memory (>2GB available)"
    else
        echo -e "${YELLOW}⚠${NC} Low memory (<2GB available), build may be slow"
        WARNINGS=$((WARNINGS + 1))
    fi
fi
echo ""

echo "=========================================="
echo "Validation Summary"
echo "=========================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo "The build environment is ready."
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validation completed with $WARNINGS warning(s)${NC}"
    echo "The build may work but some optional features might be unavailable."
    exit 0
else
    echo -e "${RED}✗ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo "Please fix the errors before attempting to build."
    exit 1
fi
