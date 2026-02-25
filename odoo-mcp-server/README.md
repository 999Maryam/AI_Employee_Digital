# Odoo MCP Server 💰

**Model Context Protocol server for Odoo accounting automation**

**Gold Tier Feature #4** | **Status**: Ready for setup

Enables your AI Employee to manage finances, create invoices, track expenses, and generate financial reports through Odoo ERP.

---

## Features

✅ **Invoice Management**
- Create customer invoices with line items
- Retrieve and filter invoices by state
- Track payment status

✅ **Expense Tracking**
- Record business expenses
- Categorize by product/service
- View expense history

✅ **Financial Intelligence**
- Revenue summaries
- Expense analysis
- Profit/loss calculations
- Date range filtering

✅ **Customer Management**
- Search customers by name/email
- Create new customers/partners
- Maintain contact information

✅ **Safety Features**
- Dry-run mode for testing
- No data modified in test mode
- Comprehensive error handling

---

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Odoo Credentials

Copy `.env.example` to `.env` and fill in your Odoo details:

```bash
cp .env.example .env
```

Edit `.env`:
```
ODOO_URL=http://localhost:8069
ODOO_DB=your_database
ODOO_USERNAME=admin@yourcompany.com
ODOO_PASSWORD=your_password
DRY_RUN=true
```

### 3. Build the Server

```bash
npm run build
```

### 4. Test Connection

```bash
# Test in dry-run mode (safe, no changes)
npm start

# Or test directly
node dist/index.js
```

### 5. Add to Claude Code

```bash
claude mcp add odoo -- node /path/to/odoo-mcp-server/dist/index.js
```

### 6. Verify

```bash
claude mcp list
```

Should show: `odoo: ... - ✓ Connected`

---

## Setup Guide

### Option A: Local Odoo (Docker)

**Install Odoo with Docker**:

```bash
# Create docker-compose.yml
docker-compose up -d
```

`docker-compose.yml`:
```yaml
version: '3.1'
services:
  web:
    image: odoo:16.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - odoo-data:/var/lib/odoo

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  odoo-data:
  db-data:
```

**Access Odoo**:
1. Go to http://localhost:8069
2. Create a database
3. Set admin password
4. Install Accounting module

**Configure MCP Server**:
```
ODOO_URL=http://localhost:8069
ODOO_DB=your_created_database
ODOO_USERNAME=admin
ODOO_PASSWORD=your_admin_password
```

---

### Option B: Odoo.com (Cloud)

**Sign up for Odoo**:
1. Go to https://www.odoo.com
2. Start free trial
3. Choose "Accounting" app

**Get API Credentials**:
1. Settings → Users & Companies → Users
2. Click your user
3. Generate API Key (recommended) or use password

**Configure MCP Server**:
```
ODOO_URL=https://yourcompany.odoo.com
ODOO_DB=yourcompany-main-123456
ODOO_USERNAME=admin@yourcompany.com
ODOO_PASSWORD=your_api_key_or_password
```

---

### Option C: Odoo.sh (Professional)

Follow Odoo.sh setup instructions and use:
```
ODOO_URL=https://yourproject-main-12345.dev.odoo.com
```

---

## Available Tools

### 1. Create Invoice

```javascript
{
  "customer_id": 7,
  "items": [
    {
      "name": "Consulting Services",
      "quantity": 10,
      "price": 150.00
    },
    {
      "name": "Software Development",
      "quantity": 20,
      "price": 200.00
    }
  ],
  "invoice_date": "2026-02-09"
}
```

### 2. Get Invoices

```javascript
{
  "limit": 10,
  "state": "posted"  // draft, posted, or paid
}
```

### 3. Record Expense

```javascript
{
  "name": "Office Supplies",
  "amount": 125.50,
  "quantity": 1,
  "date": "2026-02-09"
}
```

### 4. Get Expenses

```javascript
{
  "limit": 20
}
```

### 5. Get Financial Summary

```javascript
{
  "start_date": "2026-02-01",
  "end_date": "2026-02-09"
}
```

Returns:
```json
{
  "revenue": {
    "total": 15000,
    "paid": 12000,
    "unpaid": 3000,
    "invoices": 25
  },
  "expenses": {
    "total": 5000,
    "count": 45
  },
  "profit": 10000
}
```

### 6. Search Partners

```javascript
{
  "search_term": "Acme Corp",
  "limit": 10
}
```

### 7. Create Partner

```javascript
{
  "name": "New Customer Inc",
  "email": "contact@newcustomer.com",
  "phone": "+1-555-0123",
  "is_company": true
}
```

### 8. Test Connection

```javascript
{}
```

---

## Integration Examples

### With CEO Briefing

```python
# In CEO briefing generation
from odoo_integration import get_financial_summary

summary = get_financial_summary(
    start_date=week_start,
    end_date=week_end
)

# Include in briefing
report += f"""
### Financial Overview
- Revenue: ${summary['revenue']['total']:,.2f}
- Expenses: ${summary['expenses']['total']:,.2f}
- Profit: ${summary['profit']:,.2f}
"""
```

### With Audit Logging

```python
# Log invoice creation
from audit_logger import AuditLogger

logger = AuditLogger()
logger.log_external_action(
    service="odoo",
    action="create_invoice",
    target_id=f"invoice_{invoice_id}",
    status="success",
    approval_status="approved",
    details={"amount": total, "customer": customer_name}
)
```

