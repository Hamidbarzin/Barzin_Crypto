#!/bin/bash

# اسکریپت راه‌اندازی ربات در پس‌زمینه برای Replit

# تنظیم رنگ‌ها برای خروجی
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}در حال راه‌اندازی ربات هوشمند در پس‌زمینه...${NC}"

# بررسی وجود فایل قفل
if [ -f ".smart_bot_lock" ]; then
    echo -e "${RED}ربات قبلاً راه‌اندازی شده است.${NC}"
    echo -e "${YELLOW}اگر مطمئن هستید که ربات در حال اجرا نیست، فایل .smart_bot_lock را حذف کنید و دوباره تلاش کنید.${NC}"
    exit 1
fi

# ایجاد فایل قفل
touch .smart_bot_lock

# اجرای ربات در پس‌زمینه
nohup python smart_ai_scheduler.py > smart_bot_nohup.log 2>&1 &
PID=$!

echo -e "${GREEN}ربات هوشمند با شناسه فرآیند $PID شروع به کار کرد.${NC}"
echo -e "${YELLOW}لاگ‌های ربات در فایل smart_bot_nohup.log ذخیره می‌شوند.${NC}"
echo -e "${YELLOW}برای توقف ربات، از دستور زیر استفاده کنید:${NC}"
echo -e "${YELLOW}  ./stop_replit_bot.sh${NC}"

# ارسال یک پیام تست اضافی
echo -e "${YELLOW}در حال ارسال یک پیام تست...${NC}"
python -c "import simple_ai_mode; simple_ai_mode.send_test_message()"

# ذخیره PID در فایل
echo $PID > .smart_bot_pid

echo -e "${GREEN}ربات با موفقیت راه‌اندازی شد و آماده ارسال گزارش‌های دوره‌ای است.${NC}"
