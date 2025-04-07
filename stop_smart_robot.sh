#!/bin/bash

# اسکریپت توقف ربات هوشمند

# تنظیم رنگ‌ها برای خروجی
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}در حال توقف ربات هوشمند تحلیل ارز دیجیتال...${NC}"

# بررسی وجود فایل PID
if [ ! -f "smart_ai_scheduler.pid" ]; then
    echo -e "${RED}فایل PID ربات هوشمند یافت نشد. به نظر می‌رسد ربات در حال اجرا نیست.${NC}"
    exit 1
fi

# خواندن PID
PID=$(cat smart_ai_scheduler.pid)

# بررسی وجود فرآیند
if ! ps -p $PID > /dev/null; then
    echo -e "${YELLOW}فرآیند با شناسه $PID یافت نشد. در حال پاکسازی فایل PID...${NC}"
    rm smart_ai_scheduler.pid
    exit 1
fi

# توقف فرآیند
echo -e "${YELLOW}در حال توقف فرآیند با شناسه $PID...${NC}"
kill $PID

# بررسی موفقیت‌آمیز بودن توقف
sleep 2
if ps -p $PID > /dev/null; then
    echo -e "${RED}توقف ربات با خطا مواجه شد. در حال اجبار به توقف...${NC}"
    kill -9 $PID
    sleep 1
fi

# حذف فایل PID
rm smart_ai_scheduler.pid

echo -e "${GREEN}ربات هوشمند با موفقیت متوقف شد.${NC}"
exit 0
