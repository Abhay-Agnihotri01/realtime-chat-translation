import hashlib
import time
from typing import Dict, Optional

class PrivacyService:
    def __init__(self):
        self.message_retention_hours = 24  # Auto-delete after 24h
        self.stored_messages: Dict[str, dict] = {}
    
    def anonymize_user_id(self, user_id: str) -> str:
        """Hash user ID for privacy"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def should_retain_message(self, timestamp: float) -> bool:
        """Check if message should be retained based on privacy policy"""
        return (time.time() - timestamp) < (self.message_retention_hours * 3600)
    
    def sanitize_message(self, message: str) -> str:
        """Remove potential PII from messages"""
        # Basic PII removal - in production, use more sophisticated methods
        import re
        # Remove email patterns
        message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', message)
        # Remove phone patterns
        message = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE]', message)
        return message

privacy_service = PrivacyService()