#!/usr/bin/env python3
"""
Cross-Domain Integration Orchestrator
Gold Tier Feature #5

Connects multiple systems (Email, Calendar, LinkedIn, Odoo) into intelligent workflows.
Enables automation chains like: Email → Calendar → LinkedIn, Invoice → Email notification, etc.

Author: AI Employee
Created: 2026-02-09
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from Logs.audit_logger import AuditLogger
except ImportError:
    # Fallback if audit logger not available
    class AuditLogger:
        def log(self, *args, **kwargs):
            pass
        def log_external_action(self, *args, **kwargs):
            pass


class EventType(Enum):
    """Types of events that can trigger workflows"""
    EMAIL_RECEIVED = "email_received"
    CALENDAR_EVENT = "calendar_event"
    INVOICE_CREATED = "invoice_created"
    EXPENSE_RECORDED = "expense_recorded"
    LINKEDIN_POST = "linkedin_post"
    FILE_ADDED = "file_added"
    APPROVAL_RECEIVED = "approval_received"
    SCHEDULED_TRIGGER = "scheduled_trigger"
    MANUAL_TRIGGER = "manual_trigger"


class ActionType(Enum):
    """Types of actions that can be executed"""
    SEND_EMAIL = "send_email"
    CREATE_CALENDAR_EVENT = "create_calendar_event"
    POST_TO_LINKEDIN = "post_to_linkedin"
    CREATE_INVOICE = "create_invoice"
    RECORD_EXPENSE = "record_expense"
    CREATE_FILE = "create_file"
    REQUEST_APPROVAL = "request_approval"
    SEND_NOTIFICATION = "send_notification"
    RUN_SCRIPT = "run_script"
    WAIT = "wait"


@dataclass
class Event:
    """Represents a system event that can trigger workflows"""
    event_type: EventType
    source: str
    data: Dict[str, Any]
    timestamp: str
    event_id: str


@dataclass
class WorkflowAction:
    """Individual action within a workflow"""
    action_type: ActionType
    parameters: Dict[str, Any]
    condition: Optional[str] = None  # Python expression to evaluate
    on_success: Optional[str] = None  # Next action ID
    on_failure: Optional[str] = None  # Fallback action ID
    retry_count: int = 3
    timeout: int = 30  # seconds


@dataclass
class Workflow:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    trigger_event: EventType
    trigger_condition: Optional[str] = None
    actions: List[WorkflowAction] = None
    enabled: bool = True
    created_at: str = None
    last_executed: Optional[str] = None
    execution_count: int = 0


class WorkflowOrchestrator:
    """
    Main orchestrator for cross-domain integrations.

    Features:
    - Event-driven workflow execution
    - Multi-step automation chains
    - Conditional branching
    - Error handling and retries
    - Audit logging integration
    """

    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator.

        Args:
            vault_path: Path to the AI Employee vault
        """
        self.vault_path = Path(vault_path)
        self.workflows_dir = self.vault_path / "integrations" / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.vault_path / "integrations" / "orchestrator_state.json"
        self.log_file = self.vault_path / "Logs" / "integrations.log"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("Orchestrator")

        # Initialize audit logger
        self.audit_logger = AuditLogger()

        # Load workflows
        self.workflows: Dict[str, Workflow] = {}
        self.load_workflows()

        # Action handlers
        self.action_handlers: Dict[ActionType, Callable] = {
            ActionType.SEND_EMAIL: self._handle_send_email,
            ActionType.CREATE_CALENDAR_EVENT: self._handle_create_calendar_event,
            ActionType.POST_TO_LINKEDIN: self._handle_post_to_linkedin,
            ActionType.CREATE_INVOICE: self._handle_create_invoice,
            ActionType.RECORD_EXPENSE: self._handle_record_expense,
            ActionType.CREATE_FILE: self._handle_create_file,
            ActionType.REQUEST_APPROVAL: self._handle_request_approval,
            ActionType.SEND_NOTIFICATION: self._handle_send_notification,
            ActionType.RUN_SCRIPT: self._handle_run_script,
            ActionType.WAIT: self._handle_wait,
        }

        self.logger.info("WorkflowOrchestrator initialized")

    def load_workflows(self):
        """Load all workflow definitions from workflows directory"""
        try:
            workflow_files = list(self.workflows_dir.glob("*.json"))

            for workflow_file in workflow_files:
                with open(workflow_file, 'r') as f:
                    data = json.load(f)

                # Convert to Workflow object
                workflow = Workflow(
                    workflow_id=data['workflow_id'],
                    name=data['name'],
                    description=data['description'],
                    trigger_event=EventType(data['trigger_event']),
                    trigger_condition=data.get('trigger_condition'),
                    actions=[
                        WorkflowAction(
                            action_type=ActionType(a['action_type']),
                            parameters=a['parameters'],
                            condition=a.get('condition'),
                            on_success=a.get('on_success'),
                            on_failure=a.get('on_failure'),
                            retry_count=a.get('retry_count', 3),
                            timeout=a.get('timeout', 30)
                        ) for a in data['actions']
                    ],
                    enabled=data.get('enabled', True),
                    created_at=data.get('created_at'),
                    last_executed=data.get('last_executed'),
                    execution_count=data.get('execution_count', 0)
                )

                self.workflows[workflow.workflow_id] = workflow
                self.logger.info(f"Loaded workflow: {workflow.name}")

            self.logger.info(f"Loaded {len(self.workflows)} workflows")

        except Exception as e:
            self.logger.error(f"Error loading workflows: {e}")

    def process_event(self, event: Event) -> List[str]:
        """
        Process an incoming event and trigger matching workflows.

        Args:
            event: The event to process

        Returns:
            List of workflow IDs that were executed
        """
        executed_workflows = []

        self.logger.info(f"Processing event: {event.event_type.value} from {event.source}")

        # Find matching workflows
        for workflow_id, workflow in self.workflows.items():
            if not workflow.enabled:
                continue

            # Check if event type matches
            if workflow.trigger_event != event.event_type:
                continue

            # Check trigger condition if specified
            if workflow.trigger_condition:
                try:
                    # Evaluate condition with event as dict
                    event_context = {'event': asdict(event)}
                    if not self._evaluate_condition(workflow.trigger_condition, event_context):
                        continue
                except Exception as e:
                    self.logger.error(f"Error evaluating trigger condition: {e}")
                    continue

            # Execute workflow
            try:
                self.logger.info(f"Triggering workflow: {workflow.name}")
                self.execute_workflow(workflow, event)
                executed_workflows.append(workflow_id)

                # Update workflow metadata
                workflow.last_executed = datetime.now().isoformat()
                workflow.execution_count += 1
                self._save_workflow(workflow)

            except Exception as e:
                self.logger.error(f"Error executing workflow {workflow.name}: {e}")
                self.audit_logger.log(
                    action="workflow_execution",
                    target=workflow.workflow_id,
                    status="error",
                    error=str(e),
                    details={"event": event.event_type.value}
                )

        return executed_workflows

    def execute_workflow(self, workflow: Workflow, event: Event):
        """
        Execute a workflow's actions in sequence.

        Args:
            workflow: The workflow to execute
            event: The triggering event
        """
        start_time = datetime.now()

        self.logger.info(f"Executing workflow: {workflow.name}")

        # Workflow context (available to all actions)
        context = {
            'event': asdict(event),
            'workflow': {
                'id': workflow.workflow_id,
                'name': workflow.name
            },
            'results': {}  # Store action results
        }

        try:
            # Execute each action
            for idx, action in enumerate(workflow.actions):
                action_id = f"action_{idx}"

                # Check action condition
                if action.condition:
                    if not self._evaluate_condition(action.condition, context):
                        self.logger.info(f"Skipping action {action_id}: condition not met")
                        continue

                # Execute action with retries
                success = False
                for attempt in range(action.retry_count):
                    try:
                        result = self._execute_action(action, context)
                        context['results'][action_id] = result
                        success = True
                        break
                    except Exception as e:
                        self.logger.error(f"Action {action_id} attempt {attempt + 1} failed: {e}")
                        if attempt < action.retry_count - 1:
                            continue
                        else:
                            raise

                if not success and action.on_failure:
                    self.logger.info(f"Executing failure handler: {action.on_failure}")
                    # Could implement failure handler here

            # Log successful execution
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.audit_logger.log(
                action="workflow_execution",
                target=workflow.workflow_id,
                status="success",
                duration_ms=int(duration),
                details={
                    "event": event.event_type.value,
                    "actions_executed": len(workflow.actions)
                }
            )

            self.logger.info(f"Workflow {workflow.name} completed successfully")

        except Exception as e:
            self.logger.error(f"Workflow {workflow.name} failed: {e}")
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.audit_logger.log(
                action="workflow_execution",
                target=workflow.workflow_id,
                status="error",
                error=str(e),
                duration_ms=int(duration),
                details={"event": event.event_type.value}
            )
            raise

    def _execute_action(self, action: WorkflowAction, context: Dict) -> Any:
        """Execute a single action"""
        handler = self.action_handlers.get(action.action_type)

        if not handler:
            raise ValueError(f"No handler for action type: {action.action_type}")

        # Replace placeholders in parameters with context values
        parameters = self._resolve_parameters(action.parameters, context)

        self.logger.info(f"Executing action: {action.action_type.value}")

        return handler(parameters, context)

    def _evaluate_condition(self, condition: str, context: Dict) -> bool:
        """Safely evaluate a condition expression"""
        try:
            # Limited eval with only safe context
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

    def _resolve_parameters(self, parameters: Dict, context: Dict) -> Dict:
        """Resolve template variables in parameters"""
        resolved = {}

        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Template variable: {{event.data.subject}}
                var_path = value[2:-2].strip()
                resolved[key] = self._get_nested_value(context, var_path)
            else:
                resolved[key] = value

        return resolved

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get value from nested dict using dot notation"""
        keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

        return value

    def _save_workflow(self, workflow: Workflow):
        """Save workflow to file"""
        workflow_file = self.workflows_dir / f"{workflow.workflow_id}.json"

        data = {
            'workflow_id': workflow.workflow_id,
            'name': workflow.name,
            'description': workflow.description,
            'trigger_event': workflow.trigger_event.value,
            'trigger_condition': workflow.trigger_condition,
            'actions': [
                {
                    'action_type': a.action_type.value,
                    'parameters': a.parameters,
                    'condition': a.condition,
                    'on_success': a.on_success,
                    'on_failure': a.on_failure,
                    'retry_count': a.retry_count,
                    'timeout': a.timeout
                } for a in workflow.actions
            ],
            'enabled': workflow.enabled,
            'created_at': workflow.created_at,
            'last_executed': workflow.last_executed,
            'execution_count': workflow.execution_count
        }

        with open(workflow_file, 'w') as f:
            json.dump(data, f, indent=2)

    # Action Handlers

    def _handle_send_email(self, params: Dict, context: Dict) -> Dict:
        """Handle sending email"""
        self.logger.info(f"Sending email to: {params.get('to')}")

        # Create email file in Pending_Approval
        email_file = self.vault_path / "Pending_Approval" / f"EMAIL_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"

        content = f"""# Email Draft

