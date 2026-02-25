# LinkedIn MCP Server

Model Context Protocol (MCP) server that enables Claude Code to post content to LinkedIn automatically.

## Features

- ✅ Post to LinkedIn via the Posts API (2026)
- ✅ OAuth 2.0 authentication
- ✅ Dry-run mode for testing
- ✅ Character limit validation (3,000 chars)
- ✅ Visibility controls (PUBLIC, CONNECTIONS, LOGGED_IN)
- ✅ Connection verification
- ✅ Error handling and logging

## Prerequisites

1. **LinkedIn Developer Account**
   - Create an app at: https://www.linkedin.com/developers/apps
   - Verify with a LinkedIn Company Page

2. **Required Products/Permissions**
   - "Sign In with LinkedIn using OpenID Connect"
   - "Share on LinkedIn"
   - This adds scopes: `openid`, `profile`, `email`, `w_member_social`

3. **Node.js**
   - Version 20+ LTS

## Installation

```bash
# Navigate to server directory
cd linkedin-mcp-server

# Install dependencies
npm install

# Build TypeScript
npm run build
```

## Configuration

1. **Create `.env` file** (copy from `.env.example`):

```bash
cp .env.example .env
```

2. **Get Access Token**:
   - Go to: https://www.linkedin.com/developers/tools/oauth/token-generator
   - Select your app
   - Check scopes: `openid`, `profile`, `email`, `w_member_social`
   - Request token (valid for 60 days)
   - Copy token to `.env` as `LINKEDIN_ACCESS_TOKEN`

3. **Get Person URN**:
   - Use the access token to call: `https://api.linkedin.com/v2/userinfo`
   - Get the `sub` field from response
   - Set in `.env` as: `LINKEDIN_PERSON_URN=urn:li:person:{sub}`

4. **Set Mode**:
   - `DRY_RUN=true` - Test mode (no actual posting)
   - `DRY_RUN=false` - Live mode (posts to LinkedIn)

## Usage

### Standalone Testing

```bash
# Test the server
npm run dev

# Run in production
npm start
```

### With Claude Code

Add to your Claude Code MCP configuration (`claude_desktop_config.json` or similar):

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "node",
      "args": ["/mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/linkedin-mcp-server/dist/index.js"],
      "env": {
        "LINKEDIN_ACCESS_TOKEN": "your_token",
        "LINKEDIN_PERSON_URN": "urn:li:person:your_id",
        "DRY_RUN": "false"
      }
    }
  }
}
```

## Available Tools

### 1. `post_to_linkedin`

Create and publish a post to LinkedIn.

**Parameters**:
- `commentary` (string, required): Post text (max 3,000 characters)
- `visibility` (string, optional): "PUBLIC", "CONNECTIONS", or "LOGGED_IN" (default: PUBLIC)

**Example**:
```json
{
  "commentary": "Just built an amazing MCP server for LinkedIn automation! #AI #Automation",
  "visibility": "PUBLIC"
}
```

### 2. `verify_linkedin_connection`

Verify that the LinkedIn API connection is working.

**Parameters**: None

**Example**:
```json
{}
```

## Integration with AI Employee

The `/linkedin-post` skill in the AI Employee vault automatically uses this MCP server after approval:

1. User runs `/linkedin-post` or creates a draft manually
2. Post is saved to `Pending_Approval/`
3. User reviews and moves to `Approved/`
4. User runs `/check-approvals`
5. MCP server posts to LinkedIn
6. Result logged in `Logs/` and file moved to `Done/`

## Troubleshooting

### "Access token is invalid"

- Token may have expired (60-day limit)
- Regenerate token at: https://www.linkedin.com/developers/tools/oauth/token-generator
- Update `.env` file

### "LinkedIn API error: 401"

- Check that app has required products enabled
- Verify scopes: `w_member_social` is critical for posting
- Confirm Person URN format: `urn:li:person:{id}`

### "Post exceeds LinkedIn maximum"

- LinkedIn Posts API has 3,000 character limit
- Edit post to be shorter
- The `/linkedin-post` skill includes character counter

### "DRY_RUN mode - not posting"

- This is intentional for testing
- Set `DRY_RUN=false` in `.env` for live posting
- Restart the MCP server after changing .env

## Security Best Practices

- ⚠️ **Never commit `.env` file** - it contains your access token
- ⚠️ **Rotate tokens** - LinkedIn tokens expire in 60 days, set reminders
- ⚠️ **Use DRY_RUN first** - Always test with `DRY_RUN=true` before going live
- ✅ **Monitor usage** - Check LinkedIn API rate limits
- ✅ **Review posts** - Use human approval workflow

## Development

```bash
# Watch mode (auto-rebuild)
npm run watch

# In another terminal
npm start
```

## LinkedIn API Resources

- [Posts API Documentation](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)
- [OAuth 2.0 Guide](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [Developer Portal](https://www.linkedin.com/developers/)
- [Token Generator](https://www.linkedin.com/developers/tools/oauth/token-generator)

## MCP Resources

- [Model Context Protocol](https://modelcontextprotocol.io)
- [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Specification](https://modelcontextprotocol.io/specification/2025-11-25)

## License

MIT

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review LinkedIn API documentation
3. Create issue in AI Employee vault repository

---

**Built for**: AI Employee Silver Tier
**Created**: 2026-02-07
**Version**: 1.0.0
