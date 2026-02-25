---
name: create-plan
description: Generate structured Plan.md for any task with step-by-step breakdown, dependencies, and approval workflow. Use when user requests a plan or complex task needs decomposition.
when_to_use: User asks to "create plan", "make a plan", "plan this task" OR complex multi-step task needs structured approach
---

# Create Plan Skill

You are my AI Employee. Follow these steps to create a comprehensive plan:

1. Read Company_Handbook.md and CLAUDE.md first for rules.
2. Understand the task requirements:
   - What is the goal?
   - What are the constraints?
   - What resources are needed?
   - Are there dependencies?
3. Create a structured plan file in Plans/Plan_[YYYY-MM-DD]_[TaskName].md with:
   - **Goal**: Clear one-sentence objective
   - **Context**: Background and why this matters
   - **Prerequisites**: What must exist before starting
   - **Steps**: Numbered checklist with - [ ] checkboxes
   - **Dependencies**: What blocks this? What does this block?
   - **Risk Assessment**: What could go wrong?
   - **Approval Required**: Yes/No (if yes, list what needs approval)
   - **Estimated Complexity**: Simple/Medium/Complex
4. If the plan requires external actions (email, payment, API calls):
   - Mark those steps clearly with [REQUIRES APPROVAL]
   - Create a Pending_Approval/APPROVAL_[TaskName].md file
   - Include plan summary and what you're asking permission to do
5. Update Dashboard.md under "## Recent Activity": "- Created plan: [TaskName]"
6. Log in Logs/[current-date].md
7. Output: "Plan created at Plans/Plan_[date]_[TaskName].md. [X] steps identified. [Approval required: Yes/No]"

Template Structure:
```markdown
# Plan: [Task Name]
**Created**: [Date]
**Status**: Draft / Approved / In Progress / Completed

## Goal
[One sentence describing the outcome]

## Context
[Why are we doing this? What's the background?]

## Prerequisites
- [ ] Prerequisite 1
- [ ] Prerequisite 2

## Steps
1. - [ ] Step 1 description
2. - [ ] Step 2 description [REQUIRES APPROVAL]
3. - [ ] Step 3 description

## Dependencies
- **Blocks**: [What can't start until this is done]
- **Blocked By**: [What must finish before this can start]

## Risk Assessment
- **Risk 1**: [Description] - Mitigation: [How to handle]
- **Risk 2**: [Description] - Mitigation: [How to handle]

## Approval Required
[Yes/No - List what specific actions need human approval]

## Notes
[Any additional context, links, or references]
```

Rules:
- Be specific and actionable in every step
- Use imperative verbs (Create, Send, Update, Review)
- Flag sensitive operations clearly
- Include rollback steps for risky operations
- Always timestamp plans
- Link to related files in the vault when relevant

Examples:
- Input: "Plan to respond to 5 client emails" → Create plan with email list, draft steps, approval flags
- Input: "Plan LinkedIn posting schedule for next week" → Create plan with content calendar, post drafts, scheduling logic
