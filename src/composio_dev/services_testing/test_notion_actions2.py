from composio_dev.helper.utils import toolset

# Try different action names for creating pages
test_actions = [
    "NOTION_PAGES_CREATE",
    "NOTION_CREATE_DATABASE_ITEM",
    "NOTION_ADD_DATABASE_ITEM",
    "NOTION_DATABASE_CREATE_PAGE",
    "NOTION_PAGES_CREATE_PAGE",
]

print("Testing different Notion create action names:\n")
for action_name in test_actions:
    print(f"Testing {action_name}:")
    try:
        result = toolset.execute_action(
            action=action_name,
            params={
                "databaseId": "2933da3f-160e-803b-96f9-ed9c767767c6",
                "properties": {
                    "Item": {
                        "title": [{"text": {"content": "Test Item"}}]
                    }
                }
            }
        )
        print(f"  ✅ {action_name} works!")
        print(f"     successful={result.get('successful')}")
    except Exception as e:
        error_msg = str(e)
        if "No metadata" in error_msg:
            print(f"  ❌ Deprecated/Not found")
        else:
            print(f"  ⚠️  Error: {error_msg[:100]}")
    print()
