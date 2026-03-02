"""
Master Orchestrator - The Brain
Monitors /Approved folder and triggers execution automatically
"""

import os
import sys
import time
import yaml
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from executor import SocialMediaExecutor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'./Logs/actions_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MasterOrchestrator:
    """Monitors approved posts and executes them automatically"""

    def __init__(self):
        """Initialize orchestrator with folder paths and executors"""
        self.approved_dir = Path("./Approved")
        self.done_dir = Path("./Done")
        self.log_dir = Path("./Logs")

        # Create directories if they don't exist
        self.approved_dir.mkdir(parents=True, exist_ok=True)
        self.done_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Retry configuration
        self.max_retries = 3
        self.retry_cooldown = 300  # 5 minutes
        self.rate_limit_delay = 60  # Minimum 60 seconds between posts

        # Track last post time for rate limiting
        self.last_post_time = 0

        # Initialize executors
        self.executors = {
            "linkedin": SocialMediaExecutor("linkedin"),
            "facebook": SocialMediaExecutor("facebook"),
            "odoo": SocialMediaExecutor("odoo")
        }

        logger.info("🤖 Master Orchestrator initialized")
        logger.info(f"   Monitoring: {self.approved_dir}")
        logger.info(f"   Max retries: {self.max_retries}")
        logger.info(f"   Retry cooldown: {self.retry_cooldown}s")
        logger.info(f"   Rate limit: {self.rate_limit_delay}s between posts")

    def monitor_approved_folder(self):
        """Continuously monitor Approved folder for new posts"""
        print("\n" + "=" * 60)
        print("🚀 Master Orchestrator started")
        print("=" * 60)
        print(f"📁 Monitoring: {self.approved_dir}")
        print("⏰ Check interval: 10 seconds")
        print("Press Ctrl+C to stop\n")

        while True:
            try:
                # Find all POST_*.md and INVOICE_*.md files
                post_files = list(self.approved_dir.glob("POST_*.md"))
                invoice_files = list(self.approved_dir.glob("INVOICE_*.md"))
                files = post_files + invoice_files

                if files:
                    logger.info(f"📬 Found {len(files)} approved item(s)")

                for file in files:
                    logger.info(f"\n{'=' * 60}")
                    logger.info(f"📝 Processing: {file.name}")
                    logger.info(f"{'=' * 60}")

                    # Rate limiting
                    self._enforce_rate_limit()

                    self.process_post(file)

                # Sleep before next check
                time.sleep(10)

            except KeyboardInterrupt:
                logger.info("\n\n🛑 Orchestrator stopped by user")
                print("Goodbye! 👋")
                break

            except Exception as e:
                logger.error(f"❌ Error in orchestrator main loop: {e}", exc_info=True)
                print("⏳ Waiting 30s before retry...")
                time.sleep(30)

    def _enforce_rate_limit(self):
        """Enforce rate limiting between posts"""
        current_time = time.time()
        time_since_last_post = current_time - self.last_post_time

        if time_since_last_post < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last_post
            logger.info(f"⏳ Rate limiting: waiting {wait_time:.0f}s before next post")
            time.sleep(wait_time)

        self.last_post_time = time.time()

    def process_post(self, file_path: Path):
        """
        Process a single approved post or invoice

        Args:
            file_path: Path to the post/invoice file
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse YAML frontmatter and content
            metadata, post_content = self._parse_post(content)

            # Determine type (post or invoice)
            file_type = metadata.get('type', 'post')

            if file_type == 'invoice':
                self._process_invoice(file_path, metadata, post_content)
            else:
                self._process_social_post(file_path, metadata, post_content)

        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}", exc_info=True)
            self._log_error(file_path, str(e))

    def _process_social_post(self, file_path: Path, metadata: dict, post_content: str):
        """Process social media post"""
        platform = metadata.get('platform', '').lower()
        image_path = metadata.get('image', 'none')

        if image_path == 'none' or not image_path:
            image_path = None

        logger.info(f"🎯 Platform: {platform}")
        logger.info(f"📝 Content length: {len(post_content)} characters")
        if image_path:
            logger.info(f"🖼️  Image: {image_path}")

        # Validate platform
        if platform not in ['linkedin', 'facebook']:
            logger.error(f"❌ Unknown platform: {platform}")
            logger.error(f"   Supported platforms: linkedin, facebook")
            return

        # Execute post with retry logic
        result = self._execute_with_retry(platform, post_content, image_path)

        if result['success']:
            logger.info(f"✅ Successfully posted to {platform.upper()}")
            self._move_to_done(file_path, result)
            self._log_success(file_path, result)
        else:
            logger.error(f"❌ Failed to post to {platform.upper()}")
            logger.error(f"   Error: {result.get('error', 'Unknown error')}")
            self._log_failure(file_path, result)

    def _process_invoice(self, file_path: Path, metadata: dict, post_content: str):
        """Process Odoo invoice"""
        logger.info(f"💰 Processing Odoo invoice")
        logger.info(f"   Customer: {metadata.get('customer')}")
        logger.info(f"   Amount: {metadata.get('amount')}")

        result = self._execute_with_retry('odoo', post_content, metadata=metadata)

        if result['success']:
            logger.info(f"✅ Successfully created invoice in Odoo")
            self._move_to_done(file_path, result)
            self._log_success(file_path, result)
        else:
            logger.error(f"❌ Failed to create invoice")
            logger.error(f"   Error: {result.get('error', 'Unknown error')}")
            self._log_failure(file_path, result)

    def _execute_with_retry(self, platform: str, content: str, image_path: str = None, metadata: dict = None) -> dict:
        """
        Execute post with retry logic

        Args:
            platform: Platform name (linkedin, facebook, odoo)
            content: Post content or invoice description
            image_path: Optional image path
            metadata: Optional metadata for invoices

        Returns:
            dict: Execution result
        """
        executor = self.executors.get(platform)

        if not executor:
            return {
                "success": False,
                "error": f"Unknown platform: {platform}",
                "platform": platform
            }

        for attempt in range(1, self.max_retries + 1):
            logger.info(f"🔄 Attempt {attempt}/{self.max_retries}")

            # Execute based on platform
            if platform == "linkedin":
                result = executor.post_to_linkedin(content, image_path)
            elif platform == "facebook":
                result = executor.post_to_facebook(content, image_path)
            elif platform == "odoo":
                result = executor.create_odoo_invoice(
                    customer=metadata.get('customer'),
                    amount=metadata.get('amount'),
                    description=content
                )
            else:
                result = {
                    "success": False,
                    "error": f"Unsupported platform: {platform}",
                    "platform": platform
                }

            if result['success']:
                return result

            # Retry logic
            if attempt < self.max_retries:
                logger.info(f"⏳ Waiting {self.retry_cooldown}s before retry...")
                time.sleep(self.retry_cooldown)
            else:
                logger.error(f"❌ All {self.max_retries} attempts failed")

        return result

    def _parse_post(self, content: str) -> tuple:
        """
        Parse YAML frontmatter and post content with error handling

        Args:
            content: Raw file content

        Returns:
            tuple: (metadata dict, post content string)
        """
        try:
            parts = content.split('---', 2)

            if len(parts) >= 3:
                # Has YAML frontmatter
                try:
                    metadata = yaml.safe_load(parts[1])
                    if metadata is None:
                        metadata = {}
                    post_content = parts[2].strip()
                except yaml.YAMLError as e:
                    logger.warning(f"⚠️ YAML parsing error: {e}")
                    metadata = {}
                    post_content = content
            else:
                # No frontmatter
                metadata = {}
                post_content = content.strip()

            return metadata, post_content

        except Exception as e:
            logger.error(f"Error parsing post: {e}", exc_info=True)
            return {}, content

    def _move_to_done(self, file_path: Path, result: dict):
        """
        Move completed post to Done folder

        Args:
            file_path: Original file path
            result: Execution result
        """
        try:
            # Create new filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{file_path.stem}_completed_{timestamp}.md"
            done_path = self.done_dir / new_name

            # Move file
            file_path.rename(done_path)
            logger.info(f"📁 Moved to Done: {done_path.name}")

        except Exception as e:
            logger.warning(f"⚠️ Could not move file to Done: {e}")

    def _log_success(self, file_path: Path, result: dict):
        """Log successful execution"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path.name,
            "platform": result.get('platform'),
            "status": "success",
            "result": result
        }
        self._write_log(log_entry)

    def _log_failure(self, file_path: Path, result: dict):
        """Log failed execution"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path.name,
            "platform": result.get('platform'),
            "status": "failure",
            "error": result.get('error'),
            "result": result
        }
        self._write_log(log_entry)

    def _log_error(self, file_path: Path, error: str):
        """Log processing error"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path.name,
            "status": "error",
            "error": error
        }
        self._write_log(log_entry)

    def _write_log(self, log_entry: dict):
        """Write log entry to file"""
        try:
            log_file = self.log_dir / "orchestrator.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(yaml.dump([log_entry], default_flow_style=False))
                f.write("\n")
        except Exception as e:
            logger.warning(f"⚠️ Could not write log: {e}")


def main():
    """Run the orchestrator"""
    orchestrator = MasterOrchestrator()
    orchestrator.monitor_approved_folder()


if __name__ == "__main__":
    main()
