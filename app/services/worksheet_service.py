from models.worksheet import Worksheet
from sqlalchemy.ext.asyncio import AsyncSession
from repository.worksheet_repository import WorksheetRepository
from repository.spreadsheet_repository import SpreadsheetRepository
from typing import List, Optional
from fastapi import Depends, HTTPException
import os
from core.postgres import get_db
import logging
import uuid
from sheets_integration.sheets_service import SheetsService

logger = logging.getLogger(__name__)

class WorksheetService:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.worksheetRepository = WorksheetRepository(session)
        self.spreadsheetRepository = SpreadsheetRepository(session)
        self.sheetsService = SheetsService()

    async def create_worksheet(self, name: str, spreadsheet_id: str, end_row: int = 0, sync_google: bool = True) -> Worksheet:
        """Create a new worksheet record and also create it in Google Sheets.
        - spreadsheet_id: local DB spreadsheet.id (not Google ID)
        - name: worksheet name to create both locally and in Google Sheets
        """
        # 1) Fetch the spreadsheet to get its name (connect by name)
        spreadsheet = await self.spreadsheetRepository.get_spreadsheet(spreadsheet_id)
        if not spreadsheet:
            raise HTTPException(status_code=404, detail="Spreadsheet not found")

        if sync_google:
            if not (os.getenv("GOOGLE_SHEETS_CREDENTIALS") or os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")):
                raise HTTPException(status_code=503, detail="Google Sheets is not configured. Set credentials or use sync_google=false for a local-only record.")
            # 2) Connect to Google spreadsheet by NAME and create worksheet there first
            connect_result = await self.sheetsService.connect_to_spreadsheet_by_name(spreadsheet.name)
            if connect_result.get("status") != "success":
                error_msg = connect_result.get("error", "Unknown error connecting to Google Sheets")
                raise RuntimeError(f"Failed to connect to Google Spreadsheet: {error_msg}")

            create_result = await self.sheetsService.create_worksheet(title=name, rows=1000, cols=20)
            if create_result.get("status") != "success":
                error_msg = create_result.get("error", "Unknown error creating worksheet in Google Sheets")
                raise RuntimeError(f"Failed to create worksheet in Google Sheets: {error_msg}")

        # 3) Create local DB record
        worksheet = Worksheet(
            id=str(uuid.uuid4()),
            name=name,
            end_row=end_row,
            status=False,
            spreadsheet_id=spreadsheet_id
        )
        created_worksheet = await self.worksheetRepository.create_worksheet(worksheet)
        logger.info(f"Created worksheet record: {created_worksheet.name} with ID: {created_worksheet.id}")
        return created_worksheet

    async def get_worksheet(self, worksheet_id: str) -> Optional[Worksheet]:
        """Get a worksheet by ID."""
        return await self.worksheetRepository.get_worksheet(worksheet_id)

    async def get_all_worksheets(self) -> List[Worksheet]:
        """Get all worksheets."""
        return await self.worksheetRepository.get_all_worksheets()

    async def get_worksheets_by_spreadsheet(self, spreadsheet_id: str) -> List[Worksheet]:
        """Get all worksheets for a specific spreadsheet."""
        return await self.worksheetRepository.get_worksheets_by_spreadsheet(spreadsheet_id)

    async def update_worksheet(self, worksheet_id: str, name: Optional[str] = None, end_row: Optional[int] = None, status: Optional[bool] = None) -> Optional[Worksheet]:
        """Update a worksheet."""
        worksheet = await self.worksheetRepository.get_worksheet(worksheet_id)
        if not worksheet:
            return None

        if name is not None:
            worksheet.name = name
        if end_row is not None:
            worksheet.end_row = end_row
        if status is not None:
            if status:
                # If setting this to active, deactivate others in the same spreadsheet first
                await self.worksheetRepository.set_active_worksheet(worksheet_id)
            else:
                worksheet.status = status

        updated_worksheet = await self.worksheetRepository.update_worksheet(worksheet)
        logger.info(f"Updated worksheet: {updated_worksheet.id}")
        return updated_worksheet

    async def delete_worksheet(self, worksheet_id: str) -> bool:
        """Delete a worksheet."""
        success = await self.worksheetRepository.delete_worksheet(worksheet_id)
        if success:
            logger.info(f"Deleted worksheet: {worksheet_id}")
        return success

    async def get_active_worksheet(self, spreadsheet_id: str) -> Optional[Worksheet]:
        """Get the currently active worksheet for a spreadsheet."""
        return await self.worksheetRepository.get_active_worksheet(spreadsheet_id)

    async def set_active_worksheet(self, worksheet_id: str) -> bool:
        """Set a worksheet as the active one in its spreadsheet."""
        success = await self.worksheetRepository.set_active_worksheet(worksheet_id)
        if success:
            logger.info(f"Set active worksheet: {worksheet_id}")
        return success