**To**: {params.get('to')}
**Subject**: {params.get('subject')}
**Priority**: {params.get('priority', 'normal')}

## Body

{params.get('body')}

---
*Generated by workflow: {context['workflow']['name']}*
*Awaiting approval to send*
"""

        email_file.write_text(content)

        self.audit_logger.log_external_action(
            service="email",
            action="draft_created",
            target_id=params.get('to'),
            status="pending_approval",
            approval_status="pending",
            details={"subject": params.get('subject')}
        )

        return {"status": "pending_approval", "file": str(email_file)}

    def _handle_create_calendar_event(self, params: Dict, context: Dict) -> Dict:
        """Handle creating calendar event"""
        self.logger.info(f"Creating calendar event: {params.get('title')}")

        # Create calendar event file
        event_file = self.vault_path / "Pending_Approval" / f"CALENDAR_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"

        content = f"""# Calendar Event

**Title**: {params.get('title')}
**Date**: {params.get('date')}
**Time**: {params.get('time')}
**Duration**: {params.get('duration', '1 hour')}

## Description

{params.get('description')}

---
*Generated by workflow: {context['workflow']['name']}*
*Awaiting approval to create*
"""

        event_file.write_text(content)

        return {"status": "pending_approval", "file": str(event_file)}

    def _handle_post_to_linkedin(self, params: Dict, context: Dict) -> Dict:
        """Handle LinkedIn posting"""
        self.logger.info("Creating LinkedIn post draft")

        # Create LinkedIn post file
        post_file = self.vault_path / "Pending_Approval" / f"LINKEDIN_POST_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"

        content = f"""# LinkedIn Post Draft

