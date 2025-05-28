#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import datetime
import sys
import re

# Unique identifier for cron jobs created by this script
CRON_COMMENT = "#restart_scheduler_job_by_script"
SCRIPT_NAME = os.path.basename(__file__)

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
        print(f"{FAIL}This script requires root privileges to manage crontab.{ENDC}")
        print(f"Please run with '{BOLD}sudo python3 {SCRIPT_NAME}{ENDC}' or if installed in PATH '{BOLD}sudo {SCRIPT_NAME.replace('.py', '')}{ENDC}'.")
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
            if "no crontab for" not in e.stderr.decode().lower() if e.stderr else True:
                 if e.stderr and "no crontab for" not in e.stderr.decode().lower():
                    print(f"{FAIL}Error clearing crontab: {e.stderr.decode().strip()}{ENDC}")
                    return False
            return True 
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
    """Removes all cron jobs previously set by this script."""
    current_crontab = get_current_crontab()
    lines = current_crontab.splitlines()
    original_job_count = sum(1 for line in lines if CRON_COMMENT in line)

    if original_job_count == 0:
        if inform_user:
            print(f"{OKBLUE}ℹ️ No restart tasks set by this script were found to clear.{ENDC}")
        return True

    new_lines = [line for line in lines if CRON_COMMENT not in line]
    new_crontab_content = "\n".join(new_lines)
    if new_lines: 
        new_crontab_content += "\n"
    
    if set_crontab(new_crontab_content):
        if inform_user:
            print(f"{OKGREEN}✅ All previous restart settings ({original_job_count} item(s)) were successfully cleared.{ENDC}")
        return True
    else:
        if inform_user:
            print(f"{FAIL}⚠️ Error clearing previous crontab tasks.{ENDC}")
        return False

def add_cron_job(schedule_expression, job_description):
    """Adds a new cron job for restarting the system, after clearing old ones from this script."""
    if not remove_all_script_cron_jobs(inform_user=False):
        print(f"{FAIL}⚠️ Could not clear previous tasks. New task not added.{ENDC}")
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
        print(f"{OKGREEN}✅ Restart task successfully set for '{job_description}' ({schedule_expression}).{ENDC}")
    else:
        print(f"{FAIL}⚠️ Error setting new crontab task.{ENDC}")

def get_script_cron_jobs():
    """Gets cron jobs set by this script."""
    current_crontab = get_current_crontab()
    return [line for line in current_crontab.splitlines() if CRON_COMMENT in line and line.strip()]

def display_current_time():
    """Displays the current system time in a formatted way."""
    now = datetime.datetime.now()
    day_en = now.strftime("%A") # English day name

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

def handle_hourly_restart():
    print(f"\n{UNDERLINE}Setting up hourly restart...{ENDC}")
    add_cron_job("0 * * * *", "Hourly (at the top of the hour)")

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
        print(f"{OKBLUE}ℹ️ No restart settings found by this script.{ENDC}")

def handle_clear_settings():
    print(f"\n{UNDERLINE}Clearing previous restart settings...{ENDC}")
    remove_all_script_cron_jobs(inform_user=True)

def handle_uninstall_script():
    print(f"\n{UNDERLINE}Uninstall script and settings...{ENDC}")
    if remove_all_script_cron_jobs(inform_user=True):
        print(f"\n{OKBLUE}All restart tasks scheduled by this script have been cleared.{ENDC}")
        print(f"To completely remove the script, please manually delete the script file:")
        try:
            script_full_path = os.path.abspath(__file__)
            print(f"  {BOLD}{script_full_path}{ENDC}")
            print(f"Also, if you copied it to a PATH directory (e.g., /usr/local/bin), remove that copy as well.")
        except NameError: 
             print(f"  {BOLD}Please manually delete the current script file.{ENDC}")
        print(f"\n{WARNING}Note: This option does not delete the script file itself from the disk, it only provides guidance.{ENDC}")
    else:
        print(f"{FAIL}⚠️ Error clearing crontab tasks. Full uninstallation of settings not completed.{ENDC}")

def display_menu_and_get_choice():
    """Displays the main menu and gets the user's choice."""
    print(f"{HEADER}Please select an option:{ENDC}")
    options = [
        "Hourly Restart (at the top of the hour)",
        "Daily Restart (at a specific time)",
        "Restart Every Few Days (at a specific time)",
        "Show Current Restart Settings",
        "Clear Previous Restart Settings (without uninstalling script)",
        "Uninstall Script and All Its Settings (guides manual file deletion)",
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
    print(f"{BOLD}{OKGREEN}Welcome to the System Restart Scheduler Script!{ENDC}")
    print("=" * 60) # Adjusted for potentially longer English text
    print(f"Guide to run this script from any path (without 'python3' prefix):")
    print(f"  1. Copy the script to a directory in your PATH, e.g., /usr/local/bin:")
    print(f"     {BOLD}sudo cp {SCRIPT_NAME} /usr/local/bin/restart_scheduler{ENDC}")
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
        '1': handle_hourly_restart,
        '2': handle_daily_restart,
        '3': handle_every_few_days_restart,
        '4': handle_show_settings,
        '5': handle_clear_settings,
        '6': handle_uninstall_script,
    }

    while True:
        display_current_time()
        choice = display_menu_and_get_choice()

        if choice in actions:
            actions[choice]()
        elif choice == str(len(actions) + 1): # Exit option
            print(f"{OKGREEN}Exiting program.{ENDC}")
            break
        
        if choice != str(len(actions) + 1) : 
            input(f"\n{OKBLUE}--- Press Enter to return to the menu ---{ENDC}")
            clear_screen()

if __name__ == "__main__":
    main()
