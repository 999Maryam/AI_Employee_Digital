---
name: linkedin-post
description: Draft and schedule LinkedIn posts with professional formatting. Creates approval workflow, then executes via MCP server after approval. Use when user wants to post to LinkedIn.
when_to_use: User says "post to LinkedIn", "create LinkedIn post", "share on LinkedIn" OR scheduled posting task
---

# LinkedIn Post Skill

You are my AI Employee. Follow these steps to create and post to LinkedIn:

1. Read Company_Handbook.md and CLAUDE.md first for rules.
2. Understand the posting request:
   - What's the content/topic?
   - Is there a source file to reference?
   - What's the tone? (Professional, casual, thought leadership, announcement)
   - Are there hashtags, mentions, or links needed?
   - Is this scheduled or immediate?
3. Draft the LinkedIn post:
   - **Hook**: First line must grab attention
   - **Body**: 2-4 paragraphs, use line breaks for readability
   - **Call-to-Action**: What should readers do?
   - **Hashtags**: 3-5 relevant hashtags (research current trending if needed)
   - **Length**: 1,300-3,000 characters (LinkedIn's sweet spot)
4. Create approval file: Pending_Approval/LINKEDIN_POST_[YYYY-MM-DD]_[topic-slug].md

   Structure:
   ```markdown
   # LinkedIn Post for Approval
   **Date**: [Current Date]
   **Topic**: [Brief topic]
   **Tone**: [Professional/Casual/etc]
   **Status**: Awaiting Approval

   ---

   ## Post Content

   [Full post text exactly as it will appear]

   ---

   ## Metadata
   - **Hashtags**: #tag1 #tag2 #tag3
   - **Links**: [If any]
   - **Mentions**: [If any]
   - **Media**: [If images/videos attached]
   - **Schedule**: [Immediate / Date-Time]

   ## Notes
   [Any context for the approver]

   ---

   **To approve**: Move this file to Approved/
   **To reject**: Move this file to Needs_Action/ with edit notes
   ```

5. Update Dashboard.md under "## Pending Actions": "- LinkedIn post awaiting approval: [topic]"
6. Log in Logs/[current-date].md
7. Output: "LinkedIn post drafted and sent for approval. Check Pending_Approval/LINKEDIN_POST_[date]_[topic].md"

## After Approval (when file moves to Approved/)

8. When user runs /check-approvals and this file is in Approved/:
   - Read the approved post content
   - **[PLACEHOLDER FOR MCP SERVER]** - Execute LinkedIn API call via MCP server
   - For now: Log "Would post to LinkedIn: [first 50 chars]..."
   - Create success log in Logs/linkedin_posts_[YYYY-MM].md:
     ```markdown
     ## [Date Time]
     **Status**: Posted Successfully
     **Content**: [First 100 characters]...
     **Link**: [LinkedIn post URL if available]
     ```
   - Move file to Done/LINKEDIN_POSTED_[date]_[topic].md
   - Update Dashboard.md: "- Posted to LinkedIn: [topic]"

Rules:
- NEVER post without approval
- Maintain professional tone unless explicitly told otherwise
- Check character limits (max 3,000 characters)
- Avoid controversial topics without explicit user guidance
- Include relevant hashtags but don't overdo it (max 5)
- Line breaks improve readability - use them
- Emojis only if user requests or it fits brand voice

LinkedIn Best Practices:
- Start strong - first 2 lines show in feed before "see more"
- Use short paragraphs (1-2 sentences)
- Ask questions to drive engagement
- Include personal experience or stories
- Tag relevant people/companies when appropriate
- Post during business hours (9am-5pm local time preferred)

Examples:
- Input: "Post about our new product launch" → Draft announcement post with features, benefits, CTA
- Input: "Share my article about AI automation" → Draft thought leadership post with article link, key takeaways
- Input: "Weekly team win celebration" → Draft casual but professional team recognition post

## Integration Notes
**MCP Server Required**: For actual posting, you'll need to implement a LinkedIn MCP server with OAuth authentication. Until then, this skill creates properly formatted drafts ready for manual posting or future automation.
