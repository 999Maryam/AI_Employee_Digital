#!/usr/bin/env python3
"""
Audit Log Analyzer

Analyzes audit logs to generate insights, detect patterns, and identify issues.

Features:
- Success rate analysis
- Performance metrics
- Security event detection
- Approval workflow analysis
- Trend identification

Gold Tier Feature #3
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any
import statistics


AUDIT_DIR = Path(__file__).parent / "audit"


class LogAnalyzer:
    """Analyze audit logs for insights and patterns."""

    def __init__(self):
        self.logs = self._load_all_logs()

    def _load_all_logs(self) -> List[Dict]:
        """Load all audit logs from the audit directory."""
        logs = []
        if not AUDIT_DIR.exists():
            return logs

        for log_file in AUDIT_DIR.glob("*.json"):
            if log_file.name == "audit_schema.json":
                continue

            try:
                with open(log_file, 'r') as f:
                    logs.append(json.load(f))
            except Exception as e:
                print(f"Error loading {log_file}: {e}")

        return sorted(logs, key=lambda x: x["timestamp"])

    def generate_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Generate comprehensive summary of audit logs.

        Args:
            hours: Time window to analyze

        Returns:
            Dictionary with summary statistics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_logs = [
            log for log in self.logs
            if datetime.fromisoformat(log["timestamp"]) >= cutoff_time
        ]

        if not recent_logs:
            return {"message": "No logs in specified time period"}

        # Calculate statistics
        total_actions = len(recent_logs)
        success_count = sum(1 for log in recent_logs if log["status"] == "success")
        failure_count = sum(1 for log in recent_logs if log["status"] == "failure")
        pending_count = sum(1 for log in recent_logs if log["status"] == "pending")

        # Action type breakdown
        action_counts = Counter(log["action"] for log in recent_logs)

        # Actor breakdown
        actor_counts = Counter(log["actor"] for log in recent_logs)

        # Approval workflow stats
        approval_stats = {
            "approved": sum(1 for log in recent_logs if log.get("approval_status") == "approved"),
            "rejected": sum(1 for log in recent_logs if log.get("approval_status") == "rejected"),
            "pending": sum(1 for log in recent_logs if log.get("approval_status") == "pending"),
            "not_required": sum(1 for log in recent_logs if log.get("approval_status") == "not_required")
        }

        # Performance metrics (if duration_ms available)
        durations = [log.get("duration_ms") for log in recent_logs if log.get("duration_ms")]
        perf_stats = {}
        if durations:
            perf_stats = {
                "avg_duration_ms": statistics.mean(durations),
                "median_duration_ms": statistics.median(durations),
                "max_duration_ms": max(durations),
                "min_duration_ms": min(durations)
            }

        # Security level breakdown
        security_counts = Counter(log.get("security_level", "unknown") for log in recent_logs)

        return {
            "period": f"Last {hours} hours",
            "total_actions": total_actions,
            "success_rate": f"{(success_count/total_actions*100):.1f}%" if total_actions > 0 else "N/A",
            "status_breakdown": {
                "success": success_count,
                "failure": failure_count,
                "pending": pending_count
            },
            "actions": dict(action_counts.most_common(10)),
            "actors": dict(actor_counts),
            "approval_workflow": approval_stats,
            "performance": perf_stats,
            "security_levels": dict(security_counts),
            "time_range": {
                "start": recent_logs[0]["timestamp"] if recent_logs else None,
                "end": recent_logs[-1]["timestamp"] if recent_logs else None
            }
        }

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect unusual patterns or security issues."""
        anomalies = []

        # Check for unusual failure rates
        recent_logs = self._get_recent_logs(hours=1)
        if len(recent_logs) > 10:
            failure_rate = sum(1 for log in recent_logs if log["status"] == "failure") / len(recent_logs)
            if failure_rate > 0.3:  # More than 30% failures
                anomalies.append({
                    "type": "high_failure_rate",
                    "severity": "warning",
                    "message": f"High failure rate detected: {failure_rate*100:.1f}%",
                    "recommendation": "Review recent errors and investigate root cause"
                })

        # Check for security events
        security_events = [log for log in recent_logs if log.get("action", "").startswith("security_")]
        if security_events:
            anomalies.append({
                "type": "security_events",
                "severity": "alert",
                "message": f"{len(security_events)} security events detected",
                "events": [{"action": log["action"], "time": log["timestamp"]} for log in security_events],
                "recommendation": "Review security events immediately"
            })

        # Check for rejected approvals
        recent_rejections = [
            log for log in recent_logs
            if log.get("approval_status") == "rejected"
        ]
        if recent_rejections:
            anomalies.append({
                "type": "rejected_approvals",
                "severity": "info",
                "message": f"{len(recent_rejections)} actions were rejected",
                "recommendation": "Review rejection reasons to improve autonomous decision-making"
            })

        # Check for slow operations
        slow_ops = [
            log for log in recent_logs
            if log.get("duration_ms") and log.get("duration_ms") > 5000  # Slower than 5 seconds
        ]
        if slow_ops:
            anomalies.append({
                "type": "slow_operations",
                "severity": "warning",
                "message": f"{len(slow_ops)} slow operations detected",
                "slowest": max(slow_ops, key=lambda x: x.get("duration_ms", 0))["action"],
                "recommendation": "Investigate performance bottlenecks"
            })

        return anomalies

    def _get_recent_logs(self, hours: int = 24) -> List[Dict]:
        """Get logs from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            log for log in self.logs
            if datetime.fromisoformat(log["timestamp"]) >= cutoff_time
        ]

    def generate_report(self, output_file: str = None) -> str:
        """
        Generate comprehensive analysis report.

        Args:
            output_file: Optional file path to save report

        Returns:
            Report as markdown string
        """
        summary_24h = self.generate_summary(hours=24)
        summary_7d = self.generate_summary(hours=168)  # 7 days
        anomalies = self.detect_anomalies()

        report = f"""# Audit Log Analysis Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Logs Analyzed**: {len(self.logs)}

