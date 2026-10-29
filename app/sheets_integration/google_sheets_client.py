import os
import logging
from typing import List, Dict, Optional, Any
import gspread
from google.oauth2.service_account import Credentials
import json
import time
from requests.exceptions import ConnectionError, RequestException

logger = logging.getLogger(__name__)

class GoogleSheetsClient:
    """Client for connecting to and managing Google Sheets."""

    def __init__(self):
        self.client = None
        self.current_spreadsheet = None
        self.credentials_path = None
        self.setup_credentials()

    def retry_api_call(self, func, *args, max_retries=3, base_delay=1, **kwargs):
        """Retry API calls with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except (ConnectionError, RequestException, Exception) as e:
                if attempt == max_retries - 1:  # Last attempt
                    logger.error(f"❌ API call failed after {max_retries} attempts: {e}")
                    raise e

                delay = base_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"⚠️ API call failed (attempt {attempt + 1}/{max_retries}), retrying in {delay}s: {e}")
                time.sleep(delay)

    def setup_credentials(self):
        """Setup Google Sheets API credentials."""
        try:
            # Try to get credentials from environment variable (JSON string)
            credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")

            if credentials_json:
                # Parse JSON credentials from environment variable
                credentials_dict = json.loads(credentials_json)
                print(credentials_dict)
                credentials = Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                )
            else:
                # Try to use credentials file from env or default to sheets_integration/credentials.json
                credentials_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
                if credentials_file and os.path.exists(credentials_file):
                    credentials_path = credentials_file
                else:
                    # Default to sheets_integration/credentials.json
                    default_path = os.path.join(os.path.dirname(__file__), "credentials.json")
                    if os.path.exists(default_path):
                        credentials_path = default_path
                    else:
                        logger.error("No Google Sheets credentials found!")
                        return
                credentials = Credentials.from_service_account_file(
                    credentials_path,
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                )
            self.client = gspread.authorize(credentials)
            logger.info("✅ Google Sheets client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to setup Google Sheets credentials: {e}")
            self.client = None

    def test_connection(self) -> bool:
        """Test the Google Sheets connection."""
        try:
            if not self.client:
                logger.error("No Google Sheets client available")
                return False

            # Try to list spreadsheets to test connection
            self.retry_api_call(self.client.list_spreadsheet_files)
            logger.info("✅ Google Sheets connection test successful")
            return True

        except Exception as e:
            logger.error(f"❌ Google Sheets connection test failed: {e}")
            return False

    def connect_to_spreadsheet(self, spreadsheet_id: str) -> bool:
        """Connect to a specific Google Spreadsheet by ID."""
        try:
            if not self.client:
                logger.error("Google Sheets client not initialized")
                return False

            self.current_spreadsheet = self.retry_api_call(
                self.client.open_by_key,
                spreadsheet_id
            )
            logger.info(f"✅ Connected to spreadsheet: {self.current_spreadsheet.title}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to spreadsheet {spreadsheet_id}: {e}")
            return False

    def connect_to_spreadsheet_by_name(self, spreadsheet_name: str) -> bool:
        """Connect to a Google Spreadsheet by name."""
        try:
            if not self.client:
                logger.error("Google Sheets client not initialized")
                return False

            # List all spreadsheets visible to the service account
            spreadsheets = self.retry_api_call(self.client.list_spreadsheet_files)
            logger.info(f"Service account can see these spreadsheets: {[s['name'] for s in spreadsheets]}")

            self.current_spreadsheet = self.retry_api_call(
                self.client.open,
                spreadsheet_name
            )
            logger.info(f"✅ Connected to spreadsheet: {self.current_spreadsheet.title}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to spreadsheet '{spreadsheet_name}': {e}")
            return False

    def create_new_spreadsheet(self, title: str) -> Optional[str]:
        """Create a new Google Spreadsheet."""
        try:
            if not self.client:
                logger.error("Google Sheets client not initialized")
                return None

            spreadsheet = self.client.create(title)
            self.current_spreadsheet = spreadsheet

            logger.info(f"✅ Created new spreadsheet: {title}")
            logger.info(f"📋 Spreadsheet ID: {spreadsheet.id}")
            logger.info(f"🔗 URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")

            return spreadsheet.id

        except Exception as e:
            logger.error(f"❌ Failed to create spreadsheet '{title}': {e}")
            return None

    def list_worksheets(self) -> List[str]:
        """List all worksheets in the current spreadsheet."""
        try:
            if not self.current_spreadsheet:
                logger.error("No spreadsheet connected")
                return []

            worksheets = self.current_spreadsheet.worksheets()
            worksheet_names = [ws.title for ws in worksheets]

            logger.info(f"📋 Found {len(worksheet_names)} worksheets: {worksheet_names}")
            return worksheet_names

        except Exception as e:
            logger.error(f"❌ Failed to list worksheets: {e}")
            return []

    def create_worksheet(self, title: str, rows: int = 1000, cols: int = 20) -> bool:
        """Create a new worksheet in the current spreadsheet."""
        try:
            if not self.current_spreadsheet:
                logger.error("No spreadsheet connected")
                return False

            worksheet = self.current_spreadsheet.add_worksheet(
                title=title,
                rows=rows,
                cols=cols
            )

            logger.info(f"✅ Created new worksheet: {title} ({rows}x{cols})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create worksheet '{title}': {e}")
            return False

    def get_worksheet(self, worksheet_name: str):
        """Get a specific worksheet by name."""
        try:
            if not self.current_spreadsheet:
                logger.error("No spreadsheet connected")
                return None

            worksheet = self.current_spreadsheet.worksheet(worksheet_name)
            logger.info(f"✅ Accessed worksheet: {worksheet_name}")
            return worksheet

        except Exception as e:
            logger.error(f"❌ Failed to access worksheet '{worksheet_name}': {e}")
            return None

    def delete_worksheet(self, worksheet_name: str) -> bool:
        """Delete a worksheet by name."""
        try:
            if not self.current_spreadsheet:
                logger.error("No spreadsheet connected")
                return False

            worksheet = self.current_spreadsheet.worksheet(worksheet_name)
            self.current_spreadsheet.del_worksheet(worksheet)

            logger.info(f"🗑️ Deleted worksheet: {worksheet_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete worksheet '{worksheet_name}': {e}")
            return False

    def get_spreadsheet_info(self) -> Dict[str, Any]:
        """Get information about the current spreadsheet."""
        try:
            if not self.current_spreadsheet:
                return {"error": "No spreadsheet connected"}

            worksheets = self.list_worksheets()

            return {
                "title": self.current_spreadsheet.title,
                "id": self.current_spreadsheet.id,
                "url": f"https://docs.google.com/spreadsheets/d/{self.current_spreadsheet.id}",
                "worksheets": worksheets,
                "worksheet_count": len(worksheets)
            }

        except Exception as e:
            logger.error(f"❌ Failed to get spreadsheet info: {e}")
            return {"error": str(e)}

    def is_connected(self) -> bool:
        """Check if connected to a spreadsheet."""
        return self.current_spreadsheet is not None

    def get_connection_status(self) -> Dict[str, Any]:
        """Get the current connection status."""
        return {
            "client_initialized": self.client is not None,
            "spreadsheet_connected": self.current_spreadsheet is not None,
            "spreadsheet_title": self.current_spreadsheet.title if self.current_spreadsheet else None,
            "spreadsheet_id": self.current_spreadsheet.id if self.current_spreadsheet else None
        }

    def write_receipt_data(self, worksheet_name: str, start_row: int, receipt_data: dict) -> dict:
        """Write receipt data to a worksheet starting from a specific row."""
        try:
            if not self.current_spreadsheet:
                logger.error("No spreadsheet connected")
                return {"success": False, "error": "No spreadsheet connected"}

            worksheet = self.current_spreadsheet.worksheet(worksheet_name)

            # Prepare the data to write
            rows_to_write = []
            current_row = start_row

            # Header row with vendor and date
            vendor = receipt_data.get('vendor', 'Unknown')
            date = receipt_data.get('date', 'Unknown')
            rows_to_write.append([vendor, date])
            vendor_row = current_row  # Remember vendor row for formatting
            current_row += 1

            # Items
            items = receipt_data.get('items', [])
            for item in items:
                name = item.get('name', '')
                price = item.get('price', 0.0)
                product_id = item.get('product_id', '')

                # Add any additional info (like 'A' or 'AMR' suffixes)
                price_display = str(price)

                rows_to_write.append([name, price_display])
                current_row += 1

            # Subtotal, Tax, Total
            subtotal = receipt_data.get('subtotal', 0.0)
            tax = receipt_data.get('tax', 0.0)
            total = receipt_data.get('total', 0.0)

            if subtotal > 0:
                rows_to_write.append(["Subtotal", str(subtotal)])
                current_row += 1

            rows_to_write.append(["Tax", str(tax)])
            current_row += 1

            rows_to_write.append(["Total", str(total)])
            current_row += 1

            # Write all data at once
            end_row = start_row + len(rows_to_write) - 1
            range_name = f"A{start_row}:B{end_row}"

            self.retry_api_call(
                worksheet.update,
                range_name,
                rows_to_write
            )

            # Apply bold formatting to vendor name (first cell)
            vendor_cell = f"A{vendor_row}"
            self.retry_api_call(
                worksheet.format,
                vendor_cell,
                {
                    "textFormat": {
                        "bold": True
                    }
                }
            )

            logger.info(f"✅ Written receipt data to {worksheet_name} rows {start_row}-{end_row} with bold vendor")

            return {
                "success": True,
                "start_row": start_row,
                "end_row": end_row,
                "rows_written": len(rows_to_write),
                "range": range_name
            }

        except Exception as e:
            logger.error(f"❌ Failed to write receipt data to worksheet '{worksheet_name}': {e}")
            return {
                "success": False,
                "error": str(e)
            }
