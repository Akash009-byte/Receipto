from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Spreadsheet(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    spreadsheet_id: str = Field(unique=True, description="Google Spreadsheet ID")
    name: str = Field(description="Name of the spreadsheet")
    url: Optional[str] = Field(default=None, description="URL to the spreadsheet")
    status: bool = Field(default=False, description="Only one can be in true state at one time")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to worksheets
    worksheets: List["Worksheet"] = Relationship(back_populates="spreadsheet", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