---

## 24-Hour Summary

**Period**: Last 24 hours
**Total Actions**: {summary_24h.get('total_actions', 0)}
**Success Rate**: {summary_24h.get('success_rate', 'N/A')}

### Status Breakdown
- ✅ Success: {summary_24h.get('status_breakdown', {}).get('success', 0)}
- ❌ Failure: {summary_24h.get('status_breakdown', {}).get('failure', 0)}
- ⏳ Pending: {summary_24h.get('status_breakdown', {}).get('pending', 0)}

### Top Actions
"""

        # Add top actions
        for action, count in list(summary_24h.get('actions', {}).items())[:5]:
            report += f"- {action}: {count} times\n"

        report += f"""
### Approval Workflow
- ✅ Approved: {summary_24h.get('approval_workflow', {}).get('approved', 0)}
- ❌ Rejected: {summary_24h.get('approval_workflow', {}).get('rejected', 0)}
- ⏳ Pending: {summary_24h.get('approval_workflow', {}).get('pending', 0)}
- ➖ Not Required: {summary_24h.get('approval_workflow', {}).get('not_required', 0)}

"""

        # Performance metrics
        perf = summary_24h.get('performance', {})
        if perf:
            report += f"""### Performance Metrics
- Average Duration: {perf.get('avg_duration_ms', 0):.0f}ms
- Median Duration: {perf.get('median_duration_ms', 0):.0f}ms
- Fastest: {perf.get('min_duration_ms', 0):.0f}ms
- Slowest: {perf.get('max_duration_ms', 0):.0f}ms

"""

        # 7-day trends
        report += f"""---

## 7-Day Trends

**Total Actions**: {summary_7d.get('total_actions', 0)}
**Success Rate**: {summary_7d.get('success_rate', 'N/A')}

### Most Common Actions (7 days)
"""
        for action, count in list(summary_7d.get('actions', {}).items())[:10]:
            report += f"- {action}: {count} times\n"

        # Anomalies
        report += "\n---\n\n## Anomalies & Alerts\n\n"
        if anomalies:
            for anomaly in anomalies:
                severity_emoji = {
                    "alert": "🚨",
                    "warning": "⚠️",
                    "info": "ℹ️"
                }.get(anomaly["severity"], "•")

                report += f"### {severity_emoji} {anomaly['type'].replace('_', ' ').title()}\n"
                report += f"**Severity**: {anomaly['severity']}\n"
                report += f"**Message**: {anomaly['message']}\n"
                report += f"**Recommendation**: {anomaly['recommendation']}\n\n"
        else:
            report += "✅ No anomalies detected - all systems operating normally.\n\n"

        # Security summary
        security_levels = summary_24h.get('security_levels', {})
        report += f"""---

## Security Overview (24h)

**Confidential Actions**: {security_levels.get('confidential', 0)}
**Restricted Actions**: {security_levels.get('restricted', 0)}
**Internal Actions**: {security_levels.get('internal', 0)}
**Public Actions**: {security_levels.get('public', 0)}

"""

        # Recommendations
        report += """---

## Recommendations

"""
        if summary_24h.get('total_actions', 0) == 0:
            report += "- No activity detected - consider checking if watchers are running\n"
        elif summary_24h.get('status_breakdown', {}).get('failure', 0) > 0:
            report += f"- Investigate {summary_24h['status_breakdown']['failure']} failed actions\n"

        if summary_24h.get('approval_workflow', {}).get('pending', 0) > 0:
            report += f"- Review {summary_24h['approval_workflow']['pending']} pending approvals\n"

        report += "\n---\n\n"
        report += "*Report generated by Enhanced Audit Logging System (Gold Tier Feature #3)*\n"

        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)

        return report


def main():
    """Command-line interface for log analyzer."""
    import sys

    analyzer = LogAnalyzer()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "summary":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            summary = analyzer.generate_summary(hours=hours)
            print(json.dumps(summary, indent=2))

        elif command == "anomalies":
            anomalies = analyzer.detect_anomalies()
            print(json.dumps(anomalies, indent=2))

        elif command == "report":
            output_file = sys.argv[2] if len(sys.argv) > 2 else None
            report = analyzer.generate_report(output_file=output_file)
            print(report)

        else:
            print(f"Unknown command: {command}")
            print("Usage: python log_analyzer.py [summary|anomalies|report] [args...]")

    else:
        # Default: generate report
        report = analyzer.generate_report()
        print(report)


if __name__ == "__main__":
    main()
