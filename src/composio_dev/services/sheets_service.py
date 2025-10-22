import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from helper.utils import toolset
from composio import App
import json

class SheetsService:
    def __init__(self):
        self.toolset = toolset
        self.connected = False
        self._check_connection()
    
    def _check_connection(self):
        """Check if Google Sheets is connected"""
        try:
            accounts = self.toolset.get_connected_accounts()
            # If we have any connected accounts, assume Google Sheets is available
            # since we're using the toolset which manages multiple integrations
            if accounts and len(accounts) > 0:
                self.connected = True
            else:
                self.connected = False
        except Exception as e:
            print(f"Error checking Sheets connection: {e}")
            self.connected = False
    
    def get_inventory_data(self, spreadsheet_id: str, range_name: str = "A:G"):
        """Get inventory data from Google Sheets"""
        if not self.connected:
            return {"error": "Google Sheets not connected"}
        
        try:
            result = self.toolset.execute_action(
                action="GOOGLESHEETS_GET_SPREADSHEET_BY_DATA_FILTER",
                params={
                    "spreadsheetId": spreadsheet_id,
                    "dataFilters": [
                        {
                            "gridRange": {
                                "sheetId": 0
                            }
                        }
                    ],
                    "includeGridData": True
                }
            )
            
            # Extract values from the response
            if result.get("data") and result.get("data", {}).get("sheets"):
                sheets = result.get("data", {}).get("sheets", [])
                values = []
                for sheet in sheets:
                    if "data" in sheet:
                        for grid_data in sheet.get("data", []):
                            if "rowData" in grid_data:
                                for row in grid_data.get("rowData", []):
                                    row_values = []
                                    for cell in row.get("values", []):
                                        cell_value = cell.get("userEnteredValue", {})
                                        if "stringValue" in cell_value:
                                            row_values.append(cell_value["stringValue"])
                                        elif "numberValue" in cell_value:
                                            row_values.append(str(int(cell_value["numberValue"])))
                                        else:
                                            row_values.append("")
                                    if row_values:
                                        values.append(row_values)
                return {"values": values} if values else {"values": []}
            return result
        except Exception as e:
            return {"error": f"Failed to read sheet: {str(e)}"}
    
    def update_stock(self, spreadsheet_id: str, row: int, new_stock: int):
        """Update stock value in specific row"""
        if not self.connected:
            return {"error": "Google Sheets not connected"}
        
        try:
            # Update column C (Current Stock) for the specific row
            result = self.toolset.execute_action(
                action="GOOGLESHEETS_BATCH_UPDATE_VALUES_BY_DATA_FILTER",
                params={
                    "spreadsheetId": spreadsheet_id,
                    "valueInputOption": "USER_ENTERED",
                    "data": [
                        {
                            "dataFilter": {
                                "a1Range": f"'Sheet1'!C{row}"
                            },
                            "values": [
                                [new_stock]
                            ],
                            "majorDimension": "ROWS"
                        }
                    ]
                }
            )
            return result
        except Exception as e:
            return {"error": f"Failed to update stock: {str(e)}"}
    
    def create_new_stock_entry(self, spreadsheet_id: str, item_data: dict):
        """Create a new stock entry in the inventory sheet"""
        if not self.connected:
            return {"error": "Google Sheets not connected"}
        
        try:
            # Step 1: Read the existing data to find the last filled row
            read_result = self.toolset.execute_action(
                action="GOOGLESHEETS_BATCH_GET",
                params={
                    "spreadsheet_id": spreadsheet_id,
                    "ranges": ["Sheet1!A:A"],  # Adjust the range with the correct sheet name
                    "valueRenderOption": "FORMATTED_VALUE"
                }
            )

            print("read_result:", read_result)

            # Step 2: Determine the last filled row
            if 'valueRanges' in read_result and read_result['valueRanges']:
                last_filled_row = len(read_result['valueRanges'][0].get('values', []))  # Use get to avoid KeyError
                print("last_filled_row:", last_filled_row)
            else:
                last_filled_row = 0  # No data found, start from the first row

            # Step 3: Prepare the new row data
            row_values = [
                item_data.get("item_id", ""),
                item_data.get("item_name", ""),
                item_data.get("current_stock", 0),
                item_data.get("min_threshold", 0),
                item_data.get("daily_usage", 0),
                item_data.get("supplier", ""),
                item_data.get("unit_cost", 0)
            ]
            print("row_values:", row_values)
            
            # Step 4: Add the new row
            update_result = self.toolset.execute_action(
                action="GOOGLESHEETS_BATCH_UPDATE",
                params={
                    "spreadsheet_id": spreadsheet_id,
                    "sheet_name": "Sheet1",  # Ensure this matches your sheet name
                    "first_cell_location": f"A{last_filled_row + 1}",  # Start from the next empty row
                    "valueInputOption": "USER_ENTERED",
                    "values": [row_values]
                }
            )

            print("update_result:", update_result)

            return update_result
        except Exception as e:
            return {"error": f"Failed to create new stock entry: {str(e)}"}


    def track_stock_changes(self, spreadsheet_id: str):
        """Track and return items with low stock"""
        data = self.get_inventory_data(spreadsheet_id)
        if "error" in data:
            return data
        
        low_stock_items = []
        try:
            values = data.get("values", [])
            headers = values[0] if values else []
            
            for i, row in enumerate(values[1:], 2):  # Start from row 2
                if len(row) >= 5:
                    current_stock = int(row[2]) if row[2].isdigit() else 0
                    min_threshold = int(row[3]) if row[3].isdigit() else 0
                    
                    if current_stock <= min_threshold:
                        low_stock_items.append({
                            "row": i,
                            "item_id": row[0],
                            "item_name": row[1],
                            "current_stock": current_stock,
                            "min_threshold": min_threshold,
                            "supplier": row[5] if len(row) > 5 else "",
                            "unit_cost": row[6] if len(row) > 6 else ""
                        })
        except Exception as e:
            return {"error": f"Failed to process data: {str(e)}"}
        
        return {"low_stock_items": low_stock_items}