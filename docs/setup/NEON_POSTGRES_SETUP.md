# Vercel + Neon Postgres Setup Guide

## Why Neon Postgres?

For production deployment with Vercel serverless, we need persistent storage. **Neon Serverless Postgres** is the best choice because:

- ✅ **Structured Data**: Perfect for OHLC time-series data
- ✅ **Serverless**: Scales automatically, pay-per-use
- ✅ **SQL Queries**: Complex filtering, aggregations, date ranges
- ✅ **Free Tier**: 0.5GB storage, 100 hours compute/month
- ✅ **Postgres**: Full PostgreSQL compatibility
- ✅ **Fast**: Low latency reads from Vercel

## Architecture

```
┌─────────────────────────────────────┐
│      GitHub Actions (Daily)         │
│  1. Scrape Investing.com            │
│  2. INSERT/UPDATE Neon Postgres     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│       Neon Postgres Database        │
│  Table: cds_data                    │
│  - date (PRIMARY KEY)               │
│  - open, high, low, close           │
│  - change_pct                       │
│  - created_at, updated_at           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│     Vercel Serverless API           │
│  - GET /health                      │
│  - GET /cds/ (query database)       │
│  - GET /cds/latest                  │
│  - GET /cds/stats                   │
└─────────────────────────────────────┘
```

## Setup Steps

### 1. Create Neon Database

1. Go to Vercel Dashboard
2. Click **Storage** tab
3. Click **Create Database**
4. Select **Neon** (Postgres)
5. Choose **Free Tier**
6. Name: `brazilian-cds-db`
7. Click **Create**

Vercel will automatically:
- Create Neon database
- Add connection string to your project env vars
- Set up `POSTGRES_URL`, `POSTGRES_PRISMA_URL`, etc.

### 2. Install Dependencies

Add to `requirements.txt`:
```
psycopg2-binary
sqlalchemy
```

Or for async (recommended):
```
asyncpg
sqlalchemy[asyncio]
```

### 3. Database Schema

The project will create this table automatically:

```sql
CREATE TABLE cds_data (
    date DATE PRIMARY KEY,
    open NUMERIC(10, 4),
    high NUMERIC(10, 4),
    low NUMERIC(10, 4),
    close NUMERIC(10, 4) NOT NULL,
    change_pct NUMERIC(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cds_date ON cds_data(date DESC);
```

### 4. Environment Variables

Vercel automatically adds these when you create Neon database:
- `POSTGRES_URL` - Full connection string
- `POSTGRES_PRISMA_URL` - For Prisma ORM
- `POSTGRES_URL_NON_POOLING` - Direct connection
- `POSTGRES_USER` - Database user
- `POSTGRES_HOST` - Database host
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DATABASE` - Database name

For GitHub Actions, add these as **Repository Secrets**:
- `NEON_DATABASE_URL` - Copy from Vercel env vars

### 5. Migration Strategy

**From CSV to Database:**

Run migration script once (locally or in GitHub Actions):
```bash
python scripts/migrate_csv_to_db.py
```

This will:
- Read existing `data/brasil_CDS_historical.csv`
- Create database table
- Insert all historical data
- Verify data integrity

## Benefits vs CSV Storage

| Feature | CSV (GitHub) | Neon Postgres |
|---------|--------------|---------------|
| Query Speed | Slow (full scan) | Fast (indexed) |
| Concurrent Reads | Limited | Unlimited |
| Filtering | Load all → filter | Server-side query |
| Updates | Overwrite file | UPDATE statement |
| Backups | Git history | Neon auto-backup |
| Data Integrity | None | Constraints/ACID |
| Scalability | Poor | Excellent |
| API Latency | Medium | Low |

## Updated File Structure

```
brazilian_cds/
├── src/
│   ├── storage/
│   │   ├── csv_storage.py      # Keep for local dev
│   │   └── postgres_storage.py # NEW: Postgres operations
│   └── database/
│       ├── __init__.py
│       ├── models.py            # NEW: SQLAlchemy models
│       └── connection.py        # NEW: Database connection
├── scripts/
│   ├── migrate_csv_to_db.py   # NEW: Migration script
│   └── update_cds.py           # Updated for Postgres
└── alembic/                     # Optional: DB migrations
```

## Development vs Production

### Local Development
- Uses CSV files (as before)
- No database required
- Fast iteration
- `ENVIRONMENT=development`

### Production (Vercel)
- Uses Neon Postgres
- Persistent data
- Scalable queries
- `ENVIRONMENT=production`

## Cost Analysis

### Neon Free Tier
- **Storage**: 0.5GB (plenty for time-series data)
- **Compute**: 100 hours/month
- **Estimate**: ~1GB for 10 years of daily data
- **Cost**: $0/month (within free tier)

### Vercel Free Tier
- **API Calls**: Unlimited within bandwidth
- **Bandwidth**: 100GB/month
- **Functions**: 100GB-hours
- **Cost**: $0/month

**Total**: $0/month

## Data Retention

Your use case: ~250 trading days/year
- 1 year = 250 records
- 10 years = 2,500 records
- Size: ~100KB

**Neon free tier (0.5GB) = 50+ years of data** ✅

## Backup Strategy

1. **Neon Auto-Backup**: 7 days retention
2. **GitHub Actions**: Daily export to CSV (backup)
3. **Manual Export**: Download via API

## Security

- ✅ Connection pooling
- ✅ SSL/TLS encryption
- ✅ Vercel managed secrets
- ✅ No direct database access
- ✅ API rate limiting

## Next Steps

1. ✅ Create Neon database in Vercel
2. ✅ Install Python Postgres dependencies
3. ✅ Run code generation (next message)
4. ✅ Run migration script
5. ✅ Update GitHub Actions workflow
6. ✅ Deploy to Vercel
7. ✅ Test API endpoints

Ready to proceed with code implementation?
