#!/usr/bin/env python3
"""
سرویس کوییز دانش ارزهای دیجیتال

این ماژول توابع مربوط به مدیریت کوییز دانش ارزهای دیجیتال را ارائه می‌دهد.
"""

import logging
import json
import random
from datetime import datetime
import os
from crypto_bot.database import get_db, get_models

# دریافت شی پایگاه داده و مدل‌ها
db = get_db()
User, CryptoQuiz, UserQuizAttempt, UserQuizScore = get_models()

# تنظیم لاگ
logger = logging.getLogger(__name__)

# ثابت‌های کوییز
BADGE_LEVELS = {
    'beginner': 50,
    'novice': 100,
    'intermediate': 200,
    'advanced': 400,
    'expert': 800,
    'master': 1500,
    'crypto_genius': 3000
}

DIFFICULTY_POINTS = {
    'easy': 5,
    'medium': 10,
    'hard': 20
}

LEVEL_THRESHOLDS = {
    1: 0,
    2: 50,
    3: 150,
    4: 300,
    5: 600,
    6: 1000,
    7: 1500,
    8: 2500,
    9: 4000,
    10: 6000
}

DEFAULT_QUIZ_QUESTIONS = [
    {
        'question': 'What is Bitcoin?',
        'difficulty': 'easy',
        'category': 'bitcoin',
        'option_a': 'A digital currency',
        'option_b': 'A social media platform',
        'option_c': 'A web browser',
        'option_d': 'An email service',
        'correct_answer': 'a',
        'explanation': 'Bitcoin is the first decentralized digital currency that allows peer-to-peer transactions without an intermediary.'
    },
    {
        'question': 'Who created Bitcoin?',
        'difficulty': 'easy',
        'category': 'bitcoin',
        'option_a': 'Elon Musk',
        'option_b': 'Satoshi Nakamoto',
        'option_c': 'Bill Gates',
        'option_d': 'Mark Zuckerberg',
        'correct_answer': 'b',
        'explanation': 'Bitcoin was created by an anonymous person or group using the pseudonym Satoshi Nakamoto in 2008.'
    },
    {
        'question': 'What is the maximum supply of Bitcoin?',
        'difficulty': 'medium',
        'category': 'bitcoin',
        'option_a': '1 million',
        'option_b': '21 million',
        'option_c': '100 million',
        'option_d': 'Unlimited',
        'correct_answer': 'b',
        'explanation': 'Bitcoin has a fixed maximum supply of 21 million coins, which makes it a deflationary asset.'
    },
    {
        'question': 'What is a blockchain?',
        'difficulty': 'medium',
        'category': 'general',
        'option_a': 'A type of cryptocurrency',
        'option_b': 'A decentralized database or ledger',
        'option_c': 'A hardware wallet',
        'option_d': 'A mining computer',
        'correct_answer': 'b',
        'explanation': 'A blockchain is a distributed, decentralized ledger that records transactions across multiple computers.'
    },
    {
        'question': 'What is a smart contract?',
        'difficulty': 'medium',
        'category': 'general',
        'option_a': 'A legal agreement for buying crypto',
        'option_b': 'A self-executing contract with the terms written in code',
        'option_c': 'A hardware device for storing crypto',
        'option_d': 'A contract that requires KYC verification',
        'correct_answer': 'b',
        'explanation': 'Smart contracts are self-executing contracts where the terms are directly written into code and automatically execute when conditions are met.'
    },
    {
        'question': 'Which consensus mechanism does Bitcoin use?',
        'difficulty': 'hard',
        'category': 'bitcoin',
        'option_a': 'Proof of Stake (PoS)',
        'option_b': 'Proof of Work (PoW)',
        'option_c': 'Delegated Proof of Stake (DPoS)',
        'option_d': 'Proof of Authority (PoA)',
        'correct_answer': 'b',
        'explanation': 'Bitcoin uses Proof of Work (PoW), which requires miners to solve complex mathematical problems to validate transactions and create new blocks.'
    },
    {
        'question': 'What is the primary cryptocurrency on the Ethereum network?',
        'difficulty': 'easy',
        'category': 'general',
        'option_a': 'Bitcoin',
        'option_b': 'Litecoin',
        'option_c': 'Ether (ETH)',
        'option_d': 'Cardano (ADA)',
        'correct_answer': 'c',
        'explanation': 'Ether (ETH) is the native cryptocurrency of the Ethereum blockchain platform.'
    },
    {
        'question': 'What is a "whale" in cryptocurrency terms?',
        'difficulty': 'medium',
        'category': 'general',
        'option_a': 'A new type of cryptocurrency',
        'option_b': 'An individual or entity that holds a large amount of a cryptocurrency',
        'option_c': 'A type of blockchain attack',
        'option_d': 'A mining pool',
        'correct_answer': 'b',
        'explanation': 'A "whale" refers to an individual or entity that holds a large amount of a particular cryptocurrency, enough to potentially influence the market price.'
    },
    {
        'question': 'What is a Bitcoin halving?',
        'difficulty': 'medium',
        'category': 'bitcoin',
        'option_a': 'When Bitcoin price cuts in half',
        'option_b': 'When the Bitcoin network splits into two',
        'option_c': 'When the reward for mining Bitcoin blocks is cut in half',
        'option_d': 'When transaction fees are reduced by 50%',
        'correct_answer': 'c',
        'explanation': 'A Bitcoin halving is an event where the reward for mining new blocks is cut in half, which happens approximately every four years.'
    },
    {
        'question': 'What does "HODL" stand for in crypto communities?',
        'difficulty': 'easy',
        'category': 'general',
        'option_a': 'Hold On for Dear Life',
        'option_b': 'High-Oscillation Digital Ledger',
        'option_c': 'It was a typo for "hold" that became a meme',
        'option_d': 'Highly Optimized Decentralized Liquidity',
        'correct_answer': 'c',
        'explanation': 'HODL originated from a typo in a Bitcoin forum where someone wrote "HODL" instead of "HOLD" in 2013, which then became a backronym for "Hold On for Dear Life."'
    }
]

