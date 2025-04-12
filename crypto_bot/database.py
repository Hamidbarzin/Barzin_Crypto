"""
ماژول پایگاه داده برای کریپتو بارزین

این ماژول برای مدیریت ارتباط با پایگاه داده استفاده می‌شود.
"""

from models import db

# ارائه شی db از ماژول models برای استفاده در سایر ماژول‌ها
def get_db():
    """
    دریافت نمونه پایگاه داده
    
    Returns:
        SQLAlchemy: نمونه پایگاه داده
    """
    return db

# دریافت مدل‌های مورد نیاز از ماژول models
def get_models():
    """
    دریافت مدل‌های پایگاه داده
    
    Returns:
        tuple: مدل‌های پایگاه داده
    """
    from models import User, CryptoQuiz, UserQuizAttempt, UserQuizScore
    return User, CryptoQuiz, UserQuizAttempt, UserQuizScore