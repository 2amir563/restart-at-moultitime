sudo bash -c '
    set -e;
    SCRIPT_URL="https://bayanbox.ir/download/1575796786760718991/restart-scheduler.py";
    INSTALL_DIR="/usr/local/bin";
    SCRIPT_NAME_IN_PATH="restart_scheduler";
    TEMP_DOWNLOAD_FILE="/tmp/restart_scheduler_temp.py";
    FINAL_SCRIPT_PATH="$INSTALL_DIR/$SCRIPT_NAME_IN_PATH";

    echo "INFO: Downloading restart_scheduler script...";
    if curl -fsSLk "$SCRIPT_URL" -o "$TEMP_DOWNLOAD_FILE"; then
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
