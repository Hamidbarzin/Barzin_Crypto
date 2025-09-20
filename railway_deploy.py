#!/usr/bin/env python3
"""
Railway Deployment Script
This script helps deploy the full Barzin Crypto application to Railway
"""

import subprocess
import sys
import time

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 Railway Deployment Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    success, stdout, stderr = run_command("pwd")
    if success:
        print(f"📁 Current directory: {stdout.strip()}")
    
    # Check git status
    print("\n📋 Checking Git status...")
    success, stdout, stderr = run_command("git status --porcelain")
    if success and stdout.strip():
        print("⚠️  Uncommitted changes detected:")
        print(stdout)
        print("Committing changes...")
        run_command("git add .")
        run_command('git commit -m "Force Railway redeploy"')
    else:
        print("✅ Working directory is clean")
    
    # Push to GitHub to trigger Railway deployment
    print("\n🔄 Pushing to GitHub to trigger Railway deployment...")
    success, stdout, stderr = run_command("git push origin main")
    if success:
        print("✅ Successfully pushed to GitHub")
        print("🚀 Railway should now be deploying the full application...")
        print("\n📱 Your Railway app: https://web-production-929a2.up.railway.app")
        print("⏱️  Please wait 2-3 minutes for the deployment to complete")
        print("\n🔍 Check Railway dashboard for deployment status")
    else:
        print("❌ Failed to push to GitHub:")
        print(stderr)
        return False
    
    print("\n✅ Deployment process initiated!")
    return True

if __name__ == "__main__":
    main()