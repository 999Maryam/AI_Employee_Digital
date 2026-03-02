"""
Social Media Automation System
Terminal-controlled posting to LinkedIn, Facebook, Email, and Odoo
"""

__version__ = "1.0.0"
__author__ = "AI Employee"

from .session_manager import SessionManager
from .executor import SocialMediaExecutor
from .orchestrator import MasterOrchestrator
from .cli import SocialMediaCLI

__all__ = [
    'SessionManager',
    'SocialMediaExecutor',
    'MasterOrchestrator',
    'SocialMediaCLI'
]
