#!/usr/bin/env python3
"""
Integration Helper - Simple interface for triggering workflows

Makes it easy for other scripts (watchers, hooks, etc.) to trigger workflows.

Usage:
    from integrations.integration_helper import trigger_invoice_created, trigger_email_received

    # Trigger invoice workflow
    trigger_invoice_created(
        invoice_number="INV-001",
        customer_id=7,
        amount=5000.00,
        customer_email="customer@example.com"
    )
"""

import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from integrations.orchestrator import WorkflowOrchestrator, Event, EventType


# Global orchestrator instance
VAULT_PATH = "/mnt/f/Maryam/Quarter_4/Ai_Employee_Vault"
_orchestrator = None


def get_orchestrator():
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = WorkflowOrchestrator(VAULT_PATH)
    return _orchestrator


def trigger_invoice_created(invoice_number: str, customer_id: int, amount: float,
                           customer_email: str = None, items: list = None):
    """
    Trigger invoice creation workflow.

    Args:
        invoice_number: Invoice ID
        customer_id: Odoo customer ID
        amount: Total invoice amount
        customer_email: Customer email address
        items: List of invoice line items
    """
    orchestrator = get_orchestrator()

    event = Event(
        event_type=EventType.INVOICE_CREATED,
        source="odoo_mcp",
        data={
            "invoice_number": invoice_number,
            "customer_id": customer_id,
            "amount": amount,
            "customer_email": customer_email,
            "items": items or []
        },
        timestamp=datetime.now().isoformat(),
        event_id=f"invoice_{uuid.uuid4().hex[:8]}"
    )

    return orchestrator.process_event(event)


def trigger_email_received(subject: str, sender: str, body: str,
                          suggested_date: str = None, suggested_time: str = None):
    """
    Trigger email received workflow.

    Args:
        subject: Email subject
        sender: Sender email address
        body: Email body content
        suggested_date: Suggested meeting date (if meeting email)
        suggested_time: Suggested meeting time (if meeting email)
    """
    orchestrator = get_orchestrator()

    event = Event(
        event_type=EventType.EMAIL_RECEIVED,
        source="gmail_watcher",
        data={
            "subject": subject,
            "sender": sender,
            "body": body,
            "suggested_date": suggested_date,
            "suggested_time": suggested_time,
            "received_at": datetime.now().isoformat()
        },
        timestamp=datetime.now().isoformat(),
        event_id=f"email_{uuid.uuid4().hex[:8]}"
    )

    return orchestrator.process_event(event)


def trigger_expense_recorded(name: str, amount: float, date: str = None):
    """
    Trigger expense recorded workflow.

    Args:
        name: Expense description
        amount: Expense amount
        date: Expense date
    """
    orchestrator = get_orchestrator()

    event = Event(
        event_type=EventType.EXPENSE_RECORDED,
        source="odoo_mcp",
        data={
            "name": name,
            "amount": amount,
            "date": date or datetime.now().strftime("%Y-%m-%d")
        },
        timestamp=datetime.now().isoformat(),
        event_id=f"expense_{uuid.uuid4().hex[:8]}"
    )

    return orchestrator.process_event(event)


def trigger_linkedin_post_scheduled(post_content: str, image_path: str = None):
    """
    Trigger LinkedIn post workflow.

    Args:
        post_content: Post text content
        image_path: Optional image path
    """
    orchestrator = get_orchestrator()

    event = Event(
        event_type=EventType.CALENDAR_EVENT,
        source="calendar",
        data={
            "event_type": "linkedin_post",
            "post_content": post_content,
            "image_path": image_path
        },
        timestamp=datetime.now().isoformat(),
        event_id=f"linkedin_{uuid.uuid4().hex[:8]}"
    )

    return orchestrator.process_event(event)


def trigger_morning_routine(pending_count: int = 0):
    """
    Trigger morning automation routine.

    Args:
        pending_count: Number of pending approvals
    """
    orchestrator = get_orchestrator()

    event = Event(
        event_type=EventType.SCHEDULED_TRIGGER,
        source="scheduler",
        data={
            "trigger_time": "08:00",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "pending_count": pending_count
        },
        timestamp=datetime.now().isoformat(),
        event_id=f"morning_{datetime.now().strftime('%Y%m%d')}"
    )

    return orchestrator.process_event(event)


def trigger_file_added(file_path: str, file_type: str):
    """
    Trigger file added workflow.

    Args:
        file_path: Path to added file
        file_type: Type of file (email, invoice, etc.)
    """
    orchestrator = get_orchestrator()

    event = Event(
        event_type=EventType.FILE_ADDED,
        source="filesystem_watcher",
        data={
            "file_path": file_path,
            "file_type": file_type,
            "added_at": datetime.now().isoformat()
        },
        timestamp=datetime.now().isoformat(),
        event_id=f"file_{uuid.uuid4().hex[:8]}"
    )

    return orchestrator.process_event(event)


def trigger_approval_received(approval_type: str, approved: bool, details: dict = None):
    """
    Trigger approval workflow.

    Args:
        approval_type: Type of approval (invoice, expense, email, etc.)
        approved: Whether approved or rejected
        details: Additional approval details
    """
    orchestrator = get_orchestrator()

    event = Event(
        event_type=EventType.APPROVAL_RECEIVED,
        source="human",
        data={
            "approval_type": approval_type,
            "approved": approved,
            "details": details or {},
            "approved_at": datetime.now().isoformat()
        },
        timestamp=datetime.now().isoformat(),
        event_id=f"approval_{uuid.uuid4().hex[:8]}"
    )

    return orchestrator.process_event(event)


# Example usage
if __name__ == "__main__":
    print("Integration Helper Examples\n")

    # Example 1: Invoice created
    print("1. Triggering invoice creation workflow...")
    result = trigger_invoice_created(
        invoice_number="INV-2026-001",
        customer_id=7,
        amount=5000.00,
        customer_email="customer@example.com",
        items=[
            {"name": "Consulting", "quantity": 10, "price": 150},
            {"name": "Development", "quantity": 20, "price": 200}
        ]
    )
    print(f"   Executed {len(result)} workflows\n")

    # Example 2: Email with meeting
    print("2. Triggering email received workflow...")
    result = trigger_email_received(
        subject="Meeting next week",
        sender="colleague@company.com",
        body="Let's schedule a meeting for next Tuesday at 2pm",
        suggested_date="2026-02-16",
        suggested_time="14:00"
    )
    print(f"   Executed {len(result)} workflows\n")

    # Example 3: Large expense
    print("3. Triggering expense workflow...")
    result = trigger_expense_recorded(
        name="New laptop",
        amount=1500.00
    )
    print(f"   Executed {len(result)} workflows\n")

    # Example 4: Morning routine
    print("4. Triggering morning routine...")
    result = trigger_morning_routine(pending_count=3)
    print(f"   Executed {len(result)} workflows\n")

    print("Done! Check Inbox and Pending_Approval folders for results.")
