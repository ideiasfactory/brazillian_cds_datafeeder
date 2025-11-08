# Deployment Guide

## Overview

This project is designed to run in two modes:

1. **Development (Local)**: Full-featured development environment with hot reload
2. **Production (Vercel + GitHub Actions)**:
   - **API**: Serverless deployment on Vercel
   - **Data Updates**: Daily cron job via GitHub Actions

## Architecture

```
┌─────────────────────────────────────────────────┐
│              GitHub Repository                   │
│  ┌──────────────────────────────────────────┐  │
│  │  data/brasil_CDS_historical.csv          │  │
│  └──────────────────────────────────────────┘  │
│                     ▲                            │
│                     │                            │
│            Daily at 02:00 UTC                   │
│                     │                            │
│  ┌──────────────────────────────────────────┐  │
│  │    GitHub Actions Workflow               │  │
│  │  - Fetch data from Investing.com         │  │
│  │  - Update CSV                            │  │
│  │  - Commit & Push                         │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                     │
                     │ (reads data)
                     ▼
         ┌────────────────────────┐
         │   Vercel Serverless    │
         │    FastAPI (Python)    │
         │  - GET /health         │
         │  - GET /cds/           │
         │  - GET /cds/latest     │
         │  - GET /cds/stats      │
         └────────────────────────┘
```

## Local Development Setup

### 1. Prerequisites

- Python 3.11+
- pyenv (recommended)
- Git

### 2. Initial Setup

```bash
# Clone repository
cd /path/to/project

# Create virtual environment
pyenv virtualenv 3.11.0 brazilian_cds_feeder
pyenv local brazilian_cds_feeder

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Development Server

```bash
# Update data first (optional)
python scripts/update_cds.py

# Start API with hot reload
python scripts/start_api.py
```

Or with uvicorn directly:
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Access:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. Environment Variables for Development

Create `.env` file:
```bash
# Environment
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO

# BetterStack (optional)
BETTERSTACK_SOURCE_TOKEN=your_token_here
BETTERSTACK_INGESTING_HOST=in.logtail.com

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
```

## Production Deployment

### Part 1: Vercel (Serverless API)

#### 1. Prerequisites

- Vercel account
- Vercel CLI (optional): `npm install -g vercel`

#### 2. Connect Repository to Vercel

**Option A: Via Vercel Dashboard (Recommended)**

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure project:
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)

**Option B: Via Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel
```

#### 3. Configure Environment Variables in Vercel

Go to: **Project Settings > Environment Variables**

Add the following:

```
ENVIRONMENT=production
LOG_LEVEL=INFO
BETTERSTACK_SOURCE_TOKEN=your_token (optional)
BETTERSTACK_INGESTING_HOST=in.logtail.com (optional)
```

#### 4. Deploy

Vercel will automatically deploy when you push to your repository.

Manual deploy:
```bash
vercel --prod
```

#### 5. Verify Deployment

Visit your Vercel URL:
- https://your-project.vercel.app/health
- https://your-project.vercel.app/docs

### Part 2: GitHub Actions (Daily CronJob)

#### 1. Configure GitHub Secrets

Go to: **Repository > Settings > Secrets and variables > Actions**

Add secrets (optional for logging):
- `BETTERSTACK_SOURCE_TOKEN`
- `BETTERSTACK_INGESTING_HOST`

#### 2. Enable GitHub Actions

The workflow is already configured in `.github/workflows/update-cds-data.yml`

It will:
- Run daily at 02:00 UTC (23:00 BRT previous day)
- Fetch data from Investing.com
- Update `data/brasil_CDS_historical.csv`
- Commit and push changes
- Upload data as artifact

#### 3. Manual Trigger

You can manually trigger the workflow:

1. Go to: **Actions** tab
2. Select: **Update CDS Data Daily**
3. Click: **Run workflow**

#### 4. Monitor Runs

Check workflow runs in the **Actions** tab of your repository.

### Part 3: Data Flow

1. **GitHub Actions runs daily** → Updates CSV in repository
2. **Vercel reads data** → From GitHub repository (via git)
3. **API serves data** → Fresh data from latest commit

**Note**: In production, Vercel reads the CSV file from the repository. The file is read-only in Vercel's serverless environment. Updates happen via GitHub Actions.

## Important Configuration Files

### `vercel.json`
```json
{
  "version": 2,
  "builds": [{"src": "api/index.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "api/index.py"}],
  "env": {"ENVIRONMENT": "production"}
}
```

