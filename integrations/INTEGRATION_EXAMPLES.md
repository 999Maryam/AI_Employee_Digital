# Integration Examples

How to integrate the orchestrator with existing systems.

---

## Gmail Watcher Integration

Add to `gmail_watcher.py`:

```python
# At the top of the file
from integrations.integration_helper import trigger_email_received

# In the process_email() function
def process_email(email_data):
    """Process a single email"""

    # Existing code to save email...

    # NEW: Trigger orchestrator workflows
    try:
        workflows_triggered = trigger_email_received(
            subject=email_data['subject'],
            sender=email_data['from'],
            body=email_data.get('body', ''),
            suggested_date=extract_date_from_email(email_data),  # Your extraction logic
            suggested_time=extract_time_from_email(email_data)   # Your extraction logic
        )

        if workflows_triggered:
            print(f"Triggered {len(workflows_triggered)} workflows for email: {email_data['subject']}")
    except Exception as e:
        print(f"Error triggering workflows: {e}")
```

---

## Odoo MCP Server Integration

Add to `odoo-mcp-server/src/index.ts`:

After successfully creating an invoice:

```typescript
// In the create_invoice tool handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "create_invoice") {
    // Existing invoice creation code...
    const invoiceId = await odooClient.createInvoice(invoiceData);

    // NEW: Trigger workflow via Python helper
    try {
      const { spawn } = require('child_process');
      const pythonScript = `
from integrations.integration_helper import trigger_invoice_created

trigger_invoice_created(
    invoice_number="${invoiceId}",
    customer_id=${customerId},
    amount=${totalAmount},
    customer_email="${customerEmail}",
    items=${JSON.stringify(lineItems)}
)
      `;

      spawn('python3', ['-c', pythonScript]);
    } catch (error) {
      console.error('Error triggering workflow:', error);
    }

    return {
      content: [{ type: "text", text: `Invoice created: ${invoiceId}` }]
    };
  }
});
```

**Better approach** - Create a Node.js wrapper:

```javascript
// odoo-mcp-server/src/workflow-trigger.js
const { spawn } = require('child_process');

function triggerInvoiceCreated(invoiceData) {
  const script = `
from integrations.integration_helper import trigger_invoice_created
import json

data = json.loads('''${JSON.stringify(invoiceData)}''')
trigger_invoice_created(
    invoice_number=data['invoice_number'],
    customer_id=data['customer_id'],
    amount=data['amount'],
    customer_email=data.get('customer_email'),
    items=data.get('items', [])
)
  `;

  spawn('python3', ['-c', script]);
}

module.exports = { triggerInvoiceCreated };
```

Then use:

```javascript
const { triggerInvoiceCreated } = require('./workflow-trigger');

// After creating invoice
triggerInvoiceCreated({
  invoice_number: invoiceId,
  customer_id: customerId,
  amount: totalAmount,
  customer_email: customerEmail,
  items: lineItems
});
```

---

## Scheduled Triggers with Cron

Create `/mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/integrations/scheduler.py`:

```python
#!/usr/bin/env python3
"""
Workflow Scheduler
Triggers time-based workflows using cron
"""

import schedule
import time
from datetime import datetime
from pathlib import Path

from integration_helper import trigger_morning_routine


def count_pending_approvals():
    """Count files in Pending_Approval folder"""
    pending_dir = Path("/mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/Pending_Approval")
    return len(list(pending_dir.glob("*.md")))


def morning_routine():
    """Run morning automation"""
    print(f"Running morning routine at {datetime.now()}")

    pending_count = count_pending_approvals()
    trigger_morning_routine(pending_count=pending_count)

    print("Morning routine triggered")


def main():
    """Schedule workflows"""
    # Morning routine at 8 AM
    schedule.every().day.at("08:00").do(morning_routine)

    # Add more schedules here:
    # schedule.every().monday.at("09:00").do(weekly_report)
    # schedule.every().hour.do(check_urgent_emails)

    print("Scheduler started. Press Ctrl+C to exit.")
    print("Scheduled jobs:")
    for job in schedule.jobs:
        print(f"  - {job}")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main()
```

