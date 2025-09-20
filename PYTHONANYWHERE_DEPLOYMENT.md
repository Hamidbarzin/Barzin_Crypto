# 🚀 راهنمای Deploy روی PythonAnywhere

## مرحله 1: ثبت‌نام
1. برو به [PythonAnywhere](https://www.pythonanywhere.com/)
2. روی **"Sign up"** کلیک کن
3. یک حساب رایگان ایجاد کن
4. ایمیل خودت را تأیید کن

## مرحله 2: آپلود پروژه

### روش 1: از GitHub (توصیه می‌شود)
1. به **"Consoles"** برو
2. یک **"Bash console"** باز کن
3. دستور زیر را اجرا کن:
```bash
git clone https://github.com/Hamidbarzin/Barzin_Crypto.git
cd Barzin_Crypto
```

### روش 2: آپلود مستقیم
1. پروژه را ZIP کن
2. به **"Files"** برو
3. فایل ZIP را آپلود کن
4. در PythonAnywhere extract کن

## مرحله 3: نصب Dependencies
1. در **Bash console** دستورات زیر را اجرا کن:
```bash
cd Barzin_Crypto
pip3.10 install --user -r requirements_pythonanywhere.txt
```

## مرحله 4: ایجاد Web App
1. به **"Web"** برو
2. روی **"Add a new web app"** کلیک کن
3. **"Flask"** را انتخاب کن
4. **"Python 3.10"** را انتخاب کن
5. مسیر فایل اصلی: `main.py`

## مرحله 5: تنظیم WSGI
1. فایل `wsgi.py` را ویرایش کن
2. `yourusername` را با نام کاربری خودت جایگزین کن:
```python
path = '/home/yourusername/Barzin_Crypto'
```

## مرحله 6: راه‌اندازی
1. روی **"Reload"** کلیک کن
2. وب‌سایت شما آماده است!
3. دامنه: `http://yourusername.pythonanywhere.com/`

## ✅ مزایای PythonAnywhere:
- ✅ بدون محدودیت حجم 250MB
- ✅ مخصوص Python و Flask
- ✅ دامنه رایگان
- ✅ پشتیبانی کامل از WebSocket
- ✅ 512MB فضای رایگان
- ✅ پشتیبانی 24/7

## 🔧 عیب‌یابی:
اگر مشکلی پیش آمد:
1. به **"Web"** برو
2. روی **"Error log"** کلیک کن
3. خطاها را بررسی کن
4. در صورت نیاز، dependencies را دوباره نصب کن

## 📞 پشتیبانی:
- **Forums:** https://www.pythonanywhere.com/forums/
- **Email:** liveusercare@pythonanywhere.com
