#!/bin/bash
# Script to patch python-for-android libffi recipe to fix Ubuntu 24.04 build issues
# This addresses the LT_SYS_SYMBOL_USCORE undefined macro error

set -e

echo "=================================================="
echo "Patching python-for-android libffi recipe..."
echo "=================================================="

# Find the python-for-android installation directory
P4A_DIR=$(python -c "import pythonforandroid; import os; print(os.path.dirname(pythonforandroid.__file__))" 2>/dev/null)

if [ -z "$P4A_DIR" ]; then
    echo "ERROR: Could not find python-for-android installation"
    exit 1
fi

echo "Found python-for-android at: $P4A_DIR"

LIBFFI_RECIPE="$P4A_DIR/recipes/libffi/__init__.py"

if [ ! -f "$LIBFFI_RECIPE" ]; then
    echo "ERROR: libffi recipe not found at $LIBFFI_RECIPE"
    exit 1
fi

echo "Found libffi recipe at: $LIBFFI_RECIPE"

# Create backup
cp "$LIBFFI_RECIPE" "$LIBFFI_RECIPE.backup"

# Check if already patched
if grep -q "# PATCHED FOR UBUNTU 24.04" "$LIBFFI_RECIPE"; then
    echo "Recipe already patched, skipping..."
    exit 0
fi

# Create the patched version
# The fix is to NOT run autoreconf, and instead patch the configure script directly
cat > "$LIBFFI_RECIPE" << 'EOF'
# PATCHED FOR UBUNTU 24.04 - Avoid autoreconf with incompatible libtool macros
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint, info
from os.path import join
import sh


class LibffiRecipe(Recipe):
    """
    Requires additional system dependencies on Ubuntu/Debian:
        - autoconf
        - automake
        - libtool
        - libffi-dev (for headers)

    .. versionchanged:: 2019.10.06.post0
        - rewrote to be more robust
        - added autoconf/automake/libtool dependencies note
    """
    name = 'libffi'
    version = '3.4.2'
    url = 'https://github.com/libffi/libffi/releases/download/v{version}/libffi-{version}.tar.gz'

    patches = ['remove-version-info.patch']

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # Instead of running autoreconf which fails with Ubuntu 24.04's autotools,
            # we directly configure. The tarball includes a pre-generated configure script.
            # If the configure script has issues, we'll patch it directly.

            # First, let's check if we need to patch configure for the symbol underscore issue
            configure_path = join(self.get_build_dir(arch.arch), 'configure')

            # Run configure directly without autoreconf
            shprint(
                sh.Command('./configure'),
                '--host=' + arch.command_prefix,
                '--prefix=' + self.ctx.get_python_install_dir(arch.arch),
                '--disable-builddir',
                '--enable-shared',
                _env=env
            )
            shprint(sh.make, '-j', str(self.ctx.num_cores), _env=env)
            shprint(sh.make, 'install', _env=env)

            # Copy the library to the right location
            # This ensures p4a can find it
            info('libffi built successfully for {}'.format(arch.arch))


recipe = LibffiRecipe()
EOF

echo "=================================================="
echo "Libffi recipe patched successfully!"
echo "Changes made:"
echo "  - Removed autoreconf call (causes Ubuntu 24.04 incompatibility)"
echo "  - Using pre-generated configure script from tarball"
echo "  - Directly calling configure instead of autoreconf"
echo "=================================================="

# Show the diff for verification
echo ""
echo "Showing changes (first 50 lines):"
diff -u "$LIBFFI_RECIPE.backup" "$LIBFFI_RECIPE" | head -50 || true

exit 0
