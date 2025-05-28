# restart-at-moultitime
برای ریستارت سرور در زمان مشخص خودم درست کردم این کد را


Install the Script:
Run the following command on your Linux system
اجرای اولیه اسکریپت: برای نصب فقط کافی است کد زیر را تماما کپی کرده و در سیستم اجرا کنیم


```
sudo bash -c '
    set -e;
    SCRIPT_URL="https://raw.githubusercontent.com/2amir563/restart-at-moultitime/refs/heads/main/restart_scheduler.py";
    INSTALL_DIR="/usr/local/bin";
    SCRIPT_NAME_IN_PATH="restart_scheduler";
    TEMP_DOWNLOAD_FILE="/tmp/restart_scheduler_temp.py";
    FINAL_SCRIPT_PATH="$INSTALL_DIR/$SCRIPT_NAME_IN_PATH";

    echo "INFO: Downloading restart_scheduler script...";
    if curl -fsSL "$SCRIPT_URL" -o "$TEMP_DOWNLOAD_FILE"; then
        echo "INFO: Download successful to $TEMP_DOWNLOAD_FILE.";
    else
        echo "ERROR: Download failed. Please check the URL and your internet connection." >&2;
        exit 1;
    fi;

    echo "INFO: Installing script to $FINAL_SCRIPT_PATH...";
    if mv "$TEMP_DOWNLOAD_FILE" "$FINAL_SCRIPT_PATH"; then
        echo "INFO: Script moved to $FINAL_SCRIPT_PATH.";
    else
        echo "ERROR: Failed to move script to $FINAL_SCRIPT_PATH. Check permissions for $INSTALL_DIR." >&2;
        # Clean up temp file if it still exists and mv failed
        if [ -f "$TEMP_DOWNLOAD_FILE" ]; then rm "$TEMP_DOWNLOAD_FILE"; fi;
        exit 1;
    fi;

    echo "INFO: Making script executable...";
    if chmod +x "$FINAL_SCRIPT_PATH"; then
        echo "INFO: Script is now executable.";
    else
        echo "ERROR: Failed to make script executable. Check permissions." >&2;
        exit 1;
    fi;

    echo "INFO: Setup complete. Running the script ($FINAL_SCRIPT_PATH)...";
    "$FINAL_SCRIPT_PATH";
    echo "INFO: Script execution finished or has been handed over to the script itself.";
'
```

Run the Script:
After setup, simply run

اجرای مجدد: پس از اجرای دستور اولیه، برای اجرای دوباره اسکریپت از هر دایرکتوری، کافی است:


```
restart_scheduler
```

This displays the menu:


```
╔══════════════════════════════════════╗
║    Current System Time & Date      ║
╠══════════════════════════════════════╣
║  Time:      22:28:21               ║
║  Date:      2025-05-28               ║
║  Day:           Wednesday       ║
╚══════════════════════════════════════╝

Please select an option:
1. Interval Restart (every N hours from a start time)
2. Daily Restart (at a specific time)
3. Restart Every Few Days (at a specific time)
4. Show Current Restart Settings
5. Clear Previous Restart Settings (without uninstalling script)
6. Uninstall Script and All Its Settings (guides manual file deletion)
7. Exit

```

نسخه قدیم
```
Please select an option:
1. Hourly
2. Daily
3. Every few days
4. Show current settings
5. Clear scheduled restarts
6. Uninstall script
7. Exit
```


