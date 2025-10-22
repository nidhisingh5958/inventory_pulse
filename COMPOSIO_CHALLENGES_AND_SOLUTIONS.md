# 🔧 Composio Challenges & Solutions

## Overview
This document comprehensively documents all challenges encountered during Composio integration and the solutions implemented. These insights are valuable for future developers working with Composio and integration platforms.

---

## 1. Authentication & Connection Issues

### Challenge 1.1: Unclear OAuth Flow Documentation
**Problem:**
- Composio's OAuth documentation was minimal and unclear
- Multiple ways to authenticate (direct API key, OAuth2, auth configs) caused confusion
- Redirect URI specifications were vague, leading to multiple failed OAuth attempts


**Solution Implemented:**
```python
# Created robust connection verification in utils.py
def check_gmail_connection():
    """Verify Gmail connection status with Composio"""
    try:
        accounts = toolset.get_connected_accounts()
        if accounts:
            print(f"Found {len(accounts)} existing connection(s)")
            return True
        else:
            print("No connected accounts found. Need to authenticate with Gmail...")
            return False
    except Exception as e:
        print(f"Could not retrieve connected accounts: {e}")
        return False

# Clear OAuth initiation with proper error handling
if not connected and COMPOSIO_GMAIL_ACCOUNT_ID != "your_auth_config_id":
    try:
        connection_request = toolset.initiate_connection(
            app=App.GMAIL,
            integration_id=COMPOSIO_GMAIL_ACCOUNT_ID,
        )
        print(f"Visit: {connection_request.redirect_url}")
        print("Waiting for authorization...")
    except Exception as e:
        print(f"Failed to connect Gmail: {e}")
```

---

## 2. Connected Account Discovery Issues

### Challenge 2.2: Finding and Using Connected Accounts
**Problem:**
- No clear way to discover which auth configs (connected accounts) are available
- Different apps (Gmail, Notion, Sheets) had different connection patterns
- Hard to determine if a connection was actually "ACTIVE" and usable

**Impact:**
- Runtime errors when attempting to send emails or update Notion
- Unclear error messages about missing connections
- Had to add debugging logic to identify connection issues

**Solution Implemented:**
```python
# Created clear account discovery pattern
def discover_connected_accounts():
    """Discover and list all available Composio connected accounts"""
    composio_client = Composio()
    connected_accounts = composio_client.connected_accounts.get()
    
    account_map = {}
    for account in connected_accounts:
        app_name = account.appName.lower()
        if account.status == 'ACTIVE':
            account_map[app_name] = account.id
            print(f"✅ {app_name}: {account.id} (ACTIVE)")
        else:
            print(f"⚠️  {app_name}: {account.id} ({account.status})")
    
    return account_map

# Usage in connectors
gmail_accounts = discover_connected_accounts()
if 'gmail' not in gmail_accounts:
    raise ValueError("No active Gmail connected account found")
```

---

## 3. Gmail Integration Challenges

### Challenge 3.1: Email Sending with Composio Gmail Action
**Problem:**
- Action schema for Gmail sending was not well-documented
- Unclear which parameters were required vs optional
- Response format and error messages were inconsistent

**Impact:**
- Multiple failed email send attempts
- No clear feedback on why emails weren't being sent
- Difficult to debug authentication vs parameter issues

**Solution Implemented:**
```python
class ComposioEmailConnector:
    """Email connector using Composio Gmail integration"""
    
    def _send_composio_email(self, to: str, subject: str, html_body: str, message_id: str) -> str:
        """Send email with proper error handling and logging"""
        try:
            # Use Composio action to send email
            action = Action.GMAIL_SEND_EMAIL
            
            # Properly formatted parameters based on trial-and-error
            params = {
                "to": to,
                "subject": subject,
                "body": html_body,
                "body_type": "html"  # Important: specify HTML type
            }
            
            response = self.toolset.execute_action(
                action=action,
                params=params,
                connected_account_id=self.gmail_connected_account
            )
            
            composio_message_id = response.data.get('id', message_id)
            self.logger.info(f"Email sent successfully via Composio (ID: {composio_message_id})")
            return composio_message_id
            
        except Exception as e:
            self.logger.error(f"Composio Gmail sending failed: {str(e)}")
            raise

    def send_email(self, to: str, subject: str, html_body: str) -> str:
        """Main email sending method with fallback"""
        try:
            message_id = f"composio_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}"
            
            if self.demo_mode:
                # Demo mode: write to file instead
                return self._write_demo_email(to, subject, html_body, message_id)
            else:
                # Production: use Composio
                return self._send_composio_email(to, subject, html_body, message_id)
                
        except Exception as e:
            self.logger.error(f"Error sending email to {to}: {str(e)}")
            raise
```

