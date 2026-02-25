# CEO Briefing Skill

**Purpose**: Generate comprehensive weekly business intelligence report every Monday morning

**Tier**: Gold Tier (Autonomous Employee)

**Invocation**: `/ceo-briefing` or automatically scheduled for Monday 9 AM

---

## Overview

This skill transforms your AI Employee into a business analyst and strategic advisor. It autonomously:
- Reviews all business activities from the past week
- Analyzes task completion rates and bottlenecks
- Audits financial transactions (when Odoo is integrated)
- Identifies trends and anomalies
- Provides proactive strategic suggestions
- Generates executive-ready presentation

**This is the standout feature that makes your AI a true Digital FTE.**

---

## When to Run

**Automatic Schedule**: Every Monday at 9:00 AM
**Manual Trigger**: User runs `/ceo-briefing`
**Ad-hoc**: User requests "Give me a business update"

---

## Execution Steps

### Phase 1: Data Collection (5 minutes)

1. **Read Core Files**:
   - CLAUDE.md (understand business context)
   - Company_Handbook.md (business rules)
   - Dashboard.md (current status)
   - All files in Done/ folder from past 7 days
   - All files in Plans/ folder
   - All log files from Logs/ (past 7 days)

2. **Analyze Task Performance**:
   - Count completed tasks (Done folder)
   - Count pending tasks (Needs_Action folder)
   - Count awaiting approval (Pending_Approval folder)
   - Identify overdue or stalled tasks
   - Calculate completion rate

3. **Review Communication**:
   - Scan email logs (Logs/ folder)
   - Check LinkedIn post performance
   - Review any social media engagement
   - Identify unanswered messages

4. **Financial Data** (when available):
   - Bank transaction summary
   - Revenue vs expenses
   - Unusual transactions
   - Budget tracking
   - Invoice status

5. **System Health**:
   - Check watcher status (gmail_watcher, filesystem_watcher)
   - MCP server connectivity
   - Error logs
   - Storage usage
   - API rate limits

### Phase 2: Analysis (5 minutes)

6. **Identify Patterns**:
   - What's working well?
   - What's causing delays?
   - Which areas need attention?
   - Are there recurring issues?
   - What's trending up/down?

7. **Calculate Metrics**:
   - Task completion rate (%)
   - Average task completion time
   - Email response time
   - System uptime (%)
   - Cost per task (when financial data available)

8. **Risk Assessment**:
   - Identify potential problems before they escalate
   - Flag unusual patterns
   - Check for security issues
   - Monitor resource constraints

### Phase 3: Strategic Recommendations (3 minutes)

9. **Proactive Suggestions**:
   - Process improvements
   - Automation opportunities
   - Cost optimizations
   - Revenue opportunities
   - Resource allocation recommendations

10. **Prioritized Action Items**:
    - High priority: What needs immediate attention
    - Medium priority: Important but not urgent
    - Low priority: Nice to have improvements

### Phase 4: Report Generation (2 minutes)

11. **Create Executive Report**:
    - Save to: `Reports/CEO_Briefing_[YYYY-WW].md`
    - Format: Clean, scannable, executive-ready
    - Include: Charts/tables where helpful (ASCII format)
    - Length: 2-3 pages (readable in 5 minutes)

12. **Update Dashboard**:
    - Add briefing summary to Dashboard.md
    - Update key metrics
    - Flag critical issues at top

13. **Generate Notification**:
    - Create file in Inbox: `CEO_BRIEFING_READY_[date].md`
    - Include executive summary (first 3 bullet points)
    - Link to full report

---

## Report Structure

### Executive Summary (Top 3 Items)
- Most important insights in 3 bullet points
- Designed to be read in 30 seconds

### 📊 Weekly Metrics Dashboard
```
Task Completion Rate:  [##########] 85% (↑ 5% from last week)
Email Response Time:   [########  ] 2.3 hours avg
System Uptime:         [##########] 99.5%
Active Projects:       5 in progress, 2 completed
```

