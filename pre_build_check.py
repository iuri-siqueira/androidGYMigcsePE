#!/usr/bin/env python3
"""
IGCSE GYM - Comprehensive Pre-Build Validation Script
This script ensures all requirements are met before building the Android APK
"""

import os
import sys
import json
import subprocess
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class PreBuildValidator:
    """Validates all requirements before building"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0

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

    def warn(self, description, validation_func):
        """Run a validation check that only warns"""
        print(f"\n{Colors.BLUE}[WARN]{Colors.END} {description}...", end=" ")

        try:
            result, message = validation_func()
            if result:
                print(f"{Colors.GREEN}✓ OK{Colors.END}")
                if message:
                    print(f"  → {message}")
            else:
                print(f"{Colors.YELLOW}⚠ WARNING{Colors.END}")
                print(f"  → {Colors.YELLOW}{message}{Colors.END}")
                self.warnings.append(message)
        except Exception as e:
            print(f"{Colors.YELLOW}⚠ WARNING{Colors.END}")
            warn_msg = f"{description}: {str(e)}"
            print(f"  → {Colors.YELLOW}{warn_msg}{Colors.END}")
            self.warnings.append(warn_msg)

    def validate_file_exists(self, filepath, description):
        """Check if a file exists"""
        def check():
            exists = os.path.exists(filepath)
            if exists:
                size = os.path.getsize(filepath)
                return True, f"Found ({size:,} bytes)"
            return False, f"File not found: {filepath}"

        self.check(f"Checking {description}", check)

    def validate_directory_exists(self, dirpath, description):
        """Check if a directory exists"""
        def check():
            exists = os.path.isdir(dirpath)
            if exists:
                count = len(os.listdir(dirpath))
                return True, f"Found ({count} items)"
            return False, f"Directory not found: {dirpath}"

        self.check(f"Checking {description}", check)

    def validate_python_version(self):
        """Check Python version"""
        def check():
            version = sys.version_info
            version_str = f"{version.major}.{version.minor}.{version.micro}"

            if version.major == 3 and version.minor >= 8:
                return True, f"Python {version_str} (compatible)"
            return False, f"Python {version_str} - requires Python 3.8+"

        self.check("Checking Python version", check)

    def validate_buildozer_spec(self):
        """Validate buildozer.spec configuration"""
        def check():
            spec_path = "buildozer.spec"
            if not os.path.exists(spec_path):
                return False, "buildozer.spec not found"

            with open(spec_path, 'r') as f:
                content = f.read()

            required_settings = {
                'title = IGCSE GYM': 'Application title',
                'package.name = igcsegym': 'Package name',
                'package.domain = com.igcse': 'Package domain',
                'source.main = main_android.py': 'Main entry point',
                'requirements = python3,kivy': 'Python requirements',
                'android.api = 33': 'Target Android API',
                'android.minapi = 21': 'Minimum Android API',
                'android.archs = arm64-v8a': 'ARM64 architecture',
                'p4a.branch = develop': 'P4A develop branch',
            }

            missing = []
            for setting, desc in required_settings.items():
                if setting not in content:
                    missing.append(desc)

            if missing:
                return False, f"Missing settings: {', '.join(missing)}"

            return True, "All required settings present"

        self.check("Validating buildozer.spec", check)

    def validate_main_app_file(self):
        """Validate main application file"""
        def check():
            app_path = "main_android.py"
            if not os.path.exists(app_path):
                return False, "main_android.py not found"

            with open(app_path, 'r') as f:
                content = f.read()

            # Check for critical components
            critical_components = [
                ('class IGCSEGymApp(App):', 'Main app class'),
                ('class WorkoutScreen', 'Workout screen'),
                ('class ReportsScreen', 'Reports screen'),
                ('class RestTimerWidget', 'Rest timer'),
                ('class DataStorage', 'Data storage'),
                ('xlsxwriter', 'Excel export library'),
                ('def export_to_excel_format', 'Excel export function'),
            ]

            missing = []
            for component, desc in critical_components:
                if component not in content:
                    missing.append(desc)

            if missing:
                return False, f"Missing components: {', '.join(missing)}"

            # Count exercises in default data
            exercise_count = content.count('"id":')
            return True, f"All components present, {exercise_count} exercises defined"

        self.check("Validating main application file", check)

    def validate_exercise_data(self):
        """Validate exercise data completeness"""
        def check():
            app_path = "main_android.py"
            with open(app_path, 'r') as f:
                content = f.read()

            # Expected exercises
            expected_exercises = {
                'Session 1': ["Back squat", "Bridge", "Bench press", "Bench superman",
                            "Bentover Row", "Pallof Twist", "Shoulder press", "Knee Tucks"],
                'Session 2': ["Plank", "Incline Bench Press", "Pallof Press",
                            "Lat Pull Downs", "Landmines", "Upright row"],
                'Warmup Dynamic': ["Arm Circles", "Leg Swings", "Torso Twists", "High Knees"],
                'Warmup Stability': ["Single Leg Balance", "Bird Dog", "Wall Sits", "Glute Bridges"],
                'Warmup Movement': ["Bodyweight Squats", "Push-up to Downward Dog",
                                  "Lunge with Rotation", "Cat-Cow Stretch"]
            }

            missing = []
            for category, exercises in expected_exercises.items():
                for exercise in exercises:
                    if f'"{exercise}"' not in content:
                        missing.append(f"{exercise} ({category})")

            if missing:
                return False, f"Missing exercises: {', '.join(missing[:3])}... ({len(missing)} total)"

            total_exercises = sum(len(exs) for exs in expected_exercises.values())
            return True, f"All {total_exercises} exercises present"

        self.check("Validating exercise database", check)

    def validate_permissions(self):
        """Validate Android permissions"""
        def check():
            spec_path = "buildozer.spec"
            with open(spec_path, 'r') as f:
                content = f.read()

            required_permissions = [
                'WRITE_EXTERNAL_STORAGE',
                'READ_EXTERNAL_STORAGE',
            ]

            missing = []
            for perm in required_permissions:
                if perm not in content:
                    missing.append(perm)

            if missing:
                return False, f"Missing permissions: {', '.join(missing)}"

            return True, "All required permissions configured"

        self.check("Validating Android permissions", check)

    def validate_assets(self):
        """Validate required assets"""
        assets = {
            'assets/icon.png': 'App icon',
            'assets/presplash.png': 'Splash screen'
        }

        for asset_path, desc in assets.items():
            self.validate_file_exists(asset_path, desc)

    def validate_python_packages(self):
        """Check if required Python packages are available"""
        def check():
            try:
                import kivy
                return True, f"Kivy {kivy.__version__}"
            except ImportError:
                return False, "Kivy not installed (install: pip install kivy)"

        self.check("Checking Kivy installation", check)

        def check_buildozer():
            try:
                result = subprocess.run(['buildozer', 'version'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    return True, f"Buildozer installed: {version}"
                return False, "Buildozer not working"
            except FileNotFoundError:
                return False, "Buildozer not installed (install: pip install buildozer)"
            except subprocess.TimeoutExpired:
                return False, "Buildozer check timed out"

        self.check("Checking Buildozer installation", check_buildozer)

    def validate_git_status(self):
        """Check git status"""
        def check():
            try:
                result = subprocess.run(['git', 'status', '--porcelain'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    changes = result.stdout.strip()
                    if changes:
                        num_files = len(changes.split('\n'))
                        return True, f"{num_files} uncommitted changes"
                    return True, "Working tree clean"
                return False, "Git not available"
            except:
                return False, "Git check failed"

        self.warn("Checking git status", check)

    def validate_disk_space(self):
        """Check available disk space"""
        def check():
            try:
                stat = os.statvfs('.')
                free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)

                if free_gb < 5:
                    return False, f"Only {free_gb:.1f}GB free - need at least 5GB"
                return True, f"{free_gb:.1f}GB available"
            except:
                return True, "Could not check disk space"

        self.check("Checking disk space", check)

    def validate_feature_completeness(self):
        """Validate all features are implemented"""
        def check():
            app_path = "main_android.py"
            with open(app_path, 'r') as f:
                content = f.read()

            required_features = {
                'Rest timer': ['class RestTimerWidget', 'DEFAULT_REST_TIME_SECONDS = 75'],
                'Excel export': ['xlsxwriter', 'def export_to_excel_format'],
                'CSV fallback': ['import csv', 'csv.writer'],
                'Data persistence': ['class DataStorage', 'json.dump'],
                'Workout logging': ['def log_workout', 'save_workout_session'],
                'Input validation': ['MAX_WEIGHT_KG', 'MAX_REPS', 'Invalid Input'],
                'Android storage': ['primary_external_storage_path', 'Download'],
                'Warmup categories': ['warmup-dynamic', 'warmup-stability', 'warmup-movement'],
            }

            missing_features = []
            for feature, keywords in required_features.items():
                if not all(keyword in content for keyword in keywords):
                    missing_features.append(feature)

            if missing_features:
                return False, f"Missing features: {', '.join(missing_features)}"

            return True, f"All {len(required_features)} features implemented"

        self.check("Validating feature completeness", check)

    def run_all_checks(self):
        """Run all validation checks"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}IGCSE GYM - Pre-Build Validation{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}")

        # Core system checks
        print(f"\n{Colors.BOLD}[1] System Requirements{Colors.END}")
        self.validate_python_version()
        self.validate_python_packages()
        self.validate_disk_space()

        # Project structure checks
        print(f"\n{Colors.BOLD}[2] Project Structure{Colors.END}")
        self.validate_file_exists("buildozer.spec", "buildozer.spec")
        self.validate_file_exists("main_android.py", "main_android.py")
        self.validate_file_exists("requirements.txt", "requirements.txt")
        self.validate_directory_exists("assets", "assets directory")

        # Configuration checks
        print(f"\n{Colors.BOLD}[3] Build Configuration{Colors.END}")
        self.validate_buildozer_spec()
        self.validate_permissions()

        # Application checks
        print(f"\n{Colors.BOLD}[4] Application Code{Colors.END}")
        self.validate_main_app_file()
        self.validate_exercise_data()
        self.validate_feature_completeness()

        # Asset checks
        print(f"\n{Colors.BOLD}[5] Required Assets{Colors.END}")
        self.validate_assets()

        # Optional checks (warnings only)
        print(f"\n{Colors.BOLD}[6] Optional Checks{Colors.END}")
        self.validate_git_status()

        # Summary
        self.print_summary()

        return len(self.errors) == 0

    def print_summary(self):
        """Print validation summary"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}Validation Summary{Colors.END}")
        print(f"{'='*70}")

        print(f"\nChecks passed: {Colors.GREEN}{self.checks_passed}/{self.checks_total}{Colors.END}")

        if self.warnings:
            print(f"\n{Colors.YELLOW}Warnings ({len(self.warnings)}):{Colors.END}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if self.errors:
            print(f"\n{Colors.RED}Errors ({len(self.errors)}):{Colors.END}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

            print(f"\n{Colors.RED}{Colors.BOLD}✗ Validation FAILED{Colors.END}")
            print(f"{Colors.RED}Please fix the errors above before building.{Colors.END}")
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All checks PASSED!{Colors.END}")
            print(f"{Colors.GREEN}Ready to build the APK.{Colors.END}")

        print(f"{'='*70}\n")


def main():
    """Main entry point"""
    validator = PreBuildValidator()
    success = validator.run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
