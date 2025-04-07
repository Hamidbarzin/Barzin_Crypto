#!/bin/bash

# اسکریپت توقف ربات در Replit

# تنظیم رنگ‌ها برای خروجی
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}در حال توقف ربات هوشمند...${NC}"

# بررسی وجود فایل قفل
if [ ! -f ".smart_bot_lock" ]; then
    echo -e "${RED}ربات در حال اجرا نیست.${NC}"
    exit 1
fi

# خواندن PID
if [ -f ".smart_bot_pid" ]; then
    PID=$(cat .smart_bot_pid)
    
    # توقف فرآیند
    if ps -p $PID > /dev/null; then
        echo -e "${YELLOW}در حال توقف فرآیند با شناسه $PID...${NC}"
        kill $PID
        sleep 2
        
        # بررسی آیا هنوز در حال اجراست
        if ps -p $PID > /dev/null; then
            echo -e "${RED}فرآیند هنوز در حال اجراست. در حال اجبار به توقف...${NC}"
            kill -9 $PID
        fi
    else
        echo -e "${YELLOW}فرآیند با شناسه $PID یافت نشد.${NC}"
    fi
else
    echo -e "${RED}فایل PID یافت نشد.${NC}"
fi

# حذف فایل‌های قفل و PID
rm -f .smart_bot_lock .smart_bot_pid

echo -e "${GREEN}ربات با موفقیت متوقف شد.${NC}"
