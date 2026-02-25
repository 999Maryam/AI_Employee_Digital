#!/usr/bin/env python3
"""
Ralph Wiggum Autonomy Loop - Stop Hook for Claude Code

This hook prevents Claude from exiting prematurely by checking if the task is truly complete.
If the task is incomplete, it re-injecting the prompt with additional context to continue working.

Named after Ralph Wiggum: "I'm helping!" - Never gives up until the job is done.

Usage:
    Configure in Claude Code settings as a stop hook
    Hook runs before Claude exits each turn
    Checks completion criteria and decides whether to continue or allow exit

Gold Tier Feature: Core autonomy engine
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration
MAX_ITERATIONS = 10  # Safety limit to prevent infinite loops
VAULT_PATH = Path(__file__).parent.parent.parent  # AI_Employee_Vault root
ITERATION_LOG = VAULT_PATH / "Logs" / "autonomy_iterations.md"
CONFIG_FILE = VAULT_PATH / "Plans" / "autonomy_config.json"


def log_iteration(task_info, iteration, decision, reason):
    """Log autonomy loop iterations for debugging and audit."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
## Iteration {iteration} - {timestamp}
**Decision**: {decision}
**Reason**: {reason}
**Task**: {task_info.get('task', 'Unknown')}
**Context**: {task_info.get('context', 'N/A')}

---
"""

    # Append to log file
    with open(ITERATION_LOG, 'a', encoding='utf-8') as f:
        f.write(log_entry)


def load_config():
    """Load autonomy configuration."""
    if not CONFIG_FILE.exists():
        # Default configuration
        return {
            "enabled": True,
            "max_iterations": MAX_ITERATIONS,
            "strict_mode": False,
            "require_explicit_completion": True,
            "check_criteria": [
                "files_created",
                "tasks_completed",
                "explicit_done_statement"
            ]
        }

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_vault_changes(initial_state):
    """Check if meaningful changes were made to the vault."""
    changes = {
        "files_created": 0,
        "files_modified": 0,
        "folders_created": 0
    }

    # Check for new files in key directories
    key_dirs = ["Done", "Plans", "Reports", "Logs"]

    for dir_name in key_dirs:
        dir_path = VAULT_PATH / dir_name
        if dir_path.exists():
            files = list(dir_path.glob("*.md"))
            # Simple heuristic: count recent files (last hour)
            recent_files = [f for f in files if (datetime.now().timestamp() - f.stat().st_mtime) < 3600]
            changes["files_created"] += len(recent_files)

    return changes


def check_completion_indicators(last_message):
    """
    Check if the last message contains completion indicators.

    Returns: (is_complete, confidence, reason)
    """
    if not last_message:
        return False, 0.0, "No message to analyze"

    # Strong completion indicators
    strong_indicators = [
        "task complete",
        "all done",
        "finished successfully",
        "completed successfully",
        "✅ complete",
        "mission accomplished",
        "everything is done",
        "all tasks completed"
    ]

    # Weak completion indicators
    weak_indicators = [
        "done",
        "finished",
        "completed",
        "ready",
        "success"
    ]

    # Incompletion indicators (override completion)
    incomplete_indicators = [
        "error",
        "failed",
        "need to",
        "should do",
        "next step",
        "waiting for",
        "not yet",
        "still need",
        "TODO",
        "pending",
        "in progress"
    ]

    message_lower = last_message.lower()

    # Check for incompletion signals
    for indicator in incomplete_indicators:
        if indicator in message_lower:
            return False, 0.9, f"Incomplete indicator found: '{indicator}'"

    # Check for strong completion
    for indicator in strong_indicators:
        if indicator in message_lower:
            return True, 0.95, f"Strong completion indicator: '{indicator}'"

    # Check for weak completion (requires multiple)
    weak_count = sum(1 for indicator in weak_indicators if indicator in message_lower)
    if weak_count >= 2:
        return True, 0.7, f"Multiple weak indicators ({weak_count})"

    # Default: assume incomplete if no clear indicators
    return False, 0.5, "No clear completion indicators"


def check_needs_action_folder():
    """Check if there are pending tasks in Needs_Action folder."""
    needs_action_path = VAULT_PATH / "Needs_Action"
    if not needs_action_path.exists():
        return False, "Needs_Action folder doesn't exist"

    pending_files = list(needs_action_path.glob("*.md"))
    if pending_files:
        return False, f"{len(pending_files)} files still in Needs_Action"

    return True, "Needs_Action folder is empty"


def check_task_list():
    """Check if there are pending tasks in task list."""
    # This would integrate with Claude Code's task system
    # For now, we'll do a simple check

    # Check if Dashboard shows pending items
    dashboard_path = VAULT_PATH / "Dashboard.md"
    if dashboard_path.exists():
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for pending action indicators
            if "pending actions: 0" in content.lower():
                return True, "No pending actions in Dashboard"
            if "needs_action: **0 files**" in content.lower():
                return True, "No files needing action"

    return False, "Pending actions may exist"


def should_continue(hook_input):
    """
    Main decision function: Should Claude continue working?

    Returns: (continue, reason)
    """
    config = load_config()

    # Safety check: Don't exceed max iterations
    iteration_count = hook_input.get("iteration", 1)
    if iteration_count >= config.get("max_iterations", MAX_ITERATIONS):
        return False, f"Max iterations ({config['max_iterations']}) reached - safety stop"

    # Extract last message from Claude
    last_message = hook_input.get("last_response", "")

    # Check completion indicators in message
    is_complete, confidence, reason = check_completion_indicators(last_message)

    if is_complete and confidence > 0.8:
        log_iteration(hook_input, iteration_count, "ALLOW EXIT", reason)
        return False, reason

    # Check vault changes
    changes = check_vault_changes({})
    if changes["files_created"] == 0 and iteration_count > 1:
        # No progress made - might be stuck
        log_iteration(hook_input, iteration_count, "ALLOW EXIT", "No progress detected - potential stuck state")
        return False, "No vault changes detected - allowing exit to prevent infinite loop"

    # Check Needs_Action folder
    needs_action_clear, na_reason = check_needs_action_folder()
    if not needs_action_clear:
        log_iteration(hook_input, iteration_count, "CONTINUE", na_reason)
        return True, na_reason

    # Check task list
    tasks_clear, task_reason = check_task_list()
    if not tasks_clear and config.get("require_explicit_completion", True):
        log_iteration(hook_input, iteration_count, "CONTINUE", task_reason)
        return True, task_reason

    # If we're here and confidence is low, ask for explicit completion
    if confidence < 0.7 and config.get("require_explicit_completion", True):
        log_iteration(hook_input, iteration_count, "CONTINUE", "No explicit task completion statement")
        return True, "Task completion not explicitly confirmed"

    # Default: allow exit
    log_iteration(hook_input, iteration_count, "ALLOW EXIT", "All criteria satisfied")
    return False, "Task appears complete"


def generate_continuation_prompt(hook_input, reason):
    """Generate prompt to re-inject and continue working."""
    iteration = hook_input.get("iteration", 1)
    original_task = hook_input.get("task", "the current task")

    prompt = f"""
