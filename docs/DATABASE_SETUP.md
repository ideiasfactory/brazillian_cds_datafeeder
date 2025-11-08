# Database Setup Guide

This guide explains how to set up and use the Neon PostgreSQL database for the Brazilian CDS data project.

## Table of Contents
- [Overview](#overview)
- [Local Development Setup](#local-development-setup)
- [Production Setup (Vercel + Neon)](#production-setup-vercel--neon)
- [Database Schema](#database-schema)
- [Migration](#migration)
- [Troubleshooting](#troubleshooting)

## Overview

The project uses **Neon PostgreSQL** as the production database, which is a serverless PostgreSQL service that integrates seamlessly with Vercel. In development mode, you can use either CSV files (default) or a local/remote PostgreSQL instance.

### Storage Modes

- **Development**: CSV files (default) or PostgreSQL if `NEON_DATABASE_URL` is set
- **Production**: PostgreSQL (required for Vercel serverless deployment)

## Local Development Setup

### Option 1: Using CSV Files (Default)

No additional setup required. The application will use CSV files in the `data/` directory.

### Option 2: Using PostgreSQL Locally

1. **Install PostgreSQL** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. **Create a database**:
   ```bash
   # Start PostgreSQL
   sudo service postgresql start  # Linux
   brew services start postgresql # macOS
   
   # Create database
   createdb brazilian_cds
   ```

3. **Configure environment variable** in `.env`:
   ```env
   NEON_DATABASE_URL=postgresql://user:password@localhost:5432/brazilian_cds
   ENVIRONMENT=development
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migration script**:
   ```bash
   python scripts/migrate_csv_to_db.py
   ```

## Production Setup (Vercel + Neon)

### Step 1: Create Neon Database

1. **Sign up for Neon**: Go to [Neon](https://neon.tech) and create an account (free tier available)

2. **Create a new project**:
   - Click "New Project"
   - Choose a name (e.g., "brazilian-cds")
   - Select a region close to your Vercel deployment
   - Copy the connection string

3. **Get connection string**:
   - Format: `postgresql://[user]:[password]@[host]/[database]?sslmode=require`
   - Example: `postgresql://user:pass@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require`

### Step 2: Configure Vercel

1. **Add environment variable** in Vercel dashboard:
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add variable:
     - Name: `NEON_DATABASE_URL`
     - Value: Your Neon connection string
     - Environment: Production

2. **Add to Vercel CLI** (optional):
   ```bash
   vercel env add NEON_DATABASE_URL
   # Paste your connection string when prompted
   ```

### Step 3: Configure GitHub Actions

1. **Add GitHub secret**:
   - Go to your repository settings
   - Navigate to "Secrets and variables" → "Actions"
   - Click "New repository secret"
   - Name: `NEON_DATABASE_URL`
   - Value: Your Neon connection string

2. **Verify workflow configuration** (already configured in `.github/workflows/update-cds-data.yml`):
   ```yaml
   env:
     NEON_DATABASE_URL: ${{ secrets.NEON_DATABASE_URL }}
     ENVIRONMENT: production
   ```

### Step 4: Initial Data Migration

1. **Local setup** (one-time):
   ```bash
   # Add database URL to .env
   echo "NEON_DATABASE_URL=your_connection_string" >> .env
   
   # Run migration
   python scripts/migrate_csv_to_db.py
   ```

2. **Verify migration**:
   ```bash
   python -c "
   import asyncio
   from src.storage.postgres_storage import PostgresStorage
   
   async def check():
       storage = PostgresStorage()
       stats = await storage.get_stats()
       print(f'Total records: {stats[\"total_records\"]}')
   
   asyncio.run(check())
   "
   ```

## Database Schema

### Table: `cds_data`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `date` | DATE | PRIMARY KEY | Trading date |
| `open` | NUMERIC(10,4) | | Opening price |
| `high` | NUMERIC(10,4) | | Highest price |
| `low` | NUMERIC(10,4) | | Lowest price |
| `close` | NUMERIC(10,4) | | Closing price |
| `change_pct` | NUMERIC(10,4) | | Percentage change |
| `created_at` | TIMESTAMP | DEFAULT now() | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT now() | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `date`
- INDEX on `date DESC` for latest queries

## Migration

### CSV to PostgreSQL

The migration script (`scripts/migrate_csv_to_db.py`) provides:

**Features**:
- Data validation (column checks, type conversion)
- Duplicate detection and handling
- Progress reporting
- Verification after migration

**Usage**:
```bash
python scripts/migrate_csv_to_db.py
```

**What it does**:
1. Reads CSV data from `data/brasil_CDS_historical.csv`
2. Validates data structure and types
3. Creates database tables if needed
4. Upserts data (insert or update on conflict)
5. Verifies migration success
6. Shows comparison between CSV and database

**Example output**:
```
============================================================
Brazilian CDS Data Migration Tool
CSV → PostgreSQL (Neon)
============================================================
[INFO] Starting CSV to PostgreSQL migration...
[INFO] Reading CSV data from: /path/to/brasil_CDS_historical.csv
[INFO] Loaded 1500 records from CSV
[INFO] Validating CSV data...
[SUCCESS] CSV validation passed. Total records: 1500
[INFO] Ensuring database tables exist...
[INFO] Migrating data to PostgreSQL...
[SUCCESS] Successfully migrated 1500 records to PostgreSQL
[INFO] Verifying migration...
[SUCCESS] Verification complete. Database contains 1500 records
[INFO] Latest record: 2025-01-07 - Close: 156.75
============================================================
[SUCCESS] Migration completed successfully!
============================================================
```

## Troubleshooting

### Connection Issues

**Problem**: `could not connect to server`

**Solutions**:
- Verify `NEON_DATABASE_URL` is correctly set
- Check network connectivity
- Ensure SSL mode is included: `?sslmode=require`
- Test connection manually:
  ```bash
  psql "your_connection_string"
  ```

### Migration Errors

**Problem**: `table already exists`

**Solution**: Tables are created automatically. If you need to reset:
```sql
-- Connect to database
psql "your_connection_string"

-- Drop and recreate
DROP TABLE IF EXISTS cds_data;
-- Run migration script again
```

**Problem**: `duplicate key value violates unique constraint`

**Solution**: The migration uses `ON CONFLICT` to handle duplicates automatically. If you still see this error, check your data for true duplicates.

### Performance Issues

**Problem**: Slow queries

**Solutions**:
- Ensure indexes are created (automatic on migration)
- Check Neon dashboard for connection limits
- Consider upgrading Neon plan for better performance

### Vercel Deployment

**Problem**: API returns 500 errors

**Solutions**:
1. Check Vercel logs: `vercel logs`
2. Verify environment variables are set
3. Ensure database URL is accessible from Vercel
4. Check Neon connection limits

**Problem**: Timeout errors

**Solution**: Neon free tier may suspend inactive databases. First request after suspension takes longer:
```python
# Add connection pooling (already configured)
# Pool warms up on first request
```

## Best Practices

1. **Security**:
   - Never commit `NEON_DATABASE_URL` to git
   - Use environment variables
   - Rotate credentials periodically

2. **Backups**:
   - Neon provides automatic backups
   - Keep CSV backups for critical data
   - Test restore procedures

3. **Monitoring**:
   - Check Neon dashboard for metrics
   - Monitor Vercel logs for errors
   - Set up alerts for failures

4. **Development**:
   - Use CSV in development by default
   - Test with database before production deploy
   - Run migration script in staging first

## Additional Resources

- [Neon Documentation](https://neon.tech/docs)
- [Vercel PostgreSQL Integration](https://vercel.com/docs/storage/vercel-postgres)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