### `api/index.py`
Entry point for Vercel serverless function.

### `.github/workflows/update-cds-data.yml`
GitHub Actions workflow for daily data updates.

## Storage Strategy

### Development
- CSV stored in: `data/brasil_CDS_historical.csv`
- Backups in: `data/brasil_CDS_historical__bkp_*.csv`
- Writable filesystem

### Production (Vercel)
- CSV read from: GitHub repository (read-only)
- No backups created (filesystem is ephemeral)
- Data updates via GitHub Actions

## Monitoring

### API Health

```bash
# Check API health
curl https://your-project.vercel.app/health

# Expected response
{"status":"healthy","version":"1.0.0"}
```

### GitHub Actions

- View logs in **Actions** tab
- Artifacts stored for 7 days
- Email notifications on failure

### BetterStack Logging (Optional)

If configured, logs are sent to BetterStack:
- API requests and errors
- Data update status
- System events

## Troubleshooting

### Vercel Deployment Issues

**Problem**: Build fails
**Solution**: Check Python version in `vercel.json` matches requirements

**Problem**: Module not found
**Solution**: Ensure all dependencies in `requirements.txt`

**Problem**: API returns 404
**Solution**: Check `vercel.json` routes configuration

### GitHub Actions Issues

**Problem**: Workflow doesn't run
**Solution**: Check if Actions are enabled in repository settings

**Problem**: Commit fails
**Solution**: Ensure GitHub Actions has write permissions

**Problem**: Data update fails
**Solution**: Check logs in Actions tab, verify Investing.com is accessible

### Data Issues

**Problem**: API returns old data
**Solution**: Check if GitHub Actions ran successfully, redeploy Vercel

**Problem**: No data in production
**Solution**: Ensure `data/brasil_CDS_historical.csv` is committed to repository

## Costs

- **Vercel**: Free tier includes 100GB bandwidth, serverless functions
- **GitHub Actions**: Free tier includes 2,000 minutes/month
- **This project usage**: ~1-2 minutes/day = ~60 minutes/month (well within free tier)

## Scaling Considerations

For higher traffic or more frequent updates:

1. **Add caching**: Redis or Vercel KV
2. **Use database**: PostgreSQL, MongoDB
3. **CDN**: Serve static data files via CDN
4. **Increase GitHub Actions frequency**: Change cron schedule
5. **Add webhook**: Trigger Vercel redeployment after data update

## Security Best Practices

1. ✅ Never commit secrets to repository
2. ✅ Use environment variables for sensitive data
3. ✅ Enable CORS with specific origins in production
4. ✅ Add rate limiting for API endpoints
5. ✅ Monitor API usage and errors
6. ✅ Keep dependencies updated

## Testing Deployment

### Test Local Development
```bash
python scripts/update_cds.py
python scripts/start_api.py
curl http://localhost:8000/health
```

### Test Production API
```bash
curl https://your-project.vercel.app/health
curl https://your-project.vercel.app/cds/latest?n=5
curl https://your-project.vercel.app/cds/stats
```

### Test GitHub Actions
1. Go to Actions tab
2. Manually trigger workflow
3. Check logs for success
4. Verify CSV updated in repository

## Rollback Strategy

### Rollback Vercel Deployment
```bash
# Via Vercel Dashboard
Project > Deployments > Click previous deployment > Promote to Production

# Via CLI
vercel rollback
```

### Rollback Data Updates
```bash
# Revert commit in GitHub
git revert <commit-hash>
git push origin main
```

## CI/CD Pipeline

```
Push to main
    ↓
GitHub Actions
    ↓
Update CSV ─────→ Commit & Push
    ↓
Vercel Auto-Deploy
    ↓
Production API Live
```

## Support Checklist

- [ ] Vercel project created and connected
- [ ] Environment variables configured in Vercel
- [ ] GitHub Actions enabled
- [ ] GitHub secrets configured (if using BetterStack)
- [ ] First manual workflow run successful
- [ ] API endpoints tested in production
- [ ] Monitoring configured (optional)
- [ ] Documentation reviewed by team

## Next Steps After Deployment

1. Set up monitoring and alerting
2. Configure custom domain (optional)
3. Add authentication if needed
4. Implement rate limiting
5. Add more comprehensive tests
6. Set up staging environment
7. Configure backup strategy
