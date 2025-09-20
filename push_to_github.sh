#!/bin/bash

# SalamMessenger GitHub Push Script

echo "🚀 Pushing SalamMessenger to GitHub..."

# Check if remote exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ Remote 'origin' already exists"
    git remote -v
else
    echo "❌ No remote 'origin' found"
    echo "Please create a GitHub repository first:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: salam-messenger"
    echo "3. Description: Real-time Crypto Trading Bot with AI Assistant"
    echo "4. Make it Public"
    echo "5. Don't initialize with README, .gitignore, or license"
    echo "6. Click 'Create repository'"
    echo ""
    echo "Then run this command to add the remote:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/salam-messenger.git"
    echo ""
    echo "Replace YOUR_USERNAME with your actual GitHub username"
    exit 1
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo "🌐 Your repository is now available at:"
    git remote get-url origin | sed 's/\.git$//'
    echo ""
    echo "📋 Next steps:"
    echo "1. Visit your repository on GitHub"
    echo "2. Go to Settings > Pages to enable GitHub Pages (optional)"
    echo "3. Go to Settings > Secrets to add environment variables"
    echo "4. Deploy to Vercel using the GitHub integration"
else
    echo "❌ Failed to push to GitHub"
    echo "Please check your GitHub repository URL and try again"
fi
