#!/bin/bash

# اسکریپت راه‌اندازی ربات هوشمند

# تنظیم رنگ‌ها برای خروجی
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}در حال راه‌اندازی ربات هوشمند تحلیل ارز دیجیتال...${NC}"

# بررسی وجود فایل PID
if [ -f "smart_ai_scheduler.pid" ]; then
    PID=$(cat smart_ai_scheduler.pid)
    if ps -p $PID > /dev/null; then
        echo -e "${RED}ربات هوشمند قبلاً راه‌اندازی شده و در حال اجرا است (PID: $PID)${NC}"
        echo -e "${YELLOW}برای راه‌اندازی مجدد، ابتدا ربات را با اجرای اسکریپت stop_smart_robot.sh متوقف کنید.${NC}"
        exit 1
    else
        echo -e "${YELLOW}فایل PID قدیمی یافت شد اما فرآیند مربوطه در حال اجرا نیست. در حال پاکسازی...${NC}"
        rm smart_ai_scheduler.pid
    fi
fi

# شروع اجرای اسکریپت زمان‌بندی در پس‌زمینه
echo -e "${YELLOW}در حال شروع زمان‌بندی ربات هوشمند در پس‌زمینه...${NC}"
nohup python smart_ai_scheduler.py > smart_ai_scheduler.log 2>&1 &

# بررسی موفقیت‌آمیز بودن راه‌اندازی
sleep 2
if [ -f "smart_ai_scheduler.pid" ]; then
    PID=$(cat smart_ai_scheduler.pid)
    if ps -p $PID > /dev/null; then
        echo -e "${GREEN}ربات هوشمند با موفقیت راه‌اندازی شد!${NC}"
        echo -e "${GREEN}شناسه فرآیند (PID): $PID${NC}"
        echo -e "${YELLOW}لاگ‌های ربات در فایل smart_ai_scheduler.log ذخیره می‌شوند.${NC}"
        echo -e "${YELLOW}برای مشاهده لاگ‌ها، می‌توانید از دستور زیر استفاده کنید:${NC}"
        echo -e "${YELLOW}  tail -f smart_ai_scheduler.log${NC}"
        echo -e "${YELLOW}برای توقف ربات، از دستور زیر استفاده کنید:${NC}"
        echo -e "${YELLOW}  ./stop_smart_robot.sh${NC}"
        exit 0
    fi
fi

echo -e "${RED}راه‌اندازی ربات هوشمند با خطا مواجه شد. لطفاً لاگ‌ها را بررسی کنید.${NC}"
exit 1
