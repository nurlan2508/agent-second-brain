"""OpenAI Whisper transcription service."""

import logging

import httpx

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    """Service for transcribing audio using OpenAI Whisper."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe audio bytes to text.

        Args:
            audio_bytes: Audio file content

        Returns:
            Transcribed text

        Raises:
            Exception: If transcription fails
        """
        logger.info("Starting transcription, audio size: %d bytes", len(audio_bytes))

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files={"file": ("voice.ogg", audio_bytes, "audio/ogg")},
                data={"model": "whisper-1", "language": "ru"},
            )
            response.raise_for_status()
            transcript = response.json().get("text", "")

        logger.info("Transcription complete: %d chars", len(transcript))
        return transcript