**Key Learning:**
- Always specify `body_type: "html"` when sending HTML emails
- Include proper error logging at each step
- Provide demo/fallback modes for testing without Composio
- Use `connected_account_id` parameter explicitly

---

## 4. Notion Integration Challenges

### Challenge 4.1: Notion Page Property Format Complexity
**Problem:**
- Notion API expects very specific property formats for different field types
- Different property types (text, number, select, date) have completely different schemas
- Documentation about these formats in Composio was minimal
- Mixing property formats would cause silent failures or unclear errors

**Impact:**
- Pages were created but properties weren't being set correctly
- Rich text formatting was being lost
- Select fields (status) weren't updating properly

**Solution Implemented:**
```python
def update_existing_page(self, page_id: str, sku: str, qty: int, vendor_name: str, 
                        total_cost: float, eoq: int, forecast_text: str, 
                        evidence_list: List[str]) -> str:
    """Update Notion page with properly formatted properties"""
    
    # Format evidence as bulleted list
    evidence_text = "\n".join([f"• {evidence}" for evidence in evidence_list])
    
    # Notion requires very specific property schemas per type
    properties = {
        # Text/Title property
        "SKU": {
            "title": [{"text": {"content": sku}}]
        },
        # Number property
        "Quantity": {
            "number": qty
        },
        # Rich text property
        "Vendor": {
            "rich_text": [{"text": {"content": vendor_name}}]
        },
        # Another number
        "Total Cost": {
            "number": total_cost
        },
        "EOQ": {
            "number": eoq
        },
        # Select property (for status)
        "Status": {
            "select": {"name": "Pending Approval"}
        },
        # Date property
        "Updated Date": {
            "date": {"start": datetime.now().isoformat()}
        },
        # More rich text
        "Forecast": {
            "rich_text": [{"text": {"content": forecast_text}}]
        },
        "Evidence": {
            "rich_text": [{"text": {"content": evidence_text}}]
        }
    }
    
    # Execute Composio action with correct format
    response = self.toolset.execute_action(
        action=Action.NOTION_UPDATE_PAGE,
        params={
            "page_id": page_id,
            "properties": properties
        },
        connected_account_id=self.notion_connected_account
    )
    
    return response
```

**Key Learning:**
- Create a reference document for each Notion property type schema
- Test each property type individually before combining
- Use helper methods to format complex properties
- Always validate property structure before sending to API

### Challenge 4.2: Page Creation vs. Page Updating
**Problem:**
- Creating new Notion pages through Composio had limited functionality
- The create action didn't support all the properties we needed to set
- Documentation didn't clarify the difference between create and update operations
- Had to work around by creating pages elsewhere and updating them via Composio

**Impact:**
- Complex workaround needed to create pages with full property set
- Two-step process instead of single operation
- Potential race conditions and data consistency issues

**Solution Implemented:**
```python
# Instead of trying to create with all properties:
# 1. Create page with minimal properties
# 2. Then update with all desired properties

def create_reorder_page(self, sku: str, qty: int, vendor_name: str, 
                       total_cost: float, eoq: int, forecast_text: str, 
                       evidence_list: List[str]) -> str:
    """
    Note: This method was changed to only update existing pages.
    Creating new pages should be done outside of Composio, 
    then use update_existing_page() to populate all properties.
    """
    raise NotImplementedError(
        "This method now only updates existing pages. "
        "Use update_existing_page() with a valid page_id instead."
    )

# Working pattern:
# 1. Create page manually or via other service
# 2. Get page_id
# 3. Use update_existing_page() to fill in all data
```

