#!/usr/bin/env python3
"""
روت‌های مربوط به کوییز دانش ارزهای دیجیتال

این ماژول روت‌های مربوط به صفحات کوییز و مدیریت آن را ارائه می‌دهد.
"""

import logging
import json
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from crypto_bot.crypto_quiz_service import (
    load_default_quiz_questions,
    get_quiz_questions,
    submit_quiz_answer,
    get_user_stats,
    get_leaderboard
)
from crypto_bot.database import get_db, get_models

# دریافت شی پایگاه داده و مدل‌ها
db = get_db()
User, CryptoQuiz, UserQuizAttempt, UserQuizScore = get_models()

# تنظیم لاگ
logger = logging.getLogger(__name__)

def register_routes(app):
    """
    ثبت روت‌های کوییز با برنامه فلسک
    
    Args:
        app: برنامه فلسک
    """
    
    @app.route('/crypto-quiz')
    def crypto_quiz_home():
        """صفحه اصلی کوییز دانش ارزهای دیجیتال"""
        # بارگذاری اولیه سوالات
        load_default_quiz_questions()
        
        # دریافت آمار کاربر
        user_id = session.get('user_id', 0)
        user_stats = get_user_stats(user_id)
        
        # دریافت لیدربورد
        leaderboard = get_leaderboard(10)
        
        # دریافت ۵ سوال تصادفی برای مثال
        categories = db.session.query(CryptoQuiz.category).distinct().all()
        categories = [category[0] for category in categories]
        
        return render_template(
            'crypto_quiz_home.html',
            user_stats=user_stats,
            leaderboard=leaderboard,
            categories=categories
        )
    
    @app.route('/crypto-quiz/start')
    def crypto_quiz_start():
        """شروع یک کوییز جدید"""
        # دریافت پارامترها
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        count = request.args.get('count', 5, type=int)
        
        # محدود کردن تعداد سوالات
        if count < 1:
            count = 1
        elif count > 10:
            count = 10
        
        # دریافت سوالات
        questions = get_quiz_questions(count, difficulty, category)
        
        if not questions:
            flash('No questions available for the selected criteria. Try different options.', 'warning')
            return redirect(url_for('crypto_quiz_home'))
        
        # ذخیره سوالات در session
        session['quiz_questions'] = [q.id for q in questions]
        session['current_question'] = 0
        session['quiz_score'] = 0
        session['quiz_correct'] = 0
        
        # هدایت به سوال اول
        return redirect(url_for('crypto_quiz_question'))
    
    @app.route('/crypto-quiz/question', methods=['GET', 'POST'])
    def crypto_quiz_question():
        """نمایش سوال کوییز و پردازش پاسخ"""
        # بررسی اینکه آیا کوییز آغاز شده است
        if 'quiz_questions' not in session:
            flash('Please start a quiz first!', 'warning')
            return redirect(url_for('crypto_quiz_home'))
        
        # بررسی وضعیت کوییز
        quiz_questions = session.get('quiz_questions', [])
        current_index = session.get('current_question', 0)
        
        if current_index >= len(quiz_questions):
            # کوییز تمام شده است
            return redirect(url_for('crypto_quiz_result'))
        
        # دریافت سوال فعلی
        question_id = quiz_questions[current_index]
        question = CryptoQuiz.query.get(question_id)
        
        if not question:
            flash('Question not found. Please try again.', 'error')
            return redirect(url_for('crypto_quiz_home'))
        
        # پردازش پاسخ
        if request.method == 'POST':
            user_answer = request.form.get('answer')
            user_id = session.get('user_id', 0)
            
            if not user_answer:
                flash('Please select an answer', 'warning')
                return render_template('crypto_quiz_question.html', 
                                      question=question, 
                                      current=current_index + 1,
                                      total=len(quiz_questions))
            
            # ثبت پاسخ
            result = submit_quiz_answer(user_id, question_id, user_answer)
            
            if result['success']:
                # بروزرسانی امتیازات session
                if result['is_correct']:
                    session['quiz_correct'] = session.get('quiz_correct', 0) + 1
                    session['quiz_score'] = session.get('quiz_score', 0) + result['points_earned']
                
                # ذخیره نتیجه در session
                session['last_answer_result'] = {
                    'is_correct': result['is_correct'],
                    'correct_answer': result['correct_answer'],
                    'explanation': result['explanation'],
                    'user_answer': user_answer,
                    'question_text': question.question
                }
                
                # حرکت به سوال بعدی
                session['current_question'] = current_index + 1
                
                # هدایت به صفحه نتیجه سوال
                return redirect(url_for('crypto_quiz_answer_result'))
            else:
                flash(result['message'], 'error')
        
        # نمایش سوال
        return render_template('crypto_quiz_question.html', 
                              question=question, 
                              current=current_index + 1,
                              total=len(quiz_questions))
    
    @app.route('/crypto-quiz/answer-result')
    def crypto_quiz_answer_result():
        """نمایش نتیجه پاسخ به سوال"""
        # بررسی اینکه آیا نتیجه‌ای وجود دارد
        if 'last_answer_result' not in session:
            return redirect(url_for('crypto_quiz_question'))
        
        result = session['last_answer_result']
        quiz_questions = session.get('quiz_questions', [])
        current_index = session.get('current_question', 0)
        
        # دریافت سوال فعلی
        if current_index > 0 and current_index <= len(quiz_questions):
            question_id = quiz_questions[current_index - 1]
            question = CryptoQuiz.query.get(question_id)
        else:
            # اگر شماره سوال اشتباه باشد، به صفحه خانه برگرد
            flash('Question not found', 'error')
            return redirect(url_for('crypto_quiz_home'))
        
        # بررسی اینکه آیا این آخرین سوال بود
        is_last_question = current_index >= len(quiz_questions)
        
        return render_template('crypto_quiz_answer_result.html',
                              result=result,
                              question=question,
                              quiz_score=session.get('quiz_score', 0),
                              quiz_correct=session.get('quiz_correct', 0),
                              total_questions=len(quiz_questions),
                              current_question=current_index,
                              is_last_question=is_last_question)
    
    @app.route('/crypto-quiz/result')
    def crypto_quiz_result():
        """نمایش نتیجه نهایی کوییز"""
        # بررسی اینکه آیا کوییز انجام شده است
        if 'quiz_questions' not in session:
            flash('No quiz results available', 'warning')
            return redirect(url_for('crypto_quiz_home'))
        
        # دریافت آمار
        user_id = session.get('user_id', 0)
        user_stats = get_user_stats(user_id)
        
        # امتیازات کوییز فعلی
        quiz_score = session.get('quiz_score', 0)
        quiz_correct = session.get('quiz_correct', 0)
        total_questions = len(session.get('quiz_questions', []))
        
        # پاک کردن داده‌های کوییز از session
        for key in ['quiz_questions', 'current_question', 'quiz_score', 'quiz_correct', 'last_answer_result']:
            if key in session:
                session.pop(key)
        
        return render_template('crypto_quiz_result.html',
                              quiz_score=quiz_score,
                              quiz_correct=quiz_correct,
                              total_questions=total_questions,
                              user_stats=user_stats)
    
    @app.route('/crypto-quiz/leaderboard')
    def crypto_quiz_leaderboard():
        """صفحه لیدربورد کوییز"""
        leaderboard = get_leaderboard(50)
        
        return render_template('crypto_quiz_leaderboard.html',
                              leaderboard=leaderboard)
    
    @app.route('/crypto-quiz/profile')
    def crypto_quiz_profile():
        """صفحه پروفایل کاربر در کوییز"""
        user_id = session.get('user_id', 0)
        user_stats = get_user_stats(user_id)
        
        # دریافت تاریخچه کوییز کاربر
        from models import UserQuizAttempt
        
        recent_attempts = (
            UserQuizAttempt.query.filter_by(user_id=user_id)
            .order_by(UserQuizAttempt.timestamp.desc())
            .limit(20)
            .all()
        )
        
        history = []
        for attempt in recent_attempts:
            quiz = CryptoQuiz.query.get(attempt.quiz_id)
            if quiz:
                history.append({
                    'question': quiz.question,
                    'user_answer': attempt.answer,
                    'correct_answer': quiz.correct_answer,
                    'is_correct': attempt.is_correct,
                    'points': attempt.points_earned,
                    'timestamp': attempt.timestamp
                })
        
        return render_template('crypto_quiz_profile.html',
                              user_stats=user_stats,
                              history=history)
    
    @app.route('/api/crypto-quiz/stats')
    def api_crypto_quiz_stats():
        """
        API برای دریافت آمار کاربر در کوییز
        """
        user_id = session.get('user_id', 0)
        user_stats = get_user_stats(user_id)
        
        return jsonify(user_stats)