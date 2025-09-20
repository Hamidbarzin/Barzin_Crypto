#!/usr/bin/env python3
"""
Railway Deployment Script for BarzinCrypto
This script helps you deploy your Flask app to Railway
"""

import webbrowser
import time

def print_step(step, description):
    print(f"\n{'='*50}")
    print(f"مرحله {step}: {description}")
    print('='*50)

def main():
    print("🚀 راهنمای Deploy روی Railway")
    print("="*50)
    
    print_step(1, "ثبت‌نام در Railway")
    print("1. برو به: https://railway.app/")
    print("2. روی 'Sign up' کلیک کن")
    print("3. 'Sign up with GitHub' را انتخاب کن")
    print("4. اجازه دسترسی به repository را بده")
    
    print_step(2, "Deploy پروژه")
    print("1. روی 'New Project' کلیک کن")
    print("2. 'Deploy from GitHub repo' را انتخاب کن")
    print("3. Repository 'Hamidbarzin/Barzin_Crypto' را انتخاب کن")
    print("4. روی 'Deploy Now' کلیک کن")
    
    print_step(3, "تنظیمات خودکار")
    print("Railway خودکار:")
    print("✅ Python 3.10 را تشخیص می‌دهد")
    print("✅ Dependencies را نصب می‌کند")
    print("✅ render_main.py را اجرا می‌کند")
    print("✅ دامنه رایگان می‌دهد")
    
    print_step(4, "دریافت دامنه")
    print("1. بعد از deploy، دامنه شما آماده است")
    print("2. فرمت: https://yourproject.railway.app")
    print("3. روی دامنه کلیک کن تا وب‌سایت را ببینی")
    
    print("\n🎉 تبریک! پروژه شما deploy شد!")
    print("="*50)
    
    # Open Railway in browser
    print("\n🌐 باز کردن Railway در مرورگر...")
    time.sleep(2)
    webbrowser.open('https://railway.app/')
    
    print("\n✅ Railway در مرورگر باز شد!")
    print("حالا مراحل بالا را دنبال کن!")

if __name__ == "__main__":
    main()
