# Plan: Build LinkedIn MCP Server
**Created**: 2026-02-07
**Status**: Draft

## Goal
Create a Model Context Protocol (MCP) server that enables Claude Code to post content to LinkedIn via API, completing the Silver tier requirement.

## Context
The /linkedin-post skill is ready and creates properly formatted posts with approval workflow. However, it currently has a placeholder for actual posting. We need an MCP server to execute the posting action after approval.

**Why this matters**:
- Completes Silver tier "One MCP server" requirement
- Enables true social media automation
- Foundation for Gold tier cross-domain integrations

## Prerequisites
- [ ] LinkedIn Developer Account created
- [ ] LinkedIn App registered to get API credentials
- [ ] OAuth 2.0 authentication flow understood
- [ ] Node.js v24+ installed (verified: ✅)
- [ ] Understanding of MCP protocol specification

## Steps

1. - [ ] **Research LinkedIn API** (2026-02-08)
   - Review LinkedIn Marketing API documentation
   - Understand OAuth 2.0 authentication requirements
   - Identify correct API endpoint for posting (UGC Post API)
   - Check rate limits and restrictions

2. - [ ] **Register LinkedIn Developer App** [REQUIRES APPROVAL]
   - Create LinkedIn Developer account if needed
   - Register new app for personal use
   - Configure OAuth redirect URIs
   - Obtain Client ID and Client Secret

3. - [ ] **Design MCP Server Architecture**
   - Define server capabilities (post, draft, schedule)
   - Design tool schemas for Claude Code integration
   - Plan credential storage (.env file, not in vault)
   - Design error handling and logging

4. - [ ] **Implement OAuth Flow**
   - Create authorization URL generator
   - Implement callback handler for auth code
   - Token exchange and storage
   - Token refresh mechanism

5. - [ ] **Build Core MCP Server**
   ```javascript
   // Tentative structure:
   // - linkedin-mcp-server/
   //   - package.json
   //   - server.js (main MCP server)
   //   - auth.js (OAuth handling)
   //   - linkedin-client.js (API wrapper)
   //   - .env (credentials - gitignored)
   ```

6. - [ ] **Implement LinkedIn Posting Tool**
   - Function to create UGC post
   - Handle text, hashtags, mentions
   - Support for media attachments (images/videos)
   - Return post URL and analytics

7. - [ ] **Integrate with Claude Code**
   - Add MCP server to Claude Code config
   - Test tool discovery
   - Verify parameter passing from skills

8. - [ ] **Test End-to-End Flow** [REQUIRES APPROVAL]
   - Run /linkedin-post skill
   - Approve post in Pending_Approval
   - Run /check-approvals
   - Verify actual post appears on LinkedIn
   - Check logging and error handling

9. - [ ] **Security Hardening**
   - Ensure .env file in .gitignore
   - Validate all user inputs
   - Implement rate limiting
   - Add dry-run mode for testing

10. - [ ] **Documentation**
    - README with setup instructions
    - Authentication guide
    - Troubleshooting section
    - Example usage

## Dependencies
- **Blocks**: Full Silver tier completion, LinkedIn automation, Gold tier social media features
- **Blocked By**: None (can start immediately with research phase)

## Risk Assessment

**Risk 1: LinkedIn API Access Restrictions**
- LinkedIn has strict API access policies - may require app review
- **Mitigation**: Start with personal use case, consider alternative APIs if blocked, have manual posting fallback

**Risk 2: OAuth Complexity**
- OAuth 2.0 flow can be tricky to implement correctly
- **Mitigation**: Use proven libraries (passport-linkedin-oauth2), test thoroughly in sandbox, reference working examples

**Risk 3: Token Expiration**
- LinkedIn tokens expire and need refresh
- **Mitigation**: Implement automatic token refresh, add alerts for auth failures, document re-authentication process

**Risk 4: Rate Limiting**
- LinkedIn API has rate limits (varies by endpoint)
- **Mitigation**: Implement exponential backoff, queue posts if needed, add rate limit monitoring

**Risk 5: MCP Integration Issues**
- First MCP server implementation may have integration bugs
- **Mitigation**: Start simple, reference MCP examples, test with mock endpoints first

## Approval Required
**Yes** - The following steps need human approval:
1. Registering LinkedIn Developer App (step 2)
2. End-to-end testing with real LinkedIn post (step 8)

All other development and testing can proceed autonomously in development mode.

## Estimated Complexity
**Complex** (First MCP server + OAuth + External API)

## Alternative Approaches Considered

**Option A: Direct LinkedIn API in Python**
- Pro: Keep everything in Python with watchers
- Con: MCP is the proper architecture for Claude Code integrations

**Option B: Use third-party service (Buffer, Hootsuite API)**
- Pro: Simpler authentication, more features
- Con: Adds dependency, monthly cost, less control

**Option C: IFTTT/Zapier webhook integration**
- Pro: No code, quick setup
- Con: Not a true MCP server, doesn't fulfill Silver tier requirement

**Selected**: Option A (proper MCP server) - best for learning and extensibility

## Notes
- This is the first MCP server for the AI Employee system
- Success here creates template for future MCP servers (email, calendar, payments)
- Consider building in modular way for easy extension
- Reference: https://github.com/anthropics/anthropic-quickstarts (MCP examples)

## Resources
- LinkedIn Marketing API Docs: https://learn.microsoft.com/en-us/linkedin/
- MCP Specification: https://github.com/anthropics/anthropic-sdk-typescript
- OAuth 2.0 Guide: https://oauth.net/2/
- Node.js LinkedIn library: https://www.npmjs.com/package/linkedin-api-client

---

**Next Review**: 2026-02-08 (after research phase)
