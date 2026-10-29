from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, Depends
from services.spreadsheet_service import SpreadsheetService
from models.spreadsheet import Spreadsheet
from typing import List, Optional
from core.postgres import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/api/spreadsheets'
)

# Request/Response models
class CreateSpreadsheetRequest(BaseModel):
    spreadsheet_id: str  # Google Spreadsheet ID
    name: str
    url: Optional[str] = None

class UpdateSpreadsheetRequest(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    status: Optional[bool] = None

# Dependency to provide a SpreadsheetService instance with session injection
def get_spreadsheet_service(db: AsyncSession = Depends(get_db)) -> SpreadsheetService:
    return SpreadsheetService(session=db)

@router.post("", response_model=Spreadsheet)
async def create_spreadsheet(
    request: CreateSpreadsheetRequest,
    spreadsheet_service: SpreadsheetService = Depends(get_spreadsheet_service)
):
    """Create a new spreadsheet record."""
    try:
        return await spreadsheet_service.create_spreadsheet(
            spreadsheet_id=request.spreadsheet_id,
            name=request.name,
            url=request.url
        )
    except IntegrityError:
        raise
    except Exception as e:
        logger.error(f"Error creating spreadsheet: {e}")
        raise HTTPException(status_code=500, detail="Failed to create spreadsheet")

@router.get("/{spreadsheet_id}", response_model=Spreadsheet)
async def get_spreadsheet(
    spreadsheet_id: str,
    spreadsheet_service: SpreadsheetService = Depends(get_spreadsheet_service)
):
    """Get a spreadsheet by ID."""
    spreadsheet = await spreadsheet_service.get_spreadsheet(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")
    return spreadsheet

@router.get("/google/{google_spreadsheet_id}", response_model=Spreadsheet)
async def get_spreadsheet_by_google_id(
    google_spreadsheet_id: str,
    spreadsheet_service: SpreadsheetService = Depends(get_spreadsheet_service)
):
    """Get a spreadsheet by Google Spreadsheet ID."""
    spreadsheet = await spreadsheet_service.get_spreadsheet_by_google_id(google_spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")
    return spreadsheet

@router.get("", response_model=List[Spreadsheet])
async def get_all_spreadsheets(
    spreadsheet_service: SpreadsheetService = Depends(get_spreadsheet_service)
):
    """Get all spreadsheets."""
    return await spreadsheet_service.get_all_spreadsheets()

@router.put("/{spreadsheet_id}", response_model=Spreadsheet)
async def update_spreadsheet(
    spreadsheet_id: str,
    request: UpdateSpreadsheetRequest,
    spreadsheet_service: SpreadsheetService = Depends(get_spreadsheet_service)
):
    """Update a spreadsheet."""
    updated_spreadsheet = await spreadsheet_service.update_spreadsheet(
        spreadsheet_id=spreadsheet_id,
        name=request.name,
        url=request.url,
        status=request.status
    )
    if not updated_spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")
    return updated_spreadsheet

@router.delete("/{spreadsheet_id}")
async def delete_spreadsheet(
    spreadsheet_id: str,
    spreadsheet_service: SpreadsheetService = Depends(get_spreadsheet_service)
):
    """Delete a spreadsheet."""
    success = await spreadsheet_service.delete_spreadsheet(spreadsheet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")
    return {"message": "Spreadsheet deleted successfully"}

@router.get("/active/current", response_model=Spreadsheet)
async def get_active_spreadsheet(
    spreadsheet_service: SpreadsheetService = Depends(get_spreadsheet_service)
):
    """Get the currently active spreadsheet."""
    spreadsheet = await spreadsheet_service.get_active_spreadsheet()
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="No active spreadsheet found")
    return spreadsheet

@router.post("/{spreadsheet_id}/activate")
async def set_active_spreadsheet(
    spreadsheet_id: str,
    spreadsheet_service: SpreadsheetService = Depends(get_spreadsheet_service)
):
    """Set a spreadsheet as the active one."""
    success = await spreadsheet_service.set_active_spreadsheet(spreadsheet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")
    return {"message": f"Spreadsheet {spreadsheet_id} set as active"}
