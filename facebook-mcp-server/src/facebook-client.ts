/**
 * Facebook Graph API Client
 *
 * Handles Facebook Graph API operations for posting and managing content
 */

import axios, { AxiosInstance } from 'axios';

export interface FacebookPost {
  message: string;
  link?: string;
  photo?: string;
  published?: boolean;
  scheduled_publish_time?: number;
}

export interface FacebookPostResponse {
  id: string;
  message?: string;
  created_time?: string;
  permalink_url?: string;
  shares?: {
    count: number;
  };
  reactions?: {
    summary: {
      total_count: number;
    };
  };
  comments?: {
    summary: {
      total_count: number;
    };
  };
}

export interface FacebookPhoto {
  url: string;
  caption?: string;
  published?: boolean;
}

export interface FacebookPhotoResponse {
  id: string;
  post_id?: string;
  permalink_url?: string;
}

export interface PageInfo {
  id: string;
  name: string;
  access_token?: string;
  category?: string;
  fan_count?: number;
}

export class FacebookClient {
  private client: AxiosInstance;
  private dryRun: boolean;
  private debug: boolean;
  private apiVersion: string;
  private pageId?: string;

  constructor(
    accessToken: string,
    options: {
      dryRun?: boolean;
      debug?: boolean;
      apiVersion?: string;
      pageId?: string;
    } = {}
  ) {
    this.dryRun = options.dryRun ?? false;
    this.debug = options.debug ?? false;
    this.apiVersion = options.apiVersion ?? 'v19.0';
    this.pageId = options.pageId;

    this.client = axios.create({
      baseURL: `https://graph.facebook.com/${this.apiVersion}`,
      params: {
        access_token: accessToken,
      },
    });

    if (this.debug) {
      console.log('[FacebookClient] Initialized', {
        dryRun: this.dryRun,
        apiVersion: this.apiVersion,
        hasPageId: !!this.pageId,
      });
    }
  }

  /**
   * Create a text post
   */
  async createPost(post: FacebookPost): Promise<FacebookPostResponse> {
    if (this.debug) {
      console.log('[FacebookClient] createPost called', { post, dryRun: this.dryRun });
    }

    if (this.dryRun) {
      console.log('[DRY RUN] Would create Facebook post:', post.message);
      return {
        id: `dry_run_${Date.now()}`,
        message: post.message,
        created_time: new Date().toISOString(),
        permalink_url: 'https://facebook.com/dry_run_post',
        shares: { count: 0 },
        reactions: { summary: { total_count: 0 } },
        comments: { summary: { total_count: 0 } },
      };
    }

    try {
      const endpoint = this.pageId ? `/${this.pageId}/feed` : '/me/feed';

      const payload: any = {
        message: post.message,
      };

      if (post.link) {
        payload.link = post.link;
      }

      if (post.published !== undefined) {
        payload.published = post.published;
      }

      if (post.scheduled_publish_time) {
        payload.scheduled_publish_time = post.scheduled_publish_time;
        payload.published = false;
      }

      const response = await this.client.post(endpoint, null, {
        params: payload,
      });

      if (this.debug) {
        console.log('[FacebookClient] Post created successfully', response.data);
      }

      // Get full post details
      return await this.getPost(response.data.id);
    } catch (error: any) {
      if (this.debug) {
        console.error('[FacebookClient] Error creating post:', error.response?.data || error.message);
      }
      throw new Error(
        `Failed to create Facebook post: ${error.response?.data?.error?.message || error.message}`
      );
    }
  }

  /**
   * Create a photo post
   */
  async createPhotoPost(photo: FacebookPhoto): Promise<FacebookPhotoResponse> {
    if (this.debug) {
      console.log('[FacebookClient] createPhotoPost called', { photo, dryRun: this.dryRun });
    }

    if (this.dryRun) {
      console.log('[DRY RUN] Would create Facebook photo post:', photo.url);
      return {
        id: `dry_run_photo_${Date.now()}`,
        post_id: `dry_run_post_${Date.now()}`,
        permalink_url: 'https://facebook.com/dry_run_photo',
      };
    }

    try {
      const endpoint = this.pageId ? `/${this.pageId}/photos` : '/me/photos';

      const payload: any = {
        url: photo.url,
      };

      if (photo.caption) {
        payload.caption = photo.caption;
      }

      if (photo.published !== undefined) {
        payload.published = photo.published;
      }

      const response = await this.client.post(endpoint, null, {
        params: payload,
      });

      if (this.debug) {
        console.log('[FacebookClient] Photo post created successfully', response.data);
      }

      return response.data;
    } catch (error: any) {
      if (this.debug) {
        console.error('[FacebookClient] Error creating photo post:', error.response?.data || error.message);
      }
      throw new Error(
        `Failed to create Facebook photo post: ${error.response?.data?.error?.message || error.message}`
      );
    }
  }

