# PyJNIus Python 3.11 Compatibility Fix

## Problem
The build was failing with this error:
```
Error compiling Cython file:
jnius/jnius_utils.pxi:323:37: undeclared name not builtin: long
```

## Root Cause
- Python 3.11+ removed the `long` type (merged into `int`)
- PyJNIus versions < 1.7.0 still used `long` in Cython code
- This caused compilation failures when building for Android with Python 3.11

## Solution
Updated the custom PyJNIus recipe to use version **1.7.0** which includes:
- Native Python 3.11+ support
- Proper handling of `int` type (no more `long`)
- No patches required

## Changes Made

### 1. Updated `recipes/pyjnius/__init__.py`
- Changed from `version = 'master'` to `version = '1.7.0'`
- Removed patch dependency
- Updated URL to use `.tar.gz` format
- Added clear documentation

### 2. Removed `recipes/pyjnius/python311_compat.patch`
- No longer needed with PyJNIus 1.7.0+

## Build Configuration
The buildozer.spec properly references custom recipes:
```ini
p4a.local_recipes = ./recipes
```

## Why This Works
- PyJNIus 1.7.0 was released in September 2024
- It includes official Python 3.11 support
- All `long` references have been updated to `int`
- No manual patching required

## Testing
Build with: `buildozer android debug`

The build should now complete successfully without the "undeclared name not builtin: long" error.

## References
- PyPI: https://pypi.org/project/pyjnius/
- GitHub: https://github.com/kivy/pyjnius
- Release 1.7.0 includes Python 3.11 support
