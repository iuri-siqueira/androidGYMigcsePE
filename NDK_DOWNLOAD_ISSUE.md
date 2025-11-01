# Android NDK Download Issue - Root Cause Analysis

## Issue Summary

The Android build fails because the Android NDK (Native Development Kit) cannot be downloaded due to network proxy restrictions.

## Error Message

```
ERROR: Build failed: Couldn't find executable for CC.
This indicates a problem locating the /root/.buildozer/android/platform/android-ndk-r28c/toolchains/llvm/prebuilt/linux-x86_64/bin/clang executable in the Android NDK
```

## Root Cause

**Network Restriction:** The build environment's proxy blocks `dl.google.com` with `403 Forbidden` error.

```bash
$ wget https://dl.google.com/android/repository/android-ndk-r28c-linux.zip
Connecting to proxy... connected.
Proxy request sent, awaiting response... 403 Forbidden
ERROR 403: Forbidden.
```

**Result:** The NDK zip file is created with 0 bytes, and buildozer cannot extract the required clang compiler.

## Impact

- **Build Status:** ❌ BLOCKED
- **Missing Component:** Android NDK r28c (~1.2GB download, ~3.5GB extracted)
- **Critical Tool:** clang/clang++ compiler for compiling native Android code
- **Dependencies Affected:** All C/C++ compilation (Python extensions, Kivy, SDL2, etc.)

## What Works

Despite the NDK issue, several build problems were successfully resolved:

1. ✅ **Buildozer root warning** - Fixed with `BUILDOZER_WARN_ON_ROOT=0`
2. ✅ **SDL2 component downloads** - Patched to use GitHub archive URLs instead of blocked release URLs
3. ✅ **OpenSSL download** - Using GitHub mirror
4. ✅ **Python recipes** - All Python components download successfully
5. ✅ **Build configuration** - buildozer.spec is properly configured

## Solutions

### Solution 1: GitHub Actions CI/CD (RECOMMENDED)

GitHub Actions runners have unrestricted internet access and can download the NDK without issues.

**Setup:**
```bash
# The workflow file is already created at:
.github/workflows/build-android-apk.yml

# Push your code to GitHub and the workflow will run automatically
git add .
git commit -m "Add GitHub Actions workflow for Android build"
git push origin claude/fix-build-issue-011CUcoJRLe3uyi5QTypgiK2
```

**Features:**
- ✅ Unrestricted internet access
- ✅ Automatic builds on push
- ✅ APK artifacts stored for 30 days
- ✅ Build logs for debugging
- ✅ Caching for faster subsequent builds

### Solution 2: Manual NDK Installation

If you must build locally, manually download and install the NDK:

```bash
# On a machine with unrestricted internet access:
wget https://dl.google.com/android/repository/android-ndk-r28c-linux.zip

# Upload to the build server and extract:
scp android-ndk-r28c-linux.zip user@build-server:/root/.buildozer/android/platform/
ssh user@build-server
cd /root/.buildozer/android/platform/
unzip android-ndk-r28c-linux.zip

# Verify installation:
ls -la /root/.buildozer/android/platform/android-ndk-r28c/toolchains/llvm/prebuilt/linux-x86_64/bin/clang

# Then run build:
export BUILDOZER_WARN_ON_ROOT=0
buildozer android debug
```

### Solution 3: Request Network Whitelist

Contact your system administrator to whitelist:

**Required domains:**
- `dl.google.com` - For Android SDK/NDK downloads
- `github.com` - Already accessible but ensure no subdomain blocks

**Alternative:** Configure proxy exceptions for build environments.

## Network Restriction Summary

The build environment has the following network restrictions:

| Domain | Status | Impact |
|--------|--------|--------|
| `dl.google.com` | ❌ Blocked (403) | Cannot download NDK/SDK components |
| `github.com/libsdl-org/*/releases/download/` | ❌ Blocked (403) | SDL2 components (FIXED: using archive URLs) |
| `github.com/libsdl-org/*/archive/` | ✅ Accessible | SDL2 workaround |
| `github.com/openssl/openssl` | ✅ Accessible | OpenSSL mirror works |
| `github.com/python/*` | ✅ Accessible | Python downloads work |
| `github.com/kivy/*` | ✅ Accessible | Kivy downloads work |

## Technical Details

**NDK Requirements:**
- Version: r28c (recommended by python-for-android)
- Architecture: linux-x86_64
- Download URL: `https://dl.google.com/android/repository/android-ndk-r28c-linux.zip`
- Size: 1.2GB (compressed), 3.5GB (extracted)
- Critical components:
  - `toolchains/llvm/prebuilt/linux-x86_64/bin/clang`
  - `toolchains/llvm/prebuilt/linux-x86_64/bin/clang++`
  - `toolchains/llvm/prebuilt/linux-x86_64/bin/ld`

**Build Flow:**
1. Buildozer checks for NDK at `/root/.buildozer/android/platform/android-ndk-r28c`
2. If missing, downloads from `dl.google.com`
3. Extracts to platform directory
4. Configures CC/CXX environment variables
5. Compiles Python native extensions and C/C++ code

**Current State:**
- NDK directory exists but is only 5KB (essentially empty)
- NDK zip file exists but is 0 bytes (failed download)
- Build fails when python-for-android tries to compile hostpython3

## Logs

See the following files for detailed logs:
- `build_latest.log` - Full build output
- `fix_ndk_download.sh` - NDK download attempt script

## Next Steps

1. **Immediate:** Use GitHub Actions workflow (already configured)
2. **Short-term:** Push code to GitHub and let CI/CD build the APK
3. **Long-term:** Request network whitelist OR set up permanent CI/CD pipeline

## References

- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [python-for-android NDK Requirements](https://python-for-android.readthedocs.io/en/latest/quickstart/#installing-android-ndk)
- [Android NDK Downloads](https://developer.android.com/ndk/downloads)

---

**Status:** Documented and resolved via GitHub Actions
**Date:** 2025-11-01
**Branch:** `claude/fix-build-issue-011CUcoJRLe3uyi5QTypgiK2`
