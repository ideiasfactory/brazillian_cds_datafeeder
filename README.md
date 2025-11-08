# Brazilian CDS Data Feeder

A modular Python application for scraping, storing, and serving Brazilian CDS (Credit Default Swap) historical data from Investing.com.

## Features

- 🔄 **Data Scraper**: Automated scraping of Brazilian CDS data from Investing.com
- 💾 **CSV Storage**: Efficient storage with automatic deduplication and backup
- 🚀 **REST API**: FastAPI-powered API for accessing historical data
- ☁️ **Serverless Deployment**: Vercel-ready for production deployment
- ⏰ **Automated Updates**: GitHub Actions cron job for daily data updates
- 📊 **Logging**: Comprehensive logging with optional BetterStack integration
- ⚙️ **Configurable**: Environment-based configuration for flexibility
- 🔀 **Multi-Environment**: Separate dev and production configurations

## Project Structure

```
brazilian_cds/
├── config/              # Configuration settings
│   ├── __init__.py
│   └── settings.py      # Centralized settings
├── data/                # Data storage directory
│   └── brasil_CDS_historical.csv
├── scripts/             # Executable scripts
│   └── update_cds.py    # CLI script to update CDS data
├── src/                 # Source code
│   ├── api/            # FastAPI application
│   │   ├── main.py     # FastAPI app
│   │   ├── models/     # Pydantic models
│   │   └── routes/     # API routes
│   ├── scrapers/       # Web scrapers
│   │   └── investing_scraper.py
│   ├── storage/        # Data storage
│   │   └── csv_storage.py
│   └── utils/          # Utilities
│       └── logger.py   # Logging configuration
├── tests/              # Unit tests
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore file
├── requirements.txt    # Python dependencies
├── setup.py            # Package setup
└── README.md           # This file
```

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create and activate a virtual environment**:
   ```bash
   pyenv virtualenv 3.11.0 brazilian_cds_feeder
   pyenv local brazilian_cds_feeder
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# BetterStack (Logtail) Configuration (optional)
BETTERSTACK_SOURCE_TOKEN=your_token_here
BETTERSTACK_INGESTING_HOST=in.logtail.com

# Logging Configuration
LOG_LEVEL=INFO

# Data Source Configuration
INVESTING_URL=https://br.investing.com/rates-bonds/brazil-cds-5-years-usd-historical-data
CSV_OUTPUT_PATH=brasil_CDS_historical.csv

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
```

## Usage

### Local Development

#### Update CDS Data

Run the data scraper to fetch and update CDS data:

```bash
python scripts/update_cds.py
```

#### Start the API

Run the FastAPI server:

```bash
python scripts/start_api.py
```

Or use uvicorn directly:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for comprehensive deployment guide.

**Quick Overview:**
- **API**: Deploy to Vercel (serverless)
- **Data Updates**: GitHub Actions cron job (daily at 02:00 UTC)

```bash
# Deploy to Vercel
vercel --prod

# GitHub Actions runs automatically
# Or trigger manually from Actions tab
```

### API Endpoints

Once the API is running, visit `http://localhost:8000/docs` for interactive documentation.

#### Available Endpoints:

- **GET /health** - Health check endpoint
  ```bash
  curl http://localhost:8000/health
  ```

- **GET /cds/** - Get CDS data with optional filtering
  ```bash
  # Get all data
  curl http://localhost:8000/cds/
  
  # Filter by date range
  curl "http://localhost:8000/cds/?start_date=2025-01-01&end_date=2025-11-07"
  
  # Limit results
  curl "http://localhost:8000/cds/?limit=100"
  ```

- **GET /cds/latest** - Get the latest N records
  ```bash
  curl "http://localhost:8000/cds/latest?n=10"
  ```

- **GET /cds/stats** - Get dataset statistics
  ```bash
  curl http://localhost:8000/cds/stats
  ```

## Development

### Install development dependencies:

```bash
pip install -e ".[dev]"
```

### Run tests:

```bash
pytest
```

### Code formatting:

```bash
black src/ scripts/ tests/
isort src/ scripts/ tests/
```

### Type checking:

```bash
mypy src/
```

## Architecture

### Modular Design

The project follows best practices with clear separation of concerns:

- **Config Layer**: Centralized configuration management
- **Storage Layer**: CSV operations with backup and deduplication
- **Scraper Layer**: Web scraping with retry logic and multiple parsing strategies
- **API Layer**: RESTful API with FastAPI and Pydantic validation
- **Utils Layer**: Shared utilities like logging

### Key Design Patterns

- **Singleton Settings**: Single source of truth for configuration
- **Repository Pattern**: CDSStorage abstracts data access
- **Dependency Injection**: Loose coupling between components
- **Error Handling**: Comprehensive exception handling and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is for educational and personal use.

## Troubleshooting

### Import Errors

If you encounter import errors, ensure the project root is in your Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Data Not Found

If the API returns 404, ensure the data file exists:

```bash
python scripts/update_cds.py
```

### Connection Issues

If scraping fails, check:
- Internet connectivity
- Investing.com website availability
- Request headers and timeout settings in `.env`

## Support

For issues or questions, please open an issue in the repository.
