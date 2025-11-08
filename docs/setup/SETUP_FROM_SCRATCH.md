# Setup From Scratch Guide

This guide will walk you through setting up the Brazilian CDS Data Feeder project from scratch. Whether you're setting up for local development or production deployment, this document provides a comprehensive overview and references to detailed setup guides.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup Guides](#detailed-setup-guides)
- [Architecture Overview](#architecture-overview)
- [Troubleshooting](#troubleshooting)

## Overview

The Brazilian CDS Data Feeder is a production-ready application that:
- Scrapes Brazilian CDS (Credit Default Swap) data from Investing.com
- Provides a REST API to access historical data
- Supports dual deployment modes (local development and serverless production)
- Uses CSV storage for development and PostgreSQL (Neon) for production
- Runs automated daily data updates via GitHub Actions

## Prerequisites

Before starting, ensure you have:

### Required for Local Development
- **Python 3.11+** (managed via pyenv recommended)
- **Git** for version control
- **pip** for package management

### Required for Production Deployment
- **Vercel Account** (free tier available)
- **Neon PostgreSQL Account** (free tier available)
- **GitHub Account** (for automated updates via Actions)

### Optional
- **BetterStack Account** for centralized logging (optional)
- **Local PostgreSQL** if you want to test database locally

## Quick Start

For a rapid setup to get started immediately:

**👉 See [QUICKSTART.md](./QUICKSTART.md)**

The quickstart guide covers:
- Clone repository
- Install dependencies
- Configure environment
- Run first data update
- Start API server
- Access interactive documentation

**Estimated time: 10-15 minutes**

## Detailed Setup Guides

### 1. Environment Setup

#### Python Environment with pyenv

```bash
# Install pyenv (if not installed)
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11

# Create virtual environment
pyenv virtualenv 3.11 brazilian_cds_feeder

# Activate environment
pyenv activate brazilian_cds_feeder

# Install dependencies
pip install -r requirements.txt
```

#### Environment Variables

Create a `.env` file in the project root:

```env
# Environment Mode
ENVIRONMENT=development  # or 'production'

# Data Source
INVESTING_URL=https://br.investing.com/rates-bonds/brazil-cds-5-years-usd-historical-data

# Logging (Optional)
LOG_LEVEL=INFO
BETTERSTACK_SOURCE_TOKEN=your_token_here  # Optional

# Database (Required for Production)
NEON_DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 2. Development vs Production Setup

The project supports two distinct modes with different configurations:

**👉 See [DEV_PROD_GUIDE.md](../DEV_PROD_GUIDE.md)**

This guide explains:
- Environment detection
- Storage differences (CSV vs PostgreSQL)
- Configuration management
- Testing strategies
- Deployment workflows

### 3. Database Setup (Production)

For production deployment, you'll need to set up Neon PostgreSQL:

**👉 See [DATABASE_SETUP.md](../DATABASE_SETUP.md)**

This comprehensive guide covers:
- Creating Neon account and database
- Configuring Vercel environment variables
- Setting up GitHub Actions secrets
- Database schema documentation
- Migration from CSV to PostgreSQL
- Troubleshooting connection issues

**👉 Also see [NEON_POSTGRES_SETUP.md](./NEON_POSTGRES_SETUP.md)** for step-by-step Neon setup

**👉 See [POSTGRES_INTEGRATION.md](../POSTGRES_INTEGRATION.md)** for implementation details

### 4. Production Deployment

Deploy to Vercel with serverless functions and automated updates:

**👉 See [PRODUCTION_SETUP.md](./PRODUCTION_SETUP.md)**

Covers:
- Vercel deployment configuration
- Environment variable setup
- Domain configuration
- Serverless function optimization

**👉 See [DEPLOYMENT.md](./DEPLOYMENT.md)**

Covers:
- GitHub Actions workflow
- Automated daily updates
- Monitoring and alerts
- Rollback procedures

## Architecture Overview

### Project Structure

```
brazilian_cds/
├── config/              # Configuration management
│   └── settings.py      # Environment-based settings
├── src/
│   ├── api/            # FastAPI application
│   │   ├── main.py     # API entry point
│   │   ├── routes/     # API endpoints
│   │   └── models/     # Pydantic schemas
│   ├── database/       # Database layer
│   │   ├── models.py   # SQLAlchemy models
│   │   └── connection.py # Connection management
│   ├── scrapers/       # Web scraping
│   │   └── investing_scraper.py
│   ├── storage/        # Data storage
│   │   ├── csv_storage.py      # CSV operations
│   │   └── postgres_storage.py # PostgreSQL operations
│   └── utils/          # Utilities
│       └── logger.py   # Logging configuration
├── scripts/            # CLI scripts
│   ├── update_cds.py   # Data update script
│   ├── start_api.py    # API server starter
│   └── migrate_csv_to_db.py # Migration tool
├── api/               # Vercel serverless entry
│   └── index.py
├── .github/
│   └── workflows/     # GitHub Actions
│       └── update-cds-data.yml
├── docs/              # Documentation
│   ├── setup/         # Setup guides
│   └── *.md          # Technical docs
└── tests/            # Test suite
```

### Data Flow

**Development Mode:**
```
Investing.com → Scraper → CSV Storage → Local File
                                      ↓
                                   FastAPI → JSON Response
```

**Production Mode:**
```
Investing.com → Scraper → PostgreSQL → Neon Database
                                      ↓
                           Vercel Serverless API → JSON Response
                                      ↓
                           GitHub Actions (Daily Cron)
```

### Technology Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Scraping**: requests, lxml, pandas
- **Database**: PostgreSQL (via asyncpg, SQLAlchemy async)
- **Deployment**: Vercel (serverless functions)
- **CI/CD**: GitHub Actions (cron jobs)
- **Logging**: loguru, BetterStack (optional)
- **Environment**: python-dotenv, pyenv

## Setup Workflow

### For First-Time Setup (No Resources Created Yet)

Follow this sequence:

1. **Clone and Install** (5 minutes)
   ```bash
   git clone <repository>
   cd brazilian_cds
   pyenv virtualenv 3.11 brazilian_cds_feeder
   pyenv activate brazilian_cds_feeder
   pip install -r requirements.txt
   ```

2. **Configure Environment** (3 minutes)
   ```bash
   cp .env.example .env  # If available
   # Edit .env with your settings
   ```

3. **Test Locally with CSV** (2 minutes)
   ```bash
   # Update data
   python scripts/update_cds.py
   
   # Start API
   python scripts/start_api.py
   
   # Visit http://localhost:8000/docs
   ```

4. **Create Neon Database** (5-10 minutes)
   - Sign up at [neon.tech](https://neon.tech)
   - Create project
   - Copy connection string
   - Add to `.env`: `NEON_DATABASE_URL=postgresql://...`
   
   **See [DATABASE_SETUP.md](../DATABASE_SETUP.md) for detailed steps**

5. **Migrate Data to Database** (2 minutes)
   ```bash
   python scripts/migrate_csv_to_db.py
   ```

6. **Test with Database** (2 minutes)
   ```bash
   ENVIRONMENT=production python scripts/update_cds.py
   ENVIRONMENT=production python scripts/start_api.py
   ```

7. **Deploy to Vercel** (10 minutes)
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Login
   vercel login
   
   # Deploy
   vercel
   
   # Add environment variable
   vercel env add NEON_DATABASE_URL
   
   # Deploy to production
   vercel --prod
   ```
   
   **See [PRODUCTION_SETUP.md](./PRODUCTION_SETUP.md) for detailed steps**

8. **Configure GitHub Actions** (5 minutes)
   - Go to repository Settings → Secrets → Actions
   - Add `NEON_DATABASE_URL` secret
   - Add `BETTERSTACK_SOURCE_TOKEN` secret (optional)
   - Workflow will run daily at 02:00 UTC
   
   **See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed steps**

### Total Estimated Time
- **Basic setup (CSV only)**: ~15 minutes
- **Full setup (with database and deployment)**: ~45-60 minutes

## Verification Steps

After setup, verify everything works:

### 1. Local Verification

```bash
# Check data file exists
ls -lh data/brasil_CDS_historical.csv

# Check data update works
python scripts/update_cds.py

# Check API works
python scripts/start_api.py &
curl http://localhost:8000/health
curl http://localhost:8000/cds/latest
```

### 2. Database Verification

```bash
# Check database connection
python -c "
import asyncio
from src.storage.postgres_storage import PostgresStorage

async def check():
    storage = PostgresStorage()
    stats = await storage.get_stats()
    print(f'Records: {stats[\"total_records\"]}')
    print(f'Latest: {stats[\"latest_date\"]}')

asyncio.run(check())
"
```

### 3. Production Verification

```bash
# Check Vercel deployment
curl https://your-app.vercel.app/health
curl https://your-app.vercel.app/cds/latest

# Check GitHub Actions
# Go to Actions tab in GitHub repository
# Verify workflow runs successfully
```

## Troubleshooting

### Common Issues

#### 1. Python/Dependency Issues

**Problem**: Import errors or missing packages

**Solution**:
```bash
# Ensure virtual environment is activated
pyenv activate brazilian_cds_feeder

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Scraping Issues

**Problem**: "No data fetched" or "Table not found"

**Solution**:
- Check internet connection
- Verify `INVESTING_URL` in `.env`
- Website structure may have changed (check `TABLE_XPATH`)
- Try with different user agent

#### 3. Database Connection Issues

**Problem**: "could not connect to server"

**Solution**:
- Verify `NEON_DATABASE_URL` is correct
- Ensure SSL mode: `?sslmode=require`
- Check Neon dashboard for database status
- Test connection: `psql "your_connection_string"`

**See [DATABASE_SETUP.md](../DATABASE_SETUP.md#troubleshooting)** for more details

#### 4. Vercel Deployment Issues

**Problem**: API returns 500 errors

**Solution**:
```bash
# Check logs
vercel logs

# Verify environment variables
vercel env ls

# Redeploy
vercel --prod --force
```

#### 5. GitHub Actions Issues

**Problem**: Workflow fails

**Solution**:
- Check Actions logs in GitHub
- Verify secrets are set correctly
- Ensure `NEON_DATABASE_URL` secret exists
- Test script locally first

## Additional Resources

### Documentation Index

- **[README.md](../../README.md)** - Project overview
- **[QUICKSTART.md](./QUICKSTART.md)** - Fast setup guide
- **[DEV_PROD_GUIDE.md](../DEV_PROD_GUIDE.md)** - Development vs Production
- **[DATABASE_SETUP.md](../DATABASE_SETUP.md)** - Database configuration
- **[NEON_POSTGRES_SETUP.md](./NEON_POSTGRES_SETUP.md)** - Neon setup steps
- **[POSTGRES_INTEGRATION.md](../POSTGRES_INTEGRATION.md)** - Implementation details
- **[PRODUCTION_SETUP.md](./PRODUCTION_SETUP.md)** - Vercel deployment
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - CI/CD with GitHub Actions
- **[REFACTORING_SUMMARY.md](../REFACTORING_SUMMARY.md)** - Project history

### External Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vercel Documentation](https://vercel.com/docs)
- [Neon Documentation](https://neon.tech/docs)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [pyenv Documentation](https://github.com/pyenv/pyenv)

## Getting Help

If you encounter issues not covered in this guide:

1. Check the specific setup guides referenced above
2. Review error messages carefully
3. Check logs (application, Vercel, GitHub Actions)
4. Verify environment variables are set correctly
5. Test components individually (scraper, storage, API)

## Next Steps

After completing setup:

1. **Customize Configuration**: Adjust settings in `.env` for your needs
2. **Set Up Monitoring**: Configure BetterStack for centralized logging
3. **Add Tests**: Write tests for your specific use cases
4. **Configure Alerts**: Set up alerts for workflow failures
5. **Optimize Performance**: Review and tune connection pooling, caching, etc.
6. **Scale**: Consider Neon and Vercel paid plans for higher limits

---

**Last Updated**: November 7, 2025

**Questions?** Check the other documentation files in the `docs/` folder for detailed information on specific topics.
