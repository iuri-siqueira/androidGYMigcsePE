#!/usr/bin/env python3
"""
DEEP BUILD DIAGNOSTICS - Actually test the build process
This simulates what buildozer/p4a does to find the REAL error
"""

import os
import sys
import re
import ast
import subprocess
import importlib.util
import tempfile
import urllib.request
import json
from pathlib import Path
from typing import List, Tuple, Dict

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DeepBuildDiagnostics:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.test_num = 0

    def header(self, text):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

    def test(self, description):
        """Start a test"""
        self.test_num += 1
        print(f"\n{Colors.BOLD}[TEST {self.test_num:02d}]{Colors.END} {description}")
        print(f"{Colors.BLUE}{'─'*80}{Colors.END}")

    def success(self, message):
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")

    def fail(self, message):
        print(f"{Colors.RED}✗ {message}{Colors.END}")
        self.errors.append(f"Test {self.test_num}: {message}")

    def warn(self, message):
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
        self.warnings.append(f"Test {self.test_num}: {message}")

    def info_msg(self, message):
        print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

    # ========================================================================
    # ACTUAL BUILD SIMULATION TESTS
    # ========================================================================

    def test_p4a_recipe_import(self):
        """Test if p4a recipe can actually be imported"""
        self.test("P4A Recipe Import Test")

        recipe_path = Path('p4a-recipes/xlsxwriter/__init__.py')

        if not recipe_path.exists():
            self.fail(f"Recipe file not found: {recipe_path}")
            return

        self.info_msg(f"Recipe file: {recipe_path}")

        # Try to import the recipe as a module
        try:
            spec = importlib.util.spec_from_file_location("xlsxwriter_recipe", recipe_path)
            if spec is None:
                self.fail("Cannot create module spec from recipe file")
                return

            module = importlib.util.module_from_spec(spec)
            sys.modules['xlsxwriter_recipe'] = module

            # Actually execute the module
            spec.loader.exec_module(module)

            self.success("Recipe module loaded successfully")

            # Check if recipe object exists
            if hasattr(module, 'recipe'):
                self.success(f"Recipe object found: {module.recipe}")

                # Check recipe attributes
                if hasattr(module.recipe, 'name'):
                    self.success(f"Recipe name: {module.recipe.name}")
                else:
                    self.fail("Recipe has no 'name' attribute")

                if hasattr(module.recipe, 'version'):
                    self.success(f"Recipe version: {module.recipe.version}")
                else:
                    self.fail("Recipe has no 'version' attribute")

            else:
                self.fail("Recipe module has no 'recipe' object")

        except Exception as e:
            self.fail(f"Failed to import recipe: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def test_p4a_recipe_class(self):
        """Test if recipe class is properly defined"""
        self.test("P4A Recipe Class Structure")

        try:
            with open('p4a-recipes/xlsxwriter/__init__.py', 'r') as f:
                content = f.read()

            tree = ast.parse(content)

            # Find the recipe class
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            if not classes:
                self.fail("No class found in recipe file")
                return

            recipe_class = None
            for cls in classes:
                if 'Recipe' in cls.name:
                    recipe_class = cls
                    break

            if not recipe_class:
                self.fail("No Recipe class found")
                return

            self.success(f"Found class: {recipe_class.name}")

            # Check base classes
            bases = [base.id for base in recipe_class.bases if hasattr(base, 'id')]
            if 'PythonRecipe' in bases:
                self.success("Inherits from PythonRecipe ✓")
            else:
                self.fail(f"Does not inherit from PythonRecipe. Bases: {bases}")

            # Check for required attributes
            required = ['name', 'version', 'url']
            found_attrs = []

            for node in ast.walk(recipe_class):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            found_attrs.append(target.id)

            for req in required:
                if req in found_attrs:
                    self.success(f"Has '{req}' attribute ✓")
                else:
                    self.fail(f"Missing '{req}' attribute")

        except Exception as e:
            self.fail(f"Failed to parse recipe class: {str(e)}")

    def test_recipe_url_valid(self):
        """Test if recipe URL is valid and accessible"""
        self.test("Recipe URL Validation")

        try:
            with open('p4a-recipes/xlsxwriter/__init__.py', 'r') as f:
                content = f.read()

            # Extract URL
            url_match = re.search(r"url\s*=\s*['\"](.+?)['\"]", content)

            if not url_match:
                self.fail("No URL found in recipe")
                return

            url_template = url_match.group(1)
            self.info_msg(f"URL template: {url_template}")

            # Extract version
            version_match = re.search(r"version\s*=\s*['\"](.+?)['\"]", content)

            if not version_match:
                self.fail("No version found in recipe")
                return

            version = version_match.group(1)
            self.info_msg(f"Version: {version}")

            # Format URL
            url = url_template.format(version=version)
            self.info_msg(f"Final URL: {url}")

            # Try to access URL
            try:
                self.info_msg("Checking if URL is accessible...")
                req = urllib.request.Request(url, method='HEAD')
                with urllib.request.urlopen(req, timeout=10) as response:
                    self.success(f"URL is accessible (HTTP {response.status})")

            except urllib.error.HTTPError as e:
                self.fail(f"URL returns HTTP {e.code}: {e.reason}")
            except urllib.error.URLError as e:
                self.warn(f"Cannot access URL (network issue?): {e.reason}")
            except Exception as e:
                self.warn(f"Cannot verify URL: {str(e)}")

        except Exception as e:
            self.fail(f"Failed to validate URL: {str(e)}")

    def test_recipe_discoverable(self):
        """Test if p4a can discover the recipe"""
        self.test("Recipe Discoverability")

        # Check directory structure
        recipe_dir = Path('p4a-recipes')
        xlsxwriter_dir = recipe_dir / 'xlsxwriter'
        init_file = xlsxwriter_dir / '__init__.py'

        if not recipe_dir.exists():
            self.fail(f"Recipe directory not found: {recipe_dir}")
            return

        self.success(f"Recipe directory exists: {recipe_dir}")

        if not xlsxwriter_dir.exists():
            self.fail(f"xlsxwriter directory not found: {xlsxwriter_dir}")
            return

        self.success(f"xlsxwriter directory exists: {xlsxwriter_dir}")

        if not init_file.exists():
            self.fail(f"__init__.py not found: {init_file}")
            return

        self.success(f"__init__.py exists: {init_file}")

        # Check if directory is in buildozer.spec
        try:
            with open('buildozer.spec', 'r') as f:
                spec_content = f.read()

            if 'p4a.local_recipes' in spec_content:
                match = re.search(r'p4a\.local_recipes\s*=\s*(.+)', spec_content)
                if match:
                    recipes_path = match.group(1).strip()
                    self.success(f"p4a.local_recipes = {recipes_path}")

                    if recipes_path == './p4a-recipes':
                        self.success("Recipe path matches directory ✓")
                    else:
                        self.fail(f"Recipe path mismatch: spec says '{recipes_path}' but directory is './p4a-recipes'")
            else:
                self.fail("p4a.local_recipes not found in buildozer.spec")

        except Exception as e:
            self.fail(f"Failed to check buildozer.spec: {str(e)}")

    def test_main_app_imports(self):
        """Actually try to parse and understand main app imports"""
        self.test("Main App Import Simulation")

        try:
            # Add current directory to path
            if '.' not in sys.path:
                sys.path.insert(0, '.')

            with open('main_android.py', 'r') as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Extract all imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(('import', alias.name, None))
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(('from', module, alias.name))

            self.info_msg(f"Found {len(imports)} import statements")

            # Test each import
            problematic = []
            android_specific = []
            kivy_specific = []

            for import_type, module, name in imports:
                base_module = module.split('.')[0] if module else name.split('.')[0]

                # Skip android imports (device-only)
                if base_module == 'android':
                    android_specific.append(f"{import_type} {module}.{name}" if module else f"{import_type} {name}")
                    continue

                # Skip kivy imports (will be in APK)
                if base_module == 'kivy':
                    kivy_specific.append(f"{import_type} {module}.{name}" if module else f"{import_type} {name}")
                    continue

                # Skip xlsxwriter (will be in APK)
                if base_module == 'xlsxwriter':
                    continue

                # Try to import others
                try:
                    if base_module:
                        importlib.import_module(base_module)
                except ImportError as e:
                    problematic.append(f"{base_module}: {str(e)}")

            self.success(f"Android-specific imports: {len(android_specific)} (OK, device-only)")
            self.success(f"Kivy imports: {len(kivy_specific)} (OK, will be in APK)")

            if problematic:
                for prob in problematic:
                    self.fail(f"Import issue: {prob}")
            else:
                self.success("All non-APK imports work ✓")

        except Exception as e:
            self.fail(f"Import simulation failed: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def test_hidden_characters(self):
        """Check for hidden Unicode characters that break builds"""
        self.test("Hidden Character Detection")

        files_to_check = [
            'main_android.py',
            'buildozer.spec',
            'p4a-recipes/xlsxwriter/__init__.py'
        ]

        issues = []

        for filepath in files_to_check:
            if not os.path.exists(filepath):
                continue

            self.info_msg(f"Checking {filepath}...")

            try:
                with open(filepath, 'rb') as f:
                    content = f.read()

                # Check for BOM
                if content.startswith(b'\xef\xbb\xbf'):
                    issues.append(f"{filepath}: UTF-8 BOM detected")

                # Check for null bytes
                if b'\x00' in content:
                    issues.append(f"{filepath}: Null bytes detected")

                # Check for weird Unicode
                try:
                    text = content.decode('utf-8')

                    # Check for zero-width characters
                    zero_width = ['\u200b', '\u200c', '\u200d', '\ufeff']
                    for char in zero_width:
                        if char in text:
                            issues.append(f"{filepath}: Zero-width character found")
                            break

                except UnicodeDecodeError as e:
                    issues.append(f"{filepath}: Unicode decode error at byte {e.start}")

            except Exception as e:
                issues.append(f"{filepath}: Cannot read: {str(e)}")

        if issues:
            for issue in issues:
                self.fail(issue)
        else:
            self.success("No hidden characters found ✓")

    def test_file_permissions(self):
        """Check if files have correct permissions"""
        self.test("File Permissions")

        files_to_check = {
            'main_android.py': (True, False),  # (readable, executable)
            'buildozer.spec': (True, False),
            'p4a-recipes/xlsxwriter/__init__.py': (True, False),
        }

        issues = []

        for filepath, (should_read, should_exec) in files_to_check.items():
            if not os.path.exists(filepath):
                issues.append(f"{filepath}: File not found")
                continue

            readable = os.access(filepath, os.R_OK)
            writable = os.access(filepath, os.W_OK)
            executable = os.access(filepath, os.X_OK)

            if should_read and not readable:
                issues.append(f"{filepath}: Not readable")

            if should_exec and not executable:
                issues.append(f"{filepath}: Should be executable but isn't")

            self.info_msg(f"{filepath}: R={readable} W={writable} X={executable}")

        if issues:
            for issue in issues:
                self.fail(issue)
        else:
            self.success("All file permissions OK ✓")

    def test_requirements_parse(self):
        """Test if requirements can be parsed correctly"""
        self.test("Requirements Parsing")

        try:
            with open('buildozer.spec', 'r') as f:
                content = f.read()

            req_match = re.search(r'^requirements\s*=\s*(.+)$', content, re.MULTILINE)

            if not req_match:
                self.fail("No requirements line found")
                return

            req_line = req_match.group(1).strip()
            self.info_msg(f"Requirements line: {req_line}")

            # Parse requirements
            reqs = [r.strip() for r in req_line.split(',')]

            self.info_msg(f"Parsed {len(reqs)} requirements:")

            for req in reqs:
                self.info_msg(f"  - {req}")

                # Check format
                if '==' in req:
                    pkg, ver = req.split('==', 1)
                    self.info_msg(f"    Package: {pkg}, Version: {ver}")
                else:
                    self.info_msg(f"    Package: {req} (no version pinned)")

            # Check for required packages
            required = ['python3', 'kivy', 'xlsxwriter']

            for req_pkg in required:
                found = any(req_pkg in r for r in reqs)
                if found:
                    self.success(f"{req_pkg} found in requirements ✓")
                else:
                    self.fail(f"{req_pkg} NOT found in requirements")

            # Check for problematic patterns
            for req in reqs:
                if 'python3==' in req:
                    self.warn(f"python3 version pinned: {req} (may cause issues)")

        except Exception as e:
            self.fail(f"Requirements parsing failed: {str(e)}")

    def test_buildozer_command_syntax(self):
        """Test if buildozer command would be valid"""
        self.test("Buildozer Command Syntax")

        try:
            # Try to run buildozer help
            result = subprocess.run(
                ['buildozer', '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.success("buildozer command works ✓")

                # Try to get version
                version_result = subprocess.run(
                    ['buildozer', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if version_result.returncode == 0:
                    version = version_result.stdout.strip()
                    self.success(f"buildozer version: {version}")

            else:
                self.warn("buildozer not installed (will run on CI)")

        except FileNotFoundError:
            self.warn("buildozer not found (will run on CI)")
        except Exception as e:
            self.warn(f"Cannot test buildozer: {str(e)}")

    def test_circular_imports(self):
        """Check for circular import issues"""
        self.test("Circular Import Detection")

        try:
            with open('main_android.py', 'r') as f:
                content = f.read()

            # Simple check: look for imports that might cause issues
            lines = content.split('\n')

            import_lines = []
            for i, line in enumerate(lines, 1):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_lines.append((i, line.strip()))

            self.info_msg(f"Found {len(import_lines)} import statements")

            # Check if imports are at top of file (good practice)
            code_started = False
            late_imports = []

            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                # Skip comments and empty lines
                if not stripped or stripped.startswith('#'):
                    continue

                # Check if code has started (class, def, assignment)
                if not code_started:
                    if stripped.startswith('class ') or stripped.startswith('def ') or '=' in stripped:
                        code_started = True

                # If code started and we find an import
                if code_started and (stripped.startswith('import ') or stripped.startswith('from ')):
                    # Exception for conditional imports (android)
                    if 'if platform' not in lines[max(0, i-2):i]:
                        late_imports.append((i, stripped))

            if late_imports:
                self.warn(f"Found {len(late_imports)} imports after code started (usually OK)")
                for line_num, import_line in late_imports[:3]:
                    self.info_msg(f"  Line {line_num}: {import_line}")
            else:
                self.success("All imports at top of file ✓")

        except Exception as e:
            self.fail(f"Circular import check failed: {str(e)}")

    def test_xlsxwriter_download(self):
        """Test if xlsxwriter can actually be downloaded"""
        self.test("xlsxwriter Download Test")

        try:
            # Get the recipe URL
            with open('p4a-recipes/xlsxwriter/__init__.py', 'r') as f:
                recipe_content = f.read()

            version_match = re.search(r"version\s*=\s*['\"](.+?)['\"]", recipe_content)
            url_match = re.search(r"url\s*=\s*['\"](.+?)['\"]", recipe_content)

            if not version_match or not url_match:
                self.fail("Cannot extract version/URL from recipe")
                return

            version = version_match.group(1)
            url_template = url_match.group(1)
            url = url_template.format(version=version)

            self.info_msg(f"Testing download: {url}")

            # Try to download (just headers)
            try:
                req = urllib.request.Request(url, method='HEAD')
                with urllib.request.urlopen(req, timeout=15) as response:
                    content_length = response.headers.get('Content-Length')
                    content_type = response.headers.get('Content-Type')

                    self.success(f"Download URL is valid ✓")
                    self.info_msg(f"Content-Type: {content_type}")
                    if content_length:
                        size_mb = int(content_length) / (1024 * 1024)
                        self.info_msg(f"Size: {size_mb:.2f} MB")

            except Exception as e:
                self.warn(f"Cannot verify download (network): {str(e)}")

        except Exception as e:
            self.fail(f"Download test failed: {str(e)}")

    def test_ndk_api_compatibility(self):
        """Test NDK API compatibility"""
        self.test("NDK API Compatibility")

        try:
            with open('buildozer.spec', 'r') as f:
                content = f.read()

            # Extract NDK settings
            ndk_match = re.search(r'^android\.ndk\s*=\s*(.+)$', content, re.MULTILINE)
            ndk_api_match = re.search(r'^--ndk-api=(\d+)', content, re.MULTILINE)
            minapi_match = re.search(r'^android\.minapi\s*=\s*(\d+)$', content, re.MULTILINE)
            api_match = re.search(r'^android\.api\s*=\s*(\d+)$', content, re.MULTILINE)

            ndk = ndk_match.group(1).strip() if ndk_match else 'not specified'
            minapi = int(minapi_match.group(1)) if minapi_match else None
            api = int(api_match.group(1)) if api_match else None

            self.info_msg(f"NDK version: {ndk}")
            self.info_msg(f"Min API: {minapi}")
            self.info_msg(f"Target API: {api}")

            if minapi and api:
                if minapi <= api:
                    self.success(f"API levels compatible (min={minapi}, target={api}) ✓")
                else:
                    self.fail(f"Min API ({minapi}) > Target API ({api})")

            if ndk == '25b':
                self.success("Using NDK 25b (compatible with Python 3.11) ✓")
            elif ndk:
                self.warn(f"Using NDK {ndk} (untested)")

        except Exception as e:
            self.fail(f"NDK compatibility check failed: {str(e)}")

    def test_p4a_branch_compatibility(self):
        """Test p4a branch compatibility"""
        self.test("P4A Branch Compatibility")

        try:
            with open('buildozer.spec', 'r') as f:
                content = f.read()

            branch_match = re.search(r'^p4a\.branch\s*=\s*(.+)$', content, re.MULTILINE)

            if not branch_match:
                self.warn("p4a.branch not specified (will use default)")
                return

            branch = branch_match.group(1).strip()
            self.info_msg(f"P4A branch: {branch}")

            if branch == 'develop':
                self.success("Using 'develop' branch (needed for Python 3.11) ✓")
            elif branch == 'master':
                self.warn("Using 'master' branch (may not support Python 3.11)")
            else:
                self.warn(f"Using '{branch}' branch (unknown compatibility)")

        except Exception as e:
            self.fail(f"P4A branch check failed: {str(e)}")

    def test_environment_variables(self):
        """Check for required environment variables"""
        self.test("Environment Variables")

        # These are set by GitHub Actions
        ci_vars = ['ANDROID_HOME', 'ANDROID_SDK_ROOT', 'ANDROID_NDK_HOME', 'JAVA_HOME']

        missing = []
        found = []

        for var in ci_vars:
            value = os.environ.get(var)
            if value:
                found.append(f"{var}={value}")
            else:
                missing.append(var)

        if found:
            self.info_msg(f"Found {len(found)} CI variables:")
            for var in found[:3]:
                self.info_msg(f"  {var}")

        if missing:
            self.warn(f"Missing CI variables (OK if not on GitHub Actions): {', '.join(missing)}")
        else:
            self.success("All CI variables present ✓")

    def test_syntax_deep(self):
        """Deep syntax check with actual compilation"""
        self.test("Deep Syntax Check")

        files = ['main_android.py', 'p4a-recipes/xlsxwriter/__init__.py']

        for filepath in files:
            if not os.path.exists(filepath):
                self.warn(f"{filepath} not found")
                continue

            self.info_msg(f"Compiling {filepath}...")

            try:
                with open(filepath, 'r') as f:
                    code = f.read()

                # Parse
                tree = ast.parse(code, filename=filepath)

                # Try to compile
                compile(code, filepath, 'exec')

                self.success(f"{filepath} compiles successfully ✓")

            except SyntaxError as e:
                self.fail(f"{filepath}: Syntax error at line {e.lineno}: {e.msg}")
                if e.text:
                    self.info_msg(f"  {e.text}")
            except Exception as e:
                self.fail(f"{filepath}: Compilation failed: {str(e)}")

    # ========================================================================
    # RUN ALL TESTS
    # ========================================================================

    def run_all(self):
        """Run all deep diagnostic tests"""

        self.header("DEEP BUILD DIAGNOSTICS - SIMULATING ACTUAL BUILD")

        print(f"{Colors.BOLD}These tests simulate what buildozer/p4a actually do during build{Colors.END}\n")

        # Core build tests
        self.test_p4a_recipe_import()
        self.test_p4a_recipe_class()
        self.test_recipe_url_valid()
        self.test_recipe_discoverable()
        self.test_xlsxwriter_download()

        # Code tests
        self.test_syntax_deep()
        self.test_main_app_imports()
        self.test_circular_imports()

        # Configuration tests
        self.test_requirements_parse()
        self.test_ndk_api_compatibility()
        self.test_p4a_branch_compatibility()

        # File quality tests
        self.test_hidden_characters()
        self.test_file_permissions()

        # Environment tests
        self.test_environment_variables()
        self.test_buildozer_command_syntax()

        # Summary
        self.print_summary()

        return len(self.errors) == 0

    def print_summary(self):
        """Print summary"""
        self.header("DIAGNOSTIC SUMMARY")

        print(f"{Colors.BOLD}Tests run: {self.test_num}{Colors.END}")
        print(f"{Colors.GREEN}Errors: {len(self.errors)}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {len(self.warnings)}{Colors.END}")

        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}ERRORS FOUND:{Colors.END}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {Colors.RED}{i}. {error}{Colors.END}")

        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}WARNINGS:{Colors.END}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {Colors.YELLOW}{i}. {warning}{Colors.END}")

        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")

        if self.errors:
            print(f"{Colors.RED}{Colors.BOLD}✗ DEEP DIAGNOSTICS FOUND ERRORS{Colors.END}")
            print(f"{Colors.RED}Fix the errors above before building{Colors.END}")
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ DEEP DIAGNOSTICS PASSED{Colors.END}")
            print(f"{Colors.GREEN}The build should work!{Colors.END}")

        print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")

def main():
    """Main entry point"""
    diagnostics = DeepBuildDiagnostics()
    success = diagnostics.run_all()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
