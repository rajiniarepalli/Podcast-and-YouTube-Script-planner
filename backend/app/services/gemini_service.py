
import asyncio
from google import genai
from google.genai import errors
from fastapi import HTTPException, status
from app.config import settings


class GeminiService:

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL

        if (
            not settings.GEMINI_API_KEY
            or settings.GEMINI_API_KEY == "your_actual_gemini_api_key_here"
        ):
            self.client = None
        else:
            self.client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

        print(
            "Gemini Service Initialized",
            flush=True
        )
        print(
            "Configured Gemini Model:",
            self.model_name,
            flush=True
        )

    def _ensure_client(self):
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API Key is not configured."
            )

    async def generate_text(self, prompt: str) -> str:

        self._ensure_client()

        print(
            "Using Gemini model:",
            self.model_name,
            flush=True
        )

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt
            )

            if response and response.text:
                print(
                    "Gemini generation successful.",
                    flush=True
                )
                return response.text

            raise HTTPException(
                status_code=502,
                detail="Gemini returned an empty response."
            )

        except errors.APIError as e:

            error_msg = str(e)

            print(
                "ACTUAL GEMINI ERROR:",
                error_msg,
                flush=True
            )

            upper_error = error_msg.upper()

            if "429" in upper_error or "RESOURCE_EXHAUSTED" in upper_error:
                raise HTTPException(
                    status_code=429,
                    detail=f"Gemini quota exceeded or rate limited: {error_msg}"
                )

            if "503" in upper_error or "UNAVAILABLE" in upper_error:
                raise HTTPException(
                    status_code=503,
                    detail=f"Gemini service temporarily unavailable: {error_msg}"
                )

            if (
                "INVALID_ARGUMENT" in upper_error
                or "API_KEY_INVALID" in upper_error
            ):
                raise HTTPException(
                    status_code=401,
                    detail=f"Gemini authentication/configuration error: {error_msg}"
                )

            raise HTTPException(
                status_code=502,
                detail=f"Gemini API error: {error_msg}"
            )

        except HTTPException:
            raise

        except Exception as e:

            print(
                "UNEXPECTED GEMINI ERROR:",
                str(e),
                flush=True
            )

            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )


gemini_service = GeminiService()
