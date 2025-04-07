#!/bin/bash
# اسکریپت نمایش قابلیت‌های هوش مصنوعی ربات

# رنگ‌های ANSI
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# عنوان
echo -e "${YELLOW}=== نمایش قابلیت‌های هوش مصنوعی ربات تحلیل ارزهای دیجیتال ===${NC}"
echo

# بررسی وجود کلید API هوش مصنوعی
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}⚠️ کلید API هوش مصنوعی تنظیم نشده است${NC}"
    echo -e "${YELLOW}برای استفاده از قابلیت‌های هوش مصنوعی، لطفاً کلید API را با دستور زیر تنظیم کنید:${NC}"
    echo -e "export OPENAI_API_KEY=\"کلید-API-شما\""
    echo
    read -p "آیا می‌خواهید بدون کلید API ادامه دهید؟ (y/n): " continue_without_key
    
    if [ "$continue_without_key" != "y" ]; then
        echo "نمایش قابلیت‌های هوش مصنوعی لغو شد"
        exit 1
    fi
    
    echo -e "${YELLOW}ادامه بدون کلید API. ممکن است برخی قابلیت‌ها کار نکنند.${NC}"
    echo
fi

# منوی انتخاب
echo -e "${BLUE}لطفاً یکی از قابلیت‌های زیر را برای نمایش انتخاب کنید:${NC}"
echo "1) تحلیل کلی بازار با هوش مصنوعی"
echo "2) تحلیل هوشمند بیت‌کوین"
echo "3) فرصت‌های معاملاتی هوشمند"
echo "4) تحلیل تأثیر اخبار بر بازار"
echo "5) ارسال گزارش کامل"
echo "6) ارسال پیام تست"
echo "0) خروج"
echo

# دریافت انتخاب کاربر
read -p "انتخاب شما (0-6): " choice
echo

# اجرای قابلیت انتخاب شده
case $choice in
    1)
        echo -e "${GREEN}در حال اجرای تحلیل کلی بازار با هوش مصنوعی...${NC}"
        python3 telegram_smart_reporter.py --overview
        ;;
    2)
        echo -e "${GREEN}در حال اجرای تحلیل هوشمند بیت‌کوین...${NC}"
        python3 telegram_smart_reporter.py --coin BTC/USDT
        ;;
    3)
        echo -e "${GREEN}در حال ارسال فرصت‌های معاملاتی هوشمند...${NC}"
        python3 telegram_smart_reporter.py --opportunities
        ;;
    4)
        echo -e "${GREEN}در حال اجرای تحلیل تأثیر اخبار بر بازار...${NC}"
        python3 telegram_smart_reporter.py --news
        ;;
    5)
        echo -e "${GREEN}در حال ارسال گزارش کامل...${NC}"
        python3 telegram_smart_reporter.py --full
        ;;
    6)
        echo -e "${GREEN}در حال ارسال پیام تست...${NC}"
        python3 telegram_smart_reporter.py --test
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
