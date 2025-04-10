# پیاده‌سازی چندزبانگی در پروژه‌های وب (React و Python)
# Multilingual Implementation for Web Projects (React and Python)

این مخزن شامل مثال‌هایی برای پیاده‌سازی چندزبانگی (i18n) در پروژه‌های وب با استفاده از React در فرانت‌اند و Python (Flask یا Django) در بک‌اند است.

This repository contains examples for implementing internationalization (i18n) in web projects using React in the frontend and Python (Flask or Django) in the backend.

## ساختار پروژه / Project Structure

```
examples/
├── react-i18n-example/     # مثال پیاده‌سازی چندزبانگی در React
├── flask-babel-example/    # مثال پیاده‌سازی چندزبانگی در Flask
└── django-example/         # مثال پیاده‌سازی چندزبانگی در Django
```

## مثال React / React Example

این مثال نشان می‌دهد چگونه می‌توان از i18next برای پیاده‌سازی چندزبانگی در یک برنامه React استفاده کرد. امکانات شامل:

* پشتیبانی از زبان‌های انگلیسی و فارسی
* تشخیص خودکار زبان مرورگر
* امکان تغییر زبان توسط کاربر
* پشتیبانی از RTL برای زبان فارسی
* ارسال زبان انتخاب شده به API‌ها

This example demonstrates how to use i18next to implement multilingual support in a React application. Features include:

* Support for English and Persian languages
* Automatic browser language detection
* User language switching
* RTL support for Persian language
* Sending selected language to APIs

## مثال Flask / Flask Example

این مثال نشان می‌دهد چگونه می‌توان از Flask-Babel برای پیاده‌سازی چندزبانگی در یک برنامه Flask استفاده کرد. امکانات شامل:

* پشتیبانی از زبان‌های انگلیسی و فارسی
* تشخیص زبان از پارامترهای URL، کوکی‌ها و هدرهای HTTP
* API‌های چندزبانه با پیام‌های خطای ترجمه شده
* قالب‌های Jinja2 با پشتیبانی چندزبانه

This example demonstrates how to use Flask-Babel to implement multilingual support in a Flask application. Features include:

* Support for English and Persian languages
* Language detection from URL parameters, cookies, and HTTP headers
* Multilingual APIs with translated error messages
* Jinja2 templates with multilingual support

## مثال Django / Django Example

این مثال نشان می‌دهد چگونه می‌توان از سیستم ترجمه داخلی Django برای پیاده‌سازی چندزبانگی استفاده کرد. امکانات شامل:

* پشتیبانی از زبان‌های انگلیسی و فارسی
* پیشوندهای URL بر اساس زبان (مانند `/en/` و `/fa/`)
* مدل‌های Django با فیلدهای ترجمه شده
* API‌های چندزبانه با پیام‌های خطای ترجمه شده
* قالب‌های Django با پشتیبانی چندزبانه

This example demonstrates how to use Django's built-in translation system to implement multilingual support. Features include:

* Support for English and Persian languages
* Language-specific URL prefixes (like `/en/` and `/fa/`)
* Django models with translated fields
* Multilingual APIs with translated error messages
* Django templates with multilingual support

## طریقه اجرا / How to Run

### React Example

```bash
cd examples/react-i18n-example
npm install
npm start
```

### Flask Example

```bash
cd examples/flask-babel-example
pip install -r requirements.txt
flask run
```

### Django Example

```bash
cd examples/django-example
pip install -r requirements.txt
python manage.py runserver
```

## نکات مهم / Important Notes

1. برای زبان فارسی، استفاده از فونت‌های مناسب مانند Vazir یا Tahoma توصیه می‌شود.
2. برای پروژه‌های React، استفاده از استایل‌های CSS logical properties برای پشتیبانی بهتر از RTL توصیه می‌شود.
3. در پروژه‌های Django، از `i18n_patterns` برای URLهای چندزبانه استفاده کنید.
4. در پروژه‌های Flask، از `babel.localeselector` برای تعیین زبان استفاده کنید.

1. For Persian language, using appropriate fonts like Vazir or Tahoma is recommended.
2. For React projects, using CSS logical properties for better RTL support is recommended.
3. In Django projects, use `i18n_patterns` for multilingual URLs.
4. In Flask projects, use `babel.localeselector` for language selection.