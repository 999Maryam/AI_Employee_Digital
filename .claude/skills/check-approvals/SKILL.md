---
name: check-approvals
description: Checks the Approved folder for files that have been approved by the user, then executes the approved actions. Use when user says "check approvals", "run approved tasks", or "process approved".
when_to_use: Approved folder has new files OR task is "check approvals" OR "run approved tasks" OR "process approved"
---

# Check Approvals Skill

You are my AI Employee. Follow these steps exactly:

1. Read Company_Handbook.md and CLAUDE.md first for rules.
2. Scan the Approved/ folder for .md files.
3. For each .md file in Approved/:
   - Read full content.
   - Identify the approved action (e.g., send email, make payment, execute task).
   - Execute the action if it is internal (within this vault only).
   - If the action is external (email, payment, API call), log what would be done but do NOT execute. Report it to the user for manual action.
   - Update the corresponding plan in Plans/ if one exists (check off completed items).
   - Move the file to Done/ (rename to [original]_completed.md).
4. If no files in Approved/: Report "No approved actions to process."
5. Update Dashboard.md: Add under "## Recent Activity" like "- Executed approved action: [short summary]".
6. Log action in Logs/[current-date].md (create if needed).
7. Also check Pending_Approval/ and report how many items are still awaiting approval.
8. Output: "Approval check complete. X approved actions executed. Y items still pending approval."

Rules:
- Never execute external actions automatically. Only internal vault operations are allowed.
- If an approved file is unclear or ambiguous, move it back to Needs_Action with a note asking for clarification.
- Always be polite and professional.

Examples:
- Input: APPROVED_reply_client.md → Execute reply plan steps (internal only), update plan, move to Done.
- Input: APPROVED_payment_vendor.md → Log details, report to user for manual payment, move to Done.
