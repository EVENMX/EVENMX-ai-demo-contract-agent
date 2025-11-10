# Vercel Deployment Setup Guide

## Required Environment Variables

You **must** configure these environment variables in your Vercel project dashboard:

### Required:
1. **OPENROUTER_API_KEY** - Your OpenRouter API key for LLM functionality
   - Get it from: https://openrouter.ai/
   - Without this, the contract review will use fallback heuristics only

### Optional (for extended features):
2. **OPENROUTER_MODEL** (optional) - Default: "openai/gpt-5-mini"
   - Override the default LLM model

3. **TELEGRAM_BOT_TOKEN** (optional) - For Telegram notifications
   - Get from: https://t.me/BotFather

4. **TELEGRAM_BOSS_CHAT_ID** (optional) - Your Telegram chat ID
   - Get by messaging: https://t.me/userinfobot

## How to Set Environment Variables in Vercel

1. Go to your project in Vercel Dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add each variable with its value
4. Select which environments to apply to (Production, Preview, Development)
5. Click **Save**
6. **Redeploy** your application for changes to take effect

## Deployment Checklist

- [ ] Set `OPENROUTER_API_KEY` in Vercel dashboard
- [ ] (Optional) Set `TELEGRAM_BOT_TOKEN` if using Telegram notifications
- [ ] (Optional) Set `TELEGRAM_BOSS_CHAT_ID` if using Telegram notifications
- [ ] Verify all files are committed to your repository
- [ ] Push changes to trigger automatic deployment
- [ ] Check deployment logs for any errors
- [ ] Test the `/healthz` endpoint to verify deployment
- [ ] Test contract upload functionality

## Common Issues

### Issue: 500 Internal Server Error / FUNCTION_INVOCATION_FAILED
**Causes:**
- Missing environment variables (especially `OPENROUTER_API_KEY`)
- Files not found (templates, data files)
- Python runtime errors

**Solutions:**
1. Check Vercel function logs: Go to your deployment → Functions tab → View logs
2. Verify environment variables are set correctly
3. Ensure all required files are included in deployment (not in `.vercelignore`)
4. Check that `vercel.json` includes all necessary files

### Issue: Files Not Found
The app now uses `PROJECT_ROOT` environment variable to locate files correctly in Vercel's serverless environment. This is automatically set by `api/index.py`.

## Local Testing

To test locally before deploying:

```bash
# Install Vercel CLI
npm i -g vercel

# Run locally (simulates Vercel environment)
vercel dev

# Test the application
curl http://localhost:3000/healthz
```

## Monitoring

After deployment, monitor your application:

1. **Function Logs**: Vercel Dashboard → Your Project → Functions → View Logs
2. **Analytics**: Vercel Dashboard → Your Project → Analytics
3. **Health Check**: Visit `https://your-domain.vercel.app/healthz`

## Support

If you encounter issues:
1. Check the deployment logs in Vercel Dashboard
2. Verify all environment variables are set
3. Review the error message in function logs
4. Consult Vercel documentation: https://vercel.com/docs/functions/serverless-functions/runtimes/python

