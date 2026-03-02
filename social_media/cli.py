"""
CLI - Terminal Command Interface
Simple terminal commands to create social media posts and Odoo invoices
"""

import argparse
import os
import csv
from datetime import datetime
from pathlib import Path


class SocialMediaCLI:
    """Command-line interface for social media automation"""

    def __init__(self):
        self.pending_dir = Path("./Pending_Approval")
        self.pending_dir.mkdir(parents=True, exist_ok=True)

    def create_post(self, platform: str, content: str = None, image_path: str = None):
        """
        Create a social media post draft

        Args:
            platform: Platform name (linkedin, facebook, both)
            content: Post content (if None, will prompt interactively)
            image_path: Optional path to image file
        """
        # Interactive mode if no content provided
        if not content:
            print("\n📝 Interactive Post Creation")
            print("=" * 60)
            content = input("Enter your post content: ")

            if not image_path:
                image_input = input("Image path (press Enter to skip): ").strip()
                if image_input:
                    image_path = image_input

        # Handle "both" platform
        if platform == 'both':
            self.create_post('linkedin', content, image_path)
            self.create_post('facebook', content, image_path)
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"POST_{platform}_{timestamp}.md"
        filepath = self.pending_dir / filename

        # Create post with YAML metadata
        post_content = f"""---
platform: {platform}
created: {datetime.now().isoformat()}
status: pending
image: {image_path if image_path else 'none'}
type: post
---

{content}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(post_content)

        print(f"✅ Post draft created: {filename}")
        print(f"📁 Location: {filepath}")
        print(f"👉 Review and move to /Approved to publish")

        return filepath

    def create_odoo_invoice(self, customer: str = None, amount: float = None, description: str = None):
        """
        Create Odoo invoice draft

        Args:
            customer: Customer name
            amount: Invoice amount
            description: Invoice description
        """
        # Interactive mode if parameters not provided
        if not customer:
            print("\n💰 Interactive Invoice Creation")
            print("=" * 60)
            customer = input("Customer name: ")
            amount = float(input("Invoice amount ($): "))
            description = input("Description: ")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"INVOICE_{timestamp}.md"
        filepath = self.pending_dir / filename

        invoice_content = f"""---
type: invoice
customer: {customer}
amount: {amount}
created: {datetime.now().isoformat()}
status: pending
---

{description}

## Invoice Preview
- **Customer**: {customer}
- **Amount**: ${amount:,.2f}
- **Description**: {description}
- **Date**: {datetime.now().strftime('%Y-%m-%d')}

Move this file to /Approved to create the invoice in Odoo.
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(invoice_content)

        print(f"✅ Invoice draft created: {filename}")
        print(f"📁 Location: {filepath}")
        print(f"💰 Customer: {customer} | Amount: ${amount:,.2f}")
        print(f"👉 Review and move to /Approved to create in Odoo")

        return filepath

    def create_email_draft(self, recipient: str = None, subject: str = None, body: str = None):
        """
        Create email draft

        Args:
            recipient: Email recipient
            subject: Email subject
            body: Email body
        """
        # Interactive mode
        if not recipient:
            print("\n📧 Interactive Email Creation")
            print("=" * 60)
            recipient = input("Recipient email: ")
            subject = input("Subject: ")
            body = input("Body: ")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"EMAIL_{timestamp}.md"
        filepath = self.pending_dir / filename

        email_content = f"""---
type: email
recipient: {recipient}
subject: {subject}
created: {datetime.now().isoformat()}
status: pending
---

{body}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(email_content)

        print(f"✅ Email draft created: {filename}")
        print(f"📁 Location: {filepath}")
        return filepath

    def bulk_post_from_csv(self, csv_path: str):
        """
        Create multiple posts from CSV file

        CSV format: platform,content,image_path
        Example:
            linkedin,"My first post",./images/pic1.jpg
            facebook,"My second post",
            both,"Post to both platforms",./images/pic2.jpg

        Args:
            csv_path: Path to CSV file
        """
        if not os.path.exists(csv_path):
            print(f"❌ CSV file not found: {csv_path}")
            return

        print(f"\n📊 Bulk Post Creation from {csv_path}")
        print("=" * 60)

        created_count = 0
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                platform = row.get('platform', 'linkedin')
                content = row.get('content', '')
                image_path = row.get('image_path', '').strip()

                if not image_path:
                    image_path = None

                if content:
                    self.create_post(platform, content, image_path)
                    created_count += 1

        print(f"\n✅ Created {created_count} post draft(s)")
        print(f"👉 Review files in {self.pending_dir} and move to /Approved")


def main():
    """Main CLI entry point with detailed help"""
    parser = argparse.ArgumentParser(
        description='🤖 Social Media Automation CLI - Terminal-controlled posting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create LinkedIn post
  python cli.py post linkedin "Just shipped a new feature! 🚀"

  # Create Facebook post with image
  python cli.py post facebook "Check this out!" --image ./photo.jpg

  # Post to both platforms
  python cli.py post both "This goes everywhere!"

  # Interactive mode (no content provided)
  python cli.py post linkedin

  # Create Odoo invoice
  python cli.py odoo-invoice "Acme Corp" 1500 "Website development"

  # Interactive invoice creation
  python cli.py odoo-invoice

  # Bulk posts from CSV
  python cli.py bulk posts.csv

  # Create email draft
  python cli.py email "client@example.com" "Project Update" "Here's the latest..."

CSV Format for bulk posts:
  platform,content,image_path
  linkedin,"My post content",./images/pic.jpg
  facebook,"Another post",
  both,"Post to both",./images/chart.png

Workflow:
  1. Run command to create draft in /Pending_Approval
  2. Review the draft file
  3. Move to /Approved folder to trigger posting
  4. Orchestrator automatically posts and moves to /Done
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Post command
    post_parser = subparsers.add_parser('post', help='Create a social media post')
    post_parser.add_argument('platform', choices=['linkedin', 'facebook', 'both'],
                            help='Platform to post to')
    post_parser.add_argument('content', nargs='?', default=None,
                            help='Post content (omit for interactive mode)')
    post_parser.add_argument('--image', help='Path to image file', default=None)

    # Odoo invoice command
    invoice_parser = subparsers.add_parser('odoo-invoice',
                                          help='Create an Odoo invoice draft')
    invoice_parser.add_argument('customer', nargs='?', default=None,
                               help='Customer name (omit for interactive mode)')
    invoice_parser.add_argument('amount', nargs='?', type=float, default=None,
                               help='Invoice amount')
    invoice_parser.add_argument('description', nargs='?', default=None,
                               help='Invoice description')

    # Email command
    email_parser = subparsers.add_parser('email', help='Create an email draft')
    email_parser.add_argument('recipient', nargs='?', default=None,
                             help='Email recipient (omit for interactive mode)')
    email_parser.add_argument('subject', nargs='?', default=None,
                             help='Email subject')
    email_parser.add_argument('body', nargs='?', default=None,
                             help='Email body')

    # Bulk command
    bulk_parser = subparsers.add_parser('bulk', help='Create posts from CSV file')
    bulk_parser.add_argument('csv_file', help='Path to CSV file')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = SocialMediaCLI()

    if args.command == 'post':
        cli.create_post(args.platform, args.content, args.image)

    elif args.command == 'odoo-invoice':
        cli.create_odoo_invoice(args.customer, args.amount, args.description)

    elif args.command == 'email':
        cli.create_email_draft(args.recipient, args.subject, args.body)

    elif args.command == 'bulk':
        cli.bulk_post_from_csv(args.csv_file)


if __name__ == "__main__":
    main()
