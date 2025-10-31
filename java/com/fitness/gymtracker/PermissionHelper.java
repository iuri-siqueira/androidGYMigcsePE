package com.fitness.gymtracker;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.Settings;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import android.content.pm.PackageManager;
import android.Manifest;

/**
 * Helper class for managing Android storage permissions
 * Handles both legacy permissions and Android 13+ MANAGE_EXTERNAL_STORAGE
 */
public class PermissionHelper {
    private static final int REQUEST_EXTERNAL_STORAGE = 1;
    private static final int REQUEST_MANAGE_STORAGE = 2;

    /**
     * Request storage permissions appropriate for the Android version
     */
    public static void requestStoragePermissions(Activity activity) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            // Android 11+ (API 30+) - Request MANAGE_EXTERNAL_STORAGE
            if (!Environment.isExternalStorageManager()) {
                try {
                    Intent intent = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
                    Uri uri = Uri.fromParts("package", activity.getPackageName(), null);
                    intent.setData(uri);
                    activity.startActivityForResult(intent, REQUEST_MANAGE_STORAGE);
                } catch (Exception e) {
                    // Fallback to general settings if the specific intent fails
                    Intent intent = new Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION);
                    activity.startActivityForResult(intent, REQUEST_MANAGE_STORAGE);
                }
            }
        } else {
            // Legacy permissions for Android 10 and below
            String[] permissions = {
                Manifest.permission.WRITE_EXTERNAL_STORAGE,
                Manifest.permission.READ_EXTERNAL_STORAGE
            };

            ActivityCompat.requestPermissions(activity, permissions, REQUEST_EXTERNAL_STORAGE);
        }
    }

    /**
     * Check if storage permissions are granted
     */
    public static boolean hasStoragePermissions(Activity activity) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            return Environment.isExternalStorageManager();
        } else {
            int write = ContextCompat.checkSelfPermission(activity,
                Manifest.permission.WRITE_EXTERNAL_STORAGE);
            int read = ContextCompat.checkSelfPermission(activity,
                Manifest.permission.READ_EXTERNAL_STORAGE);
            return write == PackageManager.PERMISSION_GRANTED &&
                   read == PackageManager.PERMISSION_GRANTED;
        }
    }
}