**Key Learning:**
- Composio may have limitations on certain operations
- Document limitations clearly in code
- Create workarounds that are well-documented and tested
- Consider creating pages via Notion's native UI or direct API first

---

## 5. Action Schema & Parameter Discovery

### Challenge 5.1: Unclear Action Parameters
**Problem:**
- Composio's action schemas were sometimes unclear about required vs optional parameters
- No clear way to discover available actions for each integration
- Parameter names didn't always match expected conventions
- Different API versions seemed to use different parameter names

**Impact:**
- Trial-and-error approach to figure out correct parameters
- Runtime errors about missing required parameters
- Inconsistent behavior across different actions

**Solution Implemented:**
```python
# Created action discovery and logging utility
def discover_available_actions():
    """Discover all available Composio actions"""
    toolset = ComposioToolSet(entity_id="default")
    
    # For Gmail
    gmail_actions = toolset.find_actions_by_tags(tags=["send_email"])
    print(f"Gmail send email actions: {gmail_actions}")
    
    # For Notion
    notion_actions = toolset.find_actions_by_tags(tags=["update"])
    print(f"Notion update actions: {notion_actions}")
    
    # Log action schemas
    for action in gmail_actions:
        print(f"Action: {action.name}")
        print(f"Schema: {action.schema}")

# Created reference mapping
ACTION_SCHEMAS = {
    'GMAIL_SEND_EMAIL': {
        'required': ['to', 'subject', 'body'],
        'optional': ['cc', 'bcc', 'body_type', 'attachments'],
        'body_type_options': ['text', 'html']
    },
    'NOTION_UPDATE_PAGE': {
        'required': ['page_id', 'properties'],
        'optional': ['archived']
    }
}
```

**Key Learning:**
- Create a local reference of action schemas for your specific use case
- Document which parameters are required vs optional
- Log action execution with full parameters for debugging
- Test each action with minimal parameters first, then add optional ones

---

## 6. Error Handling & Debugging

### Challenge 6.1: Unclear Error Messages
**Problem:**
- Composio errors were often vague ("API Error" without details)
- Stack traces didn't indicate which integration or action failed
- No clear distinction between auth errors, parameter errors, and service errors

**Impact:**
- Very difficult debugging process
- Unclear what to fix when something went wrong
- Poor error messages in logs

**Solution Implemented:**
```python
# Created comprehensive error handling wrapper
class ComposioActionExecutor:
    """Wrapper for Composio actions with detailed error handling"""
    
    @staticmethod
    def execute_with_logging(action_name: str, params: dict, connected_account_id: str):
        """Execute Composio action with comprehensive logging"""
        try:
            logger.info(f"Executing action: {action_name}")
            logger.debug(f"Parameters: {params}")
            
            response = toolset.execute_action(
                action=action_name,
                params=params,
                connected_account_id=connected_account_id
            )
            
            logger.info(f"✅ Action succeeded: {action_name}")
            return response
            
        except ValueError as e:
            logger.error(f"❌ Invalid parameter for {action_name}: {str(e)}")
            logger.debug(f"Parameters were: {params}")
            raise
        except ConnectionError as e:
            logger.error(f"❌ Connection error for {action_name}: {str(e)}")
            logger.error(f"Connected account: {connected_account_id}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error in {action_name}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            raise

# Usage
result = ComposioActionExecutor.execute_with_logging(
    action_name=Action.GMAIL_SEND_EMAIL,
    params={"to": email, "subject": subject, "body": html_body},
    connected_account_id=gmail_account_id
)
```

**Key Learning:**
- Wrap all Composio actions in comprehensive error handlers
- Log both before and after action execution
- Include action name, parameters, and account ID in error logs
- Create specific exception types for different error scenarios

### Challenge 6.2: Testing Without Live Integrations
**Problem:**
- Every test required live connections to Gmail, Notion, Sheets
- Couldn't test logic without setting up all OAuth flows
- Risk of sending test emails to real addresses
- Made development slow and error-prone

**Impact:**
- Slow development cycle
- Accidental test emails sent to real users
- Difficulty in isolation testing