### ✅ Accomplishments (Past 7 Days)
- Major tasks completed
- Milestones achieved
- Problems solved
- Skills demonstrated

### 📈 Performance Analysis
**What's Working Well:**
- [List 3-5 successes]

**Areas for Improvement:**
- [List 3-5 challenges with proposed solutions]

### 💰 Financial Overview (when Odoo integrated)
**Revenue:**
- Total income this week: $X,XXX
- Top revenue sources
- Compared to previous week

**Expenses:**
- Total spending this week: $X,XXX
- Largest expenses
- Budget status

**Net Position:**
- Profit/Loss this week
- Trend analysis

### 🚨 Issues & Bottlenecks
**Critical (Requires Immediate Action):**
- [List with proposed solutions]

**Important (Address This Week):**
- [List with timeline]

**Watch List (Monitor):**
- [Items to keep eye on]

### 🎯 Strategic Recommendations
**Priority 1 (This Week):**
1. [Action item with rationale]
2. [Action item with rationale]
3. [Action item with rationale]

**Priority 2 (This Month):**
1. [Action item]
2. [Action item]

**Future Opportunities:**
- [Long-term improvements]

### 📅 Week Ahead Preview
**Upcoming Deadlines:**
- [List with dates]

**Scheduled Tasks:**
- [Planned activities]

