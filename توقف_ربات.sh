#!/bin/bash
# اسکریپت توقف ربات تحلیل ارزهای دیجیتال

# رنگ‌های ANSI
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# عنوان
echo -e "${YELLOW}=== توقف ربات تحلیل ارزهای دیجیتال ===${NC}"
echo

# بررسی اجرای ربات ساده
if pgrep -f "python3 simple_ai_mode.py" > /dev/null; then
    echo -e "${BLUE}در حال توقف ربات ساده...${NC}"
    pkill -f "python3 simple_ai_mode.py"
    echo -e "${GREEN}ربات ساده متوقف شد ✓${NC}"
fi

# بررسی اجرای ربات هوشمند
if pgrep -f "python3 telegram_smart_reporter.py" > /dev/null; then
    echo -e "${BLUE}در حال توقف ربات هوشمند...${NC}"
    pkill -f "python3 telegram_smart_reporter.py"
    echo -e "${GREEN}ربات هوشمند متوقف شد ✓${NC}"
fi

# بررسی اجرای زمان‌بندی خودکار
if [ -f "scheduler.pid" ]; then
    pid=$(cat scheduler.pid)
    if kill -0 $pid 2>/dev/null; then
        echo -e "${BLUE}در حال توقف زمان‌بندی خودکار...${NC}"
        kill $pid
        rm scheduler.pid
        echo -e "${GREEN}زمان‌بندی خودکار متوقف شد ✓${NC}"
    else
        echo -e "${YELLOW}فایل PID وجود دارد، اما فرآیند در حال اجرا نیست.${NC}"
        rm scheduler.pid
    fi
elif [ -f "smart_scheduler.pid" ]; then
    pid=$(cat smart_scheduler.pid)
    if kill -0 $pid 2>/dev/null; then
        echo -e "${BLUE}در حال توقف زمان‌بندی هوشمند...${NC}"
        kill $pid
        rm smart_scheduler.pid
        echo -e "${GREEN}زمان‌بندی هوشمند متوقف شد ✓${NC}"
    else
        echo -e "${YELLOW}فایل PID وجود دارد، اما فرآیند در حال اجرا نیست.${NC}"
        rm smart_scheduler.pid
    fi
else
    echo -e "${YELLOW}هیچ فرآیند زمان‌بندی در حال اجرا یافت نشد.${NC}"
fi

echo
echo -e "${GREEN}تمام فرآیندهای مرتبط با ربات تحلیل ارزهای دیجیتال متوقف شدند.${NC}"
echo -e "${BLUE}برای راه‌اندازی مجدد ربات، از اسکریپت راه‌اندازی_ربات_هوشمند.sh استفاده کنید.${NC}"
