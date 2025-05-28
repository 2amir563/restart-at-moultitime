import os
import subprocess
import pytz
import logging
from crontab import CronTab
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='/var/log/server_restart.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_and_install_cron():
    """Check if cron is installed and install it if necessary"""
    try:
        # Check if crontab is installed
        subprocess.run(['which', 'crontab'], check=True, capture_output=True)
        logging.info("cron is already installed.")
        print("cron is already installed.")
        
        # Check if cron service is active
        if os.path.exists('/etc/debian_version'):
            subprocess.run(['systemctl', 'is-active', '--quiet', 'cron'], check=True)
        elif os.path.exists('/etc/redhat-release') or os.path.exists('/etc/fedora-release'):
            subprocess.run(['systemctl', 'is-active', '--quiet', 'crond'], check=True)
        elif os.path.exists('/etc/arch-release'):
            subprocess.run(['systemctl', 'is-active', '--quiet', 'cronie'], check=True)
        logging.info("cron service is active.")
        return True
    except subprocess.CalledProcessError:
        logging.warning("cron is not installed or not active. Installing...")
        print("cron is not installed or not active. Installing...")
        try:
            # Detect operating system
            if os.path.exists('/etc/debian_version'):
                # Debian/Ubuntu
                subprocess.run(['apt-get', 'update'], check=True)
                subprocess.run(['apt-get', 'install', '-y', 'cron'], check=True)
                subprocess.run(['systemctl', 'enable', 'cron'], check=True)
                subprocess.run(['systemctl', 'start', 'cron'], check=True)
            elif os.path.exists('/etc/redhat-release') or os.path.exists('/etc/fedora-release'):
                # CentOS/RHEL/Fedora
                pkg_manager = 'dnf' if os.path.exists('/etc/fedora-release') else 'yum'
                subprocess.run([pkg_manager, 'install', '-y', 'cronie'], check=True)
                subprocess.run(['systemctl', 'enable', 'crond'], check=True)
                subprocess.run(['systemctl', 'start', 'crond'], check=True)
            elif os.path.exists('/etc/arch-release'):
                # Arch Linux
                subprocess.run(['pacman', '-S', '--noconfirm', 'cronie'], check=True)
                subprocess.run(['systemctl', 'enable', 'cronie'], check=True)
                subprocess.run(['systemctl', 'start', 'cronie'], check=True)
            else:
                logging.error("Unsupported operating system (only Debian/Ubuntu, CentOS/RHEL/Fedora, or Arch supported).")
                print("Unsupported operating system (only Debian/Ubuntu, CentOS/RHEL/Fedora, or Arch supported).")
                return False
            logging.info("cron installed and activated successfully.")
            print("cron installed and activated successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Error installing cron: {e}")
            print(f"Error installing cron: {e}")
            return False

def show_current_cron():
    """Display current cron job settings for server_restart"""
    try:
        cron = CronTab(user='root')
        jobs = list(cron.find_comment('server_restart'))
        if not jobs:
            print("No server restart cron jobs are currently set.")
            logging.info("No server restart cron jobs found.")
        else:
            print("Current server restart cron job(s):")
            for job in jobs:
                print(f"- {job}")
                logging.info(f"Displayed cron job: {job}")
    except Exception as e:
        logging.error(f"Error displaying cron jobs: {e}")
        print(f"Error displaying cron jobs: {e}")

def uninstall_script():
    """Uninstall the script, cron jobs, and log file"""
    try:
        # Remove cron jobs
        cron = CronTab(user='root')
        cron.remove_all(comment='server_restart')
        cron.write()
        logging.info("All server_restart cron jobs removed.")
        print("All server restart cron jobs removed.")

        # Remove log file
        if os.path.exists('/var/log/server_restart.log'):
            os.remove('/var/log/server_restart.log')
            logging.info("Log file /var/log/server_restart.log removed.")
            print("Log file /var/log/server_restart.log removed.")

        # Remove script from /usr/local/bin
        script_path = '/usr/local/bin/restart_server'
        if os.path.exists(script_path):
            os.remove(script_path)
            logging.info(f"Script file {script_path} removed.")
            print(f"Script file {script_path} removed.")

        # Remove repository directory if it exists
        repo_dir = os.path.expanduser('~/restart-at-moultitime')
        if os.path.exists(repo_dir):
            subprocess.run(['rm', '-rf', repo_dir], check=True)
            logging.info(f"Repository directory {repo_dir} removed.")
            print(f"Repository directory {repo_dir} removed.")

        print("Script uninstalled successfully. Exiting.")
        logging.info("Script uninstalled successfully.")
        return True
    except Exception as e:
        logging.error(f"Error uninstalling script: {e}")
        print(f"Error uninstalling script: {e}")
        return False

