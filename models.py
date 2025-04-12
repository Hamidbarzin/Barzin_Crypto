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

class CryptoQuiz(db.Model):
    """
    مدل سوالات کوییز ارز دیجیتال
    
    این مدل برای نگهداری سوالات کوییز دانش ارزهای دیجیتال استفاده می‌شود.
    """
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False, default='medium')  # easy, medium, hard
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # a, b, c یا d
    explanation = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default='general')  # general, bitcoin, technical, etc.
    points = db.Column(db.Integer, nullable=False, default=10)

class UserQuizAttempt(db.Model):
    """
    مدل تلاش‌های کاربر در کوییز
    
    این مدل برای نگهداری تاریخچه تلاش‌های کاربر و امتیازات آن‌ها استفاده می‌شود.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('crypto_quiz.id'), nullable=False)
    answer = db.Column(db.String(1), nullable=True)  # پاسخ کاربر
    is_correct = db.Column(db.Boolean, nullable=True)
    points_earned = db.Column(db.Integer, nullable=True, default=0)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    # ارتباطات
    user = db.relationship('User', backref='quiz_attempts')
    quiz = db.relationship('CryptoQuiz', backref='attempts')

class UserQuizScore(db.Model):
    """
    مدل امتیازات کاربر در کوییز
    
    این مدل برای نگهداری مجموع امتیازات کاربر و سطح او استفاده می‌شود.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    total_points = db.Column(db.Integer, nullable=False, default=0)
    total_correct = db.Column(db.Integer, nullable=False, default=0)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    level = db.Column(db.Integer, nullable=False, default=1)
    badges = db.Column(db.String(500), nullable=True)  # JSON string of earned badges
    last_quiz_date = db.Column(db.DateTime, nullable=True)
    
    # ارتباط با کاربر
    user = db.relationship('User', backref=db.backref('quiz_score', uselist=False))