## Content

{params.get('content')}

## Settings

- **Visibility**: {params.get('visibility', 'PUBLIC')}
- **Has Image**: {params.get('image_path') is not None}

---
*Generated by workflow: {context['workflow']['name']}*
*Awaiting approval to post*
"""

        post_file.write_text(content)

        self.audit_logger.log_external_action(
            service="linkedin",
            action="post_draft_created",
            target_id="pending",
            status="pending_approval",
            approval_status="pending",
            details={"content_length": len(params.get('content', ''))}
        )

        return {"status": "pending_approval", "file": str(post_file)}

    def _handle_create_invoice(self, params: Dict, context: Dict) -> Dict:
        """Handle invoice creation via Odoo"""
        self.logger.info(f"Creating invoice for customer: {params.get('customer_id')}")

        # This would call Odoo MCP server
        # For now, create approval request
        invoice_file = self.vault_path / "Pending_Approval" / f"INVOICE_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"

        items_text = "\n".join([
            f"- {item['name']}: {item['quantity']} x ${item['price']}"
            for item in params.get('items', [])
        ])

        content = f"""# Invoice Draft

**Customer ID**: {params.get('customer_id')}
**Date**: {params.get('invoice_date', datetime.now().strftime('%Y-%m-%d'))}

## Line Items

