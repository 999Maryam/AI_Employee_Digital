# Facebook MCP Server 📘

**Model Context Protocol server for Facebook automation**

**Gold Tier Feature #6** | **Status**: Ready for setup ✅

Enables your AI Employee to post to Facebook, manage content, and track engagement through Facebook Graph API.

---

## Features

✅ **Post Management**
- Create text posts
- Create photo posts with captions
- Schedule posts (Pages only)
- Delete posts
- Get post details with engagement metrics

✅ **Content Retrieval**
- Get recent posts from profile or page
- View post engagement (reactions, comments, shares)
- Access post analytics (Pages only)

✅ **Profile & Page Management**
- Get user profile information
- List managed Facebook pages
- Switch between profile and page posting

✅ **Safety Features**
- Dry-run mode for testing
- No data modified in test mode
- Comprehensive error handling
- OAuth 2.0 secure authentication

---

## Quick Start

### 1. Install Dependencies

```bash
cd facebook-mcp-server
npm install
```

### 2. Get Facebook Access Token

**Option A: Graph API Explorer (Quick Test)**

1. Go to [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app (or create one)
3. Click "Get Token" → "Get User Access Token"
4. Select permissions:
   - `pages_manage_posts` (for page posting)
   - `pages_read_engagement` (for analytics)
   - `publish_to_groups` (optional)
5. Copy the access token

**Option B: Create Facebook App (Production)**

1. Go to [Facebook Developers](https://developers.facebook.com/apps)
2. Click "Create App" → Choose app type
3. Set up OAuth redirect
4. Get App ID and App Secret
5. Generate User Access Token with required permissions

### 3. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
FACEBOOK_ACCESS_TOKEN=your_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here  # Optional
DRY_RUN=true
```

### 4. Build the Server

```bash
npm run build
```

### 5. Test Connection

```bash
# Test in dry-run mode (safe, no changes)
npm start
```

### 6. Add to Claude Code

```bash
claude mcp add facebook -- node /path/to/facebook-mcp-server/dist/index.js
```

### 7. Verify

```bash
claude mcp list
```

Should show: `facebook: ... - ✓ Connected`

---

## Setup Guide

### Getting Facebook Page ID

**Method 1: From Page Settings**
1. Go to your Facebook Page
2. Click "About"
3. Scroll to "Page ID" (or check URL)

**Method 2: From Graph API Explorer**
```
https://graph.facebook.com/v19.0/me/accounts?access_token=YOUR_TOKEN
```

**Method 3: From Page URL**
- If URL is `facebook.com/YourPageName`, use Graph API:
  ```
  https://graph.facebook.com/v19.0/YourPageName
  ```

### Access Token Types

**User Access Token**
- Posts to your personal profile
- Expires in 1-2 hours
- Good for testing

**Page Access Token**
- Posts to your Facebook page
- Can be long-lived (60 days) or permanent
- Required for insights/analytics
- Get from `/me/accounts` endpoint

**Extended Access Token**
- Lasts 60 days instead of 1-2 hours
- Exchange short token for long token:
  ```
  https://graph.facebook.com/v19.0/oauth/access_token
    ?grant_type=fb_exchange_token
    &client_id=YOUR_APP_ID
    &client_secret=YOUR_APP_SECRET
    &fb_exchange_token=SHORT_TOKEN
  ```

---

## Available Tools

### 1. Create Text Post

```javascript
{
  "message": "Check out my new blog post about AI automation!",
  "link": "https://yourblog.com/ai-automation"
}
```

### 2. Create Photo Post

```javascript
{
  "url": "https://example.com/image.jpg",
  "caption": "Beautiful sunset at the beach! 🌅"
}
```

**Note**: Image URL must be publicly accessible

### 3. Schedule Post (Pages Only)

```javascript
{
  "message": "This post will go live tomorrow!",
  "scheduled_publish_time": 1707567600  // Unix timestamp
}
```

### 4. Get Post Details

```javascript
{
  "post_id": "123456789_987654321"
}
```

Returns:
```json
{
  "id": "123456789_987654321",
  "message": "Post content",
  "created_time": "2026-02-10T10:30:00+0000",
  "permalink_url": "https://facebook.com/...",
  "reactions": { "summary": { "total_count": 25 } },
  "comments": { "summary": { "total_count": 3 } },
  "shares": { "count": 5 }
}
```

### 5. Delete Post

```javascript
{
  "post_id": "123456789_987654321"
}
```

### 6. Get Recent Posts

```javascript
{
  "limit": 10
}
```

### 7. Get Managed Pages

```javascript
{}
```

Returns list of pages you manage with IDs and access tokens.

### 8. Get Profile

```javascript
{}
```

Returns your Facebook profile info.

### 9. Get Post Insights (Pages Only)

```javascript
{
  "post_id": "123456789_987654321"
}
```

Returns analytics: impressions, reach, engagement.

### 10. Test Connection

```javascript
{}
```

Verifies API connection and permissions.

---

## Usage Examples

### Post to Facebook

```
"Create a Facebook post:

Excited to share my latest project! 🚀

I've built an AI Employee that automates social media, handles emails, and generates business intelligence reports.

Check it out: https://github.com/yourusername/ai-employee"
```

### Post with Photo

```
"Post this image to Facebook with caption:

URL: https://i.imgur.com/example.jpg
Caption: Just completed my hackathon project! #AI #Automation"
```

### Check Recent Posts

```
"Show my last 5 Facebook posts with engagement stats"
```

### Delete a Post

```
"Delete Facebook post ID 123456789_987654321"
```

---

## Integration Examples

### With LinkedIn MCP

**Cross-post to both platforms:**

```python
# Post to both LinkedIn and Facebook
message = "Exciting news about our new product launch! 🎉"

# LinkedIn
linkedin_post(message)

# Facebook
facebook_post(message)
```

### With CEO Briefing

```python
# Include Facebook metrics in weekly briefing
facebook_posts = get_facebook_posts(limit=7)
total_engagement = sum(
    p.reactions.total_count +
    p.comments.total_count +
    p.shares.count
    for p in facebook_posts
)

briefing += f"""
### Social Media (Facebook)
- Posts this week: {len(facebook_posts)}
- Total engagement: {total_engagement}
- Average per post: {total_engagement / len(facebook_posts):.1f}
"""
```

### With Audit Logging

```python
from audit_logger import AuditLogger

logger = AuditLogger()
result = create_facebook_post(message)

logger.log_external_action(
    service="facebook",
    action="create_post",
    target_id=result.id,
    status="success",
    approval_status="approved",
    details={"engagement": result.reactions.total_count}
)
```

---

## Permissions Required

### Minimum Permissions (Profile Posting)
- `public_profile` - Basic info
- `email` - Email address

### Page Posting
- `pages_show_list` - List pages
- `pages_manage_posts` - Create/delete posts
- `pages_read_engagement` - View engagement

### Advanced Features
- `pages_read_user_content` - Read page content
- `pages_manage_engagement` - Respond to comments
- `publish_to_groups` - Post to groups

### How to Add Permissions

1. Graph API Explorer → "Get Token" → "Get User Access Token"
2. Select permissions needed
3. Click "Generate Access Token"
4. Grant permissions when prompted
5. Copy the new token to `.env`

---

## Security

### Access Token Safety

**Never commit access tokens**:
- `.env` is gitignored
- Use environment variables in production
- Rotate tokens regularly

### Token Storage

**Best practices**:
- Store in `.env` file locally
- Use secrets manager in production (Vault, AWS Secrets Manager)
- Set short expiration for testing
- Use long-lived tokens for production

### API Rate Limits

**Facebook limits**:
- 200 calls per hour per user
- 4800 calls per hour per app
- Posts: ~25 per day for profiles, unlimited for pages

**Handle limits**:
```typescript
try {
  await createPost(message);
} catch (error) {
  if (error.code === 4) {
    // Rate limited
    console.log('Rate limited, retry in 1 hour');
  }
}
```

---

## Troubleshooting

### "Invalid OAuth access token"

**Solutions**:
1. Token expired → Generate new token
2. Wrong permissions → Add required permissions
3. App not approved → Use Graph API Explorer for testing

### "This endpoint requires the 'pages_manage_posts' permission"

**Solution**: Add permission in Graph API Explorer when generating token

### "Cannot post to profile"

Facebook restricts profile posting. **Solution**: Use Facebook Page instead.

### Photo Upload Fails

**Check**:
1. Is URL publicly accessible?
2. Is image format supported? (JPG, PNG)
3. Is image size < 10MB?

### "Unsupported post request"

**Common causes**:
- Using user token for page-only features
- Missing required fields
- Invalid post ID format

---

## Development

### Run in Dev Mode

```bash
# Watch mode (auto-rebuild)
npm run dev

# In another terminal
npm start
```

### Add New Tools

1. Add method to `FacebookClient` (src/facebook-client.ts)
2. Define Zod schema
3. Add tool definition in `tools` array
4. Add handler in `setRequestHandler`
5. Rebuild and test

### Testing

```bash
# Always test in DRY_RUN mode first
DRY_RUN=true npm start

# Then test with real Facebook
DRY_RUN=false npm start
```

---

## Facebook API Versions

### Current: v19.0 (February 2024)

**Supported until**: May 2026

### Upgrading API Version

1. Update `.env`:
   ```
   FACEBOOK_API_VERSION=v20.0
   ```

2. Check [API Changelog](https://developers.facebook.com/docs/graph-api/changelog)

3. Test thoroughly in dry-run mode

---

## Gold Tier Impact

### Business Value

**Before Facebook Integration**:
- Manual Facebook posting (5-10 min per post)
- No cross-platform automation
- Limited social media reach
- No engagement tracking

**After Facebook Integration**:
- Automated Facebook posting (<1 min)
- Multi-platform posting (LinkedIn + Facebook)
- Broader audience reach
- Real-time engagement metrics

**ROI**: ~30-60 minutes saved per week on social media

### Multi-Platform Social Media

With both LinkedIn and Facebook MCP servers:

**Capabilities**:
- Cross-post to both platforms simultaneously
- Platform-specific formatting
- Unified engagement tracking
- Centralized social media management

**Example Workflow**:
```
1. Write one message
2. Auto-post to LinkedIn (professional)
3. Auto-post to Facebook (personal/page)
4. Track engagement on both
5. Include in CEO briefing
```

---

## Roadmap

### Current Features
- ✅ Text posts
- ✅ Photo posts
- ✅ Post deletion
- ✅ Engagement metrics
- ✅ Profile & page management

### Future Enhancements
- [ ] Video posts
- [ ] Story posting
- [ ] Comment management
- [ ] Automated responses
- [ ] Advanced analytics
- [ ] Group posting
- [ ] Event creation
- [ ] Live streaming

---

## FAQ

**Q: Do I need a Facebook Page or can I use my profile?**
A: Both work! Pages have more features (scheduling, insights) but profiles work for basic posting.

**Q: How long does the access token last?**
A: User tokens: 1-2 hours. Extended tokens: 60 days. Page tokens: Can be permanent.

**Q: Can I schedule posts?**
A: Yes, but only for Facebook Pages, not personal profiles.

**Q: Is there a posting limit?**
A: Personal profiles: ~25 posts/day. Pages: Much higher (100+).

**Q: Can I post to multiple pages?**
A: Yes! Use `get_facebook_pages` to list pages, then set `FACEBOOK_PAGE_ID` in `.env`.

**Q: How do I get analytics?**
A: Use `get_facebook_post_insights` - requires Facebook Page and page access token.

**Q: Can I test without posting publicly?**
A: Yes! Use `DRY_RUN=true` mode, or post as draft with `published: false`.

---

## Resources

- Facebook Graph API Docs: https://developers.facebook.com/docs/graph-api
- API Explorer: https://developers.facebook.com/tools/explorer/
- Permissions Reference: https://developers.facebook.com/docs/permissions/reference
- Rate Limits: https://developers.facebook.com/docs/graph-api/overview/rate-limiting
- Changelog: https://developers.facebook.com/docs/graph-api/changelog

---

**Status**: Operational (pending Facebook setup)
**Tier**: Gold Feature #6 - FINAL! 🏆
**Impact**: VERY HIGH - Multi-platform social media automation

---

*Facebook MCP Server - Completing your social media automation stack* 📘

**GOLD TIER 100% COMPLETE!** 🎉🥇
