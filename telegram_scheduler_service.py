#!/usr/bin/env python3
"""
Internal Telegram Scheduling Service

This module provides a scheduling service for automatically sending Telegram messages
using the replit_telegram_sender module.
"""

import threading
import time
import logging
import datetime
import pytz
import replit_telegram_sender
import os
import json
from crypto_bot.price_alert_service import check_price_alerts

# Setup logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("telegram_scheduler")

# Toronto timezone
toronto_tz = pytz.timezone('America/Toronto')

# Settings file path
SETTINGS_FILE = "telegram_scheduler_settings.json"

class TelegramSchedulerService:
    """
    Telegram Scheduling Service Class
    
    This class creates a separate thread for scheduling Telegram messages
    that automatically sends Telegram messages.
    """
    
    def __init__(self):
        """
        Initialize the class
        """
        self.thread = None
        self.running = False
        self.system_report_counter = 0
        self.technical_analysis_counter = 0
        self.trading_signals_counter = 0
        self.crypto_news_counter = 0
        self.interval = 3600  # 1 hour = 3600 seconds
        self.system_report_interval = 12  # Every 12 times (6 hours)
        self.technical_analysis_interval = 4  # Every 4 times (2 hours)
        self.trading_signals_interval = 8  # Every 8 times (4 hours)
        self.crypto_news_interval = 16  # Every 16 times (8 hours)
        
        # Default user-configurable settings
        self.active_hours_start = 8  # Start hour (8 AM)
        self.active_hours_end = 22   # End hour (10 PM)
        self.message_sending_enabled = True  # Is message sending enabled?
        self.auto_start_on_boot = True  # Should the service start automatically on boot?
        
        # Important coins for technical analysis
        self.important_coins = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"]
        self.current_coin_index = 0
        
        # Load settings from file if they exist
        self._load_settings()
    
    def start(self):
        """
        Start the scheduling service
        
        Returns:
            bool: Service startup status
        """
        if self.running:
            logger.warning("Service is already running")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.start()
        
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"Telegram scheduling service started ({now_toronto.strftime('%Y-%m-%d %H:%M:%S')} Toronto)")
        
        # Send test message at startup
        self._send_test_message()
        
        return True
    
    def stop(self):
        """
        Stop the scheduling service
        
        Returns:
            bool: Service stop status
        """
        if not self.running:
            logger.warning("Service is not running")
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(1.0)  # Wait maximum 1 second for thread termination
            
        logger.info("Telegram scheduling service stopped")
        return True
    
    def status(self):
        """
        Get service status
        
        Returns:
            dict: Service status
        """
        return {
            "running": self.running,
            "message_sending_enabled": self.message_sending_enabled,
            "auto_start_on_boot": self.auto_start_on_boot,
            "active_hours_start": self.active_hours_start,
            "active_hours_end": self.active_hours_end,
            "interval": self.interval,
            "system_report_counter": self.system_report_counter,
            "technical_analysis_counter": self.technical_analysis_counter,
            "trading_signals_counter": self.trading_signals_counter,
            "crypto_news_counter": self.crypto_news_counter,
            "next_price_report": self._get_next_report_time(),
            "next_system_report": self._get_next_system_report_time(),
            "next_technical_analysis": self._get_next_technical_analysis_time(),
            "next_trading_signals": self._get_next_trading_signals_time(),
            "next_crypto_news": self._get_next_crypto_news_time(),
            "next_coin_for_analysis": self.important_coins[self.current_coin_index]
        }
    
    def _scheduler_loop(self):
        """
        Main scheduling loop
        
        This method runs in a separate thread and is responsible for sending
        scheduled messages.
        
        For the replit environment, we use smaller time intervals so that
        if the thread is interrupted, we detect the problem sooner
        """
        try:
            # Send initial price report
            logger.info("Sending initial price report...")
            self._send_price_report()
            
            # Counter for sending messages every 1 hour
            counter = 0
            # Smaller interval for status checks - default was 5 minutes (300 seconds)
            # Increased to 60 minutes (3600 seconds) to match the reporting interval
            small_interval = 3600  # 60 minutes
            ticks_for_report = 1  # Send report once per interval
            
            while self.running:
                # Sleep with smaller interval for better control
                time.sleep(small_interval)
                
                if not self.running:
                    break
                
                # Check current time in Toronto
                now_toronto = datetime.datetime.now(toronto_tz)
                current_hour = now_toronto.hour
                
                # Only send between specified hours
                is_active_hours = self.active_hours_start <= current_hour < self.active_hours_end
                
                # If message sending is disabled, not active
                is_active_hours = is_active_hours and self.message_sending_enabled
                
                counter += 1
                logger.info(f"Tick {counter} of {ticks_for_report} for next report")
                
                # Send price report every 1 hour (if in active hours)
                if counter >= ticks_for_report and is_active_hours:
                    logger.info("Time to send price report...")
                    self._send_price_report()
                    counter = 0
                # If we reached the required number of ticks but are in inactive hours, just reset the counter
                elif counter >= ticks_for_report and not is_active_hours:
                    if not self.message_sending_enabled:
                        logger.info("Message sending disabled, report not sent")
                    else:
                        logger.info(f"Outside active hours ({self.active_hours_start} AM to {self.active_hours_end} PM), report not sent")
                    counter = 0
                
                # Only check price alerts once per hour (to avoid checking too frequently)
                # This helps prevent spam notifications
                if counter == 1:
                    try:
                        self._check_price_alerts()
                    except Exception as e:
                        logger.error(f"Error checking price alerts: {str(e)}")
                
                # Increment counters
                self.system_report_counter += 1
                self.technical_analysis_counter += 1
                self.trading_signals_counter += 1
                self.crypto_news_counter += 1
                
                # Only if message sending is active, send reports
                if self.message_sending_enabled and is_active_hours:
                    # Send system report every 6 hours
                    if self.system_report_counter >= self.system_report_interval:
                        self._send_system_report()
                        self.system_report_counter = 0
                    
                    # Send technical analysis every 2 hours
                    if self.technical_analysis_counter >= self.technical_analysis_interval:
                        self._send_technical_analysis()
                        self.technical_analysis_counter = 0
                    
                    # Send trading signals every 4 hours
                    if self.trading_signals_counter >= self.trading_signals_interval:
                        self._send_trading_signals()
                        self.trading_signals_counter = 0
                        
                    # Send crypto news every 8 hours
                    if self.crypto_news_counter >= self.crypto_news_interval:
                        self._send_crypto_news()
                        self.crypto_news_counter = 0
                elif not self.message_sending_enabled and (self.system_report_counter >= self.system_report_interval or 
                      self.technical_analysis_counter >= self.technical_analysis_interval or
                      self.trading_signals_counter >= self.trading_signals_interval or
                      self.crypto_news_counter >= self.crypto_news_interval):
                    # Reset counters when they reach maximum values
                    if self.system_report_counter >= self.system_report_interval:
                        logger.info("Message sending disabled, system report not sent")
                        self.system_report_counter = 0
                    
                    if self.technical_analysis_counter >= self.technical_analysis_interval:
                        logger.info("Message sending disabled, technical analysis not sent")
                        self.technical_analysis_counter = 0
                    
                    if self.trading_signals_counter >= self.trading_signals_interval:
                        logger.info("Message sending disabled, trading signals not sent")
                        self.trading_signals_counter = 0
                    
                    if self.crypto_news_counter >= self.crypto_news_interval:
                        logger.info("Message sending disabled, crypto news not sent")
                        self.crypto_news_counter = 0
        
        except Exception as e:
            logger.error(f"Error in scheduling loop: {str(e)}")
            self.running = False
    
    def _send_price_report(self):
        """
        Send price report
        
        Returns:
            bool: Success or failure of message sending
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"Sending price report ({now_toronto.strftime('%H:%M:%S')} Toronto)...")
        
        try:
            success = replit_telegram_sender.send_price_report()
            if success:
                logger.info("Price report sent successfully")
            else:
                logger.error("Error sending price report")
            return success
        except Exception as e:
            logger.error(f"Exception in sending price report: {str(e)}")
            return False
    
    def _send_system_report(self):
        """
        Send system report
        
        Returns:
            bool: Success or failure of message sending
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"Sending system report ({now_toronto.strftime('%H:%M:%S')} Toronto)...")
        
        try:
            success = replit_telegram_sender.send_system_report()
            if success:
                logger.info("System report sent successfully")
            else:
                logger.error("Error sending system report")
            return success
        except Exception as e:
            logger.error(f"Exception in sending system report: {str(e)}")
            return False
    
    def _send_test_message(self):
        """
        Send test message
        
        Returns:
            bool: Success or failure of message sending
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"Sending test message ({now_toronto.strftime('%H:%M:%S')} Toronto)...")
        
        try:
            success = replit_telegram_sender.send_test_message()
            if success:
                logger.info("Test message sent successfully")
            else:
                logger.error("Error sending test message")
            return success
        except Exception as e:
            logger.error(f"Exception in sending test message: {str(e)}")
            return False
    
    def _get_next_report_time(self):
        """
        Calculate next report time
        
        Returns:
            str: Next report time
        """
        if not self.running:
            return "Service is not running"
        
        now = datetime.datetime.now(toronto_tz)
        next_time = now + datetime.timedelta(seconds=self.interval)
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_next_system_report_time(self):
        """
        Calculate next system report time
        
        Returns:
            str: Next system report time
        """
        if not self.running:
            return "Service is not running"
        
        now = datetime.datetime.now(toronto_tz)
        reports_left = self.system_report_interval - self.system_report_counter
        seconds_left = reports_left * self.interval
        next_time = now + datetime.timedelta(seconds=seconds_left)
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_next_technical_analysis_time(self):
        """
        Calculate next technical analysis time
        
        Returns:
            str: Next technical analysis time
        """
        if not self.running:
            return "Service is not running"
        
        now = datetime.datetime.now(toronto_tz)
        reports_left = self.technical_analysis_interval - self.technical_analysis_counter
        seconds_left = reports_left * self.interval
        next_time = now + datetime.timedelta(seconds=seconds_left)
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_next_trading_signals_time(self):
        """
        Calculate next trading signals time
        
        Returns:
            str: Next trading signals time
        """
        if not self.running:
            return "Service is not running"
        
        now = datetime.datetime.now(toronto_tz)
        reports_left = self.trading_signals_interval - self.trading_signals_counter
        seconds_left = reports_left * self.interval
        next_time = now + datetime.timedelta(seconds=seconds_left)
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
        
    def _send_technical_analysis(self):
        """
        Send technical analysis for a currency
        
        Returns:
            bool: Success or failure of sending analysis
        """
        # Select the currency to analyze
        symbol = self.important_coins[self.current_coin_index]
        
        # Update index for next time
        self.current_coin_index = (self.current_coin_index + 1) % len(self.important_coins)
        
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"Sending technical analysis for {symbol} ({now_toronto.strftime('%H:%M:%S')} Toronto)...")
        
        try:
            success = replit_telegram_sender.send_technical_analysis(symbol)
            if success:
                logger.info(f"Technical analysis for {symbol} sent successfully")
            else:
                logger.error(f"Error sending technical analysis for {symbol}")
            return success
        except Exception as e:
            logger.error(f"Exception in sending technical analysis for {symbol}: {str(e)}")
            return False
    
    def _send_trading_signals(self):
        """
        Send trading signals
        
        Returns:
            bool: Success or failure of sending signals
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"Sending trading signals ({now_toronto.strftime('%H:%M:%S')} Toronto)...")
        
        try:
            success = replit_telegram_sender.send_trading_signals()
            if success:
                logger.info("Trading signals sent successfully")
            else:
                logger.error("Error sending trading signals")
            return success
        except Exception as e:
            logger.error(f"Exception in sending trading signals: {str(e)}")
            return False
            
    def _check_price_alerts(self):
        """
        Check price alerts
        
        Returns:
            list: List of triggered alerts
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"Checking price alerts ({now_toronto.strftime('%H:%M:%S')} Toronto)...")
        
        try:
            triggered_alerts = check_price_alerts()
            if triggered_alerts:
                logger.info(f"{len(triggered_alerts)} price alerts triggered")
            return triggered_alerts
        except Exception as e:
            logger.error(f"Exception in checking price alerts: {str(e)}")
            return []
            
    def _send_crypto_news(self):
        """
        Send cryptocurrency news
        
        Returns:
            bool: Success or failure of sending news
        """
        now_toronto = datetime.datetime.now(toronto_tz)
        logger.info(f"Sending cryptocurrency news ({now_toronto.strftime('%H:%M:%S')} Toronto)...")
        
        try:
            # Using api_telegram_send_news in main.py
            # This method uses get_crypto_news_formatted_for_telegram module
            success = replit_telegram_sender.send_crypto_news()
            if success:
                logger.info("Cryptocurrency news sent successfully")
            else:
                logger.error("Error sending cryptocurrency news")
            return success
        except Exception as e:
            logger.error(f"Exception in sending cryptocurrency news: {str(e)}")
            return False
            
    def _get_next_crypto_news_time(self):
        """
        Calculate next cryptocurrency news time
        
        Returns:
            str: Next cryptocurrency news time
        """
        if not self.running:
            return "Service is not running"
        
        now = datetime.datetime.now(toronto_tz)
        reports_left = self.crypto_news_interval - self.crypto_news_counter
        seconds_left = reports_left * self.interval
        next_time = now + datetime.timedelta(seconds=seconds_left)
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
    
    def _load_settings(self):
        """
        Load settings from file
        """
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                
                # Update settings
                if 'message_sending_enabled' in settings:
                    self.message_sending_enabled = bool(settings['message_sending_enabled'])
                
                if 'auto_start_on_boot' in settings:
                    self.auto_start_on_boot = bool(settings['auto_start_on_boot'])
                
                if 'active_hours_start' in settings:
                    active_hours_start = int(settings['active_hours_start'])
                    if 0 <= active_hours_start <= 23:
                        self.active_hours_start = active_hours_start
                
                if 'active_hours_end' in settings:
                    active_hours_end = int(settings['active_hours_end'])
                    if 1 <= active_hours_end <= 24:
                        self.active_hours_end = active_hours_end
                
                if 'interval' in settings:
                    interval = int(settings['interval'])
                    if interval >= 60:
                        self.interval = interval
                
                logger.info(f"Settings loaded from {SETTINGS_FILE}")
            else:
                logger.info(f"Settings file {SETTINGS_FILE} not found, using defaults")
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
    
    def _save_settings(self):
        """
        Save settings to file
        """
        try:
            settings = {
                'message_sending_enabled': self.message_sending_enabled,
                'auto_start_on_boot': self.auto_start_on_boot,
                'active_hours_start': self.active_hours_start,
                'active_hours_end': self.active_hours_end,
                'interval': self.interval
            }
            
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
            
            logger.info(f"Settings saved to {SETTINGS_FILE}")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            return False

# Service instance to be used in main.py
telegram_scheduler = TelegramSchedulerService()


def start_scheduler():
    """
    Start Telegram scheduling
    
    Returns:
        bool: Startup status
    """
    return telegram_scheduler.start()


def stop_scheduler():
    """
    Stop Telegram scheduling
    
    Returns:
        bool: Stop status
    """
    return telegram_scheduler.stop()


def get_scheduler_status():
    """
    Get scheduling status
    
    Returns:
        dict: Current scheduling status
    """
    return telegram_scheduler.status()


def update_scheduler_settings(settings):
    """
    Update scheduler settings
    
    Args:
        settings (dict): New settings
        
    Returns:
        dict: Updated status
    """
    if 'message_sending_enabled' in settings:
        telegram_scheduler.message_sending_enabled = bool(settings['message_sending_enabled'])
        
    if 'auto_start_on_boot' in settings:
        telegram_scheduler.auto_start_on_boot = bool(settings['auto_start_on_boot'])
        
    if 'active_hours_start' in settings:
        try:
            # Ensure value is between 0 and 23
            active_hours_start = int(settings['active_hours_start'])
            if 0 <= active_hours_start <= 23:
                telegram_scheduler.active_hours_start = active_hours_start
        except (ValueError, TypeError):
            pass
            
    if 'active_hours_end' in settings:
        try:
            # Ensure value is between 0 and 24
            active_hours_end = int(settings['active_hours_end'])
            if 1 <= active_hours_end <= 24:
                telegram_scheduler.active_hours_end = active_hours_end
        except (ValueError, TypeError):
            pass
            
    if 'interval' in settings:
        try:
            # Ensure value is at least 60 seconds
            interval = int(settings['interval'])
            if interval >= 60:
                telegram_scheduler.interval = interval
        except (ValueError, TypeError):
            pass
    
    # Save settings to file
    telegram_scheduler._save_settings()
    
    # Return current status
    return telegram_scheduler.status()


# If this file is run directly, start scheduling and run for 1 minute
if __name__ == "__main__":
    print("Starting Telegram scheduling service test...")
    
    if start_scheduler():
        print("Service started successfully")
        print("Running for 1 minute...")
        
        # Run test for 1 minute
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("Test stopped by user command")
        
        # Stop service
        if stop_scheduler():
            print("Service stopped successfully")
        else:
            print("Error stopping service")
    else:
        print("Error starting service")