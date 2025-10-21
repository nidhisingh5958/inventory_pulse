from composio_dev.helper.utils import toolset

# Test NOTION_QUERY_DATABASE with different parameter formats
print("Testing NOTION_QUERY_DATABASE parameter formats:\n")

database_id = "2933da3f-160e-803b-96f9-ed9c767767c6"

# Test 1: camelCase
print("1. Testing with camelCase (databaseId):")
try:
    result = toolset.execute_action(
        action="NOTION_QUERY_DATABASE",
        params={
            "databaseId": database_id
        }
    )
    print(f"   ✅ Success! successful={result.get('successful')}")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:150]}")

# Test 2: snake_case
print("\n2. Testing with snake_case (database_id):")
try:
    result = toolset.execute_action(
        action="NOTION_QUERY_DATABASE",
        params={
            "database_id": database_id
        }
    )
    print(f"   ✅ Success! successful={result.get('successful')}")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:150]}")

# Test 3: With filter in camelCase
print("\n3. Testing with filter (camelCase):")
try:
    result = toolset.execute_action(
        action="NOTION_QUERY_DATABASE",
        params={
            "databaseId": database_id,
            "filter": {
                "property": "Status",
                "select": {
                    "equals": "Pending Approval"
                }
            }
        }
    )
    print(f"   ✅ Success! successful={result.get('successful')}")
    print(f"   Results: {len(result.get('data', {}).get('response_data', {}).get('results', []))} items")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:150]}")
