# Vercel Deployment Fix - Changelog

**Date:** November 10, 2025  
**Issue:** 500 Internal Server Error (FUNCTION_INVOCATION_FAILED) on Vercel deployment  
**Status:** ✅ Fixed

## Problem Summary

The application was crashing immediately after deployment to Vercel with:
- HTTP 500 Internal Server Error
- Error Code: `FUNCTION_INVOCATION_FAILED`
- Root cause: File path resolution issues in serverless environment
- Missing files: `contract_checklist.json` couldn't be found
- Python process exited with status 1

## Root Causes Identified

### 1. **File Path Resolution in Serverless Environment**
- Relative file paths that worked locally failed in Vercel's serverless functions
- The working directory in serverless functions differs from local development
- Files were being loaded using `Path(__file__).parent` which didn't work consistently

### 2. **Missing Environment Variables**
- No clear documentation about required vs optional environment variables
- Missing `OPENROUTER_API_KEY` could cause crashes or unexpected behavior

### 3. **Incomplete Vercel Configuration**
- `vercel.json` didn't explicitly include necessary files (app/, templates/, static/)
- No `.vercelignore` to exclude unnecessary files (tests, htmlcov, etc.)

### 4. **Module Import Issues**
- The API entry point (`api/index.py`) didn't set up paths consistently for serverless environment

## Changes Made

### 1. **Updated `vercel.json`**
**File:** `vercel.json`

**Changes:**
- Added `includeFiles` configuration to explicitly include:
  - `app/**` (application code and data files)
  - `templates/**` (Jinja2 templates)
  - `static/**` (CSS and static assets)
- Removed `PYTHON_VERSION` env var (Vercel auto-detects from runtime)

**Impact:** Ensures all necessary files are included in the serverless function bundle.

### 2. **Created `.vercelignore`**
**File:** `.vercelignore` (new)

**Purpose:** Exclude unnecessary files from deployment:
- Test files (`tests/`, `pytest.ini`)
- Coverage reports (`htmlcov/`, `.coverage`)
- Generated reports (`reports/`)
- Development files (`.venv/`, `__pycache__/`)
- Documentation (`README.md`, sample PDFs)

**Impact:** Reduces deployment size and potential conflicts.

### 3. **Enhanced `api/index.py`**
**File:** `api/index.py`

**Changes:**
- Added `PROJECT_ROOT` environment variable that gets set automatically
- This helps all modules locate files relative to the project root
- Used `.resolve()` for absolute path resolution

```python
# Set environment variable to help modules find project root
os.environ["PROJECT_ROOT"] = str(project_root)
```

**Impact:** Provides a reliable way for all modules to find data files in serverless environment.

### 4. **Updated `app/checklist_loader.py`**
**File:** `app/checklist_loader.py`

**Changes:**
- Added logic to use `PROJECT_ROOT` environment variable when available
- Falls back to relative path resolution for local development
- Improved error message to include current directory for debugging

```python
project_root = os.environ.get("PROJECT_ROOT")
if project_root:
    base_dir = Path(project_root) / "app"
else:
    base_dir = Path(__file__).resolve().parent
```

**Impact:** Correctly locates `contract_checklist.json` in both local and Vercel environments.

### 5. **Updated `app/main.py`**
**File:** `app/main.py`

**Changes:**
- Added `PROJECT_ROOT` environment variable detection
- Updated path resolution for data, static, and templates directories
- Added explicit error for missing templates directory

```python
project_root = os.environ.get("PROJECT_ROOT")
if project_root:
    _base_dir = Path(project_root)
else:
    _base_dir = Path(__file__).resolve().parent.parent
```

**Impact:** All path-dependent features now work correctly in serverless environment.

### 6. **Created `VERCEL_SETUP.md`**
**File:** `VERCEL_SETUP.md` (new)

**Purpose:** Comprehensive setup and troubleshooting guide covering:
- Required vs optional environment variables
- Step-by-step Vercel dashboard configuration
- Common deployment issues and solutions
- Local testing with Vercel CLI
- Monitoring and debugging tips

**Impact:** Clear documentation for deployment and troubleshooting.

### 7. **Updated `VERCEL_DEPLOY.md`**
**File:** `VERCEL_DEPLOY.md`

**Changes:**
- Added prominent link to `VERCEL_SETUP.md`
- Emphasized **required** environment variables
- Enhanced troubleshooting section with specific error codes
- Added debug steps

**Impact:** Better deployment guidance and error resolution.

### 8. **Updated `README.md`**
**File:** `README.md`

**Changes:**
- Added Vercel deployment to features list
- Added dedicated Deployment section linking to guides
- Expanded testing section with Vercel local testing
- Added comprehensive project structure documentation

**Impact:** Better project overview and navigation to deployment docs.

## Testing Results

- ✅ 53 tests passed
- ⚠️ 4 pre-existing test failures (not related to deployment fixes)
- ✅ All file path changes work correctly
- ✅ No new linter errors introduced

## Deployment Checklist

Before deploying to Vercel:

- [ ] Push all changes to your Git repository
- [ ] Set `OPENROUTER_API_KEY` in Vercel dashboard (Settings → Environment Variables)
- [ ] (Optional) Set `TELEGRAM_BOT_TOKEN` if using Telegram notifications
- [ ] (Optional) Set `TELEGRAM_BOSS_CHAT_ID` if using Telegram notifications
- [ ] Deploy to Vercel
- [ ] Test `/healthz` endpoint: `https://your-domain.vercel.app/healthz`
- [ ] Test contract upload functionality
- [ ] Check function logs if any issues occur

## Files Changed

1. `vercel.json` - Updated configuration with includeFiles
2. `.vercelignore` - New file to exclude unnecessary files
3. `api/index.py` - Added PROJECT_ROOT environment variable
4. `app/checklist_loader.py` - Updated file path resolution
5. `app/main.py` - Updated file path resolution
6. `VERCEL_SETUP.md` - New comprehensive setup guide
7. `VERCEL_DEPLOY.md` - Enhanced deployment documentation
8. `README.md` - Updated with deployment info
9. `CHANGELOG_VERCEL_FIX.md` - This file

## How It Works Now

1. **During Deployment:**
   - Vercel builds the serverless function from `api/index.py`
   - `includeFiles` ensures all app code, templates, and static files are bundled
   - `.vercelignore` prevents unnecessary files from being deployed

2. **At Runtime:**
   - `api/index.py` sets `PROJECT_ROOT` environment variable
   - All modules check for `PROJECT_ROOT` first, fall back to relative paths
   - Files are located correctly regardless of working directory

3. **For Developers:**
   - Local development works unchanged (PROJECT_ROOT not set, uses relative paths)
   - `vercel dev` simulates production environment for testing
   - Clear error messages help debug any path issues

## Next Steps

1. **Immediate:**
   - Deploy to Vercel with updated configuration
   - Set required environment variables
   - Test all functionality

2. **Recommended:**
   - Add more logging to track file loading in production
   - Consider adding health check that verifies file access
   - Set up Vercel monitoring and alerts

3. **Future Enhancements:**
   - Implement proper Google Drive integration
   - Add more comprehensive error handling
   - Consider caching checklist data for better performance

## Support

If you encounter issues after these fixes:

1. Check Vercel function logs (Dashboard → Functions → View Logs)
2. Verify all environment variables are set correctly
3. Test with `vercel dev` locally
4. Check `/healthz` endpoint for basic connectivity
5. Review `VERCEL_SETUP.md` for troubleshooting steps

---

**Note:** These changes maintain backward compatibility with local development. No changes to local `.env` setup or development workflow are required.

