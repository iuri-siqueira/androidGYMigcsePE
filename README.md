# IGCSE GYM - Enterprise Edition v2.0.0

**Professional Fitness Tracking Application for Android**

A comprehensive, enterprise-grade workout tracking application with advanced features including Excel report generation, data backup/recovery, performance monitoring, and real-time analytics.

## Features

### Core Workout Features
- **Multiple Workout Sessions**: Two main strength training sessions with different exercise sets
- **Comprehensive Warmup System**: Three warmup routines (Dynamic Mobility, Stability Training, Movement Integration)
- **Exercise Database**: 26 pre-configured exercises with sets, reps, and descriptions
- **Real-time Logging**: Track weight and reps for each exercise
- **Rest Timer**: Built-in countdown timer with customizable intervals (30s, 60s, 75s, 90s, 120s)

### Enterprise Features
- **Excel/CSV Reports**: Generate formatted Excel (.xlsx) or CSV reports with complete workout data
- **Automatic Backups**: Rolling backups with configurable retention (keeps last 10 backups)
- **Data Recovery**: Automatic crash recovery and data integrity validation
- **Performance Monitoring**: Track operation performance and success rates
- **Analytics Engine**: Advanced insights including:
  - Workout streaks and consistency tracking
  - Progress trends per exercise
  - Personalized recommendations
  - Summary statistics

### Data Management
- **Automatic Data Validation**: SHA-256 checksums for data integrity
- **Atomic File Operations**: Prevents data corruption during writes
- **Retry Mechanisms**: Exponential backoff for failed operations
- **Comprehensive Logging**: Rotating log files with configurable size limits
- **Export/Import**: Full data export for backup and transfer

### User Interface
- **Modern Design**: Custom purple theme with gradient buttons
- **Intuitive Navigation**: Easy switching between workout types
- **Real-time Feedback**: Instant confirmation popups
- **Responsive Layout**: Optimized for portrait mobile screens
- **Progress Tracking**: Visual indicators and statistics on home screen

## Installation

### Prerequisites
- Python 3.11+
- Android SDK (for building APK)
- Buildozer (for Android packaging)

### Building for Android

#### Quick Build
```bash
# Install dependencies
pip install -r requirements.txt

# Debug build
buildozer android debug

# Release build (for production)
buildozer android release
```

#### Clean Build
```bash
# Remove all cached data and rebuild
buildozer android clean
buildozer android debug
```

### Building with GitHub Actions
The project includes a comprehensive CI/CD workflow that:
- Validates code before building
- Optimizes disk space automatically
- Retries on failures with adaptive fixes
- Uploads APK artifacts
- Creates GitHub releases on tags

## Android Permissions

The app requests the following permissions:

- **INTERNET**: For future cloud sync features (currently unused)
- **MANAGE_EXTERNAL_STORAGE**: For saving reports to Downloads folder (Android 11+)
- **WRITE_EXTERNAL_STORAGE**: Legacy permission for older Android versions
- **READ_EXTERNAL_STORAGE**: Legacy permission for older Android versions

**Note**: If storage permissions are denied, reports will be saved to the app's internal storage directory instead.

## Project Structure

```
androidGYMigcsePE/
├── main_android.py          # Main application code (2100+ lines)
├── buildozer.spec           # Android build configuration
├── requirements.txt         # Python dependencies
├── assets/                  # App resources
│   ├── icon.png            # App icon (512x512)
│   └── presplash.png       # Splash screen (800x600)
├── java/                    # Java permission handlers
│   └── com/fitness/gymtracker/
│       └── PermissionHelper.java
├── gym_data/                # Data storage (created at runtime)
│   ├── exercises.json
│   ├── sessions.json
│   ├── weights.json
│   ├── reports.json
│   ├── backups/            # Automatic backups
│   └── app.log             # Application logs
├── .github/workflows/       # CI/CD configuration
│   └── build.yml
└── bin/                     # Built APK files
```

## Configuration

### buildozer.spec
Key configuration options:

```ini
[app]
title = IGCSE GYM
package.name = gymtracker
package.domain = com.fitness.gymtracker
version = 2.0.0

# Python packages to include
requirements = python3,kivy==2.3.0,xlsxwriter,android

# Android settings
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

# Use develop branch for latest fixes
p4a.branch = develop
```

## Exercise Database

### Session 1 (8 exercises)
- Back squat (3x12)
- Bridge (3x15)
- Bench press (3x10)
- Bench superman (3x12)
- Bentover Row (3x12)
- Pallof Twist (3x10)
- Shoulder press (3x10)
- Knee Tucks (3x15)

### Session 2 (6 exercises)
- Plank (3x45s)
- Incline Bench Press (3x10)
- Pallof Press (3x12)
- Lat Pull Downs (3x12)
- Landmines (3x10)
- Upright row (3x12)

### Warmup Routines

**Dynamic Mobility**: Arm Circles, Leg Swings, Torso Twists, High Knees
**Stability Training**: Single Leg Balance, Bird Dog, Wall Sits, Glute Bridges
**Movement Integration**: Bodyweight Squats, Push-up to Downward Dog, Lunge with Rotation, Cat-Cow Stretch

