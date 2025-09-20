#!/usr/bin/env python3
"""
PythonAnywhere Deployment Script for BarzinCrypto
This script helps you deploy your Flask app to PythonAnywhere
"""

import os
import subprocess
import sys

def print_step(step, description):
    print(f"\n{'='*50}")
    print(f"مرحله {step}: {description}")
    print('='*50)

def main():
    print("🚀 راهنمای Deploy روی PythonAnywhere")
    print("="*50)
    
    print_step(1, "ثبت‌نام در PythonAnywhere")
    print("1. برو به: https://www.pythonanywhere.com/")
    print("2. روی 'Sign up' کلیک کن")
    print("3. یک حساب رایگان ایجاد کن")
    print("4. ایمیل خودت را تأیید کن")
    
    print_step(2, "آپلود پروژه")
    print("روش 1 - از GitHub:")
    print("git clone https://github.com/Hamidbarzin/Barzin_Crypto.git")
    print("\nروش 2 - آپلود مستقیم:")
    print("1. به 'Files' برو")
    print("2. پروژه را ZIP کن و آپلود کن")
    print("3. در PythonAnywhere extract کن")
    
    print_step(3, "نصب Dependencies")
    print("1. به 'Consoles' برو")
    print("2. یک 'Bash console' باز کن")
    print("3. دستورات زیر را اجرا کن:")
    print("   cd Barzin_Crypto")
    print("   pip3.10 install --user -r requirements.txt")
    
    print_step(4, "ایجاد Web App")
    print("1. به 'Web' برو")
    print("2. روی 'Add a new web app' کلیک کن")
    print("3. 'Flask' را انتخاب کن")
    print("4. 'Python 3.10' را انتخاب کن")
    print("5. مسیر فایل اصلی: main.py")
    
    print_step(5, "تنظیم WSGI")
    print("فایل wsgi.py را ویرایش کن:")
    print("""
import sys
path = '/home/yourusername/Barzin_Crypto'
if path not in sys.path:
    sys.path.append(path)

from main import app as application
    """)
    
    print_step(6, "راه‌اندازی")
    print("1. روی 'Reload' کلیک کن")
    print("2. وب‌سایت شما آماده است!")
    print("3. دامنه: http://yourusername.pythonanywhere.com/")
    
    print("\n🎉 تبریک! پروژه شما deploy شد!")
    print("="*50)

if __name__ == "__main__":
    main()
