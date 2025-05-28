import os
import subprocess
import getpass
import re

SCRIPT_NAME = "restart_server_timedarkhasti.py"
CRON_COMMENT = "# RestartScript"
CRON_FILE = "/tmp/restart_cron"
ALIAS_FILE = os.path.expanduser("~/.bashrc")

def run_as_root(command):
    """Run a command with sudo if not root."""
    if os.geteuid() != 0:
        command = f"sudo {command}"
    return subprocess.run(command, shell=True, capture_output=True, text=True)

def add_cron_job(schedule):
    """Add a cron job for system reboot with a unique comment."""
    cron_line = f"{schedule} systemctl reboot {CRON_COMMENT}\n"
    with open(CRON_FILE, "w") as f:
        f.write(cron_line)
    result = run_as_root(f"crontab {CRON_FILE}")
    if result.returncode == 0:
        print("Restart scheduled successfully.")
    else:
        print(f"Error scheduling restart: {result.stderr}")

def clear_cron_jobs():
    """Remove only cron jobs added by this script."""
    result = run_as_root("crontab -l")
    if result.returncode != 0 and "no crontab" not in result.stderr:
        print(f"Error reading crontab: {result.stderr}")
        return
    lines = result.stdout.splitlines() if result.returncode == 0 else []
    new_lines = [line for line in lines if CRON_COMMENT not in line]
    with open(CRON_FILE, "w") as f:
        for line in new_lines:
            f.write(f"{line}\n")
    result = run_as_root(f"crontab {CRON_FILE}")
    if result.returncode == 0:
        print("Scheduled restarts cleared successfully.")
    else:
        print(f"Error clearing restarts: {result.stderr}")

def show_settings():
    """Display current cron jobs added by this script."""
    result = run_as_root("crontab -l")
    if result.returncode != 0 and "no crontab" not in result.stderr:
        print(f"Error reading crontab: {result.stderr}")
        return
    lines = result.stdout.splitlines() if result.returncode == 0 else []
    restart_jobs = [line for line in lines if CRON_COMMENT in line]
    if restart_jobs:
        print("Current scheduled restarts:")
        for job in restart_jobs:
            print(job.replace(CRON_COMMENT, ""))
    else:
        print("No scheduled restarts found.")

def uninstall_script():
    """Uninstall the script, cron jobs, and alias."""
    # Clear cron jobs
    clear_cron_jobs()
    # Remove script
    script_path = f"/usr/local/bin/{SCRIPT_NAME}"
    if os.path.exists(script_path):
        result = run_as_root(f"rm -f {script_path}")
        if result.returncode == 0:
            print(f"Removed {script_path}")
        else:
            print(f"Error removing script: {result.stderr}")
    # Remove alias
    if os.path.exists(ALIAS_FILE):
        with open(ALIAS_FILE, "r") as f:
            lines = f.readlines()
        new_lines = [line for line in lines if f'alias restart-script="python3 {script_path}"' not in line]
        with open(ALIAS_FILE, "w") as f:
            f.writelines(new_lines)
        run_as_root("source ~/.bashrc")
        print("Removed alias 'restart-script'. Run 'source ~/.bashrc' in your terminal to update.")
    print("Script uninstalled successfully.")

def main():
    while True:
        print("\nPlease select an option:")
        print("1. Hourly")
        print("2. Daily")
        print("3. Every few days")
        print("4. Show current settings")
        print("5. Clear scheduled restarts")
        print("6. Uninstall script")
        print("7. Exit")
        choice = input("Enter your choice (1-7): ")

        if choice == "1":
            add_cron_job("0 * * * *")  # Every hour at minute 0
        elif choice == "2":
            time = input("Enter time for daily restart (HH:MM, 24-hour format, e.g., 02:00): ")
            if re.match(r"^\d{2}:\d{2}$", time):
                hour, minute = time.split(":")
                if 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59:
                    add_cron_job(f"{minute} {hour} * * *")
                else:
                    print("Invalid time format. Use HH:MM (e.g., 02:00).")
            else:
                print("Invalid time format. Use HH:MM (e.g., 02:00).")
        elif choice == "3":
            days = input("Enter number of days between restarts (1-30): ")
            if days.isdigit() and 1 <= int(days) <= 30:
                time = input("Enter time for restart (HH:MM, 24-hour format, e.g., 02:00): ")
                if re.match(r"^\d{2}:\d{2}$", time):
                    hour, minute = time.split(":")
                    if 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59:
                        add_cron_job(f"{minute} {hour} */{days} * *")
                    else:
                        print("Invalid time format. Use HH:MM (e.g., 02:00).")
                else:
                    print("Invalid time format. Use HH:MM (e.g., 02:00).")
            else:
                print("Invalid number of days. Enter a number between 1 and 30.")
        elif choice == "4":
            show_settings()
        elif choice == "5":
            clear_cron_jobs()
        elif choice == "6":
            uninstall_script()
            break
        elif choice == "7":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    main()
