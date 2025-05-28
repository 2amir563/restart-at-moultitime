import os
import subprocess
import getpass

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

def set_cron_schedule(schedule):
    clear_crontab()
    cron_job = f"{schedule} /sbin/reboot\n"
    with open(f"/tmp/{getpass.getuser()}_crontab", "w") as f:
        f.write(cron_job)
    subprocess.run(['crontab', f"/tmp/{getpass.getuser()}_crontab"])
    os.remove(f"/tmp/{getpass.getuser()}_crontab")
    print(f"Restart scheduled: {schedule}")

def main():
    while True:
        print("Please select an option:")
        print("1. Hourly")
        print("2. Daily")
        print("3. Every few days")
        print("4. Show current settings")
        print("5. Uninstall script")
        print("6. Clear previous settings")
        print("7. Exit")
        
        choice = input("Enter your choice (1-7): ")

        if choice == "1":
            set_cron_schedule("0 * * * *")
            print("System will restart every hour.")
        elif choice == "2":
            set_cron_schedule("0 0 * * *")
            print("System will restart daily at midnight.")
        elif choice == "3":
            days = input("Enter number of days (e.g., 3 for every 3 days): ")
            try:
                days = int(days)
                if days < 1:
                    raise ValueError
                set_cron_schedule(f"0 0 */{days} * *")
                print(f"System will restart every {days} days.")
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
