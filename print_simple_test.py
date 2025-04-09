"""
یک تست بسیار ساده برای چاپ پیام و نوشتن یک فایل
"""

import json
import os
import time

print("شروع تست ساده...")

try:
    # نوشتن در یک فایل
    data = {"test": "این یک تست ساده است"}
    with open("test_simple.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("فایل با موفقیت نوشته شد!")
    
    # بررسی فایل
    if os.path.exists("test_simple.json"):
        file_size = os.path.getsize("test_simple.json")
        print(f"فایل ایجاد شده است. اندازه: {file_size} بایت")
    else:
        print("خطا: فایل ایجاد نشده است!")
    
except Exception as e:
    print(f"خطا: {e}")

print("تست ساده به پایان رسید.")