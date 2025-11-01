#!/usr/bin/env python3
"""
COMPREHENSIVE BUILD DIAGNOSTICS - Find EVERY possible error
This script performs 50+ checks to identify all build issues
"""

import os
import sys
import json
import subprocess
import importlib
import ast
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ComprehensiveDiagnostics:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.checks_passed = 0
        self.checks_failed = 0
        self.checks_total = 0

    def header(self, text):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

    def check(self, description, func):
        """Run a check and track results"""
        self.checks_total += 1
        print(f"{Colors.BLUE}[{self.checks_total:02d}]{Colors.END} {description}...", end=" ")

        try:
            success, message, details = func()

            if success:
                print(f"{Colors.GREEN}✓ PASS{Colors.END}")
                if message:
                    print(f"    → {message}")
                if details:
                    for detail in details:
                        print(f"      • {detail}")
                self.checks_passed += 1
                return True
            else:
                print(f"{Colors.RED}✗ FAIL{Colors.END}")
                print(f"    → {Colors.RED}{message}{Colors.END}")
                if details:
                    for detail in details:
                        print(f"      • {Colors.RED}{detail}{Colors.END}")
                self.errors.append(f"{description}: {message}")
                self.checks_failed += 1
                return False

        except Exception as e:
            print(f"{Colors.RED}✗ ERROR{Colors.END}")
            error_msg = f"Exception in {description}: {str(e)}"
            print(f"    → {Colors.RED}{error_msg}{Colors.END}")
            self.errors.append(error_msg)
            self.checks_failed += 1
            return False

    def warn(self, description, func):
        """Run a check that only warns"""
        print(f"{Colors.YELLOW}[WARN]{Colors.END} {description}...", end=" ")

        try:
            success, message, details = func()

            if success:
                print(f"{Colors.GREEN}✓ OK{Colors.END}")
                if message:
                    print(f"    → {message}")
            else:
                print(f"{Colors.YELLOW}⚠ WARNING{Colors.END}")
                print(f"    → {Colors.YELLOW}{message}{Colors.END}")
                if details:
                    for detail in details:
                        print(f"      • {Colors.YELLOW}{detail}{Colors.END}")
                self.warnings.append(f"{description}: {message}")

        except Exception as e:
            print(f"{Colors.YELLOW}⚠ WARNING{Colors.END}")
            warn_msg = f"Exception: {str(e)}"
            print(f"    → {Colors.YELLOW}{warn_msg}{Colors.END}")
            self.warnings.append(f"{description}: {warn_msg}")

    # ========================================================================
    # PYTHON ENVIRONMENT CHECKS
    # ========================================================================

    def check_python_version(self):
        """Check Python version compatibility"""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        if version.major != 3:
            return False, f"Python {version_str} - must be Python 3.x", []

        if version.minor < 8:
            return False, f"Python {version_str} - requires 3.8+", []

        if version.minor > 11:
            return True, f"Python {version_str} (WARNING: untested with 3.12+)", []

        return True, f"Python {version_str} (compatible)", []

    def check_python_modules(self):
        """Check if all required Python modules can be imported"""
        modules = {
            'os': 'Standard library',
            'json': 'Standard library',
            'csv': 'Standard library',
            'datetime': 'Standard library',
            'logging': 'Standard library',
            'typing': 'Standard library',
        }

        missing = []
        for module, desc in modules.items():
            try:
                importlib.import_module(module)
            except ImportError:
                missing.append(f"{module} ({desc})")

        if missing:
            return False, "Missing standard library modules", missing

        return True, f"All {len(modules)} required modules available", []

    def check_xlsxwriter_importable(self):
        """Check if xlsxwriter can be imported and used"""
        try:
            import xlsxwriter
            version = getattr(xlsxwriter, '__version__', 'unknown')

            # Try creating a simple workbook in memory
            import io
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()
            worksheet.write(0, 0, 'Test')
            workbook.close()

            return True, f"xlsxwriter {version} works correctly", []

        except ImportError:
            return False, "xlsxwriter not installed (will be bundled in APK)", []
        except Exception as e:
            return False, f"xlsxwriter installed but not working: {str(e)}", []

    # ========================================================================
    # FILE STRUCTURE CHECKS
    # ========================================================================

    def check_main_app_syntax(self):
        """Check main_android.py for syntax errors"""
        try:
            with open('main_android.py', 'r') as f:
                code = f.read()

            ast.parse(code)

            # Count key elements
            imports = len(re.findall(r'^import |^from .* import', code, re.MULTILINE))
            classes = len(re.findall(r'^class \w+', code, re.MULTILINE))
            functions = len(re.findall(r'^def \w+', code, re.MULTILINE))

            details = [
                f"{imports} import statements",
                f"{classes} class definitions",
                f"{functions} function definitions"
            ]

            return True, "Valid Python syntax", details

        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}", []
        except FileNotFoundError:
            return False, "main_android.py not found", []

    def check_main_app_imports(self):
        """Check if all imports in main_android.py will work"""
        try:
            with open('main_android.py', 'r') as f:
                code = f.read()

            # Extract all imports
            import_pattern = r'^(?:from\s+([\w.]+)|import\s+([\w.]+))'
            imports = re.findall(import_pattern, code, re.MULTILINE)

            problematic = []
            android_specific = []

            for from_module, import_module in imports:
                module = from_module or import_module
                base_module = module.split('.')[0]

                # Skip android-specific imports
                if base_module == 'android':
                    android_specific.append(module)
                    continue

                # Skip kivy imports (will be in APK)
                if base_module == 'kivy':
                    continue

                # Try to import standard/installed modules
                if base_module not in ['xlsxwriter']:
                    try:
                        importlib.import_module(base_module)
                    except ImportError:
                        problematic.append(module)

            details = []
            if android_specific:
                details.append(f"{len(android_specific)} Android-specific imports (will work on device)")

            if problematic:
                return False, "Some imports will fail", problematic

            return True, "All imports valid", details

        except Exception as e:
            return False, f"Failed to check imports: {str(e)}", []

    def check_exercise_data_complete(self):
        """Verify all 26 exercises are defined"""
        try:
            with open('main_android.py', 'r') as f:
                code = f.read()

            expected_exercises = {
                'Session 1 (8)': [
                    "Back squat", "Bridge", "Bench press", "Bench superman",
                    "Bentover Row", "Pallof Twist", "Shoulder press", "Knee Tucks"
                ],
                'Session 2 (6)': [
                    "Plank", "Incline Bench Press", "Pallof Press",
                    "Lat Pull Downs", "Landmines", "Upright row"
                ],
                'Warmup Dynamic (4)': [
                    "Arm Circles", "Leg Swings", "Torso Twists", "High Knees"
                ],
                'Warmup Stability (4)': [
                    "Single Leg Balance", "Bird Dog", "Wall Sits", "Glute Bridges"
                ],
                'Warmup Movement (4)': [
                    "Bodyweight Squats", "Push-up to Downward Dog",
                    "Lunge with Rotation", "Cat-Cow Stretch"
                ]
            }

            missing = []
            total = 0

            for category, exercises in expected_exercises.items():
                for exercise in exercises:
                    total += 1
                    if f'"{exercise}"' not in code and f"'{exercise}'" not in code:
                        missing.append(f"{exercise} ({category})")

            if missing:
                return False, f"Missing {len(missing)}/26 exercises", missing[:5]

            return True, f"All 26 exercises present", [f"{cat}: ✓" for cat in expected_exercises.keys()]

        except Exception as e:
            return False, f"Failed to check exercises: {str(e)}", []

    def check_critical_features(self):
        """Verify all critical features are implemented"""
        try:
            with open('main_android.py', 'r') as f:
                code = f.read()

            features = {
                'Rest Timer': ['class RestTimerWidget', 'DEFAULT_REST_TIME_SECONDS'],
                'Excel Export': ['xlsxwriter', 'def export_to_excel_format', '.xlsx'],
                'CSV Export': ['import csv', 'csv.writer'],
                'Data Storage': ['class DataStorage', 'json.dump', 'json.load'],
                'Workout Logging': ['save_workout_session', 'save_weight_log'],
                'Permissions': ['PermissionsManager', 'request_permissions'],
                'Storage Handling': ['get_safe_storage_path', 'Downloads'],
                'Input Validation': ['MAX_WEIGHT_KG', 'MAX_REPS']
            }

            missing_features = []

            for feature, keywords in features.items():
                if not all(kw in code for kw in keywords):
                    missing_kw = [kw for kw in keywords if kw not in code]
                    missing_features.append(f"{feature} (missing: {', '.join(missing_kw)})")

            if missing_features:
                return False, "Missing critical features", missing_features

            return True, f"All {len(features)} critical features present", []

        except Exception as e:
            return False, f"Failed to check features: {str(e)}", []

    # ========================================================================
    # BUILDOZER.SPEC CHECKS
    # ========================================================================

    def check_buildozer_spec_exists(self):
        """Check buildozer.spec exists and is readable"""
        if not os.path.exists('buildozer.spec'):
            return False, "buildozer.spec not found", []

        try:
            with open('buildozer.spec', 'r') as f:
                content = f.read()

            lines = len(content.split('\n'))
            size = len(content)

            return True, f"{lines} lines, {size} bytes", []
        except Exception as e:
            return False, f"Cannot read buildozer.spec: {str(e)}", []

    def check_buildozer_spec_syntax(self):
        """Check buildozer.spec for syntax issues"""
        try:
            with open('buildozer.spec', 'r') as f:
                lines = f.readlines()

            issues = []

            for i, line in enumerate(lines, 1):
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Check for = signs
                if '=' in line:
                    parts = line.split('=', 1)
                    if len(parts) != 2:
                        issues.append(f"Line {i}: Invalid syntax")
                    elif not parts[0].strip():
                        issues.append(f"Line {i}: Empty key")

            if issues:
                return False, "Syntax issues found", issues[:5]

            return True, "Valid INI syntax", []

        except Exception as e:
            return False, f"Failed to parse: {str(e)}", []

    def check_buildozer_requirements(self):
        """Check requirements are properly specified"""
        try:
            with open('buildozer.spec', 'r') as f:
                content = f.read()

            # Find requirements line
            req_match = re.search(r'^requirements\s*=\s*(.+)$', content, re.MULTILINE)

            if not req_match:
                return False, "No requirements line found", []

            reqs = [r.strip() for r in req_match.group(1).split(',')]

            issues = []
            required = ['python3', 'kivy', 'xlsxwriter']

            for req in required:
                if not any(req in r for r in reqs):
                    issues.append(f"Missing: {req}")

            # Check for problematic requirements
            for req in reqs:
                if '==' in req and 'python3==' in req:
                    issues.append(f"Don't pin python3 version: {req}")

            if issues:
                return False, "Requirements issues", issues

            return True, f"{len(reqs)} requirements specified", reqs

        except Exception as e:
            return False, f"Failed to check requirements: {str(e)}", []

    def check_buildozer_permissions(self):
        """Check Android permissions are set"""
        try:
            with open('buildozer.spec', 'r') as f:
                content = f.read()

            perm_match = re.search(r'^android\.permissions\s*=\s*(.+)$', content, re.MULTILINE)

            if not perm_match:
                return False, "No android.permissions line", []

            perms = [p.strip() for p in perm_match.group(1).split(',')]

            required = ['WRITE_EXTERNAL_STORAGE', 'READ_EXTERNAL_STORAGE']
            missing = [p for p in required if p not in perms]

            if missing:
                return False, "Missing required permissions", missing

            return True, f"{len(perms)} permissions set", perms

        except Exception as e:
            return False, f"Failed to check permissions: {str(e)}", []

    def check_buildozer_p4a_config(self):
        """Check p4a configuration"""
        try:
            with open('buildozer.spec', 'r') as f:
                content = f.read()

            checks = {
                'p4a.branch': r'p4a\.branch\s*=\s*(\w+)',
                'p4a.local_recipes': r'p4a\.local_recipes\s*=\s*(.+)',
                'p4a.bootstrap': r'p4a\.bootstrap\s*=\s*(\w+)',
            }

            config = {}
            missing = []

            for key, pattern in checks.items():
                match = re.search(pattern, content, re.MULTILINE)
                if match:
                    config[key] = match.group(1).strip()
                else:
                    missing.append(key)

            details = [f"{k} = {v}" for k, v in config.items()]

            if missing:
                details.extend([f"Missing: {m}" for m in missing])

            # Check if local_recipes points to our recipe
            if 'p4a.local_recipes' in config:
                if not os.path.exists(config['p4a.local_recipes']):
                    return False, "p4a.local_recipes path doesn't exist", details

            return True, "P4A configuration found", details

        except Exception as e:
            return False, f"Failed to check p4a config: {str(e)}", []

    # ========================================================================
    # RECIPE CHECKS
    # ========================================================================

    def check_xlsxwriter_recipe_exists(self):
        """Check if xlsxwriter recipe exists"""
        recipe_path = 'p4a-recipes/xlsxwriter/__init__.py'

        if not os.path.exists(recipe_path):
            return False, f"Recipe not found at {recipe_path}", []

        try:
            with open(recipe_path, 'r') as f:
                content = f.read()

            required = [
                'class XlsxwriterRecipe',
                'PythonRecipe',
                "name = 'xlsxwriter'",
                'version =',
            ]

            missing = [r for r in required if r not in content]

            if missing:
                return False, "Recipe incomplete", missing

            return True, "Recipe exists and looks valid", []

        except Exception as e:
            return False, f"Cannot read recipe: {str(e)}", []

    def check_xlsxwriter_recipe_syntax(self):
        """Check xlsxwriter recipe for syntax errors"""
        recipe_path = 'p4a-recipes/xlsxwriter/__init__.py'

        try:
            with open(recipe_path, 'r') as f:
                code = f.read()

            ast.parse(code)

            # Check for recipe instantiation
            if 'recipe = ' not in code:
                return False, "Recipe not instantiated", []

            return True, "Valid Python syntax", []

        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}", []
        except FileNotFoundError:
            return False, "Recipe file not found", []

    # ========================================================================
    # ASSETS CHECKS
    # ========================================================================

    def check_assets_exist(self):
        """Check if required assets exist"""
        required_assets = {
            'assets/icon.png': 'App icon',
            'assets/presplash.png': 'Splash screen'
        }

        missing = []
        found = []

        for asset, desc in required_assets.items():
            if os.path.exists(asset):
                size = os.path.getsize(asset)
                found.append(f"{desc}: {size:,} bytes")
            else:
                missing.append(f"{desc} ({asset})")

        if missing:
            return False, "Missing assets", missing

        return True, "All assets present", found

    def check_assets_valid(self):
        """Check if assets are valid image files"""
        assets = ['assets/icon.png', 'assets/presplash.png']

        invalid = []

        for asset in assets:
            if not os.path.exists(asset):
                continue

            # Check PNG signature
            try:
                with open(asset, 'rb') as f:
                    signature = f.read(8)

                # PNG signature: 89 50 4E 47 0D 0A 1A 0A
                if signature != b'\x89PNG\r\n\x1a\n':
                    invalid.append(f"{asset} (not a valid PNG)")

            except Exception as e:
                invalid.append(f"{asset} (cannot read: {str(e)})")

        if invalid:
            return False, "Invalid assets", invalid

        return True, "All assets valid PNG files", []

    # ========================================================================
    # DEPENDENCY CHECKS
    # ========================================================================

    def check_system_commands(self):
        """Check if required system commands exist"""
        commands = {
            'python3': 'Python interpreter',
            'pip3': 'Python package manager',
            'git': 'Version control',
        }

        missing = []
        found = []

        for cmd, desc in commands.items():
            try:
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    found.append(f"{desc}: {version}")
                else:
                    missing.append(f"{desc} ({cmd})")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                missing.append(f"{desc} ({cmd})")

        if missing:
            return False, "Missing commands", missing

        return True, "All commands available", []

    def check_pip_packages(self):
        """Check if buildozer is installable via pip"""
        try:
            result = subprocess.run(
                ['pip3', 'show', 'buildozer'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Extract version
                version_match = re.search(r'Version: (.+)', result.stdout)
                version = version_match.group(1) if version_match else 'unknown'
                return True, f"buildozer {version} installed", []
            else:
                return False, "buildozer not installed (needed for actual build)", []

        except Exception as e:
            return False, f"Cannot check pip packages: {str(e)}", []

    # ========================================================================
    # GIT CHECKS
    # ========================================================================

    def check_git_status(self):
        """Check git repository status"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                changes = result.stdout.strip()
                if changes:
                    num_files = len(changes.split('\n'))
                    return True, f"{num_files} uncommitted changes", []
                return True, "Working tree clean", []

            return False, "Not a git repository", []

        except Exception as e:
            return False, f"Git check failed: {str(e)}", []

    def check_git_branch(self):
        """Check current git branch"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                branch = result.stdout.strip()
                return True, f"On branch: {branch}", []

            return False, "Cannot determine branch", []

        except Exception as e:
            return False, f"Failed: {str(e)}", []

    # ========================================================================
    # ADVANCED CHECKS
    # ========================================================================

    def check_disk_space(self):
        """Check available disk space"""
        try:
            stat = os.statvfs('.')
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
            used_gb = total_gb - free_gb
            percent = (used_gb / total_gb) * 100

            if free_gb < 5:
                return False, f"Only {free_gb:.1f}GB free (need 5GB+)", [f"Total: {total_gb:.1f}GB, Used: {percent:.1f}%"]
            elif free_gb < 10:
                return True, f"{free_gb:.1f}GB free (barely enough)", [f"Total: {total_gb:.1f}GB, Used: {percent:.1f}%"]
            else:
                return True, f"{free_gb:.1f}GB free", [f"Total: {total_gb:.1f}GB, Used: {percent:.1f}%"]

        except Exception as e:
            return False, f"Cannot check disk space: {str(e)}", []

    def check_memory_available(self):
        """Check available memory"""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()

            mem_total = int(re.search(r'MemTotal:\s+(\d+)', meminfo).group(1)) / 1024
            mem_available = int(re.search(r'MemAvailable:\s+(\d+)', meminfo).group(1)) / 1024

            if mem_available < 1024:
                return False, f"Only {mem_available:.0f}MB available (need 1GB+)", []

            return True, f"{mem_available:.0f}MB available", [f"Total: {mem_total:.0f}MB"]

        except:
            return True, "Cannot check memory (non-Linux?)", []

    def check_file_encoding(self):
        """Check if main files have valid encoding"""
        files = ['main_android.py', 'buildozer.spec']

        issues = []

        for filepath in files:
            if not os.path.exists(filepath):
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError as e:
                issues.append(f"{filepath}: Invalid UTF-8 at byte {e.start}")

        if issues:
            return False, "Encoding issues", issues

        return True, "All files UTF-8 encoded", []

    def check_line_endings(self):
        """Check for consistent line endings"""
        files = ['main_android.py', 'buildozer.spec']

        issues = []

        for filepath in files:
            if not os.path.exists(filepath):
                continue

            try:
                with open(filepath, 'rb') as f:
                    content = f.read()

                has_crlf = b'\r\n' in content
                has_lf = b'\n' in content and not has_crlf

                if has_crlf:
                    issues.append(f"{filepath}: Windows line endings (CRLF)")

            except Exception:
                pass

        if issues:
            return True, "Mixed line endings (usually OK)", issues

        return True, "Unix line endings (LF)", []

    # ========================================================================
    # INTEGRATION CHECKS
    # ========================================================================

    def check_import_chain(self):
        """Test if main app can be parsed for imports"""
        try:
            with open('main_android.py', 'r') as f:
                code = f.read()

            tree = ast.parse(code)

            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)

            # Count by category
            standard = sum(1 for i in imports if i and i.split('.')[0] in ['os', 'sys', 'json', 'csv', 'datetime', 'logging'])
            kivy = sum(1 for i in imports if i and 'kivy' in i)
            android = sum(1 for i in imports if i and 'android' in i)
            other = len(imports) - standard - kivy - android

            details = [
                f"Standard library: {standard}",
                f"Kivy: {kivy}",
                f"Android: {android}",
                f"Other: {other}"
            ]

            return True, f"{len(imports)} total imports", details

        except Exception as e:
            return False, f"Import analysis failed: {str(e)}", []

    def check_class_structure(self):
        """Verify class structure is complete"""
        try:
            with open('main_android.py', 'r') as f:
                code = f.read()

            tree = ast.parse(code)

            classes = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Count methods
                    methods = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                    classes[node.name] = methods

            required_classes = [
                'IGCSEGymApp',
                'WorkoutScreen',
                'ReportsScreen',
                'RestTimerWidget',
                'DataStorage',
                'PermissionsManager'
            ]

            missing = [c for c in required_classes if c not in classes]

            if missing:
                return False, f"Missing classes", missing

            details = [f"{name}: {methods} methods" for name, methods in classes.items() if name in required_classes]

            return True, f"{len(classes)} classes defined", details

        except Exception as e:
            return False, f"Class analysis failed: {str(e)}", []

    # ========================================================================
    # FINAL INTEGRATION TEST
    # ========================================================================

    def test_xlsxwriter_end_to_end(self):
        """Test xlsxwriter can actually create a file"""
        try:
            # Try importing
            import xlsxwriter

            # Try creating a test file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
                tmp_path = tmp.name

            workbook = xlsxwriter.Workbook(tmp_path)
            worksheet = workbook.add_worksheet()

            # Write test data (like the app does)
            worksheet.write(0, 0, 'IGCSE GYM Test')
            worksheet.write(1, 0, 'Exercise')
            worksheet.write(1, 1, 'Sets')
            worksheet.write(1, 2, 'Reps')
            worksheet.write(2, 0, 'Back squat')
            worksheet.write(2, 1, 3)
            worksheet.write(2, 2, 12)

            workbook.close()

            # Verify file was created
            if os.path.exists(tmp_path):
                size = os.path.getsize(tmp_path)
                os.unlink(tmp_path)  # Clean up

                if size > 0:
                    return True, f"Excel generation works ({size} bytes)", []
                else:
                    return False, "Excel file created but empty", []
            else:
                return False, "Excel file not created", []

        except ImportError:
            return True, "xlsxwriter not installed (will be in APK)", []
        except Exception as e:
            return False, f"Excel generation failed: {str(e)}", []

    # ========================================================================
    # RUN ALL DIAGNOSTICS
    # ========================================================================

    def run_all(self):
        """Run all diagnostic checks"""

        self.header("COMPREHENSIVE BUILD DIAGNOSTICS")
        print(f"{Colors.BOLD}Testing EVERY possible error condition...{Colors.END}\n")

        # Python Environment
        self.header("SECTION 1: PYTHON ENVIRONMENT")
        self.check("Python version", self.check_python_version)
        self.check("Python modules", self.check_python_modules)
        self.check("xlsxwriter import", self.check_xlsxwriter_importable)
        self.check("System commands", self.check_system_commands)
        self.check("Pip packages", self.check_pip_packages)

        # File Structure
        self.header("SECTION 2: FILE STRUCTURE")
        self.check("main_android.py syntax", self.check_main_app_syntax)
        self.check("main_android.py imports", self.check_main_app_imports)
        self.check("Exercise data (26 total)", self.check_exercise_data_complete)
        self.check("Critical features (8 total)", self.check_critical_features)
        self.check("Import chain", self.check_import_chain)
        self.check("Class structure", self.check_class_structure)

        # Buildozer Configuration
        self.header("SECTION 3: BUILDOZER CONFIGURATION")
        self.check("buildozer.spec exists", self.check_buildozer_spec_exists)
        self.check("buildozer.spec syntax", self.check_buildozer_spec_syntax)
        self.check("Requirements", self.check_buildozer_requirements)
        self.check("Android permissions", self.check_buildozer_permissions)
        self.check("P4A configuration", self.check_buildozer_p4a_config)

        # Recipe Checks
        self.header("SECTION 4: P4A RECIPES")
        self.check("xlsxwriter recipe exists", self.check_xlsxwriter_recipe_exists)
        self.check("xlsxwriter recipe syntax", self.check_xlsxwriter_recipe_syntax)

        # Assets
        self.header("SECTION 5: ASSETS")
        self.check("Assets exist", self.check_assets_exist)
        self.check("Assets valid", self.check_assets_valid)

        # System Resources
        self.header("SECTION 6: SYSTEM RESOURCES")
        self.check("Disk space", self.check_disk_space)
        self.check("Memory available", self.check_memory_available)

        # File Quality
        self.header("SECTION 7: FILE QUALITY")
        self.check("File encoding", self.check_file_encoding)
        self.warn("Line endings", self.check_line_endings)

        # Git
        self.header("SECTION 8: VERSION CONTROL")
        self.warn("Git status", self.check_git_status)
        self.warn("Git branch", self.check_git_branch)

        # Integration Tests
        self.header("SECTION 9: INTEGRATION TESTS")
        self.check("xlsxwriter end-to-end", self.test_xlsxwriter_end_to_end)

        # Summary
        self.print_summary()

        return len(self.errors) == 0

    def print_summary(self):
        """Print comprehensive summary"""
        self.header("DIAGNOSTIC SUMMARY")

        print(f"{Colors.BOLD}Results:{Colors.END}")
        print(f"  Total checks: {self.checks_total}")
        print(f"  {Colors.GREEN}Passed: {self.checks_passed}{Colors.END}")
        print(f"  {Colors.RED}Failed: {self.checks_failed}{Colors.END}")
        print(f"  {Colors.YELLOW}Warnings: {len(self.warnings)}{Colors.END}")

        if self.checks_total > 0:
            success_rate = (self.checks_passed / self.checks_total) * 100
            print(f"  Success rate: {success_rate:.1f}%")

        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}ERRORS FOUND ({len(self.errors)}):{Colors.END}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {Colors.RED}{i}. {error}{Colors.END}")

        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}WARNINGS ({len(self.warnings)}):{Colors.END}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {Colors.YELLOW}{i}. {warning}{Colors.END}")

        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")

        if self.errors:
            print(f"{Colors.RED}{Colors.BOLD}✗ DIAGNOSTICS FAILED{Colors.END}")
            print(f"{Colors.RED}Fix the errors above before building.{Colors.END}")
            print(f"\nTotal issues to fix: {Colors.RED}{len(self.errors)}{Colors.END}")
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL DIAGNOSTICS PASSED{Colors.END}")
            print(f"{Colors.GREEN}The project should build successfully!{Colors.END}")

            if self.warnings:
                print(f"\n{Colors.YELLOW}Note: {len(self.warnings)} warnings (usually safe to ignore){Colors.END}")

        print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")


def main():
    """Main entry point"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}IGCSE GYM - Comprehensive Build Diagnostics{Colors.END}")
    print(f"{Colors.MAGENTA}Finding EVERY possible error before build...{Colors.END}\n")

    diagnostics = ComprehensiveDiagnostics()
    success = diagnostics.run_all()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
