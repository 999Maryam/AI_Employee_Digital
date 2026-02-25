# Ralph Wiggum Autonomy Loop - Iteration Log

**Created**: 2026-02-09
**Purpose**: Track autonomy engine iterations and decisions
**Retention**: 90 days

This log tracks when the Ralph Wiggum Loop detects incomplete work and re-injects prompts to continue.

---

## How It Works

The Ralph Wiggum Loop is a stop hook that:
1. Intercepts Claude's exit attempts
2. Checks if the task is truly complete
3. Re-injects prompts if work remains
4. Allows exit only when completion criteria are met

**Completion Criteria**:
- Explicit completion statements ("Task Complete", "All Done", etc.)
- Needs_Action folder empty
- Dashboard shows 0 pending actions
- Files created/modified as expected
- No error or "need to" statements in last message

**Safety Limits**:
- Maximum 10 iterations per task
- Allows exit if no progress detected
- Prevents infinite loops

---

## Iteration History

Iterations will be logged below as they occur.

---
