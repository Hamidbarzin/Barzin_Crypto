"""
Scheduler module for periodically running analysis and sending notifications
"""

import logging
import schedule
import threading
import time
from datetime import datetime

from crypto_bot.market_data import get_current_prices
from crypto_bot.signal_generator import generate_signals
from crypto_bot.email_service import send_signal_notification
from crypto_bot.config import DEFAULT_ANALYSIS_INTERVAL, EMAIL_FREQUENCIES

logger = logging.getLogger(__name__)

# Global flag to control the scheduler thread
scheduler_running = False
scheduler_thread = None

def analyze_and_notify(email_settings, watched_currencies):
    """
    Analyze cryptocurrencies and send notification if needed
    
    Args:
        email_settings (dict): Email settings
        watched_currencies (list): List of currencies to analyze
    """
    try:
        logger.info(f"Running scheduled analysis for {len(watched_currencies)} currencies")
        
        # Generate signals
        signals = generate_signals(watched_currencies)
        
        # Check if there are any actionable signals (Buy or Sell)
        actionable_signals = {s: data for s, data in signals.items() 
                             if data['signal'] in ['Strong Buy', 'Buy', 'Strong Sell', 'Sell']}
        
        # Log the results
        if actionable_signals:
            logger.info(f"Found {len(actionable_signals)} actionable signals")
            
            # Send email if email notifications are enabled
            if email_settings.get('enabled') and email_settings.get('email'):
                send_signal_notification(email_settings, signals)
            else:
                logger.debug("Email notifications disabled, not sending email")
        else:
            logger.info("No actionable signals found")
            
    except Exception as e:
        logger.error(f"Error in scheduled analysis: {str(e)}")

def scheduler_loop():
    """
    Main scheduler loop that runs in a separate thread
    """
    global scheduler_running
    
    logger.info("Scheduler thread started")
    
    while scheduler_running:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}")

def start_scheduler(email_settings, watched_currencies):
    """
    Start the scheduler to periodically analyze cryptocurrencies
    
    Args:
        email_settings (dict): Email settings
        watched_currencies (list): List of currencies to watch
    """
    global scheduler_running, scheduler_thread
    
    if scheduler_running:
        logger.warning("Scheduler is already running")
        return
    
    try:
        # Clear existing jobs
        schedule.clear()
        
        # Set up recurring job for analysis
        schedule.every(DEFAULT_ANALYSIS_INTERVAL).seconds.do(
            analyze_and_notify, email_settings, watched_currencies
        )
        
        # Start the scheduler thread
        scheduler_running = True
        scheduler_thread = threading.Thread(target=scheduler_loop)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logger.info("Scheduler started successfully")
        
        # Run immediately for the first time
        analyze_and_notify(email_settings, watched_currencies)
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        scheduler_running = False

def stop_scheduler():
    """
    Stop the scheduler
    """
    global scheduler_running, scheduler_thread
    
    if not scheduler_running:
        logger.warning("Scheduler is not running")
        return
    
    try:
        scheduler_running = False
        if scheduler_thread and scheduler_thread.is_alive():
            # Wait for the thread to terminate (should be quick since we check the flag every second)
            scheduler_thread.join(timeout=5)
            
        schedule.clear()
        logger.info("Scheduler stopped successfully")
        
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