def load_default_quiz_questions():
    """
    بارگذاری سوالات پیش‌فرض کوییز به پایگاه داده
    """
    try:
        # بررسی اینکه آیا سوالاتی در پایگاه داده وجود دارد
        existing_count = CryptoQuiz.query.count()
        
        if existing_count == 0:
            # اگر سوالی در پایگاه داده نیست، سوالات پیش‌فرض را اضافه کن
            for question_data in DEFAULT_QUIZ_QUESTIONS:
                question = CryptoQuiz(
                    question=question_data['question'],
                    difficulty=question_data['difficulty'],
                    category=question_data['category'],
                    option_a=question_data['option_a'],
                    option_b=question_data['option_b'],
                    option_c=question_data['option_c'],
                    option_d=question_data['option_d'],
                    correct_answer=question_data['correct_answer'],
                    explanation=question_data['explanation'],
                    points=DIFFICULTY_POINTS.get(question_data['difficulty'], 10)
                )
                db.session.add(question)
            
            db.session.commit()
            logger.info(f"Added {len(DEFAULT_QUIZ_QUESTIONS)} default quiz questions to database")
            return True
        else:
            logger.info(f"Database already has {existing_count} quiz questions, skipping default import")
            return False
    except Exception as e:
        logger.error(f"Error loading default quiz questions: {str(e)}")
        db.session.rollback()
        return False

def get_random_quiz_question(difficulty=None, category=None, exclude_ids=None):
    """
    دریافت یک سوال کوییز تصادفی
    
    Args:
        difficulty (str, optional): سختی سوال (easy, medium, hard)
        category (str, optional): دسته‌بندی سوال
        exclude_ids (list, optional): لیست شناسه‌های سوالاتی که باید حذف شوند
        
    Returns:
        CryptoQuiz: یک شیء سوال کوییز
    """
    query = CryptoQuiz.query
    
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    if category:
        query = query.filter_by(category=category)
    
    if exclude_ids:
        query = query.filter(~CryptoQuiz.id.in_(exclude_ids))
    
    # تعداد کل سوالات مطابق با فیلترها
    count = query.count()
    
    if count == 0:
        # اگر سوالی پیدا نشد، بدون فیلتر جستجو کن
        query = CryptoQuiz.query
        if exclude_ids:
            query = query.filter(~CryptoQuiz.id.in_(exclude_ids))
        count = query.count()
        
        if count == 0:
            return None
    
    # انتخاب یک سوال تصادفی
    random_offset = random.randint(0, count - 1)
    return query.offset(random_offset).first()

