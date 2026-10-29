from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from core.postgres import get_db
from models.spreadsheet import Spreadsheet
from fastapi import Depends

class SpreadsheetRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def create_spreadsheet(self, spreadsheet: Spreadsheet) -> Spreadsheet:
        """Create a new spreadsheet in the database."""
        self.session.add(spreadsheet)
        await self.session.commit()
        await self.session.refresh(spreadsheet)
        return spreadsheet

    async def get_spreadsheet(self, spreadsheet_id: str) -> Optional[Spreadsheet]:
        """Retrieve a spreadsheet by ID."""
        result = await self.session.execute(select(Spreadsheet).where(Spreadsheet.id == spreadsheet_id))
        return result.scalar_one_or_none()

    async def get_spreadsheet_by_google_id(self, google_spreadsheet_id: str) -> Optional[Spreadsheet]:
        """Retrieve a spreadsheet by Google Spreadsheet ID."""
        result = await self.session.execute(select(Spreadsheet).where(Spreadsheet.spreadsheet_id == google_spreadsheet_id))
        return result.scalar_one_or_none()

    async def get_spreadsheet_by_name(self, name: str) -> Optional[Spreadsheet]:
        """Retrieve a spreadsheet by its name."""
        result = await self.session.execute(select(Spreadsheet).where(Spreadsheet.name == name))
        return result.scalar_one_or_none()

    async def get_all_spreadsheets(self) -> List[Spreadsheet]:
        """Retrieve all spreadsheets."""
        result = await self.session.execute(select(Spreadsheet))
        return result.scalars().all()

    async def update_spreadsheet(self, spreadsheet: Spreadsheet) -> Spreadsheet:
        """Update an existing spreadsheet."""
        await self.session.commit()
        await self.session.refresh(spreadsheet)
        return spreadsheet

    async def delete_spreadsheet(self, spreadsheet_id: str) -> bool:
        """Delete a spreadsheet by ID."""
        spreadsheet = await self.get_spreadsheet(spreadsheet_id)
        if spreadsheet:
            await self.session.delete(spreadsheet)
            await self.session.commit()
            return True
        return False

    async def get_active_spreadsheet(self) -> Optional[Spreadsheet]:
        """Get the currently active spreadsheet (status=True)."""
        result = await self.session.execute(select(Spreadsheet).where(Spreadsheet.status == True))
        return result.scalar_one_or_none()

    async def set_active_spreadsheet(self, spreadsheet_id: str) -> bool:
        """Set a spreadsheet as active and deactivate others."""
        # First, deactivate all spreadsheets
        all_spreadsheets = await self.get_all_spreadsheets()
        for sheet in all_spreadsheets:
            sheet.status = False

        # Then activate the specified one
        target_spreadsheet = await self.get_spreadsheet(spreadsheet_id)
        if target_spreadsheet:
            target_spreadsheet.status = True
            await self.session.commit()
            return True
        return False
