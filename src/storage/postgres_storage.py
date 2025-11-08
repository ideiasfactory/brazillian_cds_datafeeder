"""PostgreSQL storage module for Brazilian CDS data."""
from datetime import date, datetime
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import delete, desc, func, select
from sqlalchemy.dialects.postgresql import insert

from src.database import CDSData, get_db_session
from src.utils import get_logger

logger = get_logger()


class PostgresStorage:
    """Handle PostgreSQL storage operations for CDS data."""
    
    async def load_existing_data(self) -> pd.DataFrame:
        """Load all CDS data from database.
        
        Returns:
            DataFrame with all data sorted by date
        """
        async with get_db_session() as session:
            query = select(CDSData).order_by(CDSData.date)
            result = await session.execute(query)
            records = result.scalars().all()
            
            if not records:
                logger.warning("No data found in database")
                return pd.DataFrame(columns=["date", "open", "high", "low", "close", "change_pct"])
            
            data = [record.to_dict() for record in records]
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])
            
            logger.info(f"Loaded {len(df)} records from database")
            return df
    
    async def upsert_data(self, df: pd.DataFrame) -> int:
        """Insert or update CDS data in database.
        
        Uses PostgreSQL's ON CONFLICT to handle duplicates.
        
        Args:
            df: DataFrame with CDS data
            
        Returns:
            Number of records affected
        """
        if df.empty:
            logger.warning("No data to upsert")
            return 0
        
        # Convert DataFrame to list of dicts
        records = []
        for _, row in df.iterrows():
            record = {
                "date": row["date"].date() if isinstance(row["date"], pd.Timestamp) else row["date"],
                "open": float(row["open"]) if pd.notna(row.get("open")) else None,
                "high": float(row["high"]) if pd.notna(row.get("high")) else None,
                "low": float(row["low"]) if pd.notna(row.get("low")) else None,
                "close": float(row["close"]) if pd.notna(row["close"]) else None,
                "change_pct": float(row["change_pct"]) if pd.notna(row.get("change_pct")) else None,
            }
            records.append(record)
        
        async with get_db_session() as session:
            # Use PostgreSQL INSERT ... ON CONFLICT ... DO UPDATE
            stmt = insert(CDSData).values(records)
            stmt = stmt.on_conflict_do_update(
                index_elements=["date"],
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "change_pct": stmt.excluded.change_pct,
                    "updated_at": func.now(),
                }
            )
            
            await session.execute(stmt)
            await session.commit()
            
            logger.success(f"Upserted {len(records)} records to database")
            return len(records)
    
    async def get_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Get CDS data with optional filtering.
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            limit: Maximum number of records to return
            
        Returns:
            Filtered DataFrame
        """
        async with get_db_session() as session:
            query = select(CDSData).order_by(CDSData.date)
            
            # Apply filters
            if start_date:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.where(CDSData.date >= start)
            
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.where(CDSData.date <= end)
            
            if limit:
                # For limit, we want the most recent records
                query = select(CDSData).order_by(desc(CDSData.date)).limit(limit)
            
            result = await session.execute(query)
            records = result.scalars().all()
            
            if not records:
                return pd.DataFrame(columns=["date", "open", "high", "low", "close", "change_pct"])
            
            data = [record.to_dict() for record in records]
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])
            
            # Sort by date ascending
            df = df.sort_values("date").reset_index(drop=True)
            
            return df
    
    async def get_latest(self, n: int = 10) -> pd.DataFrame:
        """Get the latest N records.
        
        Args:
            n: Number of records to return
            
        Returns:
            DataFrame with latest n records
        """
        async with get_db_session() as session:
            query = select(CDSData).order_by(desc(CDSData.date)).limit(n)
            result = await session.execute(query)
            records = result.scalars().all()
            
            if not records:
                return pd.DataFrame(columns=["date", "open", "high", "low", "close", "change_pct"])
            
            data = [record.to_dict() for record in records]
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])
            
            # Sort by date ascending (oldest first)
            df = df.sort_values("date").reset_index(drop=True)
            
            return df
    
    async def get_stats(self) -> Dict:
        """Get basic statistics about the stored data.
        
        Returns:
            Dictionary with stats
        """
        async with get_db_session() as session:
            # Count total records
            count_query = select(func.count()).select_from(CDSData)
            count_result = await session.execute(count_query)
            total = count_result.scalar()
            
            if total == 0:
                return {
                    "total_records": 0,
                    "oldest_date": None,
                    "latest_date": None,
                    "latest_close": None,
                }
            
            # Get date range
            min_date_query = select(func.min(CDSData.date))
            min_result = await session.execute(min_date_query)
            oldest_date = min_result.scalar()
            
            max_date_query = select(func.max(CDSData.date))
            max_result = await session.execute(max_date_query)
            latest_date = max_result.scalar()
            
            # Get latest close value
            latest_query = select(CDSData).order_by(desc(CDSData.date)).limit(1)
            latest_result = await session.execute(latest_query)
            latest_record = latest_result.scalar_one_or_none()
            
            return {
                "total_records": total,
                "oldest_date": oldest_date.isoformat() if oldest_date else None,
                "latest_date": latest_date.isoformat() if latest_date else None,
                "latest_close": float(latest_record.close) if latest_record and latest_record.close else None,
            }
    
    async def delete_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> int:
        """Delete CDS data within date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            
        Returns:
            Number of records deleted
        """
        async with get_db_session() as session:
            query = delete(CDSData)
            
            if start_date:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.where(CDSData.date >= start)
            
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.where(CDSData.date <= end)
            
            result = await session.execute(query)
            await session.commit()
            
            deleted_count = result.rowcount
            logger.warning(f"Deleted {deleted_count} records from database")
            return deleted_count
