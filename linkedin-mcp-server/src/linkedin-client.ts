/**
 * LinkedIn API Client
 * Handles posting to LinkedIn via the Posts API (2026)
 */

import axios, { AxiosInstance } from 'axios';

export interface LinkedInPost {
  commentary: string;
  visibility: 'PUBLIC' | 'CONNECTIONS' | 'LOGGED_IN';
}

export interface LinkedInPostResponse {
  id: string;
  url?: string;
}

export class LinkedInClient {
  private client: AxiosInstance;
  private accessToken: string;
  private personUrn: string;
  private dryRun: boolean;

  constructor(accessToken: string, personUrn: string, dryRun: boolean = false) {
    this.accessToken = accessToken;
    this.personUrn = personUrn;
    this.dryRun = dryRun;

    this.client = axios.create({
      baseURL: 'https://api.linkedin.com',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'LinkedIn-Version': '202210',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json'
      }
    });
  }

  /**
   * Create a post on LinkedIn
   */
  async createPost(post: LinkedInPost): Promise<LinkedInPostResponse> {
    // Validate post length
    if (post.commentary.length > 3000) {
      throw new Error('Post text exceeds LinkedIn maximum of 3,000 characters');
    }

    const postData = {
      author: this.personUrn,
      commentary: post.commentary,
      visibility: post.visibility || 'PUBLIC',
      distribution: {
        feedDistribution: 'MAIN_FEED'
      },
      lifecycleState: 'PUBLISHED'
    };

    // Dry run mode - log what would be posted
    if (this.dryRun) {
      console.log('[DRY RUN] Would post to LinkedIn:', JSON.stringify(postData, null, 2));
      return {
        id: 'dry-run-' + Date.now(),
        url: 'https://linkedin.com/feed/update/dry-run-post'
      };
    }

    // Real posting
    try {
      const response = await this.client.post('/rest/posts', postData);

      const postId = response.headers['x-restli-id'] || response.data.id;

      return {
        id: postId,
        url: `https://www.linkedin.com/feed/update/${postId}`
      };
    } catch (error: any) {
      if (error.response) {
        throw new Error(`LinkedIn API error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
      }
      throw new Error(`LinkedIn API request failed: ${error.message}`);
    }
  }

  /**
   * Get user profile information (for verification)
   */
  async getUserProfile(): Promise<any> {
    try {
      const response = await this.client.get('/v2/userinfo');
      return response.data;
    } catch (error: any) {
      throw new Error(`Failed to get user profile: ${error.message}`);
    }
  }

  /**
   * Verify access token is valid
   */
  async verifyToken(): Promise<boolean> {
    try {
      await this.getUserProfile();
      return true;
    } catch (error) {
      return false;
    }
  }
}
