# Android Build Fixes Documentation

## Overview
This document describes the fixes applied to resolve the Android build issues, particularly the libffi autoconf/libtool compatibility problems on Ubuntu 24.04.

## Issues Identified

### 1. **LibFFI Autoconf/Libtool Macro Error**
**Error Message:**
```
configure.ac:215: error: possibly undefined macro: LT_SYS_SYMBOL_USCORE
autoreconf: error: /usr/bin/autoconf failed with exit status: 1
```

**Root Cause:**
- Ubuntu 24.04 ships with newer versions of autotools (autoconf 2.71+, automake 1.16+, libtool 2.4.7+)
- The libffi recipe in older versions of python-for-android had compatibility issues with these newer autotools
- Missing libtool m4 macros during the autoreconf process

**Solution:**
1. Added `libtool-bin` and `texinfo` packages to system dependencies
2. Updated python-for-android to use the `develop` branch which has fixes for newer autotools
3. Set `ACLOCAL_PATH` environment variable to ensure libtool macros are found
4. Updated buildozer.spec to use `p4a.branch = develop`

### 2. **NDK Version Compatibility**
**Issue:**
- Multiple NDK versions present in the system
- Environment variables pointing to different NDK versions

**Solution:**
- Standardized on NDK 25b (compatible with the current setup)
- Ensured buildozer.spec uses `android.ndk = 25b`
- Workflow explicitly sets `NDK_VERSION = '25b'`

### 3. **Build Dependencies**
**Missing Packages:**
- `libtool-bin` - Provides additional libtool support files
- `texinfo` - Required for generating documentation during autotools build
- Proper `autoconf`, `automake`, `libtool` versions

**Solution:**
Added all required packages to the GitHub Actions workflow.

## Changes Made

### 1. `.github/workflows/build.yml`

#### System Dependencies Update
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get install -y --no-install-recommends \
      autoconf automake libtool libtool-bin pkg-config texinfo \
      # ... other packages
```

#### Python Dependencies Update
```yaml
- name: Install Python dependencies
  run: |
    python -m pip install --user \
      git+https://github.com/kivy/python-for-android.git@develop \
      # ... other packages
```

#### Build Environment Variables
```bash
export ACLOCAL_PATH=/usr/share/aclocal
export PKG_CONFIG_PATH=/usr/lib/pkgconfig:/usr/share/pkgconfig
```

#### Added Validation Step
```yaml
- name: Validate build environment
  run: |
    chmod +x test_build_env.sh
    ./test_build_env.sh || echo "Validation completed with warnings"
```

### 2. `buildozer.spec`

```ini
p4a.branch = develop  # Changed from 'master'
```

### 3. `test_build_env.sh`

Created comprehensive validation script that checks:
- System commands (python, java, gcc, autotools, etc.)
- Python packages (buildozer, cython, p4a, kivy, etc.)
- Android environment variables
- Project files
- System libraries
- Autotools configuration
- Disk space and memory

## Testing

### Running the Validation Script Locally
```bash
chmod +x test_build_env.sh
./test_build_env.sh
```

The script will:
- Check all required tools and dependencies
- Validate Python packages
- Verify autotools installation
- Check for libtool m4 macros
- Validate project configuration
- Report any issues with color-coded output

### Building Locally
```bash
# Clean build
buildozer android clean

# Debug build
buildozer android debug

# Release build
buildozer android release
```

### Testing in GitHub Actions
The workflow now includes:
1. **Validation step** - Runs before build to catch issues early
2. **Retry logic** - Attempts build up to 3 times with adaptive fixes
3. **Comprehensive logging** - Captures full build logs
4. **Artifact uploads** - Saves APK and logs

## Common Issues and Solutions

### Issue: "possibly undefined macro: LT_SYS_SYMBOL_USCORE"
**Solution:**
1. Ensure `libtool-bin` is installed: `sudo apt-get install libtool-bin`
2. Verify libtool m4 macros exist: `ls /usr/share/aclocal/libtool*.m4`
3. Set ACLOCAL_PATH: `export ACLOCAL_PATH=/usr/share/aclocal`
4. Use python-for-android develop branch

### Issue: "autoreconf: command not found"
**Solution:**
```bash
sudo apt-get install autoconf automake libtool
```

### Issue: NDK version mismatch
**Solution:**
1. Check `buildozer.spec`: `android.ndk = 25b`
2. Clean buildozer cache: `rm -rf ~/.buildozer/android/platform/android-ndk*`
3. Let buildozer download the correct NDK version

### Issue: Out of memory during build
**Solution:**
1. Reduce Gradle workers: `export GRADLE_OPTS="$GRADLE_OPTS -Dorg.gradle.workers.max=2"`
2. Clear ccache: `ccache -C`
3. Increase swap space

### Issue: Disk space issues
**Solution:**
```bash
# Clean Docker
sudo docker system prune -af

# Clean buildozer cache
rm -rf ~/.buildozer/android/build
rm -rf .buildozer/android/app

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
```

## Verification Steps

After applying fixes, verify:

1. **Autotools are working:**
   ```bash
   autoconf --version
   automake --version
   libtoolize --version
   ```

2. **Libtool m4 macros are present:**
   ```bash
   ls -la /usr/share/aclocal/libtool*.m4
   ```

3. **Python-for-android is correct version:**
   ```bash
   p4a --version
   ```

4. **Buildozer configuration is correct:**
   ```bash
   grep -E "(p4a.branch|android.ndk)" buildozer.spec
   ```

5. **Run validation script:**
   ```bash
   ./test_build_env.sh
   ```

## References

- [Python-for-Android Documentation](https://python-for-android.readthedocs.io/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Python-for-Android GitHub Issues](https://github.com/kivy/python-for-android/issues)

## Troubleshooting

### Enable Debug Logging
Add to `buildozer.spec`:
```ini
[buildozer]
log_level = 2
```

### Manual Build with p4a
```bash
p4a create --dist_name=gymtracker \
           --bootstrap=sdl2 \
           --requirements=python3,kivy,xlsxwriter \
           --arch=arm64-v8a \
           --debug
```

### Check Build Logs
```bash
# View full buildozer log
cat .buildozer/logs/buildozer.log

# View p4a log
cat .buildozer/android/platform/build-*/logs/*
```

## Future Improvements

1. **Pin specific python-for-android commit** - For reproducible builds
2. **Add unit tests** - Test app functionality before building
3. **Optimize build time** - Use persistent cache more effectively
4. **Multi-architecture testing** - Test on different Android versions
5. **Automated APK testing** - Use Android emulator for automated testing

## Maintenance

### Keeping Dependencies Updated
```bash
# Update python-for-android
pip install --upgrade git+https://github.com/kivy/python-for-android.git@develop

# Update buildozer
pip install --upgrade buildozer

# Update Kivy
pip install --upgrade kivy
```

### Monitoring for Issues
- Watch python-for-android repository for breaking changes
- Test builds regularly with scheduled GitHub Actions runs
- Keep autotools packages updated in CI environment

---

**Last Updated:** 2025-10-30
**Status:** Active fixes for libffi autoconf compatibility issue
**Target Platform:** Android (arm64-v8a, armeabi-v7a)
**Build Environment:** Ubuntu 24.04 with Python 3.11
