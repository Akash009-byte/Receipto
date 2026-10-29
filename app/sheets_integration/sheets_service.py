import logging
from typing import Dict, List, Optional, Any
from .google_sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)

class SheetsService:
    """Service layer for Google Sheets operations."""

    def __init__(self):
        self.sheets_client = GoogleSheetsClient()

    async def get_connection_status(self) -> Dict[str, Any]:
        """Get the current Google Sheets connection status."""
        try:
            status = self.sheets_client.get_connection_status()

            # Test connection if client is initialized
            if status["client_initialized"]:
                connection_test = self.sheets_client.test_connection()
                status["connection_test_passed"] = connection_test
            else:
                status["connection_test_passed"] = False

            return {
                "status": "success",
                "data": status
            }
        except Exception as e:
            logger.error(f"Error getting sheets connection status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def connect_to_spreadsheet(self, spreadsheet_id: str) -> Dict[str, Any]:
        """Connect to a specific Google Spreadsheet."""
        try:
            success = self.sheets_client.connect_to_spreadsheet(spreadsheet_id)

            if success:
                spreadsheet_info = self.sheets_client.get_spreadsheet_info()
                return {
                    "status": "success",
                    "message": f"Connected to spreadsheet successfully",
                    "data": spreadsheet_info
                }
            else:
                return {
                    "status": "error",
                    "error": "Failed to connect to spreadsheet"
                }

        except Exception as e:
            logger.error(f"Error connecting to spreadsheet: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def connect_to_spreadsheet_by_name(self, spreadsheet_name: str) -> Dict[str, Any]:
        """Connect to a Google Spreadsheet by name."""
        try:
            success = self.sheets_client.connect_to_spreadsheet_by_name(spreadsheet_name)

            if success:
                spreadsheet_info = self.sheets_client.get_spreadsheet_info()
                return {
                    "status": "success",
                    "message": f"Connected to spreadsheet '{spreadsheet_name}' successfully",
                    "data": spreadsheet_info
                }
            else:
                return {
                    "status": "error",
                    "error": f"Failed to connect to spreadsheet '{spreadsheet_name}'"
                }

        except Exception as e:
            logger.error(f"Error connecting to spreadsheet by name: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def create_new_spreadsheet(self, title: str) -> Dict[str, Any]:
        """Create a new Google Spreadsheet."""
        try:
            spreadsheet_id = self.sheets_client.create_new_spreadsheet(title)

            if spreadsheet_id:
                spreadsheet_info = self.sheets_client.get_spreadsheet_info()
                return {
                    "status": "success",
                    "message": f"Created new spreadsheet '{title}' successfully",
                    "data": spreadsheet_info
                }
            else:
                return {
                    "status": "error",
                    "error": f"Failed to create spreadsheet '{title}'"
                }

        except Exception as e:
            logger.error(f"Error creating new spreadsheet: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def list_worksheets(self) -> Dict[str, Any]:
        """List all worksheets in the current spreadsheet."""
        try:
            if not self.sheets_client.is_connected():
                return {
                    "status": "error",
                    "error": "No spreadsheet connected"
                }

            worksheets = self.sheets_client.list_worksheets()

            return {
                "status": "success",
                "data": {
                    "worksheets": worksheets,
                    "count": len(worksheets)
                }
            }

        except Exception as e:
            logger.error(f"Error listing worksheets: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def create_worksheet(self, title: str, rows: int = 1000, cols: int = 20) -> Dict[str, Any]:
        """Create a new worksheet in the current spreadsheet."""
        try:
            if not self.sheets_client.is_connected():
                return {
                    "status": "error",
                    "error": "No spreadsheet connected"
                }

            success = self.sheets_client.create_worksheet(title, rows, cols)

            if success:
                return {
                    "status": "success",
                    "message": f"Created worksheet '{title}' successfully",
                    "data": {
                        "worksheet_name": title,
                        "rows": rows,
                        "cols": cols
                    }
                }
            else:
                return {
                    "status": "error",
                    "error": f"Failed to create worksheet '{title}'"
                }

        except Exception as e:
            logger.error(f"Error creating worksheet: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def delete_worksheet(self, worksheet_name: str) -> Dict[str, Any]:
        """Delete a worksheet from the current spreadsheet."""
        try:
            if not self.sheets_client.is_connected():
                return {
                    "status": "error",
                    "error": "No spreadsheet connected"
                }

            success = self.sheets_client.delete_worksheet(worksheet_name)

            if success:
                return {
                    "status": "success",
                    "message": f"Deleted worksheet '{worksheet_name}' successfully"
                }
            else:
                return {
                    "status": "error",
                    "error": f"Failed to delete worksheet '{worksheet_name}'"
                }

        except Exception as e:
            logger.error(f"Error deleting worksheet: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_worksheet_data(self, worksheet_name: str, range_notation: str = None) -> Dict[str, Any]:
        """Get data from a specific worksheet."""
        try:
            if not self.sheets_client.is_connected():
                return {
                    "status": "error",
                    "error": "No spreadsheet connected"
                }

            data = self.sheets_client.get_worksheet_data(worksheet_name, range_notation)

            return {
                "status": "success",
                "data": {
                    "worksheet_name": worksheet_name,
                    "range": range_notation or "All data",
                    "rows": len(data),
                    "values": data
                }
            }

        except Exception as e:
            logger.error(f"Error getting worksheet data: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_spreadsheet_info(self) -> Dict[str, Any]:
        """Get information about the current spreadsheet."""
        try:
            if not self.sheets_client.is_connected():
                return {
                    "status": "error",
                    "error": "No spreadsheet connected"
                }

            info = self.sheets_client.get_spreadsheet_info()

            if "error" in info:
                return {
                    "status": "error",
                    "error": info["error"]
                }

            return {
                "status": "success",
                "data": info
            }

        except Exception as e:
            logger.error(f"Error getting spreadsheet info: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def create_worksheet_in_spreadsheet(self, spreadsheet_name: str, worksheet_name: str, rows: int = 1000, cols: int = 20) -> Dict[str, Any]:
        """Create a new worksheet in a specific spreadsheet by name."""
        try:
            # First connect to the spreadsheet by name
            connect_success = self.sheets_client.connect_to_spreadsheet_by_name(spreadsheet_name)

            if not connect_success:
                return {
                    "status": "error",
                    "error": f"Failed to connect to spreadsheet '{spreadsheet_name}'"
                }

            # Now create the worksheet
            success = self.sheets_client.create_worksheet(worksheet_name, rows, cols)

            if success:
                return {
                    "status": "success",
                    "message": f"Created worksheet '{worksheet_name}' in spreadsheet '{spreadsheet_name}' successfully",
                    "data": {
                        "spreadsheet_name": spreadsheet_name,
                        "worksheet_name": worksheet_name,
                        "rows": rows,
                        "cols": cols
                    }
                }
            else:
                return {
                    "status": "error",
                    "error": f"Failed to create worksheet '{worksheet_name}' in spreadsheet '{spreadsheet_name}'"
                }

        except Exception as e:
            logger.error(f"Error creating worksheet in spreadsheet: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def write_receipt_to_sheet(self, spreadsheet_name: str, worksheet_name: str, start_row: int, receipt_data: dict) -> Dict[str, Any]:
        """Write receipt data to a specific worksheet in a spreadsheet."""
        try:
            # First connect to the spreadsheet by name
            connect_success = self.sheets_client.connect_to_spreadsheet_by_name(spreadsheet_name)

            if not connect_success:
                return {
                    "status": "error",
                    "error": f"Failed to connect to spreadsheet '{spreadsheet_name}'"
                }

            # Write the receipt data
            result = self.sheets_client.write_receipt_data(worksheet_name, start_row, receipt_data)

            if result["success"]:
                return {
                    "status": "success",
                    "message": f"Receipt data written to '{worksheet_name}' in spreadsheet '{spreadsheet_name}'",
                    "data": {
                        "spreadsheet_name": spreadsheet_name,
                        "worksheet_name": worksheet_name,
                        "start_row": result["start_row"],
                        "end_row": result["end_row"],
                        "rows_written": result["rows_written"],
                        "range": result["range"]
                    }
                }
            else:
                return {
                    "status": "error",
                    "error": result["error"]
                }

        except Exception as e:
            logger.error(f"Error writing receipt data: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
