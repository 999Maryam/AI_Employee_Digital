# LinkedIn MCP Server - Setup Guide

Quick start guide for setting up your LinkedIn MCP server.

## Step 1: Register LinkedIn Developer App

1. **Go to LinkedIn Developer Portal**
   - Visit: https://www.linkedin.com/developers/apps
   - Click "Create app"

2. **Fill in App Details**
   - App name: "AI Employee LinkedIn Automation" (or your choice)
   - LinkedIn Page: Select your company page (required)
   - App logo: Optional
   - Legal agreement: Accept terms

3. **Configure Products**
   - Go to "Products" tab
   - Add "Sign In with LinkedIn using OpenID Connect"
   - Add "Share on LinkedIn"
   - Wait for approval (usually instant for personal use)

4. **Get Credentials**
   - Go to "Auth" tab
   - Copy "Client ID"
   - Copy "Primary Client Secret"
   - Save these securely

## Step 2: Get Access Token

### Option A: Token Generator (Quick - 60 days)

1. Visit: https://www.linkedin.com/developers/tools/oauth/token-generator
2. Select your app from dropdown
3. Check these scopes:
   - ✅ `openid`
   - ✅ `profile`
   - ✅ `email`
   - ✅ `w_member_social` (critical for posting)
4. Click "Request access token"
5. Copy the token (valid for 60 days)

### Option B: OAuth Flow (Production - Automatic refresh)

*This is more complex but allows automatic token refresh. For now, use Option A.*

## Step 3: Get Person URN

You need your LinkedIn person ID to post as yourself.

### Using curl:

```bash
# Replace YOUR_ACCESS_TOKEN with token from Step 2
curl -X GET 'https://api.linkedin.com/v2/userinfo' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

### Response will look like:

```json
{
  "sub": "AbCdEfG123",
  "name": "Your Name",
  "email": "you@example.com",
  ...
}
```

Your Person URN is: `urn:li:person:AbCdEfG123` (use the `sub` value)

## Step 4: Configure Environment

1. **Navigate to server directory**:
   ```bash
   cd /mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/linkedin-mcp-server
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file** (use nano, vim, or any text editor):
   ```bash
   nano .env
   ```

4. **Fill in your credentials**:
   ```env
   LINKEDIN_ACCESS_TOKEN=your_token_from_step_2
   LINKEDIN_PERSON_URN=urn:li:person:your_id_from_step_3
   DRY_RUN=true
   ```

5. **Save and exit**

## Step 5: Install and Build

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build
```

## Step 6: Test the Server

### Test 1: Verify Connection

```bash
npm start
```

Server should start with:
```
LinkedIn MCP Server running on stdio
Mode: DRY RUN (no actual posting)
```

### Test 2: Verify from Another Terminal

Create a test file `test-post.json`:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "verify_linkedin_connection",
    "arguments": {}
  }
}
```

*Note: Full MCP testing requires Claude Code integration (Step 7)*

## Step 7: Integrate with Claude Code

### Option A: Claude Desktop Config

Edit `~/.config/claude/claude_desktop_config.json` (or Windows equivalent):

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "node",
      "args": [
        "/mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/linkedin-mcp-server/dist/index.js"
      ],
      "env": {
        "LINKEDIN_ACCESS_TOKEN": "your_token_here",
        "LINKEDIN_PERSON_URN": "urn:li:person:your_id",
        "DRY_RUN": "true"
      }
    }
  }
}
```

### Option B: Claude CLI Config

If using Claude CLI, add to your config file per Claude's MCP documentation.

## Step 8: Test End-to-End

1. **Update /linkedin-post skill** to use the MCP tool
2. **Run** `/linkedin-post` in Claude Code
3. **Draft** a test post
4. **Approve** it (move to Approved/)
5. **Run** `/check-approvals`
6. **Verify** dry-run output in logs

## Step 9: Go Live

When ready for real posting:

1. Edit `.env`:
   ```env
   DRY_RUN=false
   ```

2. Restart MCP server

3. Post will now go live on LinkedIn

## Maintenance

### Token Expiry (Every 60 Days)

1. LinkedIn tokens expire after 60 days
2. Set a calendar reminder for ~50 days from now
3. Regenerate token using Step 2
4. Update `.env` file
5. Restart MCP server

### Checking Token Expiry

LinkedIn doesn't provide expiry date in response, but you can track it:

```bash
# Add to .env when you get new token
TOKEN_GENERATED=2026-02-07
TOKEN_EXPIRES=2026-04-08
```

## Troubleshooting

### "npm install fails"

- Ensure Node.js 20+ is installed: `node --version`
- Try: `npm install --legacy-peer-deps`

### "TypeScript compilation errors"

- Check TypeScript version: `npx tsc --version` (should be 5.7+)
- Run: `npm run build` for detailed errors

### "Cannot find module"

- Ensure you built the project: `npm run build`
- Check that `dist/` folder exists

### "401 Unauthorized"

- Token expired or invalid
- Regenerate token (Step 2)
- Verify scopes include `w_member_social`

### "Person URN format error"

- Must be: `urn:li:person:ID`
- Get from `/v2/userinfo` endpoint
- Use the `sub` field

## Next Steps

- ✅ Server is running in DRY_RUN mode
- ☑️ Test with `/linkedin-post` skill
- ☑️ Verify posts in dry-run logs
- ☑️ Go live by setting `DRY_RUN=false`
- ☑️ Set token expiry reminder

## Questions?

- Read full README.md
- Check LinkedIn API docs: https://learn.microsoft.com/en-us/linkedin/
- Review MCP spec: https://modelcontextprotocol.io

---

**Setup Time**: ~20-30 minutes first time, ~5 minutes for token refresh

Good luck! 🚀
