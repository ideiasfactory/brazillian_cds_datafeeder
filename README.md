# Brazilian CDS Data Feeder

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready, modular Python application for scraping, storing, and serving Brazilian CDS (Credit Default Swap) 5-year historical data from Investing.com. Features dual-mode deployment with local CSV storage for development and PostgreSQL for production serverless deployment.

## ✨ Features

- 🔄 **Automated Data Scraping**: Robust web scraper with retry logic and multiple parsing strategies
- 💾 **Dual Storage System**: 
  - CSV storage for local development (with auto-backup and deduplication)
  - PostgreSQL (Neon) for production with async operations
- 🚀 **REST API**: FastAPI-powered API with automatic OpenAPI documentation
- ☁️ **Serverless Deployment**: Vercel-ready with optimized serverless functions
- ⏰ **Automated Updates**: GitHub Actions cron job for daily data updates (02:00 UTC)
- � **Environment Detection**: Automatic storage selection based on environment
- 📊 **Comprehensive Logging**: Structured logging with optional BetterStack integration
- 🗄️ **Database Migration**: Tools for CSV to PostgreSQL data migration
- � **Production Ready**: Connection pooling, error handling, and monitoring
- 📈 **Data Analytics**: Statistics endpoints for data insights

## 📁 Project Structure

```
brazilian_cds/
├── api/                    # Vercel serverless entry point
│   └── index.py           # Serverless function handler
├── config/                 # Configuration management
│   ├── __init__.py
│   └── settings.py        # Environment-based settings
├── data/                   # Local data storage (development)
│   └── brasil_CDS_historical.csv
├── docs/                   # Documentation
│   ├── setup/             # Setup guides
│   │   ├── SETUP_FROM_SCRATCH.md
│   │   ├── QUICKSTART.md
│   │   ├── VERCEL_SETUP.md
│   │   ├── NEON_POSTGRES_SETUP.md
│   │   ├── DEPLOYMENT.md
│   │   └── PRODUCTION_SETUP.md
│   ├── DATABASE_SETUP.md
│   ├── DEV_PROD_GUIDE.md
│   ├── POSTGRES_INTEGRATION.md
│   └── REFACTORING_SUMMARY.md
├── scripts/                # Executable scripts
│   ├── update_cds.py      # Data update script (CLI)
│   ├── start_api.py       # API server starter
│   └── migrate_csv_to_db.py # Database migration tool
├── src/                    # Source code
│   ├── api/               # FastAPI application
│   │   ├── main.py        # FastAPI app instance
│   │   ├── models/        # Pydantic schemas
│   │   │   └── schemas.py
│   │   └── routes/        # API endpoints
│   │       ├── health.py  # Health check
│   │       └── cds.py     # CDS data routes
│   ├── database/          # Database layer
│   │   ├── models.py      # SQLAlchemy models
│   │   └── connection.py  # Async DB connection
│   ├── scrapers/          # Web scrapers
│   │   └── investing_scraper.py
│   ├── storage/           # Data storage layer
│   │   ├── csv_storage.py       # CSV operations
│   │   └── postgres_storage.py  # PostgreSQL operations
│   └── utils/             # Utilities
│       └── logger.py      # Logging configuration
├── tests/                  # Test suite
├── .github/
│   └── workflows/
│       └── update-cds-data.yml  # Daily cron job
├── .env.example           # Environment template
├── .gitignore             # Git ignore patterns
├── .vercelignore          # Vercel ignore patterns
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/ideiasfactory/brazillian_cds_datafeeder.git
   cd brazillian_cds_datafeeder
   ```

2. **Create and activate a virtual environment**:

   ```bash
   # Using pyenv (recommended)
   pyenv install 3.11
   pyenv virtualenv 3.11 brazilian_cds_feeder
   pyenv activate brazilian_cds_feeder
   
   # Or using venv
   python3.11 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your settings (optional for basic usage)
   ```

5. **Fetch initial data**:

   ```bash
   python scripts/update_cds.py
   ```

6. **Start the API server**:

   ```bash
   python scripts/start_api.py
   ```

7. **Access the API**:
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health
   - Latest data: http://localhost:8000/cds/latest

