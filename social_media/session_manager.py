"""
Session Manager - Persistent Browser Sessions
Login once, use forever with Playwright persistent context
"""

from playwright.sync_api import sync_playwright, Browser, BrowserContext
import os
from pathlib import Path
import time


class SessionManager:
    """Manages persistent browser sessions for social media platforms"""

    def __init__(self, platform: str, headless: bool = False):
        """
        Initialize session manager for a platform

        Args:
            platform: Platform name (linkedin, facebook)
            headless: Run browser in headless mode (default: False for first login)
        """
        self.platform = platform.lower()
        self.session_dir = Path(f"./session/{self.platform}")
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.playwright = None
        self.context = None

    def get_browser_context(self) -> BrowserContext:
        """
        Get or create persistent browser context

        Returns:
            BrowserContext: Playwright browser context with saved session
        """
        if self.context:
            return self.context

        self.playwright = sync_playwright().start()

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.session_dir),
            headless=self.headless,
            viewport={'width': 1280, 'height': 720},
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        return self.context

    def is_logged_in(self, page) -> bool:
        """
        Check if user is logged in to the platform

        Args:
            page: Playwright page object

        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            if self.platform == "linkedin":
                # Check for LinkedIn navigation bar
                page.goto("https://www.linkedin.com/feed/", timeout=10000)
                page.wait_for_load_state("networkidle", timeout=10000)
                return page.locator('[data-test-global-nav-me]').is_visible(timeout=5000)

            elif self.platform == "facebook":
                # Check for Facebook account menu
                page.goto("https://www.facebook.com/", timeout=10000)
                page.wait_for_load_state("networkidle", timeout=10000)
                return page.locator('[aria-label="Account"]').is_visible(timeout=5000) or \
                       page.locator('[aria-label="Your profile"]').is_visible(timeout=5000)

            return False

        except Exception as e:
            print(f"❌ Error checking login status: {e}")
            return False

    def setup_session(self):
        """
        Interactive session setup - guides user through first-time login
        """
        print(f"\n🔐 Setting up {self.platform.upper()} session...")
        print("=" * 60)

        context = self.get_browser_context()
        page = context.pages[0] if context.pages else context.new_page()

        if self.is_logged_in(page):
            print(f"✅ Already logged in to {self.platform.upper()}!")
            context.close()
            return True

        print(f"\n📝 Please log in to {self.platform.upper()} in the browser window")
        print("   The session will be saved automatically")
        print("   Press ENTER after you've logged in...")

        # Navigate to login page
        if self.platform == "linkedin":
            page.goto("https://www.linkedin.com/login")
        elif self.platform == "facebook":
            page.goto("https://www.facebook.com/login")

        # Wait for user to log in
        input()

        # Verify login
        if self.is_logged_in(page):
            print(f"✅ Successfully logged in to {self.platform.upper()}!")
            print(f"💾 Session saved to: {self.session_dir}")
            context.close()
            return True
        else:
            print(f"❌ Login verification failed for {self.platform.upper()}")
            print("   Please try again")
            context.close()
            return False

    def close(self):
        """Close browser context and playwright"""
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()


def main():
    """CLI for session setup"""
    import argparse

    parser = argparse.ArgumentParser(description='Social Media Session Manager')
    parser.add_argument('--platform', required=True, choices=['linkedin', 'facebook'],
                       help='Platform to setup')
    parser.add_argument('--setup', action='store_true',
                       help='Run interactive setup')

    args = parser.parse_args()

    manager = SessionManager(args.platform, headless=False)

    if args.setup:
        success = manager.setup_session()
        if success:
            print(f"\n🎉 {args.platform.upper()} session is ready!")
            print(f"   You can now use the automation system")
        else:
            print(f"\n❌ Setup failed. Please try again.")
    else:
        # Test existing session
        context = manager.get_browser_context()
        page = context.pages[0] if context.pages else context.new_page()

        if manager.is_logged_in(page):
            print(f"✅ {args.platform.upper()} session is valid")
        else:
            print(f"❌ {args.platform.upper()} session is invalid. Run with --setup")

        manager.close()


if __name__ == "__main__":
    main()
