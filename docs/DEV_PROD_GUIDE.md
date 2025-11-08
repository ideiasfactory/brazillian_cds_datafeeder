# Development vs Production Cheat Sheet

## Quick Reference

### Local Development
```bash
# Setup
pyenv local brazilian_cds_feeder
pip install -r requirements.txt
cp .env.example .env

# Update data
python scripts/update_cds.py

# Start API (with hot reload)
python scripts/start_api.py

# Or with uvicorn directly
uvicorn src.api.main:app --reload
```

### Production Deployment

#### Vercel (API)
```bash
# One-time setup
npm install -g vercel
vercel login
vercel

# Deploy updates
git push origin main  # Auto-deploys

# Manual deploy
vercel --prod
```

#### GitHub Actions (CronJob)
```bash
# Runs automatically daily at 02:00 UTC
# Manual trigger: Actions tab > Run workflow

# Check status
# Repository > Actions > Update CDS Data Daily
```

## Environment Variables

### Development (.env)
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
```

### Production (Vercel Dashboard)
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
# Add BetterStack tokens if using
```

## Testing

### Local
```bash
# Test update script
python scripts/update_cds.py

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/cds/latest?n=5
```

### Production
```bash
# Test API
curl https://your-project.vercel.app/health
curl https://your-project.vercel.app/cds/stats
curl https://your-project.vercel.app/cds/latest?n=5
```

## File Locations

### Development
- Data: `data/brasil_CDS_historical.csv`
- Backups: `data/brasil_CDS_historical__bkp_*.csv`
- Logs: Console

### Production
- Data: GitHub repository (read-only in Vercel)
- Backups: Not created (ephemeral filesystem)
- Logs: Vercel logs or BetterStack

## Common Tasks

### Add New Environment Variable
1. Add to `config/settings.py`
2. Add to `.env.example`
3. Update local `.env`
4. Add to Vercel Dashboard (if needed in prod)
5. Add to GitHub Secrets (if needed in Actions)

### Update Dependencies
```bash
# Local
pip install package_name
pip freeze > requirements.txt

# Production
git push origin main  # Vercel auto-redeploys
```

### View Logs

**Local:**
```bash
# Shown in terminal
```

**Production API (Vercel):**
```bash
# Via dashboard: Project > Deployments > View Function Logs
# Via CLI: vercel logs
```

**Production CronJob (GitHub Actions):**
```bash
# Repository > Actions > Select workflow run > View logs
```

## Troubleshooting

### "Module not found" in Vercel
- Check `requirements.txt` has all dependencies
- Verify `api/index.py` path setup is correct

### Data not updating in production
- Check GitHub Actions logs
- Verify workflow has write permissions
- Check if CSV is in repository

### API returns 500 error
- Check Vercel function logs
- Verify environment variables
- Check CSV file exists and is readable

## URLs

### Development
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Production
- API: https://your-project.vercel.app
- Docs: https://your-project.vercel.app/docs
- ReDoc: https://your-project.vercel.app/redoc
- GitHub Actions: https://github.com/your-username/your-repo/actions

## Deployment Checklist

Before going to production:

- [ ] Test locally: `python scripts/update_cds.py`
- [ ] Test API locally: `python scripts/start_api.py`
- [ ] Create Vercel project
- [ ] Set Vercel environment variables
- [ ] Deploy to Vercel
- [ ] Test production API endpoints
- [ ] Enable GitHub Actions
- [ ] Set GitHub secrets (optional)
- [ ] Trigger first manual workflow run
- [ ] Verify data updates and commits
- [ ] Check API serves updated data

## Key Differences: Dev vs Prod

| Feature | Development | Production |
|---------|------------|------------|
| Environment | `development` | `production` |
| Data Location | `data/` directory | GitHub repo → `/tmp` in Vercel |
| Data Updates | Manual script | GitHub Actions (automated) |
| API Server | Uvicorn (local) | Vercel Serverless |
| Hot Reload | Enabled | Disabled |
| Logging | Console only | Console + BetterStack (opt) |
| Backups | Created | Not created |
| File System | Writable | Read-only (ephemeral) |

## Workflow

### Development Workflow
```
1. Make code changes
2. Test locally: python scripts/update_cds.py
3. Test API: python scripts/start_api.py
4. Verify endpoints work
5. Commit changes
6. Push to GitHub
```

### Production Workflow
```
1. GitHub Actions runs daily (02:00 UTC)
2. Scrapes Investing.com
3. Updates CSV in repository
4. Commits and pushes
5. Vercel detects push
6. Auto-redeploys API
7. API serves fresh data
```

## Support

- Documentation: `README.md`
- Deployment Guide: `DEPLOYMENT.md`
- Quick Start: `QUICKSTART.md`
- Refactoring Notes: `REFACTORING_SUMMARY.md`