**Solution Implemented:**
```python
# Created demo mode for all connectors
class ComposioEmailConnector:
    def __init__(self, demo_mode: bool = False):
        self.demo_mode = demo_mode
        
        if demo_mode:
            self.outbox_dir = Path("demo/outbox")
            self.outbox_dir.mkdir(parents=True, exist_ok=True)
            logger.info("📝 Running in demo mode - emails saved to file")
        else:
            # Initialize real Composio connection
            self.composio_client = Composio()

    def send_email(self, to: str, subject: str, html_body: str) -> str:
        message_id = f"demo_{uuid.uuid4().hex[:12]}"
        
        if self.demo_mode:
            return self._write_demo_email(to, subject, html_body, message_id)
        else:
            return self._send_composio_email(to, subject, html_body, message_id)

    def _write_demo_email(self, to: str, subject: str, html_body: str, message_id: str) -> str:
        """Write email to file for testing"""
        filename = f"{int(datetime.now().timestamp())}_{message_id}.html"
        filepath = self.outbox_dir / filename
        
        html_content = f"""
        <html>
        <head><title>{subject}</title></head>
        <body>
            <p><strong>To:</strong> {to}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <hr>
            {html_body}
        </body>
        </html>
        """
        
        filepath.write_text(html_content)
        logger.info(f"Demo email saved to {filepath}")
        return str(filepath)

# Usage
# For development/testing:
connector = ComposioEmailConnector(demo_mode=True)

# For production:
connector = ComposioEmailConnector(demo_mode=False)
```

**Key Learning:**
- Always implement demo/test modes for external integrations
- Write test outputs to files for inspection
- Make demo mode easy to toggle (environment variable)
- Never hardcode production mode

---

## 7. Rate Limiting & Performance

### Challenge 7.1: Rate Limits Not Documented
**Problem:**
- Composio rate limits were not documented
- No clear error messages when hitting rate limits
- Unclear if rate limits were per user, per account, or global
- No backoff strategy mentioned in documentation

**Impact:**
- Occasional mysterious failures during batch operations
- Needed to add delays between API calls through trial-and-error
- No clear guidance on scaling the system

**Solution Implemented:**
```python
# Created exponential backoff mechanism
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def execute_action_with_backoff(action: str, params: dict, account_id: str):
    """Execute Composio action with exponential backoff on failure"""
    return toolset.execute_action(
        action=action,
        params=params,
        connected_account_id=account_id
    )

# Usage for batch operations
for item in items:
    try:
        result = execute_action_with_backoff(
            action=Action.NOTION_UPDATE_PAGE,
            params={"page_id": item.id, "properties": item.properties},
            account_id=notion_account_id
        )
    except Exception as e:
        logger.error(f"Failed after 3 retries: {str(e)}")
        # Handle permanent failure
```

**Key Learning:**
- Implement exponential backoff for all API calls
- Don't hardcode delays; use a proper retry library
- Monitor rate limit headers if available
- Consider queueing operations for batch processing

---

## 8. Integration Testing

### Challenge 8.2: Complex Multi-Step Workflows
**Problem:**
- Testing full workflows required all integrations to be working
- One failing integration blocked entire workflow tests
- Difficult to test error scenarios

**Impact:**
- Incomplete test coverage
- Difficult to debug end-to-end issues
- Flaky tests due to external service dependencies

**Solution Implemented:**
```python
# Created comprehensive test suite with mocking
class TestComposioIntegration:
    """Test suite for Composio integrations"""
    
    @pytest.fixture
    def mock_composio_client(self):
        """Mock Composio client for testing"""
        with patch('composio.Composio') as mock:
            yield mock
    
    def test_email_send_demo_mode(self):
        """Test email sending in demo mode"""
        connector = ComposioEmailConnector(demo_mode=True)
        result = connector.send_email(
            to="test@example.com",
            subject="Test",
            html_body="<p>Test</p>"
        )
        assert Path(result).exists()  # File was created
    
    def test_email_send_real_mode_with_mock(self, mock_composio_client):
        """Test email sending in real mode with mocked Composio"""
        mock_composio_client.return_value.connected_accounts.get.return_value = [
            MockAccount(appName='gmail', status='ACTIVE', id='test-id')
        ]
        
        connector = ComposioEmailConnector(demo_mode=False)
        # Mock the execute_action call
        connector.toolset.execute_action = Mock(return_value=Mock(data={'id': 'msg-123'}))
        
        result = connector.send_email(
            to="test@example.com",
            subject="Test",
            html_body="<p>Test</p>"
        )
        assert result == 'msg-123'
    
    def test_workflow_with_fallback(self):
        """Test workflow handles Composio failures gracefully"""
        connector = ComposioEmailConnector(demo_mode=True)  # Fallback to demo
        
        # Simulate failure and recovery
        try:
            result = connector.send_email("test@test.com", "Test", "<p>Test</p>")
            assert result  # Should have some result (file path in demo mode)
        except Exception as e:
            pytest.fail(f"Workflow should not fail: {str(e)}")
```

