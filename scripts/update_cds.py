#!/usr/bin/env python3
"""Script to update Brazilian CDS data from Investing.com."""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from src.scrapers import fetch_investing_cds
from src.storage import CDSStorage
from src.storage.postgres_storage import PostgresStorage
from src.utils import setup_logging, get_logger


async def update_with_postgres(new_data):
    """Update CDS data using PostgreSQL storage."""
    logger = get_logger()
    
    logger.info("Usando PostgreSQL para armazenamento...")
    storage = PostgresStorage()
    
    # Upsert new data
    count = await storage.upsert_data(new_data)
    logger.success(f"✓ {count} registros inseridos/atualizados no banco de dados")
    
    # Get statistics
    stats = await storage.get_stats()
    return stats


def update_with_csv(new_data):
    """Update CDS data using CSV storage."""
    logger = get_logger()
    
    logger.info("Usando CSV para armazenamento local...")
    storage = CDSStorage()
    storage.update_from_scraper(new_data)
    logger.success("✓ Dados atualizados no arquivo CSV")
    
    # Get statistics
    stats = storage.get_stats()
    return stats


async def async_main():
    """Main async function to update CDS data."""
    # Setup logging
    setup_logging()
    logger = get_logger()
    
    logger.info("=" * 60)
    logger.info("Iniciando atualização de dados CDS do Brasil")
    logger.info(f"Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"Armazenamento: {'PostgreSQL' if settings.use_postgres else 'CSV'}")
    logger.info("=" * 60)
    
    try:
        # Fetch new data
        logger.info("Buscando dados do Investing.com...")
        new_data = fetch_investing_cds()
        logger.success(f"✓ Dados capturados: {len(new_data)} registros")
        
        # Update storage based on environment
        if settings.use_postgres:
            if not settings.DATABASE_URL:
                logger.error("DATABASE_URL não configurado. Configure NEON_DATABASE_URL no .env")
                return 1
            stats = await update_with_postgres(new_data)
        else:
            stats = update_with_csv(new_data)
        
        # Show statistics
        logger.info("=" * 60)
        logger.success("Atualização concluída com sucesso!")
        logger.info(f"Total de registros: {stats['total_records']}")
        logger.info(f"Data mais antiga: {stats['oldest_date']}")
        logger.info(f"Data mais recente: {stats['latest_date']}")
        if stats.get('latest_close'):
            logger.info(f"Último valor: {stats['latest_close']:.4f}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Erro durante atualização: {e}")
        logger.exception("Detalhes do erro:")
        return 1


def main():
    """Synchronous entry point."""
    return asyncio.run(async_main())


if __name__ == "__main__":
    sys.exit(main())
