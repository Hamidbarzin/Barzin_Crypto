"""
Email service for sending notifications and trading signals
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from crypto_bot.config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_SERVER, EMAIL_PORT

logger = logging.getLogger(__name__)

def send_email(recipient, subject, html_content, text_content=None):
    """
    Send an email with the provided content
    
    Args:
        recipient (str): Email address to send to
        subject (str): Email subject
        html_content (str): HTML content of the email
        text_content (str, optional): Plain text content as fallback
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not EMAIL_USER or not EMAIL_PASSWORD:
        logger.error("Email credentials not configured. Check EMAIL_USER and EMAIL_PASSWORD environment variables.")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = recipient
        
        # Add plain text version if provided, otherwise create from HTML
        if text_content is None:
            # Simple conversion of HTML to text (very basic)
            text_content = html_content.replace('<br>', '\n').replace('</p>', '\n').replace('</div>', '\n')
            text_content = ''.join(c for c in text_content if ord(c) < 128)  # Remove non-ASCII chars
            
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"Email sent to {recipient}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def send_test_email(recipient):
    """
    Send a test email to verify email configuration
    
    Args:
        recipient (str): Email address to send to
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Test Email from Crypto Trading Bot"
    html_content = f"""
    <html>
    <head></head>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2 style="color: #333;">Crypto Trading Bot Test Email</h2>
            <p>This is a test email from your cryptocurrency trading bot.</p>
            <p>If you're receiving this email, your email notifications are configured correctly!</p>
            <p>Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
            <p style="font-size: 12px; color: #777;">
                This is an automated message. Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    return send_email(recipient, subject, html_content)

def send_signal_notification(email_settings, signals):
    """
    Send an email notification with trading signals
    
    Args:
        email_settings (dict): Email settings including recipient address
        signals (dict): Trading signals for cryptocurrencies
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not email_settings.get('enabled') or not email_settings.get('email'):
        logger.debug("Email notifications disabled or email address not set")
        return False
    
    recipient = email_settings['email']
    subject = "Cryptocurrency Trading Signals - " + datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Create email content
    html_content = f"""
    <html>
    <head></head>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2 style="color: #333;">Cryptocurrency Trading Signals</h2>
            <p>Here are the latest trading signals for your watched cryptocurrencies:</p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Currency</th>
                    <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Signal</th>
                    <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Price</th>
                    <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Strength</th>
                </tr>
    """
    
    for symbol, signal in signals.items():
        # Set row color based on signal
        row_color = "#ffffff"
        if signal['signal'] == "Strong Buy":
            row_color = "#d4edda"  # light green
        elif signal['signal'] == "Buy":
            row_color = "#e8f5e9"  # very light green
        elif signal['signal'] == "Strong Sell":
            row_color = "#f8d7da"  # light red
        elif signal['signal'] == "Sell":
            row_color = "#feecec"  # very light red
            
        html_content += f"""
                <tr style="background-color: {row_color};">
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{symbol}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{signal['signal']}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">${signal['price']:.2f}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{signal['strength']:.2f}</td>
                </tr>
        """
    
    html_content += f"""
            </table>
            
            <div style="margin-top: 20px;">
                <h3>Signal Explanations:</h3>
                <ul>
                    <li><strong>Strong Buy</strong>: Multiple technical indicators suggest a strong upward trend.</li>
                    <li><strong>Buy</strong>: Some indicators suggest an upward trend.</li>
                    <li><strong>Neutral</strong>: No clear trend direction.</li>
                    <li><strong>Sell</strong>: Some indicators suggest a downward trend.</li>
                    <li><strong>Strong Sell</strong>: Multiple technical indicators suggest a strong downward trend.</li>
                </ul>
            </div>
            
            <p style="margin-top: 20px;">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <hr>
            <p style="font-size: 12px; color: #777;">
                This is an automated message from your cryptocurrency trading bot.
                These signals are based on technical analysis and are not financial advice.
                Please do your own research before making any investment decisions.
            </p>
        </div>
    </body>
    </html>
    """
    
    return send_email(recipient, subject, html_content)

def update_email_settings(settings):
    """
    Update email settings
    
    Args:
        settings (dict): New email settings
        
    Returns:
        dict: Updated email settings
    """
    return settings
