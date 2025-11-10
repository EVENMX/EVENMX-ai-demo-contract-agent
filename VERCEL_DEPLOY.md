# Deploying to Vercel

This project is configured for deployment to Vercel. Follow these steps:

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed (optional, for CLI deployment):
   ```bash
   npm i -g vercel
   ```

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard

1. Push your code to a Git repository (GitHub, GitLab, or Bitbucket)
2. Go to https://vercel.com/new
3. Import your repository
4. Vercel will automatically detect the Python project and use the `vercel.json` configuration
5. Add your environment variables in the Vercel dashboard:
   - `OPENROUTER_API_KEY` (optional, for LLM features)
   - `OPENROUTER_MODEL` (default: `openai/gpt-5-mini`)
   - `TELEGRAM_BOT_TOKEN` (optional)
   - `TELEGRAM_BOSS_CHAT_ID` (optional)
6. Click "Deploy"

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

- If static files aren't loading, check that the `static/` directory is in the project root
- If templates aren't found, verify the `templates/` directory structure
- Check Vercel function logs in the dashboard for runtime errors
- Ensure all required files (`contract_checklist.json`, `sample_contract.txt`) are in the repository