Run with:

```bash
python3 /mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/integrations/scheduler.py
```

Or with PM2:

```bash
pm2 start /mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/integrations/scheduler.py --interpreter python3 --name workflow-scheduler
pm2 save
```

---

## Filesystem Watcher Integration

Add to `filesystem_watcher.py`:

```python
# At the top
from integrations.integration_helper import trigger_file_added

# In the on_created handler
class VaultHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path

        # Existing code...

        # NEW: Trigger workflows
        try:
            file_type = self.detect_file_type(file_path)
            trigger_file_added(
                file_path=file_path,
                file_type=file_type
            )
        except Exception as e:
            print(f"Error triggering workflow: {e}")

    def detect_file_type(self, file_path):
        """Detect file type from name or content"""
        filename = Path(file_path).name.upper()

        if filename.startswith("EMAIL_"):
            return "email"
        elif filename.startswith("INVOICE_"):
            return "invoice"
        elif filename.startswith("EXPENSE_"):
            return "expense"
        else:
            return "unknown"
```

---

## Approval Workflow Integration

Create `/mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/integrations/approval_watcher.py`:

```python
#!/usr/bin/env python3
"""
Approval Watcher
Monitors Approved folder and triggers follow-up workflows
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from integration_helper import trigger_approval_received


class ApprovalHandler(FileSystemEventHandler):
    """Handle files moved to Approved folder"""

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        filename = Path(file_path).name

        print(f"Approval detected: {filename}")

        # Parse approval type from filename
        if filename.startswith("EMAIL_"):
            approval_type = "email"
        elif filename.startswith("INVOICE_"):
            approval_type = "invoice"
        elif filename.startswith("LINKEDIN_"):
            approval_type = "linkedin"
        elif filename.startswith("EXPENSE_"):
            approval_type = "expense"
        else:
            approval_type = "unknown"

        # Read file content for details
        try:
            content = Path(file_path).read_text()

            # Trigger approval workflow
            trigger_approval_received(
                approval_type=approval_type,
                approved=True,  # File in Approved means it's approved
                details={
                    "file_path": file_path,
                    "filename": filename,
                    "content_preview": content[:200]
                }
            )

            print(f"Triggered approval workflow for {approval_type}")

        except Exception as e:
            print(f"Error processing approval: {e}")


def main():
    """Monitor Approved folder"""
    vault_path = Path("/mnt/f/Maryam/Quarter_4/Ai_Employee_Vault")
    approved_folder = vault_path / "Approved"

    # Create folder if doesn't exist
    approved_folder.mkdir(exist_ok=True)

    # Setup watcher
    event_handler = ApprovalHandler()
    observer = Observer()
    observer.schedule(event_handler, str(approved_folder), recursive=False)
    observer.start()

    print(f"Monitoring approvals in: {approved_folder}")
    print("Press Ctrl+C to exit")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
```

---

## Testing Workflows

### Test Script

Create `integrations/test_workflows.py`:

