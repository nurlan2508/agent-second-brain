"""Google Keep service for saving notes."""

import logging

from googleapiclient.discovery import build

from d_brain.services.google_auth import GoogleAuthService

logger = logging.getLogger(__name__)


class GoogleKeepService:
    """Service for saving notes to Google Keep."""

    def __init__(self, credentials_path: str) -> None:
        """Initialize with Google credentials.

        Args:
            credentials_path: Path to service account JSON file
        """
        self.auth = GoogleAuthService(credentials_path)
        self.service = build("keep", "v1", credentials=self.auth.credentials)

    def create_note(self, title: str, content: str, labels: list[str] = None) -> dict:
        """Create a note in Google Keep.

        Args:
            title: Note title
            content: Note content/body
            labels: List of label names to add to note

        Returns:
            Created note object
        """
        try:
            note_body = {
                "title": title,
                "body": {"text": {"text": content}},
            }

            if labels:
                note_body["labels"] = {label: {} for label in labels}

            note = self.service.notes().create(body=note_body).execute()

            logger.info("Created note: %s", note["name"])
            return note

        except Exception as e:
            logger.error("Failed to create note: %s", e)
            raise
