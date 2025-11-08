"""SQLAlchemy database models for Brazilian CDS data."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Date, DateTime, Index, Numeric, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CDSData(Base):
    """CDS (Credit Default Swap) historical data model."""
    
    __tablename__ = "cds_data"
    
    # Primary key
    date = Column(Date, primary_key=True, nullable=False)
    
    # OHLC data
    open = Column(Numeric(10, 4), nullable=True)
    high = Column(Numeric(10, 4), nullable=True)
    low = Column(Numeric(10, 4), nullable=True)
    close = Column(Numeric(10, 4), nullable=False)
    
    # Additional data
    change_pct = Column(Numeric(10, 4), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_cds_date_desc', date.desc()),
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<CDSData(date={self.date}, close={self.close})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "date": self.date.isoformat() if self.date else None,
            "open": float(self.open) if self.open is not None else None,
            "high": float(self.high) if self.high is not None else None,
            "low": float(self.low) if self.low is not None else None,
            "close": float(self.close) if self.close is not None else None,
            "change_pct": float(self.change_pct) if self.change_pct is not None else None,
        }
