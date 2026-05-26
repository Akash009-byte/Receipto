from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from core.postgres import get_db
from models.worksheet import Worksheet
from fastapi import Depends

class WorksheetRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def create_worksheet(self, worksheet: Worksheet) -> Worksheet:
        """Create a new worksheet in the database."""
        self.session.add(worksheet)
        await self.session.commit()
        await self.session.refresh(worksheet)
        return worksheet

    async def get_worksheet(self, worksheet_id: str) -> Optional[Worksheet]:
        """Retrieve a worksheet by ID."""
        result = await self.session.execute(select(Worksheet).where(Worksheet.id == worksheet_id))
        return result.scalar_one_or_none()

    async def get_worksheet_by_name(self, spreadsheet_id: str, name: str) -> Optional[Worksheet]:
        """Retrieve a worksheet by name within a spreadsheet."""
        result = await self.session.execute(
            select(Worksheet).where(
                Worksheet.spreadsheet_id == spreadsheet_id,
                Worksheet.name == name
            )
        )
        return result.scalar_one_or_none()

    async def get_all_worksheets(self) -> List[Worksheet]:
        """Retrieve all worksheets."""
        result = await self.session.execute(select(Worksheet))
        return result.scalars().all()

    async def get_worksheets_by_spreadsheet(self, spreadsheet_id: str) -> List[Worksheet]:
        """Retrieve all worksheets for a specific spreadsheet."""
        result = await self.session.execute(select(Worksheet).where(Worksheet.spreadsheet_id == spreadsheet_id))
        return result.scalars().all()

    async def update_worksheet(self, worksheet: Worksheet) -> Worksheet:
        """Update an existing worksheet."""
        await self.session.commit()
        await self.session.refresh(worksheet)
        return worksheet

    async def delete_worksheet(self, worksheet_id: str) -> bool:
        """Delete a worksheet by ID."""
        worksheet = await self.get_worksheet(worksheet_id)
        if worksheet:
            await self.session.delete(worksheet)
            await self.session.commit()
            return True
        return False

    async def get_active_worksheet(self, spreadsheet_id: str) -> Optional[Worksheet]:
        """Get the currently active worksheet for a spreadsheet (status=True)."""
        result = await self.session.execute(
            select(Worksheet).where(
                Worksheet.spreadsheet_id == spreadsheet_id,
                Worksheet.status == True
            )
        )
        return result.scalar_one_or_none()

    async def set_active_worksheet(self, worksheet_id: str) -> bool:
        """Set a worksheet as active and deactivate others in the same spreadsheet."""
        worksheet = await self.get_worksheet(worksheet_id)
        if not worksheet:
            return False
        
        # First, deactivate all worksheets in the same spreadsheet
        spreadsheet_worksheets = await self.get_worksheets_by_spreadsheet(worksheet.spreadsheet_id)
        for ws in spreadsheet_worksheets:
            ws.status = False
        
        # Then activate the specified one
        worksheet.status = True
        await self.session.commit()
        return True 