For detailed setup instructions, see [docs/setup/SETUP_FROM_SCRATCH.md](docs/setup/SETUP_FROM_SCRATCH.md).

## ⚙️ Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and configure:

### Environment Variables

```bash
# Environment Mode
ENVIRONMENT=development  # or 'production'

# Data Source Configuration
INVESTING_URL=https://br.investing.com/rates-bonds/brazil-cds-5-years-usd-historical-data
CSV_OUTPUT_PATH=brasil_CDS_historical.csv

# Database Configuration (Required for Production)
NEON_DATABASE_URL=postgresql://user:pass@host/database?sslmode=require

# Logging Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# BetterStack (Logtail) Configuration (Optional)
BETTERSTACK_SOURCE_TOKEN=your_token_here
BETTERSTACK_INGESTING_HOST=in.logtail.com

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# HTTP Request Configuration (Advanced)
USER_AGENT=Mozilla/5.0...
REQUEST_TIMEOUT=20
REQUEST_RETRIES=3
```

### Storage Modes

The application automatically selects storage based on environment:

- **Development** (`ENVIRONMENT=development`): Uses CSV files in `data/` directory
- **Production** (`ENVIRONMENT=production` or `NEON_DATABASE_URL` set): Uses PostgreSQL database

See [docs/DEV_PROD_GUIDE.md](docs/DEV_PROD_GUIDE.md) for details.

## 💻 Usage

### Local Development

#### Update CDS Data

Fetch the latest CDS data from Investing.com:

```bash
python scripts/update_cds.py
```

The script will:
- Scrape data from Investing.com
- Merge with existing data
- Remove duplicates
- Create automatic backups
- Show statistics

#### Start the API Server

Run the FastAPI development server:

```bash
python scripts/start_api.py
```

Or use uvicorn directly with auto-reload:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Access API Documentation

Once running, visit:
- **Interactive Docs (Swagger UI)**: <http://localhost:8000/docs>
- **Alternative Docs (ReDoc)**: <http://localhost:8000/redoc>
- **OpenAPI Schema**: <http://localhost:8000/openapi.json>

### Production Deployment

The application is designed for serverless deployment on Vercel with PostgreSQL storage.

#### Prerequisites

1. **Neon PostgreSQL Database**: Create at [neon.tech](https://neon.tech)
   - See [docs/setup/NEON_POSTGRES_SETUP.md](docs/setup/NEON_POSTGRES_SETUP.md)

2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
   - See [docs/setup/VERCEL_SETUP.md](docs/setup/VERCEL_SETUP.md)

#### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy to production
vercel --prod
```

#### Configure GitHub Actions

Daily automated updates run via GitHub Actions (02:00 UTC).

**Required Secrets** (Repository Settings → Secrets → Actions):
- `NEON_DATABASE_URL`: PostgreSQL connection string
- `BETTERSTACK_SOURCE_TOKEN`: Logging token (optional)

See [docs/setup/DEPLOYMENT.md](docs/setup/DEPLOYMENT.md) for complete guide.

### Database Migration

If you have existing CSV data and want to migrate to PostgreSQL:

```bash
# Set database URL in .env
echo "NEON_DATABASE_URL=postgresql://..." >> .env

# Run migration
python scripts/migrate_csv_to_db.py
```

The migration script will:
- Validate CSV data structure
- Check for duplicates
- Create database tables
- Transfer data with upserts
- Verify migration success

See [docs/DATABASE_SETUP.md](docs/DATABASE_SETUP.md) for details.

## 📡 API Endpoints

### Health Check

```bash
GET /health
```

Returns API health status and environment information.

**Example:**

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "healthy",
  "environment": "development"
}
```

### Get CDS Data

```bash
GET /cds/
```

Retrieve CDS data with optional filtering.

**Query Parameters:**
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)
- `limit` (optional): Maximum records to return (1-10000)

**Examples:**

```bash
# Get all data
curl http://localhost:8000/cds/

# Filter by date range
curl "http://localhost:8000/cds/?start_date=2025-01-01&end_date=2025-11-07"

# Limit results
curl "http://localhost:8000/cds/?limit=100"

# Combine filters
curl "http://localhost:8000/cds/?start_date=2025-01-01&limit=50"
```

