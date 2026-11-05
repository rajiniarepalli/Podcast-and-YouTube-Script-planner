
import asyncio
from google import genai
from google.genai import errors
from fastapi import HTTPException, status
from app.config import settings


class GeminiService:
    def __init__(self):
        if (
            not settings.GEMINI_API_KEY
            or settings.GEMINI_API_KEY == "your_actual_gemini_api_key_here"
        ):
            self.client = None
        else:
            self.client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

        self.model_name = settings.GEMINI_MODEL

    def _ensure_client(self):
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API Key is not configured."
            )

    async def generate_text(self, prompt: str) -> str:
        self._ensure_client()

        models_to_try = list(dict.fromkeys([
            self.model_name,
            "gemini-3.7-flash",
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite"
        ]))

        last_error_msg = ""

        for model in models_to_try:
            for attempt in range(2):
                try:
                    response = await asyncio.to_thread(
                        self.client.models.generate_content,
                        model=model,
                        contents=prompt
                    )

                    if response and response.text:
                        return response.text

                    last_error_msg = f"No response received from {model}"

                except errors.APIError as e:
                    last_error_msg = str(e)
                    error_msg = last_error_msg.upper()

                    if (
                        "503" in error_msg
                        or "UNAVAILABLE" in error_msg
                        or "429" in error_msg
                        or "RESOURCE_EXHAUSTED" in error_msg
                    ):
                        # Retry once after a short delay
                        if attempt == 0:
                            await asyncio.sleep(2)
                            continue

                        # Try the next model
                        break

                    if (
                        "INVALID_ARGUMENT" in error_msg
                        or "API_KEY_INVALID" in error_msg
                    ):
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Gemini API key."
                        )

                    if "404" in error_msg or "NOT_FOUND" in error_msg:
                        break

                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Gemini API error: {last_error_msg}"
                    )

                except Exception as e:
                    last_error_msg = str(e)
                    break

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "All Gemini models are temporarily unavailable. "
                "Please try again later. "
                f"Last error: {last_error_msg}"
            )
        )


gemini_service = GeminiService()
