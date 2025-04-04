#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template_string, request, redirect, url_for
import subprocess
import os

app = Flask(__name__)

# HTML template for the ultra-simple home page
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ربات معاملاتی ارز دیجیتال</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Vazirmatn', 'Tahoma', sans-serif;
            text-align: right;
            direction: rtl;
            padding: 20px;
            line-height: 1.6;
        }
        .btn {
            margin: 5px;
        }
        .result {
            background-color: #2d2d2d;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            white-space: pre-wrap;
            direction: ltr;
            text-align: left;
            font-family: monospace;
        }
        h1, h2, h3 {
            color: #c9d1d9;
        }
        .card {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-body">
                        <h1 class="card-title">ربات معاملاتی ارز دیجیتال</h1>
                        <p class="card-text">این سیستم ساده، گزارش‌های دوره‌ای و هشدارهای معاملاتی را از طریق تلگرام ارسال می‌کند.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h3>ارسال پیام تست</h3>
                    </div>
                    <div class="card-body">
                        <p>یک پیام تست به تلگرام ارسال کنید تا از عملکرد صحیح سیستم مطمئن شوید.</p>
                        <form action="/test_telegram" method="post">
                            <button type="submit" class="btn btn-primary">ارسال پیام تست</button>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h3>ارسال گزارش دوره‌ای</h3>
                    </div>
                    <div class="card-body">
                        <p>یک گزارش دوره‌ای از وضعیت بازار ارسال کنید.</p>
                        <form action="/send_report" method="post">
                            <button type="submit" class="btn btn-success">ارسال گزارش</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h3>اطلاعات بات تلگرام</h3>
                    </div>
                    <div class="card-body">
                        <p>اطلاعات مربوط به بات تلگرام را نمایش دهید.</p>
                        <form action="/bot_info" method="post">
                            <button type="submit" class="btn btn-info">نمایش اطلاعات بات</button>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h3>راه‌اندازی زمان‌بندی خودکار</h3>
                    </div>
                    <div class="card-body">
                        <p>سیستم زمان‌بندی را فعال کنید تا گزارش‌ها هر 30 دقیقه به صورت خودکار ارسال شوند.</p>
                        <form action="/start_scheduler" method="post">
                            <button type="submit" class="btn btn-warning">راه‌اندازی زمان‌بندی</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        
        {% if result %}
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h3>نتیجه</h3>
                    </div>
                    <div class="card-body">
                        <div class="result">{{ result }}</div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """Ultra simple index page"""
    return render_template_string(HOME_TEMPLATE, result=None)

@app.route('/test_telegram', methods=['POST'])
def test_telegram():
    """ارسال پیام تست به تلگرام"""
    try:
        result = subprocess.check_output(['python', 'telegram_reporter.py', 'test'], stderr=subprocess.STDOUT)
        return render_template_string(HOME_TEMPLATE, result=result.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        return render_template_string(HOME_TEMPLATE, result=f"خطا: {e.output.decode('utf-8')}")

@app.route('/send_report', methods=['POST'])
def send_report():
    """ارسال گزارش دوره‌ای به تلگرام"""
    try:
        result = subprocess.check_output(['python', 'telegram_reporter.py'], stderr=subprocess.STDOUT)
        return render_template_string(HOME_TEMPLATE, result=result.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        return render_template_string(HOME_TEMPLATE, result=f"خطا: {e.output.decode('utf-8')}")

@app.route('/bot_info', methods=['POST'])
def bot_info():
    """نمایش اطلاعات بات تلگرام"""
    try:
        result = subprocess.check_output(['python', 'test_telegram.py', '--info'], stderr=subprocess.STDOUT)
        return render_template_string(HOME_TEMPLATE, result=result.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        return render_template_string(HOME_TEMPLATE, result=f"خطا: {e.output.decode('utf-8')}")

@app.route('/start_scheduler', methods=['POST'])
def start_scheduler():
    """راه‌اندازی زمان‌بندی خودکار"""
    try:
        # اجرای اسکریپت زمان‌بندی در پس‌زمینه
        subprocess.Popen(['./simple_scheduler.sh'], stdout=open('scheduler.log', 'a'), stderr=subprocess.STDOUT, start_new_session=True)
        return render_template_string(HOME_TEMPLATE, result="زمان‌بندی با موفقیت شروع شد. گزارش‌ها هر 30 دقیقه ارسال خواهند شد.")
    except Exception as e:
        return render_template_string(HOME_TEMPLATE, result=f"خطا در راه‌اندازی زمان‌بندی: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)