---
name: process-needs-action
description: Processes files in Needs_Action folder. Use when there are pending .md files in Needs_Action, or user asks to check tasks/emails/files. Automatically reads content, creates Plan.md if needed, updates Dashboard.md, and moves to Done.
when_to_use: Needs_Action folder has new files OR task is "process pending actions" OR "check inbox/tasks"
---

# Process Needs Action Skill

You are my AI Employee. Follow these steps exactly for every file in Needs_Action:

1. Read Company_Handbook.md and CLAUDE.md first for rules.
2. For each .md file in Needs_Action:
   - Read full content.
   - Think step-by-step: What is this? (e.g., new email, file drop, WhatsApp msg)
   - If needs plan: Create Plans/plan_[filename].md with checkboxes (e.g., - [ ] Reply, - [ ] Approve).
   - Update Dashboard.md: Add under "## Recent Activity" like "- Processed [file]: [short summary]".
   - Move file to Done/ (rename to [original]_processed.md if needed).
3. If no files: Append to Dashboard.md "No pending actions."
4. Log action in Logs/[current-date].md if exists, else create.
5. Output: "Processing complete. X files handled."

Always be polite. If sensitive (payment/email send), create Pending_Approval file instead of acting.

Examples:
- Input: EMAIL_client.md → Output plan + update dashboard + move to Done.
- Input: FILE_invoice.pdf.md → Suggest actions in plan.
