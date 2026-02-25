/**
 * OAuth 2.0 Authentication Handler for LinkedIn
 */

import axios from 'axios';

export interface OAuthConfig {
  clientId: string;
  clientSecret: string;
  redirectUri: string;
}

export interface TokenResponse {
  access_token: string;
  expires_in: number;
  refresh_token?: string;
  scope: string;
}

export class LinkedInOAuth {
  private config: OAuthConfig;

  constructor(config: OAuthConfig) {
    this.config = config;
  }

  /**
   * Generate authorization URL for user to grant access
   */
  getAuthorizationUrl(state?: string): string {
    const params = new URLSearchParams({
      response_type: 'code',
      client_id: this.config.clientId,
      redirect_uri: this.config.redirectUri,
      scope: 'openid profile email w_member_social',
      state: state || Math.random().toString(36).substring(7)
    });

    return `https://www.linkedin.com/oauth/v2/authorization?${params.toString()}`;
  }

  /**
   * Exchange authorization code for access token
   */
  async exchangeCodeForToken(code: string): Promise<TokenResponse> {
    try {
      const response = await axios.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        null,
        {
          params: {
            grant_type: 'authorization_code',
            code: code,
            redirect_uri: this.config.redirectUri,
            client_id: this.config.clientId,
            client_secret: this.config.clientSecret
          }
        }
      );

      return response.data;
    } catch (error: any) {
      throw new Error(`OAuth token exchange failed: ${error.message}`);
    }
  }

  /**
   * Refresh an expired access token
   */
  async refreshAccessToken(refreshToken: string): Promise<TokenResponse> {
    try {
      const response = await axios.post(
        'https://www.linkedin.com/oauth/v2/accessToken',
        null,
        {
          params: {
            grant_type: 'refresh_token',
            refresh_token: refreshToken,
            client_id: this.config.clientId,
            client_secret: this.config.clientSecret
          }
        }
      );

      return response.data;
    } catch (error: any) {
      throw new Error(`Token refresh failed: ${error.message}`);
    }
  }

  /**
   * Get user's person URN (needed for posting)
   */
  async getPersonUrn(accessToken: string): Promise<string> {
    try {
      const response = await axios.get('https://api.linkedin.com/v2/userinfo', {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      return `urn:li:person:${response.data.sub}`;
    } catch (error: any) {
      throw new Error(`Failed to get person URN: ${error.message}`);
    }
  }
}
