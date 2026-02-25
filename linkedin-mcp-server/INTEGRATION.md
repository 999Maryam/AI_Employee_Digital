# Integrating LinkedIn MCP Server with AI Employee

This guide explains how to connect the LinkedIn MCP server with your AI Employee skills.

## Overview

The integration flow:

1. `/linkedin-post` skill creates draft → `Pending_Approval/`
2. Human reviews and approves → moves to `Approved/`
3. `/check-approvals` skill reads approved post
4. **NEW**: Skill calls MCP tool `post_to_linkedin`
5. MCP server posts to LinkedIn
6. Result logged and file moved to `Done/`

## Step 1: Configure Claude Code

Add the LinkedIn MCP server to your Claude Code configuration.

### For Claude Desktop

Edit `~/.config/claude/claude_desktop_config.json` (Linux/Mac) or
`%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "node",
      "args": [
        "/mnt/f/Maryam/Quarter_4/Ai_Employee_Vault/linkedin-mcp-server/dist/index.js"
      ],
      "env": {
        "LINKEDIN_ACCESS_TOKEN": "YOUR_TOKEN_HERE",
        "LINKEDIN_PERSON_URN": "urn:li:person:YOUR_ID",
        "DRY_RUN": "true"
      }
    }
  }
}
```

**Important**: Replace `YOUR_TOKEN_HERE` and `YOUR_ID` with actual values from SETUP_GUIDE.md

### For Claude CLI

If using Claude CLI, check Claude's documentation for MCP server configuration in your environment.

## Step 2: Restart Claude Code

After adding the MCP configuration:

1. Close Claude Code completely
2. Restart Claude Code
3. Verify MCP server is loaded (check for "linkedin" in available tools)

## Step 3: Update /check-approvals Skill

The `/check-approvals` skill needs to be updated to use the MCP tool for LinkedIn posts.

Edit `.claude/skills/check-approvals/SKILL.md` and add LinkedIn posting logic:

```markdown
3. For each .md file in Approved/:
   - Read full content.
   - Identify the approved action:

     **If file starts with "LINKEDIN_POST_":**
     - Extract the post content from the "## Post Content" section
     - Extract visibility setting (default: PUBLIC)
     - Call MCP tool: post_to_linkedin with extracted content
     - Log the result (post ID and URL)
     - Move file to Done/LINKEDIN_POSTED_[date]_[topic].md

     **If other action (email, payment, task):**
     - Execute if internal, log if external
     - Update corresponding plan
     - Move to Done/
```

## Step 4: Test with Dry Run

1. **Ensure DRY_RUN=true** in MCP config
2. Run `/linkedin-post` to create a draft
3. Move draft from `Pending_Approval/` to `Approved/`
4. Run `/check-approvals`
5. Check logs - should see: "DRY RUN: Post would be published to LinkedIn"

## Step 5: Using the MCP Tool Directly

Once configured, Claude Code can call the LinkedIn MCP tool directly:

```markdown
Use the MCP tool post_to_linkedin with:
{
  "commentary": "Post text here...",
  "visibility": "PUBLIC"
}
```

Claude will automatically use the configured MCP server.

## Step 6: Go Live

When ready for real posting:

1. **Update MCP config**: Change `DRY_RUN` from `"true"` to `"false"`
2. **Restart Claude Code**
3. **Test with small post**: Create simple test post and approve
4. **Verify**: Check LinkedIn feed for the post
5. **Monitor logs**: Check `Logs/linkedin_posts_*.md` for success confirmations

## Expected Behavior

### Dry Run Mode (DRY_RUN=true)

```
[2026-02-07 23:00] LinkedIn MCP Tool Called
Post content: "Just testing my AI Employee..."
Mode: DRY RUN
Result: Would post to LinkedIn (not actually posted)
```

### Live Mode (DRY_RUN=false)

```
[2026-02-07 23:00] LinkedIn MCP Tool Called
Post content: "Just testing my AI Employee..."
Mode: LIVE
Result: Posted successfully
Post ID: urn:li:activity:1234567890
Post URL: https://www.linkedin.com/feed/update/urn:li:activity:1234567890
```

## Logging Best Practices

Create or update `Logs/linkedin_posts_[YYYY-MM].md` to track all LinkedIn activity:

```markdown
# LinkedIn Posts Log - February 2026

## 2026-02-07 23:15
- **Status**: Posted
- **Content**: "Just hit Silver tier with my AI Employee..."
- **Visibility**: PUBLIC
- **Characters**: 1,450
- **Post ID**: urn:li:activity:7298765432
- **Post URL**: https://linkedin.com/feed/update/urn:li:activity:7298765432
- **Approval File**: LINKEDIN_POST_2026-02-07_silver-tier-achievement.md

## 2026-02-07 22:30
- **Status**: DRY RUN
- **Content**: "Testing the LinkedIn MCP integration..."
- **Visibility**: PUBLIC
- **Characters**: 45
```

## Troubleshooting

### "MCP tool not found"

- Check Claude Code configuration
- Restart Claude Code
- Verify server path is correct
- Check that server builds successfully: `cd linkedin-mcp-server && npm run build`

### "Access token invalid"

- Token expired (60-day limit)
- Regenerate in LinkedIn Developer Portal
- Update MCP config
- Restart Claude Code

### "Post not appearing on LinkedIn"

- Check if DRY_RUN=true (won't actually post)
- Verify visibility setting (CONNECTIONS only visible to connections)
- Check LinkedIn API rate limits
- Review error logs

### "Server crashes on startup"

- Check that .env file exists (or credentials in config)
- Verify Node.js version: `node --version` (need 20+)
- Check build completed: `ls linkedin-mcp-server/dist/`
- Review server logs for errors

## Advanced: Scheduled Posting

Future enhancement - schedule posts by creating them with a timestamp:

1. Create `Pending_Approval/LINKEDIN_POST_2026-02-10_1400_topic.md`
2. Cron job checks for files with future timestamps
3. At scheduled time, auto-move to `Approved/`
4. `/check-approvals` runs and posts

## Security Reminders

- ✅ Access token in config is encrypted by Claude
- ⚠️ Never commit `.env` file to git
- ⚠️ Review all posts before approving
- ✅ Use DRY_RUN for initial testing
- ✅ Set calendar reminder for token expiry (60 days)

## Testing Checklist

Before going live:

- [ ] MCP server installed and built
- [ ] Access token obtained and configured
- [ ] Person URN obtained and configured
- [ ] DRY_RUN=true initially
- [ ] Test post created with `/linkedin-post`
- [ ] Post approved and processed
- [ ] Dry run output verified in logs
- [ ] DRY_RUN=false for live mode
- [ ] Test post successfully posted to LinkedIn
- [ ] Post appears in LinkedIn feed
- [ ] Logging working correctly

## Next Steps

- ✅ Complete this integration
- ☐ Test end-to-end with real post
- ☐ Set up token expiry reminder
- ☐ Consider implementing automatic token refresh (advanced)
- ☐ Add image/media support (future enhancement)

---

**Integration Time**: ~15 minutes after server setup

Questions? See README.md or SETUP_GUIDE.md
