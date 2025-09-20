#!/bin/bash

# SalamMessenger Vercel Deployment Script

echo "🚀 Starting SalamMessenger deployment to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Installing..."
    npm install -g vercel
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please login to Vercel first:"
    vercel login
fi

# Deploy to Vercel
echo "📦 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo "🌐 Your application is now live on Vercel!"
echo "📋 Next steps:"
echo "   1. Add your custom domain in Vercel dashboard"
echo "   2. Configure environment variables"
echo "   3. Set up your database"
echo "   4. Test all features"

echo "📖 For detailed instructions, see VERCEL_DEPLOYMENT.md"
