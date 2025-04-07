#!/bin/bash
# اسکریپت اجرای ربات تحلیل ارزهای دیجیتال در حالت ساده

# رنگ‌های ANSI
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# عنوان
echo -e "${YELLOW}=== ربات تحلیل ارزهای دیجیتال (حالت ساده) ===${NC}"
echo

# منوی انتخاب
echo -e "${BLUE}لطفاً یکی از گزینه‌های زیر را انتخاب کنید:${NC}"
echo "1) نمای کلی بازار"
echo "2) تحلیل بیت‌کوین"
echo "3) تحلیل اتریوم"
echo "4) فرصت‌های معاملاتی"
echo "5) ارسال پیام تست"
echo "0) خروج"
echo

# دریافت انتخاب کاربر
read -p "انتخاب شما (0-5): " choice
echo

# اجرای گزینه انتخاب شده
case $choice in
    1)
        echo -e "${GREEN}در حال ارسال نمای کلی بازار...${NC}"
        python3 simple_ai_mode.py --overview
        ;;
    2)
        echo -e "${GREEN}در حال ارسال تحلیل بیت‌کوین...${NC}"
        python3 simple_ai_mode.py --coin BTC/USDT
        ;;
    3)
        echo -e "${GREEN}در حال ارسال تحلیل اتریوم...${NC}"
        python3 simple_ai_mode.py --coin ETH/USDT
        ;;
    4)
        echo -e "${GREEN}در حال ارسال فرصت‌های معاملاتی...${NC}"
        python3 simple_ai_mode.py --opportunities
        ;;
    5)
        echo -e "${GREEN}در حال ارسال پیام تست...${NC}"
        python3 simple_ai_mode.py --test
        ;;
    0)
        echo "خروج از برنامه"
        exit 0
        ;;
    *)
        echo -e "${RED}انتخاب نامعتبر!${NC}"
        exit 1
        ;;
esac

echo
echo -e "${YELLOW}توجه: پیام به تلگرام ارسال شد. برای مشاهده پیام، لطفاً تلگرام خود را بررسی کنید.${NC}"
echo -e "${BLUE}برای اطلاعات بیشتر، راهنمای استفاده را مطالعه کنید: smart_robot_guide.md${NC}"
