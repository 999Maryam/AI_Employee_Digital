#!/usr/bin/env python3
"""
Gmail Watcher - Monitors for unread important emails and creates action files.
"""

import time
from datetime import datetime
from pathlib import Path
import os.path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Gmail API scope for read-only access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Paths
VAULT_ROOT = Path(__file__).parent
NEEDS_ACTION_DIR = VAULT_ROOT / "Needs_Action"
CREDENTIALS_FILE = VAULT_ROOT / "credentials.json"
TOKEN_FILE = VAULT_ROOT / "token.json"

# Check interval in seconds
CHECK_INTERVAL = 120

# Track processed message IDs to avoid duplicates
processed_ids = set()


def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None

    # Load existing token if available
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # Refresh or create new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_message_details(service, msg_id):
    """Fetch full message details."""
    message = service.users().messages().get(
        userId='me', id=msg_id, format='full'
    ).execute()

    headers = message.get('payload', {}).get('headers', [])

    def get_header(name):
        for h in headers:
            if h['name'].lower() == name.lower():
                return h['value']
        return ''

    return {
        'id': msg_id,
        'from': get_header('From'),
        'subject': get_header('Subject'),
        'date': get_header('Date'),
        'snippet': message.get('snippet', '')
    }


def create_action_file(email_data):
    """Create markdown file in Needs_Action folder."""
    msg_id = email_data['id']
    filename = f"EMAIL_{msg_id}.md"
    filepath = NEEDS_ACTION_DIR / filename

    # Escape any quotes in subject for YAML
    subject = email_data['subject'].replace('"', '\\"')
    snippet = email_data['snippet'].replace('"', '\\"')

    content = f'''---
type: email
message_id: "{msg_id}"
status: unread
created: "{datetime.now().isoformat()}"
---

# Email Action Required

**From:** {email_data['from']}

**Subject:** {email_data['subject']}

**Received:** {email_data['date']}

**Snippet:** {email_data['snippet']}

## Suggested Actions

- [ ] Read full email
- [ ] Reply to sender
- [ ] Forward to relevant person
- [ ] Create task from this email
- [ ] Archive/Mark as done
'''

    filepath.write_text(content, encoding='utf-8')
    print(f"  Created: {filename}")


def check_gmail(service):
    """Check for new unread important emails."""
    global processed_ids

    # Query for unread important emails
    query = 'is:unread is:important'

    results = service.users().messages().list(
        userId='me', q=query, maxResults=50
    ).execute()

    messages = results.get('messages', [])
    new_count = 0

    for msg in messages:
        msg_id = msg['id']

        if msg_id not in processed_ids:
            email_data = get_message_details(service, msg_id)
            create_action_file(email_data)
            processed_ids.add(msg_id)
            new_count += 1

    return new_count, len(messages)


def main():
    """Main loop - check Gmail every CHECK_INTERVAL seconds."""
    print("=" * 50)
    print("Gmail Watcher Starting")
    print(f"Checking every {CHECK_INTERVAL} seconds")
    print(f"Needs_Action folder: {NEEDS_ACTION_DIR}")
    print("=" * 50)

    # Ensure Needs_Action directory exists
    NEEDS_ACTION_DIR.mkdir(exist_ok=True)

    # Initialize Gmail service
    print("Authenticating with Gmail API...")
    service = get_gmail_service()
    print("Authentication successful!")

    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_count, total_count = check_gmail(service)

            print(f"[{timestamp}] Checked Gmail - found {new_count} new emails ({total_count} total unread important)")

        except Exception as e:
            print(f"[{timestamp}] Error checking Gmail: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