## Data Storage

### Storage Hierarchy (Android)
1. **Primary**: External Downloads folder (requires MANAGE_EXTERNAL_STORAGE)
2. **Fallback**: App external storage directory
3. **Last Resort**: App internal storage

All data is stored in JSON format with automatic backups and integrity checks.

## Reports

The app generates comprehensive Excel (.xlsx) or CSV reports including:

### Report Sections
1. **Exercise Database**: Complete list with sets, reps, descriptions
2. **Workout Sessions**: All logged workouts with dates, weights, reps
3. **Warmup Completion Log**: Tracking of warmup sessions
4. **Summary Statistics**: Total sessions, exercises, workout days

### Report Features
- **Formatted Excel** (when xlsxwriter is available): Headers, colors, auto-sizing
- **CSV Fallback**: Compatible with Excel, Google Sheets, LibreOffice
- **Automatic Timestamping**: Each report has unique timestamp
- **SHA-256 Checksums**: For data verification

## Troubleshooting

### Build Issues

**Problem**: "possibly undefined macro: LT_SYS_SYMBOL_USCORE"
```bash
# Install missing packages
sudo apt-get install -y libtool-bin libltdl-dev texinfo autoconf automake

# Set environment variables
export ACLOCAL_PATH=/usr/share/aclocal
export PKG_CONFIG_PATH=/usr/lib/pkgconfig:/usr/share/pkgconfig
```

**Problem**: "Out of memory" during build
```bash
# Reduce Gradle workers
export GRADLE_OPTS="$GRADLE_OPTS -Dorg.gradle.workers.max=2"

# Clear ccache
ccache -C
```

**Problem**: "No space left on device"
```bash
# Clean Docker
sudo docker system prune -af

# Clean buildozer cache
rm -rf ~/.buildozer/android/build
rm -rf .buildozer/android/app
```

### Runtime Issues

**Problem**: Reports not saving to Downloads
- **Cause**: Storage permission denied on Android 11+
- **Solution**: App automatically falls back to internal storage
- **Alternative**: Grant storage permission in Android Settings > Apps > IGCSE GYM > Permissions

**Problem**: Data loss after crash
- **Solution**: App automatically restores from most recent backup
- **Manual Recovery**: Check `gym_data/backups/` folder

## Development

### Running Tests
```bash
# Syntax check
python3 -m py_compile main_android.py

# Build environment validation
chmod +x test_build_env.sh
./test_build_env.sh
```

### Viewing Logs
```bash
# Application logs
cat gym_data/app.log

# Buildozer logs
cat .buildozer/logs/buildozer.log

# Python-for-android logs
cat .buildozer/android/platform/build-*/logs/*
```

## Technical Details

### Architecture
- **Design Pattern**: Repository pattern for data management
- **Error Handling**: Comprehensive try-catch with logging
- **Performance**: Monitored operations with metrics tracking
- **Data Integrity**: Checksums and atomic file operations

### Performance Features
- **Retry Mechanisms**: Exponential backoff for failed operations
- **Operation Monitoring**: Track duration and success rates
- **Memory Management**: Limited in-memory metrics (last 1000 operations)
- **Efficient Storage**: JSON with compression-ready format

### Security Notes
- **Data Encoding**: Base64 encoding (NOT encryption)
- **Permissions**: Minimal required permissions
- **Data Privacy**: All data stored locally on device
- **No Cloud**: No data sent to external servers

## Version History

### v2.0.0 - Enterprise Edition (Current)
- ✅ Excel/CSV report generation with formatting
- ✅ Automatic backup and recovery system
- ✅ Performance monitoring and analytics
- ✅ Advanced insights and recommendations
- ✅ Data integrity validation
- ✅ Comprehensive error handling
- ✅ Audit logging with rotation
- ✅ Android 13+ storage compatibility
- ✅ Runtime permission handling
- ✅ Multi-fallback storage paths

### v1.0.0 - Initial Release
- Basic workout tracking
- Simple data storage
- Manual session logging

## Credits

**Developer**: Iuri Siqueira
**License**: See LICENSE file
**Framework**: Kivy (Python mobile framework)
**Build System**: Buildozer + python-for-android

## Support

For issues, feature requests, or questions:
1. Check the troubleshooting section above
2. Review `BUILD_FIXES.md` for detailed build documentation
3. Check build environment with `./test_build_env.sh`
4. Review application logs in `gym_data/app.log`

## Future Enhancements

Potential features for future releases:
- [ ] Cloud synchronization
- [ ] Social sharing
- [ ] Custom exercise creation
- [ ] Video exercise demonstrations
- [ ] Workout program templates
- [ ] Multi-user support
- [ ] Wearable device integration
- [ ] Nutrition tracking
- [ ] Progress photos
- [ ] Advanced analytics dashboard

---

**Built with ❤️ for fitness enthusiasts**
**Enterprise-Grade • Open Source • Privacy-First**
