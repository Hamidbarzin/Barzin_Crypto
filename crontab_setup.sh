#!/bin/bash
# تنظیم crontab برای ارسال خودکار پیام تلگرام هر ۱۰ دقیقه

echo "در حال تنظیم crontab برای ارسال خودکار پیام تلگرام..."

# مسیر کامل فایل اسکریپت
SCRIPT_PATH="$PWD/api_caller.py"
LOG_PATH="$PWD/telegram_cron.log"

# ایجاد فایل crontab موقت
TEMP_CRONTAB="$(mktemp)"

# دریافت crontab فعلی
crontab -l > "$TEMP_CRONTAB" 2>/dev/null || echo "" > "$TEMP_CRONTAB"

# حذف ورودی‌های قبلی مرتبط با تلگرام
grep -v "send_price_report\|send_system_report\|send_test_message_replit" "$TEMP_CRONTAB" > "${TEMP_CRONTAB}.new"
mv "${TEMP_CRONTAB}.new" "$TEMP_CRONTAB"

# اضافه کردن دستورات جدید
echo "# ارسال گزارش قیمت هر ۱۰ دقیقه" >> "$TEMP_CRONTAB"
echo "*/10 * * * * cd $PWD && $SCRIPT_PATH http://localhost:5000/send_price_report >> $LOG_PATH 2>&1" >> "$TEMP_CRONTAB"
echo "" >> "$TEMP_CRONTAB"
echo "# ارسال گزارش سیستم هر ۶ ساعت" >> "$TEMP_CRONTAB"
echo "0 */6 * * * cd $PWD && $SCRIPT_PATH http://localhost:5000/send_system_report >> $LOG_PATH 2>&1" >> "$TEMP_CRONTAB"

# نصب crontab جدید
crontab "$TEMP_CRONTAB"

# پاکسازی
rm "$TEMP_CRONTAB"

echo "crontab با موفقیت تنظیم شد:"
crontab -l | grep -E "send_price_report|send_system_report"

echo ""
echo "توجه: crontab در محیط Replit ممکن است به درستی کار نکند. برای اطمینان از کارکرد درست،"
echo "می‌توانید دستور زیر را به صورت دستی اجرا کنید:"
echo ""
echo "cd $PWD && $SCRIPT_PATH http://localhost:5000/send_price_report >> $LOG_PATH 2>&1"