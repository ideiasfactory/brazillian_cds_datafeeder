"""Pydantic models for API requests and responses."""
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class CDSRecord(BaseModel):
    """Single CDS record."""
    date: date = Field(..., description="Date of the record")
    open: Optional[float] = Field(None, description="Opening value")
    high: Optional[float] = Field(None, description="Highest value")
    low: Optional[float] = Field(None, description="Lowest value")
    close: Optional[float] = Field(None, description="Closing value")
    change_pct: Optional[float] = Field(None, description="Percentage change")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-11-07",
                "open": 0.0145,
                "high": 0.0148,
                "low": 0.0143,
                "close": 0.0146,
                "change_pct": 0.68
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0"
            }
        }


class CDSStatsResponse(BaseModel):
    """CDS data statistics response."""
    total_records: int = Field(..., description="Total number of records")
    oldest_date: Optional[str] = Field(None, description="Oldest date in dataset")
    latest_date: Optional[str] = Field(None, description="Latest date in dataset")
    latest_close: Optional[float] = Field(None, description="Latest closing value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_records": 1500,
                "oldest_date": "2020-01-01",
                "latest_date": "2025-11-07",
                "latest_close": 0.0146
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Data not found",
                "detail": "No CDS data available for the specified date range"
            }
        }
