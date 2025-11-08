"""Configuration settings for the Brazilian CDS application."""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)


class Settings:
    """Application settings loaded from environment variables."""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    IS_PRODUCTION: bool = os.getenv("ENVIRONMENT", "development") == "production"
    
    # BetterStack (Logtail) Configuration
    BETTERSTACK_SOURCE_TOKEN: Optional[str] = os.getenv("BETTERSTACK_SOURCE_TOKEN")
    BETTERSTACK_INGESTING_HOST: str = os.getenv("BETTERSTACK_INGESTING_HOST", "in.logtail.com")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Data Source Configuration
    INVESTING_URL: str = os.getenv(
        "INVESTING_URL",
        "https://br.investing.com/rates-bonds/brazil-cds-5-years-usd-historical-data"
    )
    
    # CSV path - different for dev/prod
    _csv_filename = os.getenv("CSV_OUTPUT_PATH", "brasil_CDS_historical.csv")
    CSV_OUTPUT_PATH: Path = (
        DATA_DIR / _csv_filename
        if os.getenv("ENVIRONMENT", "development") == "development"
        else Path("/tmp") / _csv_filename  # Vercel uses /tmp for writable storage
    )
    
    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv("NEON_DATABASE_URL")
    
    # For local development, you can also use a local PostgreSQL instance
    # Example: DATABASE_URL=postgresql://user:password@localhost:5432/brazilian_cds
    
    @property
    def csv_data_path(self) -> Path:
        """Get the CSV data path for reading/writing."""
        return self.CSV_OUTPUT_PATH
    
    @property
    def use_postgres(self) -> bool:
        """Determine if Postgres should be used based on environment and configuration."""
        # Use Postgres in production or if DATABASE_URL is explicitly set
        return self.IS_PRODUCTION or (self.DATABASE_URL is not None)
    
    TABLE_XPATH: str = os.getenv(
        "TABLE_XPATH",
        "/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/div[3]/table"
    )
    
    # HTTP Request Configuration
    USER_AGENT: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    )
    ACCEPT_LANGUAGE: str = os.getenv("ACCEPT_LANGUAGE", "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7")
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "20"))
    REQUEST_RETRIES: int = int(os.getenv("REQUEST_RETRIES", "3"))
    REQUEST_BACKOFF_FACTOR: float = float(os.getenv("REQUEST_BACKOFF_FACTOR", "0.8"))
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "false").lower() == "true"
    API_TITLE: str = "Brazilian CDS Data API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for accessing Brazilian CDS (Credit Default Swap) historical data"
    
    @property
    def request_headers(self) -> dict:
        """Generate HTTP request headers."""
        return {
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": self.ACCEPT_LANGUAGE,
            "Referer": "https://br.investing.com/",
        }


# Create a singleton instance
settings = Settings()