**Resource Needs:**
- [What's needed to succeed]

### 🤖 AI Employee Performance
**Tasks Automated:** X tasks
**Time Saved:** Y hours
**Success Rate:** Z%
**Areas Learning:** [Skills being developed]

---

## Output Format

**Primary Output**: `Reports/CEO_Briefing_[YYYY-WW].md`
**Secondary**: Update Dashboard.md with summary
**Notification**: Create Inbox file for user alert

**Example Filename**: `Reports/CEO_Briefing_2026-W06.md` (Week 6 of 2026)

---

## Tone & Style

- **Professional but conversational**
- **Data-driven with context**
- **Actionable insights, not just facts**
- **Honest about problems**
- **Solution-oriented**
- **Executive-level perspective**

Think: "If you were a senior business analyst reporting to the CEO, what would you say?"

---

## Intelligence & Insights

This isn't just data aggregation - it's business intelligence:

**Good**: "You completed 47 tasks this week"
**Better**: "You completed 47 tasks this week, 15% more than last week, primarily due to better email response time"
**Best**: "You completed 47 tasks this week (↑15%). The improvement came from responding to emails 2 hours faster on average, which unblocked 8 dependent tasks. Consider applying this same urgency to LinkedIn messages for similar gains."

**Always:**
- Connect the dots between data points
- Explain WHY something happened
- Suggest HOW to improve
- Quantify impact when possible

---

## Handling Missing Data

**Early Stage (No Odoo Yet)**:
- Note: "Financial tracking will be available once Odoo integration is complete"
- Focus on tasks, communications, and system health
- Provide placeholders showing what WILL be tracked

**Partial Data**:
- Work with what's available
- Note limitations
- Make recommendations based on partial view

**Never**:
- Make up data
- Guess at financials
- Provide false confidence

---

## Automation & Scheduling

### Manual Execution
User runs: `/ceo-briefing`
AI immediately generates report

### Scheduled Execution (Future Enhancement)
**Setup with Cron (Linux/Mac)**:
```bash
# Run every Monday at 9 AM
0 9 * * 1 claude-code /ceo-briefing
```

**Setup with Task Scheduler (Windows)**:
- Trigger: Weekly, Monday, 9:00 AM
- Action: Run Claude Code with /ceo-briefing command

**Alternative**:
- Create a watcher script that triggers on Monday 9 AM
- Places "RUN_CEO_BRIEFING.md" in Needs_Action folder
- /process-needs-action picks it up and executes

---

## Integration Points

**Current Integrations**:
- Dashboard.md (status tracking)
- Done folder (task completion)
- Logs folder (activity history)
- LinkedIn posts (social media performance)
- MCP servers (system connectivity)

**Future Integrations** (Gold Tier):
- Odoo (financial data)
- Calendar (upcoming events)
- Email (response metrics)
- WhatsApp (communication analysis)
- Banking API (transaction monitoring)

---

## Success Metrics

**This skill is successful when**:
- User reads it every Monday and finds value
- Identifies at least 1 actionable insight per week
- Catches potential problems before they escalate
- Saves user from manually reviewing all systems
- Provides strategic perspective, not just data dumps

**Measure**:
- User feedback ("Was this helpful?")
- Action items implemented
- Problems prevented
- Time saved (should take 5 min to read vs 60+ min to compile manually)

---

## Examples of Great Insights

**Cost Optimization**:
"You spent $127 on API calls this week, 40% above normal. Analysis shows 80% came from failed retries due to authentication issues. Fixing the token refresh logic could save $200/month."

**Revenue Opportunity**:
"Three clients mentioned budget availability in emails this week but didn't receive follow-up proposals. Estimated opportunity: $15K-30K. Suggest creating proposal template to speed response time."

**Process Improvement**:
"Tasks requiring approval took average 2.3 days to complete vs 4 hours for auto-approved tasks. Consider raising auto-approval threshold from $50 to $100 for trusted vendors to unlock 10-15 hours per week."

**Risk Prevention**:
"Gmail watcher has failed 3 times this week due to token expiration. Risk: Missing important client emails. Recommendation: Implement token refresh automation or switch to longer-lived credentials."

---

## Advanced Features (Future Enhancements)

### Trend Analysis
- Compare week-over-week
- Identify patterns over months
- Seasonal variations
- Growth trajectories

### Predictive Insights
- "Based on current trends, you're on track to..."
- "If this pattern continues..."
- "Early warning: [metric] is trending toward threshold"

### Benchmarking
- Compare to previous periods
- Industry standards (when available)
- Personal best metrics

### Visual Dashboards
- ASCII charts for terminal
- Generate images for presentations
- Interactive HTML reports

---

## Security & Privacy

**Never Include in Report**:
- Raw passwords or API keys
- Personal sensitive information
- Client confidential data (unless explicitly approved)
- Banking account numbers

**Safe to Include**:
- Aggregated metrics
- Trends and patterns
- Non-identifying task descriptions
- Business insights

**Storage**:
- Reports stored locally in vault
- Not synced to cloud (unless user explicitly enables)
- 90-day retention by default
- Older reports archived or deleted

---

## Error Handling

**If data sources unavailable**:
- Note what's missing
- Work with available data
- Provide partial report
- Never fail silently

**If analysis takes too long**:
- Provide quick summary first
- Detailed analysis as follow-up
- Set time limits (max 15 minutes total)

**If unexpected patterns found**:
- Flag for human review
- Don't make assumptions
- Ask clarifying questions if needed

---

## Gold Tier Checklist

This skill contributes to Gold Tier by:
- ✅ Demonstrating autonomous business analysis
- ✅ Providing executive-level strategic thinking
- ✅ Integrating multiple data sources
- ✅ Operating on regular schedule (autonomous)
- ✅ Delivering actionable business intelligence
- ✅ Showcasing the "Digital FTE" value proposition

**This is THE standout feature judges will remember.**

---

## Execution Reminder

**Always:**
1. Start by reading all relevant vault files
2. Think like a business analyst, not just a data aggregator
3. Connect dots between data points
4. Provide actionable recommendations
5. Be honest about limitations
6. Format for executive readability
7. Update Dashboard.md with key insights
8. Create notification for user

**Time Budget**:
- Data collection: 5 min
- Analysis: 5 min
- Recommendations: 3 min
- Report writing: 2 min
- **Total: ~15 minutes**

---

**This skill transforms your AI from an assistant into a strategic business partner.**
