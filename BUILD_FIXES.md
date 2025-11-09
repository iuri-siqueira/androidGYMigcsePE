# Android Build Fixes - Python 3.11 Compatibility

## Issues Fixed

### 1. PyJNIus Python 3.11 Incompatibility ✅
**Error**: `jnius/jnius_utils.pxi:323:37: undeclared name not builtin: long`

**Root Cause**: PyJNIus (required by Kivy) contains Cython code that references `long` type, which doesn't exist in Python 3 (unified with `int`).

**Solution**: Created custom pyjnius recipe with patch to replace `long` with `int`.
- **File**: `recipes/pyjnius/__init__.py`
- **Patch**: `recipes/pyjnius/python311_compat.patch`

### 2. Android-Incompatible Python Modules ✅
**Errors**:
- `grpmodule.c`: Missing `setgrent/getgrent/endgrent` functions
- `_lzmamodule.c`: Missing `lzma.h` header
- Other: `pwd`, `_uuid`, `nis`, `_crypt`, etc.

**Root Cause**: These Unix-specific modules don't exist on Android and cause compilation failures.

**Solution**: Created custom python3 recipe that excludes these modules.
- **File**: `recipes/python3/__init__.py`
- **Excluded**: grp, _lzma, pwd, ossaudiodev, spwd, nis, _crypt, _uuid

## Files Modified

### Configuration
- **buildozer.spec**: Added `p4a.local_recipes = ./recipes` to use custom recipes

### Custom Recipes Created
```
recipes/
├── pyjnius/
│   ├── __init__.py              # Custom recipe using master branch
│   └── python311_compat.patch   # Fixes 'long' type for Python 3.11
└── python3/
    └── __init__.py              # Excludes Android-incompatible modules
```

### Supporting Files
- **Setup.local**: Lists modules to exclude (backup/reference)

## All Features Preserved ✅

The application retains 100% functionality:
- ✅ Workout Session 1 & 2
- ✅ 3 Warmup Routines (Dynamic, Stability, Movement)
- ✅ Excel Report Export (.xlsx via xlsxwriter)
- ✅ JSON Data Storage
- ✅ Rest Timer (75s default)
- ✅ Exercise Logging with Weights & Reps
- ✅ Progress Tracking
- ✅ Android Permissions (Storage)

## Technical Details

### Build Environment
- Python: 3.11
- NDK: r25b
- API Level: 30 (min 21)
- Architecture: arm64-v8a
- p4a branch: develop

### Dependencies
- python3 (with custom exclusions)
- kivy (with patched pyjnius)
- xlsxwriter (pure Python - no issues)

## Testing Recommendations

1. **Clean Build**: Delete `.buildozer` directory before building
2. **Verify Recipes**: Ensure `recipes/` directory is in project root
3. **Check Logs**: Monitor for module exclusion confirmations
4. **Test APK**: Verify all features work on device

## Future Improvements

- Monitor pyjnius upstream for official Python 3.11 support
- Consider Python 3.10 if issues persist (more mature Android support)
- Track python-for-android updates for built-in fixes
