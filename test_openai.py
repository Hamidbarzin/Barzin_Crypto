#!/usr/bin/env python3
"""
اسکریپت تست ساده برای بررسی اتصال به API هوش مصنوعی OpenAI
"""
import os
import sys
from openai import OpenAI

# دریافت کلید API
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    print("خطا: کلید API هوش مصنوعی تنظیم نشده است")
    print("لطفاً با دستور زیر کلید API را تنظیم کنید:")
    print("export OPENAI_API_KEY=\"کلید-API-شما\"")
    sys.exit(1)

# ایجاد کلاینت
client = OpenAI(api_key=api_key)

# یک درخواست ساده
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "سلام! لطفاً یک تحلیل کوتاه از بازار ارزهای دیجیتال ارائه دهید."}
        ],
        max_tokens=100
    )
    
    # نمایش پاسخ
    print("پاسخ دریافتی از هوش مصنوعی:")
    print("---")
    print(response.choices[0].message.content)
    print("---")
    print("اتصال به API هوش مصنوعی با موفقیت انجام شد! ✅")
    
except Exception as e:
    print(f"خطا در اتصال به API هوش مصنوعی: {str(e)} ❌")
    sys.exit(1)
