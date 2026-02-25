#!/usr/bin/env node

/**
 * LinkedIn MCP Server
 * Enables Claude Code to post to LinkedIn via Model Context Protocol
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { LinkedInClient, LinkedInPost } from './linkedin-client.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Validate required environment variables
const LINKEDIN_ACCESS_TOKEN = process.env.LINKEDIN_ACCESS_TOKEN;
const LINKEDIN_PERSON_URN = process.env.LINKEDIN_PERSON_URN;
const DRY_RUN = process.env.DRY_RUN === 'true';

if (!LINKEDIN_ACCESS_TOKEN) {
  console.error('Error: LINKEDIN_ACCESS_TOKEN environment variable is required');
  process.exit(1);
}

if (!LINKEDIN_PERSON_URN) {
  console.error('Error: LINKEDIN_PERSON_URN environment variable is required');
  console.error('Format: urn:li:person:YOUR_ID');
  process.exit(1);
}

// Initialize LinkedIn client
const linkedInClient = new LinkedInClient(
  LINKEDIN_ACCESS_TOKEN,
  LINKEDIN_PERSON_URN,
  DRY_RUN
);

// Define tool schemas using Zod
const PostToLinkedInSchema = z.object({
  commentary: z.string().max(3000).describe('The text content of the post (max 3000 characters)'),
  visibility: z.enum(['PUBLIC', 'CONNECTIONS', 'LOGGED_IN']).default('PUBLIC').describe('Post visibility setting')
});

// Define available tools
const tools: Tool[] = [
  {
    name: 'post_to_linkedin',
    description: 'Create and publish a post to LinkedIn. Posts can be up to 3,000 characters and support PUBLIC, CONNECTIONS, or LOGGED_IN visibility.',
    inputSchema: {
      type: 'object',
      properties: {
        commentary: {
          type: 'string',
          description: 'The text content of the post',
          maxLength: 3000
        },
        visibility: {
          type: 'string',
          enum: ['PUBLIC', 'CONNECTIONS', 'LOGGED_IN'],
          default: 'PUBLIC',
          description: 'Who can see this post'
        }
      },
      required: ['commentary']
    }
  },
  {
    name: 'verify_linkedin_connection',
    description: 'Verify that the LinkedIn API connection is working and the access token is valid.',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  }
];

// Create MCP server instance
const server = new Server(
  {
    name: 'linkedin-mcp-server',
    version: '1.0.0'
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools
  };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'post_to_linkedin') {
      // Validate arguments
      const validated = PostToLinkedInSchema.parse(args);

      // Create post
      const post: LinkedInPost = {
        commentary: validated.commentary,
        visibility: validated.visibility
      };

      const result = await linkedInClient.createPost(post);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              postId: result.id,
              postUrl: result.url,
              message: DRY_RUN
                ? 'DRY RUN: Post would be published to LinkedIn'
                : 'Post successfully published to LinkedIn',
              characterCount: validated.commentary.length,
              visibility: validated.visibility
            }, null, 2)
          }
        ]
      };
    }

    if (name === 'verify_linkedin_connection') {
      const isValid = await linkedInClient.verifyToken();

      if (isValid) {
        const profile = await linkedInClient.getUserProfile();
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                success: true,
                connected: true,
                message: 'LinkedIn connection verified',
                profile: {
                  name: profile.name,
                  email: profile.email,
                  sub: profile.sub
                },
                mode: DRY_RUN ? 'DRY RUN' : 'LIVE'
              }, null, 2)
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                success: false,
                connected: false,
                message: 'LinkedIn connection failed - access token may be invalid or expired'
              }, null, 2)
            }
          ],
          isError: true
        };
      }
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error: any) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: false,
            error: error.message
          }, null, 2)
        }
      ],
      isError: true
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('LinkedIn MCP Server running on stdio');
  console.error(`Mode: ${DRY_RUN ? 'DRY RUN (no actual posting)' : 'LIVE'}`);
  console.error('Available tools: post_to_linkedin, verify_linkedin_connection');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
