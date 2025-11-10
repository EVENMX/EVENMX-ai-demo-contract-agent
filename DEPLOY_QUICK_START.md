# 🚀 Vercel Deployment - Quick Start

## Step 1: Set Environment Variables in Vercel

**CRITICAL:** Set this in Vercel Dashboard → Settings → Environment Variables:

```
OPENROUTER_API_KEY=your-key-here
```

Without this, the app will crash or use fallback logic only.

### Optional (but recommended):
```
OPENROUTER_MODEL=openai/gpt-5-mini
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_BOSS_CHAT_ID=your-telegram-chat-id
```

## Step 2: Push Changes to Git

```bash
git add .
git commit -m "Fix Vercel deployment path resolution issues"
git push
```

## Step 3: Deploy

If connected to Git, Vercel will auto-deploy. Otherwise:

```bash
vercel --prod
```

## Step 4: Test

Visit your deployment and test:

1. **Health check:** `https://your-app.vercel.app/healthz`
   - Should return: `{"status":"ok"}`

2. **Main page:** `https://your-app.vercel.app/`
   - Should load the upload form

3. **Upload a contract:** 
   - Use the "Load Sample" button or upload a file
   - Select a checklist section
   - Submit and verify results

## Troubleshooting

### If you see 500 error:

1. **Check environment variables:**
   - Vercel Dashboard → Settings → Environment Variables
   - Verify `OPENROUTER_API_KEY` is set

2. **Check function logs:**
   - Vercel Dashboard → Deployments → Your Deployment → Functions → View Logs
   - Look for specific error messages

3. **Redeploy:**
   - After setting env vars, trigger a new deployment
   - Go to Deployments → Click "..." → Redeploy

### Common Issues:

| Error | Cause | Solution |
|-------|-------|----------|
| 500 FUNCTION_INVOCATION_FAILED | Missing env vars or files | Set OPENROUTER_API_KEY, check logs |
| Files not found | Deployment config issue | Ensure vercel.json includes files |
| Module import errors | Path resolution | Check api/index.py sets PROJECT_ROOT |

## Testing Locally First

Test the Vercel environment locally before deploying:

```bash
# Install Vercel CLI (if not installed)
npm i -g vercel

# Test locally
vercel dev

# Visit http://localhost:3000
```

## Full Documentation

- 📘 **Complete Setup Guide:** [VERCEL_SETUP.md](./VERCEL_SETUP.md)
- 📗 **Deployment Steps:** [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md)
- 📕 **Changes Made:** [CHANGELOG_VERCEL_FIX.md](./CHANGELOG_VERCEL_FIX.md)

## Quick Commands

```bash
# View environment variables
vercel env ls

# Add environment variable
vercel env add OPENROUTER_API_KEY

# View deployment logs
vercel logs

# Redeploy
vercel --prod
```

---

**Need Help?** Check the function logs in Vercel Dashboard first - they show exactly what went wrong!

