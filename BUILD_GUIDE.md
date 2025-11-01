# IGCSE GYM - Complete Build Guide

## Overview

This guide provides comprehensive instructions for building the IGCSE GYM Android application using Buildozer.

## Quick Start

### Prerequisites

- Ubuntu 20.04+ (or similar Linux distribution)
- Python 3.11.6
- Java JDK 17
- At least 10GB free disk space
- At least 4GB RAM

### One-Command Build

```bash
# Verify environment first
chmod +x verify_build_environment.sh
./verify_build_environment.sh

# Build the APK
buildozer android debug
```

## Detailed Build Instructions

### 1. Environment Setup

#### Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    unzip \
    zip \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo6 \
    cmake \
    libffi-dev \
    libssl-dev \
    libsqlite3-dev \
    python3-setuptools \
    python3-wheel
```

#### Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Configuration

The build is configured through `buildozer.spec`:

**Key Settings:**
- **Python Version:** 3.11.6 (stable, well-tested)
- **Kivy Version:** 2.3.0 (latest stable)
- **NDK Version:** 25b (recommended for Kivy 2.3.0)
- **SDK API:** 33 (Android 13)
- **Min API:** 21 (Android 5.0)
- **P4A Release:** 2023.12.11 (stable, NOT develop branch)

### 3. Building

#### First Build (slower, downloads dependencies)

```bash
buildozer -v android debug
```

The first build will:
- Download Android SDK (~1GB)
- Download Android NDK (~1GB)
- Download Python-for-Android
- Compile all dependencies
- Create the APK

**Expected time:** 30-60 minutes

#### Subsequent Builds (faster)

```bash
buildozer android debug
```

**Expected time:** 5-10 minutes

### 4. Build Output

Successful builds create:
- `bin/gymtracker-2.0.0-arm64-v8a_armeabi-v7a-debug.apk`

## Troubleshooting

### Common Issues and Solutions

#### 1. "Command failed" Error

**Symptom:** Build fails with "Buildozer failed to execute the last command"

**Solutions:**
1. Check full build log in `.buildozer/android/platform/build-*/build.log`
2. Clean build directory: `buildozer android clean`
3. Remove cached dependencies: `rm -rf ~/.buildozer`
4. Run with verbose logging: `buildozer -v android debug`

#### 2. NDK Download Failures

**Symptom:** Cannot download Android NDK

**Solutions:**
1. Check internet connection
2. Verify proxy settings if behind corporate firewall
3. Pre-download NDK manually to `~/.buildozer/android/platform/`

#### 3. Out of Memory Errors

**Symptom:** Build fails with memory-related errors

**Solutions:**
1. Close other applications
2. Increase swap space
3. Use single architecture: modify `android.archs = arm64-v8a` in buildozer.spec

#### 4. Gradle Build Failures

**Symptom:** Gradle compilation errors

**Solutions:**
1. Verify Java version: `java -version` (should be 17)
2. Set JAVA_HOME: `export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64`
3. Clean Gradle cache: `rm -rf ~/.gradle`

#### 5. Permission Denied Errors

**Symptom:** Cannot write to buildozer directories

**Solutions:**
1. Check directory permissions
2. Don't run buildozer as root
3. Set: `export BUILDOZER_WARN_ON_ROOT=0`

### Build Environment Verification

Always verify your environment before building:

```bash
./verify_build_environment.sh
```

This checks:
- All required commands are installed
- Python packages are available
- Environment variables are set
- Required files exist
- Sufficient disk space

### Clean Build

If you encounter persistent issues:

```bash
# Clean local build files
buildozer android clean

# Clean everything (including downloads)
rm -rf .buildozer
rm -rf ~/.buildozer
rm -rf bin