def get_user_input():
    """Get user input for restart period and time"""
    print("Please select an option:")
    print("1. Hourly")
    print("2. Daily")
    print("3. Every few days")
    print("4. Show current settings")
    print("5. Uninstall script")
    print("6. Exit")
    choice = input("Your choice (1, 2, 3, 4, 5, or 6): ")

    while choice not in ['1', '2', '3', '4', '5', '6']:
        print("Invalid input. Please enter 1, 2, 3, 4, 5, or 6.")
        choice = input("Your choice (1, 2, 3, 4, 5, or 6): ")

    if choice == '4':
        show_current_cron()
        return None, None, None, None
    elif choice == '5':
        uninstall_script()
        return None, None, None, None
    elif choice == '6':
        print("Exiting script.")
        logging.info("User chose to exit the script.")
        return None, None, None, None

    time_input = input("Enter restart time in Tehran timezone (e.g., 14:30): ")
    try:
        restart_time = datetime.strptime(time_input, "%H:%M")
        logging.info(f"Time input: {time_input}")
    except ValueError:
        logging.error("Invalid time format.")
        print("Invalid time format. Please use HH:MM format.")
        return get_user_input()

    if choice == '3':
        days_interval = input("Restart every how many days? (e.g., 2): ")
        while not days_interval.isdigit() or int(days_interval) < 1:
            print("Please enter a valid number (greater than 0).")
            days_interval = input("Restart every how many days?: ")
        days_interval = int(days_interval)
    else:
        days_interval = None

    return choice, restart_time.hour, restart_time.minute, days_interval

def setup_cron(period_type, hour, minute, days_interval):
    """Set up cron job for server restart"""
    try:
        cron = CronTab(user='root')
        
        # Remove previous cron jobs to avoid conflicts
        cron.remove_all(comment='server_restart')
        logging.info("Previous cron jobs with comment 'server_restart' removed.")

        # Set up restart command
        job = cron.new(command='/sbin/shutdown -r now', comment='server_restart')

        # Set schedule based on period type
        if period_type == '1':  # Hourly
            job.minute.on(minute)
        elif period_type == '2':  # Daily
            job.hour.on(hour)
            job.minute.on(minute)
        elif period_type == '3':  # Every few days
            job.hour.on(hour)
            job.minute.on(minute)
            job.day.every(days_interval)

        # Set timezone to Tehran
        job.setall(f'TZ=Asia/Tehran {job}')

        # Save changes
        cron.write()
        logging.info(f"cron job scheduled for {hour:02d}:{minute:02d} Tehran time.")
        print(f"Server restart scheduled for {hour:02d}:{minute:02d} Tehran time.")
    except Exception as e:
        logging.error(f"Error setting up cron job: {e}")
        print(f"Error setting up cron job: {e}")
        return False
    return True

def main():
    """Main function"""
    if os.geteuid() != 0:
        logging.error("Script executed without root privileges.")
        print("This script must be run with root privileges. Please use sudo.")
        return

    # Check and install cron if necessary
    if not check_and_install_cron():
        logging.error("Cannot proceed because cron installation failed.")
        print("Cannot proceed because cron installation failed.")
        return

    # Get input and set up cron
    period_type, hour, minute, days_interval = get_user_input()
    if period_type is None:  # User chose to exit, uninstall, or show settings
        return
    if setup_cron(period_type, hour, minute, days_interval):
        logging.info("Script executed successfully.")
    else:
        logging.error("Error executing script.")

if __name__ == "__main__":
    main()
