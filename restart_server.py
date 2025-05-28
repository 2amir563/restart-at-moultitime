import os
import subprocess
import pytz
import logging
from crontab import CronTab
from datetime import datetime

# تنظیم لاگ‌گیری
logging.basicConfig(
    filename='/var/log/server_restart.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_and_install_cron():
    """بررسی نصب بودن cron و نصب خودکار در صورت نیاز"""
    try:
        # بررسی نصب بودن crontab
        subprocess.run(['which', 'crontab'], check=True, capture_output=True)
        logging.info("cron از قبل نصب شده است.")
        print("cron از قبل نصب شده است.")
        
        # بررسی فعال بودن سرویس cron
        if os.path.exists('/etc/debian_version'):
            subprocess.run(['systemctl', 'is-active', '--quiet', 'cron'], check=True)
        elif os.path.exists('/etc/redhat-release') or os.path.exists('/etc/fedora-release'):
            subprocess.run(['systemctl', 'is-active', '--quiet', 'crond'], check=True)
        elif os.path.exists('/etc/arch-release'):
            subprocess.run(['systemctl', 'is-active', '--quiet', 'cronie'], check=True)
        logging.info("سرویس cron فعال است.")
        return True
    except subprocess.CalledProcessError:
        logging.warning("cron نصب نیست یا فعال نیست. در حال نصب...")
        print("cron نصب نیست یا فعال نیست. در حال نصب...")
        try:
            # تشخیص نوع سیستم‌عامل
            if os.path.exists('/etc/debian_version'):
                # دبیان/اوبونتو
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
                logging.error("سیستم‌عامل پشتیبانی نمی‌شود (فقط دبیان/اوبونتو، CentOS/RHEL/Fedora، یا Arch).")
                print("سیستم‌عامل پشتیبانی نمی‌شود (فقط دبیان/اوبونتو، CentOS/RHEL/Fedora، یا Arch).")
                return False
            logging.info("cron با موفقیت نصب و فعال شد.")
            print("cron با موفقیت نصب و فعال شد.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"خطا در نصب cron: {e}")
            print(f"خطا در نصب cron: {e}")
            return False

def get_user_input():
    """دریافت ورودی از کاربر برای نوع دوره و زمان ری‌استارت"""
    print("لطفاً نوع دوره را انتخاب کنید:")
    print("1. ساعتی")
    print("2. روزانه")
    print("3. چند روز یک‌بار")
    period_type = input("انتخاب شما (1، 2 یا 3): ")

    while period_type not in ['1', '2', '3']:
        print("ورودی نامعتبر است. لطفاً 1، 2 یا 3 را وارد کنید.")
        period_type = input("انتخاب شما (1، 2 یا 3): ")

    if period_type == '3':
        days_interval = input("هر چند روز یک‌بار ری‌استارت شود؟ (مثال: 2): ")
        while not days_interval.isdigit() or int(days_interval) < 1:
            print("لطفاً یک عدد معتبر (بزرگ‌تر از 0) وارد کنید.")
            days_interval = input("هر چند روز یک‌بار ری‌استارت شود؟: ")
        days_interval = int(days_interval)
    else:
        days_interval = None

    time_input = input("ساعت ری‌استارت را به وقت تهران وارد کنید (مثال: 14:30): ")
    try:
        restart_time = datetime.strptime(time_input, "%H:%M")
        logging.info(f"ورودی زمان: {time_input}")
    except ValueError:
        logging.error("فرمت ساعت نامعتبر است.")
        print("فرمت ساعت نامعتبر است. لطفاً به فرمت HH:MM وارد کنید.")
        return get_user_input()

    return period_type, restart_time.hour, restart_time.minute, days_interval

def setup_cron(period_type, hour, minute, days_interval):
    """تنظیم cron job برای ری‌استارت سرور"""
    try:
        cron = CronTab(user='root')
        
        # حذف cron jobهای قبلی برای جلوگیری از تداخل
        cron.remove_all(comment='server_restart')
        logging.info("cron jobهای قبلی با کامنت 'server_restart' حذف شدند.")

        # تنظیم دستور ری‌استارت
        job = cron.new(command='/sbin/shutdown -r now', comment='server_restart')

        # تنظیم زمان‌بندی بر اساس نوع دوره
        if period_type == '1':  # ساعتی
            job.minute.on(minute)
        elif period_type == '2':  # روزانه
            job.hour.on(hour)
            job.minute.on(minute)
        elif period_type == '3':  # چند روز یک‌بار
            job.hour.on(hour)
            job.minute.on(minute)
            job.day.every(days_interval)

        # تنظیم منطقه زمانی به تهران
        job.setall(f'TZ=Asia/Tehran {job}')

        # ذخیره تغییرات
        cron.write()
        logging.info(f"cron job تنظیم شد برای {hour:02d}:{minute:02d} به وقت تهران.")
        print(f"ری‌استارت سرور تنظیم شد برای {hour:02d}:{minute:02d} به وقت تهران.")
    except Exception as e:
        logging.error(f"خطا در تنظیم cron job: {e}")
        print(f"خطا در تنظیم cron job: {e}")
        return False
    return True

def main():
    """تابع اصلی"""
    if os.geteuid() != 0:
        logging.error("اسکریپت بدون دسترسی root اجرا شد.")
        print("این اسکریپت باید با دسترسی root اجرا شود. لطفاً با sudo اجرا کنید.")
        return

    # بررسی و نصب cron در صورت نیاز
    if not check_and_install_cron():
        logging.error("نمی‌توان ادامه داد چون cron نصب نشد.")
        print("نمی‌توان ادامه داد چون cron نصب نشد.")
        return

    # دریافت ورودی و تنظیم cron
    period_type, hour, minute, days_interval = get_user_input()
    if setup_cron(period_type, hour, minute, days_interval):
        logging.info("اسکریپت با موفقیت اجرا شد.")
    else:
        logging.error("خطا در اجرای اسکریپت.")

if __name__ == "__main__":
    main()