# Start fresh
buildozer android debug
```

## GitHub Actions CI/CD

The project includes automated builds via GitHub Actions.

**Workflow Features:**
- Automatic builds on push to main/develop branches
- Caching of SDK/NDK for faster builds
- Retry logic for network failures
- Comprehensive build logs
- APK artifact upload
- Build status summaries

**Triggering a Build:**
1. Push to `main`, `develop`, or any `claude/**` branch
2. Create a pull request
3. Manually trigger via Actions tab

**Accessing Build Artifacts:**
1. Go to Actions tab
2. Click on the workflow run
3. Download APK from Artifacts section

## Build Optimization

### Speed Improvements

1. **Use ccache:**
   ```bash
   sudo apt-get install ccache
   export USE_CCACHE=1
   ```

2. **Single Architecture:**
   ```
   android.archs = arm64-v8a
   ```

3. **Parallel Builds:**
   ```
   export GRADLE_OPTS="-Dorg.gradle.parallel=true"
   ```

### Size Optimization

1. **Remove unused architectures**
2. **Use ProGuard for release builds**
3. **Optimize assets (compress images)**

## Version Information

- **App Version:** 2.0.0
- **Package Name:** com.fitness.gymtracker
- **Minimum Android:** 5.0 (API 21)
- **Target Android:** 13 (API 33)

## Build Configuration Details

### buildozer.spec Key Sections

```ini
[app]
# Application metadata
title = IGCSE GYM
package.name = gymtracker
package.domain = com.fitness.gymtracker
version = 2.0.0

# Python requirements (stable versions)
requirements = python3==3.11.6,kivy==2.3.0,xlsxwriter==3.1.9,android,pyjnius

# Android settings
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a,armeabi-v7a

# P4A configuration (STABLE RELEASE)
p4a.release = 2023.12.11
p4a.bootstrap = sdl2
```

## Support

### Getting Help

1. **Check build logs:**
   ```bash
   cat .buildozer/android/platform/build-*/build.log | tail -n 100
   ```

2. **Run environment verification:**
   ```bash
   ./verify_build_environment.sh
   ```

3. **Enable verbose output:**
   ```bash
   buildozer -v android debug
   ```

### Reporting Issues

When reporting build issues, include:
1. Output of `./verify_build_environment.sh`
2. Last 100 lines of build log
3. `buildozer.spec` configuration
4. System information (OS, Python version, etc.)

## Performance Benchmarks

**Typical Build Times:**
- First build: 30-60 minutes
- Clean build: 10-15 minutes
- Incremental build: 2-5 minutes

**Disk Space Usage:**
- Source code: ~500 MB
- Build artifacts: ~2-3 GB
- Cache: ~1-2 GB
- **Total:** ~4-6 GB

## Security Notes

### Permissions

The app requests these permissions:
- `INTERNET` - For future cloud sync features
- `MANAGE_EXTERNAL_STORAGE` - For saving workout reports
- `WRITE_EXTERNAL_STORAGE` - For file access
- `READ_EXTERNAL_STORAGE` - For file access

### Build Security

- All dependencies use pinned versions
- No external binary downloads during build
- Source code is verified via git
- Build process is reproducible

## Release Build (Production)

For production releases:

```bash
# Build release APK
buildozer android release

# Sign the APK (requires keystore)
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
    -keystore my-release-key.keystore \
    bin/gymtracker-2.0.0-arm64-v8a_armeabi-v7a-release-unsigned.apk \
    alias_name

# Align the APK
zipalign -v 4 \
    bin/gymtracker-2.0.0-arm64-v8a_armeabi-v7a-release-unsigned.apk \
    bin/gymtracker-2.0.0-release.apk
```

## Continuous Integration

The GitHub Actions workflow provides:
- ✅ Automated testing
- ✅ Build verification
- ✅ APK artifact generation
- ✅ Build caching for speed
- ✅ Retry logic for reliability
- ✅ Comprehensive logging

**Workflow triggers:**
- Push to main/develop
- Pull requests
- Manual dispatch

## Additional Resources

- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Python-for-Android](https://python-for-android.readthedocs.io/)
- [Android Developer Guide](https://developer.android.com/)

---

**Last Updated:** 2025-11-01
**Build System Version:** Buildozer 1.5.0
**Target Platform:** Android 5.0+ (API 21+)
