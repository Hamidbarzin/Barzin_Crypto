from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    """Ultra simple index page"""
    template = """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ربات ساده ارز دیجیتال</title>
        <style>
            body {
                font-family: Tahoma, Arial, sans-serif;
                margin: 20px;
                line-height: 1.5;
            }
            h1, h2 {
                color: #333;
            }
            .update-time {
                color: #666;
            }
        </style>
    </head>
    <body>
        <h1>ربات ساده ارز دیجیتال</h1>
        <p class="update-time">آخرین به‌روزرسانی: {{ current_time }}</p>
        
        <h2>صفحه بسیار ساده برای عیب‌یابی</h2>
        <p>این صفحه به منظور آزمایش سلامت وب سرور ایجاد شده است.</p>
    </body>
    </html>
    """
    
    return render_template_string(
        template,
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)