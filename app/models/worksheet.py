from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .spreadsheet import Spreadsheet


class Worksheet(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str = Field(description="Name of the worksheet")
    end_row: int = Field(description="Last row with data")
    status: bool = Field(default=False, description="Only one can be in true state")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key to spreadsheet
    spreadsheet_id: str = Field(foreign_key="spreadsheet.id")

    # Relationship to spreadsheet
    spreadsheet: "Spreadsheet" = Relationship(back_populates="worksheets")
