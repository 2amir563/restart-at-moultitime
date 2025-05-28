import os
import subprocess
import getpass
import re
import datetime

def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_crontab():
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return ""

def clear_crontab():
    with open(f"/tmp/{getpass.getuser()}_crontab", "w") as f:
        f.write("")
    subprocess.run(['crontab', f"/tmp/{getpass.getuser()}_crontab"])
    os.remove(f"/tmp/{getpass.getuser()}_crontab")
    print("Previous settings cleared.")

def uninstall_script():
    clear_crontab()
    script_path = os.path.abspath(__file__)
    os.remove(script_path)
    print("Script uninstalled successfully.")

def show_settings():
    cron_content = get_crontab()
    if "reboot" in cron_content:
        print("Current settings:")
        print(cron_content)
    else:
        print("No restart settings configured.")

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
    clear_crontab()
    cron_job = f"{minute} {hour} {schedule} /sbin/reboot\n"
    with open(f"/tmp/{getpass.getuser()}_crontab", "w") as f:
        f.write(cron_job)
    subprocess.run(['crontab', f"/tmp/{getpass.getuser()}_crontab"])
    os.remove(f"/tmp/{getpass.getuser()}_crontab")
    print(f"Restart scheduled: {minute} {hour} {schedule}")

def main():
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