def get_quiz_questions(count=5, difficulty=None, category=None):
    """
    دریافت چند سوال کوییز
    
    Args:
        count (int): تعداد سوالات درخواستی
        difficulty (str, optional): سختی سوالات
        category (str, optional): دسته‌بندی سوالات
        
    Returns:
        list: لیستی از سوالات کوییز
    """
    questions = []
    exclude_ids = []
    
    for _ in range(count):
        question = get_random_quiz_question(difficulty, category, exclude_ids)
        if question:
            questions.append(question)
            exclude_ids.append(question.id)
    
    return questions

def submit_quiz_answer(user_id, quiz_id, answer):
    """
    ثبت پاسخ کاربر به یک سوال کوییز
    
    Args:
        user_id (int): شناسه کاربر
        quiz_id (int): شناسه سوال کوییز
        answer (str): پاسخ کاربر (a, b, c, d)
        
    Returns:
        dict: نتیجه عملیات شامل صحت پاسخ و امتیاز کسب شده
    """
    try:
        # اگر user_id صفر باشد، به جای آن از session storage استفاده کنیم
        if user_id == 0:
            # در صورت عدم وجود کاربر با شناسه 0، از امتیازات موقت استفاده می‌کنیم
            # و نتایج را برمی‌گردانیم بدون اینکه در پایگاه داده ذخیره کنیم
            
            # دریافت سوال کوییز
            quiz = CryptoQuiz.query.get(quiz_id)
            if not quiz:
                return {
                    'success': False,
                    'message': 'Quiz question not found'
                }
            
            # بررسی صحت پاسخ
            is_correct = answer.lower() == quiz.correct_answer.lower()
            points_earned = quiz.points if is_correct else 0
            
            return {
                'success': True,
                'is_correct': is_correct,
                'points_earned': points_earned,
                'correct_answer': quiz.correct_answer,
                'explanation': quiz.explanation,
                'total_points': points_earned,  # فقط امتیاز همین سوال
                'level': 1,  # سطح پیش‌فرض
                'level_up': False,
                'badges': [],
                'guest_mode': True  # نشان‌دهنده حالت مهمان
            }
        
        # بررسی اینکه آیا کاربر در پایگاه داده وجود دارد
        user = User.query.get(user_id)
        if not user:
            # اگر کاربر وجود نداشت، یک کاربر مهمان موقت ایجاد می‌کنیم
            try:
                guest_username = f"guest_{user_id}_{int(datetime.now().timestamp())}"
                new_user = User(
                    id=user_id,
                    username=guest_username,
                    is_admin=False
                )
                # تنظیم یک رمز عبور پیش‌فرض
                new_user.set_password("guest_password")  
                db.session.add(new_user)
                db.session.commit()
                logger.info(f"Created temporary guest user with ID {user_id}")
            except Exception as user_error:
                logger.error(f"Error creating guest user: {str(user_error)}")
                # اگر نتوانستیم کاربر ایجاد کنیم، حالت مهمان را برمی‌گردانیم
                quiz = CryptoQuiz.query.get(quiz_id)
                if not quiz:
                    return {
                        'success': False,
                        'message': 'Quiz question not found'
                    }
                
                is_correct = answer.lower() == quiz.correct_answer.lower()
                points_earned = quiz.points if is_correct else 0
                
                return {
                    'success': True,
                    'is_correct': is_correct,
                    'points_earned': points_earned,
                    'correct_answer': quiz.correct_answer,
                    'explanation': quiz.explanation,
                    'total_points': points_earned,
                    'level': 1,
                    'level_up': False,
                    'badges': [],
                    'guest_mode': True
                }
        
        # بررسی اینکه آیا کاربر قبلاً به این سوال پاسخ داده است
        existing_attempt = UserQuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
        
        if existing_attempt:
            return {
                'success': False,
                'message': 'You have already answered this question'
            }
        
        # دریافت سوال کوییز
        quiz = CryptoQuiz.query.get(quiz_id)
        if not quiz:
            return {
                'success': False,
                'message': 'Quiz question not found'
            }
        
        # بررسی صحت پاسخ
        is_correct = answer.lower() == quiz.correct_answer.lower()
        points_earned = quiz.points if is_correct else 0
        
        # ذخیره تلاش کاربر
        attempt = UserQuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            answer=answer.lower(),
            is_correct=is_correct,
            points_earned=points_earned
        )
        db.session.add(attempt)
        
        # بروزرسانی امتیاز کلی کاربر
        user_score = UserQuizScore.query.filter_by(user_id=user_id).first()
        
        if not user_score:
            # ایجاد رکورد امتیاز برای کاربر اگر وجود ندارد
            user_score = UserQuizScore(user_id=user_id)
            db.session.add(user_score)
        
        # بروزرسانی امتیازات
        user_score.total_questions += 1
        
        if is_correct:
            user_score.total_correct += 1
            user_score.total_points += points_earned
        
        user_score.last_quiz_date = datetime.now()
        
        # بررسی ارتقای سطح
        new_level = calculate_level(user_score.total_points)
        level_up = False
        
        if new_level > user_score.level:
            level_up = True
            user_score.level = new_level
        
        # بررسی نشان‌های جدید
        badges = get_user_badges(user_score.total_points)
        user_score.badges = json.dumps(badges)
        
        db.session.commit()
        
        return {
            'success': True,
            'is_correct': is_correct,
            'points_earned': points_earned,
            'correct_answer': quiz.correct_answer,
            'explanation': quiz.explanation,
            'total_points': user_score.total_points,
            'level': user_score.level,
            'level_up': level_up,
            'badges': badges,
            'guest_mode': False
        }
    
    except Exception as e:
        logger.error(f"Error submitting quiz answer: {str(e)}")
        db.session.rollback()
        return {
            'success': False,
            'message': f"An error occurred: {str(e)}"
        }

