# Vercel Deployment Guide for SalamMessenger

## 🚀 Deploy to Vercel with Custom Domain

### Step 1: Prepare Your Application

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

### Step 2: Deploy to Vercel

1. **Navigate to your project directory**:
   ```bash
   cd /Users/hamidrezazebardast/Desktop/Startup/SalamMessenger
   ```

2. **Deploy to Vercel**:
   ```bash
   vercel
   ```

3. **Follow the prompts**:
   - Set up and deploy? `Y`
   - Which scope? Choose your account
   - Link to existing project? `N`
   - What's your project's name? `salam-messenger` (or your preferred name)
   - In which directory is your code located? `./`

### Step 3: Configure Environment Variables

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Select your project**
3. **Go to Settings > Environment Variables**
4. **Add the following variables**:

```
SESSION_SECRET=your-secret-key-here
DATABASE_URL=your-database-url-here
OPENAI_API_KEY=your-openai-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
CRYPTO_NEWS_API_KEY=your-crypto-news-api-key
```

### Step 4: Add Custom Domain

1. **In Vercel Dashboard**, go to your project
2. **Click on "Domains" tab**
3. **Add your custom domain**:
   - Enter your domain (e.g., `salamcrypto.com`)
   - Click "Add"
4. **Configure DNS**:
   - Add a CNAME record pointing to `cname.vercel-dns.com`
   - Or add an A record pointing to Vercel's IP addresses

### Step 5: Update DNS Settings

**For your domain provider** (GoDaddy, Namecheap, etc.):

1. **Add CNAME record**:
   - Type: CNAME
   - Name: www (or @)
   - Value: cname.vercel-dns.com

2. **Add A record** (if using root domain):
   - Type: A
   - Name: @
   - Value: 76.76.19.61 (Vercel's IP)

### Step 6: SSL Certificate

Vercel automatically provides SSL certificates for custom domains. It may take a few minutes to provision.

### Step 7: Test Your Deployment

1. **Visit your custom domain**
2. **Test real-time features**:
   - Price updates should work
   - Smart assistant should be functional
   - All API endpoints should respond

## 🔧 Configuration Files

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ],
  "env": {
    "PYTHONPATH": ".",
    "FLASK_ENV": "production"
  }
}
```

### requirements.txt
All Python dependencies are listed in `requirements.txt`

## 🌐 Custom Domain Examples

- `salamcrypto.com`
- `cryptobarzin.com`
- `salamtrading.com`
- `yourdomain.com`

## 📱 Features Available on Vercel

✅ **Real-time Price Updates** (via Server-Sent Events)
✅ **Smart AI Assistant**
✅ **Trading Signals**
✅ **Technical Analysis**
✅ **Crypto News**
✅ **Multi-language Support**
✅ **Responsive Design**

## 🚨 Important Notes

1. **WebSocket Limitation**: Vercel doesn't support WebSockets, so we use Server-Sent Events instead
2. **Database**: Use a cloud database (PostgreSQL, MongoDB, etc.)
3. **File Storage**: Use cloud storage for static files
4. **Environment Variables**: Keep sensitive data in Vercel's environment variables

## 🔄 Updates and Redeployment

To update your application:

1. **Make changes to your code**
2. **Commit to Git**:
   ```bash
   git add .
   git commit -m "Update application"
   git push
   ```
3. **Vercel will automatically redeploy** (if connected to Git)

Or manually deploy:
```bash
vercel --prod
```

## 📊 Monitoring

- **Vercel Dashboard**: Monitor deployments, performance, and errors
- **Function Logs**: Check serverless function logs
- **Analytics**: View traffic and performance metrics

## 🆘 Troubleshooting

### Common Issues:

1. **Build Failures**: Check `requirements.txt` and Python version
2. **Environment Variables**: Ensure all required variables are set
3. **Database Connection**: Verify database URL and credentials
4. **Domain Issues**: Check DNS propagation (can take 24-48 hours)

### Support:
- Vercel Documentation: https://vercel.com/docs
- Vercel Community: https://github.com/vercel/vercel/discussions

---

**Your SalamMessenger application is now live on Vercel with a custom domain! 🎉**
