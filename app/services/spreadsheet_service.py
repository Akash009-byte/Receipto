from models.spreadsheet import Spreadsheet
from sqlalchemy.ext.asyncio import AsyncSession
from repository.spreadsheet_repository import SpreadsheetRepository
from typing import List, Optional
from fastapi import Depends
from core.postgres import get_db 
import logging
import uuid

logger = logging.getLogger(__name__)

class SpreadsheetService:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.spreadsheetRepository = SpreadsheetRepository(session)

    async def create_spreadsheet(self, spreadsheet_id: str, name: str, url: Optional[str] = None) -> Spreadsheet:
        """Create a new spreadsheet record."""
        spreadsheet = Spreadsheet(
            id=str(uuid.uuid4()),
            spreadsheet_id=spreadsheet_id,
            name=name,
            url=url,
            status=False
        )
        created_spreadsheet = await self.spreadsheetRepository.create_spreadsheet(spreadsheet)
        logger.info(f"Created spreadsheet: {created_spreadsheet.name} with ID: {created_spreadsheet.id}")
        return created_spreadsheet

    async def get_spreadsheet(self, spreadsheet_id: str) -> Optional[Spreadsheet]:
        """Get a spreadsheet by ID."""
        return await self.spreadsheetRepository.get_spreadsheet(spreadsheet_id)

    async def get_spreadsheet_by_google_id(self, google_spreadsheet_id: str) -> Optional[Spreadsheet]:
        """Get a spreadsheet by Google Spreadsheet ID."""
        return await self.spreadsheetRepository.get_spreadsheet_by_google_id(google_spreadsheet_id)

    async def get_all_spreadsheets(self) -> List[Spreadsheet]:
        """Get all spreadsheets."""
        return await self.spreadsheetRepository.get_all_spreadsheets()

    async def update_spreadsheet(self, spreadsheet_id: str, name: Optional[str] = None, url: Optional[str] = None, status: Optional[bool] = None) -> Optional[Spreadsheet]:
        """Update a spreadsheet."""
        spreadsheet = await self.spreadsheetRepository.get_spreadsheet(spreadsheet_id)
        if not spreadsheet:
            return None
        
        if name is not None:
            spreadsheet.name = name
        if url is not None:
            spreadsheet.url = url
        if status is not None:
            if status:
                # If setting this to active, deactivate others first
                await self.spreadsheetRepository.set_active_spreadsheet(spreadsheet_id)
            else:
                spreadsheet.status = status
        
        updated_spreadsheet = await self.spreadsheetRepository.update_spreadsheet(spreadsheet)
        logger.info(f"Updated spreadsheet: {updated_spreadsheet.id}")
        return updated_spreadsheet

    async def delete_spreadsheet(self, spreadsheet_id: str) -> bool:
        """Delete a spreadsheet."""
        success = await self.spreadsheetRepository.delete_spreadsheet(spreadsheet_id)
        if success:
            logger.info(f"Deleted spreadsheet: {spreadsheet_id}")
        return success

    async def get_active_spreadsheet(self) -> Optional[Spreadsheet]:
        """Get the currently active spreadsheet."""
        return await self.spreadsheetRepository.get_active_spreadsheet()

    async def set_active_spreadsheet(self, spreadsheet_id: str) -> bool:
        """Set a spreadsheet as the active one."""
        success = await self.spreadsheetRepository.set_active_spreadsheet(spreadsheet_id)
        if success:
            logger.info(f"Set active spreadsheet: {spreadsheet_id}")
        return success 