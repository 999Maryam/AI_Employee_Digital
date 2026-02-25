---
name: daily-briefing
description: Generate comprehensive daily summary including pending actions, completed tasks, upcoming deadlines, and system health. Foundation for Gold tier CEO briefing. Use for daily reviews.
when_to_use: User says "daily briefing", "morning update", "what do I need to know" OR automated daily schedule OR start of workday
---

# Daily Briefing Skill

You are my AI Employee. Follow these steps to create a comprehensive daily briefing:

1. Read Company_Handbook.md and CLAUDE.md first for rules.
2. Gather intelligence from across the vault:
   - **Needs_Action**: Count and categorize pending items
   - **Pending_Approval**: List items awaiting decisions
   - **Done**: Review last 24 hours of completed work
   - **Plans**: Check active plans and their progress
   - **Logs**: Scan for errors, warnings, or anomalies
   - **Dashboard.md**: Extract current metrics
3. Check system health:
   - Run basic watcher status check (lightweight version)
   - Verify critical credentials present
   - Check available disk space if possible
4. Analyze calendar/deadlines (if available):
   - Look for upcoming deadline mentions in Plans/
   - Check for scheduled posts or automated tasks
   - Identify overdue items
5. Generate briefing report in Reports/Daily_Briefing_[YYYY-MM-DD].md:

   ```markdown
   # Daily Briefing - [Day of Week], [Date]
   **Generated**: [Time]
   **Period**: Last 24 hours

   ---

   ## 🎯 Executive Summary
   [2-3 sentence overview of the day ahead and yesterday's wins]

   ---

   ## 📊 Metrics at a Glance
   - **Pending Actions**: [count] items in Needs_Action
   - **Awaiting Approval**: [count] items
   - **Completed (24h)**: [count] tasks
   - **Active Plans**: [count] in progress
   - **System Health**: [Healthy / Issues / Critical]

   ---

   ## ⚡ Priority Actions Today
   1. **[Highest Priority Task]** - [Why it matters]
   2. **[Second Priority]** - [Why it matters]
   3. **[Third Priority]** - [Why it matters]

   [Limit to top 3-5 priorities, sorted by urgency/importance]

   ---

   ## 📥 Needs Your Attention
   ### In Needs_Action ([count] items)
   - **[Category]**: [count] items - [brief description]
   - **[Category]**: [count] items - [brief description]

   ### Pending Approvals ([count] items)
   - **[Item name]**: [What needs approval]
   - **[Item name]**: [What needs approval]

   ---

   ## ✅ Yesterday's Achievements
   [Review last 24 hours from Done/ folder]
   - [Achievement 1]
   - [Achievement 2]
   - [Achievement 3]

   ---

   ## 📅 Upcoming Deadlines
   [Next 7 days, pulled from Plans/ or calendar]
   - **[Date]**: [Task/Event]
   - **[Date]**: [Task/Event]

   ---

   ## 🔧 System Status
   - **Watchers**: [X/Y running]
   - **Last Error**: [None / description + when]
   - **Credentials**: [Valid / Expiring / Issues]
   - **Disk Space**: [If available]

   ---

   ## 💡 Recommendations
   1. [Proactive suggestion based on patterns]
   2. [Optimization or improvement idea]
   3. [Risk or blocker to address]

   ---

   ## 📌 Notes & Context
   [Any additional context, trends, or observations]

   ---

   **Next Briefing**: [Tomorrow's date]
   ```

6. Update Dashboard.md:
   - Add to "## Recent Activity": "- Daily briefing generated: [date]"
   - Update "## Quick Stats" section with latest counts
7. Create quick summary for immediate display:
   ```markdown
   # Today's Snapshot
   - **Priority**: [Top 1 thing to focus on]
   - **Pending**: [count] actions needed
   - **Approvals**: [count] awaiting decision
   - **Completed**: [count] tasks done yesterday
   - **Health**: [System status]
   ```
8. Save quick summary to Dashboard.md at the top
9. Log in Logs/[current-date].md
10. Output:
    - Display the quick snapshot
    - "Full briefing: Reports/Daily_Briefing_[date].md"

## Intelligence Gathering Logic

### Categorize Needs_Action items:
- Email replies
- File processing
- Project tasks
- Administrative
- Urgent/Time-sensitive

### Priority Scoring (simple algorithm):
```
Priority Score = (Urgency × 3) + (Importance × 2) + (Age × 1)

Urgency:
- Has deadline today/tomorrow: 10
- Has deadline this week: 7
- No deadline: 3

Importance:
- External (client, revenue): 10
- Internal (team, project): 7
- Administrative: 4

Age (days in Needs_Action):
- 0-1 days: 0
- 2-3 days: 2
- 4-7 days: 5
- 8+ days: 10
```

### Pattern Recognition:
- Recurring tasks that could be automated
- Bottlenecks (same type of task piling up)
- Response time trends
- Peak activity periods

---

## Advanced Features (for Gold Tier evolution)

### Weekly variant (run Mondays):
- Include full week rollup
- Revenue/cost summaries (if banking data available)
- Strategic recommendations
- Long-term goal progress

### Integration hooks:
- Banking API for financial summaries
- Calendar API for schedule optimization
- Email metrics (response times, volume)
- Social media analytics

---

## Rules
- Be concise but comprehensive
- Highlight what matters most
- Use visual hierarchy (emojis, headers, bullets)
- Always be factual - no speculation
- If data is missing, note it rather than guess
- Maintain consistent format for easy scanning
- Include actionable next steps
- Positive tone while being realistic about challenges

## Automation Potential
This skill can be scheduled to run:
- **Daily**: 7:00 AM (start of workday)
- **Weekly**: Monday 6:00 AM (CEO briefing variant)
- **On-demand**: Anytime user requests

## Examples
- Input: "daily briefing" → Full report for today
- Input: "what should I focus on today" → Priority actions section highlighted
- Input: "morning update" → Quick snapshot + full briefing link
- Input: "weekly summary" (if Monday) → Extended version with week rollup

---

**Note**: This is a Bronze/Silver tier skill that serves as the foundation for the Gold tier "Monday Morning CEO Briefing" feature. As you add banking, social media, and other integrations, this briefing will automatically become more comprehensive.
