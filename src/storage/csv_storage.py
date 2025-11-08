"""CSV storage module for Brazilian CDS data."""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from config import settings
from src.utils import get_logger

logger = get_logger()


class CDSStorage:
    """Handle CSV storage operations for CDS data."""
    
    def __init__(self, csv_path: Optional[Path] = None):
        """Initialize storage handler.
        
        Args:
            csv_path: Path to CSV file. Uses settings default if not provided.
        """
        self.csv_path = csv_path or settings.CSV_OUTPUT_PATH
        
    def load_existing_data(self) -> pd.DataFrame:
        """Load existing CSV data if available.
        
        Returns:
            DataFrame with existing data or empty DataFrame with correct columns
        """
        if not os.path.exists(self.csv_path):
            logger.warning(f"CSV inexistente em {self.csv_path}; iniciando base vazia.")
            return pd.DataFrame(columns=["date", "open", "high", "low", "close", "change_pct"])
        
        df = pd.read_csv(self.csv_path)
        # normaliza
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        
        logger.info(f"Carregados {len(df)} registros de {self.csv_path}")
        return df
    
    def merge_and_dedup(self, old: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
        """Merge old and new data, removing duplicates.
        
        Args:
            old: Existing DataFrame
            new: New DataFrame to merge
            
        Returns:
            Merged DataFrame without duplicates, sorted by date
        """
        if old is None or old.empty:
            merged = new.copy()
        else:
            merged = pd.concat([old, new], ignore_index=True)
        
        # remove duplicatas por data (mantém a última ocorrência)
        merged = merged.drop_duplicates(subset=["date"], keep="last")
        merged = merged.sort_values("date").reset_index(drop=True)
        
        logger.info(f"Após merge e dedup: {len(merged)} registros totais")
        return merged
    
    def create_backup(self) -> Optional[str]:
        """Create a timestamped backup of the current CSV file.
        
        Returns:
            Path to backup file, or None if backup failed
        """
        if not os.path.exists(self.csv_path):
            return None
            
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.csv_path.parent / f"{self.csv_path.stem}__bkp_{ts}.csv"
        
        try:
            shutil.copy2(self.csv_path, backup_path)
            logger.info(f"Backup criado: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.warning(f"Falha ao criar backup: {e}")
            return None
    
    def save_data(self, df: pd.DataFrame, create_backup: bool = True) -> None:
        """Save DataFrame to CSV.
        
        Args:
            df: DataFrame to save
            create_backup: Whether to create a backup before saving
        """
        # Garante colunas na ordem
        cols = ["date", "open", "high", "low", "close", "change_pct"]
        for c in cols:
            if c not in df.columns:
                df[c] = pd.NA
        df = df[cols]
        
        # Cria backup se solicitado
        if create_backup:
            self.create_backup()
        
        # Salva
        df.to_csv(self.csv_path, index=False, date_format="%Y-%m-%d")
        logger.success(f"Dados salvos: {self.csv_path} ({len(df)} linhas)")
    
    def update_from_scraper(self, new_data: pd.DataFrame) -> pd.DataFrame:
        """Complete update workflow: load, merge, save.
        
        Args:
            new_data: New data from scraper
            
        Returns:
            Merged DataFrame that was saved
        """
        old_data = self.load_existing_data()
        merged = self.merge_and_dedup(old_data, new_data)
        self.save_data(merged, create_backup=True)
        return merged
    
    def get_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Get CDS data with optional date filtering.
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            
        Returns:
            Filtered DataFrame
        """
        df = self.load_existing_data()
        
        if start_date:
            start = pd.to_datetime(start_date)
            df = df[df["date"] >= start]
        
        if end_date:
            end = pd.to_datetime(end_date)
            df = df[df["date"] <= end]
        
        return df
    
    def get_latest(self, n: int = 10) -> pd.DataFrame:
        """Get the latest N records.
        
        Args:
            n: Number of records to return
            
        Returns:
            DataFrame with latest n records
        """
        df = self.load_existing_data()
        return df.tail(n)
    
    def get_stats(self) -> dict:
        """Get basic statistics about the stored data.
        
        Returns:
            Dictionary with stats (count, date_range, etc.)
        """
        df = self.load_existing_data()
        
        if df.empty:
            return {
                "total_records": 0,
                "date_range": None,
                "latest_date": None,
                "oldest_date": None,
            }
        
        return {
            "total_records": len(df),
            "date_range": {
                "start": df["date"].min().strftime("%Y-%m-%d"),
                "end": df["date"].max().strftime("%Y-%m-%d"),
            },
            "latest_date": df["date"].max().strftime("%Y-%m-%d"),
            "oldest_date": df["date"].min().strftime("%Y-%m-%d"),
            "latest_close": float(df.iloc[-1]["close"]) if "close" in df.columns else None,
        }
