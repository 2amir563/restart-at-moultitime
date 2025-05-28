# restart-at-moultitime
برای ریستارت سرور در زمان مشخص خودم درست کردم این کد را
اجرای اسکریپت:

sudo apt-get update && sudo apt-get install -y git python3-pip && pip3 install python-crontab && git clone https://github.com/2amir563/restart-at-moultitime.git && cd restart-at-moultitime && sudo python3 restart_server.py


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