⚠️ **Ralph Wiggum Autonomy Loop - Iteration {iteration}**

The task is not yet complete. Reason: {reason}

**Original Task**: {original_task}

**What to do now**:
1. Review what you've accomplished so far
2. Identify what still needs to be done
3. Complete the remaining work
4. Explicitly state "Task Complete" when everything is done

**Completion Checklist**:
- [ ] All required files created/modified
- [ ] Needs_Action folder empty (if applicable)
- [ ] Dashboard updated
- [ ] Logs written
- [ ] Explicit completion statement provided

**Continue working until ALL items are complete.**

Don't just announce what needs to be done - actually DO IT now.
"""

    return prompt


def main():
    """Main hook entry point."""
    try:
        # Read hook input from stdin (Claude Code provides this)
        hook_input = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

        # Initialize iteration counter if not present
        if "iteration" not in hook_input:
            hook_input["iteration"] = 1
        else:
            hook_input["iteration"] += 1

        # Decide whether to continue
        should_continue_working, reason = should_continue(hook_input)

        # Prepare response
        response = {
            "continue": should_continue_working,
            "reason": reason,
            "iteration": hook_input["iteration"]
        }

        # If continuing, provide continuation prompt
        if should_continue_working:
            response["inject_prompt"] = generate_continuation_prompt(hook_input, reason)

        # Output response as JSON
        print(json.dumps(response, indent=2))

        return 0 if not should_continue_working else 1

    except Exception as e:
        # Log error but don't block Claude
        error_msg = f"Ralph Wiggum Loop Error: {str(e)}"
        print(json.dumps({
            "continue": False,
            "reason": error_msg,
            "error": True
        }), file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
