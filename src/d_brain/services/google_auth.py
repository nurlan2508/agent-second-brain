"""Google API authentication service."""

import json
import logging
from pathlib import Path
from typing import Union

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)


class GoogleAuthService:
    """Service for authenticating with Google APIs using service account."""

    SCOPES = [
        "https://www.googleapis.com/auth/tasks",
        "https://www.googleapis.com/auth/keep",
        "https://www.googleapis.com/auth/calendar",
    ]

    def __init__(self, credentials_path: Union[str, Path]) -> None:
        """Initialize with service account credentials file.

        Args:
            credentials_path: Path to service account JSON file
        """
        self.credentials_path = Path(credentials_path)
        self._credentials = None

    @property
    def credentials(self) -> Credentials:
        """Get or create credentials."""
        if self._credentials is None:
            if not self.credentials_path.exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {self.credentials_path}"
                )

            with open(self.credentials_path) as f:
                service_account_info = json.load(f)

            self._credentials = Credentials.from_service_account_info(
                service_account_info, scopes=self.SCOPES
            )
            logger.info("Google credentials loaded from %s", self.credentials_path)

        # Refresh if expired
        if self._credentials.expired:
            self._credentials.refresh(Request())

        return self._credentials
