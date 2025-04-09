#!/bin/bash

# اسکریپت توقف گزارش‌دهنده هر ۱۰ دقیقه
echo "در حال توقف سرویس گزارش‌دهنده هر ۱۰ دقیقه..."

# بررسی وجود فایل PID
if [ -f "ten_minute_telegram_sender.pid" ]; then
    pid=$(cat ten_minute_telegram_sender.pid | python3 -c "import json,sys; print(json.load(sys.stdin).get('pid', 0))")
    
    if ps -p $pid > /dev/null; then
        echo "در حال توقف سرویس با PID: $pid"
        kill $pid
        echo "درخواست توقف ارسال شد"
        sleep 2
        
        # بررسی توقف کامل
        if ps -p $pid > /dev/null; then
            echo "سرویس هنوز در حال اجراست. در حال توقف اجباری..."
            kill -9 $pid
            sleep 1
        fi
        
        if ps -p $pid > /dev/null; then
            echo "خطا: نمی‌توان سرویس را متوقف کرد."
            exit 1
        else
            echo "سرویس با موفقیت متوقف شد."
            rm ten_minute_telegram_sender.pid
        fi
    else
        echo "سرویس در حال اجرا نیست. در حال پاکسازی فایل PID..."
        rm ten_minute_telegram_sender.pid
    fi
else
    echo "فایل PID یافت نشد. احتمالاً سرویس در حال اجرا نیست."
    
    # تلاش برای یافتن و توقف فرآیندهای احتمالی
    pids=$(ps aux | grep "[t]en_minute_telegram_sender.py" | awk '{print $2}')
    
    if [ -n "$pids" ]; then
        echo "فرآیندهای مرتبط یافت شد. در حال توقف..."
        
        for p in $pids; do
            echo "توقف PID: $p"
            kill $p
        done
        
        echo "همه فرآیندهای مرتبط متوقف شدند."
    else
        echo "هیچ فرآیند مرتبطی یافت نشد."
    fi
fi

echo "عملیات توقف سرویس به پایان رسید."