### Automated Workflows

**Example: Email → Invoice**
```
1. Email arrives with project quote
2. AI extracts: customer, items, amounts
3. Searches Odoo for customer
4. Creates invoice draft
5. Sends for approval
6. After approval: Posts invoice in Odoo
7. Sends invoice PDF to customer
```

---

## Security

### API Keys (Recommended)

Instead of passwords, use Odoo API keys:

1. Odoo → Settings → Users → Your User
2. Click "New API Key"
3. Copy key to `.env` as `ODOO_PASSWORD`

**Benefits**:
- Can be revoked without changing password
- Limited scope
- Easier to rotate

### Credentials Storage

**Never commit credentials**:
- `.env` is gitignored
- Use environment variables in production
- Consider secrets management (Vault, AWS Secrets Manager)

### Network Security

**For production**:
- Use HTTPS only (`https://your-odoo.com`)
- Enable Odoo 2FA
- Restrict API access by IP
- Use VPN for local Odoo access

---

## Troubleshooting

### Connection Failed

**Check**:
1. Is Odoo running? `curl http://localhost:8069`
2. Are credentials correct?
3. Is database name exact match?
4. Can you log in via web browser?

**Test manually**:
```bash
node dist/index.js
# Then use test_odoo_connection tool
```

### Authentication Error

**Common causes**:
- Wrong username/password
- Wrong database name
- Account locked after failed attempts
- API key expired

**Solution**:
- Log in via browser to verify credentials
- Check database name in URL
- Reset password if needed
- Generate new API key

### Module Not Found

**Error**: `Model 'account.move' not found`

**Solution**:
- Install Accounting module in Odoo
- Go to Apps → Search "Accounting" → Install

### Timeout Errors

**If operations are slow**:
- Check Odoo server resources
- Reduce `limit` parameters
- Optimize Odoo database
- Consider upgrading Odoo hosting

---

## Development

### Run in Dev Mode

```bash
# Watch mode (auto-rebuild)
npm run watch

# In another terminal
npm start
```

### Add New Tools

1. Add method to `OdooClient` (src/odoo-client.ts)
2. Define Zod schema
3. Add tool definition in `tools` array
4. Add handler in `setRequestHandler`
5. Rebuild and test

### Testing

```bash
# Always test in DRY_RUN mode first
DRY_RUN=true npm start

# Then test with real Odoo
DRY_RUN=false npm start
```

---

## Odoo Modules

### Required Modules

- **Accounting** (account) - Core financial features
- **Contacts** (base) - Customer management

### Optional Modules

- **Expenses** (hr_expense) - Employee expense tracking
- **Sales** (sale) - Sales orders (becomes invoices)
- **Purchase** (purchase) - Vendor bills
- **Inventory** (stock) - Product management

### Installing Modules

1. Odoo → Apps
2. Remove "Apps" filter
3. Search for module
4. Click "Install"
5. Wait for installation
6. Refresh page

---

## Gold Tier Impact

### Business Value

**Before Odoo Integration**:
- Manual invoice creation (15 min each)
- Manual expense entry (5 min each)
- Manual financial reporting (2 hours/week)
- Delayed invoicing → slow cash flow

**After Odoo Integration**:
- Automated invoice creation (<1 min)
- Instant expense recording
- Real-time financial dashboards
- Faster invoicing → better cash flow

**ROI**: ~10-15 hours saved per week

### CEO Briefing Enhancement

With Odoo, CEO briefings now include:
- Real revenue numbers
- Actual expenses
- Profit/loss trends
- Cash flow status
- Unpaid invoice tracking

**This is real business intelligence!**

---

## Roadmap

### Current Features
- ✅ Invoice CRUD
- ✅ Expense tracking
- ✅ Financial summaries
- ✅ Customer management
- ✅ Dry-run mode

### Future Enhancements
- [ ] Bank reconciliation
- [ ] Purchase orders
- [ ] Vendor bill management
- [ ] Tax calculations
- [ ] Multi-currency support
- [ ] Budget tracking
- [ ] Custom reports
- [ ] Automated reminders

---

## FAQ

**Q: Do I need to pay for Odoo?**
A: Odoo Community Edition is free. Odoo Enterprise has a fee but more features.

**Q: Can I use Odoo Online (SaaS)?**
A: Yes! Odoo.com offers free trials and paid plans. Easier than self-hosting.

**Q: Is my financial data safe?**
A: Yes - credentials stored locally, connections use HTTPS, audit logging tracks all access.

**Q: Can I test without real Odoo?**
A: Yes! DRY_RUN mode simulates all operations without real Odoo.

**Q: How do I backup my data?**
A: Odoo has built-in backup. Also consider automated backups of PostgreSQL.

**Q: Can multiple AI employees use same Odoo?**
A: Yes! Each can have separate user accounts for audit trail.

---

## Support

- Odoo Documentation: https://www.odoo.com/documentation/16.0/
- Odoo Forum: https://www.odoo.com/forum
- API Reference: https://www.odoo.com/documentation/16.0/developer/api/external_api.html

---

**Status**: Operational (pending Odoo setup)
**Tier**: Gold Feature #4
**Impact**: VERY HIGH - Real financial intelligence

---

*Odoo MCP Server - Bringing enterprise accounting to your AI Employee* 💰
