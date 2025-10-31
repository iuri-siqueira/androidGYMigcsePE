"""
IGCSE GYM - Enterprise-Grade Fitness Tracking Application
========================================================
Complete workout management with advanced features:
- Excel/CSV report generation with formatting
- Data backup and recovery
- Performance monitoring and analytics
- Crash recovery
- Data integrity validation
- Enterprise-level error handling
- Audit logging
- Advanced insights and metrics

Version: 2.0.0 (Enterprise Edition)
"""

import os
import json
import base64
import csv
import logging
import shutil
import hashlib
import time
from functools import wraps
from collections import defaultdict
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
try:
    import xlsxwriter
    XLSX_AVAILABLE = True
except ImportError:
    XLSX_AVAILABLE = False
from datetime import datetime, timedelta
from kivy.utils import platform

# Configure logging
def setup_logging():
    """Setup application logging with rotating file handler"""
    logger = logging.getLogger("IGCSEGym")
    logger.setLevel(logging.INFO)

    try:
        from logging.handlers import RotatingFileHandler as RFH

        log_dir = "gym_data"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, "app.log")

        # Create rotating file handler with configurable sizes
        max_bytes = 5*1024*1024
        backup_count = 3
        file_handler = RFH(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # If file logging fails (permissions, etc.), continue without it
        print(f"Warning: File logging disabled: {e}")

    # Always add console handler as fallback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

# Initialize logger
logger = setup_logging()
logger.info("IGCSE GYM Application Starting - Enterprise Edition v2.0.0")

# ============================================================================
# ENTERPRISE-GRADE INFRASTRUCTURE
# ============================================================================

class OperationStatus(Enum):
    """Status codes for operations"""
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    PARTIAL = "partial"

@dataclass
class PerformanceMetrics:
    """Track performance metrics for monitoring"""
    operation_name: str
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    success: bool = False
    error: Optional[str] = None

    def duration_ms(self) -> float:
        """Calculate duration in milliseconds"""
        if self.end_time == 0:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

class PerformanceMonitor:
    """Enterprise-level performance monitoring"""

    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.operation_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)

    def record_metric(self, metric: PerformanceMetrics):
        """Record a performance metric"""
        self.metrics.append(metric)
        self.operation_counts[metric.operation_name] += 1
        if not metric.success and metric.error:
            self.error_counts[metric.error] += 1

        # Keep only last 1000 metrics to prevent memory issues
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]

    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.metrics:
            return {}

        recent_metrics = self.metrics[-100:]
        avg_duration = sum(m.duration_ms() for m in recent_metrics) / len(recent_metrics)
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics)

        return {
            'total_operations': len(self.metrics),
            'avg_duration_ms': round(avg_duration, 2),
            'success_rate': round(success_rate * 100, 2),
            'operation_counts': dict(self.operation_counts),
            'error_counts': dict(self.error_counts)
        }

# Global performance monitor
perf_monitor = PerformanceMonitor()

def monitored_operation(operation_name: str):
    """Decorator to monitor operation performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            metric = PerformanceMetrics(operation_name=operation_name)
            try:
                result = func(*args, **kwargs)
                metric.success = True
                return result
            except Exception as e:
                metric.success = False
                metric.error = str(e)
                logger.error(f"Operation {operation_name} failed: {e}")
                raise
            finally:
                metric.end_time = time.time()
                perf_monitor.record_metric(metric)
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 0.5):
    """Decorator to retry failed operations with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {wait_time}s: {e}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}: {e}")
            raise last_exception
        return wrapper
    return decorator

class DataIntegrityChecker:
    """Validate data integrity and detect corruption"""

    @staticmethod
    def validate_json_structure(data: Any, required_fields: List[str]) -> bool:
        """Validate JSON structure"""
        if not isinstance(data, (list, dict)):
            return False

        if isinstance(data, dict):
            return all(field in data for field in required_fields)

        return True

    @staticmethod
    def calculate_checksum(data: str) -> str:
        """Calculate SHA-256 checksum for data"""
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def verify_file_integrity(file_path: str, expected_checksum: Optional[str] = None) -> bool:
        """Verify file hasn't been corrupted"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            if expected_checksum:
                current_checksum = DataIntegrityChecker.calculate_checksum(content)
                return current_checksum == expected_checksum

            # Try to parse as JSON to verify it's valid
            json.loads(content)
            return True
        except Exception as e:
            logger.error(f"File integrity check failed for {file_path}: {e}")
            return False

class BackupManager:
    """Enterprise-level backup and recovery system"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.backup_dir = os.path.join(data_dir, "backups")
        self.max_backups = 10  # Keep last 10 backups

        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    @monitored_operation("backup_create")
    @retry_on_failure(max_retries=3)
    def create_backup(self, file_path: str) -> Optional[str]:
        """Create backup of a file"""
        try:
            if not os.path.exists(file_path):
                return None

            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{filename}.{timestamp}.backup"
            backup_path = os.path.join(self.backup_dir, backup_name)

            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup created: {backup_name}")

            # Cleanup old backups
            self._cleanup_old_backups(filename)

            return backup_path
        except Exception as e:
            logger.error(f"Backup creation failed for {file_path}: {e}")
            return None

    def _cleanup_old_backups(self, base_filename: str):
        """Remove old backups keeping only the most recent ones"""
        try:
            backups = [f for f in os.listdir(self.backup_dir)
                      if f.startswith(base_filename) and f.endswith('.backup')]

            backups.sort(reverse=True)  # Most recent first

            # Remove old backups
            for old_backup in backups[self.max_backups:]:
                backup_path = os.path.join(self.backup_dir, old_backup)
                os.remove(backup_path)
                logger.info(f"Removed old backup: {old_backup}")
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")

    @monitored_operation("backup_restore")
    def restore_from_backup(self, file_path: str) -> bool:
        """Restore file from most recent backup"""
        try:
            filename = os.path.basename(file_path)
            backups = [f for f in os.listdir(self.backup_dir)
                      if f.startswith(filename) and f.endswith('.backup')]

            if not backups:
                logger.warning(f"No backups found for {filename}")
                return False

            # Get most recent backup
            backups.sort(reverse=True)
            latest_backup = backups[0]
            backup_path = os.path.join(self.backup_dir, latest_backup)

            shutil.copy2(backup_path, file_path)
            logger.info(f"Restored from backup: {latest_backup}")
            return True
        except Exception as e:
            logger.error(f"Restore from backup failed for {file_path}: {e}")
            return False

    def list_backups(self) -> List[str]:
        """List all available backups"""
        try:
            return [f for f in os.listdir(self.backup_dir) if f.endswith('.backup')]
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []

class AnalyticsEngine:
    """Advanced analytics and insights"""

    @staticmethod
    def calculate_workout_streaks(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate workout streaks and consistency"""
        if not sessions:
            return {'current_streak': 0, 'longest_streak': 0, 'total_days': 0}

        # Sort sessions by date
        sorted_sessions = sorted(sessions, key=lambda x: x.get('date', ''))

        dates = set()
        for session in sorted_sessions:
            try:
                date_str = session.get('date', '')[:10]  # Get just the date part
                dates.add(date_str)
            except Exception:
                continue

        if not dates:
            return {'current_streak': 0, 'longest_streak': 0, 'total_days': 0}

        sorted_dates = sorted(dates)

        # Calculate streaks
        current_streak = 1
        longest_streak = 1
        temp_streak = 1

        for i in range(1, len(sorted_dates)):
            try:
                prev_date = datetime.fromisoformat(sorted_dates[i-1])
                curr_date = datetime.fromisoformat(sorted_dates[i])
                diff = (curr_date - prev_date).days

                if diff == 1:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 1
            except Exception:
                continue

        # Check if current streak is active
        try:
            last_date = datetime.fromisoformat(sorted_dates[-1])
            days_since = (datetime.now() - last_date).days
            current_streak = temp_streak if days_since <= 1 else 0
        except Exception:
            current_streak = 0

        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_workout_days': len(dates)
        }

    @staticmethod
    def calculate_progress_trends(weights: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """Calculate progression trends for exercises"""
        trends = {}

        # Group by exercise
        by_exercise = defaultdict(list)
        for weight_log in weights:
            ex_id = weight_log.get('exercise_id')
            if ex_id:
                by_exercise[ex_id].append(weight_log)

        # Calculate trends
        for ex_id, logs in by_exercise.items():
            sorted_logs = sorted(logs, key=lambda x: x.get('date', ''))

            if len(sorted_logs) < 2:
                trends[ex_id] = {'trend': 'insufficient_data', 'change': 0}
                continue

            weights_list = [log.get('weight', 0) for log in sorted_logs]

            # Calculate percentage change
            first_weight = weights_list[0]
            last_weight = weights_list[-1]

            if first_weight > 0:
                change_pct = ((last_weight - first_weight) / first_weight) * 100
            else:
                change_pct = 0

            # Determine trend
            if change_pct > 10:
                trend = 'improving'
            elif change_pct < -10:
                trend = 'declining'
            else:
                trend = 'stable'

            trends[ex_id] = {
                'trend': trend,
                'change_percent': round(change_pct, 2),
                'first_weight': first_weight,
                'latest_weight': last_weight,
                'total_sessions': len(sorted_logs)
            }

        return trends

    @staticmethod
    def get_insights(sessions: List[Dict[str, Any]], weights: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable insights from workout data"""
        insights = []

        # Workout frequency
        if sessions:
            days = len(set(s.get('date', '')[:10] for s in sessions if s.get('date')))
            if days >= 5:
                insights.append("🔥 Excellent consistency! You're working out 5+ days.")
            elif days >= 3:
                insights.append("💪 Good progress! Aim for 5+ workout days for optimal results.")
            else:
                insights.append("📈 Try to increase workout frequency to 3-5 days per week.")

        # Progress trends
        trends = AnalyticsEngine.calculate_progress_trends(weights)
        improving = sum(1 for t in trends.values() if t.get('trend') == 'improving')

        if improving > 0:
            insights.append(f"⬆️ You're making progress in {improving} exercises!")

        # Workout streaks
        streaks = AnalyticsEngine.calculate_workout_streaks(sessions)
        if streaks['current_streak'] >= 7:
            insights.append(f"🏆 Amazing! {streaks['current_streak']}-day workout streak!")
        elif streaks['longest_streak'] >= 7:
            insights.append(f"🎯 Your best streak was {streaks['longest_streak']} days. You can do it again!")

        return insights if insights else ["Start tracking your workouts to get personalized insights!"]

# Application Constants
class AppConstants:
    """Central configuration and constants for the application"""

    # Directory and file paths
    DATA_DIR = "gym_data"
    ASSETS_DIR = "assets"

    # Validation limits
    MAX_WEIGHT_KG = 1000
    MAX_REPS = 1000
    MIN_WEIGHT_KG = 0
    MIN_REPS = 0

    # Rest timer settings
    DEFAULT_REST_TIME_SECONDS = 75  # As specified in Excel sheet
    REST_TIMER_OPTIONS = [30, 60, 75, 90, 120]  # Quick select options

    # Session type identifiers
    SESSION_TYPE_1 = "session1"
    SESSION_TYPE_2 = "session2"
    WARMUP_DYNAMIC = "warmup-dynamic"
    WARMUP_STABILITY = "warmup-stability"
    WARMUP_MOVEMENT = "warmup-movement"

    # Exercise categories
    CATEGORY_WARMUP_DYNAMIC = "Warmup-Dynamic"
    CATEGORY_WARMUP_STABILITY = "Warmup-Stability"
    CATEGORY_WARMUP_MOVEMENT = "Warmup-Movement"

    # UI Colors (RGBA)
    COLOR_PRIMARY = (0.275, 0.0, 0.545, 1)  # Dark purple #46008b
    COLOR_PRIMARY_LIGHT = (0.4, 0.1, 0.7, 0.8)  # Lighter purple
    COLOR_PRIMARY_DARK = (0.2, 0.0, 0.4, 0.3)  # Darker purple
    COLOR_BACKGROUND = (0.2, 0.2, 0.2, 1)  # Dark gray
    COLOR_SUCCESS = (0.2, 0.7, 0.2, 1)  # Green
    COLOR_TEXT_PRIMARY = (1, 1, 1, 1)  # White
    COLOR_TEXT_SECONDARY = (0.8, 0.8, 0.8, 1)  # Light gray

    # Report settings
    REPORT_DAYS_RANGE = 30
    REPORT_TITLE = "IGCSE GYM - Workout Report"

    # Popup sizes
    POPUP_SMALL = (0.6, 0.4)
    POPUP_MEDIUM = (0.7, 0.4)
    POPUP_LARGE = (0.8, 0.5)

    # Logging
    LOG_FILE_MAX_BYTES = 5 * 1024 * 1024  # 5MB
    LOG_FILE_BACKUP_COUNT = 3

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.clock import Clock
from kivy.animation import Animation

class DataStorage:
    """
    Enterprise-Grade Data Storage with:
    - Automatic backups
    - Data integrity validation
    - Crash recovery
    - Performance monitoring
    - Retry mechanisms
    """

    def __init__(self, data_dir: Optional[str] = None) -> None:
        self.data_dir: str = data_dir if data_dir else AppConstants.DATA_DIR
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Data files
        self.exercises_file = os.path.join(self.data_dir, "exercises.json")
        self.sessions_file = os.path.join(self.data_dir, "sessions.json")
        self.weights_file = os.path.join(self.data_dir, "weights.json")
        self.reports_file = os.path.join(self.data_dir, "reports.json")
        self.metadata_file = os.path.join(self.data_dir, "metadata.json")

        # Enterprise features
        self.backup_manager = BackupManager(self.data_dir)
        self.integrity_checker = DataIntegrityChecker()

        # Initialize data
        self._init_data()
        self._verify_data_integrity()

    def _init_data(self):
        """Initialize data files with default exercise database"""
        if not os.path.exists(self.exercises_file):
            default_exercises = [
                # Session 1 exercises with sets x reps format (matching Excel sheet)
                {"id": 1, "name": "Back squat", "category": "Legs", "description": "Primary compound leg exercise", "sets": 3, "reps": 12},
                {"id": 2, "name": "Bridge", "category": "Glutes", "description": "Hip bridge for glute activation", "sets": 3, "reps": 15},
                {"id": 3, "name": "Bench press", "category": "Chest", "description": "Primary chest compound exercise", "sets": 3, "reps": 10},
                {"id": 4, "name": "Bench superman", "category": "Back", "description": "Core and back stability", "sets": 3, "reps": 12},
                {"id": 5, "name": "Bentover Row", "category": "Back", "description": "Upper back strength", "sets": 3, "reps": 12},
                {"id": 6, "name": "Pallof Twist", "category": "Core", "description": "Anti-rotation core exercise", "sets": 3, "reps": 10},
                {"id": 7, "name": "Shoulder press", "category": "Shoulders", "description": "Overhead pressing movement", "sets": 3, "reps": 10},
                {"id": 8, "name": "Knee Tucks", "category": "Core", "description": "Core strengthening", "sets": 3, "reps": 15},

                # Session 2 exercises with sets x reps format
                {"id": 9, "name": "Plank", "category": "Core", "description": "Isometric core exercise", "sets": 3, "reps": 45, "unit": "seconds"},
                {"id": 10, "name": "Incline Bench Press", "category": "Chest", "description": "Upper chest development", "sets": 3, "reps": 10},
                {"id": 11, "name": "Pallof Press", "category": "Core", "description": "Anti-extension core exercise", "sets": 3, "reps": 12},
                {"id": 12, "name": "Lat Pull Downs", "category": "Back", "description": "Latissimus dorsi development", "sets": 3, "reps": 12},
                {"id": 13, "name": "Landmines", "category": "Full Body", "description": "Functional movement pattern", "sets": 3, "reps": 10},
                {"id": 14, "name": "Upright row", "category": "Shoulders", "description": "Shoulder and trap development", "sets": 3, "reps": 12},

                # Warmup Tab 1 - Dynamic Mobility
                {"id": 15, "name": "Arm Circles", "category": "Warmup-Dynamic", "description": "Shoulder mobility", "reps": 10, "unit": "each direction"},
                {"id": 16, "name": "Leg Swings", "category": "Warmup-Dynamic", "description": "Hip mobility", "reps": 10, "unit": "each leg"},
                {"id": 17, "name": "Torso Twists", "category": "Warmup-Dynamic", "description": "Spine mobility", "reps": 10, "unit": "each side"},
                {"id": 18, "name": "High Knees", "category": "Warmup-Dynamic", "description": "Dynamic warm-up", "reps": 30, "unit": "seconds"},

                # Warmup Tab 2 - Stability Training
                {"id": 19, "name": "Single Leg Balance", "category": "Warmup-Stability", "description": "Balance training", "reps": 30, "unit": "seconds each leg"},
                {"id": 20, "name": "Bird Dog", "category": "Warmup-Stability", "description": "Core stability", "reps": 10, "unit": "each side"},
                {"id": 21, "name": "Wall Sits", "category": "Warmup-Stability", "description": "Isometric strength", "reps": 30, "unit": "seconds"},
                {"id": 22, "name": "Glute Bridges", "category": "Warmup-Stability", "description": "Glute activation", "reps": 15},

                # Warmup Tab 3 - Movement Integration
                {"id": 23, "name": "Bodyweight Squats", "category": "Warmup-Movement", "description": "Movement pattern", "reps": 10},
                {"id": 24, "name": "Push-up to Downward Dog", "category": "Warmup-Movement", "description": "Full body movement", "reps": 8},
                {"id": 25, "name": "Lunge with Rotation", "category": "Warmup-Movement", "description": "Multi-planar movement", "reps": 8, "unit": "each side"},
                {"id": 26, "name": "Cat-Cow Stretch", "category": "Warmup-Movement", "description": "Spinal mobility", "reps": 10}
            ]
            self._save_json(self.exercises_file, default_exercises)

        # Initialize empty files if they don't exist
        for file_path in [self.sessions_file, self.weights_file, self.reports_file]:
            if not os.path.exists(file_path):
                self._save_json(file_path, [])

    def _verify_data_integrity(self):
        """Verify integrity of all data files on startup"""
        files_to_check = [
            self.exercises_file,
            self.sessions_file,
            self.weights_file,
            self.reports_file
        ]

        for file_path in files_to_check:
            if os.path.exists(file_path):
                if not self.integrity_checker.verify_file_integrity(file_path):
                    logger.warning(f"Integrity check failed for {file_path}, attempting restore")
                    # Try to restore from backup
                    if self.backup_manager.restore_from_backup(file_path):
                        logger.info(f"Successfully restored {file_path} from backup")
                    else:
                        logger.error(f"Failed to restore {file_path}, data may be corrupted")

    @monitored_operation("load_json")
    @retry_on_failure(max_retries=3)
    def _load_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Load data from JSON file with retry and monitoring"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Validate structure
            if not isinstance(data, list):
                logger.warning(f"Invalid JSON structure in {file_path}, expected list")
                # Try to recover from backup
                if self.backup_manager.restore_from_backup(file_path):
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                else:
                    return []

            return data
        except (FileNotFoundError, json.JSONDecodeError, IOError, PermissionError) as e:
            logger.error(f"Error loading JSON from {file_path}: {e}")
            # Try to recover from backup
            if self.backup_manager.restore_from_backup(file_path):
                logger.info(f"Recovered {file_path} from backup after load failure")
                try:
                    with open(file_path, 'r') as f:
                        return json.load(f)
                except Exception:
                    pass
            return []

    @monitored_operation("save_json")
    @retry_on_failure(max_retries=3)
    def _save_json(self, file_path: str, data: List[Dict[str, Any]]) -> bool:
        """Save data to JSON file with backup and validation"""
        try:
            # Create backup before saving
            if os.path.exists(file_path):
                self.backup_manager.create_backup(file_path)

            # Validate data structure
            if not isinstance(data, list):
                logger.error(f"Invalid data structure for {file_path}, expected list")
                return False

            # Write to temporary file first (atomic write pattern)
            temp_file = f"{file_path}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            # Verify temp file integrity
            if not self.integrity_checker.verify_file_integrity(temp_file):
                logger.error(f"Integrity check failed for temporary file")
                os.remove(temp_file)
                return False

            # Move temp file to actual file (atomic operation)
            shutil.move(temp_file, file_path)

            logger.debug(f"Successfully saved {file_path}")
            return True
        except (IOError, PermissionError, OSError) as e:
            logger.error(f"Error saving JSON to {file_path}: {e}")
            # Clean up temp file if it exists
            temp_file = f"{file_path}.tmp"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            return False

    def get_exercises(self) -> List[Dict[str, Any]]:
        """Get all exercises"""
        return self._load_json(self.exercises_file)

    def add_exercise(self, name: str, category: str, description: str = "") -> bool:
        """Add new exercise"""
        exercises = self.get_exercises()
        new_id = max([ex.get('id', 0) for ex in exercises]) + 1 if exercises else 1
        exercise = {
            'id': new_id,
            'name': name,
            'category': category,
            'description': description
        }
        exercises.append(exercise)
        return self._save_json(self.exercises_file, exercises)

    def save_workout_session(self, session_name: str, exercises_completed: List[Dict[str, Any]]) -> bool:
        """Save workout session"""
        sessions = self._load_json(self.sessions_file)
        session = {
            'id': len(sessions) + 1,
            'name': session_name,
            'date': datetime.now().isoformat(),
            'exercises': exercises_completed
        }
        sessions.append(session)
        return self._save_json(self.sessions_file, sessions)

    def save_weight_log(self, exercise_id: int, weight: float, reps: int, notes: str = "") -> bool:
        """Save weight log entry"""
        weights = self._load_json(self.weights_file)
        weight_log = {
            'id': len(weights) + 1,
            'exercise_id': exercise_id,
            'weight': weight,
            'reps': reps,
            'date': datetime.now().isoformat(),
            'notes': notes
        }
        weights.append(weight_log)
        return self._save_json(self.weights_file, weights)

    def get_workout_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get workout history"""
        sessions = self._load_json(self.sessions_file)
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_sessions = []
        for session in sessions:
            try:
                session_date = datetime.fromisoformat(session['date'])
                if session_date >= cutoff_date:
                    recent_sessions.append(session)
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Error parsing session date: {e}")
                continue

        return sorted(recent_sessions, key=lambda x: x['date'], reverse=True)

    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly workout report"""
        sessions = self.get_workout_history(7)
        weights = self._load_json(self.weights_file)

        report = {
            'week_start': (datetime.now() - timedelta(days=7)).isoformat(),
            'week_end': datetime.now().isoformat(),
            'total_sessions': len(sessions),
            'total_exercises': sum(len(s.get('exercises', [])) for s in sessions),
            'sessions': sessions,
            'progress_summary': self._calculate_progress(weights)
        }

        reports = self._load_json(self.reports_file)
        reports.append(report)
        self._save_json(self.reports_file, reports)

        return report

    def _calculate_progress(self, weights: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """Calculate weight progression"""
        progress = {}
        for weight_log in weights[-50:]:  # Last 50 entries
            exercise_id = weight_log.get('exercise_id')
            if exercise_id not in progress:
                progress[exercise_id] = []
            progress[exercise_id].append({
                'weight': weight_log.get('weight', 0),
                'date': weight_log.get('date')
            })
        return progress

    @monitored_operation("export_all_data")
    def export_all_data(self) -> Dict[str, Any]:
        """Export all data for backup/transfer (Enterprise feature)"""
        try:
            return {
                'version': '2.0.0',
                'export_date': datetime.now().isoformat(),
                'exercises': self.get_exercises(),
                'sessions': self._load_json(self.sessions_file),
                'weights': self._load_json(self.weights_file),
                'reports': self._load_json(self.reports_file),
                'checksum': self.integrity_checker.calculate_checksum(
                    json.dumps({
                        'exercises': self.get_exercises(),
                        'sessions': self._load_json(self.sessions_file),
                        'weights': self._load_json(self.weights_file)
                    }, default=str)
                )
            }
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return {}

    @monitored_operation("import_data")
    def import_data(self, data: Dict[str, Any]) -> bool:
        """Import data from backup/transfer (Enterprise feature)"""
        try:
            # Validate import data
            required_keys = ['exercises', 'sessions', 'weights']
            if not all(key in data for key in required_keys):
                logger.error("Invalid import data structure")
                return False

            # Create backups before importing
            for file_path in [self.exercises_file, self.sessions_file, self.weights_file]:
                if os.path.exists(file_path):
                    self.backup_manager.create_backup(file_path)

            # Import data
            success = True
            success &= self._save_json(self.exercises_file, data['exercises'])
            success &= self._save_json(self.sessions_file, data['sessions'])
            success &= self._save_json(self.weights_file, data['weights'])

            if 'reports' in data:
                success &= self._save_json(self.reports_file, data['reports'])

            if success:
                logger.info("Data import successful")
            else:
                logger.error("Data import completed with errors")

            return success
        except Exception as e:
            logger.error(f"Failed to import data: {e}")
            return False

    def get_insights(self) -> List[str]:
        """Get AI-powered insights about workout progress (Enterprise feature)"""
        sessions = self.get_workout_history(30)
        weights = self._load_json(self.weights_file)
        return AnalyticsEngine.get_insights(sessions, weights)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get system performance statistics (Enterprise feature)"""
        return perf_monitor.get_stats()

    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status (Enterprise feature)"""
        return {
            'data_files_ok': all(
                self.integrity_checker.verify_file_integrity(f)
                for f in [self.exercises_file, self.sessions_file, self.weights_file]
                if os.path.exists(f)
            ),
            'backups_available': len(self.backup_manager.list_backups()),
            'total_exercises': len(self.get_exercises()),
            'total_sessions': len(self._load_json(self.sessions_file)),
            'total_weight_logs': len(self._load_json(self.weights_file)),
            'storage_path': self.data_dir,
            'performance': perf_monitor.get_stats()
        }

def simple_encode(text: str) -> str:
    """
    Simple base64 encoding for data obfuscation.
    WARNING: This is NOT encryption and does NOT provide security.
    Use only for basic data encoding, not for sensitive information.
    """
    if not text:
        return ""
    try:
        encoded = base64.b64encode(text.encode()).decode()
        return encoded
    except (ValueError, TypeError, UnicodeEncodeError) as e:
        logger.error(f"Error encoding data: {e}")
        return ""

def simple_decode(encoded_text: str) -> str:
    """
    Simple base64 decoding for data obfuscation.
    WARNING: This is NOT decryption and does NOT provide security.
    """
    if not encoded_text:
        return ""
    try:
        return base64.b64decode(encoded_text.encode()).decode()
    except (ValueError, TypeError, UnicodeDecodeError) as e:
        logger.error(f"Error decoding data: {e}")
        return ""

class StyledButton(Button):
    """Modern styled button with rounded corners and gradient effect"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Transparent
        self.color = (1, 1, 1, 1)
        self.font_size = '18sp'
        self.bold = True
        self.bind(size=self.update_graphics, pos=self.update_graphics)

    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Main gradient background with rounded corners - Dark Purple theme
            Color(*AppConstants.COLOR_PRIMARY)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15])

            # Highlight border with rounded corners
            Color(*AppConstants.COLOR_PRIMARY_LIGHT)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 15), width=2)

            # Inner shadow effect
            Color(*AppConstants.COLOR_PRIMARY_DARK)
            RoundedRectangle(pos=(self.x + 2, self.y + 2), size=(self.width - 4, self.height - 4), radius=[13])

class RestTimerWidget(Popup):
    """Rest timer between sets with visual countdown"""

    def __init__(self, rest_time=60, on_complete_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.title = 'REST TIMER'
        self.size_hint = (0.8, 0.6)
        self.auto_dismiss = False

        self.rest_time = rest_time
        self.current_time = rest_time
        self.on_complete_callback = on_complete_callback
        self.timer_event = None

        self.build_timer_interface()

    def build_timer_interface(self):
        """Build the timer interface"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Timer display
        self.time_label = Label(
            text=self._format_time(self.current_time),
            font_size='48sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.time_label)

        # Progress info
        self.progress_label = Label(
            text=f'Rest Time: {self.rest_time} seconds',
            font_size='18sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        layout.add_widget(self.progress_label)

        # Control buttons
        button_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)

        # Start/Pause button
        self.start_pause_btn = StyledButton(text='START')
        self.start_pause_btn.bind(on_press=self.toggle_timer)
        button_layout.add_widget(self.start_pause_btn)

        # Reset button
        reset_btn = StyledButton(text='RESET')
        reset_btn.bind(on_press=self.reset_timer)
        button_layout.add_widget(reset_btn)

        # Skip button
        skip_btn = StyledButton(text='SKIP')
        skip_btn.bind(on_press=self.skip_timer)
        button_layout.add_widget(skip_btn)

        layout.add_widget(button_layout)

        # Quick time buttons - including Excel-specified 75s
        quick_layout = BoxLayout(size_hint_y=None, height=50, spacing=5)
        for time_val in AppConstants.REST_TIMER_OPTIONS:
            time_btn = Button(
                text=f'{time_val}s',
                size_hint_x=0.2,
                background_color=(0.3, 0.3, 0.3, 1) if time_val != AppConstants.DEFAULT_REST_TIME_SECONDS else (0.5, 0.3, 0.8, 1)  # Highlight default
            )
            time_btn.bind(on_press=lambda x, t=time_val: self.set_time(t))
            quick_layout.add_widget(time_btn)

        layout.add_widget(quick_layout)

        self.content = layout

    def _format_time(self, seconds):
        """Format seconds into MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f'{minutes:02d}:{secs:02d}'

    def set_time(self, seconds):
        """Set custom rest time"""
        self.rest_time = seconds
        self.current_time = seconds
        self.time_label.text = self._format_time(self.current_time)
        self.progress_label.text = f'Rest Time: {self.rest_time} seconds'

    def toggle_timer(self, instance):
        """Start or pause the timer"""
        if self.timer_event is None:
            # Start timer
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)
            self.start_pause_btn.text = 'PAUSE'
        else:
            # Pause timer
            self.timer_event.cancel()
            self.timer_event = None
            self.start_pause_btn.text = 'START'

    def update_timer(self, dt):
        """Update timer countdown"""
        self.current_time -= 1
        self.time_label.text = self._format_time(self.current_time)

        # Change color as time runs out
        if self.current_time <= 10:
            self.time_label.color = (1, 0.2, 0.2, 1)  # Red
        elif self.current_time <= 30:
            self.time_label.color = (1, 0.8, 0.2, 1)  # Orange
        else:
            self.time_label.color = (1, 1, 1, 1)  # White

        if self.current_time <= 0:
            self.timer_complete()

    def timer_complete(self):
        """Handle timer completion"""
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

        self.time_label.text = '00:00'
        self.time_label.color = (0.2, 1, 0.2, 1)  # Green
        self.start_pause_btn.text = 'COMPLETE!'

        # Flash animation
        anim = Animation(color=(1, 1, 1, 1), duration=0.5) + Animation(color=(0.2, 1, 0.2, 1), duration=0.5)
        anim.repeat = True
        anim.start(self.time_label)

        # Auto-close after 3 seconds
        Clock.schedule_once(self.auto_close, 3)

    def auto_close(self, dt):
        """Auto close timer and call completion callback"""
        self.dismiss()
        if self.on_complete_callback:
            self.on_complete_callback()

    def reset_timer(self, instance):
        """Reset timer to original time"""
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

        self.current_time = self.rest_time
        self.time_label.text = self._format_time(self.current_time)
        self.time_label.color = (1, 1, 1, 1)
        self.start_pause_btn.text = 'START'

    def skip_timer(self, instance):
        """Skip rest timer"""
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

        self.dismiss()
        if self.on_complete_callback:
            self.on_complete_callback()

class WorkoutRepository:
    """Repository pattern for workout data management"""

    def __init__(self, storage: DataStorage) -> None:
        self.storage = storage

    def get_session_exercises(self, session_type: str) -> List[Dict[str, Any]]:
        """Get exercises for specific session type"""
        all_exercises = self.storage.get_exercises()

        if session_type == AppConstants.WARMUP_DYNAMIC:
            return [ex for ex in all_exercises if ex['category'] == AppConstants.CATEGORY_WARMUP_DYNAMIC]
        elif session_type == AppConstants.WARMUP_STABILITY:
            return [ex for ex in all_exercises if ex['category'] == AppConstants.CATEGORY_WARMUP_STABILITY]
        elif session_type == AppConstants.WARMUP_MOVEMENT:
            return [ex for ex in all_exercises if ex['category'] == AppConstants.CATEGORY_WARMUP_MOVEMENT]
        elif session_type == AppConstants.SESSION_TYPE_1:
            session1_names = ["Back squat", "Bridge", "Bench press", "Bench superman",
                            "Bentover Row", "Pallof Twist", "Shoulder press", "Knee Tucks"]
            return [ex for ex in all_exercises if ex['name'] in session1_names]
        elif session_type == AppConstants.SESSION_TYPE_2:
            # Removed "Knee Tucks" to avoid duplication with Session 1
            session2_names = ["Plank", "Incline Bench Press", "Pallof Press", "Lat Pull Downs",
                            "Landmines", "Upright row"]
            return [ex for ex in all_exercises if ex['name'] in session2_names]

        return all_exercises

    def log_workout(self, session_type: str, completed_exercises: List[Dict[str, Any]]) -> bool:
        """Log completed workout"""
        session_name = f"{session_type.title()} - {datetime.now().strftime('%Y-%m-%d')}"
        return self.storage.save_workout_session(session_name, completed_exercises)

    def get_exercise_history(self, exercise_id: int) -> List[Dict[str, Any]]:
        """Get history for specific exercise"""
        weights = self.storage._load_json(self.storage.weights_file)
        return [w for w in weights if w.get('exercise_id') == exercise_id]

class ReportRepository:
    """Repository for report generation and management"""

    def __init__(self, storage: DataStorage) -> None:
        self.storage = storage

    def generate_progress_report(self) -> Dict[str, Any]:
        """Generate comprehensive progress report"""
        return self.storage.generate_weekly_report()

    def export_to_excel_format(self) -> str:
        """Export data as downloadable Excel .xlsx file"""
        try:
            # Get data
            sessions = self.storage.get_workout_history(AppConstants.REPORT_DAYS_RANGE)
            weights = self.storage._load_json(self.storage.weights_file)
            exercises = self.storage.get_exercises()

            # Create Downloads directory
            downloads_dir = self._get_downloads_directory()
            os.makedirs(downloads_dir, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if XLSX_AVAILABLE:
                # Create Excel file with xlsxwriter (pure Python, works on Android)
                filename = f"IGCSE_GYM_Report_{timestamp}.xlsx"
                filepath = os.path.join(downloads_dir, filename)
                logger.info(f"Creating Excel report with xlsxwriter: {filepath}")

                # Create workbook
                workbook = xlsxwriter.Workbook(filepath)
                worksheet = workbook.add_worksheet("IGCSE GYM Report")

                # Define formats
                header_format = workbook.add_format({
                    'bold': True,
                    'font_size': 14,
                    'bg_color': '#46008B',
                    'font_color': 'white'
                })
                section_format = workbook.add_format({
                    'bold': True,
                    'font_size': 12
                })
                col_header_format = workbook.add_format({'bold': True})

                row = 0

                # Main Header
                worksheet.write(row, 0, AppConstants.REPORT_TITLE, header_format)
                row += 1
                worksheet.write(row, 0, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                row += 2

                # Exercise Database Section
                worksheet.write(row, 0, "EXERCISE DATABASE", section_format)
                row += 1
                headers = ['Exercise Name', 'Category', 'Sets', 'Reps', 'Description']
                for col, header in enumerate(headers):
                    worksheet.write(row, col, header, col_header_format)
                row += 1

                for exercise in exercises:
                    sets = exercise.get('sets', 1)
                    reps = exercise['reps']
                    unit = exercise.get('unit', 'reps')
                    reps_display = f"{reps} {unit}" if unit != 'reps' else str(reps)

                    worksheet.write(row, 0, exercise['name'])
                    worksheet.write(row, 1, exercise['category'])
                    worksheet.write(row, 2, sets if not exercise['category'].startswith('Warmup') else 1)
                    worksheet.write(row, 3, reps_display)
                    worksheet.write(row, 4, exercise['description'])
                    row += 1

                row += 1

                # Workout Sessions Section
                worksheet.write(row, 0, "WORKOUT SESSIONS", section_format)
                row += 1
                session_headers = ['Date', 'Session Type', 'Exercise', 'Weight (kg)', 'Reps Completed', 'Sets']
                for col, header in enumerate(session_headers):
                    worksheet.write(row, col, header, col_header_format)
                row += 1

                for session in sessions:
                    session_date = session.get('date', 'Unknown')
                    session_name = session.get('name', 'Workout')

                    for exercise_log in session.get('exercises', []):
                        exercise_info = next((ex for ex in exercises if ex['id'] == exercise_log.get('exercise_id')), {})
                        exercise_name = exercise_log.get('name', exercise_info.get('name', 'Unknown'))

                        weight = exercise_log.get('weight', 0)
                        reps = exercise_log.get('reps', 0)
                        sets = exercise_info.get('sets', 1)

                        if 'warmup' in session_name.lower():
                            session_type = 'Warmup'
                            weight_val = 'N/A'
                        else:
                            session_type = 'Strength Training'
                            weight_val = weight

                        worksheet.write(row, 0, session_date)
                        worksheet.write(row, 1, session_type)
                        worksheet.write(row, 2, exercise_name)
                        worksheet.write(row, 3, weight_val)
                        worksheet.write(row, 4, reps)
                        worksheet.write(row, 5, sets if session_type != 'Warmup' else 'N/A')
                        row += 1

                row += 1

                # Warmup Tracking Section
                worksheet.write(row, 0, "WARMUP COMPLETION LOG", section_format)
                row += 1
                warmup_headers = ['Date', 'Warmup Type', 'Exercises Completed', 'Total Time (estimated)']
                for col, header in enumerate(warmup_headers):
                    worksheet.write(row, col, header, col_header_format)
                row += 1

                warmup_sessions = [s for s in sessions if 'warmup' in s.get('name', '').lower()]
                for warmup in warmup_sessions:
                    warmup_type = 'Unknown'
                    if 'dynamic' in warmup.get('name', '').lower():
                        warmup_type = 'Dynamic Mobility'
                    elif 'stability' in warmup.get('name', '').lower():
                        warmup_type = 'Stability Training'
                    elif 'movement' in warmup.get('name', '').lower():
                        warmup_type = 'Movement Integration'

                    exercise_count = len(warmup.get('exercises', []))
                    estimated_time = f"{exercise_count * 2} minutes"

                    worksheet.write(row, 0, warmup.get('date', 'Unknown'))
                    worksheet.write(row, 1, warmup_type)
                    worksheet.write(row, 2, exercise_count)
                    worksheet.write(row, 3, estimated_time)
                    row += 1

                row += 1

                # Summary Statistics
                worksheet.write(row, 0, "SUMMARY STATISTICS", section_format)
                row += 1
                worksheet.write(row, 0, "Total Workout Sessions")
                worksheet.write(row, 1, len([s for s in sessions if 'warmup' not in s.get('name', '').lower()]))
                row += 1
                worksheet.write(row, 0, "Total Warmup Sessions")
                worksheet.write(row, 1, len(warmup_sessions))
                row += 1
                worksheet.write(row, 0, "Total Exercises in Database")
                worksheet.write(row, 1, len(exercises))
                row += 1
                worksheet.write(row, 0, "Report Date Range")
                worksheet.write(row, 1, f"{AppConstants.REPORT_DAYS_RANGE} days")

                # Auto-adjust column widths
                worksheet.set_column(0, 0, 25)  # Exercise Name / Date
                worksheet.set_column(1, 1, 20)  # Category / Type
                worksheet.set_column(2, 2, 12)  # Sets
                worksheet.set_column(3, 3, 15)  # Reps / Weight
                worksheet.set_column(4, 4, 40)  # Description

                # Close workbook
                workbook.close()
                logger.info(f"Excel report created successfully: {filename}")
                return filepath

            else:
                # CSV export fallback (used when xlsxwriter is not available)
                filename = f"IGCSE_GYM_Report_{timestamp}.csv"
                filepath = os.path.join(downloads_dir, filename)
                logger.info(f"Creating CSV report (xlsxwriter not available): {filepath}")

                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)

                    # Header
                    writer.writerow([AppConstants.REPORT_TITLE])
                    writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
                    writer.writerow([])

                    # Exercise Database Section
                    writer.writerow(['EXERCISE DATABASE'])
                    writer.writerow(['Exercise Name', 'Category', 'Sets', 'Reps', 'Description'])
                    for exercise in exercises:
                        sets = exercise.get('sets', 1)
                        reps = exercise['reps']
                        unit = exercise.get('unit', 'reps')
                        reps_display = f"{reps} {unit}" if unit != 'reps' else str(reps)

                        writer.writerow([
                            exercise['name'],
                            exercise['category'],
                            sets if not exercise['category'].startswith('Warmup') else 1,
                            reps_display,
                            exercise['description']
                        ])

                    writer.writerow([])

                    # Workout Sessions Section
                    writer.writerow(['WORKOUT SESSIONS'])
                    writer.writerow(['Date', 'Session Type', 'Exercise', 'Weight (kg)', 'Reps Completed', 'Sets'])

                    for session in sessions:
                        session_date = session.get('date', 'Unknown')
                        session_name = session.get('name', 'Workout')

                        for exercise_log in session.get('exercises', []):
                            exercise_info = next((ex for ex in exercises if ex['id'] == exercise_log.get('exercise_id')), {})
                            exercise_name = exercise_log.get('name', exercise_info.get('name', 'Unknown'))

                            weight = exercise_log.get('weight', 0)
                            reps = exercise_log.get('reps', 0)
                            sets = exercise_info.get('sets', 1)

                            if 'warmup' in session_name.lower():
                                session_type = 'Warmup'
                                weight = 'N/A'
                            else:
                                session_type = 'Strength Training'

                            writer.writerow([
                                session_date,
                                session_type,
                                exercise_name,
                                weight,
                                reps,
                                sets if session_type != 'Warmup' else 'N/A'
                            ])

                    writer.writerow([])

                    # Warmup Tracking Section
                    writer.writerow(['WARMUP COMPLETION LOG'])
                    writer.writerow(['Date', 'Warmup Type', 'Exercises Completed', 'Total Time (estimated)'])

                    warmup_sessions = [s for s in sessions if 'warmup' in s.get('name', '').lower()]
                    for warmup in warmup_sessions:
                        warmup_type = 'Unknown'
                        if 'dynamic' in warmup.get('name', '').lower():
                            warmup_type = 'Dynamic Mobility'
                        elif 'stability' in warmup.get('name', '').lower():
                            warmup_type = 'Stability Training'
                        elif 'movement' in warmup.get('name', '').lower():
                            warmup_type = 'Movement Integration'

                        exercise_count = len(warmup.get('exercises', []))
                        estimated_time = f"{exercise_count * 2} minutes"

                        writer.writerow([
                            warmup.get('date', 'Unknown'),
                            warmup_type,
                            exercise_count,
                            estimated_time
                        ])

                    writer.writerow([])

                    # Summary Statistics
                    writer.writerow(['SUMMARY STATISTICS'])
                    writer.writerow(['Metric', 'Value'])
                    writer.writerow(['Total Workout Sessions', len([s for s in sessions if 'warmup' not in s.get('name', '').lower()])])
                    writer.writerow(['Total Warmup Sessions', len(warmup_sessions)])
                    writer.writerow(['Total Exercises in Database', len(exercises)])
                    writer.writerow(['Report Date Range', f'{AppConstants.REPORT_DAYS_RANGE} days'])

                logger.info(f"CSV report created successfully: {filename}")
                return filepath

        except Exception as e:
            logger.error(f"Excel export failed: {e}", exc_info=True)
            return f"Error: {str(e)}"

    def _get_downloads_directory(self) -> str:
        """Get the appropriate downloads directory based on platform"""
        if platform == 'android':
            # Android storage handling with multiple fallbacks
            try:
                from android.storage import primary_external_storage_path, app_storage_path

                # Try to use Downloads folder first (requires MANAGE_EXTERNAL_STORAGE on API 30+)
                try:
                    android_downloads = os.path.join(primary_external_storage_path(), 'Download')
                    if os.path.exists(android_downloads) and os.access(android_downloads, os.W_OK):
                        logger.info(f"Using Android downloads path: {android_downloads}")
                        return android_downloads
                except Exception as e:
                    logger.warning(f"Cannot access Downloads folder: {e}")

                # Fallback to app's external storage (doesn't need special permissions)
                try:
                    app_external = app_storage_path()
                    if app_external and os.path.exists(app_external):
                        downloads_alt = os.path.join(app_external, 'downloads')
                        os.makedirs(downloads_alt, exist_ok=True)
                        logger.info(f"Using app external storage: {downloads_alt}")
                        return downloads_alt
                except Exception as e:
                    logger.warning(f"Cannot access app external storage: {e}")

                # Final fallback to app's internal storage
                app_internal = os.path.join(os.path.expanduser("~"), 'downloads')
                os.makedirs(app_internal, exist_ok=True)
                logger.info(f"Using app internal storage: {app_internal}")
                return app_internal

            except Exception as e:
                logger.error(f"Failed to get Android storage path: {e}, using internal storage")
                # Absolute fallback
                fallback = os.path.join(os.path.expanduser("~"), 'downloads')
                os.makedirs(fallback, exist_ok=True)
                return fallback
        else:
            # Desktop Downloads folder
            home = os.path.expanduser("~")
            downloads = os.path.join(home, 'Downloads')
            if not os.path.exists(downloads):
                downloads = os.path.join(home, 'Desktop')  # Fallback
            if not os.path.exists(downloads):
                downloads = home  # Last resort fallback
            return downloads

class WorkoutScreen(BoxLayout):
    """Main workout screen with all features"""

    def __init__(self, session_type, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        self.session_type = session_type
        self.app = app_instance
        self.completed_exercises = []

        # Background
        with self.canvas.before:
            Color(*AppConstants.COLOR_BACKGROUND)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.build_workout_interface()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def build_workout_interface(self):
        """Build the workout interface"""
        # Title
        title = Label(
            text=f'{self.session_type.upper()} WORKOUT',
            font_size='32sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=80
        )
        self.add_widget(title)

        # Exercise list
        scroll = ScrollView()
        exercise_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        exercise_layout.bind(minimum_height=exercise_layout.setter('height'))

        exercises = self.app.workout_repo.get_session_exercises(self.session_type)

        for exercise in exercises:
            exercise_widget = self.create_exercise_widget(exercise)
            exercise_layout.add_widget(exercise_widget)

        scroll.add_widget(exercise_layout)
        self.add_widget(scroll)

        # Control buttons
        button_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)

        complete_btn = StyledButton(text='COMPLETE WORKOUT')
        complete_btn.bind(on_press=self.complete_workout)
        button_layout.add_widget(complete_btn)

        # Add REST TIMER button only for strength training sessions (not warmup)
        if not self.session_type.startswith('warmup'):
            rest_timer_btn = StyledButton(text='⏱️ REST TIMER (75s)')
            rest_timer_btn.bind(on_press=self.start_session_rest_timer)
            button_layout.add_widget(rest_timer_btn)

        back_btn = StyledButton(text='← GO BACK')
        back_btn.bind(on_press=self.go_back)
        button_layout.add_widget(back_btn)

        self.add_widget(button_layout)

    def create_exercise_widget(self, exercise):
        """Create widget for individual exercise"""
        container = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=10)

        # Exercise info
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.6)

        name_label = Label(
            text=exercise['name'],
            font_size='18sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign='left'
        )
        name_label.bind(size=name_label.setter('text_size'))

        # Show sets x reps format matching Excel sheet
        is_warmup = exercise['category'].startswith('Warmup')
        if is_warmup:
            reps_text = f"{exercise['reps']} {exercise.get('unit', 'reps')}"
        else:
            sets = exercise.get('sets', 3)
            reps = exercise['reps']
            unit = exercise.get('unit', 'reps')
            reps_text = f"{sets}x{reps} {unit}"

        desc_label = Label(
            text=f"{exercise['description']} - {reps_text}",
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1),
            halign='left'
        )
        desc_label.bind(size=desc_label.setter('text_size'))

        info_layout.add_widget(name_label)
        info_layout.add_widget(desc_label)

        # Input layout - different for warmup vs strength exercises
        input_layout = BoxLayout(orientation='horizontal', size_hint_x=0.4, spacing=5)

        if is_warmup:
            # For warmup: only show completion button (no weight/reps input)
            complete_btn = Button(
                text='COMPLETE',
                background_color=(0.2, 0.7, 0.2, 1)
            )
            complete_btn.bind(on_press=lambda x: self.log_exercise(exercise, None, exercise['reps']))
            input_layout.add_widget(complete_btn)
        else:
            # For strength exercises: weight input + fixed reps display + log button
            weight_input = TextInput(
                hint_text='Weight',
                multiline=False,
                size_hint_x=0.5,
                input_filter='float'
            )

            sets = exercise.get('sets', 3)
            reps = exercise['reps']
            unit = exercise.get('unit', 'reps')
            reps_label = Label(
                text=f"{sets}x{reps} {unit}",
                font_size='14sp',
                color=(1, 1, 1, 1),
                size_hint_x=0.3
            )

            log_btn = Button(
                text='LOG',
                size_hint_x=0.25,
                background_color=(0.2, 0.7, 0.2, 1)
            )
            log_btn.bind(on_press=lambda x: self.log_exercise(exercise, weight_input.text, exercise['reps']))

            input_layout.add_widget(weight_input)
            input_layout.add_widget(reps_label)
            input_layout.add_widget(log_btn)

        container.add_widget(info_layout)
        container.add_widget(input_layout)

        return container

    def log_exercise(self, exercise, weight, reps):
        """Log exercise completion with input validation"""
        is_warmup = exercise['category'].startswith('Warmup')

        if is_warmup:
            # For warmup exercises, just log completion
            try:
                reps_val = int(reps) if reps else exercise['reps']

                # Validate reps value
                if reps_val <= AppConstants.MIN_REPS:
                    popup = Popup(
                        title='Invalid Input',
                        content=Label(text='Reps must be greater than 0'),
                        size_hint=AppConstants.POPUP_SMALL
                    )
                    popup.open()
                    return

                if reps_val > AppConstants.MAX_REPS:
                    popup = Popup(
                        title='Invalid Input',
                        content=Label(text=f'Reps value seems too high (max: {AppConstants.MAX_REPS})'),
                        size_hint=AppConstants.POPUP_SMALL
                    )
                    popup.open()
                    return

                self.completed_exercises.append({
                    'exercise_id': exercise['id'],
                    'name': exercise['name'],
                    'weight': 0,  # No weight for warmup
                    'reps': reps_val
                })

                # Show confirmation
                unit = exercise.get('unit', 'reps')
                popup = Popup(
                    title='Exercise Completed',
                    content=Label(text=f"{exercise['name']}: {reps_val} {unit}"),
                    size_hint=(0.6, 0.4)
                )
                popup.open()
            except (ValueError, TypeError):
                popup = Popup(
                    title='Invalid Input',
                    content=Label(text='Please enter a valid number for reps'),
                    size_hint=(0.6, 0.4)
                )
                popup.open()

        elif weight and reps:
            try:
                weight_val = float(weight)
                reps_val = int(reps)

                # Validate weight value
                if weight_val <= AppConstants.MIN_WEIGHT_KG:
                    popup = Popup(
                        title='Invalid Weight',
                        content=Label(text='Weight must be greater than 0'),
                        size_hint=AppConstants.POPUP_SMALL
                    )
                    popup.open()
                    return

                if weight_val > AppConstants.MAX_WEIGHT_KG:
                    popup = Popup(
                        title='Invalid Weight',
                        content=Label(text=f'Weight seems too high (max: {AppConstants.MAX_WEIGHT_KG}kg)'),
                        size_hint=AppConstants.POPUP_SMALL
                    )
                    popup.open()
                    return

                # Validate reps value
                if reps_val <= AppConstants.MIN_REPS:
                    popup = Popup(
                        title='Invalid Reps',
                        content=Label(text='Reps must be greater than 0'),
                        size_hint=AppConstants.POPUP_SMALL
                    )
                    popup.open()
                    return

                if reps_val > AppConstants.MAX_REPS:
                    popup = Popup(
                        title='Invalid Reps',
                        content=Label(text=f'Reps value seems too high (max: {AppConstants.MAX_REPS})'),
                        size_hint=AppConstants.POPUP_SMALL
                    )
                    popup.open()
                    return

                self.app.storage.save_weight_log(exercise['id'], weight_val, reps_val)
                self.completed_exercises.append({
                    'exercise_id': exercise['id'],
                    'name': exercise['name'],
                    'weight': weight_val,
                    'reps': reps_val
                })

                # Show confirmation
                popup = Popup(
                    title='Exercise Logged',
                    content=Label(text=f"{exercise['name']}: {weight}kg x {reps} reps"),
                    size_hint=(0.6, 0.4)
                )
                popup.open()

            except ValueError:
                popup = Popup(
                    title='Invalid Input',
                    content=Label(text='Please enter valid numbers for weight and reps'),
                    size_hint=(0.6, 0.4)
                )
                popup.open()
        else:
            popup = Popup(
                title='Missing Input',
                content=Label(text='Please enter weight before logging'),
                size_hint=(0.6, 0.4)
            )
            popup.open()

    def start_session_rest_timer(self, instance):
        """Start rest timer for the workout session"""
        # Default rest time as specified in Excel sheet Recovery column
        rest_time = AppConstants.DEFAULT_REST_TIME_SECONDS

        timer = RestTimerWidget(
            rest_time=rest_time,
            on_complete_callback=lambda: self.on_rest_complete()
        )
        timer.title = 'REST BETWEEN EXERCISES'
        timer.progress_label.text = f'Recovery Time: {rest_time} seconds (as per Excel)'
        timer.open()

    def on_rest_complete(self):
        """Handle rest timer completion"""
        popup = Popup(
            title='Rest Complete!',
            content=Label(text='Ready for next exercise'),
            size_hint=(0.6, 0.4)
        )
        popup.open()

    def complete_workout(self, instance):
        """Complete the workout session"""
        if self.completed_exercises:
            self.app.workout_repo.log_workout(self.session_type, self.completed_exercises)

            popup = Popup(
                title='Workout Complete!',
                content=Label(text=f'Logged {len(self.completed_exercises)} exercises'),
                size_hint=(0.6, 0.4)
            )
            popup.open()

        self.go_back(instance)

    def go_back(self, instance):
        """Return to main menu"""
        self.app.show_main_screen()

class ReportsScreen(BoxLayout):
    """Reports and analytics screen"""

    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        self.app = app_instance

        # Background
        with self.canvas.before:
            Color(*AppConstants.COLOR_BACKGROUND)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.build_reports_interface()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def build_reports_interface(self):
        """Build reports interface"""
        # Title
        title = Label(
            text='WORKOUT REPORTS',
            font_size='32sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=80
        )
        self.add_widget(title)

        # Description - dynamic based on availability
        if XLSX_AVAILABLE:
            desc_text = 'Download your complete workout data as an Excel file (.xlsx)\nwith formatting and colors.'
        else:
            desc_text = 'Download your complete workout data as a CSV file\nthat opens in Excel, Google Sheets, or any spreadsheet app.'

        desc = Label(
            text=desc_text,
            font_size='18sp',
            color=(0.8, 0.8, 0.8, 1),
            halign='center',
            size_hint_y=None,
            height=80
        )
        self.add_widget(desc)

        # Download button - dynamic text
        button_text = '📥 DOWNLOAD EXCEL REPORT' if XLSX_AVAILABLE else '📥 DOWNLOAD REPORT (CSV)'
        download_btn = StyledButton(
            text=button_text,
            size_hint_y=None,
            height=80
        )
        download_btn.bind(on_press=self.download_excel_report)
        self.add_widget(download_btn)

        # Status area
        self.status_label = Label(
            text='Ready to download your workout report',
            font_size='16sp',
            color=(0.7, 0.7, 0.7, 1),
            halign='center',
            size_hint_y=None,
            height=60
        )
        self.add_widget(self.status_label)

        # Info section
        info_text = """
The workout report includes:
• Complete exercise database with sets/reps
• All workout session records
• Warmup completion tracking
• Summary statistics
• Date ranges and progress data

""" + ("Excel format with formatting and colors." if XLSX_AVAILABLE else "CSV format - opens in Excel, Google Sheets, or any spreadsheet app.") + """
File will be saved to your Downloads folder.
        """

        info_label = Label(
            text=info_text,
            font_size='14sp',
            color=(0.6, 0.6, 0.6, 1),
            halign='center',
            valign='center'
        )
        info_label.bind(size=info_label.setter('text_size'))
        self.add_widget(info_label)

        # Back button
        back_btn = StyledButton(
            text='← GO BACK',
            size_hint_y=None,
            height=60
        )
        back_btn.bind(on_press=self.go_back)
        self.add_widget(back_btn)

    def generate_report(self, instance):
        """Generate and display weekly report"""
        report = self.app.report_repo.generate_progress_report()

        report_text = f"""
WEEKLY WORKOUT REPORT
{'='*30}

Week: {report['week_start'][:10]} to {report['week_end'][:10]}
Total Sessions: {report['total_sessions']}
Total Exercises: {report['total_exercises']}

SESSIONS COMPLETED:
"""

        for session in report['sessions']:
            report_text += f"• {session['name']} - {len(session.get('exercises', []))} exercises\n"

        if report['progress_summary']:
            report_text += "\nPROGRESS SUMMARY:\n"
            exercises = self.app.storage.get_exercises()
            exercise_names = {ex['id']: ex['name'] for ex in exercises}

            for ex_id, logs in report['progress_summary'].items():
                if logs:
                    ex_name = exercise_names.get(int(ex_id), f"Exercise {ex_id}")
                    latest_weight = logs[-1]['weight']
                    report_text += f"• {ex_name}: {latest_weight}kg\n"

        self.report_label.text = report_text
        self.report_label.text_size = (self.width - 40, None)

    def download_excel_report(self, instance):
        """Download workout report file"""
        try:
            self.status_label.text = 'Generating report...'

            # Generate and save the report file
            filepath = self.app.report_repo.export_to_excel_format()

            if filepath.startswith('Error:'):
                self.status_label.text = 'Download failed'
                popup = Popup(
                    title='Download Error',
                    content=Label(text=filepath),
                    size_hint=(0.7, 0.4)
                )
                popup.open()
            else:
                filename = os.path.basename(filepath)
                self.status_label.text = f'Downloaded: {filename}'

                # Dynamic success message
                if XLSX_AVAILABLE:
                    msg = f'Excel report saved as:\n{filename}\n\nFormatted .xlsx file\nCheck your Downloads folder'
                else:
                    msg = f'Report saved as:\n{filename}\n\nCSV format - opens in any spreadsheet app\nCheck your Downloads folder'

                popup = Popup(
                    title='Report Downloaded!',
                    content=Label(text=msg),
                    size_hint=(0.8, 0.5)
                )
                popup.open()

        except Exception as e:
            self.status_label.text = 'Download failed'
            popup = Popup(
                title='Download Error',
                content=Label(text=f'Failed to generate report:\n{str(e)}'),
                size_hint=(0.7, 0.4)
            )
            popup.open()

    def go_back(self, instance):
        """Return to main menu"""
        self.app.show_main_screen()

class WarmupMenuScreen(BoxLayout):
    """Warmup selection menu with three workout types"""

    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        self.app = app_instance

        # Background
        with self.canvas.before:
            Color(*AppConstants.COLOR_BACKGROUND)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.build_warmup_menu()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def build_warmup_menu(self):
        """Build the warmup menu interface"""
        # Title
        title = Label(
            text='WARM-UP ROUTINES',
            font_size='32sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=80
        )
        self.add_widget(title)

        # Description
        desc = Label(
            text='Choose your warm-up routine:',
            font_size='18sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=50
        )
        self.add_widget(desc)

        # Dynamic Mobility button
        warmup_dynamic_btn = StyledButton(
            text='Dynamic Mobility',
            size_hint_y=None,
            height=70
        )
        warmup_dynamic_btn.bind(on_press=lambda x: self.app.show_workout_screen('warmup-dynamic'))
        self.add_widget(warmup_dynamic_btn)

        # Stability Training button
        warmup_stability_btn = StyledButton(
            text='Stability Training',
            size_hint_y=None,
            height=70
        )
        warmup_stability_btn.bind(on_press=lambda x: self.app.show_workout_screen('warmup-stability'))
        self.add_widget(warmup_stability_btn)

        # Movement Integration button
        warmup_movement_btn = StyledButton(
            text='Movement Integration',
            size_hint_y=None,
            height=70
        )
        warmup_movement_btn.bind(on_press=lambda x: self.app.show_workout_screen('warmup-movement'))
        self.add_widget(warmup_movement_btn)

        # Go back button
        back_btn = StyledButton(
            text='← GO BACK',
            size_hint_y=None,
            height=60
        )
        back_btn.bind(on_press=self.go_back)
        self.add_widget(back_btn)

    def go_back(self, instance):
        """Return to main menu"""
        self.app.show_main_screen()

class IGCSEGymApp(App):
    """Main application class with ALL features"""

    def build(self):
        # Initialize storage and repositories
        self.storage = DataStorage()
        self.workout_repo = WorkoutRepository(self.storage)
        self.report_repo = ReportRepository(self.storage)

        # Create main layout
        self.main_layout = BoxLayout()
        self.show_main_screen()

        return self.main_layout

    def on_start(self):
        """Called when the app starts - request permissions on Android"""
        super().on_start()
        if platform == 'android':
            self.request_android_permissions()

    def request_android_permissions(self):
        """Request necessary permissions on Android"""
        try:
            from android.permissions import request_permissions, check_permission, Permission

            # List of permissions to request
            permissions = []

            # Check and request MANAGE_EXTERNAL_STORAGE for Android 11+ (API 30+)
            if not check_permission(Permission.WRITE_EXTERNAL_STORAGE):
                permissions.append(Permission.WRITE_EXTERNAL_STORAGE)

            if not check_permission(Permission.READ_EXTERNAL_STORAGE):
                permissions.append(Permission.READ_EXTERNAL_STORAGE)

            if not check_permission(Permission.INTERNET):
                permissions.append(Permission.INTERNET)

            # Request permissions if needed
            if permissions:
                logger.info(f"Requesting Android permissions: {permissions}")
                request_permissions(permissions, self.on_permissions_callback)
            else:
                logger.info("All permissions already granted")

        except Exception as e:
            logger.warning(f"Permission request failed: {e}")
            # App will continue to work with internal storage

    def on_permissions_callback(self, permissions, grant_results):
        """Handle permission request results"""
        try:
            granted = [p for p, g in zip(permissions, grant_results) if g]
            denied = [p for p, g in zip(permissions, grant_results) if not g]

            if granted:
                logger.info(f"Permissions granted: {granted}")

            if denied:
                logger.warning(f"Permissions denied: {denied}")
                # Show info popup that app will use internal storage
                content = Label(
                    text="Storage permission not granted.\nReports will be saved to app's internal storage.",
                    halign='center'
                )
                popup = Popup(
                    title='Storage Access',
                    content=content,
                    size_hint=(0.8, 0.4)
                )
                # Auto-dismiss after 3 seconds
                Clock.schedule_once(lambda dt: popup.dismiss(), 3)
                popup.open()

        except Exception as e:
            logger.error(f"Error in permission callback: {e}")

    def show_main_screen(self):
        """Display main menu screen"""
        self.main_layout.clear_widgets()

        main_screen = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Background
        with main_screen.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Dark gray background
            main_screen.rect = Rectangle(size=main_screen.size, pos=main_screen.pos)
        main_screen.bind(size=self._update_main_rect, pos=self._update_main_rect)

        # Title
        title = Label(
            text='IGCSE GYM',
            font_size='36sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=100
        )
        main_screen.add_widget(title)

        # Warm-up button - leads to warmup menu
        warmup_btn = StyledButton(
            text='WARM-UP ROUTINES',
            size_hint_y=None,
            height=70
        )
        warmup_btn.bind(on_press=lambda x: self.show_warmup_menu())
        main_screen.add_widget(warmup_btn)

        # Session 1 button
        session1_btn = StyledButton(
            text='WORKOUT SESSION 1',
            size_hint_y=None,
            height=70
        )
        session1_btn.bind(on_press=lambda x: self.show_workout_screen('session1'))
        main_screen.add_widget(session1_btn)

        # Session 2 button
        session2_btn = StyledButton(
            text='WORKOUT SESSION 2',
            size_hint_y=None,
            height=70
        )
        session2_btn.bind(on_press=lambda x: self.show_workout_screen('session2'))
        main_screen.add_widget(session2_btn)

        # Reports button
        reports_btn = StyledButton(
            text='VIEW REPORTS',
            size_hint_y=None,
            height=70
        )
        reports_btn.bind(on_press=lambda x: self.show_reports_screen())
        main_screen.add_widget(reports_btn)

        # Status area with enterprise insights
        workouts_this_week = len(self.storage.get_workout_history(7))
        total_exercises = len(self.storage.get_exercises())
        insights = self.storage.get_insights()
        health = self.storage.get_health_status()

        # Create insights text
        insights_text = "\n".join(f"• {insight}" for insight in insights[:3])

        status_text = f"""
IGCSE IURI GYM - ENTERPRISE EDITION v2.0.0

📊 Recent Activity:
• {workouts_this_week} workouts this week
• {total_exercises} exercises in database
• {health['total_weight_logs']} total exercise logs
• {health['backups_available']} backups available

💡 Insights:
{insights_text}

Select a workout type above to begin!
        """

        status_label = Label(
            text=status_text,
            font_size='15sp',
            color=(0.8, 0.8, 0.8, 1),
            halign='center',
            valign='top'
        )
        status_label.bind(size=status_label.setter('text_size'))
        main_screen.add_widget(status_label)

        self.main_layout.add_widget(main_screen)
        self.main_screen_ref = main_screen

    def _update_main_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def show_workout_screen(self, session_type):
        """Show workout screen for specific session type"""
        self.main_layout.clear_widgets()
        workout_screen = WorkoutScreen(session_type, self)
        self.main_layout.add_widget(workout_screen)

    def show_reports_screen(self):
        """Show reports and analytics screen"""
        self.main_layout.clear_widgets()
        reports_screen = ReportsScreen(self)
        self.main_layout.add_widget(reports_screen)

    def show_warmup_menu(self):
        """Show warmup selection menu with three tabs"""
        self.main_layout.clear_widgets()
        warmup_menu = WarmupMenuScreen(self)
        self.main_layout.add_widget(warmup_menu)

if __name__ == '__main__':
    IGCSEGymApp().run()