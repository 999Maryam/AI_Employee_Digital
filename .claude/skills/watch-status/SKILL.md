---
name: watch-status
description: Monitor health and status of all watcher scripts (Gmail, WhatsApp, filesystem, etc). Shows running status, last activity, errors, and suggests fixes. Use when checking system health.
when_to_use: User asks "check watchers", "watcher status", "are watchers running" OR troubleshooting OR daily health check
---

# Watch Status Skill

You are my AI Employee. Follow these steps to check watcher health:

1. Read Company_Handbook.md and CLAUDE.md first for rules.
2. Identify all watcher scripts in the vault:
   - Look for *_watcher.py files in vault root
   - Common watchers: gmail_watcher.py, whatsapp_watcher.py, filesystem_watcher.py, bank_watcher.py
3. For each watcher found:
   - Check if it's currently running (use bash: `ps aux | grep [w]atcher_name`)
   - Find last activity timestamp (check Logs/ for recent entries from that watcher)
   - Look for error logs or crash reports
   - Verify required credentials/tokens exist (check for token.json, credentials.json, .env)
4. Check if PM2 is being used for process management:
   - Run: `pm2 list` to see managed processes
   - If PM2 is installed: show status from PM2
   - If not installed: note this as a recommendation
5. Create status report in Reports/Watcher_Status_[YYYY-MM-DD].md:

   ```markdown
   # Watcher Status Report
   **Generated**: [Current Date Time]
   **Status**: All Healthy / Issues Detected

   ## Summary
   - **Total Watchers**: [count]
   - **Running**: [count]
   - **Stopped**: [count]
   - **Errors**: [count]

   ## Watcher Details

   ### gmail_watcher.py
   - **Status**: Running / Stopped / Error
   - **PID**: [process ID if running]
   - **Last Activity**: [timestamp from logs]
   - **Last Action**: [brief description]
   - **Issues**: [None / description]

   ### filesystem_watcher.py
   - **Status**: Running / Stopped / Error
   - **PID**: [process ID if running]
   - **Last Activity**: [timestamp from logs]
   - **Last Action**: [brief description]
   - **Issues**: [None / description]

   [Repeat for each watcher found]

   ## Credentials Check
   - **Gmail Token**: Present / Missing
   - **Credentials**: Present / Missing
   - **Environment Variables**: [List critical ones and their status]

   ## Process Management
   - **PM2 Installed**: Yes / No
   - **PM2 Status**: [output from pm2 list if available]

   ## Recommendations
   1. [Action item 1 if any issues]
   2. [Action item 2 if any issues]
   3. [General improvements]

   ## Next Steps
   - [What to do if issues found]
   - [Scheduled next check: date]
   ```

6. If critical issues detected (watcher stopped, credentials missing):
   - Create alert file in Needs_Action/ALERT_Watcher_Down_[name].md
   - Include troubleshooting steps
7. Update Dashboard.md under "## System Status":
   ```markdown
   - **Watchers**: [X/Y] running | Last checked: [timestamp]
   ```
8. Log check in Logs/[current-date].md
9. Output summary:
   - "Watcher Status: [X/Y] healthy. [Issues found: description / All systems operational]"
   - "Full report: Reports/Watcher_Status_[date].md"

## Diagnostic Commands

Use these bash commands to gather information:

```bash
# Check running Python processes
ps aux | grep python | grep watcher

# Check PM2 processes
pm2 list

# Check for errors in last 24 hours (example for gmail watcher)
find Logs/ -name "*.md" -mtime -1 -exec grep -l "gmail_watcher" {} \;

# Verify credentials exist
ls -lh credentials.json token.json 2>/dev/null || echo "Credentials missing"

# Check Python dependencies
python3 -c "import google.auth; print('Gmail libs OK')" 2>/dev/null || echo "Gmail libs missing"
```

## Troubleshooting Guide

Include this in the report if issues found:

**If watcher is stopped:**
1. Check error logs in Logs/
2. Verify credentials are present and valid
3. Restart manually: `python3 [watcher_name].py &`
4. Or with PM2: `pm2 restart [watcher_name]`

**If credentials missing:**
1. Check for credentials.json and token.json
2. Re-authenticate if needed
3. Verify .env file has required API keys

**If watcher running but no activity:**
1. Check if monitored service has new items
2. Verify API rate limits not exceeded
3. Check network connectivity
4. Review watcher log for silent failures

**If PM2 not installed:**
1. Install: `npm install -g pm2`
2. Setup watchers: `pm2 start gmail_watcher.py --interpreter python3`
3. Save config: `pm2 save`
4. Enable startup: `pm2 startup`

Rules:
- Always be factual - don't guess if a watcher is running
- Prioritize critical watchers (Gmail, payment systems)
- Include actionable recommendations
- Never restart watchers without user approval
- Keep credentials secure - never log them
- Timestamp all checks for audit trail

Examples:
- Input: "check watchers" → Full status report showing all watchers healthy
- Input: "why didn't I get the email notification?" → Check gmail_watcher status, find it stopped, create alert
- Input: "watcher health check" → Generate report, all systems operational, log to Dashboard
