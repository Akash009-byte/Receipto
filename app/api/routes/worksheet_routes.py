from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, Depends
from services.worksheet_service import WorksheetService
from models.worksheet import Worksheet
from typing import List, Optional
from core.postgres import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/api/worksheets'
)

# Request/Response models
class CreateWorksheetRequest(BaseModel):
    name: str
    spreadsheet_id: str
    end_row: int = 0
    sync_google: bool = True

class UpdateWorksheetRequest(BaseModel):
    name: Optional[str] = None
    end_row: Optional[int] = None
    status: Optional[bool] = None

# Dependency to provide a WorksheetService instance with session injection
def get_worksheet_service(db: AsyncSession = Depends(get_db)) -> WorksheetService:
    return WorksheetService(session=db)

@router.post("", response_model=Worksheet)
async def create_worksheet(
    request: CreateWorksheetRequest,
    worksheet_service: WorksheetService = Depends(get_worksheet_service)
):
    """Create a new worksheet record."""
    try:
        return await worksheet_service.create_worksheet(
            name=request.name,
            spreadsheet_id=request.spreadsheet_id,
            end_row=request.end_row,
            sync_google=request.sync_google
        )
    except HTTPException:
        raise
    except IntegrityError:
        raise
    except Exception as e:
        logger.error(f"Error creating worksheet: {e}")
        raise HTTPException(status_code=500, detail="Failed to create worksheet")

@router.get("/{worksheet_id}", response_model=Worksheet)
async def get_worksheet(
    worksheet_id: str,
    worksheet_service: WorksheetService = Depends(get_worksheet_service)
):
    """Get a worksheet by ID."""
    worksheet = await worksheet_service.get_worksheet(worksheet_id)
    if not worksheet:
        raise HTTPException(status_code=404, detail="Worksheet not found")
    return worksheet

@router.get("", response_model=List[Worksheet])
async def get_all_worksheets(
    worksheet_service: WorksheetService = Depends(get_worksheet_service)
):
    """Get all worksheets."""
    return await worksheet_service.get_all_worksheets()

@router.get("/spreadsheet/{spreadsheet_id}", response_model=List[Worksheet])
async def get_worksheets_by_spreadsheet(
    spreadsheet_id: str,
    worksheet_service: WorksheetService = Depends(get_worksheet_service)
):
    """Get all worksheets for a specific spreadsheet."""
    return await worksheet_service.get_worksheets_by_spreadsheet(spreadsheet_id)

@router.put("/{worksheet_id}", response_model=Worksheet)
async def update_worksheet(
    worksheet_id: str,
    request: UpdateWorksheetRequest,
    worksheet_service: WorksheetService = Depends(get_worksheet_service)
):
    """Update a worksheet."""
    updated_worksheet = await worksheet_service.update_worksheet(
        worksheet_id=worksheet_id,
        name=request.name,
        end_row=request.end_row,
        status=request.status
    )
    if not updated_worksheet:
        raise HTTPException(status_code=404, detail="Worksheet not found")
    return updated_worksheet

@router.delete("/{worksheet_id}")
async def delete_worksheet(
    worksheet_id: str,
    worksheet_service: WorksheetService = Depends(get_worksheet_service)
):
    """Delete a worksheet."""
    success = await worksheet_service.delete_worksheet(worksheet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Worksheet not found")
    return {"message": "Worksheet deleted successfully"}

@router.get("/spreadsheet/{spreadsheet_id}/active", response_model=Worksheet)
async def get_active_worksheet(
    spreadsheet_id: str,
    worksheet_service: WorksheetService = Depends(get_worksheet_service)
):
    """Get the currently active worksheet for a spreadsheet."""
    worksheet = await worksheet_service.get_active_worksheet(spreadsheet_id)
    if not worksheet:
        raise HTTPException(status_code=404, detail="No active worksheet found for this spreadsheet")
    return worksheet

@router.post("/{worksheet_id}/activate")
async def set_active_worksheet(
    worksheet_id: str,
    worksheet_service: WorksheetService = Depends(get_worksheet_service)
):
    """Set a worksheet as the active one in its spreadsheet."""
    success = await worksheet_service.set_active_worksheet(worksheet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Worksheet not found")
    return {"message": f"Worksheet {worksheet_id} set as active"}