  /**
   * Get a post by ID
   */
  async getPost(postId: string): Promise<FacebookPostResponse> {
    if (this.debug) {
      console.log('[FacebookClient] getPost called', { postId });
    }

    if (this.dryRun) {
      console.log('[DRY RUN] Would get Facebook post:', postId);
      return {
        id: postId,
        message: 'This is a dry run post',
        created_time: new Date().toISOString(),
        permalink_url: `https://facebook.com/post/${postId}`,
        shares: { count: 5 },
        reactions: { summary: { total_count: 25 } },
        comments: { summary: { total_count: 3 } },
      };
    }

    try {
      const response = await this.client.get(`/${postId}`, {
        params: {
          fields: 'id,message,created_time,permalink_url,shares,reactions.summary(true),comments.summary(true)',
        },
      });

      return response.data;
    } catch (error: any) {
      if (this.debug) {
        console.error('[FacebookClient] Error getting post:', error.response?.data || error.message);
      }
      throw new Error(
        `Failed to get Facebook post: ${error.response?.data?.error?.message || error.message}`
      );
    }
  }

  /**
   * Delete a post
   */
  async deletePost(postId: string): Promise<boolean> {
    if (this.debug) {
      console.log('[FacebookClient] deletePost called', { postId, dryRun: this.dryRun });
    }

    if (this.dryRun) {
      console.log('[DRY RUN] Would delete Facebook post:', postId);
      return true;
    }

    try {
      await this.client.delete(`/${postId}`);

      if (this.debug) {
        console.log('[FacebookClient] Post deleted successfully');
      }

      return true;
    } catch (error: any) {
      if (this.debug) {
        console.error('[FacebookClient] Error deleting post:', error.response?.data || error.message);
      }
      throw new Error(
        `Failed to delete Facebook post: ${error.response?.data?.error?.message || error.message}`
      );
    }
  }

  /**
   * Get user's posts
   */
  async getPosts(limit: number = 10): Promise<FacebookPostResponse[]> {
    if (this.debug) {
      console.log('[FacebookClient] getPosts called', { limit });
    }

    if (this.dryRun) {
      console.log('[DRY RUN] Would get Facebook posts');
      return Array.from({ length: Math.min(limit, 3) }, (_, i) => ({
        id: `dry_run_post_${i}`,
        message: `This is dry run post ${i + 1}`,
        created_time: new Date(Date.now() - i * 86400000).toISOString(),
        permalink_url: `https://facebook.com/post/${i}`,
        shares: { count: i * 2 },
        reactions: { summary: { total_count: i * 10 } },
        comments: { summary: { total_count: i } },
      }));
    }

    try {
      const endpoint = this.pageId ? `/${this.pageId}/posts` : '/me/posts';

      const response = await this.client.get(endpoint, {
        params: {
          fields: 'id,message,created_time,permalink_url,shares,reactions.summary(true),comments.summary(true)',
          limit: Math.min(limit, 100),
        },
      });

      return response.data.data || [];
    } catch (error: any) {
      if (this.debug) {
        console.error('[FacebookClient] Error getting posts:', error.response?.data || error.message);
      }
      throw new Error(
        `Failed to get Facebook posts: ${error.response?.data?.error?.message || error.message}`
      );
    }
  }

  /**
   * Get user's pages (if any)
   */
  async getPages(): Promise<PageInfo[]> {
    if (this.debug) {
      console.log('[FacebookClient] getPages called');
    }

    if (this.dryRun) {
      console.log('[DRY RUN] Would get Facebook pages');
      return [
        {
          id: 'dry_run_page_1',
          name: 'Dry Run Page',
          category: 'Company',
          fan_count: 1000,
        },
      ];
    }

    try {
      const response = await this.client.get('/me/accounts', {
        params: {
          fields: 'id,name,access_token,category,fan_count',
        },
      });

      return response.data.data || [];
    } catch (error: any) {
      if (this.debug) {
        console.error('[FacebookClient] Error getting pages:', error.response?.data || error.message);
      }
      throw new Error(
        `Failed to get Facebook pages: ${error.response?.data?.error?.message || error.message}`
      );
    }
  }

  /**
   * Get user profile information
   */
  async getProfile(): Promise<{ id: string; name: string; email?: string }> {
    if (this.debug) {
      console.log('[FacebookClient] getProfile called');
    }

    if (this.dryRun) {
      console.log('[DRY RUN] Would get user profile');
      return {
        id: 'dry_run_user_id',
        name: 'Dry Run User',
        email: 'dryrun@example.com',
      };
    }

    try {
      const response = await this.client.get('/me', {
        params: {
          fields: 'id,name,email',
        },
      });

      return response.data;
    } catch (error: any) {
      if (this.debug) {
        console.error('[FacebookClient] Error getting profile:', error.response?.data || error.message);
      }
      throw new Error(
        `Failed to get Facebook profile: ${error.response?.data?.error?.message || error.message}`
      );
    }
  }

  /**
   * Test Facebook connection
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.getProfile();
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get post insights (analytics) - Pages only
   */
  async getPostInsights(postId: string): Promise<any> {
    if (this.debug) {
      console.log('[FacebookClient] getPostInsights called', { postId });
    }

    if (this.dryRun) {
      console.log('[DRY RUN] Would get post insights');
      return {
        impressions: 250,
        reach: 180,
        engagement: 45,
      };
    }

    try {
      const response = await this.client.get(`/${postId}/insights`, {
        params: {
          metric: 'post_impressions,post_engaged_users,post_clicks',
        },
      });

      return response.data.data;
    } catch (error: any) {
      if (this.debug) {
        console.error('[FacebookClient] Error getting insights:', error.response?.data || error.message);
      }
      // Insights might not be available for all posts
      return null;
    }
  }
}
