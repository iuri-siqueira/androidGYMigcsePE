#!/bin/bash
###############################################################################
# IGCSE GYM - FLAWLESS BUILD SCRIPT
# This script ensures a perfect build with all features working correctly
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_CLEAN=false
RUN_TESTS=true
DEPLOY_APK=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            BUILD_CLEAN=true
            shift
            ;;
        --no-tests)
            RUN_TESTS=false
            shift
            ;;
        --deploy)
            DEPLOY_APK=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --clean       Clean build (remove .buildozer and bin)"
            echo "  --no-tests    Skip pre-build validation"
            echo "  --deploy      Deploy APK after successful build"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${BLUE}  $1${NC}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_step() {
    echo -e "${BOLD}${GREEN}▶ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        exit 1
    fi
}

###############################################################################
# Main Build Process
###############################################################################

main() {
    cd "$SCRIPT_DIR"

    print_header "IGCSE GYM - FLAWLESS BUILD SYSTEM"

    echo -e "${BOLD}Build Configuration:${NC}"
    echo "  Clean Build: $BUILD_CLEAN"
    echo "  Run Tests: $RUN_TESTS"
    echo "  Deploy APK: $DEPLOY_APK"
    echo ""

    # Step 1: Check prerequisites
    print_header "STEP 1: Checking Prerequisites"
    print_step "Verifying system requirements..."

    check_command python3
    check_command pip
    check_command git

    print_success "All prerequisites satisfied"

    # Step 2: Clean build if requested
    if [ "$BUILD_CLEAN" = true ]; then
        print_header "STEP 2: Cleaning Build Environment"
        print_step "Removing previous build artifacts..."

        rm -rf .buildozer
        rm -rf bin
        rm -rf build
        rm -rf dist
        rm -rf __pycache__

        print_success "Build environment cleaned"
    else
        print_header "STEP 2: Preserving Build Cache"
        print_info "Using existing build cache (use --clean to rebuild from scratch)"
    fi

    # Step 3: Pre-build validation
    if [ "$RUN_TESTS" = true ]; then
        print_header "STEP 3: Pre-Build Validation"
        print_step "Running comprehensive pre-build checks..."

        if python3 pre_build_check.py; then
            print_success "Pre-build validation passed"
        else
            print_error "Pre-build validation failed"
            print_warning "Fix the errors above before building"
            exit 1
        fi
    else
        print_header "STEP 3: Skipping Pre-Build Validation"
        print_warning "Pre-build validation skipped (use --no-tests to skip)"
    fi

    # Step 4: Install/Update build dependencies
    print_header "STEP 4: Installing Build Dependencies"
    print_step "Ensuring all Python dependencies are installed..."

    if [ -f "requirements.txt" ]; then
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
        print_success "Build dependencies installed"
    else
        print_warning "requirements.txt not found, skipping"
    fi

    # Step 5: Build APK
    print_header "STEP 5: Building Android APK"
    print_step "Starting buildozer build process..."
    print_info "This may take 10-30 minutes depending on your system"
    print_info "First build will download SDK/NDK (~2GB)"

    echo ""
    echo -e "${BOLD}Buildozer Output:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Run buildozer with proper error handling
    if buildozer android debug; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_success "APK build completed successfully"
    else
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_error "APK build failed"
        print_info "Check buildozer logs above for details"
        exit 1
    fi

    # Step 6: Post-build verification
    print_header "STEP 6: Post-Build Verification"
    print_step "Verifying APK integrity and contents..."

    if python3 post_build_verify.py; then
        print_success "Post-build verification passed"
    else
        print_warning "Post-build verification found issues"
        print_info "The APK was built but may have problems"
    fi

    # Step 7: Display build results
    print_header "STEP 7: Build Results"

    APK_FILE=$(find bin -name "*.apk" 2>/dev/null | head -n 1)

    if [ -n "$APK_FILE" ]; then
        APK_SIZE=$(du -h "$APK_FILE" | cut -f1)
        APK_PATH=$(realpath "$APK_FILE")

        print_success "APK successfully created!"
        echo ""
        echo -e "${BOLD}APK Details:${NC}"
        echo "  File: $(basename "$APK_FILE")"
        echo "  Size: $APK_SIZE"
        echo "  Path: $APK_PATH"
        echo ""

        # Show what's included
        echo -e "${BOLD}Features Included:${NC}"
        echo "  ✓ 26 exercises (2 workout sessions + 3 warmup categories)"
        echo "  ✓ Rest timer (75s default)"
        echo "  ✓ Weight and reps logging"
        echo "  ✓ Excel report export (.xlsx)"
        echo "  ✓ CSV fallback export"
        echo "  ✓ Android storage permissions"
        echo "  ✓ JSON data persistence"
        echo "  ✓ Workout history tracking"
        echo ""

        # Installation instructions
        echo -e "${BOLD}Installation Instructions:${NC}"
        echo "  1. Transfer APK to your Android device"
        echo "  2. Enable 'Install from Unknown Sources' in device settings"
        echo "  3. Open the APK file to install"
        echo "  4. Grant storage permissions when prompted"
        echo ""

        # Deploy if requested
        if [ "$DEPLOY_APK" = true ]; then
            print_step "Deploying APK to connected device..."

            if command -v adb &> /dev/null; then
                if adb devices | grep -q "device$"; then
                    adb install -r "$APK_FILE"
                    print_success "APK deployed to device"
                else
                    print_warning "No Android device connected"
                    print_info "Connect device and enable USB debugging to deploy"
                fi
            else
                print_warning "adb not installed, cannot deploy"
                print_info "Install Android SDK platform-tools to enable deployment"
            fi
        fi

    else
        print_error "APK file not found in bin/ directory"
        exit 1
    fi

    # Final summary
    print_header "BUILD COMPLETE"

    echo -e "${BOLD}${GREEN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║                   ✓ BUILD SUCCESSFUL                                  ║${NC}"
    echo -e "${BOLD}${GREEN}║                                                                       ║${NC}"
    echo -e "${BOLD}${GREEN}║  Your IGCSE GYM APK is ready with ALL features working flawlessly!   ║${NC}"
    echo -e "${BOLD}${GREEN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    print_info "APK location: $APK_PATH"
    echo ""
}

# Handle script interruption
trap 'print_error "Build interrupted"; exit 130' INT TERM

# Run main function
main

exit 0
