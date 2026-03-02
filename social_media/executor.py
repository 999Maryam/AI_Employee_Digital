"""
Social Media Executor - The Muscle
Executes actual posting to LinkedIn, Facebook, Odoo using browser automation
"""

from playwright.sync_api import TimeoutError, Page
import time
import os
import random
import logging
import xmlrpc.client
from pathlib import Path
from datetime import datetime
from .session_manager import SessionManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Dry-run mode
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'


class SocialMediaExecutor:
    """Executes social media posts with error handling and screenshots"""

    def __init__(self, platform: str):
        """
        Initialize executor for a platform

        Args:
            platform: Platform name (linkedin, facebook, odoo)
        """
        self.platform = platform.lower()

        if self.platform != 'odoo':
            self.session_manager = SessionManager(self.platform, headless=True)

        self.log_dir = Path("./Logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Odoo credentials
        if self.platform == 'odoo':
            self.odoo_url = os.getenv('ODOO_URL')
            self.odoo_db = os.getenv('ODOO_DB')
            self.odoo_user = os.getenv('ODOO_USER')
            self.odoo_password = os.getenv('ODOO_PASSWORD')

        logger.info(f"🔧 Executor initialized for {platform.upper()}")
        if DRY_RUN:
            logger.info("⚠️  DRY_RUN mode enabled - no actual posts will be made")

    def post_to_linkedin(self, content: str, image_path: str = None) -> dict:
        """
        Post content to LinkedIn

        Args:
            content: Post text content
            image_path: Optional path to image file

        Returns:
            dict: Result with success status and details
        """
        if DRY_RUN:
            logger.info(f"🔵 [DRY-RUN] Would post to LinkedIn:")
            logger.info(f"   Content: {content[:100]}...")
            if image_path:
                logger.info(f"   Image: {image_path}")
            return {
                "success": True,
                "platform": "LinkedIn",
                "timestamp": datetime.now().isoformat(),
                "dry_run": True
            }

        context = None
        try:
            logger.info(f"🔵 Posting to LinkedIn...")

            context = self.session_manager.get_browser_context()
            page = context.pages[0] if context.pages else context.new_page()

            # Navigate to LinkedIn feed
            page.goto("https://www.linkedin.com/feed/", timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # Anti-detection delay
            time.sleep(random.uniform(2, 4))

            # Verify login
            if not self.session_manager.is_logged_in(page):
                raise Exception("Not logged in to LinkedIn. Run session setup first.")

            # Click "Start a post" button with multiple fallback selectors
            start_post_selectors = [
                'button:has-text("Start a post")',
                '[aria-label="Start a post"]',
                '.share-box-feed-entry__trigger',
                '[data-test-share-box-trigger]',
                'button[aria-label="Open share box"]'
            ]

            clicked = False
            for selector in start_post_selectors:
                try:
                    page.click(selector, timeout=3000)
                    clicked = True
                    logger.debug(f"✓ Clicked using selector: {selector}")
                    break
                except:
                    continue

            if not clicked:
                self._save_error_screenshot(page, "linkedin_no_start_button")
                raise Exception("Could not find 'Start a post' button")

            # Wait for editor to appear
            page.wait_for_selector('.ql-editor', timeout=5000)
            time.sleep(random.uniform(1, 2))

            # Fill content
            editor = page.locator('.ql-editor').first
            editor.click()
            time.sleep(0.5)
            editor.fill(content)
            time.sleep(random.uniform(1, 2))

            logger.info(f"✓ Content filled ({len(content)} chars)")

            # Upload image if provided
            if image_path and os.path.exists(image_path):
                try:
                    logger.info(f"📸 Uploading image: {image_path}")

                    # Click image upload button with fallbacks
                    image_selectors = [
                        '[aria-label="Add a photo"]',
                        'button:has-text("Add a photo")',
                        '[data-test-media-upload-button]'
                    ]

                    for selector in image_selectors:
                        try:
                            page.click(selector, timeout=3000)
                            break
                        except:
                            continue

                    time.sleep(1)

                    # Upload file
                    page.set_input_files('input[type="file"]', image_path)
                    time.sleep(random.uniform(3, 5))  # Wait for upload

                    logger.info(f"✓ Image uploaded successfully")

                except Exception as e:
                    logger.warning(f"⚠️ Image upload failed: {e}")

            # Anti-detection delay before posting
            time.sleep(random.uniform(2, 3))

            # Click Post button with multiple fallback selectors
            post_button_selectors = [
                'button:has-text("Post")',
                '[aria-label="Post"]',
                '.share-actions__primary-action',
                '[data-test-share-button]'
            ]

            posted = False
            for selector in post_button_selectors:
                try:
                    page.click(selector, timeout=3000)
                    posted = True
                    logger.debug(f"✓ Posted using selector: {selector}")
                    break
                except:
                    continue

            if not posted:
                self._save_error_screenshot(page, "linkedin_no_post_button")
                raise Exception("Could not find Post button")

            # Wait for post to complete
            time.sleep(5)

            logger.info(f"✅ Successfully posted to LinkedIn")

            return {
                "success": True,
                "platform": "LinkedIn",
                "timestamp": datetime.now().isoformat(),
                "content_length": len(content),
                "has_image": image_path is not None
            }

        except Exception as e:
            logger.error(f"❌ LinkedIn posting failed: {e}", exc_info=True)
            if context:
                page = context.pages[0] if context.pages else None
                if page:
                    self._save_error_screenshot(page, "linkedin")

            return {
                "success": False,
                "platform": "LinkedIn",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

        finally:
            if context:
                context.close()

    def post_to_facebook(self, content: str, image_path: str = None) -> dict:
        """
        Post content to Facebook

        Args:
            content: Post text content
            image_path: Optional path to image file

        Returns:
            dict: Result with success status and details
        """
        if DRY_RUN:
            logger.info(f"🔵 [DRY-RUN] Would post to Facebook:")
            logger.info(f"   Content: {content[:100]}...")
            if image_path:
                logger.info(f"   Image: {image_path}")
            return {
                "success": True,
                "platform": "Facebook",
                "timestamp": datetime.now().isoformat(),
                "dry_run": True
            }

        context = None
        try:
            logger.info(f"🔵 Posting to Facebook...")

            context = self.session_manager.get_browser_context()
            page = context.pages[0] if context.pages else context.new_page()

            # Navigate to Facebook
            page.goto("https://www.facebook.com/", timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)

            # Anti-detection delay
            time.sleep(random.uniform(2, 4))

            # Verify login
            if not self.session_manager.is_logged_in(page):
                raise Exception("Not logged in to Facebook. Run session setup first.")

            # Click "What's on your mind?" area with fallbacks
            create_post_selectors = [
                '[aria-label="Create a post"]',
                '[role="button"]:has-text("What\'s on your mind")',
                'div[role="button"]:has-text("Write something")',
                '.x1i10hfl.xjbqb8w'
            ]

            clicked = False
            for selector in create_post_selectors:
                try:
                    page.click(selector, timeout=3000)
                    clicked = True
                    logger.debug(f"✓ Clicked using selector: {selector}")
                    break
                except:
                    continue

            if not clicked:
                self._save_error_screenshot(page, "facebook_no_create_button")
                raise Exception("Could not find create post button")

            # Wait for post dialog
            time.sleep(random.uniform(2, 3))

            # Type content using keyboard (more reliable than fill)
            page.keyboard.type(content, delay=random.randint(30, 80))
            time.sleep(random.uniform(1, 2))

            logger.info(f"✓ Content typed ({len(content)} chars)")

            # Upload image if provided
            if image_path and os.path.exists(image_path):
                try:
                    logger.info(f"📸 Uploading image: {image_path}")

                    # Find and click photo/video button
                    photo_selectors = [
                        '[aria-label="Photo/video"]',
                        'div[aria-label="Photo/video"]',
                        '[role="button"]:has-text("Photo/video")'
                    ]

                    for selector in photo_selectors:
                        try:
                            page.click(selector, timeout=3000)
                            break
                        except:
                            continue

                    time.sleep(1)

                    # Upload file
                    page.set_input_files('input[type="file"]', image_path)
                    time.sleep(random.uniform(3, 5))  # Wait for upload and preview

                    logger.info(f"✓ Image uploaded successfully")

                except Exception as e:
                    logger.warning(f"⚠️ Image upload failed: {e}")

            # Wait for preview to load
            time.sleep(random.uniform(2, 3))

            # Click Post button with multiple fallback selectors
            post_button_selectors = [
                'div[aria-label="Post"]',
                '[role="button"]:has-text("Post")',
                '[aria-label="Share"]',
                'div[role="button"]:has-text("Post")'
            ]

            posted = False
            for selector in post_button_selectors:
                try:
                    page.click(selector, timeout=3000)
                    posted = True
                    logger.debug(f"✓ Posted using selector: {selector}")
                    break
                except:
                    continue

            if not posted:
                self._save_error_screenshot(page, "facebook_no_post_button")
                raise Exception("Could not find Post button")

            # Wait for post to complete
            time.sleep(5)

            logger.info(f"✅ Successfully posted to Facebook")

            return {
                "success": True,
                "platform": "Facebook",
                "timestamp": datetime.now().isoformat(),
                "content_length": len(content),
                "has_image": image_path is not None
            }

        except Exception as e:
            logger.error(f"❌ Facebook posting failed: {e}", exc_info=True)
            if context:
                page = context.pages[0] if context.pages else None
                if page:
                    self._save_error_screenshot(page, "facebook")

            return {
                "success": False,
                "platform": "Facebook",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

        finally:
            if context:
                context.close()

    def create_odoo_invoice(self, customer: str, amount: float, description: str) -> dict:
        """
        Create invoice in Odoo using XML-RPC

        Args:
            customer: Customer name
            amount: Invoice amount
            description: Invoice description

        Returns:
            dict: Result with success status and invoice ID
        """
        if DRY_RUN:
            logger.info(f"💰 [DRY-RUN] Would create Odoo invoice:")
            logger.info(f"   Customer: {customer}")
            logger.info(f"   Amount: ${amount}")
            logger.info(f"   Description: {description}")
            return {
                "success": True,
                "platform": "Odoo",
                "timestamp": datetime.now().isoformat(),
                "dry_run": True,
                "invoice_id": "DRY_RUN_123"
            }

        try:
            logger.info(f"💰 Creating Odoo invoice...")
            logger.info(f"   Customer: {customer}")
            logger.info(f"   Amount: ${amount}")

            # Validate credentials
            if not all([self.odoo_url, self.odoo_db, self.odoo_user, self.odoo_password]):
                raise Exception("Odoo credentials not configured in .env file")

            # Connect to Odoo
            common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            uid = common.authenticate(self.odoo_db, self.odoo_user, self.odoo_password, {})

            if not uid:
                raise Exception("Odoo authentication failed")

            logger.debug(f"✓ Authenticated with Odoo (UID: {uid})")

            models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')

            # Find or create customer
            partner_ids = models.execute_kw(
                self.odoo_db, uid, self.odoo_password,
                'res.partner', 'search',
                [[['name', '=', customer]]]
            )

            if partner_ids:
                partner_id = partner_ids[0]
                logger.debug(f"✓ Found existing customer (ID: {partner_id})")
            else:
                # Create new customer
                partner_id = models.execute_kw(
                    self.odoo_db, uid, self.odoo_password,
                    'res.partner', 'create',
                    [{'name': customer}]
                )
                logger.info(f"✓ Created new customer (ID: {partner_id})")

            # Create invoice
            invoice_data = {
                'partner_id': partner_id,
                'move_type': 'out_invoice',
                'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                'invoice_line_ids': [(0, 0, {
                    'name': description,
                    'quantity': 1,
                    'price_unit': amount,
                })]
            }

            invoice_id = models.execute_kw(
                self.odoo_db, uid, self.odoo_password,
                'account.move', 'create',
                [invoice_data]
            )

            logger.info(f"✅ Successfully created invoice (ID: {invoice_id})")

            return {
                "success": True,
                "platform": "Odoo",
                "timestamp": datetime.now().isoformat(),
                "invoice_id": invoice_id,
                "customer": customer,
                "amount": amount
            }

        except Exception as e:
            logger.error(f"❌ Odoo invoice creation failed: {e}", exc_info=True)
            return {
                "success": False,
                "platform": "Odoo",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _save_error_screenshot(self, page: Page, platform: str):
        """
        Save screenshot on error for debugging

        Args:
            page: Playwright page object
            platform: Platform name for filename
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.log_dir / f"{platform}_error_{timestamp}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"📸 Error screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.warning(f"⚠️ Could not save screenshot: {e}")


def main():
    """CLI for testing executor"""
    import argparse

    parser = argparse.ArgumentParser(description='Social Media Executor')
    parser.add_argument('platform', choices=['linkedin', 'facebook', 'odoo'],
                       help='Platform to post to')
    parser.add_argument('content', help='Post content or invoice description')
    parser.add_argument('--image', help='Path to image file', default=None)
    parser.add_argument('--customer', help='Customer name (for Odoo)', default=None)
    parser.add_argument('--amount', type=float, help='Invoice amount (for Odoo)', default=0)

    args = parser.parse_args()

    executor = SocialMediaExecutor(args.platform)

    if args.platform == 'linkedin':
        result = executor.post_to_linkedin(args.content, args.image)
    elif args.platform == 'facebook':
        result = executor.post_to_facebook(args.content, args.image)
    elif args.platform == 'odoo':
        if not args.customer or not args.amount:
            print("❌ --customer and --amount required for Odoo invoices")
            return
        result = executor.create_odoo_invoice(args.customer, args.amount, args.content)

    print(f"\n📊 Result: {result}")


if __name__ == "__main__":
    main()
