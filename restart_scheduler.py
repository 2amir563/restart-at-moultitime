```python
#!/usr/bin/env python3
import os
import subprocess
import getpass
import re
import datetime
import tempfile
import shutil

def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_crontab():
    try:
        result = subprocess.run(['crontab', '-u', getpass.getuser(), '-l'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""
    except Exception as e:
        print(f"Error accessing crontab: {e}")
        return ""

def clear_crontab():
    try:
        temp_file = f"/tmp/{getpass.getuser()}_crontab_{os.getpid()}"
        with open(temp_file, "w") as f:
            f.write("")
        subprocess.run(['crontab', '-u', getpass.getuser(), temp_file], check=True)
        os.remove(temp_file)
        print("Previous crontab settings cleared.")
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"Error clearing crontab: {e}")

def uninstall_script():
    try:
        clear_crontab()
        script_path = os.path.abspath(__file__)
        global_path = "/usr/local/bin/restart_scheduler"
        if os.path.exists(script_path) and script_path != global_path:
            os.remove(script_path)
            print("Script removed from current directory.")
        if os.path.exists(global_path):
            os.remove(global_path)
            print("Global command removed from /usr/local/bin.")
        if os.path.exists("/restart_scheduler.py"):
            os.remove("/restart_scheduler.py")
            print("Removed misplaced script from /restart_scheduler.py.")
        print("Script uninstalled successfully.")
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"Error uninstalling script: {e}")

def show_settings():
    cron_content = get_crontab()
    if cron_content:
        print("Current restart settings:")
        found = False
        for line in cron_content.splitlines():
            if "/sbin/reboot" in line:
                print(f" - {line}")
                found = True
        if not found:
            print("No active restart settings found in crontab.")
    else:
        print("No restart settings configured (crontab is empty).")

def validate_time(hour, minute):
    try:
        hour = int(hour)
        minute = int(minute)
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return True
        return False
    except ValueError:
        return False

def get_time_input():
    while True:
        time_input = input("Enter start time (HH:MM, e.g., 10:05): ")
        if not re.match(r"^\d{1,2}:\d{2}$", time_input):
            print("Invalid format. Use HH:MM (e.g., 10:05).")
            continue
        hour, minute = time_input.split(":")
        if validate_time(hour, minute):
            return int(hour), int(minute)
        print("Invalid time. Hour must be 0-23, minute must be 0-59.")

def set_cron_schedule(schedule, hour, minute):
    try:
        # Preserve existing crontab entries not related to reboot
        cron_content = get_crontab()
        new_cron_lines = [line for line in cron_content.splitlines() if "/sbin/reboot" not in line]
        cron_job = f"{minute} {hour} {schedule} /sbin/reboot"
        new_cron_lines.append(cron_job)
        # Write to temp file
        temp_file = f"/tmp/{getpass.getuser()}_crontab_{os.getpid()}"
        with open(temp_file, "w") as f:
            f.write("\n".join(new_cron_lines) + "\n")
        # Update crontab
        subprocess.run(['crontab', '-u', getpass.getuser(), temp_file], check=True)
        # Verify crontab was updated
        updated_cron = get_crontab()
        if cron_job in updated_cron:
            print(f"Restart scheduled: {cron_job}")
        else:
            print("Error: Crontab was not updated correctly. Check permissions or cron service.")
        os.remove(temp_file)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"Error setting crontab: {e}")

def install_global_command():
    try:
        script_path = os.path.abspath(__file__)
        global_path = "/usr/local/bin/restart_scheduler"
        if not os.path.exists(global_path) or os.path.getmtime(script_path) > os.path.getmtime(global_path):
            shutil.copy(script_path, global_path)
            os.chmod(global_path, 0o755)
            print("Global command 'restart_scheduler' installed or updated in /usr/local/bin.")
        else:
            print("Global command already up-to-date in /usr/local/bin.")
    except (OSError, shutil.Error) as e:
        print(f"Error installing global command: {e}")

def main():
    # Install global command
    install_global_command()

    # Check if crontab already has reboot settings
    cron_content = get_crontab()
    if cron_content and "/sbin/reboot" in cron_content:
        print("Existing restart settings detected:")
        show_settings()
        overwrite = input("Do you want to overwrite existing settings? (y/n): ")
        if overwrite.lower() != "y":
            print("Keeping existing settings.")

    while True:
        print(f"Current time: {get_current_time()}")
        print("Please select an option:")
        print("1. Hourly")
        print("2. Daily")
        print("3. Every few days")
        print("4. Show current settings")
        print("5. Uninstall script")
        print("6. Clear previous settings")
        print("7. Exit")
        
        choice = input("Enter your choice (1-7): ")

        if choice in ["1", "2", "3"]:
            hour, minute = get_time_input()
        
        if choice == "1":
            # For hourly, run every 4 hours starting from specified time
            hours = f"{hour},{(hour+4)%24},{(hour+8)%24},{(hour+12)%24},{(hour+16)%24},{(hour+20)%24}"
            set_cron_schedule(f"* * * *", hours, minute)
            print(f"System will restart every 4 hours starting at {hour:02d}:{minute:02d} (e.g., {hour:02d}:{minute:02d}, {(hour+4)%24:02d}:{minute:02d}, ...).")
        elif choice == "2":
            set_cron_schedule("* * *", hour, minute)
            print(f"System will restart daily at {hour:02d}:{minute:02d}.")
        elif choice == "3":
            days = input("Enter number of days (e.g., 3 for every 3 days): ")
            try:
                days = int(days)
                if days < 1:
                    raise ValueError
                set_cron_schedule(f"*/{days} * *", hour, minute)
                print(f"System will restart every {days} days at {hour:02d}:{minute:02d}.")
            except ValueError:
                print("Please enter a valid number of days.")
        elif choice == "4":
            show_settings()
        elif choice == "5":
            confirm = input("Are you sure you want to uninstall the script? (y/n): ")
            if confirm.lower() == "y":
                uninstall_script()
                break
        elif choice == "6":
            clear_crontab()
        elif choice == "7":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
```
