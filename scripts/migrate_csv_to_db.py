"""
Migration script to transfer data from CSV to PostgreSQL database.

This script reads existing CSV data and migrates it to the Neon Postgres database.
It includes validation and integrity checks to ensure data quality.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from loguru import logger

from config.settings import settings
from src.database.connection import get_db_session, create_tables
from src.storage.postgres_storage import PostgresStorage


def validate_csv_data(df: pd.DataFrame) -> bool:
    """
    Validate CSV data before migration.
    
    Args:
        df: DataFrame containing CSV data
        
    Returns:
        True if data is valid, False otherwise
    """
    logger.info("Validating CSV data...")
    
    # Check required columns
    required_columns = ["date", "open", "high", "low", "close", "change_pct"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        return False
    
    # Check for null values in critical columns
    null_counts = df[required_columns].isnull().sum()
    if null_counts.any():
        logger.warning(f"Found null values:\n{null_counts[null_counts > 0]}")
    
    # Check data types
    try:
        df["date"] = pd.to_datetime(df["date"])
        for col in ["open", "high", "low", "close", "change_pct"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    except Exception as e:
        logger.error(f"Data type conversion failed: {e}")
        return False
    
    # Check for duplicate dates
    duplicates = df[df["date"].duplicated()]
    if not duplicates.empty:
        logger.warning(f"Found {len(duplicates)} duplicate dates")
        logger.info("Will keep the latest record for each date")
    
    logger.success(f"CSV validation passed. Total records: {len(df)}")
    return True


async def migrate_data():
    """
    Main migration function.
    
    Reads CSV data and migrates it to PostgreSQL database with validation.
    """
    try:
        # Check if DATABASE_URL is configured
        if not settings.DATABASE_URL:
            logger.error("DATABASE_URL not configured. Please set NEON_DATABASE_URL in .env file")
            logger.info("Example: NEON_DATABASE_URL=postgresql://user:password@host/database")
            return False
        
        logger.info("Starting CSV to PostgreSQL migration...")
        logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
        
        # Check if CSV file exists
        csv_path = Path(settings.CSV_DATA_PATH)
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            logger.info("Please run the data update script first to generate CSV data")
            return False
        
        # Read CSV data
        logger.info(f"Reading CSV data from: {csv_path}")
        df = pd.read_csv(csv_path)
        
        if df.empty:
            logger.warning("CSV file is empty. Nothing to migrate.")
            return True
        
        logger.info(f"Loaded {len(df)} records from CSV")
        
        # Validate data
        if not validate_csv_data(df):
            logger.error("Data validation failed. Migration aborted.")
            return False
        
        # Create database tables if they don't exist
        logger.info("Ensuring database tables exist...")
        await create_tables()
        
        # Initialize storage
        storage = PostgresStorage()
        
        # Check if database already has data
        existing_data = await storage.load_existing_data()
        
        if not existing_data.empty:
            logger.warning(f"Database already contains {len(existing_data)} records")
            response = await asyncio.to_thread(
                input, "Do you want to proceed? This will update existing records (y/n): "
            )
            if response.lower() != 'y':
                logger.info("Migration cancelled by user")
                return False
        
        # Migrate data
        logger.info("Migrating data to PostgreSQL...")
        count = await storage.upsert_data(df)
        
        if count > 0:
            logger.success(f"Successfully migrated {count} records to PostgreSQL")
            
            # Verify migration
            logger.info("Verifying migration...")
            migrated_data = await storage.load_existing_data()
            logger.success(f"Verification complete. Database contains {len(migrated_data)} records")
            
            # Show latest record
            latest = await storage.get_latest()
            if latest:
                logger.info(f"Latest record: {latest['date']} - Close: {latest['close']}")
            
            return True
        else:
            logger.error("Migration failed")
            return False
                
    except Exception as e:
        logger.error(f"Migration error: {e}")
        logger.exception("Full traceback:")
        return False


async def verify_migration():
    """
    Verify that CSV and database data match.
    """
    try:
        logger.info("Verifying data consistency...")
        
        # Read CSV
        csv_path = Path(settings.CSV_DATA_PATH)
        if not csv_path.exists():
            logger.warning("CSV file not found for verification")
            return
        
        csv_df = pd.read_csv(csv_path)
        csv_df["date"] = pd.to_datetime(csv_df["date"])
        
        # Read from database
        storage = PostgresStorage()
        db_df = await storage.load_existing_data()
        
        # Compare counts
        logger.info(f"CSV records: {len(csv_df)}")
        logger.info(f"Database records: {len(db_df)}")
        
        if len(csv_df) == len(db_df):
            logger.success("Record counts match ✓")
        else:
            logger.warning(f"Record count mismatch: CSV={len(csv_df)}, DB={len(db_df)}")
        
        # Compare date ranges
        csv_dates = sorted(csv_df["date"].unique())
        db_dates = sorted(db_df["date"].unique())
        
        logger.info(f"CSV date range: {csv_dates[0]} to {csv_dates[-1]}")
        logger.info(f"DB date range: {db_dates[0]} to {db_dates[-1]}")
        
        # Check for missing dates
        missing_in_db = set(csv_dates) - set(db_dates)
        missing_in_csv = set(db_dates) - set(csv_dates)
        
        if missing_in_db:
            logger.warning(f"Dates in CSV but not in DB: {len(missing_in_db)}")
        if missing_in_csv:
            logger.warning(f"Dates in DB but not in CSV: {len(missing_in_csv)}")
        
        if not missing_in_db and not missing_in_csv:
            logger.success("All dates present in both sources ✓")
        
    except Exception as e:
        logger.error(f"Verification error: {e}")


def main():
    """
    CLI entry point for migration script.
    """
    logger.info("=" * 60)
    logger.info("Brazilian CDS Data Migration Tool")
    logger.info("CSV → PostgreSQL (Neon)")
    logger.info("=" * 60)
    
    # Run migration
    success = asyncio.run(migrate_data())
    
    if success:
        # Run verification
        asyncio.run(verify_migration())
        
        logger.info("=" * 60)
        logger.success("Migration completed successfully!")
        logger.info("=" * 60)
        return 0
    else:
        logger.info("=" * 60)
        logger.error("Migration failed!")
        logger.info("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
