# Social Media Automation - Complete Step-by-Step Guide

**Last Updated**: 2026-02-27
**Version**: 1.0.0
**Status**: Production-Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [First-Time Setup](#first-time-setup)
6. [Creating Posts](#creating-posts)
7. [Creating Odoo Invoices](#creating-odoo-invoices)
8. [Workflow Explained](#workflow-explained)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

---

## Overview

This system allows you to post to LinkedIn, Facebook, and create Odoo invoices directly from your terminal with a simple Human-in-the-Loop approval workflow.

**Key Features:**
- Terminal-controlled posting
- Review before publishing (Human-in-the-Loop)
- Persistent browser sessions (login once)
- Dry-run mode for testing
- Image upload support
- Bulk operations from CSV
- Enterprise logging

---

## Prerequisites

Before you start, make sure you have:

- **Python 3.8+** installed
- **pip** (Python package manager)
- **Internet connection**
- **LinkedIn account** (for LinkedIn posting)
- **Facebook account** (for Facebook posting)
- **Odoo account** (for invoice creation)

Check Python version:
```bash
python3 --version
```

---

## Installation

### Step 1: Navigate to Project Directory

```bash
cd /path/to/AI_Employee_Vault
```

### Step 2: Run Setup Script

```bash
bash social_media/setup.sh
```

This will:
- Install Python dependencies (playwright, pyyaml, python-dotenv)
- Install Playwright browsers (Chromium)
- Create necessary directories
- Copy .env.example to .env

**Alternative Manual Installation:**

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r social_media/requirements.txt

# Install Playwright browsers
playwright install chromium

# Create directories
mkdir -p Pending_Approval Approved Done Logs session/linkedin session/facebook

# Copy configuration template
cp social_media/.env.example .env
```

---

## Configuration

### Step 1: Edit .env File

```bash
nano .env
```

### Step 2: Configure Settings

**Required Settings:**

```env
# System Configuration
DRY_RUN=true              # Set to false when ready for real posting
LOG_LEVEL=INFO            # DEBUG, INFO, WARNING, ERROR

# Odoo Configuration (if using Odoo invoices)
ODOO_URL=https://your-instance.odoo.com
ODOO_DB=your_database_name
ODOO_USER=your_email@example.com
ODOO_PASSWORD=your_odoo_password
```

**Important:**
- Start with `DRY_RUN=true` to test without actual posting
- LinkedIn and Facebook don't need API keys (uses browser sessions)
- Only configure Odoo if you plan to create invoices

### Step 3: Save and Exit

Press `Ctrl+X`, then `Y`, then `Enter`

---

## First-Time Setup

### Step 1: LinkedIn Session Setup

```bash
python social_media/session_manager.py --platform linkedin --setup
```

**What happens:**
1. A browser window will open
2. Log in to LinkedIn manually
3. Press Enter in terminal after logging in
4. Session is saved to `./session/linkedin/`

**You only need to do this once!** The session persists.

### Step 2: Facebook Session Setup

```bash
python social_media/session_manager.py --platform facebook --setup
```

**What happens:**
1. A browser window will open
2. Log in to Facebook manually
3. Press Enter in terminal after logging in
4. Session is saved to `./session/facebook/`

**You only need to do this once!** The session persists.

### Step 3: Verify Sessions

```bash
# Check LinkedIn session
python social_media/session_manager.py --platform linkedin

# Check Facebook session
python social_media/session_manager.py --platform facebook
```

You should see: `✅ [platform] session is valid`

---

## Creating Posts

### Method 1: Simple LinkedIn Post

```bash
python social_media/cli.py post linkedin "Just shipped a new feature! 🚀 #AI #Automation"
```

**What happens:**
1. Draft created in `Pending_Approval/POST_linkedin_YYYYMMDD_HHMMSS.md`
2. You review the file
3. Move to `Approved/` folder when ready
4. Orchestrator posts automatically
5. File moved to `Done/` when complete

### Method 2: Facebook Post with Image

```bash
python social_media/cli.py post facebook "Check out this visualization!" --image ./images/chart.png
```

### Method 3: Post to Both Platforms

```bash
python social_media/cli.py post both "This message goes to LinkedIn and Facebook!"
```

### Method 4: Interactive Mode

```bash
python social_media/cli.py post linkedin
```

**What happens:**
- You'll be prompted to enter content
- You'll be asked if you want to add an image
- Draft is created automatically

### Method 5: Bulk Posts from CSV

**Step 1:** Create `posts.csv`:

```csv
platform,content,image_path
linkedin,"First post content",./images/pic1.jpg
facebook,"Second post content",
both,"Post to both platforms",./images/pic2.jpg
```

**Step 2:** Import:

```bash
python social_media/cli.py bulk posts.csv
```

---

## Creating Odoo Invoices

### Method 1: Simple Invoice

```bash
python social_media/cli.py odoo-invoice "Acme Corporation" 1500 "Website development - Phase 1"
```

**What happens:**
1. Draft created in `Pending_Approval/INVOICE_YYYYMMDD_HHMMSS.md`
2. You review the invoice preview
3. Move to `Approved/` folder when ready
4. Orchestrator creates invoice in Odoo
5. File moved to `Done/` when complete

### Method 2: Interactive Mode

```bash
python social_media/cli.py odoo-invoice
```

**What happens:**
- You'll be prompted for customer name
- You'll be prompted for amount
- You'll be prompted for description
- Draft is created automatically

---

## Workflow Explained

### The Complete Workflow

```
1. CREATE DRAFT
   ↓
   Terminal Command → Draft saved to /Pending_Approval

2. REVIEW
   ↓
   You review the file, edit if needed

3. APPROVE
   ↓
   Move file to /Approved folder

4. AUTO-EXECUTE
   ↓
   Orchestrator detects file and posts automatically

5. COMPLETE
   ↓
   File moved to /Done with timestamp
```

### Starting the Orchestrator

The orchestrator monitors the `/Approved` folder 24/7 and automatically posts when it detects files.

**Option 1: Run Directly**

```bash
python social_media/orchestrator.py
```

Press `Ctrl+C` to stop.

**Option 2: Run with PM2 (Recommended for 24/7)**

```bash
# Install PM2 (if not installed)
npm install -g pm2

# Start orchestrator
pm2 start social_media/orchestrator.py --interpreter python3 --name social-orchestrator

# Save PM2 configuration
pm2 save

# Enable startup on boot
pm2 startup

# Check status
pm2 status

# View logs
pm2 logs social-orchestrator

# Stop orchestrator
pm2 stop social-orchestrator
```

### Manual Workflow (Without Orchestrator)

If you don't want to run the orchestrator, you can post manually:

```bash
# For LinkedIn
python social_media/executor.py linkedin "Your content here"

# For Facebook
python social_media/executor.py facebook "Your content here"

# For Odoo
python social_media/executor.py odoo "Description" --customer "Customer Name" --amount 1500
```

---

## Advanced Features

### 1. Dry-Run Mode

Test without actually posting:

```bash
# In .env file
DRY_RUN=true
```

All posts will be simulated with logs. Check `Logs/actions_YYYYMMDD.log` for results.

### 2. Image Upload

```bash
# LinkedIn with image
python social_media/cli.py post linkedin "Check this chart!" --image ./reports/chart.png

# Facebook with image
python social_media/cli.py post facebook "New product!" --image ./products/photo.jpg
```

**Supported formats:** JPG, PNG, GIF
**Recommended size:** < 10MB

### 3. Email Drafts (Future Feature)

```bash
python social_media/cli.py email "client@example.com" "Project Update" "Here's the latest..."
```

### 4. Logging Levels

```bash
# In .env file
LOG_LEVEL=DEBUG   # Verbose output for troubleshooting
LOG_LEVEL=INFO    # Standard output (recommended)
LOG_LEVEL=WARNING # Warnings only
LOG_LEVEL=ERROR   # Errors only
```

Logs are saved to:
- `Logs/actions_YYYYMMDD.log` - Daily action logs
- `Logs/orchestrator.log` - Orchestrator events
- `Logs/*_error_*.png` - Error screenshots

### 5. Rate Limiting

Built-in 60-second minimum delay between posts to avoid detection.

To change (in `orchestrator.py`):
```python
self.rate_limit_delay = 60  # seconds
```

---

## Troubleshooting

### Problem: "Not logged in to LinkedIn"

**Solution:**
```bash
python social_media/session_manager.py --platform linkedin --setup
```

Re-run the session setup to log in again.

---

### Problem: "Could not find 'Start a post' button"

**Cause:** LinkedIn UI changed, selectors need updating.

**Solution:**
1. Check error screenshot in `Logs/linkedin_error_*.png`
2. Update selectors in `social_media/executor.py`:

```python
start_post_selectors = [
    'button:has-text("Start a post")',
    '[aria-label="Start a post"]',
    # Add new selector here based on screenshot
]
```

---

### Problem: "Odoo authentication failed"

**Solution:**
1. Check credentials in `.env`:
   - Verify `ODOO_URL` includes `https://`
   - Confirm `ODOO_DB` name is correct
   - Use correct email and password

2. Test connection:
```bash
python social_media/executor.py odoo "Test" --customer "Test Customer" --amount 100
```

---

### Problem: "Module not found: playwright"

**Solution:**
```bash
pip install -r social_media/requirements.txt
playwright install chromium
```

---

### Problem: Posts not executing

**Checklist:**
1. Is orchestrator running? `ps aux | grep orchestrator`
2. Is file in `/Approved` folder? `ls Approved/`
3. Is `DRY_RUN=false` in `.env`?
4. Check logs: `tail -f Logs/actions_*.log`

---

### Problem: Image upload fails

**Checklist:**
1. Does image file exist? `ls -lh path/to/image.jpg`
2. Is file size < 10MB? `du -h path/to/image.jpg`
3. Is format JPG, PNG, or GIF?
4. Check logs for specific error

---

## Best Practices

### 1. Always Test with Dry-Run First

```bash
# In .env
DRY_RUN=true
```

Create a test post, verify it looks correct in logs, then set `DRY_RUN=false`.

---

### 2. Review Before Approving

Always check the draft in `Pending_Approval/` before moving to `Approved/`.

**Check:**
- Content is correct
- No typos
- Image path is valid (if using images)
- Platform is correct

---

### 3. Monitor Logs Regularly

```bash
# View today's logs
tail -f Logs/actions_$(date +%Y%m%d).log

# View orchestrator logs
tail -f Logs/orchestrator.log
```

---

### 4. Keep Sessions Fresh

If you change your LinkedIn/Facebook password, re-run session setup:

```bash
python social_media/session_manager.py --platform linkedin --setup
```

---

### 5. Backup Your .env File

```bash
cp .env .env.backup
```

Never commit `.env` to git (it's in `.gitignore`).

---

### 6. Use Descriptive Content

Good:
```bash
python social_media/cli.py post linkedin "Excited to announce our new AI feature that helps automate social media posting! 🚀 #AI #Automation"
```

Bad:
```bash
python social_media/cli.py post linkedin "test"
```

---

### 7. Schedule Posts During Business Hours

For maximum engagement, post during:
- **LinkedIn**: 7-9 AM, 12-1 PM, 5-6 PM (weekdays)
- **Facebook**: 1-4 PM (weekdays), 12-1 PM (weekends)

---

### 8. Use Images When Possible

Posts with images get 2-3x more engagement.

```bash
python social_media/cli.py post linkedin "Check out our latest results!" --image ./reports/chart.png
```

---

### 9. Keep Content Professional

- Use proper grammar and spelling
- Avoid controversial topics
- Include relevant hashtags (2-5 per post)
- Tag relevant people/companies when appropriate

---

### 10. Monitor Rate Limits

The system has built-in 60-second delays, but be aware of platform limits:
- **LinkedIn**: ~100 posts/day recommended
- **Facebook**: ~50 posts/day recommended

---

## Quick Reference

### Common Commands

```bash
# LinkedIn post
python social_media/cli.py post linkedin "Your content"

# Facebook post with image
python social_media/cli.py post facebook "Content" --image ./photo.jpg

# Post to both
python social_media/cli.py post both "Content"

# Odoo invoice
python social_media/cli.py odoo-invoice "Customer" 1500 "Description"

# Interactive mode
python social_media/cli.py post linkedin

# Bulk import
python social_media/cli.py bulk posts.csv

# Start orchestrator
python social_media/orchestrator.py

# Check session
python social_media/session_manager.py --platform linkedin

# View logs
tail -f Logs/actions_$(date +%Y%m%d).log
```

---

## File Locations

```
Pending_Approval/  - Drafts awaiting your review
Approved/          - Approved posts (auto-executed by orchestrator)
Done/              - Completed posts with timestamps
Logs/              - Error screenshots and logs
session/           - Browser session data (login once)
  ├── linkedin/    - LinkedIn session
  └── facebook/    - Facebook session
```

---

## Getting Help

1. **Read the logs:**
   ```bash
   tail -f Logs/actions_*.log
   ```

2. **Check error screenshots:**
   ```bash
   ls -lh Logs/*_error_*.png
   ```

3. **Enable debug logging:**
   ```bash
   # In .env
   LOG_LEVEL=DEBUG
   ```

4. **Test with dry-run:**
   ```bash
   # In .env
   DRY_RUN=true
   ```

---

## Summary

You now have a complete terminal-controlled social media automation system!

**Remember:**
1. Start with `DRY_RUN=true` to test
2. Review all posts before approving
3. Monitor logs regularly
4. Keep sessions fresh
5. Follow platform best practices

**Happy posting! 🚀**

---

**Version**: 1.0.0
**Last Updated**: 2026-02-27
**Status**: Production-Ready
