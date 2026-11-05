
import asyncio
import os

from google import genai
from google.genai import errors
from fastapi import HTTPException, status

from app.config import settings


class GeminiService:

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL

        self.fallback_model = os.getenv(
            "GEMINI_FALLBACK_MODEL", ""
        ).strip()

        if (
            not settings.GEMINI_API_KEY
            or settings.GEMINI_API_KEY == "your_actual_gemini_api_key_here"
        ):
            self.client = None
        else:
            self.client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

        print("Gemini Service Initialized", flush=True)
        print("Primary Model:", self.model_name, flush=True)
        print("Backup Model:", self.fallback_model or "Not configured", flush=True)

    def _ensure_client(self):
        if not self.client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API Key is not configured."
            )

    async def _generate_with_model(self, model, prompt):
        return await asyncio.to_thread(
            self.client.models.generate_content,
            model=model,
            contents=prompt
        )

    async def generate_text(self, prompt: str) -> str:

        self._ensure_client()

        models = [self.model_name]

        if self.fallback_model and self.fallback_model != self.model_name:
            models.append(self.fallback_model)

        errors_found = []

        for model in models:

            print("Trying Gemini model:", model, flush=True)

            # Maximum 3 attempts for each model
            for attempt in range(1, 4):

                try:
                    print(
                        f"Attempt {attempt}/3 for {model}",
                        flush=True
                    )

                    response = await self._generate_with_model(
                        model, prompt
                    )

                    if response and response.text:
                        print(
                            "Gemini generation successful using:",
                            model,
                            flush=True
                        )
                        return response.text

                    raise HTTPException(
                        status_code=502,
                        detail=f"Empty response from {model}."
                    )

                except errors.APIError as e:

                    error_msg = str(e)
                    upper_error = error_msg.upper()

                    print(
                        "GEMINI API ERROR:",
                        model,
                        error_msg,
                        flush=True
                    )

                    retryable = (
                        "503" in upper_error
                        or "UNAVAILABLE" in upper_error
                        or "429" in upper_error
                        or "RESOURCE_EXHAUSTED" in upper_error
                    )

                    if retryable:
                        errors_found.append(
                            f"{model}: {error_msg}"
                        )

                        if attempt < 3:
                            wait_time = 2 ** attempt

                            print(
                                f"Retrying {model} after {wait_time} seconds",
                                flush=True
                            )

                            await asyncio.sleep(wait_time)
                            continue

                        print(
                            f"All attempts failed for {model}",
                            flush=True
                        )
                        break

                    if (
                        "INVALID_ARGUMENT" in upper_error
                        or "API_KEY_INVALID" in upper_error
                    ):
                        raise HTTPException(
                            status_code=401,
                            detail=f"Gemini configuration error: {error_msg}"
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

        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini is temporarily unavailable. "
                "Both models failed after retry attempts. "
                "Please try again later."
            )
        )


gemini_service = GeminiService()
