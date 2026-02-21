"""Google Tasks service for creating tasks."""

import logging
from typing import Union

from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from d_brain.services.google_auth import GoogleAuthService

logger = logging.getLogger(__name__)


class GoogleTasksService:
    """Service for creating tasks in Google Tasks."""

    def __init__(self, credentials_path: str) -> None:
        """Initialize with Google credentials.

        Args:
            credentials_path: Path to service account JSON file
        """
        self.auth = GoogleAuthService(credentials_path)
        self.service = build("tasks", "v1", credentials=self.auth.credentials)
        self._tasklist_id = None

    def _get_tasklist(self) -> str:
        """Get or create 'Second Brain' tasklist.

        Returns:
            Tasklist ID
        """
        if self._tasklist_id:
            return self._tasklist_id

        try:
            # Get tasklists
            results = self.service.tasklists().list().execute()
            tasklists = results.get("items", [])

            # Find or create "Second Brain" list
            for tasklist in tasklists:
                if tasklist["title"] == "Second Brain":
                    self._tasklist_id = tasklist["id"]
                    logger.info("Found existing tasklist: %s", self._tasklist_id)
                    return self._tasklist_id

            # Create new tasklist
            new_list = self.service.tasklists().insert(
                body={"title": "Second Brain"}
            ).execute()
            self._tasklist_id = new_list["id"]
            logger.info("Created new tasklist: %s", self._tasklist_id)
            return self._tasklist_id

        except Exception as e:
            logger.error("Failed to get tasklist: %s", e)
            raise

    def create_task(
        self, title: str, notes: str = "", due_date: str = ""
    ) -> dict:
        """Create a task in Google Tasks.

        Args:
            title: Task title
            notes: Task notes/description
            due_date: Due date in YYYY-MM-DD format (will be converted to RFC 3339)

        Returns:
            Created task object
        """
        try:
            tasklist_id = self._get_tasklist()

            task_body = {"title": title}
            if notes:
                task_body["notes"] = notes
            if due_date:
                # Convert YYYY-MM-DD to RFC 3339 format (required by Google Tasks API)
                # The API expects format like "2026-02-25T00:00:00Z"
                if len(due_date) == 10:  # YYYY-MM-DD format
                    task_body["due"] = f"{due_date}T00:00:00Z"
                else:
                    task_body["due"] = due_date

            task = (
                self.service.tasks()
                .insert(tasklist=tasklist_id, body=task_body)
                .execute()
            )

            logger.info("Created task: %s", task["id"])
            return task

        except Exception as e:
            logger.error("Failed to create task: %s", e)
            raise
