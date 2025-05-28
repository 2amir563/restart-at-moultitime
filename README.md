# restart-at-moultitime
برای ریستارت سرور در زمان مشخص خودم درست کردم این کد را


Install the Script:
Run the following command on your Linux system

```
sudo bash -c '
    set -e;
    SCRIPT_URL="https://raw.githubusercontent.com/2amir563/restart-at-moultitime/refs/heads/main/restart_scheduler.py";
    INSTALL_DIR="/usr/local/bin";
    SCRIPT_NAME_IN_PATH="restart_scheduler";
    TEMP_DOWNLOAD_FILE="/tmp/restart_scheduler_temp.py";
    FINAL_SCRIPT_PATH="$INSTALL_DIR/$SCRIPT_NAME_IN_PATH";

    echo "INFO: Downloading restart_scheduler script...";
    if curl -fsSL "$SCRIPT_URL" -o "$TEMP_DOWNLOAD_FILE"; then
        echo "INFO: Download successful to $TEMP_DOWNLOAD_FILE.";
    else
        echo "ERROR: Download failed. Please check the URL and your internet connection." >&2;
        exit 1;
    fi;

    echo "INFO: Installing script to $FINAL_SCRIPT_PATH...";
    if mv "$TEMP_DOWNLOAD_FILE" "$FINAL_SCRIPT_PATH"; then
        echo "INFO: Script moved to $FINAL_SCRIPT_PATH.";
    else
        echo "ERROR: Failed to move script to $FINAL_SCRIPT_PATH. Check permissions for $INSTALL_DIR." >&2;
        # Clean up temp file if it still exists and mv failed
        if [ -f "$TEMP_DOWNLOAD_FILE" ]; then rm "$TEMP_DOWNLOAD_FILE"; fi;
        exit 1;
    fi;

    echo "INFO: Making script executable...";
    if chmod +x "$FINAL_SCRIPT_PATH"; then
        echo "INFO: Script is now executable.";
    else
        echo "ERROR: Failed to make script executable. Check permissions." >&2;
        exit 1;
    fi;

    echo "INFO: Setup complete. Running the script ($FINAL_SCRIPT_PATH)...";
    "$FINAL_SCRIPT_PATH";
    echo "INFO: Script execution finished or has been handed over to the script itself.";
'
```

Run the Script:
After setup, simply run


```
restart_scheduler
```

This displays the menu:
```
Please select an option:
1. Hourly
2. Daily
3. Every few days
4. Show current settings
5. Clear scheduled restarts
6. Uninstall script
7. Exit
```


.....................................................................................................................................

### 服务器

```
1
```


..............................................................


بنابراین، دستور پیشنهادی:

bash

sudo apt-get update && sudo apt-get install -y git python3-pip && pip3 install --break-system-packages python-crontab && ( [ -d ~/restart-at-moultitime ] && cd ~/restart-at-moultitime && git pull origin main || git clone https://github.com/2amir563/restart-at-moultitime.git ) && sudo cp ~/restart-at-moultitime/restart_server.py /usr/local/bin/restart_server && sudo chmod +x /usr/local/bin/restart_server && sudo restart_server

نکات مهم:
توزیع لینوکس: این دستور برای اوبونتو/دبیان است. اگر از توزیع دیگری (مثل CentOS، Fedora، یا Arch) استفاده می‌کنید، لطفاً خروجی cat /etc/os-release را به اشتراک بگذارید تا دستور متناسب را ارائه کنم. برای مثال:
CentOS/RHEL:
bash

sudo yum install -y git python3-pip && pip3 install --break-system-packages python-crontab && ( [ -d ~/restart-at-moultitime ] && cd ~/restart-at-moultitime && git pull origin main || git clone https://github.com/2amir563/restart-at-moultitime.git ) && sudo cp ~/restart-at-moultitime/restart_server.py /usr/local/bin/restart_server && sudo chmod +x /usr/local/bin/restart_server && sudo restart_server


Fedora:
bash

sudo dnf install -y git python3-pip && pip3 install --break-system-packages python-crontab && ( [ -d ~/restart-at-moultitime ] && cd ~/restart-at-moultitime && git pull origin main || git clone https://github.com/2amir563/restart-at-moultitime.git ) && sudo cp ~/restart-at-moultitime/restart_server.py /usr/local/bin/restart_server && sudo chmod +x /usr/local/bin/restart_server && sudo restart_server

Arch Linux:
bash

sudo pacman -S --noconfirm git python-pip && pip3 install --break-system-packages python-crontab && ( [ -d ~/restart-at-moultitime ] && cd ~/restart-at-moultitime && git pull origin main || git clone https://github.com/2amir563/restart-at-moultitime.git ) && sudo cp ~/restart-at-moultitime/restart_server.py /usr/local/bin/restart_server && sudo chmod +x /usr/local/bin/restart_server && sudo restart_server
اجرای مجدد: پس از اجرای دستور اولیه، برای اجرای دوباره اسکریپت از هر دایرکتوری، کافی است:
bash

sudo restart_server
حذف اسکریپت: برای حذف کامل اسکریپت و اثرات آن، از گزینه 5 داخل اسکریپت (sudo restart_server و انتخاب 5) یا دستور دستی زیر استفاده کنید:
bash

sudo crontab -u root -r && sudo rm -f /usr/local/bin/restart_server && sudo rm -f /var/log/server_restart.log && rm -rf ~/restart-at-moultitime
(توجه: این دستور تمام cron jobهای کاربر root را حذف می‌کند. اگر می‌خواهید فقط cron jobهای مربوط به اسکریپت حذف شوند، از گزینه 5 استفاده کنید.)
بررسی: برای اطمینان از نصب و تنظیمات:
bash

sudo crontab -l  # بررسی cron jobها
cat /var/log/server_restart.log  # بررسی لاگ‌ها
در صورت بروز خطا:
اگر با خطای دیگری مواجه شدید (مثلاً مشکلات مجوز یا نصب)، متن خطا را به اشتراک بگذارید. همچنین، اگر توزیع لینوکس شما مشخص نیست، خروجی cat /etc/os-release را ارائه دهید تا دستور را دقیق‌تر کنم.

............................................................................................................................................




اجرای اولیه اسکریپت:

sudo apt-get update && sudo apt-get install -y git python3-pip && pip3 install --break-system-packages python-crontab && ( [ -d ~/restart-at-moultitime ] && cd ~/restart-at-moultitime && git pull origin main || git clone https://github.com/2amir563/restart-at-moultitime.git ) && sudo cp ~/restart-at-moultitime/restart_server.py /usr/local/bin/restart_server && sudo chmod +x /usr/local/bin/restart_server && sudo restart_server



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
