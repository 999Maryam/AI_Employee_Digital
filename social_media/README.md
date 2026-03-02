# Terminal-Based Social Media Automation System

**Version**: 1.0.0
**Status**: Production-Ready
**Last Updated**: 2026-02-27

A semi-autonomous social media manager with Human-in-the-Loop (HITL) architecture. Control LinkedIn, Facebook, and Odoo from your terminal with simple commands.

## 🎯 Features

- **Terminal Control**: Create posts via simple CLI commands
- **Multi-Platform**: LinkedIn, Facebook, Odoo invoices
- **Human-in-the-Loop**: Review and approve before posting
- **Persistent Sessions**: Login once, use forever
- **Dry-Run Mode**: Test without actual posting
- **Image Support**: Upload images with posts
- **Bulk Operations**: Create multiple posts from CSV
- **Robust Logging**: Enterprise-grade logging with timestamps
- **Rate Limiting**: Anti-detection with 60s minimum delay
- **Error Handling**: Screenshots on failure, 3 retry attempts
- **Interactive Mode**: Prompts for input if not provided

## 🚀 Quick Start

### 1. Installation

```bash
# Run setup script
bash social_media/setup.sh

# Or manual installation
pip install -r social_media/requirements.txt
playwright install chromium
```

### 2. Configuration

```bash
# Copy environment template
cp social_media/.env.example .env

# Edit .env with your credentials
nano .env
```

Required settings in `.env`:
```env
DRY_RUN=true              # Set to false for actual posting
LOG_LEVEL=INFO            # DEBUG, INFO, WARNING, ERROR
ODOO_URL=https://your-instance.odoo.com
ODOO_DB=your_database
ODOO_USER=your_email@example.com
ODOO_PASSWORD=your_password
```

### 3. Session Setup (One-Time)

```bash
# LinkedIn session
python social_media/session_manager.py --platform linkedin --setup

# Facebook session
python social_media/session_manager.py --platform facebook --setup
```

### 4. Start Orchestrator (24/7 Monitoring)

```bash
# Run directly
python social_media/orchestrator.py

# Or with PM2 for 24/7 operation
pm2 start social_media/orchestrator.py --interpreter python3 --name social-orchestrator
pm2 save
```

### 5. Create Your First Post

```bash
# LinkedIn post
python social_media/cli.py post linkedin "Just shipped a new feature! 🚀"

# Facebook post with image
python social_media/cli.py post facebook "Check this out!" --image ./photo.jpg

# Post to both platforms
python social_media/cli.py post both "This goes everywhere!"

# Odoo invoice
python social_media/cli.py odoo-invoice "Acme Corp" 1500 "Website development"
```

## 📖 Complete Usage Guide

### CLI Commands

#### Social Media Posts

```bash
# Basic post
python social_media/cli.py post linkedin "Your content here"

# Post with image
python social_media/cli.py post linkedin "Content" --image ./path/to/image.jpg

# Post to multiple platforms
python social_media/cli.py post both "Same content on LinkedIn and Facebook"

# Interactive mode (prompts for input)
python social_media/cli.py post linkedin
```

#### Odoo Invoices

```bash
# Create invoice
python social_media/cli.py odoo-invoice "Customer Name" 1500 "Service description"

# Interactive mode
python social_media/cli.py odoo-invoice
```

#### Bulk Operations

Create `posts.csv`:
```csv
platform,content,image_path
linkedin,"First post content",./images/pic1.jpg
facebook,"Second post content",
both,"Post to both platforms",./images/pic2.jpg
```

Run bulk import:
```bash
python social_media/cli.py bulk posts.csv
```

#### Email Drafts

```bash
python social_media/cli.py email "client@example.com" "Subject" "Email body"
```

### Workflow

1. **Create Draft**: Run CLI command → Draft saved to `/Pending_Approval`
2. **Review**: Check the draft file, edit if needed
3. **Approve**: Move file to `/Approved` folder
4. **Auto-Execute**: Orchestrator detects file and posts automatically
5. **Complete**: File moved to `/Done` with timestamp

## 🏗️ Architecture

```
Terminal Command → CLI → Pending_Approval/ → [Human Review] → Approved/ → Orchestrator → Executor → Done/
```

### Components

- **cli.py**: Terminal interface for creating drafts
- **session_manager.py**: Persistent browser sessions (login once)
- **executor.py**: Platform-specific posting logic (LinkedIn, Facebook, Odoo)
- **orchestrator.py**: Monitors `/Approved` and triggers execution
- **requirements.txt**: Python dependencies
- **setup.sh**: Automated installation script

### Folder Structure

```
AI_Employee_Vault/
├── social_media/
│   ├── __init__.py
│   ├── cli.py                 # Terminal commands
│   ├── session_manager.py     # Session persistence
│   ├── executor.py            # Platform posting logic
│   ├── orchestrator.py        # Monitoring & execution
│   ├── requirements.txt       # Dependencies
│   └── setup.sh              # Setup script
├── session/
│   ├── linkedin/             # LinkedIn session data
│   └── facebook/             # Facebook session data
├── Pending_Approval/         # Drafts awaiting review
├── Approved/                 # Approved posts (auto-executed)
├── Done/                     # Completed posts
├── Logs/                     # Error screenshots & logs
├── .env                      # Configuration (DO NOT COMMIT)
└── .env.example             # Configuration template
```

## 🔧 Advanced Features

### Dry-Run Mode

