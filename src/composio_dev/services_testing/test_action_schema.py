from composio_dev.helper.utils import toolset

# Find the action
actions = toolset.find_actions_by_tags(tags=["sheets"])
for action in actions:
    if "GET_SPREADSHEET_BY_DATA_FILTER" in action.name:
        print(f"Action: {action.name}")
        print(f"Description: {action.description}")
        if hasattr(action, 'schema'):
            print(f"Schema: {action.schema}")
        break

print("\n\nTrying to execute with camelCase:")
try:
    result = toolset.execute_action(
        action="GOOGLESHEETS_GET_SPREADSHEET_BY_DATA_FILTER",
        params={
            "spreadsheetId": "11kjQlvSRpy8Bqm2WCfgwY3C21kdwFMxP_7B8zEpEFys",
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
    print("SUCCESS with camelCase!")
    print(result)
except Exception as e:
    print(f"Failed: {e}")
