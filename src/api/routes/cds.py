"""API routes for CDS data."""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from config import settings
from src.api.models import CDSRecord, CDSStatsResponse, ErrorResponse
from src.storage import CDSStorage
from src.storage.postgres_storage import PostgresStorage

router = APIRouter(prefix="/cds", tags=["CDS Data"])


def get_storage():
    """Get the appropriate storage based on environment configuration."""
    if settings.use_postgres:
        return PostgresStorage()
    return CDSStorage()


@router.get(
    "/",
    response_model=List[CDSRecord],
    responses={
        404: {"model": ErrorResponse, "description": "No data found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get CDS data",
    description="Retrieve Brazilian CDS historical data with optional date filtering"
)
async def get_cds_data(
    start_date: Optional[str] = Query(
        None,
        description="Start date in YYYY-MM-DD format",
        example="2025-01-01"
    ),
    end_date: Optional[str] = Query(
        None,
        description="End date in YYYY-MM-DD format",
        example="2025-11-07"
    ),
    limit: Optional[int] = Query(
        None,
        description="Maximum number of records to return",
        ge=1,
        le=10000
    )
) -> List[CDSRecord]:
    """Get CDS data with optional filtering."""
    try:
        storage = get_storage()
        
        if isinstance(storage, PostgresStorage):
            df = await storage.get_data(start_date=start_date, end_date=end_date, limit=limit)
        else:
            df = storage.get_data(start_date=start_date, end_date=end_date)
            if limit:
                df = df.tail(limit)
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail="No CDS data found for the specified criteria"
            )
        
        # Convert to list of dicts
        records = df.to_dict(orient="records")
        
        # Convert to Pydantic models
        return [CDSRecord(**record) for record in records]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving CDS data: {str(e)}"
        )


@router.get(
    "/latest",
    response_model=List[CDSRecord],
    responses={
        404: {"model": ErrorResponse, "description": "No data found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get latest CDS records",
    description="Retrieve the most recent N CDS records"
)
async def get_latest_cds_data(
    n: int = Query(
        10,
        description="Number of latest records to return",
        ge=1,
        le=1000
    )
) -> List[CDSRecord]:
    """Get the latest N CDS records."""
    try:
        storage = get_storage()
        
        if isinstance(storage, PostgresStorage):
            df = await storage.get_data(limit=n)
        else:
            df = storage.get_latest(n=n)
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail="No CDS data available"
            )
        
        # Convert to list of dicts
        records = df.to_dict(orient="records")
        
        # Convert to Pydantic models
        return [CDSRecord(**record) for record in records]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving latest CDS data: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=CDSStatsResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get CDS data statistics",
    description="Retrieve statistics about the stored CDS data"
)
async def get_cds_stats() -> CDSStatsResponse:
    """Get statistics about the CDS data."""
    try:
        storage = get_storage()
        
        if isinstance(storage, PostgresStorage):
            stats = await storage.get_stats()
        else:
            stats = storage.get_stats()
        
        return CDSStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving CDS statistics: {str(e)}"
        )