Test without actual posting:
```bash
# In .env
DRY_RUN=true

# All posts will be simulated with logs
python social_media/cli.py post linkedin "Test post"
```

### Logging Levels

```bash
# In .env
LOG_LEVEL=DEBUG   # Verbose output
LOG_LEVEL=INFO    # Standard output (recommended)
LOG_LEVEL=WARNING # Warnings only
LOG_LEVEL=ERROR   # Errors only
```

Logs are saved to:
- `./Logs/actions_YYYYMMDD.log` - Daily action logs
- `./Logs/orchestrator.log` - Orchestrator events
- `./Logs/*_error_*.png` - Error screenshots

### Rate Limiting

Built-in 60-second minimum delay between posts to avoid detection. Configurable in `orchestrator.py`:

```python
self.rate_limit_delay = 60  # seconds
```

### Anti-Detection Features

- Random delays (2-4 seconds) between actions
- Human-like typing speed (30-80ms per character)
- Multiple fallback selectors for each button
- Full-page error screenshots for debugging

### Image Upload

Supports common image formats (JPG, PNG, GIF):

```bash
python social_media/cli.py post linkedin "Check out this chart!" --image ./reports/chart.png
```

Images are uploaded before posting and validated for existence.

## 🧪 Testing

Run the full test suite:

```bash
python test_full_flow.py
```

Tests include:
- LinkedIn post creation
- Odoo invoice creation
- Executor dry-run simulation
- File workflow (Pending → Approved → Done)

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use app-specific passwords** for email/Odoo
3. **Encrypt session folders** (optional, for sensitive environments)
4. **Review all posts** before moving to `/Approved`
5. **Enable rate limiting** to avoid platform bans
6. **Monitor logs** for suspicious activity

### .gitignore

```
.env
session/
Logs/
*.log
*.png
__pycache__/
```

## 🐛 Troubleshooting

### "Could not find 'Start a post' button"

LinkedIn UI changed. Update selectors in `executor.py`:

```python
start_post_selectors = [
    'button:has-text("Start a post")',
    '[aria-label="Start a post"]',
    # Add new selector here
]
```

### "Not logged in to LinkedIn"

Session expired. Re-run setup:

```bash
python social_media/session_manager.py --platform linkedin --setup
```

### "Odoo authentication failed"

Check credentials in `.env`:
- Verify ODOO_URL (include https://)
- Confirm ODOO_DB name
- Use correct email and password

### Posts not executing

1. Check orchestrator is running: `ps aux | grep orchestrator`
2. Verify file is in `/Approved` folder
3. Check logs: `tail -f Logs/actions_*.log`
4. Ensure DRY_RUN=false in `.env`

### Image upload fails

- Verify image path exists
- Check file size (< 10MB recommended)
- Ensure format is JPG, PNG, or GIF
- Check logs for specific error

## 📊 Monitoring

### Check Orchestrator Status

```bash
# If running with PM2
pm2 status
pm2 logs social-orchestrator

# If running directly
ps aux | grep orchestrator
```

### View Logs

```bash
# Today's actions
tail -f Logs/actions_$(date +%Y%m%d).log

# Orchestrator events
tail -f Logs/orchestrator.log

# All error screenshots
ls -lh Logs/*_error_*.png
```

### Pending Items

```bash
# Check pending approvals
ls -lh Pending_Approval/

# Check approved queue
ls -lh Approved/

# Check completed items
ls -lh Done/
```

## 🚀 Deployment

### Production Deployment with PM2

```bash
# Install PM2
npm install -g pm2

# Start orchestrator
pm2 start social_media/orchestrator.py --interpreter python3 --name social-orchestrator

# Save PM2 configuration
pm2 save

# Enable startup on boot
pm2 startup

# Monitor
pm2 monit
```

### Systemd Service (Alternative)

Create `/etc/systemd/system/social-orchestrator.service`:

```ini
[Unit]
Description=Social Media Orchestrator
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/AI_Employee_Vault
ExecStart=/usr/bin/python3 social_media/orchestrator.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable social-orchestrator
sudo systemctl start social-orchestrator
sudo systemctl status social-orchestrator
```

## 📝 File Format Reference

### Post File Format

```markdown
---
platform: linkedin
created: 2026-02-27T10:30:00
status: pending
image: ./images/photo.jpg
type: post
---

Your post content goes here.

You can use multiple lines,
emojis 🚀, and formatting.
```

### Invoice File Format

```markdown
---
type: invoice
customer: Acme Corporation
amount: 1500.00
created: 2026-02-27T10:30:00
status: pending
---

Website development - Phase 1
- Homepage redesign
- Contact form integration
- Mobile optimization
```

## 🤝 Contributing

This is a personal AI Employee project. For issues or suggestions:

1. Check existing issues in the repository
2. Create detailed bug reports with logs
3. Include screenshots for UI-related issues
4. Test with DRY_RUN=true first

## 📄 License

Private project - All rights reserved

## 🙏 Acknowledgments

- Built with Playwright for browser automation
- Uses XML-RPC for Odoo integration
- Inspired by Human-in-the-Loop AI architectures

## 📞 Support

For questions or issues:
1. Check troubleshooting section above
2. Review logs in `/Logs` folder
3. Test with `python test_full_flow.py`
4. Enable DEBUG logging for detailed output

---

**Built with ❤️ by AI Employee**
**Last Updated**: 2026-02-27
**Version**: 1.0.0 - Production Ready
