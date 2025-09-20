# PythonAnywhere deployment configuration
# This file contains instructions for deploying to PythonAnywhere

"""
PythonAnywhere Deployment Instructions for BarzinCrypto:

1. Go to https://www.pythonanywhere.com/
2. Create a free account
3. Upload your project files
4. Install dependencies: pip3.10 install --user -r requirements.txt
5. Create a web app and point it to main.py
6. Your app will be available at: yourusername.pythonanywhere.com

Alternative: Use Railway.app
1. Go to https://railway.app/
2. Connect your GitHub repository
3. Railway will automatically detect Python and deploy
4. You'll get a free domain like: yourproject.railway.app

Alternative: Use Render.com
1. Go to https://render.com/
2. Connect your GitHub repository
3. Choose "Web Service" and Python
4. You'll get a free domain like: yourproject.onrender.com
"""

print("Choose your deployment platform:")
print("1. PythonAnywhere - Free Python hosting")
print("2. Railway.app - Modern deployment platform")
print("3. Render.com - Simple deployment")
print("4. Heroku - Popular platform (requires credit card)")