### Get Latest Records

```bash
GET /cds/latest
```

Retrieve the most recent N CDS records.

**Query Parameters:**
- `n` (optional): Number of records (default: 10, max: 1000)

**Example:**

```bash
curl "http://localhost:8000/cds/latest?n=20"
```

### Get Statistics

```bash
GET /cds/stats
```

Get dataset statistics including record count and date range.

**Example:**

```bash
curl http://localhost:8000/cds/stats
```

**Response:**

```json
{
  "total_records": 1500,
  "oldest_date": "2020-01-02",
  "latest_date": "2025-11-07",
  "latest_close": 156.75,
  "date_range_days": 2136
}
```

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **Python 3.11+**: Core language
- **FastAPI**: Modern web framework for APIs
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

**Data Processing:**
- **pandas**: Data manipulation and analysis
- **requests**: HTTP client for web scraping
- **lxml**: HTML/XML parsing

**Database:**
- **PostgreSQL**: Production database (Neon)
- **SQLAlchemy**: Async ORM
- **asyncpg**: Async PostgreSQL driver

**Deployment:**
- **Vercel**: Serverless hosting
- **GitHub Actions**: CI/CD automation

**Monitoring:**
- **loguru**: Structured logging
- **BetterStack (Logtail)**: Centralized log management (optional)

### Architecture Patterns

#### Modular Design

The project follows a clean architecture with separation of concerns:

```
┌─────────────────────────────────────────────────┐
│                  API Layer                      │
│         (FastAPI Routes & Models)               │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Business Logic                     │
│     (Scrapers, Storage, Processing)             │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│             Data Layer                          │
│  (CSV Storage / PostgreSQL Database)            │
└─────────────────────────────────────────────────┘
```

#### Storage Strategy

**Development Mode:**
```
Investing.com → Scraper → CSV Storage → data/
                                      ↓
                           FastAPI → JSON Response
```

**Production Mode:**
```
Investing.com → Scraper → PostgreSQL → Neon Database
                                      ↓
                           Vercel API → JSON Response
                                      ↓
                        GitHub Actions (Daily Cron)
```

#### Key Design Patterns

- **Repository Pattern**: `CDSStorage` and `PostgresStorage` abstract data access
- **Singleton Configuration**: Single `settings` instance for configuration
- **Dependency Injection**: Loose coupling between components
- **Factory Pattern**: Storage selection based on environment
- **Strategy Pattern**: Different storage strategies (CSV vs PostgreSQL)
- **Async/Await**: Non-blocking I/O for database operations

### Data Flow

1. **Scraping**: `InvestingScraper` fetches HTML from Investing.com
2. **Parsing**: Multiple parsing strategies for robustness
3. **Validation**: Pydantic models ensure data integrity
4. **Storage**: Environment-based storage selection
5. **API**: FastAPI serves data with automatic documentation
6. **Automation**: GitHub Actions triggers daily updates

### Environment-Based Behavior

The application automatically adapts based on `ENVIRONMENT` variable:

| Feature | Development | Production |
|---------|-------------|------------|
| Storage | CSV files | PostgreSQL (Neon) |
| Location | `data/` directory | Cloud database |
| API Server | Uvicorn (local) | Vercel (serverless) |
| Updates | Manual script | GitHub Actions (cron) |
| Logging | Console | BetterStack (optional) |
| CORS | Permissive | Configured |

## 🧪 Development

### Development Setup

Install development dependencies:

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_scraper.py

# Run with verbose output
pytest -v
```

### Code Quality

Format code:

```bash
# Format with black
black src/ scripts/ tests/

# Sort imports
isort src/ scripts/ tests/

# Both together
black src/ scripts/ tests/ && isort src/ scripts/ tests/
```

Type checking:

```bash
mypy src/
```

Linting:

```bash
# Run flake8
flake8 src/ scripts/