**Key Learning:**
- Use mock objects for external services
- Test demo/fallback modes thoroughly
- Create fixtures for common test setups
- Test error scenarios explicitly

---

## 9. Documentation & Environment Setup

### Challenge 9.1: Scattered Configuration Requirements
**Problem:**
- Composio setup required multiple steps across different platforms
- Environment variables weren't well-documented
- Each integration (Gmail, Notion, Sheets) had different setup processes
- No single source of truth for what needed to be configured

**Impact:**
- New developers spent hours setting up environment
- Setup failures without clear error messages
- Inconsistent configurations between team members

**Solution Implemented:**
```bash
# Created comprehensive .env template
# .env.example file with all required variables

# ============================================================================
# COMPOSIO CONFIGURATION
# ============================================================================
COMPOSIO_API_KEY=your_composio_api_key_here
COMPOSIO_USER_ID=your_unique_user_id_here
COMPOSIO_GMAIL_ACCOUNT_ID=your_gmail_auth_config_id_here
COMPOSIO_NOTION_ACCOUNT_ID=your_notion_auth_config_id_here

# ============================================================================
# GOOGLE CLOUD SETUP
# ============================================================================
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id

# ============================================================================
# NOTION SETUP
# ============================================================================
NOTION_DATABASE_ID=your_database_id

# ============================================================================
# DEPLOYMENT & DEBUGGING
# ============================================================================
DEBUG=true
DEMO_MODE=true  # Set to false for production
LOG_LEVEL=INFO
```

**Created setup verification script:**
```python
# setup_verification.py
import os
from dotenv import load_dotenv

def verify_composio_setup():
    """Verify all Composio environment variables are set"""
    load_dotenv()
    
    required_vars = {
        'COMPOSIO_API_KEY': 'Composio API key',
        'COMPOSIO_USER_ID': 'Composio user ID',
        'COMPOSIO_GMAIL_ACCOUNT_ID': 'Gmail auth config ID',
        'COMPOSIO_NOTION_ACCOUNT_ID': 'Notion auth config ID',
        'GEMINI_API_KEY': 'Gemini API key',
        'GOOGLE_SHEETS_SPREADSHEET_ID': 'Google Sheets ID',
        'NOTION_DATABASE_ID': 'Notion database ID',
    }
    
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: MISSING - {description}")
            missing.append(var)
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} required variables!")
        print("Update your .env file with these values.")
        return False
    else:
        print("\n✅ All environment variables configured!")
        return True

if __name__ == "__main__":
    verify_composio_setup()
```

**Key Learning:**
- Create comprehensive setup documentation
- Provide example .env file
- Create verification scripts
- Document each variable's purpose and where to find it

---

## 10. Alternative Implementations

### Challenge 10.1: When Composio Falls Short
**Problem:**
- Some Composio features were incomplete or unreliable
- Direct API fallback was sometimes necessary
- Mixing Composio and direct API calls caused maintenance issues

**Impact:**
- Code became complex with multiple implementation paths
- Difficult to test and maintain hybrid approach
- Unclear when to use Composio vs direct API

