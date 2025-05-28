#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import datetime
import sys
import re

# Unique identifier for cron jobs created by this script
CRON_COMMENT = "#restart_scheduler_job_by_script"

# Determine the name the script was executed with for display purposes
try:
    # sys.argv[0] is the name/path used to invoke the script
    # os.path.basename gives just the script name part
    # If sys.argv or sys.argv[0] is empty/None, fallback to __file__
    EXECUTED_SCRIPT_NAME = os.path.basename(sys.argv[0] if sys.argv and sys.argv[0] else __file__)
except Exception:
    EXECUTED_SCRIPT_NAME = "restart_scheduler.py" # A sensible fallback

# ANSI color codes for better terminal output
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def check_root():
    """Checks if the script is run as root."""
    if os.geteuid() != 0:
        print(f"{FAIL}This script requires root privileges to manage crontab and itself.{ENDC}")
        # Use EXECUTED_SCRIPT_NAME for more accurate instruction
        script_call_name = EXECUTED_SCRIPT_NAME.replace('.py', '') if '.py' in EXECUTED_SCRIPT_NAME.lower() else EXECUTED_SCRIPT_NAME
        print(f"Please run with '{BOLD}sudo python3 {EXECUTED_SCRIPT_NAME}{ENDC}' or if installed in PATH '{BOLD}sudo {script_call_name}{ENDC}'.")
        sys.exit(1)

def get_current_crontab():
    """Gets the current user's crontab content."""
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return result.stdout
        elif "no crontab for" in result.stderr.lower() or result.stdout == "":
            return ""
        else:
            # Only print warning if stderr has content beyond "no crontab for"
            if result.stderr and "no crontab for" not in result.stderr.lower():
                 print(f"{WARNING}Warning while reading crontab: {result.stderr.strip()}{ENDC}")
            return ""
    except FileNotFoundError:
        print(f"{FAIL}Command 'crontab' not found. Is it installed?{ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{FAIL}Unknown error while reading crontab: {e}{ENDC}")
        sys.exit(1)

