"""
WSGI configuration for PythonAnywhere
This file tells PythonAnywhere how to run your Flask app
"""

import sys
import os

# Add your project directory to the Python path
path = '/home/yourusername/Barzin_Crypto'  # Change 'yourusername' to your actual username
if path not in sys.path:
    sys.path.append(path)

# Change to your project directory
os.chdir(path)

# Import your Flask app
from main import app as application

# Optional: Set environment variables if needed
# os.environ['FLASK_ENV'] = 'production'