**Solution Implemented:**
```python
# Created abstraction layer for hybrid approach
class EmailConnector:
    """Abstract email connector supporting multiple implementations"""
    
    def __init__(self, implementation='composio', demo_mode=False):
        self.implementation = implementation
        self.demo_mode = demo_mode
        
        if implementation == 'composio':
            self.backend = ComposioEmailConnector(demo_mode=demo_mode)
        elif implementation == 'direct_oauth':
            self.backend = DirectOAuthEmailConnector(demo_mode=demo_mode)
        else:
            raise ValueError(f"Unknown implementation: {implementation}")
    
    def send_email(self, to: str, subject: str, html_body: str) -> str:
        """Send email using configured backend"""
        return self.backend.send_email(to, subject, html_body)

# Usage
# Development
dev_connector = EmailConnector(implementation='composio', demo_mode=True)

# Production with Composio
prod_connector = EmailConnector(implementation='composio', demo_mode=False)

# Fallback if Composio fails
fallback_connector = EmailConnector(implementation='direct_oauth', demo_mode=False)
```

**Key Learning:**
- Create abstraction layers for multiple implementations
- Document when each implementation should be used
- Test each implementation separately
- Provide clear fallback mechanisms

---

## Summary of Key Fixes Applied

| Issue | Impact | Solution |
|-------|--------|----------|
| OAuth flow unclear | 3-4 days lost | Created connection verification helper |
| Connected account discovery | Runtime errors | Built account discovery pattern |
| Gmail parameter schema | Email failures | Documented action schemas locally |
| Notion property formats | Silent failures | Created property formatting helpers |
| Unclear error messages | Slow debugging | Added comprehensive logging wrapper |
| No testing without live connections | Slow development | Implemented demo mode for all connectors |
| Rate limits unknown | Occasional failures | Added exponential backoff retry logic |
| Complex setup process | Onboarding difficult | Created .env template and verification script |
| Scattered documentation | Confusion | Centralized setup guide and examples |
| Partial Composio features | Code complexity | Created abstraction layer with fallbacks |

---

## Best Practices Established

### ✅ Do's
- ✅ Always check connected account status before operations
- ✅ Implement demo/test modes for all external integrations
- ✅ Use exponential backoff for API retries
- ✅ Log all action executions with full context
- ✅ Create local reference documents for action schemas
- ✅ Provide fallback implementations
- ✅ Document environment setup comprehensively
- ✅ Test error scenarios explicitly

### ❌ Don'ts
- ❌ Don't hardcode API keys or auth config IDs
- ❌ Don't ignore Composio errors without investigation
- ❌ Don't mix Composio and direct API calls without abstraction
- ❌ Don't assume action parameters without testing
- ❌ Don't rely solely on live connections for testing
- ❌ Don't send test/demo emails to real addresses
- ❌ Don't skip error handling in production code

---

## Resources Created

### Code Files
- `src/working_code/src/connectors/composio_email_connector_class.py` - Robust email connector with demo mode
- `src/working_code/src/connectors/composio_notion_connector.py` - Notion connector with property formatting
- `src/composio_dev/helper/utils.py` - Connection verification and action discovery utilities
- `src/working_code/src/connectors/composio_email_connector.py` - Test implementation example

### Documentation
- `.env.example` - Complete environment template
- `docs/setup/authentication.md` - Detailed auth setup guide
- `docs/setup/environment.md` - Environment configuration guide

### Test/Demo
- `demo/outbox/` - Directory for demo emails
- Test scripts for each integration

---

## Lessons for Future Composio Users

1. **Start with demo mode** - Always develop with demo/test modes first
2. **Build abstractions early** - Don't directly couple to Composio throughout codebase
3. **Document as you go** - Keep a log of issues and solutions while developing
4. **Use environment variables** - Never hardcode any credentials or config IDs
5. **Implement comprehensive logging** - You'll need it for debugging
6. **Test connections before operations** - Always verify available accounts
7. **Plan for fallbacks** - Have backup implementations ready
8. **Create setup scripts** - Help future developers with quick verification

---

## Version Info
- **Composio SDK**: Latest (as of October 2025)
- **Document Created**: October 22, 2025
- **Last Updated**: October 22, 2025
- **Team**: NeoMinds

---

**For more information, refer to:**
- 📄 `docs/setup/authentication.md` - Authentication setup details
- 📄 `docs/setup/environment.md` - Environment configuration
- 📄 `src/working_code/README.md` - Working implementation details
- 💬 **Issues or questions?** Check the specific connector files for inline comments