def set_crontab(content):
    """Sets the user's crontab content."""
    if not content.strip():
        try:
            subprocess.run(['crontab', '-r'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as e:
            # If 'no crontab for' is the error, it's effectively cleared/empty.
            if e.stderr and "no crontab for" not in e.stderr.decode().lower():
                print(f"{FAIL}Error trying to clear crontab (it might have been already empty): {e.stderr.decode().strip()}{ENDC}")
                # return False # Still, the state is 'empty', so perhaps true is better.
            return True # Treat as success if crontab is now effectively empty.
    try:
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True, encoding='utf-8')
        stdout, stderr = process.communicate(input=content)
        if process.returncode == 0:
            return True
        else:
            print(f"{FAIL}Error setting crontab: {stderr or stdout or 'Unknown error'}{ENDC}")
            return False
    except FileNotFoundError:
        print(f"{FAIL}Command 'crontab' not found. Is it installed?{ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{FAIL}Unknown error while setting crontab: {e}{ENDC}")
        sys.exit(1)

def remove_all_script_cron_jobs(inform_user=True):
    """Removes all cron jobs previously set by this script.
    Returns:
        - Number of jobs actually removed (>=0) on success.
        - -1 on failure to set/modify crontab.
    """
    current_crontab = get_current_crontab()
    lines = current_crontab.splitlines()

    jobs_to_remove_lines = [line for line in lines if CRON_COMMENT in line]
    num_jobs_found = len(jobs_to_remove_lines)

    if num_jobs_found == 0:
        if inform_user:
            print(f"{OKBLUE}ℹ️ No restart tasks set by this script were found in crontab.{ENDC}")
        return 0 # 0 jobs existed, 0 removed, operation successful

    new_lines = [line for line in lines if CRON_COMMENT not in line]
    new_crontab_content = "\n".join(new_lines)
    if new_lines:
        new_crontab_content += "\n"
    else: # If all lines were script lines, ensure content is empty for crontab -r behavior
        new_crontab_content = ""


    if set_crontab(new_crontab_content):
        if inform_user:
            print(f"{OKGREEN}✅ Successfully cleared {num_jobs_found} previously set restart task(s) from crontab.{ENDC}")
        return num_jobs_found # Number of jobs removed
    else:
        if inform_user:
            # set_crontab would have printed specific errors
            print(f"{FAIL}⚠️ Failed to update crontab to remove tasks.{ENDC}")
        return -1 # Indicates failure

def add_cron_job(schedule_expression, job_description):
    """Adds a new cron job for restarting the system, after clearing old ones from this script."""
    # remove_all_script_cron_jobs returns -1 on failure, >=0 on success (including 0 found)
    clear_status = remove_all_script_cron_jobs(inform_user=False)
    if clear_status == -1 :
        print(f"{FAIL}⚠️ Could not clear previous tasks due to an error. New task not added.{ENDC}")
        return

    current_crontab = get_current_crontab()
    lines = current_crontab.splitlines()

    reboot_paths = ["/sbin/reboot", "/usr/sbin/reboot", "/bin/reboot", "/usr/bin/reboot"]
    reboot_command_to_use = None
    for path in reboot_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            reboot_command_to_use = path
            break

    if not reboot_command_to_use:
        shutdown_paths = ["/sbin/shutdown", "/usr/sbin/shutdown", "/bin/shutdown", "/usr/bin/shutdown"]
        shutdown_command_base = None
        for path in shutdown_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                shutdown_command_base = path
                break
        if shutdown_command_base:
            reboot_command_to_use = f"{shutdown_command_base} -r now"
        else:
            print(f"{FAIL}⚠️ No valid command for restart (reboot or shutdown) found. Please check the correct path.{ENDC}")
            print(f"{FAIL}Cannot set restart task.{ENDC}")
            return

    new_job = f"{schedule_expression} {reboot_command_to_use} {CRON_COMMENT} ({job_description})"
    lines.append(new_job)

    new_crontab_content = "\n".join(lines)
    if lines:
        new_crontab_content += "\n"

    if set_crontab(new_crontab_content):
        print(f"{OKGREEN}✅ Restart task successfully set for '{job_description}'.{ENDC}")
        print(f"   Cron schedule: {BOLD}{schedule_expression}{ENDC}")
    else:
        print(f"{FAIL}⚠️ Error setting new crontab task.{ENDC}")

def get_script_cron_jobs():
    """Gets cron jobs set by this script."""
    current_crontab = get_current_crontab()
    return [line for line in current_crontab.splitlines() if CRON_COMMENT in line and line.strip()]

def display_current_time():
    """Displays the current system time in a formatted way."""
    now = datetime.datetime.now()
    day_en = now.strftime("%A")

    print(f"\n{OKCYAN}╔══════════════════════════════════════╗{ENDC}")
    print(f"{OKCYAN}║    {BOLD}{HEADER}Current System Time & Date{ENDC}      {OKCYAN}║{ENDC}")
    print(f"{OKCYAN}╠══════════════════════════════════════╣{ENDC}")
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
    print(f"{OKCYAN}║  {BOLD}{OKGREEN}Time:      {time_str}{ENDC}               {OKCYAN}║{ENDC}")
    print(f"{OKCYAN}║  {BOLD}{OKBLUE}Date:      {date_str}{ENDC}               {OKCYAN}║{ENDC}")
    print(f"{OKCYAN}║  {BOLD}{OKBLUE}Day:       {day_en.center(18)}{ENDC}  {OKCYAN}║{ENDC}")
    print(f"{OKCYAN}╚══════════════════════════════════════╝{ENDC}\n")

def get_valid_time_input():
    """Gets HH:MM time input from user and validates it."""
    while True:
        try:
            time_str = input(f"Please enter the time in HH:MM format (e.g., 14:30 or 08:05): ").strip()
            match = re.fullmatch(r"([01]?[0-9]|2[0-3]):([0-5][0-9])", time_str)
            if match:
                hour, minute = match.groups()
                return f"{int(hour):02d}", f"{int(minute):02d}"
            else:
                print(f"{WARNING}Invalid time format. Please use HH:MM (e.g., 08:00 or 23:59).{ENDC}")
        except ValueError:
            print(f"{WARNING}Invalid input. Please use numbers for hour and minute.{ENDC}")

def handle_interval_restart(): # Renamed from handle_hourly_restart
    print(f"\n{UNDERLINE}Setting up interval restart...{ENDC}")

    n_hours = 0
    while True:
        try:
            n_hours_str = input("Restart every how many hours? (e.g., 4 for every 4 hours, 1-24): ").strip()
            if not n_hours_str.isdigit():
                print(f"{WARNING}Invalid input. Please enter a number.{ENDC}")
                continue
            n_hours = int(n_hours_str)
            if 1 <= n_hours <= 24:
                break
            else:
                print(f"{WARNING}Number of hours must be between 1 and 24.{ENDC}")
        except ValueError:
            print(f"{WARNING}Invalid input. Please enter a whole number.{ENDC}")

    print("From what time should the first restart in the interval begin?")
    start_hour_str, start_minute_str = get_valid_time_input()

    hours_to_schedule = set()
    h = int(start_hour_str)
    for _ in range(24): # Iterate at most 24 times to find all unique hours in the sequence
        if h not in hours_to_schedule:
            hours_to_schedule.add(h)
            h = (h + n_hours) % 24
        else: # Cycle detected
            break
    if not hours_to_schedule: # Should only happen if N_hours was invalid, but for safety.
         hours_to_schedule.add(int(start_hour_str))


    sorted_hour_list = sorted(list(hours_to_schedule))
    hour_string = ",".join(map(str, sorted_hour_list))

    cron_schedule = f"{start_minute_str} {hour_string} * * *"
    job_description = f"Every {n_hours} hours, starting at {start_hour_str}:{start_minute_str}"

    add_cron_job(cron_schedule, job_description)

def handle_daily_restart():
    print(f"\n{UNDERLINE}Setting up daily restart...{ENDC}")
    print("At what time should the daily restart occur?")
    hour, minute = get_valid_time_input()
    add_cron_job(f"{minute} {hour} * * *", f"Daily at {hour}:{minute}")

def handle_every_few_days_restart():
    print(f"\n{UNDERLINE}Setting up restart every few days...{ENDC}")
    while True:
        try:
            days_str = input("Restart every how many days? (e.g., 3 for every 3 days): ").strip()
            if not days_str.isdigit():
                print(f"{WARNING}Invalid input. Please enter a number.{ENDC}")
                continue
            days = int(days_str)
            if days > 0:
                break
            else:
                print(f"{WARNING}Number of days must be a positive integer greater than zero.{ENDC}")
        except ValueError:
            print(f"{WARNING}Invalid input. Please enter a number.{ENDC}")
    print(f"At what time should the restart occur every {days} days?")
    hour, minute = get_valid_time_input()
    add_cron_job(f"{minute} {hour} */{days} * *", f"Every {days} days at {hour}:{minute}")

def handle_show_settings():
    print(f"\n{UNDERLINE}Displaying current restart settings...{ENDC}")
    jobs = get_script_cron_jobs()
    if jobs:
        print(f"{OKGREEN}Restart tasks scheduled by this script:{ENDC}")
        for job in jobs:
            match_desc = re.search(r'\(([^)]+)\)$', job)
            desc = match_desc.group(1) if match_desc else "No description"
            cron_part_match = re.match(r'([^#]+)', job)
            cron_part = cron_part_match.group(1).strip() if cron_part_match else "Scheduling undefined"
            print(f"  - {BOLD}{cron_part}{ENDC} ({desc})")
    else:
        print(f"{OKBLUE}ℹ️ No restart settings found by this script in crontab.{ENDC}")

def handle_clear_settings():
    print(f"\n{UNDERLINE}Clearing previous restart settings (keeps script file)...{ENDC}")
    remove_all_script_cron_jobs(inform_user=True)

def handle_uninstall_script():
    print(f"\n{UNDERLINE}Uninstall script and settings...{ENDC}")

    status_or_count = remove_all_script_cron_jobs(inform_user=True)

    if status_or_count != -1: # Cron jobs cleared successfully or none existed
        # Message about cron jobs already printed by remove_all_script_cron_jobs

        script_to_delete_path = ""
        try:
            # Determine the path of the script being executed
            # sys.argv[0] is usually the most reliable for how the script was invoked
            if sys.argv and sys.argv[0] and os.path.exists(sys.argv[0]):
                 script_to_delete_path = os.path.abspath(sys.argv[0])
            # Fallback to __file__ if sys.argv[0] is not usable or doesn't exist (e.g. embedded interpreter)
            elif os.path.exists(__file__):
                 script_to_delete_path = os.path.abspath(__file__)
            else:
                # This case should be rare if the script is running.
                raise FileNotFoundError("Script path could not be reliably determined.")

        except Exception as e:
            print(f"{FAIL}\nCould not determine the path of the currently running script: {e}{ENDC}")
            print(f"{OKBLUE}Skipping self-deletion. Please remove script files manually.{ENDC}")
            print(f"  - You may need to check common installation paths like: {BOLD}/usr/local/bin/restart_scheduler{ENDC}")
            return # Exit this function, user will go back to menu

        if not os.path.isfile(script_to_delete_path): # Check if it's a file and not a directory
            print(f"{WARNING}\nThe determined script path ({script_to_delete_path}) is not a file or seems to no longer exist. Skipping deletion.{ENDC}")
            print(f"{OKBLUE}Please remove script files manually if they exist elsewhere.{ENDC}")
            print(f"  - Check common installation paths like: {BOLD}/usr/local/bin/restart_scheduler{ENDC}")
            return

        print(f"\n{WARNING}You are about to PERMANENTLY DELETE the script file itself:{ENDC}")
        print(f"  Script file: {BOLD}{script_to_delete_path}{ENDC}")

        confirm = input(f"{OKCYAN}Are you sure you want to delete this script file? (yes/no): {ENDC}").strip().lower()

        if confirm == 'yes':
            try:
                os.remove(script_to_delete_path)
                print(f"{OKGREEN}✅ Script file '{script_to_delete_path}' has been successfully deleted.{ENDC}")

                # Advise about other potential copies, especially the one in /usr/local/bin if different.
                common_install_name = "restart_scheduler" # Default name used in installation instructions
                common_install_path = f"/usr/local/bin/{common_install_name}"

                if os.path.abspath(script_to_delete_path) == os.path.abspath(common_install_path):
                    print(f"{OKBLUE}This appears to be the installed version at '{common_install_path}'.{ENDC}")
                elif os.path.exists(common_install_path):
                     print(f"{WARNING}Note: If you installed a copy to '{common_install_path}', you may need to delete it manually as well.{ENDC}")

                print(f"\n{OKGREEN}Uninstallation process complete (tasks cleared and this script file deleted).{ENDC}")
                print(f"{OKGREEN}Exiting program now.{ENDC}")
                sys.exit(0) # Exit the script as it has deleted itself

            except OSError as e:
                print(f"{FAIL}⚠️ Error deleting script file '{script_to_delete_path}': {e}{ENDC}")
                print(f"{OKBLUE}You may need to delete it manually. Scheduled tasks (if any) remain cleared.{ENDC}")
        else:
            print(f"{OKBLUE}Script file deletion cancelled by user.{ENDC}")
            print(f"Scheduled tasks (if any) remain cleared. You can delete the script file manually if you wish:")
            print(f"  - Script file: {BOLD}{script_to_delete_path}{ENDC}")
            common_install_name = "restart_scheduler"
            common_install_path = f"/usr/local/bin/{common_install_name}"
            if os.path.abspath(script_to_delete_path) != os.path.abspath(common_install_path):
                print(f"  - Also consider checking common installation paths like: {BOLD}{common_install_path}{ENDC}")
    else: # status_or_count == -1 (failure clearing cron jobs)
        # Error message already printed by remove_all_script_cron_jobs or set_crontab
        print(f"{FAIL}Could not complete the uninstallation of scheduled settings due to an error in crontab modification.{ENDC}")
        print(f"{FAIL}Script file has NOT been deleted.{ENDC}")


def display_menu_and_get_choice():
    """Displays the main menu and gets the user's choice."""
    print(f"{HEADER}Please select an option:{ENDC}")
    options = [
        "Interval Restart (every N hours from a start time)",
        "Daily Restart (at a specific time)",
        "Restart Every Few Days (at a specific time)",
        "Show Current Restart Settings",
        "Clear Previous Restart Settings (keeps script file)",
        "Uninstall (clears settings AND deletes this script file)", # Updated menu text
        "Exit"
    ]
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        choice = input(f"{OKCYAN}Your choice (1-{len(options)}): {ENDC}").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return choice
        else:
            print(f"{WARNING}Invalid choice. Please enter a number between 1 and {len(options)}.{ENDC}")


def print_installation_instructions():
    """Prints script installation instructions for global execution."""
    # Use EXECUTED_SCRIPT_NAME for consistency in example commands
    print(f"{BOLD}{OKGREEN}Welcome to the System Restart Scheduler Script!{ENDC}")
    print("=" * 60)
    print(f"Guide to run this script from any path (without 'python3' prefix):")
    print(f"  1. Copy the script to a directory in your PATH, e.g., /usr/local/bin:")
    print(f"     {BOLD}sudo cp {EXECUTED_SCRIPT_NAME} /usr/local/bin/restart_scheduler{ENDC}")
    print(f"     (You can rename 'restart_scheduler' to your preference)")
    print(f"  2. Make it executable:")
    print(f"     {BOLD}sudo chmod +x /usr/local/bin/restart_scheduler{ENDC}")
    print(f"  Now you can run the script from anywhere using: '{BOLD}sudo restart_scheduler{ENDC}'")
    print("=" * 60)

def main():
    """Main function to run the script."""
    check_root()
    clear_screen()
    print_installation_instructions()

    actions = {
        '1': handle_interval_restart,
        '2': handle_daily_restart,
        '3': handle_every_few_days_restart,
        '4': handle_show_settings,
        '5': handle_clear_settings,      # This only clears cron
        '6': handle_uninstall_script,  # This now attempts to delete script file too
    }

    while True:
        display_current_time()
        choice = display_menu_and_get_choice()

        if choice in actions:
            actions[choice]()
            # If handle_uninstall_script was called and successful, sys.exit(0) would have ended the script.
            # Otherwise, or for other actions, the loop continues.
        elif choice == str(len(actions) + 1): # Exit option
            print(f"{OKGREEN}Exiting program.{ENDC}")
            break

        # This input will not be reached if sys.exit(0) was called in handle_uninstall_script.
        input(f"\n{OKBLUE}--- Press Enter to return to the menu ---{ENDC}")
        clear_screen()

if __name__ == "__main__":
    main()
