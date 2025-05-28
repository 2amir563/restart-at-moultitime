# restart-at-moultitime
برای ریستارت سرور در زمان مشخص خودم درست کردم این کد را
اجرای اولیه اسکریپت:
sudo apt-get update && sudo apt-get install -y git python3-pip && pip3 install python-crontab && git clone https://github.com/2amir563/restart-at-moultitime.git && sudo cp restart-at-moultitime/restart_server.py /usr/local/bin/restart_server && sudo chmod +x /usr/local/bin/restart_server && sudo restart_server

اجرای مجدد اسکریپت:
پس از نصب اولیه، برای اجرای دوباره اسکریپت از هر دایرکتوری، کافی است این دستور را اجرا کنید:


sudo restart_server


دستور یک‌خطی برای حذف اسکریپت (اوبونتو/دبیان):

sudo crontab -u root -r && sudo rm -f /usr/local/bin/restart_server && sudo rm -f /var/log/server_restart.log && rm -rf ~/restart-at-moultitime


دستورات برای توزیع‌های دیگر:
اگر از توزیعی غیر از اوبونتو/دبیان استفاده می‌کنید:

CentOS/RHEL:
sudo yum install -y git python3-pip && pip3 install python-crontab && git clone https://github.com/2amir563/restart-at-moultitime.git && sudo cp restart-at-moultitime/restart_server.py /usr/local/bin/restart_server && sudo chmod +x /usr/local/bin/restart_server && sudo restart_server


Fedora:

sudo dnf install -y git python3-pip && pip3 install python-crontab && git clone https://github.com/2amir563/restart-at-moultitime.git && sudo cp restart-at-moultitime/restart_server.py /usr/local/bin/restart_server && sudo chmod +x /usr/local/bin/restart_server && sudo restart_server


Arch Linux:
sudo pacman -S --noconfirm git python-pip && pip3 install python-crontab && git clone https://github.com/2amir563/restart-at-moultitime.git && sudo cp restart-at-moultitime/restart_server.py /usr/local/bin/restart_server && sudo chmod +x /usr/local/bin/restart_server && sudo restart_server


...................................................................................................











sudo apt-get update && sudo apt-get install -y git python3-pip && pip3 install python-crontab && git clone https://github.com/2amir563/restart-at-moultitime.git && cd restart-at-moultitime && sudo python3 restart_server.py


دستور یک‌خطی برای پاک کردن اسکریپت (اوبونتو/دبیان):

sudo crontab -u root -r && sudo rm -rf /var/log/server_restart.log && cd ~ && rm -rf restart-at-moultitime


فایل را با نام restart_server.py ذخیره کنید.
با دسترسی root اجرا کنید:
text

سپس مخزن را از گیت‌هاب کلون کنید:

git clone https://github.com/2amir563/restart-at-moultitime.git
cd restart-at-moultitime



sudo python3 restart_server.py

ورودی‌ها:
نوع دوره (۱: ساعتی، ۲: روزانه، ۳: چند روز یک‌بار).
اگر چند روز یک‌بار انتخاب شود، تعداد روزها را وارد کنید.
ساعت به وقت تهران (مثال: 14:30).
بررسی لاگ‌ها:
لاگ‌ها در /var/log/server_restart.log ذخیره می‌شوند. برای مشاهده:
text

cat /var/log/server_restart.log

Server Restart Scheduler

This Python script schedules a Linux server restart at a specified time in the Tehran timezone using cron. It automatically checks and installs cron if not present.

Prerequisites





Python 3



python-crontab package (pip install python-crontab)



Root access on the Linux server



Supported distributions: Debian/Ubuntu, CentOS/RHEL, Fedora, Arch Linux

Usage





Save the script as restart_server.py.



Run the script with root privileges:

sudo python3 restart_server.py



Follow the prompts to select the restart period (hourly, daily, or every few days) and specify the time in Tehran timezone (e.g., 14:30).

Logs





Logs are saved in /var/log/server_restart.log.



View logs with:

cat /var/log/server_restart.log

Notes





The script sets up a cron job to restart the server using /sbin/shutdown -r now.



To view the scheduled cron job:

sudo crontab -l



To remove the cron job, edit the crontab:

sudo crontab -e

and delete the line with the server_restart comment.
