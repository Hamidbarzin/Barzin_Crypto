#!/usr/bin/env python3
"""
ماژول احراز هویت برای کنترل پنل تلگرام

این ماژول مدیریت احراز هویت برای کنترل پنل تلگرام را انجام می‌دهد.
"""

import os
import json
import hashlib
from functools import wraps
from flask import session, redirect, url_for, flash, request

# فایل ذخیره‌سازی اطلاعات کاربران (با رمز عبور هش شده)
AUTH_FILE = 'telegram_panel_auth.json'

# رمز عبور پیش‌فرض برای اولین راه‌اندازی
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'crypto_barzin'

def init_auth():
    """
    ایجاد فایل احراز هویت در صورت عدم وجود
    
    Returns:
        bool: وضعیت موفقیت
    """
    if not os.path.exists(AUTH_FILE):
        default_password_hash = hashlib.sha256(DEFAULT_PASSWORD.encode()).hexdigest()
        users = {
            DEFAULT_USERNAME: {
                'password_hash': default_password_hash
            }
        }
        with open(AUTH_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4)
        return True
    return False

def hash_password(password):
    """
    هش‌گذاری رمز عبور
    
    Args:
        password (str): رمز عبور
        
    Returns:
        str: هش رمز عبور
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(username, password):
    """
    بررسی صحت نام کاربری و رمز عبور
    
    Args:
        username (str): نام کاربری
        password (str): رمز عبور
        
    Returns:
        bool: آیا احراز هویت موفق بود
    """
    init_auth()  # اطمینان از وجود فایل احراز هویت
    
    try:
        with open(AUTH_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        if username in users:
            password_hash = hash_password(password)
            return password_hash == users[username]['password_hash']
    except Exception as e:
        print(f"خطا در احراز هویت: {str(e)}")
    
    return False

def change_password(username, new_password):
    """
    تغییر رمز عبور
    
    Args:
        username (str): نام کاربری
        new_password (str): رمز عبور جدید
        
    Returns:
        bool: آیا تغییر رمز موفق بود
    """
    init_auth()  # اطمینان از وجود فایل احراز هویت
    
    try:
        with open(AUTH_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        if username in users:
            users[username]['password_hash'] = hash_password(new_password)
            
            with open(AUTH_FILE, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=4)
            return True
    except Exception as e:
        print(f"خطا در تغییر رمز عبور: {str(e)}")
    
    return False

def login_required(view_func):
    """
    دکوراتور برای محدود کردن دسترسی به کاربران احراز هویت شده
    
    Args:
        view_func (callable): تابع نمایش
        
    Returns:
        callable: تابع بسته‌بندی شده
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'telegram_auth' not in session or not session['telegram_auth']:
            # ذخیره آدرس درخواستی برای هدایت پس از ورود
            session['next_url'] = request.url
            return redirect(url_for('telegram_login'))
        return view_func(*args, **kwargs)
    return wrapped_view