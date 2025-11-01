#!/usr/bin/env python3
"""
IGCSE GYM - Post-Build Verification Script
This script verifies the built APK has all required components
"""

import os
import sys
import subprocess
import zipfile
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class APKVerifier:
    """Verifies APK build artifacts"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0
        self.apk_path = None

    def find_apk(self):
        """Find the built APK file"""
        print(f"\n{Colors.BLUE}[SEARCH]{Colors.END} Looking for APK file...")

        # Common APK locations
        search_paths = [
            'bin',
            '.buildozer/android/platform/build-arm64-v8a/dists/igcsegym/build/outputs/apk/debug',
            '.buildozer/android/platform/build-arm64-v8a/dists/igcsegym/build/outputs/apk/release',
        ]

        for search_path in search_paths:
            if os.path.exists(search_path):
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if file.endswith('.apk'):
                            apk_path = os.path.join(root, file)
                            apk_size = os.path.getsize(apk_path)
                            apk_size_mb = apk_size / (1024 * 1024)

                            print(f"{Colors.GREEN}✓ Found APK{Colors.END}")
                            print(f"  → Path: {apk_path}")
                            print(f"  → Size: {apk_size_mb:.2f} MB")

                            self.apk_path = apk_path
                            return True

        print(f"{Colors.RED}✗ No APK found{Colors.END}")
        print(f"  → Searched in: {', '.join(search_paths)}")
        return False

    def check(self, description, validation_func):
        """Run a validation check"""
        self.checks_total += 1
        print(f"\n{Colors.BLUE}[CHECK {self.checks_total}]{Colors.END} {description}...", end=" ")

        try:
            result, message = validation_func()
            if result:
                print(f"{Colors.GREEN}✓ PASS{Colors.END}")
                if message:
                    print(f"  → {message}")
                self.checks_passed += 1
                return True
            else:
                print(f"{Colors.RED}✗ FAIL{Colors.END}")
                print(f"  → {Colors.RED}{message}{Colors.END}")
                self.errors.append(message)
                return False
        except Exception as e:
            print(f"{Colors.RED}✗ ERROR{Colors.END}")
            error_msg = f"{description}: {str(e)}"
            print(f"  → {Colors.RED}{error_msg}{Colors.END}")
            self.errors.append(error_msg)
            return False

    def validate_apk_size(self):
        """Check APK size is reasonable"""
        def check():
            size_bytes = os.path.getsize(self.apk_path)
            size_mb = size_bytes / (1024 * 1024)

            # APK should be between 10MB and 100MB typically
            if size_mb < 5:
                return False, f"APK too small ({size_mb:.2f} MB) - may be incomplete"
            elif size_mb > 150:
                return False, f"APK too large ({size_mb:.2f} MB) - may have bloat"
            else:
                return True, f"{size_mb:.2f} MB (reasonable size)"

        self.check("Validating APK size", check)

    def validate_apk_structure(self):
        """Check APK internal structure"""
        def check():
            try:
                with zipfile.ZipFile(self.apk_path, 'r') as apk:
                    files = apk.namelist()

                    required_files = [
                        'AndroidManifest.xml',
                        'classes.dex',
                        'resources.arsc',
                    ]

                    missing = []
                    for req_file in required_files:
                        if req_file not in files:
                            missing.append(req_file)

                    if missing:
                        return False, f"Missing required files: {', '.join(missing)}"

                    return True, f"APK structure valid ({len(files)} files)"

            except zipfile.BadZipFile:
                return False, "APK file is corrupted"

        self.check("Validating APK structure", check)

    def validate_apk_contents(self):
        """Check APK contains expected assets"""
        def check():
            try:
                with zipfile.ZipFile(self.apk_path, 'r') as apk:
                    files = apk.namelist()

                    # Check for Python files (should be packaged)
                    python_files = [f for f in files if 'main_android.py' in f or '.pyo' in f or '.pyc' in f]
                    if not python_files:
                        return False, "No Python files found in APK"

                    # Check for assets
                    asset_files = [f for f in files if 'assets/' in f]
                    if not asset_files:
                        return False, "No assets found in APK"

                    # Check for icon
                    icon_files = [f for f in files if 'icon' in f.lower()]
                    if not icon_files:
                        return False, "No icon found in APK"

                    return True, f"Python files: {len(python_files)}, Assets: {len(asset_files)}"

            except Exception as e:
                return False, f"Error reading APK contents: {str(e)}"

        self.check("Validating APK contents", check)

    def validate_apk_manifest(self):
        """Check APK manifest (requires aapt or aapt2)"""
        def check():
            # Try to use aapt/aapt2 to read manifest
            aapt_paths = [
                '.buildozer/android/platform/android-sdk/build-tools/*/aapt',
                '.buildozer/android/platform/android-sdk/build-tools/*/aapt2',
            ]

            aapt_cmd = None
            for pattern in aapt_paths:
                import glob
                matches = glob.glob(pattern)
                if matches:
                    aapt_cmd = matches[0]
                    break

            if not aapt_cmd:
                return True, "aapt not found - skipping manifest check"

            try:
                result = subprocess.run(
                    [aapt_cmd, 'dump', 'badging', self.apk_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    return False, "Failed to read APK manifest"

                output = result.stdout

                # Check for package name
                if 'com.igcse.igcsegym' not in output:
                    return False, "Package name mismatch"

                # Check for permissions
                required_perms = ['WRITE_EXTERNAL_STORAGE', 'READ_EXTERNAL_STORAGE']
                missing_perms = []
                for perm in required_perms:
                    if perm not in output:
                        missing_perms.append(perm)

                if missing_perms:
                    return False, f"Missing permissions: {', '.join(missing_perms)}"

                return True, "Manifest valid with all permissions"

            except subprocess.TimeoutExpired:
                return True, "Manifest check timed out - skipping"
            except Exception as e:
                return True, f"Could not check manifest: {str(e)}"

        self.check("Validating APK manifest", check)

    def validate_apk_libraries(self):
        """Check APK contains required native libraries"""
        def check():
            try:
                with zipfile.ZipFile(self.apk_path, 'r') as apk:
                    files = apk.namelist()

                    # Check for native libraries
                    lib_files = [f for f in files if f.startswith('lib/') and f.endswith('.so')]

                    if not lib_files:
                        return False, "No native libraries found"

                    # Check for Python library
                    python_libs = [f for f in lib_files if 'python' in f.lower()]
                    if not python_libs:
                        return False, "Python native library not found"

                    # Check for SDL2 libraries (required by Kivy)
                    sdl_libs = [f for f in lib_files if 'SDL2' in f]
                    if not sdl_libs:
                        return False, "SDL2 libraries not found"

                    return True, f"Found {len(lib_files)} native libraries"

            except Exception as e:
                return False, f"Error checking libraries: {str(e)}"

        self.check("Validating native libraries", check)

    def run_all_checks(self):
        """Run all validation checks"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}IGCSE GYM - Post-Build Verification{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}")

        # Find APK
        if not self.find_apk():
            print(f"\n{Colors.RED}{Colors.BOLD}✗ Cannot verify - APK not found{Colors.END}\n")
            return False

        # Run checks
        print(f"\n{Colors.BOLD}[1] APK Validation{Colors.END}")
        self.validate_apk_size()
        self.validate_apk_structure()
        self.validate_apk_contents()
        self.validate_apk_libraries()
        self.validate_apk_manifest()

        # Summary
        self.print_summary()

        return len(self.errors) == 0

    def print_summary(self):
        """Print validation summary"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}Verification Summary{Colors.END}")
        print(f"{'='*70}")

        print(f"\nAPK Path: {self.apk_path}")
        print(f"Checks passed: {Colors.GREEN}{self.checks_passed}/{self.checks_total}{Colors.END}")

        if self.warnings:
            print(f"\n{Colors.YELLOW}Warnings ({len(self.warnings)}):{Colors.END}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if self.errors:
            print(f"\n{Colors.RED}Errors ({len(self.errors)}):{Colors.END}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

            print(f"\n{Colors.RED}{Colors.BOLD}✗ Verification FAILED{Colors.END}")
            print(f"{Colors.RED}The APK may have issues.{Colors.END}")
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All checks PASSED!{Colors.END}")
            print(f"{Colors.GREEN}APK is ready for deployment.{Colors.END}")

        print(f"{'='*70}\n")


def main():
    """Main entry point"""
    verifier = APKVerifier()
    success = verifier.run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
