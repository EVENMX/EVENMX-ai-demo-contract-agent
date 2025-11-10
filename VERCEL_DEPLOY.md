# Deploying to Vercel

This project is configured for deployment to Vercel. Follow these steps:

> **⚠️ IMPORTANT**: Before deploying, read [VERCEL_SETUP.md](./VERCEL_SETUP.md) for complete environment variable configuration and troubleshooting guide.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed (optional, for CLI deployment):
   ```bash
   npm i -g vercel
   ```

## Quick Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. Push your code to a Git repository (GitHub, GitLab, or Bitbucket)
2. Go to https://vercel.com/new
3. Import your repository
4. Vercel will automatically detect the Python project and use the `vercel.json` configuration
5. **REQUIRED**: Add your environment variables in the Vercel dashboard:
   - `OPENROUTER_API_KEY` (**required** - without this, the app will crash or use fallback logic)
   - `OPENROUTER_MODEL` (optional, default: `openai/gpt-5-mini`)
   - `TELEGRAM_BOT_TOKEN` (optional)
   - `TELEGRAM_BOSS_CHAT_ID` (optional)
6. Click "Deploy"
7. Wait for deployment to complete
8. Test the `/healthz` endpoint to verify: `https://your-domain.vercel.app/healthz`

### Option 2: Deploy via CLI

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. For production deployment:
   ```bash
   vercel --prod
   ```

5. Set environment variables:
   ```bash
   vercel env add OPENROUTER_API_KEY
   vercel env add TELEGRAM_BOT_TOKEN
   # ... etc
   ```

## Important Notes

- **File System**: The app is configured to work without file writes in the serverless environment. Reports are generated in-memory for demo purposes.
- **Static Files**: Static files (CSS) are served through Vercel's CDN.
- **Templates**: Jinja2 templates are included in the deployment.
- **Timeout**: The function timeout is set to 60 seconds (configurable in `vercel.json`).

## Testing Locally with Vercel

You can test the Vercel configuration locally:

```bash
vercel dev
```

This will start a local server that mimics Vercel's serverless environment.

## Troubleshooting

**For detailed troubleshooting, see [VERCEL_SETUP.md](./VERCEL_SETUP.md)**

### Common Issues:

1. **500 FUNCTION_INVOCATION_FAILED**:
   - Missing `OPENROUTER_API_KEY` environment variable
   - Files not found (check function logs)
   - View detailed logs in Vercel Dashboard → Functions → View Logs

2. **Files Not Found**:
   - The app now uses `PROJECT_ROOT` environment variable (automatically set)
   - Ensure `vercel.json` includes all necessary files in `includeFiles`
   - Check that files aren't excluded in `.vercelignore`

3. **Static Files Not Loading**:
   - Verify `static/` directory is in project root
   - Check `vercel.json` routes configuration

4. **Templates Not Found**:
   - Verify `templates/` directory structure
   - Check that templates are included in deployment

### Debug Steps:
1. Check deployment logs in Vercel Dashboard
2. Test healthcheck endpoint: `/healthz`
3. View function logs for detailed error messages
4. Verify all environment variables are set correctly
