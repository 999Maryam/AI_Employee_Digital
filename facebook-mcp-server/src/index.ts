#!/usr/bin/env node

/**
 * Facebook MCP Server
 *
 * Model Context Protocol server for Facebook automation
 * Provides tools for posting, managing content, and analytics
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import dotenv from 'dotenv';
import { FacebookClient } from './facebook-client.js';

// Load environment variables
dotenv.config();

// Validate required environment variables
const FACEBOOK_ACCESS_TOKEN = process.env.FACEBOOK_ACCESS_TOKEN;
const DRY_RUN = process.env.DRY_RUN === 'true';
const DEBUG = process.env.DEBUG === 'true';
const FACEBOOK_API_VERSION = process.env.FACEBOOK_API_VERSION || 'v19.0';
const FACEBOOK_PAGE_ID = process.env.FACEBOOK_PAGE_ID;

if (!FACEBOOK_ACCESS_TOKEN) {
  console.error('ERROR: FACEBOOK_ACCESS_TOKEN environment variable is required');
  console.error('Please set it in your .env file or environment');
  process.exit(1);
}

// Initialize Facebook client
const facebookClient = new FacebookClient(FACEBOOK_ACCESS_TOKEN, {
  dryRun: DRY_RUN,
  debug: DEBUG,
  apiVersion: FACEBOOK_API_VERSION,
  pageId: FACEBOOK_PAGE_ID,
});

// Zod schemas for input validation
const CreatePostSchema = z.object({
  message: z.string().min(1).describe('The text content of the post'),
  link: z.string().url().optional().describe('Optional link to share'),
  scheduled_publish_time: z.number().optional().describe('Unix timestamp for scheduled post'),
});

const CreatePhotoPostSchema = z.object({
  url: z.string().url().describe('URL of the image to post'),
  caption: z.string().optional().describe('Caption for the photo'),
});

const GetPostSchema = z.object({
  post_id: z.string().describe('The Facebook post ID'),
});

const DeletePostSchema = z.object({
  post_id: z.string().describe('The Facebook post ID to delete'),
});

const GetPostsSchema = z.object({
  limit: z.number().min(1).max(100).default(10).describe('Number of posts to retrieve (max 100)'),
});

const GetPostInsightsSchema = z.object({
  post_id: z.string().describe('The Facebook post ID'),
});

// Initialize MCP server
const server = new Server(
  {
    name: 'facebook-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'create_facebook_post',
        description: 'Create a new text post on Facebook (profile or page)',
        inputSchema: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              description: 'The text content of the post',
            },
            link: {
              type: 'string',
              description: 'Optional link to share in the post',
            },
            scheduled_publish_time: {
              type: 'number',
              description: 'Optional Unix timestamp for scheduled post (Pages only)',
            },
          },
          required: ['message'],
        },
      },
      {
        name: 'create_facebook_photo_post',
        description: 'Create a new photo post on Facebook with optional caption',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'URL of the image to post (must be publicly accessible)',
            },
            caption: {
              type: 'string',
              description: 'Optional caption for the photo',
            },
          },
          required: ['url'],
        },
      },
      {
        name: 'get_facebook_post',
        description: 'Get details of a specific Facebook post including engagement metrics',
        inputSchema: {
          type: 'object',
          properties: {
            post_id: {
              type: 'string',
              description: 'The Facebook post ID',
            },
          },
          required: ['post_id'],
        },
      },
      {
        name: 'delete_facebook_post',
        description: 'Delete a Facebook post',
        inputSchema: {
          type: 'object',
          properties: {
            post_id: {
              type: 'string',
              description: 'The Facebook post ID to delete',
            },
          },
          required: ['post_id'],
        },
      },
      {
        name: 'get_facebook_posts',
        description: 'Get recent Facebook posts from profile or page',
        inputSchema: {
          type: 'object',
          properties: {
            limit: {
              type: 'number',
              description: 'Number of posts to retrieve (1-100, default: 10)',
              default: 10,
            },
          },
        },
      },
      {
        name: 'get_facebook_pages',
        description: 'Get list of Facebook pages you manage',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'get_facebook_profile',
        description: 'Get your Facebook profile information',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'get_facebook_post_insights',
        description: 'Get analytics/insights for a Facebook post (Pages only)',
        inputSchema: {
          type: 'object',
          properties: {
            post_id: {
              type: 'string',
              description: 'The Facebook post ID',
            },
          },
          required: ['post_id'],
        },
      },
      {
        name: 'test_facebook_connection',
        description: 'Test the Facebook API connection',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args } = request.params;

    switch (name) {
      case 'create_facebook_post': {
        const parsed = CreatePostSchema.parse(args);
        const result = await facebookClient.createPost({
          message: parsed.message,
          link: parsed.link,
          scheduled_publish_time: parsed.scheduled_publish_time,
        });

        return {
          content: [
            {
              type: 'text',
              text: DRY_RUN
                ? `[DRY RUN] Facebook post created successfully!\n\nPost ID: ${result.id}\nMessage: ${result.message}\nPermalink: ${result.permalink_url}\n\nNote: This was a test. No actual post was made.`
                : `Facebook post created successfully! 🎉\n\nPost ID: ${result.id}\nPermalink: ${result.permalink_url}\n\nEngagement:\n- Reactions: ${result.reactions?.summary?.total_count || 0}\n- Comments: ${result.comments?.summary?.total_count || 0}\n- Shares: ${result.shares?.count || 0}`,
            },
          ],
        };
      }

      case 'create_facebook_photo_post': {
        const parsed = CreatePhotoPostSchema.parse(args);
        const result = await facebookClient.createPhotoPost({
          url: parsed.url,
          caption: parsed.caption,
        });

        return {
          content: [
            {
              type: 'text',
              text: DRY_RUN
                ? `[DRY RUN] Facebook photo post created successfully!\n\nPhoto ID: ${result.id}\nPost ID: ${result.post_id}\nPermalink: ${result.permalink_url}\n\nNote: This was a test. No actual photo was posted.`
                : `Facebook photo post created successfully! 🎉\n\nPhoto ID: ${result.id}\nPost ID: ${result.post_id}\nPermalink: ${result.permalink_url}`,
            },
          ],
        };
      }

      case 'get_facebook_post': {
        const parsed = GetPostSchema.parse(args);
        const result = await facebookClient.getPost(parsed.post_id);

        return {
          content: [
            {
              type: 'text',
              text: `Post Details:\n\nID: ${result.id}\nMessage: ${result.message || 'No text'}\nCreated: ${result.created_time}\nPermalink: ${result.permalink_url}\n\nEngagement:\n- Reactions: ${result.reactions?.summary?.total_count || 0}\n- Comments: ${result.comments?.summary?.total_count || 0}\n- Shares: ${result.shares?.count || 0}`,
            },
          ],
        };
      }

      case 'delete_facebook_post': {
        const parsed = DeletePostSchema.parse(args);
        await facebookClient.deletePost(parsed.post_id);

        return {
          content: [
            {
              type: 'text',
              text: DRY_RUN
                ? `[DRY RUN] Would delete post ${parsed.post_id}\n\nNote: This was a test. No post was deleted.`
                : `Post ${parsed.post_id} deleted successfully! ✅`,
            },
          ],
        };
      }

      case 'get_facebook_posts': {
        const parsed = GetPostsSchema.parse(args);
        const results = await facebookClient.getPosts(parsed.limit);

        const postsText = results
          .map(
            (post, i) =>
              `${i + 1}. Post ID: ${post.id}\n   Message: ${post.message?.substring(0, 100) || 'No text'}${post.message && post.message.length > 100 ? '...' : ''}\n   Created: ${post.created_time}\n   Reactions: ${post.reactions?.summary?.total_count || 0} | Comments: ${post.comments?.summary?.total_count || 0} | Shares: ${post.shares?.count || 0}\n   Link: ${post.permalink_url}`
          )
          .join('\n\n');

        return {
          content: [
            {
              type: 'text',
              text: `Found ${results.length} posts:\n\n${postsText || 'No posts found'}`,
            },
          ],
        };
      }

      case 'get_facebook_pages': {
        const results = await facebookClient.getPages();

        const pagesText = results
          .map(
            (page, i) =>
              `${i + 1}. ${page.name}\n   ID: ${page.id}\n   Category: ${page.category || 'N/A'}\n   Fans: ${page.fan_count || 0}`
          )
          .join('\n\n');

        return {
          content: [
            {
              type: 'text',
              text: `Found ${results.length} pages:\n\n${pagesText || 'No pages found'}`,
            },
          ],
        };
      }

      case 'get_facebook_profile': {
        const result = await facebookClient.getProfile();

        return {
          content: [
            {
              type: 'text',
              text: `Facebook Profile:\n\nID: ${result.id}\nName: ${result.name}\nEmail: ${result.email || 'Not available'}`,
            },
          ],
        };
      }

      case 'get_facebook_post_insights': {
        const parsed = GetPostInsightsSchema.parse(args);
        const result = await facebookClient.getPostInsights(parsed.post_id);

        if (!result) {
          return {
            content: [
              {
                type: 'text',
                text: 'Post insights are not available. This feature requires:\n1. A Facebook Page (not personal profile)\n2. Page access token\n3. Sufficient permissions',
              },
            ],
          };
        }

        return {
          content: [
            {
              type: 'text',
              text: `Post Insights:\n\n${JSON.stringify(result, null, 2)}`,
            },
          ],
        };
      }

      case 'test_facebook_connection': {
        const isConnected = await facebookClient.testConnection();

        return {
          content: [
            {
              type: 'text',
              text: isConnected
                ? `✅ Facebook connection successful!\n\nMode: ${DRY_RUN ? 'DRY RUN (test mode)' : 'LIVE'}\nAPI Version: ${FACEBOOK_API_VERSION}\nPage ID: ${FACEBOOK_PAGE_ID || 'Not configured (posting to profile)'}`
                : '❌ Facebook connection failed. Please check your access token and permissions.',
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error: any) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  if (DEBUG) {
    console.error('[FacebookMCP] Server started successfully');
    console.error(`[FacebookMCP] Mode: ${DRY_RUN ? 'DRY RUN' : 'LIVE'}`);
    console.error(`[FacebookMCP] API Version: ${FACEBOOK_API_VERSION}`);
  }
}

main().catch((error) => {
  console.error('[FacebookMCP] Fatal error:', error);
  process.exit(1);
});
