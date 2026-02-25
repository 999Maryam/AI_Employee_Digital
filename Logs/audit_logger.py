#!/usr/bin/env python3
"""
Enhanced Audit Logger for AI Employee

Provides enterprise-grade audit logging with:
- Structured JSON logs
- 90-day retention
- Searchable by all fields
- Automatic cleanup
- Security event tracking

Gold Tier Feature #3
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import hashlib

# Configuration
VAULT_PATH = Path(__file__).parent.parent  # AI_Employee_Vault root
AUDIT_DIR = Path(__file__).parent / "audit"
RETENTION_DAYS = 90
SCHEMA_FILE = AUDIT_DIR / "audit_schema.json"


class AuditLogger:
    """Enhanced audit logging system with structured data and retention."""

    def __init__(self, actor: str = "AI_Employee"):
        """
        Initialize audit logger.

        Args:
            actor: Who is performing the action (e.g., "AI_Employee", "User", "System")
        """
        self.actor = actor
        self.session_id = self._generate_session_id()

        # Ensure audit directory exists
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)

        # Initialize schema if it doesn't exist
        if not SCHEMA_FILE.exists():
            self._initialize_schema()

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.sha256(f"{self.actor}_{timestamp}".encode()).hexdigest()[:16]

    def _initialize_schema(self):
        """Create audit log schema definition."""
        schema = {
            "version": "1.0",
            "description": "Audit log schema for AI Employee",
            "retention_days": RETENTION_DAYS,
            "fields": {
                "timestamp": {
                    "type": "string",
                    "format": "ISO8601",
                    "description": "When the action occurred",
                    "required": True
                },
                "session_id": {
                    "type": "string",
                    "description": "Session identifier for grouping related actions",
                    "required": True
                },
                "actor": {
                    "type": "string",
                    "description": "Who performed the action",
                    "required": True,
                    "examples": ["AI_Employee", "User", "System", "MCP_Server"]
                },
                "action": {
                    "type": "string",
                    "description": "What action was performed",
                    "required": True,
                    "examples": [
                        "create_file", "modify_file", "delete_file",
                        "send_email", "post_linkedin", "execute_command",
                        "approve_action", "reject_action", "authenticate"
                    ]
                },
                "target": {
                    "type": "string",
                    "description": "What was acted upon",
                    "required": True,
                    "examples": ["file:Reports/briefing.md", "email:user@domain.com", "post:linkedin:123"]
                },
                "status": {
                    "type": "string",
                    "description": "Result of the action",
                    "required": True,
                    "enum": ["success", "failure", "pending", "skipped"]
                },
                "approval_status": {
                    "type": "string",
                    "description": "Approval workflow status",
                    "required": False,
                    "enum": ["approved", "rejected", "pending", "not_required"]
                },
                "details": {
                    "type": "object",
                    "description": "Additional context about the action",
                    "required": False
                },
                "error": {
                    "type": "string",
                    "description": "Error message if status is failure",
                    "required": False
                },
                "duration_ms": {
                    "type": "integer",
                    "description": "How long the action took in milliseconds",
                    "required": False
                },
                "security_level": {
                    "type": "string",
                    "description": "Security classification of the action",
                    "required": False,
                    "enum": ["public", "internal", "confidential", "restricted"]
                }
            }
        }

        with open(SCHEMA_FILE, 'w') as f:
            json.dump(schema, f, indent=2)

    def log(
        self,
        action: str,
        target: str,
        status: str,
        approval_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration_ms: Optional[int] = None,
        security_level: str = "internal"
    ) -> str:
        """
        Log an action to the audit trail.

        Args:
            action: Action performed (e.g., "create_file", "post_linkedin")
            target: What was acted upon (e.g., "file:Reports/briefing.md")
            status: Result (success, failure, pending, skipped)
            approval_status: Approval state (approved, rejected, pending, not_required)
            details: Additional context dictionary
            error: Error message if status is failure
            duration_ms: How long the action took
            security_level: Security classification

        Returns:
            Path to the log entry file
        """
        timestamp = datetime.now()
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "session_id": self.session_id,
            "actor": self.actor,
            "action": action,
            "target": target,
            "status": status,
            "approval_status": approval_status or "not_required",
            "details": details or {},
            "error": error,
            "duration_ms": duration_ms,
            "security_level": security_level
        }

        # Generate log filename (YYYY-MM-DD_HH-MM-SS_action.json)
        filename = f"{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}_{action}.json"
        log_path = AUDIT_DIR / filename

        # Write log entry
        with open(log_path, 'w') as f:
            json.dump(log_entry, f, indent=2)

        return str(log_path)

    def log_file_operation(
        self,
        operation: str,
        filepath: str,
        status: str,
        details: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """Log file create/read/write/delete operations."""
        return self.log(
            action=f"file_{operation}",
            target=f"file:{filepath}",
            status=status,
            details=details,
            error=error
        )

    def log_external_action(
        self,
        service: str,
        action: str,
        target_id: str,
        status: str,
        approval_status: str,
        details: Optional[Dict] = None,
        error: Optional[str] = None,
        duration_ms: Optional[int] = None
    ):
        """Log external API calls (LinkedIn, email, etc.)."""
        return self.log(
            action=f"{service}_{action}",
            target=f"{service}:{target_id}",
            status=status,
            approval_status=approval_status,
            details=details,
            error=error,
            duration_ms=duration_ms,
            security_level="confidential"  # External actions are sensitive
        )

    def log_approval(
        self,
        action_type: str,
        action_id: str,
        decision: str,
        approver: str,
        reason: Optional[str] = None
    ):
        """Log approval/rejection decisions."""
        return self.log(
            action=f"approval_{decision}",
            target=f"action:{action_type}:{action_id}",
            status="success",
            approval_status=decision,
            details={
                "approver": approver,
                "reason": reason,
                "original_action": action_type
            }
        )

    def log_security_event(
        self,
        event_type: str,
        target: str,
        status: str,
        details: Optional[Dict] = None
    ):
        """Log security-related events."""
        return self.log(
            action=f"security_{event_type}",
            target=target,
            status=status,
            details=details,
            security_level="restricted"
        )

    def cleanup_old_logs(self, retention_days: int = RETENTION_DAYS):
        """
        Remove audit logs older than retention period.

        Args:
            retention_days: How many days to keep logs (default: 90)
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0

        for log_file in AUDIT_DIR.glob("*.json"):
            # Skip schema file
            if log_file.name == "audit_schema.json":
                continue

            # Check file modification time
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_time < cutoff_date:
                log_file.unlink()
                deleted_count += 1

        return deleted_count

    def get_recent_logs(self, hours: int = 24) -> List[Dict]:
        """
        Get recent audit logs.

        Args:
            hours: How many hours back to retrieve

        Returns:
            List of log entries
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_logs = []

        for log_file in sorted(AUDIT_DIR.glob("*.json")):
            if log_file.name == "audit_schema.json":
                continue

            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_time >= cutoff_time:
                with open(log_file, 'r') as f:
                    recent_logs.append(json.load(f))

        return recent_logs

    def search_logs(
        self,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        target: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Search audit logs by criteria.

        Args:
            actor: Filter by actor
            action: Filter by action type
            target: Filter by target (supports wildcards)
            status: Filter by status
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of matching log entries
        """
        matching_logs = []

        for log_file in AUDIT_DIR.glob("*.json"):
            if log_file.name == "audit_schema.json":
                continue

            with open(log_file, 'r') as f:
                log_entry = json.load(f)

            # Apply filters
            if actor and log_entry.get("actor") != actor:
                continue

            if action and not log_entry.get("action", "").startswith(action):
                continue

            if target and target not in log_entry.get("target", ""):
                continue

            if status and log_entry.get("status") != status:
                continue

            # Date range filtering
            log_time = datetime.fromisoformat(log_entry["timestamp"])
            if start_date and log_time < start_date:
                continue
            if end_date and log_time > end_date:
                continue

            matching_logs.append(log_entry)

        return sorted(matching_logs, key=lambda x: x["timestamp"], reverse=True)


# Convenience function for quick logging
def audit_log(action: str, target: str, status: str, **kwargs):
    """Quick audit log function."""
    logger = AuditLogger()
    return logger.log(action, target, status, **kwargs)


# Example usage
if __name__ == "__main__":
    # Demo the audit logger
    logger = AuditLogger(actor="AI_Employee")

    # Log some example actions
    logger.log_file_operation("create", "Reports/CEO_Briefing.md", "success")

    logger.log_external_action(
        service="linkedin",
        action="post",
        target_id="123456",
        status="success",
        approval_status="approved",
        duration_ms=1250
    )

    logger.log_approval(
        action_type="linkedin_post",
        action_id="post_123",
        decision="approved",
        approver="User"
    )

    # Get recent logs
    recent = logger.get_recent_logs(hours=24)
    print(f"Found {len(recent)} logs in last 24 hours")

    # Search logs
    linkedin_actions = logger.search_logs(action="linkedin")
    print(f"Found {len(linkedin_actions)} LinkedIn actions")
