# راهنمای استقرار ربات روی Fly.io

## پیش‌نیازها

1. حساب کاربری در [Fly.io](https://fly.io)
2. نصب [Flyctl CLI](https://fly.io/docs/hands-on/install-flyctl/)
3. توکن بات تلگرام و شناسه چت

## مراحل استقرار

### 1. ورود به حساب Fly.io

ابتدا با دستور زیر وارد حساب خود شوید:

```
flyctl auth login
```

### 2. تنظیم متغیرهای محیطی

متغیرهای زیر را در محیط خود تنظیم کنید:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export DEFAULT_CHAT_ID="your_chat_id"
```

برای استفاده از توکن API (اختیاری، برای استقرار خودکار):

```bash
export FLY_API_TOKEN="your_fly_api_token"
```

### 3. اجرای اسکریپت استقرار

```bash
./deploy/fly/deploy.sh
```

## استقرار دستی

اگر می‌خواهید به صورت دستی استقرار کنید:

### 1. ایجاد برنامه

```bash
flyctl apps create crypto-telegram-bot
```

### 2. تنظیم متغیرهای محیطی

```bash
flyctl secrets set TELEGRAM_BOT_TOKEN="your_bot_token"
flyctl secrets set DEFAULT_CHAT_ID="your_chat_id"
```

### 3. استقرار

```bash
flyctl deploy
```

## مشاهده لاگ‌ها

```bash
flyctl logs
```

## کنترل برنامه

توقف برنامه:
```bash
flyctl apps suspend crypto-telegram-bot
```

راه‌اندازی مجدد:
```bash
flyctl apps resume crypto-telegram-bot
```

## مزایای Fly.io برای کاربران کانادایی

1. دارای مرکز داده در تورنتو
2. لایه رایگان کافی برای اجرای ربات
3. اتصال پایدار و کم‌تأخیر
4. بدون نیاز به اجرای VPS