```python
#!/usr/bin/env python3
"""
Test all workflows
"""

from integration_helper import (
    trigger_invoice_created,
    trigger_email_received,
    trigger_expense_recorded,
    trigger_linkedin_post_scheduled,
    trigger_morning_routine
)


def test_invoice_workflow():
    """Test invoice → email workflow"""
    print("Testing invoice workflow...")

    result = trigger_invoice_created(
        invoice_number="TEST-INV-001",
        customer_id=999,
        amount=250.00,
        customer_email="test@example.com"
    )

    print(f"  Result: {len(result)} workflows triggered")
    return len(result) > 0


def test_email_workflow():
    """Test email → calendar workflow"""
    print("Testing email workflow...")

    result = trigger_email_received(
        subject="Meeting tomorrow at 2pm",
        sender="colleague@company.com",
        body="Let's meet tomorrow at 2pm to discuss the project",
        suggested_date="2026-02-10",
        suggested_time="14:00"
    )

    print(f"  Result: {len(result)} workflows triggered")
    return len(result) > 0


def test_expense_workflow():
    """Test expense approval workflow"""
    print("Testing expense workflow...")

    result = trigger_expense_recorded(
        name="Test large expense",
        amount=750.00
    )

    print(f"  Result: {len(result)} workflows triggered")
    return len(result) > 0


def test_morning_workflow():
    """Test morning routine"""
    print("Testing morning routine...")

    result = trigger_morning_routine(pending_count=5)

    print(f"  Result: {len(result)} workflows triggered")
    return len(result) > 0


def main():
    """Run all tests"""
    print("=" * 60)
    print("WORKFLOW INTEGRATION TESTS")
    print("=" * 60)
    print()

    tests = [
        ("Invoice → Email", test_invoice_workflow),
        ("Email → Calendar", test_email_workflow),
        ("Expense Approval", test_expense_workflow),
        ("Morning Routine", test_morning_workflow)
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
            print()
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((name, False))
            print()

    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    print()
    passed_count = sum(1 for _, p in results if p)
    print(f"Total: {passed_count}/{len(results)} tests passed")

    print()
    print("Check these folders for results:")
    print("  - Inbox/ (notifications)")
    print("  - Pending_Approval/ (approval requests)")
    print("  - Logs/integrations.log (execution logs)")


if __name__ == "__main__":
    main()
```

Run tests:

```bash
cd /mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/integrations
python3 test_workflows.py
```

---

## Production Deployment

### 1. Start Orchestrator Service

**Option A: PM2**

```bash
# Note: Orchestrator is event-driven, runs when triggered
# No need for standalone service unless you want monitoring

# If you want continuous monitoring:
pm2 start /mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/integrations/scheduler.py --interpreter python3 --name workflow-scheduler

pm2 start /mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/integrations/approval_watcher.py --interpreter python3 --name approval-watcher

pm2 save
```

**Option B: Systemd Service**

Create `/etc/systemd/system/workflow-scheduler.service`:

```ini
[Unit]
Description=Workflow Scheduler
After=network.target

[Service]
Type=simple
User=maryam
WorkingDirectory=/mnt/f/Maryam/Quarter_4/Ai_Employee_Vault
ExecStart=/usr/bin/python3 /mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/integrations/scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable workflow-scheduler
sudo systemctl start workflow-scheduler
sudo systemctl status workflow-scheduler
```

### 2. Integration Checklist

- [ ] Gmail watcher triggers email workflows
- [ ] Odoo MCP triggers invoice/expense workflows
- [ ] Filesystem watcher triggers file workflows
- [ ] Approval watcher monitors approvals
- [ ] Scheduler runs time-based workflows
- [ ] All workflows logged to audit trail

### 3. Monitoring

**Check logs:**

```bash
# Orchestrator logs
tail -f /mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/Logs/integrations.log

# Audit logs
tail -f /mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/Logs/audit/*.json
```

**Check workflow stats:**

```python
from integrations.orchestrator import WorkflowOrchestrator

orch = WorkflowOrchestrator("/mnt/f/Maryam/Quarter_4/Ai_Employee_Vault")

for wf_id, wf in orch.workflows.items():
    print(f"{wf.name}: {wf.execution_count} executions")
```

---

## Summary

Integration points:

1. **Gmail Watcher** → `trigger_email_received()`
2. **Odoo MCP** → `trigger_invoice_created()`, `trigger_expense_recorded()`
3. **File System** → `trigger_file_added()`
4. **Scheduler** → `trigger_morning_routine()`, custom schedules
5. **Approvals** → `trigger_approval_received()`

All integrations use the simple helper functions for clean, maintainable code.