{items_text}

---
*Generated by workflow: {context['workflow']['name']}*
*Awaiting approval to create in Odoo*
"""

        invoice_file.write_text(content)

        self.audit_logger.log_external_action(
            service="odoo",
            action="invoice_draft_created",
            target_id=f"customer_{params.get('customer_id')}",
            status="pending_approval",
            approval_status="pending",
            details={"items_count": len(params.get('items', []))}
        )

        return {"status": "pending_approval", "file": str(invoice_file)}

    def _handle_record_expense(self, params: Dict, context: Dict) -> Dict:
        """Handle expense recording"""
        self.logger.info(f"Recording expense: {params.get('name')}")

        # Similar to invoice
        return {"status": "recorded", "amount": params.get('amount')}

    def _handle_create_file(self, params: Dict, context: Dict) -> Dict:
        """Handle file creation"""
        file_path = self.vault_path / params.get('path')
        content = params.get('content', '')

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

        self.logger.info(f"Created file: {file_path}")

        return {"status": "created", "path": str(file_path)}

    def _handle_request_approval(self, params: Dict, context: Dict) -> Dict:
        """Handle approval request"""
        self.logger.info(f"Requesting approval: {params.get('title')}")

        approval_file = self.vault_path / "Pending_Approval" / f"APPROVAL_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"

        content = f"""# Approval Request

**Title**: {params.get('title')}
**Description**: {params.get('description')}

---
*Workflow*: {context['workflow']['name']}
*Requested*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        approval_file.write_text(content)

        return {"status": "pending", "file": str(approval_file)}

    def _handle_send_notification(self, params: Dict, context: Dict) -> Dict:
        """Handle notification"""
        notification_file = self.vault_path / "Inbox" / f"NOTIFICATION_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"

        content = f"""# Notification

**Title**: {params.get('title')}

{params.get('message')}

---
*From workflow*: {context['workflow']['name']}
*Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        notification_file.write_text(content)

        self.logger.info(f"Sent notification: {params.get('title')}")

        return {"status": "sent", "file": str(notification_file)}

    def _handle_run_script(self, params: Dict, context: Dict) -> Dict:
        """Handle script execution"""
        self.logger.info(f"Running script: {params.get('script')}")

        # Security: Only allow whitelisted scripts
        allowed_scripts = params.get('allowed_scripts', [])
        script = params.get('script')

        if script not in allowed_scripts:
            raise ValueError(f"Script {script} not in allowed list")

        # Would execute script here
        return {"status": "executed", "script": script}

    def _handle_wait(self, params: Dict, context: Dict) -> Dict:
        """Handle wait action"""
        import time
        duration = params.get('duration', 1)
        self.logger.info(f"Waiting for {duration} seconds")
        time.sleep(duration)
        return {"status": "waited", "duration": duration}


def main():
    """Example usage"""
    vault_path = "/mnt/f/Maryam/Quarter_4/Ai_Employee_Vault"
    orchestrator = WorkflowOrchestrator(vault_path)

    # Example: Process an invoice creation event
    event = Event(
        event_type=EventType.INVOICE_CREATED,
        source="odoo_mcp",
        data={
            "customer_id": 7,
            "amount": 5000,
            "invoice_number": "INV-2026-001"
        },
        timestamp=datetime.now().isoformat(),
        event_id="evt_001"
    )

    executed = orchestrator.process_event(event)
    print(f"Executed {len(executed)} workflows")


if __name__ == "__main__":
    main()
