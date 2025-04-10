#!/usr/bin/env python3
"""
مدل‌های پایگاه داده برای سیستم مدیریت ارزهای دیجیتال

این فایل شامل تعریف جداول و ارتباطات پایگاه داده است.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    مدل کاربر برای احراز هویت
    
    این مدل برای نگهداری اطلاعات کاربران سیستم استفاده می‌شود.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        """
        تنظیم رمز عبور با هش‌گذاری
        
        Args:
            password (str): رمز عبور جدید
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        بررسی صحت رمز عبور
        
        Args:
            password (str): رمز عبور برای بررسی
            
        Returns:
            bool: آیا رمز عبور صحیح است
        """
        return check_password_hash(self.password_hash, password)

class PriceAlert(db.Model):
    """
    مدل هشدار قیمت
    
    این مدل برای نگهداری اطلاعات هشدارهای قیمت استفاده می‌شود.
    """
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(10), nullable=False)  # above یا below
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    active = db.Column(db.Boolean, default=True)
    
    # ارتباط با کاربر
    user = db.relationship('User', backref='price_alerts')