def calculate_level(points):
    """
    محاسبه سطح کاربر بر اساس امتیازات
    
    Args:
        points (int): مجموع امتیازات کاربر
        
    Returns:
        int: سطح کاربر
    """
    for level, threshold in sorted(LEVEL_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
        if points >= threshold:
            return level
    
    return 1  # سطح پیش‌فرض

def get_user_badges(points):
    """
    دریافت نشان‌های کاربر بر اساس امتیازات
    
    Args:
        points (int): مجموع امتیازات کاربر
        
    Returns:
        list: لیست نشان‌های کسب شده
    """
    earned_badges = []
    
    for badge, threshold in sorted(BADGE_LEVELS.items(), key=lambda x: x[1]):
        if points >= threshold:
            earned_badges.append(badge)
    
    return earned_badges

def get_user_stats(user_id):
    """
    دریافت آمار کاربر در کوییز
    
    Args:
        user_id (int): شناسه کاربر
        
    Returns:
        dict: آمار کاربر
    """
    user_score = UserQuizScore.query.filter_by(user_id=user_id).first()
    
    if not user_score:
        return {
            'total_points': 0,
            'total_correct': 0,
            'total_questions': 0,
            'accuracy': 0,
            'level': 1,
            'badges': [],
            'next_level': 2,
            'points_to_next_level': LEVEL_THRESHOLDS[2]
        }
    
    # محاسبه دقت
    accuracy = 0
    if user_score.total_questions > 0:
        accuracy = (user_score.total_correct / user_score.total_questions) * 100
    
    # محاسبه سطح بعدی
    current_level = user_score.level
    next_level = current_level + 1
    
    if next_level in LEVEL_THRESHOLDS:
        points_to_next_level = LEVEL_THRESHOLDS[next_level] - user_score.total_points
    else:
        next_level = current_level
        points_to_next_level = 0
    
    # دریافت نشان‌ها
    badges = []
    if user_score.badges:
        try:
            badges = json.loads(user_score.badges)
        except:
            badges = []
    
    return {
        'total_points': user_score.total_points,
        'total_correct': user_score.total_correct,
        'total_questions': user_score.total_questions,
        'accuracy': round(accuracy, 1),
        'level': user_score.level,
        'badges': badges,
        'next_level': next_level,
        'points_to_next_level': points_to_next_level
    }

def get_leaderboard(limit=10):
    """
    دریافت جدول رتبه‌بندی کاربران
    
    Args:
        limit (int): تعداد کاربران درخواستی
        
    Returns:
        list: لیست کاربران برتر
    """
    # پیدا کردن کاربران با بیشترین امتیاز
    top_users = (
        db.session.query(
            UserQuizScore, 
            User.username
        )
        .join(User, UserQuizScore.user_id == User.id)
        .order_by(UserQuizScore.total_points.desc())
        .limit(limit)
        .all()
    )
    
    leaderboard = []
    
    for idx, (score, username) in enumerate(top_users, 1):
        leaderboard.append({
            'rank': idx,
            'username': username,
            'points': score.total_points,
            'level': score.level,
            'correct_answers': score.total_correct,
            'total_questions': score.total_questions,
            'accuracy': round((score.total_correct / score.total_questions * 100), 1) if score.total_questions > 0 else 0
        })
    
    return leaderboard