# Run pylint
pylint src/ scripts/
```

### Project Guidelines

- **PEP 8**: Follow Python style guide
- **Type Hints**: Use type annotations
- **Docstrings**: Document all public functions and classes
- **Error Handling**: Use comprehensive try-except blocks
- **Logging**: Use structured logging (loguru)
- **Testing**: Maintain test coverage above 80%

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

### Setup Guides

- **[SETUP_FROM_SCRATCH.md](docs/setup/SETUP_FROM_SCRATCH.md)** - Complete setup guide for new users
- **[QUICKSTART.md](docs/setup/QUICKSTART.md)** - Fast 15-minute setup
- **[VERCEL_SETUP.md](docs/setup/VERCEL_SETUP.md)** - Vercel deployment step-by-step
- **[NEON_POSTGRES_SETUP.md](docs/setup/NEON_POSTGRES_SETUP.md)** - Database setup guide
- **[DEPLOYMENT.md](docs/setup/DEPLOYMENT.md)** - GitHub Actions configuration
- **[PRODUCTION_SETUP.md](docs/setup/PRODUCTION_SETUP.md)** - Production deployment

### Technical Documentation

- **[DATABASE_SETUP.md](docs/DATABASE_SETUP.md)** - Database configuration and migration
- **[DEV_PROD_GUIDE.md](docs/DEV_PROD_GUIDE.md)** - Development vs Production differences
- **[POSTGRES_INTEGRATION.md](docs/POSTGRES_INTEGRATION.md)** - PostgreSQL implementation details
- **[REFACTORING_SUMMARY.md](docs/REFACTORING_SUMMARY.md)** - Project evolution and history

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Contribution Guidelines

- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Follow existing code style
- Ensure all tests pass before submitting

## 🐛 Troubleshooting

### Common Issues

#### Import Errors

**Problem:** `ModuleNotFoundError` when running scripts

**Solution:**
```bash
# Ensure virtual environment is activated
pyenv activate brazilian_cds_feeder  # or source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Data Not Found

**Problem:** API returns 404 or "No data found"

**Solution:**
```bash
# Run the update script first
python scripts/update_cds.py

# Check if data file exists
ls -lh data/brasil_CDS_historical.csv

# For production, check database connection
python -c "from config import settings; print(settings.DATABASE_URL)"
```

#### Scraping Fails

**Problem:** "No data fetched" or "Table not found"

**Solution:**
- Check internet connectivity
- Verify Investing.com is accessible
- Website structure may have changed (check `TABLE_XPATH` in settings)
- Try with different `USER_AGENT` in `.env`

#### Database Connection Issues

**Problem:** Cannot connect to PostgreSQL

**Solution:**
```bash
# Verify DATABASE_URL format
echo $NEON_DATABASE_URL

# Test connection
psql "$NEON_DATABASE_URL"

# Check Neon dashboard for database status
# Free tier databases may be suspended when idle
```

#### Vercel Deployment Fails

**Problem:** Deployment errors or API returns 500

**Solution:**
```bash
# Check Vercel logs
vercel logs

# Verify environment variables
vercel env ls

# Ensure NEON_DATABASE_URL is set
vercel env add NEON_DATABASE_URL

# Force redeploy
vercel --prod --force
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Data source: [Investing.com](https://br.investing.com/)
- Hosting: [Vercel](https://vercel.com/)
- Database: [Neon](https://neon.tech/)
- Logging: [BetterStack](https://betterstack.com/)

## 📞 Support

For questions, issues, or suggestions:

- **Issues**: [GitHub Issues](https://github.com/ideiasfactory/brazillian_cds_datafeeder/issues)
- **Documentation**: See `docs/` directory
- **Email**: [Contact maintainer]

## 🗺️ Roadmap

Future enhancements planned:

- [ ] Add more financial instruments (10Y, 20Y CDS)
- [ ] Real-time data updates via WebSocket
- [ ] Data visualization dashboard
- [ ] Historical data analysis endpoints
- [ ] Export to multiple formats (JSON, XML, Excel)
- [ ] Caching layer for improved performance
- [ ] Rate limiting and API authentication
- [ ] Comprehensive test coverage (>90%)
- [ ] Docker containerization
- [ ] Grafana/Prometheus monitoring

---

**Made with ❤️ for the Brazilian financial data community**
