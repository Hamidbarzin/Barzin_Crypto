"""
سرویس اعلان و هشدار ایمیلی برای ارسال هشدارها در مورد فرصت‌های خرید و فروش و نوسانات بازار
"""

import os
import sys
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# پشتیبانی از SendGrid به عنوان یک سرویس ارسال ایمیل اضافی
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# تنظیم لاگر
logger = logging.getLogger(__name__)

# دریافت اطلاعات ایمیل از متغیرهای محیطی
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_SERVER = os.environ.get("EMAIL_SERVER", "mail.smtp2go.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 2525))

# تنظیمات SendGrid
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
USE_SENDGRID = bool(SENDGRID_API_KEY and SENDGRID_AVAILABLE)

def send_email_via_sendgrid(to_email, subject, html_content, text_content=None):
    """
    ارسال ایمیل با استفاده از سرویس SendGrid

    Args:
        to_email (str): آدرس ایمیل گیرنده
        subject (str): موضوع ایمیل
        html_content (str): محتوای HTML ایمیل
        text_content (str, optional): محتوای متنی ایمیل (برای کلاینت‌های بدون پشتیبانی HTML)

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    if not SENDGRID_API_KEY:
        logger.error("کلید API سندگرید تنظیم نشده است")
        return False

    # اگر محتوای متنی ارائه نشده باشد، استفاده از همان محتوای HTML
    if text_content is None:
        import re
        # حذف تگ‌های HTML برای نسخه متنی
        text_content = re.sub(r'<.*?>', '', html_content)

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        from_email = Email(EMAIL_USER) if EMAIL_USER else Email("noreply@crypto-bot.com")
        to_email_obj = To(to_email)
        plain_content = Content("text/plain", text_content)
        html_content_obj = Content("text/html", html_content)
        
        mail = Mail(from_email, to_email_obj, subject, plain_content)
        mail.add_content(html_content_obj)
        
        response = sg.send(mail)
        
        if response.status_code >= 200 and response.status_code < 300:
            logger.info(f"ایمیل با موضوع '{subject}' به '{to_email}' از طریق SendGrid ارسال شد")
            return True
        else:
            logger.error(f"خطا در ارسال ایمیل از طریق SendGrid: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"خطا در ارسال ایمیل از طریق SendGrid: {str(e)}")
        return False

def send_email_via_smtp(to_email, subject, html_content, text_content=None):
    """
    ارسال ایمیل با استفاده از پروتکل SMTP

    Args:
        to_email (str): آدرس ایمیل گیرنده
        subject (str): موضوع ایمیل
        html_content (str): محتوای HTML ایمیل
        text_content (str, optional): محتوای متنی ایمیل (برای کلاینت‌های بدون پشتیبانی HTML)

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    if not all([EMAIL_USER, EMAIL_PASSWORD]):
        logger.error("تنظیمات ایمیل SMTP کامل نیست")
        return False

    # اگر محتوای متنی ارائه نشده باشد، از همان محتوای HTML استفاده می‌کنیم
    if text_content is None:
        import re
        # حذف تگ‌های HTML برای نسخه متنی
        text_content = re.sub(r'<.*?>', '', html_content)

    try:
        # ایجاد پیام
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = EMAIL_USER
        message["To"] = to_email

        # افزودن بخش‌های متنی و HTML
        part1 = MIMEText(text_content, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")
        message.attach(part1)
        message.attach(part2)

        # ارسال ایمیل
        with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
            if EMAIL_SERVER != "localhost":
                server.starttls()  # امنیت TLS
                if EMAIL_USER and EMAIL_PASSWORD:
                    server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(message)

        logger.info(f"ایمیل با موضوع '{subject}' به '{to_email}' از طریق SMTP ارسال شد")
        return True

    except Exception as e:
        logger.error(f"خطا در ارسال ایمیل از طریق SMTP: {str(e)}")
        return False

def send_email_notification(to_email, subject, html_content, text_content=None):
    """
    ارسال ایمیل با استفاده از تنظیمات موجود (SendGrid یا SMTP)

    Args:
        to_email (str): آدرس ایمیل گیرنده
        subject (str): موضوع ایمیل
        html_content (str): محتوای HTML ایمیل
        text_content (str, optional): محتوای متنی ایمیل (برای کلاینت‌های بدون پشتیبانی HTML)

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    # ابتدا سعی می‌کنیم از سندگرید استفاده کنیم، اگر تنظیم شده باشد
    if USE_SENDGRID:
        result = send_email_via_sendgrid(to_email, subject, html_content, text_content)
        if result:
            return True
        else:
            logger.warning("ارسال ایمیل از طریق SendGrid با خطا مواجه شد، تلاش با SMTP")
    
    # اگر SendGrid تنظیم نشده باشد یا با خطا مواجه شده باشد، از SMTP استفاده می‌کنیم
    return send_email_via_smtp(to_email, subject, html_content, text_content)

def send_buy_sell_email(to_email, symbol, action, price, reason):
    """
    ارسال اعلان خرید یا فروش از طریق ایمیل

    Args:
        to_email (str): آدرس ایمیل گیرنده
        symbol (str): نماد ارز
        action (str): 'خرید' یا 'فروش'
        price (float): قیمت فعلی
        reason (str): دلیل توصیه

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    subject = f"سیگنال {action} برای {symbol}"
    
    # محتوای HTML
    html_content = f"""
    <html dir="rtl" lang="fa">
    <head>
        <style>
            body {{ font-family: Tahoma, Arial, sans-serif; direction: rtl; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #181A20; color: #eaecef; border-radius: 10px; }}
            .header {{ background-color: #FCD535; color: #000; padding: 10px; border-radius: 5px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ font-size: 12px; text-align: center; margin-top: 20px; color: #6c757d; }}
            .price {{ font-size: 24px; font-weight: bold; color: #FCD535; }}
            .reason {{ background-color: #2b2f36; padding: 10px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🔔 سیگنال {action} برای {symbol}</h2>
            </div>
            <div class="content">
                <p>ربات هوشمند تحلیل ارز دیجیتال، یک سیگنال {action} برای {symbol} شناسایی کرده است.</p>
                <p>💰 <strong>قیمت فعلی:</strong> <span class="price">{price}</span></p>
                <p>📊 <strong>دلیل:</strong></p>
                <div class="reason">
                    <p>{reason}</p>
                </div>
                <p>⏰ <strong>زمان:</strong> {get_current_persian_time()}</p>
            </div>
            <div class="footer">
                <p>این ایمیل به صورت خودکار توسط ربات تحلیل ارز دیجیتال ارسال شده است.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # محتوای متنی ساده
    text_content = f"""
    🔔 سیگنال {action} برای {symbol}
    
    ربات هوشمند تحلیل ارز دیجیتال، یک سیگنال {action} برای {symbol} شناسایی کرده است.
    
    💰 قیمت فعلی: {price}
    
    📊 دلیل: {reason}
    
    ⏰ زمان: {get_current_persian_time()}
    
    این ایمیل به صورت خودکار توسط ربات تحلیل ارز دیجیتال ارسال شده است.
    """
    
    return send_email_notification(to_email, subject, html_content, text_content)

def send_volatility_email(to_email, symbol, price, change_percent, timeframe="1h"):
    """
    ارسال هشدار نوسان قیمت از طریق ایمیل

    Args:
        to_email (str): آدرس ایمیل گیرنده
        symbol (str): نماد ارز
        price (float): قیمت فعلی
        change_percent (float): درصد تغییر
        timeframe (str): بازه زمانی تغییر

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    direction = "افزایش" if change_percent > 0 else "کاهش"
    emoji = "🚀" if change_percent > 0 else "📉"
    color = "#22c55e" if change_percent > 0 else "#ef4444"
    
    subject = f"هشدار نوسان قیمت {symbol}: {direction} {abs(change_percent):.2f}%"
    
    # محتوای HTML
    html_content = f"""
    <html dir="rtl" lang="fa">
    <head>
        <style>
            body {{ font-family: Tahoma, Arial, sans-serif; direction: rtl; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #181A20; color: #eaecef; border-radius: 10px; }}
            .header {{ background-color: {color}; color: #fff; padding: 10px; border-radius: 5px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ font-size: 12px; text-align: center; margin-top: 20px; color: #6c757d; }}
            .price {{ font-size: 24px; font-weight: bold; color: #FCD535; }}
            .change {{ font-size: 20px; font-weight: bold; color: {color}; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>{emoji} هشدار نوسان قیمت {symbol}</h2>
            </div>
            <div class="content">
                <p>ربات هوشمند تحلیل ارز دیجیتال، یک نوسان قابل توجه در قیمت {symbol} شناسایی کرده است.</p>
                <p>💰 <strong>قیمت فعلی:</strong> <span class="price">{price}</span></p>
                <p>📊 <strong>{direction}:</strong> <span class="change">{abs(change_percent):.2f}%</span> در {timeframe}</p>
                <p>⏰ <strong>زمان:</strong> {get_current_persian_time()}</p>
            </div>
            <div class="footer">
                <p>این ایمیل به صورت خودکار توسط ربات تحلیل ارز دیجیتال ارسال شده است.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # محتوای متنی ساده
    text_content = f"""
    {emoji} هشدار نوسان قیمت {symbol}
    
    ربات هوشمند تحلیل ارز دیجیتال، یک نوسان قابل توجه در قیمت {symbol} شناسایی کرده است.
    
    💰 قیمت فعلی: {price}
    
    📊 {direction}: {abs(change_percent):.2f}% در {timeframe}
    
    ⏰ زمان: {get_current_persian_time()}
    
    این ایمیل به صورت خودکار توسط ربات تحلیل ارز دیجیتال ارسال شده است.
    """
    
    return send_email_notification(to_email, subject, html_content, text_content)

def send_market_trend_email(to_email, trend, affected_coins, reason):
    """
    ارسال هشدار روند کلی بازار از طریق ایمیل

    Args:
        to_email (str): آدرس ایمیل گیرنده
        trend (str): روند بازار ('صعودی'، 'نزولی' یا 'خنثی')
        affected_coins (list): لیست ارزهای تحت تأثیر
        reason (str): دلیل روند

    Returns:
        bool: آیا ارسال موفقیت‌آمیز بود
    """
    emoji = "🚀" if trend == "صعودی" else "📉" if trend == "نزولی" else "⚖️"
    color = "#22c55e" if trend == "صعودی" else "#ef4444" if trend == "نزولی" else "#eab308"
    
    subject = f"تحلیل روند بازار: {trend}"
    
    # ساخت لیست ارزها به صورت HTML
    coins_html = ""
    for i, coin in enumerate(affected_coins[:10]):
        coins_html += f"<span style='margin-left: 10px;'>{coin}</span>"
        if i % 3 == 2:  # هر 3 مورد یک خط جدید
            coins_html += "<br>"
    
    if len(affected_coins) > 10:
        coins_html += f"<br>و {len(affected_coins) - 10} ارز دیگر"
    
    # محتوای HTML
    html_content = f"""
    <html dir="rtl" lang="fa">
    <head>
        <style>
            body {{ font-family: Tahoma, Arial, sans-serif; direction: rtl; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #181A20; color: #eaecef; border-radius: 10px; }}
            .header {{ background-color: {color}; color: #fff; padding: 10px; border-radius: 5px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ font-size: 12px; text-align: center; margin-top: 20px; color: #6c757d; }}
            .reason {{ background-color: #2b2f36; padding: 10px; border-radius: 5px; }}
            .trend {{ font-size: 20px; font-weight: bold; color: {color}; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>{emoji} تحلیل روند بازار</h2>
            </div>
            <div class="content">
                <p>ربات هوشمند تحلیل ارز دیجیتال، روند فعلی بازار را تحلیل کرده است.</p>
                <p>📊 <strong>روند فعلی:</strong> <span class="trend">{trend}</span></p>
                <p>🔍 <strong>دلیل:</strong></p>
                <div class="reason">
                    <p>{reason}</p>
                </div>
                <p>💱 <strong>ارزهای تحت تأثیر:</strong></p>
                <div class="coins">
                    {coins_html}
                </div>
                <p>⏰ <strong>زمان:</strong> {get_current_persian_time()}</p>
            </div>
            <div class="footer">
                <p>این ایمیل به صورت خودکار توسط ربات تحلیل ارز دیجیتال ارسال شده است.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # محتوای متنی ساده
    text_content = f"""
    {emoji} تحلیل روند بازار
    
    ربات هوشمند تحلیل ارز دیجیتال، روند فعلی بازار را تحلیل کرده است.
    
    📊 روند فعلی: {trend}
    
    🔍 دلیل: {reason}
    
    💱 ارزهای تحت تأثیر: {', '.join(affected_coins[:10])}
    {f'و {len(affected_coins) - 10} ارز دیگر' if len(affected_coins) > 10 else ''}
    
    ⏰ زمان: {get_current_persian_time()}
    
    این ایمیل به صورت خودکار توسط ربات تحلیل ارز دیجیتال ارسال شده است.
    """
    
    return send_email_notification(to_email, subject, html_content, text_content)

def send_test_email(to_email):
    """
    ارسال ایمیل تست برای بررسی عملکرد سیستم اعلان ایمیلی

    Args:
        to_email (str): آدرس ایمیل گیرنده

    Returns:
        dict: وضعیت ارسال و پیام
    """
    subject = "پیام تست از ربات معامله ارز دیجیتال"
    
    # محتوای HTML
    html_content = f"""
    <html dir="rtl" lang="fa">
    <head>
        <style>
            body {{ font-family: Tahoma, Arial, sans-serif; direction: rtl; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #181A20; color: #eaecef; border-radius: 10px; }}
            .header {{ background-color: #FCD535; color: #000; padding: 10px; border-radius: 5px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ font-size: 12px; text-align: center; margin-top: 20px; color: #6c757d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🤖 پیام تست ربات معامله ارز دیجیتال</h2>
            </div>
            <div class="content">
                <p>این یک پیام تست است برای بررسی عملکرد سیستم اعلان ایمیلی.</p>
                <p>⏰ <strong>زمان:</strong> {get_current_persian_time()}</p>
                <p>سیستم اعلان‌های ایمیلی با موفقیت فعال شده است.</p>
            </div>
            <div class="footer">
                <p>این ایمیل به صورت خودکار توسط ربات تحلیل ارز دیجیتال ارسال شده است.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # محتوای متنی ساده
    text_content = f"""
    🤖 پیام تست ربات معامله ارز دیجیتال
    
    این یک پیام تست است برای بررسی عملکرد سیستم اعلان ایمیلی.
    
    ⏰ زمان: {get_current_persian_time()}
    
    سیستم اعلان‌های ایمیلی با موفقیت فعال شده است.
    
    این ایمیل به صورت خودکار توسط ربات تحلیل ارز دیجیتال ارسال شده است.
    """
    
    result = send_email_notification(to_email, subject, html_content, text_content)
    if result:
        return {
            "success": True,
            "message": "ایمیل تست با موفقیت ارسال شد."
        }
    else:
        return {
            "success": False,
            "message": "خطا در ارسال ایمیل تست. لطفاً تنظیمات را بررسی کنید."
        }

def get_current_persian_time():
    """
    دریافت زمان فعلی به فرمت مناسب فارسی

    Returns:
        str: زمان فعلی
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")