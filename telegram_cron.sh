#!/bin/bash
# اسکریپت ارسال منظم پیام تلگرام با استفاده از cURL

echo "در حال ارسال پیام به تلگرام ($(date))..."

# ارسال گزارش قیمت
curl -s "http://localhost:5000/send_price_report" | jq .

# بعد از هر 36 بار (حدود 6 ساعت) گزارش سیستم ارسال شود
COUNTER_FILE=".telegram_cron_counter"

if [ ! -f "$COUNTER_FILE" ]; then
  echo "0" > "$COUNTER_FILE"
fi

COUNTER=$(cat "$COUNTER_FILE")
COUNTER=$((COUNTER + 1))

if [ "$COUNTER" -ge 36 ]; then
  echo "در حال ارسال گزارش سیستم..."
  curl -s "http://localhost:5000/send_system_report" | jq .
  COUNTER=0
fi

echo "$COUNTER" > "$COUNTER_FILE"
echo "------------------------------"