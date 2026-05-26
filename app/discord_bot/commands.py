import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.postgres import get_db
from services.spreadsheet_service import SpreadsheetService
from services.worksheet_service import WorksheetService

logger = logging.getLogger(__name__)

class DiscordCommandHandler:
    def __init__(self, db_session: AsyncSession):
        self.spreadsheet_service = SpreadsheetService(session=db_session)
        self.worksheet_service = WorksheetService(session=db_session)

    @staticmethod
    def parse_command(content: str) -> Optional[tuple[str, Optional[str]]]:
        """Parse plain text content into (command, argument)."""
        if not content:
            return None
        text = content.strip()
        if not text:
            return None
        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else None
        if cmd in {"ss", "ws"}:
            return (cmd, arg)
        return None

    async def handle_ss(self, arg: Optional[str]) -> str:
        """Handle spreadsheet commands.
        - ss -> return active spreadsheet name
        - ss <name> -> set active to <name> if exists (by name), otherwise keep current
        """
        if arg:
            # Try to connect spreadsheet by name and set active if found
            # We assume spreadsheet already exists in DB; we are not creating DB rows via Discord here
            spreadsheets = await self.spreadsheet_service.get_all_spreadsheets()
            match = next((s for s in spreadsheets if s.name.lower() == arg.lower()), None)
            if match:
                await self.spreadsheet_service.set_active_spreadsheet(match.id)
                return f"✅ Active spreadsheet set to: {match.name}"
            else:
                active = await self.spreadsheet_service.get_active_spreadsheet()
                if active:
                    return f"⚠️ Spreadsheet '{arg}' not found. Current active: {active.name}"
                return f"⚠️ Spreadsheet '{arg}' not found and no active spreadsheet set."
        else:
            active = await self.spreadsheet_service.get_active_spreadsheet()
            if active:
                return f"📄 Active spreadsheet: {active.name}"
            return "⚠️ No active spreadsheet set."

    async def handle_ws(self, arg: Optional[str]) -> str:
        """Handle worksheet commands.
        - ws -> return active worksheet for active spreadsheet
        - ws <name> -> if exists in active spreadsheet, set active; else create and set active
        """
        active_sheet = await self.spreadsheet_service.get_active_spreadsheet()
        if not active_sheet:
            return "⚠️ No active spreadsheet. Use 'ss <name>' to set one."
        if arg:
            # See if worksheet exists in this spreadsheet
            worksheets = await self.worksheet_service.get_worksheets_by_spreadsheet(active_sheet.id)
            match = next((w for w in worksheets if w.name.lower() == arg.lower()), None)
            if match:
                await self.worksheet_service.set_active_worksheet(match.id)
                return f"✅ Active worksheet set to: {match.name}"
            # Create then activate
            created = await self.worksheet_service.create_worksheet(name=arg, spreadsheet_id=active_sheet.id)
            await self.worksheet_service.set_active_worksheet(created.id)
            return f"✅ Created and set active worksheet: {created.name}"
        else:
            active_ws = await self.worksheet_service.get_active_worksheet(active_sheet.id)
            if active_ws:
                return f"📄 Active worksheet: {active_ws.name} (spreadsheet: {active_sheet.name})"
            return f"⚠️ No active worksheet for spreadsheet: {active_sheet.name}. Use 'ws <name>' to create or activate one."
