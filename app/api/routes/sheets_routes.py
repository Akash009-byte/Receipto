from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sheets_integration.sheets_service import SheetsService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/sheets')

# Global sheets service instance
sheets_service = SheetsService()

class SpreadsheetConnectionRequest(BaseModel):
    spreadsheet_id: str

class SpreadsheetNameRequest(BaseModel):
    spreadsheet_name: str

class CreateSpreadsheetRequest(BaseModel):
    title: str

class CreateWorksheetRequest(BaseModel):
    title: str
    rows: int = 1000
    cols: int = 20

class CreateWorksheetInSpreadsheetRequest(BaseModel):
    spreadsheet_name: str
    worksheet_name: str
    rows: int = 1000
    cols: int = 20

class DeleteWorksheetRequest(BaseModel):
    worksheet_name: str

class WriteReceiptDataRequest(BaseModel):
    spreadsheet_name: str
    worksheet_name: str
    row: int
    data: dict

class WorksheetDataRequest(BaseModel):
    worksheet_name: str
    range_notation: str = None  # Optional: e.g., "A1:C10"

@router.get("/status")
async def get_sheets_status():
    """Get the current Google Sheets connection status."""
    try:
        result = await sheets_service.get_connection_status()
        return result
    except Exception as e:
        logger.error(f"Error getting sheets status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sheets status")

@router.post("/connect")
async def connect_to_spreadsheet(request: SpreadsheetConnectionRequest):
    """Connect to a Google Spreadsheet by ID."""
    try:
        result = await sheets_service.connect_to_spreadsheet(request.spreadsheet_id)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting to spreadsheet: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to spreadsheet")

@router.post("/connect-by-name")
async def connect_to_spreadsheet_by_name(request: SpreadsheetNameRequest):
    """Connect to a Google Spreadsheet by name."""
    try:
        result = await sheets_service.connect_to_spreadsheet_by_name(request.spreadsheet_name)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting to spreadsheet by name: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to spreadsheet")

@router.post("/create")
async def create_new_spreadsheet(request: CreateSpreadsheetRequest):
    """Create a new Google Spreadsheet."""
    try:
        result = await sheets_service.create_new_spreadsheet(request.title)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating new spreadsheet: {e}")
        raise HTTPException(status_code=500, detail="Failed to create spreadsheet")

@router.get("/info")
async def get_spreadsheet_info():
    """Get information about the current connected spreadsheet."""
    try:
        result = await sheets_service.get_spreadsheet_info()

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting spreadsheet info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get spreadsheet info")

@router.get("/worksheets")
async def list_worksheets():
    """List all worksheets in the current spreadsheet."""
    try:
        result = await sheets_service.list_worksheets()

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing worksheets: {e}")
        raise HTTPException(status_code=500, detail="Failed to list worksheets")

@router.post("/worksheets")
async def create_worksheet(request: CreateWorksheetRequest):
    """Create a new worksheet in the current spreadsheet."""
    try:
        result = await sheets_service.create_worksheet(
            request.title,
            request.rows,
            request.cols
        )

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating worksheet: {e}")
        raise HTTPException(status_code=500, detail="Failed to create worksheet")

@router.post("/worksheets/create-in-spreadsheet")
async def create_worksheet_in_spreadsheet(request: CreateWorksheetInSpreadsheetRequest):
    """Create a new worksheet within a specific spreadsheet by name."""
    try:
        result = await sheets_service.create_worksheet_in_spreadsheet(
            request.spreadsheet_name,
            request.worksheet_name,
            request.rows,
            request.cols
        )

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating worksheet in spreadsheet: {e}")
        raise HTTPException(status_code=500, detail="Failed to create worksheet in spreadsheet")

@router.delete("/worksheets")
async def delete_worksheet(request: DeleteWorksheetRequest):
    """Delete a worksheet from the current spreadsheet."""
    try:
        result = await sheets_service.delete_worksheet(request.worksheet_name)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting worksheet: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete worksheet")

@router.post("/worksheets/data")
async def get_worksheet_data(request: WorksheetDataRequest):
    """Get data from a specific worksheet."""
    try:
        result = await sheets_service.get_worksheet_data(
            request.worksheet_name,
            request.range_notation
        )

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting worksheet data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get worksheet data")

@router.post("/worksheets/write-receipt")
async def write_receipt_data(request: WriteReceiptDataRequest):
    """Write receipt data to a specific worksheet."""
    try:
        result = await sheets_service.write_receipt_to_sheet(
            request.spreadsheet_name,
            request.worksheet_name,
            request.row,
            request.data
        )

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error writing receipt data: {e}")
        raise HTTPException(status_code=500, detail="Failed to write receipt data")
